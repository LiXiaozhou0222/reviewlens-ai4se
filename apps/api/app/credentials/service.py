"""Process-memory lifecycle for the private credential Vault."""

import time
from pathlib import Path

from app.credentials.vault import (
    create_vault_payload,
    decrypt_api_key,
    load_vault,
    write_vault_atomically,
)


_INITIAL_UNLOCK_FAILURE_DELAY_SECONDS = 0.05
_MAX_UNLOCK_FAILURE_DELAY_SECONDS = 0.25


class VaultUnlockError(RuntimeError):
    """The single public failure for an unavailable or unreadable Vault."""

    def __init__(self) -> None:
        super().__init__("Vault unlock failed")


class VaultService:
    """Keeps an API key in memory only after an explicit unlock."""

    def __init__(self, vault_path: Path) -> None:
        self._vault_path = vault_path
        self._unlocked_api_key: str | None = None
        self._consecutive_unlock_failures = 0

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked_api_key is not None

    @property
    def unlocked_api_key(self) -> str | None:
        return self._unlocked_api_key

    def initialize(self, *, master_password: str, api_key: str, model: str) -> None:
        if self._vault_path.exists():
            raise VaultUnlockError()

        payload = create_vault_payload(
            master_password=master_password,
            api_key=api_key,
            model=model,
        )
        write_vault_atomically(path=self._vault_path, payload=payload)
        self._unlocked_api_key = None

    def unlock(self, *, master_password: str) -> None:
        _, api_key = self._read_verified_vault(master_password=master_password)
        self._unlocked_api_key = api_key

    def lock(self) -> None:
        """Discard the process-memory credential without changing the Vault."""
        self._unlocked_api_key = None

    def update(self, *, master_password: str, api_key: str, model: str) -> None:
        """Reverify the operator and atomically replace the encrypted credential."""
        self._read_verified_vault(master_password=master_password)
        payload = create_vault_payload(
            master_password=master_password,
            api_key=api_key,
            model=model,
        )
        write_vault_atomically(path=self._vault_path, payload=payload)
        self.lock()

    def clear(self, *, master_password: str) -> None:
        """Reverify the operator before deleting disk and memory credentials."""
        self._read_verified_vault(master_password=master_password)
        self._vault_path.unlink()
        self.lock()

    def status(self) -> dict[str, str | bool | None]:
        """Return non-sensitive Vault state suitable for an admin response."""
        if not self._vault_path.exists():
            return {
                "exists": False,
                "unlocked": self.is_unlocked,
                "provider": None,
                "model": None,
                "masked_api_key": None,
            }

        try:
            payload = load_vault(self._vault_path)
        except Exception:
            return {
                "exists": True,
                "unlocked": self.is_unlocked,
                "provider": None,
                "model": None,
                "masked_api_key": None,
            }

        key_tail = payload.get("key_tail")
        masked_api_key = (
            f"••••{key_tail}"
            if isinstance(key_tail, str) and len(key_tail) == 4
            else None
        )
        provider = payload.get("provider")
        model = payload.get("model")
        return {
            "exists": True,
            "unlocked": self.is_unlocked,
            "provider": provider if isinstance(provider, str) else None,
            "model": model if isinstance(model, str) else None,
            "masked_api_key": masked_api_key,
        }

    def _read_verified_vault(
        self, *, master_password: str
    ) -> tuple[dict[str, object], str]:
        try:
            payload = load_vault(self._vault_path)
            api_key = decrypt_api_key(
                master_password=master_password, payload=payload
            )
        except Exception:
            # Password, ciphertext, and serialization failures must not form
            # distinguishable public error oracles.
            self._consecutive_unlock_failures += 1
            delay_seconds = min(
                _INITIAL_UNLOCK_FAILURE_DELAY_SECONDS * self._consecutive_unlock_failures,
                _MAX_UNLOCK_FAILURE_DELAY_SECONDS,
            )
            time.sleep(delay_seconds)
            raise VaultUnlockError() from None

        self._consecutive_unlock_failures = 0
        return payload, api_key
