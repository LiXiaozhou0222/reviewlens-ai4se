import base64
import json
from pathlib import Path

import pytest

from app.credentials.service import VaultService


FAKE_API_KEY = "fake-api-key-for-vault-tests"
MASTER_PASSWORD = "test-only-vault-password"


def test_initialize_encrypts_fake_key_with_scrypt_and_aes_256_gcm(
    tmp_path: Path,
) -> None:
    """Replacing either the KDF or cipher with an unsafe choice must fail this test."""
    vault_path = tmp_path / "credentials" / "vault.json"
    service = VaultService(vault_path)

    service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )

    persisted = json.loads(vault_path.read_text(encoding="utf-8"))
    serialized = vault_path.read_text(encoding="utf-8")

    assert persisted["version"] == 1
    assert persisted["kdf"]["name"] == "scrypt"
    assert persisted["cipher"]["name"] == "AES-256-GCM"
    assert len(base64.b64decode(persisted["kdf"]["salt"])) >= 16
    assert len(base64.b64decode(persisted["cipher"]["nonce"])) == 12
    assert base64.b64decode(persisted["cipher"]["ciphertext"])
    assert len(base64.b64decode(persisted["cipher"]["tag"])) == 16
    assert persisted["provider"] == "openai"
    assert persisted["model"] == "gpt-test-model"
    assert FAKE_API_KEY not in serialized
    assert MASTER_PASSWORD not in serialized


def test_initialize_atomic_replacement_failure_leaves_no_partial_vault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed replacement must leave no partial Vault in place."""
    vault_path = tmp_path / "credentials" / "vault.json"
    service = VaultService(vault_path)

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("test replacement failure")

    monkeypatch.setattr("app.credentials.vault.os.replace", fail_replace)

    with pytest.raises(OSError, match="test replacement failure"):
        service.initialize(
            master_password=MASTER_PASSWORD,
            api_key=FAKE_API_KEY,
            model="gpt-test-model",
        )

    assert vault_path.exists() is False
    assert list(vault_path.parent.glob("*.tmp")) == []


def test_correct_password_unlocks_in_memory_only(tmp_path: Path) -> None:
    """Removing in-memory state must make a second unlock necessary after restart."""
    vault_path = tmp_path / "credentials" / "vault.json"
    initializer = VaultService(vault_path)
    initializer.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )

    restarted_service = VaultService(vault_path)

    assert restarted_service.is_unlocked is False
    assert restarted_service.unlocked_api_key is None

    restarted_service.unlock(master_password=MASTER_PASSWORD)

    assert restarted_service.is_unlocked is True
    assert restarted_service.unlocked_api_key == FAKE_API_KEY
    assert FAKE_API_KEY not in vault_path.read_text(encoding="utf-8")
