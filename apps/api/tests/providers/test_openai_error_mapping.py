import json
from typing import Any

import httpx
import pytest

from app.models.domain import AIReviewStatus
from app.providers.openai_provider import OpenAIReviewProvider
from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)


class _FailingResponses:
    def create(self, **kwargs: object) -> Any:
        del kwargs
        raise APITimeoutError(
            request=httpx.Request("POST", "https://api.openai.com/v1/responses")
        )


class _FailingClient:
    responses = _FailingResponses()


def test_timeout_maps_to_public_timeout_without_raw_body() -> None:
    fake_key = "sk-fake-timeout-test-value"
    raw_body = "raw provider body with fake sensitive detail"
    payload = {"input": raw_body, "output_schema_version": "1.0.0"}
    provider = OpenAIReviewProvider(
        api_key=fake_key,
        model="gpt-fake-review-model",
        client=_FailingClient(),
    )

    result = provider.review(payload)

    assert result.status is AIReviewStatus.TIMEOUT
    serialized = result.model_dump_json()
    assert raw_body not in serialized
    assert fake_key not in serialized


class _ErrorResponses:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def create(self, **kwargs: object) -> Any:
        del kwargs
        raise self._error


class _ErrorClient:
    def __init__(self, error: Exception) -> None:
        self.responses = _ErrorResponses(error)


def _status_error(error_type: type[APIStatusError], status_code: int) -> Exception:
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    response = httpx.Response(status_code, request=request)
    return error_type(
        "raw fake provider exception text",
        response=response,
        body={"raw": "fake provider body detail"},
    )


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (_status_error(AuthenticationError, 401), AIReviewStatus.AUTH_FAILED),
        (_status_error(NotFoundError, 404), AIReviewStatus.MODEL_UNAVAILABLE),
        (_status_error(RateLimitError, 429), AIReviewStatus.RATE_LIMITED),
        (
            APIConnectionError(
                request=httpx.Request(
                    "POST", "https://api.openai.com/v1/responses"
                )
            ),
            AIReviewStatus.PROVIDER_UNAVAILABLE,
        ),
        (
            _status_error(APIStatusError, 503),
            AIReviewStatus.PROVIDER_UNAVAILABLE,
        ),
    ],
)
def test_sdk_errors_map_to_stable_public_statuses_without_details(
    error: Exception, expected_status: AIReviewStatus
) -> None:
    provider = OpenAIReviewProvider(
        api_key="fake-openai-key-for-error-mapping",
        model="gpt-fake-review-model",
        client=_ErrorClient(error),
    )

    result = provider.review({"output_schema_version": "1.0.0"})

    assert result.status is expected_status
    assert result.findings == ()
    serialized = result.model_dump_json()
    assert "raw fake provider exception text" not in serialized
    assert "fake provider body detail" not in serialized
    assert "fake-openai-key-for-error-mapping" not in serialized


class _CapturingResponses:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] | None = None

    def create(self, **kwargs: object) -> object:
        self.kwargs = kwargs
        return object()


class _CapturingClient:
    def __init__(self) -> None:
        self.responses = _CapturingResponses()


def test_official_client_and_responses_request_are_strictly_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _CapturingClient()
    constructor_kwargs: dict[str, object] = {}

    def fake_openai(**kwargs: object) -> _CapturingClient:
        constructor_kwargs.update(kwargs)
        return client

    monkeypatch.setattr("app.providers.openai_provider.OpenAI", fake_openai)
    provider = OpenAIReviewProvider(
        api_key="sk-fake-constructor-key",
        model="gpt-fake-review-model",
    )

    result = provider.review(
        {"output_schema_version": "1.0.0", "summary": "controlled summary"}
    )

    assert constructor_kwargs == {
        "api_key": "sk-fake-constructor-key",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30.0,
        "max_retries": 0,
    }
    assert client.responses.kwargs is not None
    assert client.responses.kwargs["model"] == "gpt-fake-review-model"
    assert client.responses.kwargs["store"] is False
    assert isinstance(client.responses.kwargs["input"], str)
    assert json.loads(client.responses.kwargs["input"]) == {
        "output_schema_version": "1.0.0",
    }
    instructions = str(client.responses.kwargs["instructions"]).lower()
    assert "untrusted" in instructions
    assert "do not execute" in instructions
    assert "tools" not in client.responses.kwargs
    assert "background" not in client.responses.kwargs
    assert "tool_choice" not in client.responses.kwargs
    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()


def test_uncontrolled_payload_text_never_reaches_responses_input() -> None:
    client = _CapturingClient()
    payload = {
        "output_schema_version": "caller-controlled-version",
        "raw_prompt": "demoCredentialAlpha123",
        "nested": {"raw_response": "provider-controlled-secret"},
    }
    original_payload = {
        "output_schema_version": "caller-controlled-version",
        "raw_prompt": "demoCredentialAlpha123",
        "nested": {"raw_response": "provider-controlled-secret"},
    }
    provider = OpenAIReviewProvider(
        api_key="sk-fake-redaction-boundary-key",
        model="gpt-fake-review-model",
        client=client,
    )

    provider.review(payload)

    assert client.responses.kwargs is not None
    assert json.loads(client.responses.kwargs["input"]) == {
        "output_schema_version": "1.0.0"
    }
    assert payload == original_payload


def test_environment_cannot_override_official_openai_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _CapturingClient()
    constructor_kwargs: dict[str, object] = {}

    def fake_openai(**kwargs: object) -> _CapturingClient:
        constructor_kwargs.update(kwargs)
        return client

    monkeypatch.setenv("OPENAI_BASE_URL", "https://attacker.invalid/v1")
    monkeypatch.setattr("app.providers.openai_provider.OpenAI", fake_openai)

    OpenAIReviewProvider(
        api_key="sk-fake-endpoint-boundary-key",
        model="gpt-fake-review-model",
    )

    assert constructor_kwargs["base_url"] == "https://api.openai.com/v1"


def test_response_validation_error_maps_without_raw_body() -> None:
    raw_body = "synthetic raw validation body"
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    response = httpx.Response(200, request=request, text=raw_body)
    error = APIResponseValidationError(
        response=response,
        body={"raw": raw_body},
        message="synthetic raw validation exception",
    )
    provider = OpenAIReviewProvider(
        api_key="sk-fake-validation-error-key",
        model="gpt-fake-review-model",
        client=_ErrorClient(error),
    )

    result = provider.review({"raw_prompt": "fake private payload"})

    assert result.status is AIReviewStatus.INVALID_RESPONSE
    assert result.findings == ()
    serialized = result.model_dump_json()
    assert raw_body not in serialized
    assert "synthetic raw validation exception" not in serialized
    assert "sk-fake-validation-error-key" not in serialized
    assert "fake private payload" not in serialized


class _FalseyClient(_CapturingClient):
    def __bool__(self) -> bool:
        return False


def test_falsey_injected_client_is_used_without_constructing_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _FalseyClient()

    def fail_if_sdk_is_constructed(**kwargs: object) -> object:
        del kwargs
        raise AssertionError("injected client must prevent SDK construction")

    monkeypatch.setattr("app.providers.openai_provider.OpenAI", fail_if_sdk_is_constructed)
    provider = OpenAIReviewProvider(
        api_key="sk-fake-falsey-client-key",
        model="gpt-fake-review-model",
        client=client,
    )

    result = provider.review({"output_schema_version": "1.0.0"})

    assert client.responses.kwargs is not None
    assert result.status is AIReviewStatus.INVALID_RESPONSE
