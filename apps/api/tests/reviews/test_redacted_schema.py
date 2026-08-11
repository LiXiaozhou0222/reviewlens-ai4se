import pytest
from pydantic import ValidationError

from app.models.domain import FindingSource, Severity
from app.reviews.schemas import SanitizedFinding


def test_sanitized_finding_has_no_raw_secret_field() -> None:
    public_fields = {
        "rule_id": "GEN-001",
        "rule_version": "1.0.0",
        "source": FindingSource.GENERAL_RULE,
        "severity": Severity.CRITICAL,
        "path": "src/example.ts",
        "new_line": 7,
        "excerpt": "[REDACTED_CREDENTIAL]",
        "message": "A credential-like value was added and redacted.",
        "suggestion": "Remove the credential and use a secure secret store.",
        "redacted": True,
        "redaction_version": "1.0.0",
        "redaction_category": "credential",
    }

    finding = SanitizedFinding(**public_fields)
    serialized = finding.model_dump()

    assert serialized == public_fields
    assert "raw_excerpt" not in serialized
    assert "match_start" not in serialized

    for forbidden_field, forbidden_value in (
        ("raw_excerpt", "rl_fake_token_for_schema_test"),
        ("match_start", 4),
        ("raw_secret", "rl_fake_token_for_schema_test"),
    ):
        with pytest.raises(ValidationError):
            SanitizedFinding(
                **public_fields,
                **{forbidden_field: forbidden_value},
            )
