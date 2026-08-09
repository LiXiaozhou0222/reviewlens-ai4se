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
