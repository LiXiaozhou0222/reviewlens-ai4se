import json
from collections.abc import Mapping

import pytest

from app.models.api import ReportView, SanitizedFinding
from app.models.domain import AIReviewStatus, FindingSource, Severity
from app.providers.base import ProviderReviewResult
from app.reviews.redaction import redact_provider_payload
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
    def __init__(
        self,
        result: ProviderReviewResult,
        *,
        provider_name: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.result = result
        self.provider_name = provider_name or result.provider
        self.model_name = model_name or result.model
        self.calls: list[Mapping[str, object]] = []

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult:
        self.calls.append(payload)
        return self.result


class _FailingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult:
        assert payload["output_schema_version"] == "1.0.0"
        self.calls += 1
        raise RuntimeError("provider internals must not escape")


class _MalformedProvider:
    def __init__(self, result: object) -> None:
        self.result = result

    def review(self, payload: Mapping[str, object]) -> object:
        del payload
        return self.result


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


def _model_constructed_ai_finding(**updates: object) -> SanitizedFinding:
    values = _ai_finding().model_dump()
    values.update(updates)
    return SanitizedFinding.model_construct(**values)


def _model_constructed_provider_result(
    *,
    status: object = AIReviewStatus.SUCCEEDED,
    provider: object = "mock",
    model: object = "mock-reviewlens-v1",
    findings: object = (),
) -> ProviderReviewResult:
    return ProviderReviewResult.model_construct(
        status=status,
        provider=provider,
        model=model,
        findings=findings,
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
    assert all(call["output_schema_version"] == "1.0.0" for call in provider.calls)

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
    assert len(provider.calls) == 1
    assert provider.calls[0]["output_schema_version"] == "1.0.0"


def test_provider_payload_contains_redacted_material_for_the_current_diff() -> None:
    fake_credential = "rl_fake_credential_T10_3_PAYLOAD_Q7XZ"
    raw_diff = (
        "diff --git a/src/settings.py b/src/settings.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1,2 @@\n"
        f'+API_KEY = "{fake_credential}"\n'
        '+console.log("review this added line")\n'
    ).encode("utf-8")


    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(),
        )
    )

    create_review(raw_diff, provider=provider)

    assert len(provider.calls) == 1
    payload = provider.calls[0]
    serialized_payload = json.dumps(payload, sort_keys=True)
    assert payload["output_schema_version"] == "1.0.0"
    assert "src/settings.py" in serialized_payload
    assert "GEN-001" in serialized_payload
    assert "Critical" in serialized_payload
    assert fake_credential not in serialized_payload
    assert "raw_excerpt" not in serialized_payload


def test_service_rejects_provider_findings_that_violate_public_safety_invariants() -> None:
    provider_secret = "rl_fake_provider_secret_T10_3_Q8WV"
    unsafe_finding = SanitizedFinding(
        rule_id="AI-UNSAFE",
        rule_version="1.0.0",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.CRITICAL,
        path="provider/unsafe",
        new_line=1,
        excerpt=provider_secret,
        message=f"unsafe provider text {provider_secret}",
        suggestion=f"retain {provider_secret}",
        redacted=False,
        redaction_version="attacker-controlled",
        redaction_category=None,
    )
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(unsafe_finding,),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]
    assert all(finding.redacted for finding in report.findings)
    assert provider_secret not in report.model_dump_json()


def test_model_construct_cannot_bypass_provider_finding_severity_validation() -> None:
    forged_finding = _model_constructed_ai_finding(severity="catastrophic")
    forged_result = _model_constructed_provider_result(findings=(forged_finding,))
    provider = _RecordingProvider(forged_result)

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_model_construct_cannot_bypass_provider_status_validation() -> None:
    forged_result = _model_constructed_provider_result(status="TRUST_PROVIDER")
    provider = _RecordingProvider(forged_result)

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_model_constructed_nested_non_finding_invalidates_entire_response() -> None:
    forged_result = _model_constructed_provider_result(
        findings=({"severity": "Low", "message": "not a canonical finding"},)
    )
    provider = _RecordingProvider(forged_result)

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


@pytest.mark.parametrize(
    ("metadata_field", "invalid_value"),
    [
        ("provider", {"untrusted": "provider metadata"}),
        ("model", ["untrusted", "model", "metadata"]),
    ],
)
def test_model_construct_cannot_bypass_provider_metadata_validation(
    metadata_field: str,
    invalid_value: object,
) -> None:
    result_values: dict[str, object] = {
        "provider": "mock",
        "model": "mock-reviewlens-v1",
    }
    result_values[metadata_field] = invalid_value
    forged_result = _model_constructed_provider_result(**result_values)
    provider = _RecordingProvider(
        forged_result,
        provider_name=result_values["provider"],  # type: ignore[arg-type]
        model_name=result_values["model"],  # type: ignore[arg-type]
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.provider is None
    assert report.model is None
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


@pytest.mark.parametrize(
    ("metadata_field", "invalid_value"),
    [
        ("redacted", "yes"),
        ("redaction_version", ["1.0.0"]),
        ("redaction_category", {"category": "provider_text"}),
    ],
)
def test_model_construct_cannot_bypass_finding_redaction_metadata_validation(
    metadata_field: str,
    invalid_value: object,
) -> None:
    forged_finding = _model_constructed_ai_finding(
        **{metadata_field: invalid_value}
    )
    forged_result = _model_constructed_provider_result(findings=(forged_finding,))
    provider = _RecordingProvider(forged_result)

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_one_model_constructed_invalid_finding_rejects_entire_valid_batch() -> None:
    valid_finding = _ai_finding()
    forged_finding = _model_constructed_ai_finding(severity="catastrophic")
    forged_result = _model_constructed_provider_result(
        findings=(valid_finding, forged_finding)
    )
    provider = _RecordingProvider(forged_result)

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_service_rejects_provider_finding_with_untrusted_rule_version() -> None:
    provider_secret = "rl_fake_provider_rule_version_T10_3_R1_Q5MX"
    unsafe_finding = _ai_finding().model_copy(
        update={"rule_version": provider_secret}
    )
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(unsafe_finding,),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]
    assert provider_secret not in report.model_dump_json()


