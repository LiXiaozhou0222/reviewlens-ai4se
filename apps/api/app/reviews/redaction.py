from app.models.api import FindingDraft, SanitizedFinding


REDACTION_VERSION = "1.0.0"
REDACTED_CREDENTIAL = "[REDACTED_CREDENTIAL]"
REDACTED_CREDENTIAL_MESSAGE = "A credential-like value was added and redacted."
REDACTED_CREDENTIAL_SUGGESTION = (
    "Remove the credential and use a secure secret store."
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
