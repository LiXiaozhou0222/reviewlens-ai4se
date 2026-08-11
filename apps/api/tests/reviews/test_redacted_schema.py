from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity
from app.reviews.redaction import redact_ai_finding, redact_provider_payload
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


def test_ai_payload_and_ai_finding_are_redacted() -> None:
    fake_credential = "ordinarySecretValue123"
    credential_assignment = f'API_KEY = "{fake_credential}"'
    provider_payload = {
        "deterministic_summary": {
            "rule_id": "GEN-001",
            "details": {
                "excerpt": credential_assignment,
                "notes": [
                    f"Credential observed: {credential_assignment}",
                    {"suggestion": f"Remove {credential_assignment} immediately."},
                ],
            },
        },
        "output_schema_version": "1.0.0",
        "raw_prompt": f"Review the change containing {credential_assignment}",
        "raw_response": f"Unvalidated response containing {credential_assignment}",
    }
    ai_finding = FindingDraft(
        rule_id="AI-001",
        rule_version="1.0.0",
        source=FindingSource.AI,
        severity=Severity.HIGH,
        path="src/config.ts",
        new_line=12,
        raw_excerpt=credential_assignment,
        message=f"The added credential {credential_assignment} can be exposed.",
        suggestion=f"Remove {credential_assignment} and load it from a secret store.",
    )
    original_payload = deepcopy(provider_payload)
    original_ai_finding = ai_finding.model_dump()

    safe_payload = redact_provider_payload(provider_payload)
    safe_ai_finding = redact_ai_finding(ai_finding)

    serialized_output = f"{safe_payload!r}\n{safe_ai_finding.model_dump_json()}"
    assert credential_assignment not in serialized_output
    assert "API_KEY" not in serialized_output
    assert fake_credential not in serialized_output
    assert "Value123" not in serialized_output
    assert "raw_prompt" not in safe_payload
    assert "raw_response" not in safe_payload
    assert isinstance(safe_ai_finding, SanitizedFinding)
    assert safe_ai_finding.source is FindingSource.AI
    assert safe_ai_finding.redacted is True
    assert provider_payload == original_payload
    assert ai_finding.model_dump() == original_ai_finding
