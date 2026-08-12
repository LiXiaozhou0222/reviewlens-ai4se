"""Lifecycle management contracts for the private credential Vault."""

import json
from pathlib import Path

import pytest

from app.credentials.service import VaultService, VaultUnlockError


MASTER_PASSWORD = "test-only-vault-password"
FAKE_API_KEY = "fake-api-key-ending-9F2A"
REPLACEMENT_FAKE_API_KEY = "replacement-fake-key-ending-7B3C"


def _initialized_and_unlocked_service(tmp_path: Path) -> VaultService:
    service = VaultService(tmp_path / "credentials" / "vault.json")
    service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )
    service.unlock(master_password=MASTER_PASSWORD)
    return service


def test_clear_removes_file_and_memory_credential(tmp_path: Path) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"

    service.clear(master_password=MASTER_PASSWORD)

    assert vault_path.exists() is False
    assert service.is_unlocked is False
    assert service.unlocked_api_key is None
    assert service.status() == {
        "exists": False,
        "unlocked": False,
        "provider": None,
        "model": None,
        "masked_api_key": None,
    }


def test_update_replaces_old_key_and_returns_service_to_locked_state(
    tmp_path: Path,
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"

    service.update(
        master_password=MASTER_PASSWORD,
        api_key=REPLACEMENT_FAKE_API_KEY,
        model="gpt-replacement-model",
    )

    assert service.is_unlocked is False
    assert service.unlocked_api_key is None
    serialized_vault = vault_path.read_text(encoding="utf-8")
    assert FAKE_API_KEY not in serialized_vault
    assert REPLACEMENT_FAKE_API_KEY not in serialized_vault

    service.unlock(master_password=MASTER_PASSWORD)

    assert service.unlocked_api_key == REPLACEMENT_FAKE_API_KEY
    assert service.unlocked_api_key != FAKE_API_KEY


def test_lock_clears_in_memory_credential(tmp_path: Path) -> None:
    service = _initialized_and_unlocked_service(tmp_path)

    service.lock()

    assert service.is_unlocked is False
    assert service.unlocked_api_key is None


def test_restart_starts_locked_even_when_vault_exists(tmp_path: Path) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"

    restarted_service = VaultService(vault_path)

    assert restarted_service.is_unlocked is False
    assert restarted_service.unlocked_api_key is None
    assert restarted_service.status()["exists"] is True


def test_status_returns_only_masked_tail_and_never_full_key(tmp_path: Path) -> None:
    service = _initialized_and_unlocked_service(tmp_path)

    status = service.status()
    serialized_status = json.dumps(status, ensure_ascii=False)

    assert status == {
        "exists": True,
        "unlocked": True,
        "provider": "openai",
        "model": "gpt-test-model",
        "masked_api_key": "••••9F2A",
    }
    assert FAKE_API_KEY not in serialized_status


def test_wrong_password_management_operations_share_failure_and_preserve_state(
    tmp_path: Path,
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    original_file = vault_path.read_bytes()
    original_status = service.status()
    original_memory_key = service.unlocked_api_key

    operations = (
        lambda: service.update(
            master_password="wrong-test-only-password",
            api_key=REPLACEMENT_FAKE_API_KEY,
            model="gpt-replacement-model",
        ),
        lambda: service.clear(master_password="wrong-test-only-password"),
    )

    for operation in operations:
        with pytest.raises(VaultUnlockError) as raised:
            operation()

        assert type(raised.value) is VaultUnlockError
        assert str(raised.value) == "Vault unlock failed"
        assert vault_path.read_bytes() == original_file
        assert service.status() == original_status
        assert service.unlocked_api_key == original_memory_key
        assert service.is_unlocked is True

    serialized_vault = vault_path.read_text(encoding="utf-8")
    assert REPLACEMENT_FAKE_API_KEY not in serialized_vault
    assert "gpt-replacement-model" not in serialized_vault


def test_initialize_existing_vault_fails_without_changing_disk_or_memory(
    tmp_path: Path,
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    original_file = vault_path.read_bytes()
    original_memory_key = service.unlocked_api_key

    with pytest.raises(VaultUnlockError) as raised:
        service.initialize(
            master_password="replacement-test-only-password",
            api_key=REPLACEMENT_FAKE_API_KEY,
            model="gpt-replacement-model",
        )

    assert type(raised.value) is VaultUnlockError
    assert str(raised.value) == "Vault unlock failed"
    assert vault_path.read_bytes() == original_file
    assert service.unlocked_api_key == original_memory_key
    assert service.is_unlocked is True


@pytest.mark.parametrize("invalid_key_tail", ["ABC", "ABCDE"])
def test_status_rejects_key_tail_that_is_not_exactly_four_characters(
    tmp_path: Path, invalid_key_tail: str
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    payload = json.loads(vault_path.read_text(encoding="utf-8"))
    payload["key_tail"] = invalid_key_tail
    vault_path.write_text(json.dumps(payload), encoding="utf-8")

    status = service.status()

    assert status["masked_api_key"] is None


def test_status_preserves_memory_unlock_state_after_external_vault_deletion(
    tmp_path: Path,
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"

    vault_path.unlink()

    assert service.status() == {
        "exists": False,
        "unlocked": True,
        "provider": None,
        "model": None,
        "masked_api_key": None,
    }
    assert service.unlocked_api_key == FAKE_API_KEY


def test_update_rotates_salt_and_nonce(tmp_path: Path) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    original_payload = json.loads(vault_path.read_text(encoding="utf-8"))

    service.update(
        master_password=MASTER_PASSWORD,
        api_key=REPLACEMENT_FAKE_API_KEY,
        model="gpt-replacement-model",
    )

    replacement_payload = json.loads(vault_path.read_text(encoding="utf-8"))
    assert replacement_payload["kdf"]["salt"] != original_payload["kdf"]["salt"]
    assert (
        replacement_payload["cipher"]["nonce"]
        != original_payload["cipher"]["nonce"]
    )


def test_failed_atomic_update_preserves_prior_usable_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _initialized_and_unlocked_service(tmp_path)
    vault_path = tmp_path / "credentials" / "vault.json"
    original_file = vault_path.read_bytes()

    def fail_replace(_source: Path, _destination: Path) -> None:
        raise OSError("simulated atomic replacement failure")

    monkeypatch.setattr("app.credentials.vault.os.replace", fail_replace)

    with pytest.raises(OSError, match="simulated atomic replacement failure"):
        service.update(
            master_password=MASTER_PASSWORD,
            api_key=REPLACEMENT_FAKE_API_KEY,
            model="gpt-replacement-model",
        )

    assert vault_path.read_bytes() == original_file
    assert REPLACEMENT_FAKE_API_KEY not in vault_path.read_text(encoding="utf-8")
    assert service.unlocked_api_key == FAKE_API_KEY

    restarted_service = VaultService(vault_path)
    restarted_service.unlock(master_password=MASTER_PASSWORD)
    assert restarted_service.unlocked_api_key == FAKE_API_KEY
    assert restarted_service.status()["model"] == "gpt-test-model"


def test_short_key_status_never_exposes_full_key(tmp_path: Path) -> None:
    short_fake_key = "abc"
    service = VaultService(tmp_path / "credentials" / "vault.json")
    service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=short_fake_key,
        model="gpt-test-model",
    )
    service.unlock(master_password=MASTER_PASSWORD)

    status = service.status()
    serialized_status = json.dumps(status, ensure_ascii=False)

    assert status["masked_api_key"] is None
    assert short_fake_key not in serialized_status
