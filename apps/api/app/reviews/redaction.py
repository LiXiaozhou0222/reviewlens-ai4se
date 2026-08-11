import re
from collections.abc import Mapping

from app.models.api import FindingDraft, SanitizedFinding
from app.models.domain import FindingSource
from app.rules.general import replace_literal_credentials


REDACTION_VERSION = "1.0.0"
REDACTED_CREDENTIAL = "[REDACTED_CREDENTIAL]"
REDACTED_CREDENTIAL_MESSAGE = "A credential-like value was added and redacted."
REDACTED_CREDENTIAL_SUGGESTION = (
    "Remove the credential and use a secure secret store."
)
_FORBIDDEN_PROVIDER_FIELDS = frozenset({"raw_prompt", "raw_response"})
_CREDENTIAL_TOKEN = re.compile(
    r"(?i)(?:rl_fake_(?:credential|token)[A-Za-z0-9_-]*|sk-[A-Za-z0-9_-]{8,})"
)


def redact_finding(finding: FindingDraft) -> SanitizedFinding:
    if finding.rule_id != "GEN-001":
        raise ValueError("T06.1 only supports GEN-001 credential findings")

    return SanitizedFinding(
        rule_id=finding.rule_id,
        rule_version=finding.rule_version,
        source=finding.source,
        severity=finding.severity,
        path=finding.path,
        new_line=finding.new_line,
        excerpt=REDACTED_CREDENTIAL,
        message=REDACTED_CREDENTIAL_MESSAGE,
        suggestion=REDACTED_CREDENTIAL_SUGGESTION,
        redacted=True,
        redaction_version=REDACTION_VERSION,
        redaction_category="credential",
    )


def redact_provider_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Return a detached provider payload without raw artifacts or credential tokens."""

    return {
        key: _redact_payload_value(value)
        for key, value in payload.items()
        if key not in _FORBIDDEN_PROVIDER_FIELDS
    }


def redact_ai_finding(finding: FindingDraft) -> SanitizedFinding:
    """Convert a schema-validated AI draft to the strict public finding model."""

    if finding.source is not FindingSource.AI:
        raise ValueError("AI finding redaction requires source=ai")

    public_text = (finding.raw_excerpt, finding.message, finding.suggestion)
    contains_credential = any(
        _redact_sensitive_text(value) != value for value in public_text
    )
    if contains_credential:
        return SanitizedFinding(
            rule_id=finding.rule_id,
            rule_version=finding.rule_version,
            source=finding.source,
            severity=finding.severity,
            path=finding.path,
            new_line=finding.new_line,
            excerpt=REDACTED_CREDENTIAL,
            message=REDACTED_CREDENTIAL_MESSAGE,
            suggestion=REDACTED_CREDENTIAL_SUGGESTION,
            redacted=True,
            redaction_version=REDACTION_VERSION,
            redaction_category="credential",
        )

    return SanitizedFinding(
        rule_id=finding.rule_id,
        rule_version=finding.rule_version,
        source=finding.source,
        severity=finding.severity,
        path=finding.path,
        new_line=finding.new_line,
        excerpt=finding.raw_excerpt,
        message=finding.message,
        suggestion=finding.suggestion,
        redacted=False,
        redaction_version=REDACTION_VERSION,
        redaction_category=None,
    )


def _redact_payload_value(value: object) -> object:
    if isinstance(value, str):
        return _redact_sensitive_text(value)
    if isinstance(value, Mapping):
        return redact_provider_payload(value)
    if isinstance(value, list):
        return [_redact_payload_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_payload_value(item) for item in value)
    return value


def _redact_sensitive_text(value: str) -> str:
    without_assignments = replace_literal_credentials(value, REDACTED_CREDENTIAL)
    return _CREDENTIAL_TOKEN.sub(REDACTED_CREDENTIAL, without_assignments)
