from collections.abc import Callable

from app.diff_parser.parser import ParsedDiff, parse_unified_diff
from app.models.api import FindingDraft
from app.rules.general import scan_gen_001, scan_gen_002, scan_gen_003, scan_gen_004


SCANNERS: tuple[Callable[[ParsedDiff], tuple[FindingDraft, ...]], ...] = (
    scan_gen_001,
    scan_gen_002,
    scan_gen_003,
    scan_gen_004,
)


_MATCHING_LINES = (
    'API_KEY = "rl_fake_token_12345678"',
    "rm -rf /tmp/reviewlens-fixture",
    "# TODO: replace this fixture",
    'API_URL = "http://example.test/api"',
)


def _assert_no_general_rule_findings(diff_text: str) -> None:
    parsed_diff = parse_unified_diff(diff_text)

    for scanner in SCANNERS:
        assert scanner(parsed_diff) == ()


def test_deleted_secret_does_not_create_finding() -> None:
    _assert_no_general_rule_findings(
        "\n".join(
            [
                "diff --git a/src/fixture.py b/src/fixture.py",
                "index 1234567..89abcde 100644",
                "--- a/src/fixture.py",
                "+++ b/src/fixture.py",
                "@@ -1,5 +1 @@",
                *(f"-{line}" for line in _MATCHING_LINES),
                "+unchanged = True",
            ]
        )
    )


def test_hunk_context_rule_patterns_do_not_create_findings() -> None:
    _assert_no_general_rule_findings(
        "\n".join(
            [
                "diff --git a/src/fixture.py b/src/fixture.py",
                "index 1234567..89abcde 100644",
                "--- a/src/fixture.py",
                "+++ b/src/fixture.py",
                "@@ -1,5 +1,5 @@",
                *(f" {line}" for line in _MATCHING_LINES),
                "+unchanged = True",
            ]
        )
    )


def test_new_file_header_rule_patterns_do_not_create_findings() -> None:
    _assert_no_general_rule_findings(
        "\n".join(
            [
                "diff --git a/src/fixture.py b/src/fixture.py",
                "index 1234567..89abcde 100644",
                "--- a/src/fixture.py",
                f"+++ b/{' '.join(_MATCHING_LINES)}",
                "@@ -1 +1 @@",
                "+unchanged = True",
            ]
        )
    )
