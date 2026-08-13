from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.api import FindingDraft, ReportView, SanitizedFinding
from app.models.domain import AIReviewStatus, FindingSource, ReviewMode, Severity


def test_review_mode_and_severity_values_are_fixed() -> None:
    assert [(member.name, member.value) for member in ReviewMode] == [
        ("PRIVATE", "private"),
        ("DEMO", "demo"),
    ]
    assert [(member.name, member.value) for member in Severity] == [
        ("CRITICAL", "Critical"),
        ("HIGH", "High"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
        ("NONE", "None"),
    ]


def test_finding_source_and_ai_review_status_values_are_fixed() -> None:
    assert [(member.name, member.value) for member in FindingSource] == [
        ("GENERAL_RULE", "general_rule"),
        ("LANGUAGE_RULE", "language_rule"),
        ("AI", "ai"),
    ]
    assert [(member.name, member.value) for member in AIReviewStatus] == [
        ("NOT_CONFIGURED", "NOT_CONFIGURED"),
        ("PENDING", "PENDING"),
        ("SUCCEEDED", "SUCCEEDED"),
        ("AUTH_FAILED", "AUTH_FAILED"),
        ("MODEL_UNAVAILABLE", "MODEL_UNAVAILABLE"),
        ("RATE_LIMITED", "RATE_LIMITED"),
        ("TIMEOUT", "TIMEOUT"),
        ("INPUT_TOO_LARGE", "INPUT_TOO_LARGE"),
        ("INVALID_RESPONSE", "INVALID_RESPONSE"),
        ("PROVIDER_UNAVAILABLE", "PROVIDER_UNAVAILABLE"),
    ]


def test_report_view_requires_sanitized_findings() -> None:
    """A report accepts sanitized findings only and cannot receive raw excerpts."""
    draft = FindingDraft(
        rule_id="RL001",
        rule_version="1.0.0",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.HIGH,
        path="src/example.py",
        new_line=12,
        raw_excerpt="synthetic non-secret source context",
        message="Avoid unsafe pattern.",
        suggestion="Use the safe alternative.",
    )
    report_fields = {
        "report_id": uuid4(),
        "created_at": datetime(2026, 8, 9, tzinfo=UTC),
        "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
        "diff_sha256": "a" * 64,
        "deterministic_risk": Severity.HIGH,
        "ai_status": AIReviewStatus.SUCCEEDED,
        "provider": "example-provider",
        "model": "example-model",
        "ruleset_version": "1.0.0",
        "app_version": "0.1.0",
    }

    with pytest.raises(ValidationError):
        ReportView(**report_fields, findings=[draft])

    finding = SanitizedFinding(
        rule_id="RL001",
        rule_version="1.0.0",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.HIGH,
        path="src/example.py",
        new_line=12,
        excerpt="synthetic sanitized context",
        message="Avoid unsafe pattern.",
        suggestion="Use the safe alternative.",
        redacted=True,
        redaction_version="1.0.0",
        redaction_category="credential",
    )

    assert ReportView(**report_fields, findings=[finding]).findings == [finding]

    with pytest.raises(ValidationError):
        SanitizedFinding(
            **finding.model_dump(), raw_excerpt="synthetic non-secret source context"
        )
