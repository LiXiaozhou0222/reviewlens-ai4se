import hashlib
from dataclasses import dataclass

from app.models.errors import PublicErrorCode


class DiffNormalizationError(ValueError):
    code: PublicErrorCode

    def __init__(self, code: PublicErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def decode_utf8_diff(raw: bytes) -> str:
    if not raw:
        raise DiffNormalizationError(PublicErrorCode.INPUT_EMPTY)

    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise DiffNormalizationError(PublicErrorCode.INVALID_UTF8) from None


@dataclass(frozen=True)
class NormalizedDiff:
    text: str
    sha256: str


def normalize_diff(raw: bytes) -> NormalizedDiff:
    text = decode_utf8_diff(raw)
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return NormalizedDiff(
        text=text,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
