from app.diff_parser.parser import ParsedDiff
from app.models.api import FindingDraft
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION


_GEN_005 = next(rule for rule in GENERAL_RULES if rule.rule_id == "GEN-005")


def scan_gen_005(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    findings: list[FindingDraft] = []

    for parsed_file in parsed_diff.files:
        if parsed_file.is_binary:
            continue

        if parsed_file.added_line_count + parsed_file.deleted_line_count < 500:
            continue

        findings.append(
            FindingDraft(
                rule_id=_GEN_005.rule_id,
                rule_version=RULESET_VERSION,
                source=_GEN_005.source,
                severity=_GEN_005.severity,
                path=parsed_file.new_path,
                new_line=None,
                raw_excerpt="",
                message=_GEN_005.message,
                suggestion=_GEN_005.suggestion,
            )
        )

    return tuple(findings)
