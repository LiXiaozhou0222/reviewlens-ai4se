import pytest

from app.diff_parser.parser import AddedLine, ParsedDiff, ParsedFile, parse_unified_diff
from app.models.domain import FindingSource, Severity
from app.rules.javascript import (
    scan_js_001,
    scan_js_002,
    scan_js_003,
    scan_js_004,
    scan_js_005,
    scan_js_006,
    scan_js_007,
)


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


def test_js_002_finds_added_debugger() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/debug.ts b/src/debug.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/debug.ts",
                "+++ b/src/debug.ts",
                "@@ -7,2 +7,3 @@",
                " export const enabled = true;",
                "+debugger;",
                " export const level = 'info';",
            ]
        )
    )

    findings = scan_js_002(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-002"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.LOW
    assert finding.path == "src/debug.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == "debugger;"
    assert finding.message
    assert finding.suggestion


def test_js_002_finds_debugger_before_closing_brace_via_asi() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/debug.ts b/src/debug.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/debug.ts",
                "+++ b/src/debug.ts",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                "+if (enabled) { debugger }",
            ]
        )
    )

    findings = scan_js_002(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-002"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == "if (enabled) { debugger }"


def test_js_002_finds_debugger_inside_template_interpolation() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/debug.js b/src/debug.js",
                "index 1234567..89abcde 100644",
                "--- a/src/debug.js",
                "+++ b/src/debug.js",
                "@@ -1 +1,2 @@",
                " export const label = 'ready';",
                '+const label = `${(() => { debugger; return "ready"; })()}`;',
            ]
        )
    )

    findings = scan_js_002(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-002"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == (
        'const label = `${(() => { debugger; return "ready"; })()}`;'
    )


def test_js_002_ignores_debugger_inside_block_comment_started_by_hunk_context() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/debug.tsx b/src/debug.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/debug.tsx",
                "+++ b/src/debug.tsx",
                "@@ -1,2 +1,3 @@",
                " /* debugging is disabled",
                "+debugger;",
                " */",
            ]
        )
    )

    assert scan_js_002(parsed_diff) == ()


@pytest.mark.parametrize(
    "added_line",
    [
        "// debugger;",
        "const snippet = 'debugger;';",
        "const snippet = `debugger;`;",
        "const debuggerEnabled = true;",
        "settings.debugger = true;",
    ],
)
def test_js_002_ignores_comments_strings_and_lookalikes(added_line: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/debug.jsx b/src/debug.jsx",
                "index 1234567..89abcde 100644",
                "--- a/src/debug.jsx",
                "+++ b/src/debug.jsx",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_002(parsed_diff) == ()


def test_js_003_finds_added_eval() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.ts b/src/legacy.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.ts",
                "+++ b/src/legacy.ts",
                "@@ -7,2 +7,3 @@",
                " export const enabled = true;",
                '+const result = eval("legacyExpression");',
                " export const level = 'info';",
            ]
        )
    )

    findings = scan_js_003(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-003"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.HIGH
    assert finding.path == "src/legacy.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == 'const result = eval("legacyExpression");'
    assert finding.message
    assert finding.suggestion


def test_js_003_finds_eval_inside_template_interpolation() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.jsx b/src/legacy.jsx",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.jsx",
                "+++ b/src/legacy.jsx",
                "@@ -1 +1,2 @@",
                " export const title = 'ready';",
                '+const title = `${eval("legacyExpression")}`;',
            ]
        )
    )

    findings = scan_js_003(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-003"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == 'const title = `${eval("legacyExpression")}`;'


def test_js_003_finds_eval_used_as_a_control_flow_condition() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.ts b/src/legacy.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.ts",
                "+++ b/src/legacy.ts",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                "+if (eval(input)) { runLegacyPath(); }",
            ]
        )
    )

    findings = scan_js_003(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-003"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == "if (eval(input)) { runLegacyPath(); }"


def test_js_003_ignores_eval_inside_block_comment_started_by_hunk_context() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.tsx b/src/legacy.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.tsx",
                "+++ b/src/legacy.tsx",
                "@@ -1,2 +1,3 @@",
                " /* dynamic evaluation is prohibited",
                '+const result = eval("legacyExpression");',
                " */",
            ]
        )
    )

    assert scan_js_003(parsed_diff) == ()


