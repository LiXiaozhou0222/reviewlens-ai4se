from collections.abc import Mapping

from app.models.api import ReportView, SanitizedFinding
from app.models.domain import AIReviewStatus, FindingSource, Severity
from app.providers.base import ProviderReviewResult
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


class _RecordingProvider:
    def __init__(self, result: ProviderReviewResult) -> None:
        self.result = result
        self.calls: list[Mapping[str, object]] = []

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult:
        self.calls.append(payload)
        return self.result


class _FailingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult:
        assert payload == {"output_schema_version": "1.0.0"}
        self.calls += 1
        raise RuntimeError("provider internals must not escape")


def _raw_diff_with_secret() -> bytes:
    return (
        "diff --git a/src/settings.py b/src/settings.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1 @@\n"
        '+API_KEY = "rl_fake_credential_T10_3_X2YZ"\n'
    ).encode("utf-8")


def _ai_finding() -> SanitizedFinding:
    return SanitizedFinding(
        rule_id="AI-001",
        rule_version="1.0.0",
        source=FindingSource.AI,
        severity=Severity.LOW,
        path="provider/ai-review",
        new_line=1,
        excerpt="[REDACTED_CREDENTIAL]",
        message="Provider-supplied text was withheld for safety.",
        suggestion="Review the deterministic findings before applying any provider suggestion.",
        redacted=True,
        redaction_version="1.0.0",
        redaction_category="provider_text",
    )


def test_ai_failure_preserves_redacted_deterministic_report() -> None:
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.TIMEOUT,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(),
        )
    )

    first_report = create_review(_raw_diff_with_secret(), provider=provider)
    second_report = create_review(_raw_diff_with_secret(), provider=provider)

    assert first_report == second_report
    assert first_report.deterministic_risk is Severity.CRITICAL
    assert first_report.ai_status is AIReviewStatus.TIMEOUT
    assert first_report.provider == "mock"
    assert first_report.model == "mock-reviewlens-v1"
    assert [finding.rule_id for finding in first_report.findings] == ["GEN-001"]
    assert len(provider.calls) == 2
    assert all(call == {"output_schema_version": "1.0.0"} for call in provider.calls)

    serialized = first_report.model_dump_json()
    assert "rl_fake_credential_T10_3_X2YZ" not in serialized
    assert "API_KEY" not in serialized
    assert "raw_excerpt" not in serialized


def test_ai_success_appends_sanitized_provider_finding_without_changing_risk() -> None:
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(_ai_finding(),),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.deterministic_risk is Severity.CRITICAL
    assert report.ai_status is AIReviewStatus.SUCCEEDED
    assert report.provider == "mock"
    assert report.model == "mock-reviewlens-v1"
    assert [finding.rule_id for finding in report.findings] == ["GEN-001", "AI-001"]
    assert report.findings[1].source is FindingSource.AI
    assert all(isinstance(finding, SanitizedFinding) for finding in report.findings)
    assert provider.calls == [{"output_schema_version": "1.0.0"}]


def test_ai_failure_discards_provider_findings() -> None:
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.INVALID_RESPONSE,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(_ai_finding(),),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_provider_exception_preserves_deterministic_report() -> None:
    provider = _FailingProvider()

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert provider.calls == 1
    assert report.ai_status is AIReviewStatus.PROVIDER_UNAVAILABLE
    assert report.provider is None
    assert report.model is None
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]
    assert "provider internals must not escape" not in report.model_dump_json()
