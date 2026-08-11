"""Process-memory lifecycle for the private credential Vault."""

from pathlib import Path

from app.credentials.vault import (
    create_vault_payload,
    decrypt_api_key,
    load_vault,
    write_vault_atomically,
)


class VaultService:
    """Keeps an API key in memory only after an explicit unlock."""

    def __init__(self, vault_path: Path) -> None:
        self._vault_path = vault_path
        self._unlocked_api_key: str | None = None

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
        payload = load_vault(self._vault_path)
        self._unlocked_api_key = decrypt_api_key(
            master_password=master_password, payload=payload
        )