@pytest.mark.parametrize(
    "added_line",
    [
        "// eval('legacyExpression')",
        "const snippet = 'eval(\"legacyExpression\")';",
        'const snippet = `eval("legacyExpression")`;',
        "const evaluate = (value: string) => value;",
        "legacy.eval('legacyExpression');",
        "window.eval('legacyExpression');",
    ],
)
def test_js_003_ignores_comments_strings_and_lookalikes(added_line: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.js b/src/legacy.js",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.js",
                "+++ b/src/legacy.js",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_003(parsed_diff) == ()


@pytest.mark.parametrize(
    ("path", "added_line"),
    [
        ("src/parser.ts", "class Parser { eval() {} }"),
        ("src/parser.js", "const parser = { eval() {} };"),
        ("src/preview.tsx", "export const Preview = () => <div>eval()</div>;"),
    ],
)
def test_js_003_ignores_method_declarations_and_jsx_text(
    path: str,
    added_line: str,
) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                f"diff --git a/{path} b/{path}",
                "index 1234567..89abcde 100644",
                f"--- a/{path}",
                f"+++ b/{path}",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_003(parsed_diff) == ()


def test_js_003_ignores_unsupported_binary_and_deleted_eval_calls() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/legacy.py b/src/legacy.py",
                "index 1234567..89abcde 100644",
                "--- a/src/legacy.py",
                "+++ b/src/legacy.py",
                "@@ -1 +1,2 @@",
                " enabled = True",
                '+result = eval("legacy_expression")',
                "diff --git a/src/removed.ts b/src/removed.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/removed.ts",
                "+++ b/src/removed.ts",
                "@@ -1,2 +1 @@",
                '-const result = eval("legacyExpression");',
                " export const enabled = true;",
            ]
        )
    )
    binary_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/legacy.ts",
                added_lines=(
                    AddedLine('const result = eval("legacyExpression");', 2),
                ),
                is_binary=True,
            ),
        )
    )

    assert scan_js_003(parsed_diff) == ()
    assert scan_js_003(binary_diff) == ()


def test_js_004_finds_added_inner_html() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.ts b/src/preview.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.ts",
                "+++ b/src/preview.ts",
                "@@ -7,2 +7,3 @@",
                " export const enabled = true;",
                "+preview.innerHTML = renderedMarkup;",
                " export const mode = 'safe';",
            ]
        )
    )

    findings = scan_js_004(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-004"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.HIGH
    assert finding.path == "src/preview.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == "preview.innerHTML = renderedMarkup;"
    assert finding.message
    assert finding.suggestion


def test_js_004_finds_added_dangerously_set_inner_html() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.tsx b/src/preview.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.tsx",
                "+++ b/src/preview.tsx",
                "@@ -1 +1,2 @@",
                " export const Preview = () => null;",
                "+export const HtmlPreview = () => <div "
                "dangerouslySetInnerHTML={{ __html: markup }} />;",
            ]
        )
    )

    findings = scan_js_004(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-004"
    assert findings[0].path == "src/preview.tsx"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == (
        "export const HtmlPreview = () => <div "
        "dangerouslySetInnerHTML={{ __html: markup }} />;"
    )


def test_js_004_finds_dangerously_set_inner_html_in_multiline_jsx_tag() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.tsx b/src/preview.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.tsx",
                "+++ b/src/preview.tsx",
                "@@ -1 +1,6 @@",
                " export const Preview = () => null;",
                "+export const HtmlPreview = () => (",
                "+  <div",
                "+    dangerouslySetInnerHTML={{ __html: markup }}",
                "+  />",
                "+);",
            ]
        )
    )

    findings = scan_js_004(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "JS-004"
    assert findings[0].path == "src/preview.tsx"
    assert findings[0].new_line == 4
    assert findings[0].raw_excerpt == "    dangerouslySetInnerHTML={{ __html: markup }}"


def test_js_004_keeps_multiline_jsx_tag_open_through_attribute_expression() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.tsx b/src/preview.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.tsx",
                "+++ b/src/preview.tsx",
                "@@ -1 +1,7 @@",
                " export const Preview = () => null;",
                "+export const HtmlPreview = () => (",
                "+  <div",
                "+    data-ready={count > 0}",
                "+    dangerouslySetInnerHTML={{ __html: markup }}",
                "+  />",
                "+);",
            ]
        )
    )

    findings = scan_js_004(parsed_diff)

    assert len(findings) == 1
    assert findings[0].new_line == 5
    assert findings[0].raw_excerpt == "    dangerouslySetInnerHTML={{ __html: markup }}"


