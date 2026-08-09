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
