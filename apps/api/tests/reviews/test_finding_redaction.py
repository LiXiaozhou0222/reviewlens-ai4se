from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity
from app.reviews.redaction import redact_finding


def test_gen_001_never_retains_secret_or_tail() -> None:
    fake_secret = "rl_fake_credential_T06_1_Q9ZX"
    finding = FindingDraft(
        rule_id="GEN-001",
        rule_version="1.0.0",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.CRITICAL,
        path="config/settings.py",
        new_line=7,
        raw_excerpt=f'API_KEY = "{fake_secret}"',
        message=f'API_KEY contains the exposed credential {fake_secret} with tail Q9ZX.',
        suggestion=f'Remove API_KEY={fake_secret}; never retain the Q9ZX tail.',
    )

    sanitized = redact_finding(finding)

    assert sanitized.rule_id == "GEN-001"
    assert sanitized.path == "config/settings.py"
    assert sanitized.new_line == 7
    assert sanitized.excerpt == "[REDACTED_CREDENTIAL]"
    assert sanitized.redacted is True
    assert sanitized.redaction_category == "credential"

    export_safe_payload = sanitized.model_dump_json()
    assert fake_secret not in export_safe_payload
    assert "Q9ZX" not in export_safe_payload
    assert "API_KEY" not in export_safe_payload
