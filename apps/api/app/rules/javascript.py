import re
from collections.abc import Callable

from app.diff_parser.parser import ParsedDiff
from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity
from app.rules.catalog import RULESET_VERSION, RuleMetadata


_JS_001 = RuleMetadata(
    rule_id="JS-001",
    name="Console output",
    source=FindingSource.LANGUAGE_RULE,
    severity=Severity.LOW,
    category="javascript",
    scope="added-line",
    message="A console.log or console.debug call was added.",
    suggestion="Remove the console output or replace it with approved logging.",
)
_JS_002 = RuleMetadata(
    rule_id="JS-002",
    name="Debugger statement",
    source=FindingSource.LANGUAGE_RULE,
    severity=Severity.LOW,
    category="javascript",
    scope="added-line",
    message="A debugger statement was added.",
    suggestion="Remove the debugger statement before merging.",
)
_JS_003 = RuleMetadata(
    rule_id="JS-003",
    name="Dynamic evaluation",
    source=FindingSource.LANGUAGE_RULE,
    severity=Severity.HIGH,
    category="javascript",
    scope="added-line",
    message="A direct eval() call was added.",
    suggestion="Avoid eval() and use a safe, explicit alternative.",
)
_JS_004 = RuleMetadata(
    rule_id="JS-004",
    name="Direct HTML injection",
    source=FindingSource.LANGUAGE_RULE,
    severity=Severity.HIGH,
    category="javascript",
    scope="added-line",
    message="A direct HTML injection sink was added.",
    suggestion="Avoid direct HTML injection or sanitize trusted content first.",
)
_SUPPORTED_EXTENSIONS = frozenset({".ts", ".tsx", ".js", ".jsx"})
_CONSOLE_CALL = re.compile(r"(?<![A-Za-z0-9_$.])console\.(?:log|debug)\s*\(")
_DEBUGGER_STATEMENT = re.compile(
    r"(?<![A-Za-z0-9_$.])debugger(?![A-Za-z0-9_$])(?=\s*(?:;|}|//|/\*|$))"
)
_EVAL_CALL = re.compile(r"(?<![A-Za-z0-9_$.])eval\s*\(")
_DIRECT_HTML_INJECTION = re.compile(
    r"(?:\.[ \t]*innerHTML|(?<![A-Za-z0-9_$])dangerouslySetInnerHTML)"
    r"(?![A-Za-z0-9_$])[ \t]*=(?!=)"
)


