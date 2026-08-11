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
        payload = create_vault_payload(
            master_password=master_password,
            api_key=api_key,
            model=model,
        )
        write_vault_atomically(path=self._vault_path, payload=payload)
        self._unlocked_api_key = None

    def unlock(self, *, master_password: str) -> None:
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

        self._unlocked_api_key = api_key
        self._consecutive_unlock_failures = 0
