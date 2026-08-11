"""Encrypted on-disk representation for the private credential Vault."""

import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


_KEY_LENGTH = 32
_SALT_LENGTH = 16
_NONCE_LENGTH = 12
_TAG_LENGTH = 16
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def create_vault_payload(
    *, master_password: str, api_key: str, model: str
) -> dict[str, Any]:
    """Encrypt one API key without retaining the derived key or plaintext."""
    salt = os.urandom(_SALT_LENGTH)
    nonce = os.urandom(_NONCE_LENGTH)
    encryption_key = _derive_key(master_password, salt)
    encrypted = AESGCM(encryption_key).encrypt(nonce, api_key.encode("utf-8"), None)

    return {
        "version": 1,
        "kdf": {
            "name": "scrypt",
            "salt": _encode(salt),
            "n": _SCRYPT_N,
            "r": _SCRYPT_R,
            "p": _SCRYPT_P,
            "length": _KEY_LENGTH,
        },
        "cipher": {
            "name": "AES-256-GCM",
            "nonce": _encode(nonce),
            "ciphertext": _encode(encrypted[:-_TAG_LENGTH]),
            "tag": _encode(encrypted[-_TAG_LENGTH:]),
        },
        "provider": "openai",
        "model": model,
        # A short input must never be echoed in full as a purported mask.
        "key_tail": api_key[-4:] if len(api_key) > 4 else None,
    }


def decrypt_api_key(*, master_password: str, payload: dict[str, Any]) -> str:
    """Decrypt a Vault payload with its stored scrypt parameters."""
    kdf = payload["kdf"]
    cipher = payload["cipher"]
    salt = _decode(kdf["salt"])
    nonce = _decode(cipher["nonce"])
    encrypted = _decode(cipher["ciphertext"]) + _decode(cipher["tag"])
    encryption_key = _derive_key(
        master_password,
        salt,
        n=kdf["n"],
        r=kdf["r"],
        p=kdf["p"],
        length=kdf["length"],
    )
    return AESGCM(encryption_key).decrypt(nonce, encrypted, None).decode("utf-8")


def load_vault(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as vault_file:
        return json.load(vault_file)


def write_vault_atomically(*, path: Path, payload: dict[str, Any]) -> None:
    """Replace a Vault only after its complete temporary file has been flushed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(payload, temporary_file, separators=(",", ":"), sort_keys=True)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _derive_key(
    master_password: str,
    salt: bytes,
    *,
    n: int = _SCRYPT_N,
    r: int = _SCRYPT_R,
    p: int = _SCRYPT_P,
    length: int = _KEY_LENGTH,
) -> bytes:
    return hashlib.scrypt(
        master_password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=length
    )


def _encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)
