from collections.abc import Mapping, Sequence

from app.models.api import FindingDraft, SanitizedFinding
from app.models.domain import FindingSource


REDACTION_VERSION = "1.0.0"
REDACTED_CREDENTIAL = "[REDACTED_CREDENTIAL]"
REDACTED_CREDENTIAL_MESSAGE = "A credential-like value was added and redacted."
REDACTED_CREDENTIAL_SUGGESTION = (
    "Remove the credential and use a secure secret store."
)
REDACTED_RULE_EXCERPT = "[REDACTED_FINDING_CONTEXT]"
REDACTED_RULE_MESSAGE = "A deterministic rule matched an added change."
REDACTED_RULE_SUGGESTION = "Review the rule identifier and affected location."
REDACTED_PROVIDER_MESSAGE = "Provider-supplied text was withheld for safety."
REDACTED_PROVIDER_SUGGESTION = (
    "Review the deterministic findings before applying any provider suggestion."
)
ALLOWED_PROVIDER_FINDING_CONTRACTS = frozenset(
    {
        ("AI-001", "1.0.0", "provider/ai-review"),
        ("AI-MOCK-001", "1.0.0", "mock/synthetic-review"),
    }
)


def _is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def redact_finding(finding: FindingDraft) -> SanitizedFinding:
    if finding.rule_id == "GEN-001":
        excerpt = REDACTED_CREDENTIAL
        message = REDACTED_CREDENTIAL_MESSAGE
        suggestion = REDACTED_CREDENTIAL_SUGGESTION
        category = "credential"
    else:
        excerpt = REDACTED_RULE_EXCERPT
        message = REDACTED_RULE_MESSAGE
        suggestion = REDACTED_RULE_SUGGESTION
        category = "deterministic_rule"

    return SanitizedFinding(
        rule_id=finding.rule_id,
        rule_version=finding.rule_version,
        source=finding.source,
        severity=finding.severity,
        path=finding.path,
        new_line=finding.new_line,
        excerpt=excerpt,
        message=message,
        suggestion=suggestion,
        redacted=True,
        redaction_version=REDACTION_VERSION,
        redaction_category=category,
    )


def redact_provider_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Copy only the structured, public-safe provider contract fields."""

    safe_payload: dict[str, object] = {"output_schema_version": REDACTION_VERSION}
    files = payload.get("files")
    if isinstance(files, Sequence) and not isinstance(files, (str, bytes)):
        safe_payload["files"] = [
            {
                "path": item["path"],
                "change_type": item["change_type"],
                "added_line_count": item["added_line_count"],
                "deleted_line_count": item["deleted_line_count"],
            }
            for item in files
            if isinstance(item, Mapping)
            and isinstance(item.get("path"), str)
            and isinstance(item.get("change_type"), str)
            and _is_strict_int(item.get("added_line_count"))
            and item["added_line_count"] >= 0
            and _is_strict_int(item.get("deleted_line_count"))
            and item["deleted_line_count"] >= 0
        ]

    findings = payload.get("deterministic_findings")
    if isinstance(findings, Sequence) and not isinstance(findings, (str, bytes)):
        safe_payload["deterministic_findings"] = [
            {
                "rule_id": item["rule_id"],
                "severity": item["severity"],
                "path": item["path"],
                "new_line": item["new_line"],
                "redaction_category": item["redaction_category"],
            }
            for item in findings
            if isinstance(item, Mapping)
            and isinstance(item.get("rule_id"), str)
            and isinstance(item.get("severity"), str)
            and isinstance(item.get("path"), str)
            and (
                item.get("new_line") is None
                or (
                    _is_strict_int(item.get("new_line"))
                    and item["new_line"] > 0
                )
            )
            and isinstance(item.get("redaction_category"), str)
        ]

    return safe_payload


def redact_ai_finding(finding: FindingDraft) -> SanitizedFinding:
    """Convert a schema-validated AI draft to the strict public finding model."""

    if finding.source is not FindingSource.AI:
        raise ValueError("AI finding redaction requires source=ai")

    return SanitizedFinding(
        rule_id=finding.rule_id,
        rule_version=finding.rule_version,
        source=finding.source,
        severity=finding.severity,
        path=finding.path,
        new_line=finding.new_line,
        excerpt=REDACTED_CREDENTIAL,
        message=REDACTED_PROVIDER_MESSAGE,
        suggestion=REDACTED_PROVIDER_SUGGESTION,
        redacted=True,
        redaction_version=REDACTION_VERSION,
        redaction_category="provider_text",
    )
