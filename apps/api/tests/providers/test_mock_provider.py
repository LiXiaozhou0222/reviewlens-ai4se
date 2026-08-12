import socket

import pytest

from app.models.domain import AIReviewStatus, FindingSource
from app.providers.mock_provider import MockReviewProvider


def test_mock_result_is_repeatable_and_network_free(monkeypatch) -> None:
    input_text = "untrusted diff text must never be echoed"

    def fail_if_network_is_used(*args: object, **kwargs: object) -> None:
        raise AssertionError("Mock provider must not access the network")

    monkeypatch.setattr(socket, "create_connection", fail_if_network_is_used)
    monkeypatch.setattr(socket.socket, "connect", fail_if_network_is_used)

    with socket.socket() as probe_socket, pytest.raises(
        AssertionError, match="Mock provider must not access the network"
    ):
        probe_socket.connect(("127.0.0.1", 9))

    provider = MockReviewProvider()

    first_result = provider.review({"diff": input_text, "path": "src/example.py"})
    second_result = provider.review({"diff": input_text, "path": "src/example.py"})

    assert first_result == second_result
    assert first_result.provider == "mock"
    assert first_result.model == "mock-reviewlens-v1"
    assert first_result.status is AIReviewStatus.SUCCEEDED
    assert len(first_result.findings) == 1
    assert first_result.findings[0].source is FindingSource.AI
    assert input_text not in first_result.model_dump_json()
