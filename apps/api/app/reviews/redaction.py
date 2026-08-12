from collections.abc import Mapping

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
    """Build the current provider contract from controlled values only.

    Provider-bound fields will be added deliberately by the provider task.  Until
    then, no caller-supplied text, mappings, or collection values are admitted.
    """

    del payload
    return {"output_schema_version": REDACTION_VERSION}


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
