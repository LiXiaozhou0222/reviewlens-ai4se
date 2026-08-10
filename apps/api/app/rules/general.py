import re

from app.diff_parser.parser import ParsedDiff
from app.models.api import FindingDraft
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION


_GEN_001 = next(rule for rule in GENERAL_RULES if rule.rule_id == "GEN-001")
_GEN_002 = next(rule for rule in GENERAL_RULES if rule.rule_id == "GEN-002")
_CREDENTIAL_LITERAL = re.compile(
    r"""(?i)(?<![A-Za-z0-9_])(?:["'])?(?:api_key|apikey|token|access_token|auth_token|password|passwd|secret)(?:["'])?(?![A-Za-z0-9_])\s*[:=]\s*(?P<quote>["'])(?P<value>(?![^"']*(?:\$\{|\{\{))[^"']+)(?P=quote)"""
)
_DESTRUCTIVE_OPERATION = re.compile(
    r"""(?ix)
    ^\s*(?:
        rm\s+-(?:rf|fr)\s+[^\s;#|&-]\S*
        |(?:drop|truncate)\s+(?:table|database)\b
        |mkfs(?:\.[a-z0-9_-]+)?\s+[^\s;#|&-]\S*
    )
    """
)


def scan_gen_001(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary:
            continue

        for added_line in parsed_file.added_lines:
            if _CREDENTIAL_LITERAL.search(added_line.content) is None:
                continue

            findings.append(
                FindingDraft(
                    rule_id=_GEN_001.rule_id,
                    rule_version=RULESET_VERSION,
                    source=_GEN_001.source,
                    severity=_GEN_001.severity,
                    path=parsed_file.new_path,
                    new_line=added_line.new_line,
                    raw_excerpt=added_line.content,
                    message=_GEN_001.message,
                    suggestion=_GEN_001.suggestion,
                )
            )

    return tuple(findings)


def scan_gen_002(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary:
            continue

        for added_line in parsed_file.added_lines:
            if _DESTRUCTIVE_OPERATION.search(added_line.content) is None:
                continue

            findings.append(
                FindingDraft(
                    rule_id=_GEN_002.rule_id,
                    rule_version=RULESET_VERSION,
                    source=_GEN_002.source,
                    severity=_GEN_002.severity,
                    path=parsed_file.new_path,
                    new_line=added_line.new_line,
                    raw_excerpt=added_line.content,
                    message=_GEN_002.message,
                    suggestion=_GEN_002.suggestion,
                )
            )

    return tuple(findings)
