import hashlib
from dataclasses import dataclass

from app.models.errors import PublicErrorCode

MAX_DIFF_BYTES = 512_000
MAX_DIFF_LINES = 5_000


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
    byte_count: int
    line_count: int


def normalize_diff(raw: bytes) -> NormalizedDiff:
    if len(raw) > MAX_DIFF_BYTES:
        raise DiffNormalizationError(PublicErrorCode.INPUT_TOO_LARGE)

    text = decode_utf8_diff(raw)
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    line_count = len(text.splitlines())
    if line_count > MAX_DIFF_LINES:
        raise DiffNormalizationError(PublicErrorCode.LINE_LIMIT_EXCEEDED)

    return NormalizedDiff(
        text=text,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        byte_count=len(raw),
        line_count=line_count,
    )