def test_js_004_ignores_bare_binding_inside_jsx_attribute_expression() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.tsx b/src/preview.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.tsx",
                "+++ b/src/preview.tsx",
                "@@ -1 +1,4 @@",
                " export const Preview = () => null;",
                "+<div",
                "+ onClick={() => { dangerouslySetInnerHTML = false; }}",
                "+/>",
            ]
        )
    )

    assert scan_js_004(parsed_diff) == ()


def test_js_004_ignores_bare_binding_after_comparison() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.tsx b/src/preview.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.tsx",
                "+++ b/src/preview.tsx",
                "@@ -1 +1,3 @@",
                " export const Preview = () => null;",
                "+const ready = count < limit;",
                "+let dangerouslySetInnerHTML = false;",
            ]
        )
    )

    assert scan_js_004(parsed_diff) == ()


def test_js_004_ignores_inner_html_inside_block_comment_started_by_hunk_context() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.ts b/src/preview.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.ts",
                "+++ b/src/preview.ts",
                "@@ -1,2 +1,3 @@",
                " /* legacy unsafe rendering",
                "+preview.innerHTML = renderedMarkup;",
                " */",
            ]
        )
    )

    assert scan_js_004(parsed_diff) == ()


@pytest.mark.parametrize(
    "added_line",
    [
        "// preview.innerHTML = renderedMarkup;",
        "const snippet = 'preview.innerHTML = renderedMarkup;';",
        "const snippet = `dangerouslySetInnerHTML={{ __html: markup }}`;",
        "preview.innerHTML;",
        "preview.notInnerHTML = renderedMarkup;",
        "const dangerouslySetInnerHTMLEnabled = true;",
        "let dangerouslySetInnerHTML = false;",
    ],
)
def test_js_004_ignores_comments_strings_and_lookalikes(added_line: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.jsx b/src/preview.jsx",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.jsx",
                "+++ b/src/preview.jsx",
                "@@ -1 +1,2 @@",
                " export const Preview = () => null;",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_004(parsed_diff) == ()


def test_js_004_ignores_unsupported_binary_and_deleted_uses() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/preview.py b/src/preview.py",
                "index 1234567..89abcde 100644",
                "--- a/src/preview.py",
                "+++ b/src/preview.py",
                "@@ -1 +1,2 @@",
                " preview = object()",
                "+preview.innerHTML = rendered_markup",
                "diff --git a/src/removed.tsx b/src/removed.tsx",
                "index 1234567..89abcde 100644",
                "--- a/src/removed.tsx",
                "+++ b/src/removed.tsx",
                "@@ -1,2 +1 @@",
                "-export const HtmlPreview = () => <div "
                "dangerouslySetInnerHTML={{ __html: markup }} />;",
                " export const Preview = () => null;",
            ]
        )
    )
    binary_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/preview.ts",
                added_lines=(AddedLine("preview.innerHTML = renderedMarkup;", 2),),
                is_binary=True,
            ),
        )
    )

    assert scan_js_004(parsed_diff) == ()
    assert scan_js_004(binary_diff) == ()


