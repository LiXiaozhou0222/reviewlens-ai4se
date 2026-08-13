"""Public failure boundaries for the private credential Vault."""

import json
from pathlib import Path

import pytest

from app.credentials.service import VaultService, VaultUnlockError


FAKE_API_KEY = "fake-api-key-for-vault-failure-tests"
MASTER_PASSWORD = "test-only-vault-password"
PUBLIC_UNLOCK_FAILURE = "Vault unlock failed"


def _initialized_service(tmp_path: Path) -> VaultService:
    vault_path = tmp_path / "credentials" / "vault.json"
    service = VaultService(vault_path)
    service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )
    return service


def test_wrong_password_returns_uniform_failure(tmp_path: Path) -> None:
    """A wrong password must not disclose cryptographic implementation details."""
    service = _initialized_service(tmp_path)

    with pytest.raises(VaultUnlockError) as raised:
        service.unlock(master_password="wrong-test-only-password")

    assert str(raised.value) == PUBLIC_UNLOCK_FAILURE
    assert raised.value.__cause__ is None
    assert "InvalidTag" not in str(raised.value)


def test_successive_wrong_passwords_apply_incremental_delay_without_error_oracle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Failed unlocks slow down incrementally without changing the public error."""
    service = _initialized_service(tmp_path)
    observed_delays: list[float] = []
    monkeypatch.setattr("app.credentials.service.time.sleep", observed_delays.append)

    failures: list[VaultUnlockError] = []
    for _ in range(2):
        with pytest.raises(VaultUnlockError) as raised:
            service.unlock(master_password="wrong-test-only-password")
        failures.append(raised.value)

    assert all(str(failure) == PUBLIC_UNLOCK_FAILURE for failure in failures)
    assert all(failure.__cause__ is None for failure in failures)
    assert len(observed_delays) == 2
    assert observed_delays[0] > 0
    assert observed_delays[1] > observed_delays[0]


def test_unlock_delay_caps_and_success_resets_the_failure_counter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Capped failed attempts remain uniform and a successful unlock resets delay."""
    service = _initialized_service(tmp_path)
    observed_delays: list[float] = []
    monkeypatch.setattr("app.credentials.service.time.sleep", observed_delays.append)

    failures: list[VaultUnlockError] = []
    for _ in range(6):
        with pytest.raises(VaultUnlockError) as raised:
            service.unlock(master_password="wrong-test-only-password")
        failures.append(raised.value)

    assert all(str(failure) == PUBLIC_UNLOCK_FAILURE for failure in failures)
    assert all(failure.__cause__ is None for failure in failures)
    assert observed_delays == pytest.approx([0.05, 0.1, 0.15, 0.2, 0.25, 0.25])
    assert max(observed_delays) <= 0.25

    service.unlock(master_password=MASTER_PASSWORD)

    with pytest.raises(VaultUnlockError) as raised:
        service.unlock(master_password="wrong-test-only-password")

    assert str(raised.value) == PUBLIC_UNLOCK_FAILURE
    assert raised.value.__cause__ is None
    assert observed_delays[-1] == 0.05


def test_tampered_vault_returns_the_same_uniform_failure(tmp_path: Path) -> None:
    """Corrupt ciphertext must not create a distinct public failure oracle."""
    service = _initialized_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    payload = json.loads(vault_path.read_text(encoding="utf-8"))
    payload["cipher"]["tag"] = "AAAAAAAAAAAAAAAAAAAAAA=="
    vault_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(VaultUnlockError) as raised:
        service.unlock(master_password=MASTER_PASSWORD)

    assert str(raised.value) == PUBLIC_UNLOCK_FAILURE
    assert raised.value.__cause__ is None
