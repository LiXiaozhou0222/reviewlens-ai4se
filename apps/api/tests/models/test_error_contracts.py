from app.config.mode_policy import ModeCapabilities, mode_capabilities
from app.models.domain import ReviewMode
from app.models.errors import PublicErrorCode


def test_input_error_codes_are_stable() -> None:
    input_error_codes = [
        PublicErrorCode.INPUT_EMPTY,
        PublicErrorCode.INPUT_TOO_LARGE,
        PublicErrorCode.LINE_LIMIT_EXCEEDED,
        PublicErrorCode.INVALID_UTF8,
        PublicErrorCode.INVALID_DIFF_FORMAT,
    ]

    assert [(member.name, member.value) for member in input_error_codes] == [
        ("INPUT_EMPTY", "INPUT_EMPTY"),
        ("INPUT_TOO_LARGE", "INPUT_TOO_LARGE"),
        ("LINE_LIMIT_EXCEEDED", "LINE_LIMIT_EXCEEDED"),
        ("INVALID_UTF8", "INVALID_UTF8"),
        ("INVALID_DIFF_FORMAT", "INVALID_DIFF_FORMAT"),
    ]


def test_complete_public_error_code_vocabulary_is_stable() -> None:
    assert [(member.name, member.value) for member in PublicErrorCode] == [
        ("INPUT_EMPTY", "INPUT_EMPTY"),
        ("INPUT_TOO_LARGE", "INPUT_TOO_LARGE"),
        ("LINE_LIMIT_EXCEEDED", "LINE_LIMIT_EXCEEDED"),
        ("INVALID_UTF8", "INVALID_UTF8"),
        ("INVALID_DIFF_FORMAT", "INVALID_DIFF_FORMAT"),
        ("RATE_LIMITED", "RATE_LIMITED"),
        ("AI_NOT_CONFIGURED", "AI_NOT_CONFIGURED"),
        ("AI_TIMEOUT", "AI_TIMEOUT"),
        ("AI_AUTH_FAILED", "AI_AUTH_FAILED"),
        ("AI_INVALID_RESPONSE", "AI_INVALID_RESPONSE"),
        ("INTERNAL_ERROR", "INTERNAL_ERROR"),
    ]


def test_demo_disables_private_features() -> None:
    capabilities = mode_capabilities(ReviewMode.DEMO)

    assert capabilities == ModeCapabilities(False, False, False, False, False)
    assert capabilities.report_persistence is False
    assert capabilities.report_history is False
    assert capabilities.ai_retry is False
    assert capabilities.persistent_export is False
    assert capabilities.credential_management is False