def scan_js_001(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary or not _is_supported_javascript_path(parsed_file.new_path):
            continue

        if parsed_file.hunks:
            for parsed_hunk in parsed_file.hunks:
                scanner = _JavaScriptLineScanner()
                for hunk_line in parsed_hunk.lines:
                    if hunk_line.kind == "deleted":
                        continue
                    contains_console_call = scanner.scan(hunk_line.content)
                    if hunk_line.kind != "added" or not contains_console_call:
                        continue
                    findings.append(_new_finding(parsed_file.new_path, hunk_line.new_line, hunk_line.content))
            continue

        for added_line in parsed_file.added_lines:
            if _JavaScriptLineScanner().scan(added_line.content):
                findings.append(
                    _new_finding(
                        parsed_file.new_path,
                        added_line.new_line,
                        added_line.content,
                    )
                )

    return tuple(findings)


def scan_js_002(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary or not _is_supported_javascript_path(parsed_file.new_path):
            continue

        if parsed_file.hunks:
            for parsed_hunk in parsed_file.hunks:
                scanner = _JavaScriptLineScanner()
                for hunk_line in parsed_hunk.lines:
                    if hunk_line.kind == "deleted":
                        continue
                    contains_debugger_statement = scanner.scan(
                        hunk_line.content,
                        _DEBUGGER_STATEMENT,
                    )
                    if hunk_line.kind != "added" or not contains_debugger_statement:
                        continue
                    findings.append(
                        _new_js_002_finding(
                            parsed_file.new_path,
                            hunk_line.new_line,
                            hunk_line.content,
                        )
                    )
            continue

        for added_line in parsed_file.added_lines:
            if _JavaScriptLineScanner().scan(added_line.content, _DEBUGGER_STATEMENT):
                findings.append(
                    _new_js_002_finding(
                        parsed_file.new_path,
                        added_line.new_line,
                        added_line.content,
                    )
                )

    return tuple(findings)


def scan_js_003(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary or not _is_supported_javascript_path(parsed_file.new_path):
            continue

        if parsed_file.hunks:
            for parsed_hunk in parsed_file.hunks:
                scanner = _JavaScriptLineScanner()
                for hunk_line in parsed_hunk.lines:
                    if hunk_line.kind == "deleted":
                        continue
                    contains_eval_call = scanner.scan(
                        hunk_line.content,
                        _EVAL_CALL,
                        _is_direct_eval_call,
                    )
                    if hunk_line.kind != "added" or not contains_eval_call:
                        continue
                    findings.append(
                        _new_js_003_finding(
                            parsed_file.new_path,
                            hunk_line.new_line,
                            hunk_line.content,
                        )
                    )
            continue

        for added_line in parsed_file.added_lines:
            if _JavaScriptLineScanner().scan(
                added_line.content,
                _EVAL_CALL,
                _is_direct_eval_call,
            ):
                findings.append(
                    _new_js_003_finding(
                        parsed_file.new_path,
                        added_line.new_line,
                        added_line.content,
                    )
                )

    return tuple(findings)


def scan_js_004(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary or not _is_supported_javascript_path(parsed_file.new_path):
            continue

        if parsed_file.hunks:
            for parsed_hunk in parsed_file.hunks:
                scanner = _JavaScriptLineScanner()
                for hunk_line in parsed_hunk.lines:
                    if hunk_line.kind == "deleted":
                        continue
                    contains_direct_html_injection = scanner.scan(
                        hunk_line.content,
                        _DIRECT_HTML_INJECTION,
                        scanner.is_direct_html_injection,
                    )
                    if hunk_line.kind != "added" or not contains_direct_html_injection:
                        continue
                    findings.append(
                        _new_js_004_finding(
                            parsed_file.new_path,
                            hunk_line.new_line,
                            hunk_line.content,
                        )
                    )
            continue

        for added_line in parsed_file.added_lines:
            scanner = _JavaScriptLineScanner()
            if scanner.scan(
                added_line.content,
                _DIRECT_HTML_INJECTION,
                scanner.is_direct_html_injection,
            ):
                findings.append(
                    _new_js_004_finding(
                        parsed_file.new_path,
                        added_line.new_line,
                        added_line.content,
                    )
                )

    return tuple(findings)


def _is_supported_javascript_path(path: str) -> bool:
    return path.casefold().endswith(tuple(_SUPPORTED_EXTENSIONS))


def _new_finding(path: str, new_line: int | None, raw_excerpt: str) -> FindingDraft:
    return FindingDraft(
        rule_id=_JS_001.rule_id,
        rule_version=RULESET_VERSION,
        source=_JS_001.source,
        severity=_JS_001.severity,
        path=path,
        new_line=new_line,
        raw_excerpt=raw_excerpt,
        message=_JS_001.message,
        suggestion=_JS_001.suggestion,
    )


def _new_js_002_finding(
    path: str,
    new_line: int | None,
    raw_excerpt: str,
) -> FindingDraft:
    return FindingDraft(
        rule_id=_JS_002.rule_id,
        rule_version=RULESET_VERSION,
        source=_JS_002.source,
        severity=_JS_002.severity,
        path=path,
        new_line=new_line,
        raw_excerpt=raw_excerpt,
        message=_JS_002.message,
        suggestion=_JS_002.suggestion,
    )


def _new_js_003_finding(
    path: str,
    new_line: int | None,
    raw_excerpt: str,
) -> FindingDraft:
    return FindingDraft(
        rule_id=_JS_003.rule_id,
        rule_version=RULESET_VERSION,
        source=_JS_003.source,
        severity=_JS_003.severity,
        path=path,
        new_line=new_line,
        raw_excerpt=raw_excerpt,
        message=_JS_003.message,
        suggestion=_JS_003.suggestion,
    )


def _new_js_004_finding(
    path: str,
    new_line: int | None,
    raw_excerpt: str,
) -> FindingDraft:
    return FindingDraft(
        rule_id=_JS_004.rule_id,
        rule_version=RULESET_VERSION,
        source=_JS_004.source,
        severity=_JS_004.severity,
        path=path,
        new_line=new_line,
        raw_excerpt=raw_excerpt,
        message=_JS_004.message,
        suggestion=_JS_004.suggestion,
    )


def _is_direct_eval_call(line: str, match: re.Match[str]) -> bool:
    closing_parenthesis = line.find(")", match.end())
    if (
        closing_parenthesis != -1
        and line[closing_parenthesis + 1 :].lstrip().startswith("{")
    ):
        return False

    opening_tag_end = line.rfind(">", 0, match.start())
    opening_tag_start = line.rfind("<", 0, match.start())
    closing_tag_start = line.find("</", match.start())
    if opening_tag_end > opening_tag_start and closing_tag_start != -1:
        text_node = line[opening_tag_end + 1 : closing_tag_start]
        if "{" not in text_node and "}" not in text_node:
            return False

    return True


class _JavaScriptLineScanner:
    def __init__(self) -> None:
        self._mode = "code"
        self._quote: str | None = None
        self._template_expression_depths: list[int] = []
        self._jsx_open_tag = False
        self._jsx_attribute_expression_depth = 0

    def is_direct_html_injection(self, _line: str, match: re.Match[str]) -> bool:
        return match.group().startswith(".") or (
            self._jsx_open_tag and self._jsx_attribute_expression_depth == 0
        )

    def scan(
        self,
        line: str,
        pattern: re.Pattern[str] = _CONSOLE_CALL,
        match_filter: Callable[[str, re.Match[str]], bool] | None = None,
    ) -> bool:
        index = 0
        contains_console_call = False

        while index < len(line):
            if self._mode == "block-comment":
                if line.startswith("*/", index):
                    self._mode = "code"
                    index += 2
                else:
                    index += 1
                continue

            if self._mode == "string":
                if line[index] == "\\":
                    index += 2
                elif line[index] == self._quote:
                    self._mode = "code"
                    self._quote = None
                    index += 1
                else:
                    index += 1
                continue

            if self._mode == "template":
                if line[index] == "\\":
                    index += 2
                elif line.startswith("${", index):
                    self._template_expression_depths.append(1)
                    self._mode = "code"
                    index += 2
                elif line[index] == "`":
                    self._mode = "code"
                    index += 1
                else:
                    index += 1
                continue

            if line.startswith("//", index):
                break
            if line.startswith("/*", index):
                self._mode = "block-comment"
                index += 2
                continue
            if line[index] in {"'", '"'}:
                self._mode = "string"
                self._quote = line[index]
                index += 1
                continue
            if line[index] == "`":
                self._mode = "template"
                index += 1
                continue
            if (
                line[index] == "<"
                and index + 1 < len(line)
                and line[index + 1].isalpha()
                and _starts_jsx_opening_tag(line, index)
            ):
                self._jsx_open_tag = True
                self._jsx_attribute_expression_depth = 0
            elif line[index] == "{" and self._jsx_open_tag:
                self._jsx_attribute_expression_depth += 1
            elif (
                line[index] == "}"
                and self._jsx_open_tag
                and self._jsx_attribute_expression_depth > 0
            ):
                self._jsx_attribute_expression_depth -= 1
            elif (
                line[index] == ">"
                and self._jsx_open_tag
                and self._jsx_attribute_expression_depth == 0
            ):
                self._jsx_open_tag = False
            if self._template_expression_depths:
                if line[index] == "{":
                    self._template_expression_depths[-1] += 1
                elif line[index] == "}":
                    self._template_expression_depths[-1] -= 1
                    if self._template_expression_depths[-1] == 0:
                        self._template_expression_depths.pop()
                        self._mode = "template"
                    index += 1
                    continue

            match = pattern.match(line, index)
            if match is not None and (match_filter is None or match_filter(line, match)):
                contains_console_call = True
            index += 1

        return contains_console_call


def _starts_jsx_opening_tag(line: str, index: int) -> bool:
    prefix = line[:index].rstrip()
    return (
        not prefix
        or prefix.endswith(("=", "(", "[", "{", ",", ":", "?", ">"))
        or bool(re.search(r"\breturn$", prefix))
    )