def test_js_005_anchors_empty_catch_to_added_line() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.ts b/src/loader.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.ts",
                "+++ b/src/loader.ts",
                "@@ -1 +1,7 @@",
                " export const enabled = true;",
                "+export async function load() {",
                "+  try {",
                "+    await fetch('/api/items');",
                "+  } catch (error) {",
                "+  }",
                "+}",
            ]
        )
    )

    findings = scan_js_005(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-005"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.MEDIUM
    assert finding.path == "src/loader.ts"
    assert finding.new_line == 5
    assert finding.raw_excerpt == "  } catch (error) {"
    assert finding.message
    assert finding.suggestion


def test_js_005_finds_fully_added_explicitly_swallowed_exception() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/cache.js b/src/cache.js",
                "index 1234567..89abcde 100644",
                "--- a/src/cache.js",
                "+++ b/src/cache.js",
                "@@ -1 +1,7 @@",
                " export const enabled = true;",
                "+function loadFromCache() {",
                "+  try {",
                "+    return readCache();",
                "+  } catch (error) {",
                "+    return undefined;",
                "+  }",
                "+}",
            ]
        )
    )

    findings = scan_js_005(parsed_diff)

    assert len(findings) == 1
    assert findings[0].new_line == 5
    assert findings[0].raw_excerpt == "  } catch (error) {"


def test_js_005_finds_fully_added_one_line_empty_catch() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.js b/src/loader.js",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.js",
                "+++ b/src/loader.js",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                "+try { work(); } catch (error) {}",
            ]
        )
    )

    findings = scan_js_005(parsed_diff)

    assert len(findings) == 1
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == "try { work(); } catch (error) {}"


def test_js_005_ignores_catches_without_a_wholly_added_structure() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.ts b/src/loader.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.ts",
                "+++ b/src/loader.ts",
                "@@ -1,5 +1,6 @@",
                " export async function load() {",
                "   try {",
                "     await fetch('/api/items');",
                "   } catch (error) {",
                "+    return undefined;",
                "   }",
                " }",
            ]
        )
    )

    assert scan_js_005(parsed_diff) == ()


@pytest.mark.parametrize(
    ("path", "added_line"),
    [
        ("src/loader.ts", "// catch (error) { return undefined; }"),
        ("src/loader.ts", 'const snippet = "catch (error) { }";'),
        ("src/loader.py", "except Exception: pass"),
    ],
)
def test_js_005_ignores_comments_strings_and_unsupported_files(
    path: str,
    added_line: str,
) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                f"diff --git a/{path} b/{path}",
                "index 1234567..89abcde 100644",
                f"--- a/{path}",
                f"+++ b/{path}",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                f"+{added_line}",
            ]
        )
    )
    binary_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/loader.ts",
                added_lines=(AddedLine("catch (error) { }", 2),),
                is_binary=True,
            ),
        )
    )

    assert scan_js_005(parsed_diff) == ()
    assert scan_js_005(binary_diff) == ()


def test_js_006_finds_unhandled_added_fetch() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.ts b/src/loader.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.ts",
                "+++ b/src/loader.ts",
                "@@ -7,2 +7,3 @@",
                " export const enabled = true;",
                "+fetch('/api/items');",
                " export const retryLimit = 3;",
            ]
        )
    )

    findings = scan_js_006(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "JS-006"
    assert finding.rule_version == "1.0.0"
    assert finding.source is FindingSource.LANGUAGE_RULE
    assert finding.severity is Severity.MEDIUM
    assert finding.path == "src/loader.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == "fetch('/api/items');"
    assert finding.message
    assert finding.suggestion


@pytest.mark.parametrize(
    "added_line",
    [
        "await fetch('/api/items');",
        "return fetch('/api/items');",
        "fetch('/api/items').then(handleResponse);",
        "const request = fetch('/api/items');",
        "// fetch('/api/items');",
        'const example = "fetch(\\\'/api/items\\\')";',
    ],
)
def test_js_006_ignores_handled_or_uncertain_added_fetches(added_line: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.js b/src/loader.js",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.js",
                "+++ b/src/loader.js",
                "@@ -1 +1,2 @@",
                " export const enabled = true;",
                f"+{added_line}",
            ]
        )
    )

    assert scan_js_006(parsed_diff) == ()