@pytest.mark.parametrize("invalid_line", [-7, 0, True])
def test_service_rejects_provider_finding_with_invalid_new_line(
    invalid_line: object,
) -> None:
    safe_finding = _ai_finding()
    unsafe_finding = SanitizedFinding.model_construct(
        **{
            **safe_finding.model_dump(),
            "new_line": invalid_line,
        }
    )
    assert unsafe_finding.new_line is invalid_line or unsafe_finding.new_line == invalid_line
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(unsafe_finding,),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


@pytest.mark.parametrize(
    ("returned_provider", "returned_model"),
    [
        ("rl_fake_provider_identity_T10_3_R2_Q4NV", "mock-reviewlens-v1"),
        ("mock", "rl_fake_model_identity_T10_3_R2_W6KX"),
    ],
)
def test_untrusted_provider_identity_is_not_returned_in_report(
    returned_provider: str,
    returned_model: str,
) -> None:
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider=returned_provider,
            model=returned_model,
            findings=(_ai_finding(),),
        ),
        provider_name="mock",
        model_name="mock-reviewlens-v1",
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.provider is None
    assert report.model is None
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]
    serialized = report.model_dump_json()
    assert returned_provider not in serialized
    assert returned_model not in serialized


@pytest.mark.parametrize("malformed_result", [None, object(), {"status": "SUCCEEDED"}])
def test_malformed_provider_return_preserves_deterministic_report(
    malformed_result: object,
) -> None:
    report = create_review(
        _raw_diff_with_secret(),
        provider=_MalformedProvider(malformed_result),  # type: ignore[arg-type]
    )

    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.provider is None
    assert report.model is None
    assert report.deterministic_risk is Severity.CRITICAL
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]


def test_provider_payload_drops_invalid_counts_and_line_numbers() -> None:
    payload = {
        "output_schema_version": "caller-controlled",
        "files": [
            {
                "path": "src/valid.ts",
                "change_type": "modified",
                "added_line_count": 2,
                "deleted_line_count": 1,
            },
            {
                "path": "src/bool.ts",
                "change_type": "modified",
                "added_line_count": True,
                "deleted_line_count": 0,
            },
            {
                "path": "src/negative.ts",
                "change_type": "modified",
                "added_line_count": -1,
                "deleted_line_count": 0,
            },
        ],
        "deterministic_findings": [
            {
                "rule_id": "GEN-003",
                "severity": "Low",
                "path": "src/valid.ts",
                "new_line": 3,
                "redaction_category": "deterministic_rule",
            },
            {
                "rule_id": "GEN-003",
                "severity": "Low",
                "path": "src/bool.ts",
                "new_line": True,
                "redaction_category": "deterministic_rule",
            },
            {
                "rule_id": "GEN-003",
                "severity": "Low",
                "path": "src/zero.ts",
                "new_line": 0,
                "redaction_category": "deterministic_rule",
            },
            {
                "rule_id": "GEN-005",
                "severity": "Medium",
                "path": "src/file-level.ts",
                "new_line": None,
                "redaction_category": "deterministic_rule",
            },
        ],
    }

    safe_payload = redact_provider_payload(payload)

    assert safe_payload == {
        "output_schema_version": "1.0.0",
        "files": [
            {
                "path": "src/valid.ts",
                "change_type": "modified",
                "added_line_count": 2,
                "deleted_line_count": 1,
            }
        ],
        "deterministic_findings": [
            {
                "rule_id": "GEN-003",
                "severity": "Low",
                "path": "src/valid.ts",
                "new_line": 3,
                "redaction_category": "deterministic_rule",
            },
            {
                "rule_id": "GEN-005",
                "severity": "Medium",
                "path": "src/file-level.ts",
                "new_line": None,
                "redaction_category": "deterministic_rule",
            },
        ],
    }


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


def test_non_success_response_with_unsafe_finding_is_invalid_as_a_whole() -> None:
    unsafe_finding = _ai_finding().model_copy(
        update={"source": FindingSource.GENERAL_RULE, "redacted": False}
    )
    provider = _RecordingProvider(
        ProviderReviewResult(
            status=AIReviewStatus.TIMEOUT,
            provider="mock",
            model="mock-reviewlens-v1",
            findings=(unsafe_finding,),
        )
    )

    report = create_review(_raw_diff_with_secret(), provider=provider)

    assert len(provider.calls) == 1
    assert report.ai_status is AIReviewStatus.INVALID_RESPONSE
    assert report.deterministic_risk is Severity.CRITICAL
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
