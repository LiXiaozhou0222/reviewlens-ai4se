from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity
from app.rules.dedupe import deduplicate_findings
from app.rules.risk import calculate_deterministic_risk, sort_findings


def _finding(
    severity: Severity,
    *,
    new_line: int | None,
    source: FindingSource = FindingSource.GENERAL_RULE,
    path: str = "src/example.ts",
    rule_id: str = "GEN-003",
) -> FindingDraft:
    return FindingDraft(
        rule_id=rule_id,
        rule_version="1.0.0",
        source=source,
        severity=severity,
        path=path,
        new_line=new_line,
        raw_excerpt=f"finding at line {new_line}",
        message="A deterministic test finding.",
        suggestion="Address the reported issue.",
    )


def test_no_deterministic_findings_has_none_risk() -> None:
    assert calculate_deterministic_risk(()) is Severity.NONE


def test_one_low_finding_has_low_risk() -> None:
    assert calculate_deterministic_risk((_finding(Severity.LOW, new_line=1),)) is Severity.LOW


def test_five_low_findings_escalate_to_medium() -> None:
    findings = tuple(_finding(Severity.LOW, new_line=line) for line in range(1, 6))

    assert calculate_deterministic_risk(findings) is Severity.MEDIUM


def test_one_medium_finding_has_medium_risk() -> None:
    assert (
        calculate_deterministic_risk((_finding(Severity.MEDIUM, new_line=1),))
        is Severity.MEDIUM
    )


def test_three_deduplicated_medium_findings_escalate_to_high() -> None:
    original = _finding(Severity.MEDIUM, new_line=1, rule_id="GEN-004")
    duplicate = original.model_copy(update={"raw_excerpt": "finding   at line 1"})
    findings = deduplicate_findings(
        (
            original,
            duplicate,
            _finding(Severity.MEDIUM, new_line=2, rule_id="GEN-004"),
            _finding(Severity.MEDIUM, new_line=3, rule_id="GEN-004"),
        )
    )

    assert len(findings) == 3
    assert calculate_deterministic_risk(findings) is Severity.HIGH


def test_one_high_finding_has_high_risk() -> None:
    assert calculate_deterministic_risk((_finding(Severity.HIGH, new_line=1),)) is Severity.HIGH


def test_multiple_high_findings_do_not_escalate_to_critical() -> None:
    findings = tuple(_finding(Severity.HIGH, new_line=line) for line in range(1, 4))

    assert calculate_deterministic_risk(findings) is Severity.HIGH


def test_one_critical_finding_has_critical_risk() -> None:
    assert (
        calculate_deterministic_risk((_finding(Severity.CRITICAL, new_line=1),))
        is Severity.CRITICAL
    )


def test_ai_findings_do_not_change_deterministic_risk() -> None:
    ai_findings = tuple(
        _finding(
            Severity.CRITICAL,
            new_line=line,
            source=FindingSource.AI,
            rule_id="AI-001",
        )
        for line in range(1, 4)
    )

    assert calculate_deterministic_risk(ai_findings) is Severity.NONE


def test_critical_ai_finding_does_not_change_deterministic_low_risk() -> None:
    findings = (
        _finding(Severity.LOW, new_line=1),
        _finding(
            Severity.CRITICAL,
            new_line=2,
            source=FindingSource.AI,
            rule_id="AI-001",
        ),
    )

    assert calculate_deterministic_risk(findings) is Severity.LOW


def test_findings_sort_by_source_partition_severity_path_line_and_rule() -> None:
    findings = (
        _finding(
            Severity.CRITICAL,
            new_line=1,
            source=FindingSource.AI,
            path="src/a.ts",
            rule_id="AI-001",
        ),
        _finding(Severity.LOW, new_line=8, path="src/z.ts", rule_id="GEN-003"),
        _finding(Severity.HIGH, new_line=9, path="src/b.ts", rule_id="JS-003"),
        _finding(Severity.HIGH, new_line=2, path="src/a.ts", rule_id="JS-004"),
        _finding(Severity.HIGH, new_line=2, path="src/a.ts", rule_id="JS-003"),
        _finding(
            Severity.LOW,
            new_line=1,
            source=FindingSource.AI,
            path="src/a.ts",
            rule_id="AI-002",
        ),
    )

    ordered = sort_findings(findings)

    assert [finding.rule_id for finding in ordered] == [
        "JS-003",
        "JS-004",
        "JS-003",
        "GEN-003",
        "AI-001",
        "AI-002",
    ]


def test_file_level_and_line_level_findings_have_stable_order() -> None:
    findings = (
        _finding(
            Severity.MEDIUM,
            new_line=9,
            path="src/example.ts",
            rule_id="JS-005",
        ),
        _finding(
            Severity.MEDIUM,
            new_line=None,
            path="src/example.ts",
            rule_id="GEN-005",
        ),
        _finding(
            Severity.MEDIUM,
            new_line=2,
            path="src/example.ts",
            rule_id="GEN-004",
        ),
    )

    ordered = sort_findings(findings)

    assert [(finding.rule_id, finding.new_line) for finding in ordered] == [
        ("GEN-005", None),
        ("GEN-004", 2),
        ("JS-005", 9),
    ]
