import json

import pytest
from pydantic import ValidationError

from app.models.api import FindingDraft, SanitizedFinding
from app.models.domain import AIReviewStatus
from app.models.domain import FindingSource
from app.providers.base import ProviderReviewResult
from app.providers.openai_provider import OpenAIReviewProvider


class _FakeResponse:
    def __init__(self, output_text: object = "not valid json") -> None:
        self._output_text = output_text
        self.output_text_was_read = False

    @property
    def output_text(self) -> object:
        self.output_text_was_read = True
        return self._output_text


class _FakeResponses:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response
        self.kwargs: dict[str, object] | None = None

    def create(self, **kwargs: object) -> _FakeResponse:
        self.kwargs = kwargs
        return self._response


class _FakeClient:
    def __init__(self, response: _FakeResponse) -> None:
        self.responses = _FakeResponses(response)


def _provider_for(response: object) -> OpenAIReviewProvider:
    return OpenAIReviewProvider(
        api_key="sk-fake-schema-validation-key",
        model="gpt-fake-review-model",
        client=_FakeClient(response),
    )


def _valid_finding(**updates: object) -> dict[str, object]:
    finding: dict[str, object] = {
        "rule_id": "AI-001",
        "rule_version": "1.0.0",
        "source": "ai",
        "severity": "Low",
        "path": "provider/ai-review",
        "new_line": 4,
        "raw_excerpt": "Synthetic provider excerpt.",
        "message": "Synthetic provider explanation.",
        "suggestion": "Synthetic provider suggestion.",
    }
    finding.update(updates)
    return finding


def test_invalid_response_creates_no_ai_finding() -> None:
    response = _FakeResponse()
    provider = _provider_for(response)

    result = provider.review({"output_schema_version": "1.0.0"})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()
    assert response.output_text_was_read is True


@pytest.mark.parametrize(
    "payload",
    [
        {
            "findings": [
                {
                    key: value
                    for key, value in _valid_finding().items()
                    if key != "message"
                }
            ]
        },
        {"findings": [_valid_finding(unexpected="provider data")]},
        {"findings": [_valid_finding(severity="urgent")]},
        {"findings": [_valid_finding(new_line="4")]},
        {"findings": [_valid_finding(source="general_rule")]},
        {"findings": [_valid_finding(rule_id="provider free text")]},
        {"findings": [_valid_finding(path="provider/free-text-path")]},
        {"findings": [], "unexpected": "provider data"},
    ],
)
def test_schema_error_discards_entire_provider_output(
    payload: dict[str, object],
) -> None:
    raw_provider_text = "demoCredentialSchemaError123"
    findings = payload.get("findings")
    if isinstance(findings, list) and findings:
        findings[0]["raw_excerpt"] = raw_provider_text
    result = _provider_for(_FakeResponse(json.dumps(payload))).review({})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()
    assert raw_provider_text not in result.model_dump_json()


@pytest.mark.parametrize(
    "response",
    [
        object(),
        _FakeResponse(None),
        _FakeResponse(""),
        _FakeResponse("   "),
    ],
)
def test_missing_empty_or_refused_output_is_invalid(response: object) -> None:
    result = _provider_for(response).review({})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()


def test_valid_response_is_immediately_redacted_before_return() -> None:
    unrecognized_fake_secret = "freelyReturnedProviderSecretQ7m9"
    raw_finding = _valid_finding(
        raw_excerpt=unrecognized_fake_secret,
        message=f"Provider explained {unrecognized_fake_secret}",
        suggestion=f"Provider suggested retaining {unrecognized_fake_secret}",
    )
    response = _FakeResponse(json.dumps({"findings": [raw_finding]}))
    client = _FakeClient(response)

    result = OpenAIReviewProvider(
        api_key="sk-fake-schema-validation-key",
        model="gpt-fake-review-model",
        client=client,
    ).review({"raw_prompt": "caller private text"})

    assert result.status is AIReviewStatus.SUCCEEDED
    assert result.provider == "openai"
    assert result.model == "gpt-fake-review-model"
    assert len(result.findings) == 1
    assert isinstance(result.findings[0], SanitizedFinding)
    assert result.findings[0].source is FindingSource.AI
    assert result.findings[0].redacted is True
    serialized = result.model_dump_json()
    assert unrecognized_fake_secret not in serialized
    assert "raw_excerpt" not in serialized
    assert "match_start" not in serialized
    assert "caller private text" not in serialized
    assert client.responses.kwargs is not None
    text_config = client.responses.kwargs["text"]
    assert isinstance(text_config, dict)
    assert text_config["format"]["type"] == "json_schema"
    assert text_config["format"]["strict"] is True
    assert text_config["format"]["schema"]["additionalProperties"] is False

    with pytest.raises(ValidationError):
        ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider="openai",
            model="gpt-fake-review-model",
            findings=(FindingDraft.model_validate(raw_finding),),
        )


@pytest.mark.parametrize("invalid_line", [0, -7, True])
def test_non_positive_or_boolean_line_discards_entire_response(
    invalid_line: object,
) -> None:
    response = _FakeResponse(
        json.dumps({"findings": [_valid_finding(new_line=invalid_line)]})
    )

    result = _provider_for(response).review({})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()


def test_one_invalid_finding_discards_otherwise_valid_batch() -> None:
    valid = _valid_finding()
    invalid = _valid_finding(new_line=-7)
    response = _FakeResponse(json.dumps({"findings": [valid, invalid]}))

    result = _provider_for(response).review({})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()


def test_empty_findings_is_a_valid_successful_response() -> None:
    result = _provider_for(
        _FakeResponse(json.dumps({"findings": []}))
    ).review({})

    assert result.status is AIReviewStatus.SUCCEEDED
    assert result.findings == ()