def test_js_006_ignores_unsupported_and_binary_added_fetches() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/loader.py b/src/loader.py",
                "index 1234567..89abcde 100644",
                "--- a/src/loader.py",
                "+++ b/src/loader.py",
                "@@ -1 +1,2 @@",
                " enabled = True",
                "+fetch('/api/items');",
            ]
        )
    )
    binary_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/loader.ts",
                added_lines=(AddedLine("fetch('/api/items');", 2),),
                is_binary=True,
            ),
        )
    )

    assert scan_js_006(parsed_diff) == ()
    assert scan_js_006(binary_diff) == ()


def test_js_007_finds_narrowed_explicit_any() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/types.ts b/src/types.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/types.ts",
                "+++ b/src/types.ts",
                "@@ -7,2 +7,9 @@",
                " export const enabled = true;",
                "+const payload: any = readPayload();",
                "+let retry: any;",
                "+var legacy: any = null;",
                "+function normalize(input: any): any { return input; }",
                "+const select = (item: any): any => item;",
                "+const result = execute(job) as any;",
                "+const first = values[0] as any;",
                " export const retryLimit = 3;",
            ]
        )
    )

    findings = scan_js_007(parsed_diff)

    assert [finding.rule_id for finding in findings] == ["JS-007"] * 7
    assert [finding.rule_version for finding in findings] == ["1.0.0"] * 7
    assert [finding.source for finding in findings] == [FindingSource.LANGUAGE_RULE] * 7
    assert [finding.severity for finding in findings] == [Severity.LOW] * 7
    assert [finding.path for finding in findings] == ["src/types.ts"] * 7
    assert [finding.new_line for finding in findings] == list(range(8, 15))
    assert [finding.raw_excerpt for finding in findings] == [
        "const payload: any = readPayload();",
        "let retry: any;",
        "var legacy: any = null;",
        "function normalize(input: any): any { return input; }",
        "const select = (item: any): any => item;",
        "const result = execute(job) as any;",
        "const first = values[0] as any;",
    ]


@pytest.mark.parametrize(
    ("path", "added_line"),
    [
        ("src/types.js", "const payload: any = readPayload();"),
        ("src/component.jsx", "const view = render() as any;"),
        ("src/types.ts", "// const payload: any = readPayload();"),
        ("src/types.ts", 'const label = "const payload: any = readPayload();";'),
        ("src/types.ts", "const label = `result as any`;"),
        ("src/types.ts", "const matcher = /result as any/;"),
        ("src/component.tsx", "const view = <div>result as any</div>;"),
        ("src/types.ts", "import { value as any } from './value';"),
        ("src/types.ts", "export { value as any };"),
        ("src/types.ts", "label: any;"),
        ("src/types.ts", "const options = { mode: any } ;"),
        ("src/types.ts", "interface Payload { value: any }"),
        ("src/types.ts", "type Payload = { value: any };"),
        ("src/types.ts", "const result = value as any;"),
        ("src/types.ts", "const result = execute(\n"),
        ("src/types.ts", ") as any;"),
    ],
)
def test_js_007_ignores_unsupported_or_uncertain_explicit_any(
    path: str, added_line: str
) -> None:
    parsed_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path=path,
                added_lines=(AddedLine(added_line, 2),),
            ),
        )
    )

    assert scan_js_007(parsed_diff) == ()


def test_js_007_ignores_deleted_context_and_binary_explicit_any() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/types.ts b/src/types.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/types.ts",
                "+++ b/src/types.ts",
                "@@ -7,3 +7,2 @@",
                " const retained: any = existingValue;",
                "-const removed: any = removedValue;",
                "+const replacement = readValue();",
                " const result = execute(job) as any;",
            ]
        )
    )
    binary_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/types.ts",
                added_lines=(AddedLine("const payload: any = readPayload();", 2),),
                is_binary=True,
            ),
        )
    )

    assert scan_js_007(parsed_diff) == ()
    assert scan_js_007(binary_diff) == ()
