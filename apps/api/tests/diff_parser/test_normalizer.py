import pytest

from app.diff_parser.normalizer import DiffNormalizationError, decode_utf8_diff
from app.models.errors import PublicErrorCode


def test_rejects_empty_input() -> None:
    with pytest.raises(DiffNormalizationError) as exc_info:
        decode_utf8_diff(b"")

    assert exc_info.value.code is PublicErrorCode.INPUT_EMPTY


def test_rejects_non_utf8_input() -> None:
    with pytest.raises(DiffNormalizationError) as exc_info:
        decode_utf8_diff(b"\xff")

    assert exc_info.value.code is PublicErrorCode.INVALID_UTF8
