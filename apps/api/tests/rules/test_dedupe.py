from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity
from app.diff_parser.parser import parse_unified_diff
from app.rules.dedupe import deduplicate_findings
from app.rules.general import scan_gen_004


def test_same_added_statement_is_counted_once() -> None:
    original = FindingDraft(
        rule_id="GEN-003",
        rule_version="1.0.0",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.LOW,
        path="src/widget.ts",
        new_line=8,
        raw_excerpt="// TODO: replace this fixture",
        message="A TODO, FIXME, or HACK marker was added.",
        suggestion="Resolve the work item or track it outside the code change.",
    )
    duplicate_with_normalized_spacing = original.model_copy(
        update={"raw_excerpt": "// TODO:   replace this fixture"}
    )

    assert deduplicate_findings((original, duplicate_with_normalized_spacing)) == (
        original,
    )


def test_two_non_loopback_http_addresses_on_one_added_line_are_not_deduplicated() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.ts b/src/client.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/client.ts",
                "+++ b/src/client.ts",
                "@@ -1 +1,2 @@",
                " export const endpoints = [];",
                '+export const endpoints = ["http://one.example.test", "http://two.example.test"];',
            ]
        )
    )

    findings = scan_gen_004(parsed_diff)

    assert len(findings) == 2
    assert len(deduplicate_findings(findings)) == 2
