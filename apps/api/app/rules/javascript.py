import re

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
_SUPPORTED_EXTENSIONS = frozenset({".ts", ".tsx", ".js", ".jsx"})
_CONSOLE_CALL = re.compile(r"(?<![A-Za-z0-9_$.])console\.(?:log|debug)\s*\(")
_DEBUGGER_STATEMENT = re.compile(
    r"(?<![A-Za-z0-9_$.])debugger(?![A-Za-z0-9_$])(?=\s*(?:;|}|//|/\*|$))"
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


class _JavaScriptLineScanner:
    def __init__(self) -> None:
        self._mode = "code"
        self._quote: str | None = None
        self._template_expression_depths: list[int] = []

    def scan(self, line: str, pattern: re.Pattern[str] = _CONSOLE_CALL) -> bool:
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

            if pattern.match(line, index) is not None:
                contains_console_call = True
            index += 1

        return contains_console_call
