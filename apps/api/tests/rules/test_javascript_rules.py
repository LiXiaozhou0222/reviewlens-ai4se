import pytest

from app.diff_parser.parser import AddedLine, ParsedDiff, ParsedFile, parse_unified_diff
from app.models.domain import FindingSource, Severity
from app.rules.javascript import scan_js_001


def test_js_001_finds_added_console_log() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/logger.ts b/src/logger.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/logger.ts",
                "+++ b/src/logger.ts",
                "@@ -7,2 +7,3 @@",
                " export const enabled = true;",
                '+console.log("diagnostic");',
                " export const level = 'info';",
            ]
        )
    )

    findings = scan_js_001(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-001"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.LOW
    assert finding.path == "src/logger.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == 'console.log("diagnostic");'
    assert finding.message
    assert finding.suggestion


def test_js_001_finds_added_console_debug() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/logger.jsx b/src/logger.jsx",
                "index 1234567..89abcde 100644",
                "--- a/src/logger.jsx",
                "+++ b/src/logger.jsx",
                "@@ -1 +1,2 @@",
                " export const logger = {};",
                '+console.debug("diagnostic");',
            ]
        )
    )

    findings = scan_js_001(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-001"
    assert findings[0].path == "src/logger.jsx"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == 'console.debug("diagnostic");'


def test_js_001_finds_direct_console_call_in_template_expression() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/logger.ts b/src/logger.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/logger.ts",
                "+++ b/src/logger.ts",
                "@@ -1 +1,2 @@",
                " export const logger = {};",
                '+const label = `value: ${console.debug("diagnostic")}`;',
            ]
        )
    )

    findings = scan_js_001(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-001"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == (
        'const label = `value: ${console.debug("diagnostic")}`;'
    )


@pytest.mark.parametrize(
    "opening_line",
    [
        "+/* console output is disabled",
        " /* console output is disabled",
    ],
)
def test_js_001_ignores_console_call_inside_multiline_block_comment(
    opening_line: str,
) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/logger.ts b/src/logger.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/logger.ts",
                "+++ b/src/logger.ts",
                "@@ -1,2 +1,3 @@",
                opening_line,
                '+console.log("diagnostic");',
                " */",
            ]
        )
    )

    assert scan_js_001(parsed_diff) == ()


def test_js_001_ignores_unsupported_and_binary_files() -> None:
    parsed_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/logger.py",
                added_lines=(AddedLine('console.log("diagnostic");', 2),),
            ),
            ParsedFile(
                new_path="src/logger.ts",
                added_lines=(AddedLine('console.debug("diagnostic");', 2),),
                is_binary=True,
            ),
        )
    )

    assert scan_js_001(parsed_diff) == ()


@pytest.mark.parametrize(
    "added_line",
    [
        "// console.log('diagnostic')",
        "const snippet = 'console.debug(\"diagnostic\")';",
        'const snippet = `console.log("diagnostic")`;',
        "console.error('diagnostic');",
        "logger.console.log('diagnostic');",
    ],
)
def test_js_001_ignores_comments_strings_errors_and_lookalikes(
    added_line: str,
) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/logger.tsx b/src/logger.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/logger.tsx",
                "+++ b/src/logger.tsx",
                "@@ -1 +1,2 @@",
                " export const logger = {};",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_001(parsed_diff) == ()
