from app.models.api import ReportView, SanitizedFinding
from app.models.domain import AIReviewStatus, Severity
from app.reviews.service import create_review


def test_create_review_returns_redacted_deterministic_report() -> None:
    fake_credential = "rl_fake_credential_T10_1_Q9ZX"
    raw_diff = (
        "diff --git a/src/settings.py b/src/settings.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1 @@\n"
        f'+API_KEY = "{fake_credential}"\n'
    ).encode("utf-8")

    first_report = create_review(raw_diff)
    second_report = create_review(raw_diff)

    assert isinstance(first_report, ReportView)
    assert first_report == second_report
    assert first_report.deterministic_risk is Severity.CRITICAL
    assert first_report.ai_status is AIReviewStatus.NOT_CONFIGURED
    assert first_report.provider is None
    assert first_report.model is None
    assert len(first_report.findings) == 1
    assert all(isinstance(finding, SanitizedFinding) for finding in first_report.findings)

    serialized = first_report.model_dump_json()
    assert fake_credential not in serialized
    assert "API_KEY" not in serialized
    assert "raw_excerpt" not in serialized


def test_create_review_sanitizes_all_fixed_rule_findings() -> None:
    raw_diff = (
        "diff --git a/src/example.ts b/src/example.ts\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/example.ts\n"
        "+++ b/src/example.ts\n"
        "@@ -0,0 +1,2 @@\n"
        '+console.log("debug detail")\n'
        "+// TODO: remove this temporary implementation\n"
    ).encode("utf-8")

    report = create_review(raw_diff)

    assert [finding.rule_id for finding in report.findings] == ["JS-001", "GEN-003"]
    assert all(finding.redacted for finding in report.findings)
    assert all(
        finding.excerpt == "[REDACTED_FINDING_CONTEXT]"
        for finding in report.findings
    )
    assert "debug detail" not in report.model_dump_json()
