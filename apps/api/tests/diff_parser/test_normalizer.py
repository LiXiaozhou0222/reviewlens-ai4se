import pytest

from app.diff_parser import normalizer
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


def test_crlf_and_lf_have_the_same_digest() -> None:
    crlf = normalizer.normalize_diff(b"+a\r\n+b\r\n")
    lf = normalizer.normalize_diff(b"+a\n+b\n")

    assert crlf.text == lf.text == "+a\n+b\n"
    assert crlf.sha256 == lf.sha256


def test_leading_bom_has_the_same_canonical_text_and_digest() -> None:
    with_bom = normalizer.normalize_diff(b"\xef\xbb\xbf+a\n")
    without_bom = normalizer.normalize_diff(b"+a\n")

    assert with_bom.text == without_bom.text == "+a\n"
    assert with_bom.sha256 == without_bom.sha256


def test_digest_is_a_64_character_lowercase_sha256_hex_string() -> None:
    result = normalizer.normalize_diff(b"+synthetic\n")

    assert result.sha256 == "bc953cb91a1b2e423b008cda1d44de01df14a97eb4cee10df258a93dcdebf536"


def test_rejects_over_line_limit() -> None:
    raw = (b"+synthetic\n" * normalizer.MAX_DIFF_LINES) + b"+synthetic"

    with pytest.raises(DiffNormalizationError) as exc_info:
        normalizer.normalize_diff(raw)

    assert exc_info.value.code is PublicErrorCode.LINE_LIMIT_EXCEEDED


def test_rejects_over_byte_limit_before_decoding() -> None:
    raw = b"a" * (normalizer.MAX_DIFF_BYTES + 1)

    with pytest.raises(DiffNormalizationError) as exc_info:
        normalizer.normalize_diff(raw)

    assert exc_info.value.code is PublicErrorCode.INPUT_TOO_LARGE


def test_accepts_exact_byte_limit_and_reports_counts() -> None:
    raw = b"a" * normalizer.MAX_DIFF_BYTES

    result = normalizer.normalize_diff(raw)

    assert result.byte_count == normalizer.MAX_DIFF_BYTES
    assert result.line_count == 1


def test_accepts_exact_line_limit_and_reports_counts() -> None:
    raw = (b"+synthetic\n" * (normalizer.MAX_DIFF_LINES - 1)) + b"+synthetic"

    result = normalizer.normalize_diff(raw)

    assert result.byte_count == len(raw)
    assert result.line_count == normalizer.MAX_DIFF_LINES
