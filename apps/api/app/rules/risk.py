from collections.abc import Iterable

from app.models.api import FindingDraft
from app.models.domain import FindingSource, Severity


_SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.NONE: 4,
}


def calculate_deterministic_risk(findings: Iterable[FindingDraft]) -> Severity:
    """Aggregate already-deduplicated deterministic findings into a risk level."""
    severities = [
        finding.severity
        for finding in findings
        if finding.source is not FindingSource.AI
    ]

    if Severity.CRITICAL in severities:
        return Severity.CRITICAL
    if Severity.HIGH in severities:
        return Severity.HIGH
    if severities.count(Severity.MEDIUM) >= 3:
        return Severity.HIGH
    if Severity.MEDIUM in severities:
        return Severity.MEDIUM
    if severities.count(Severity.LOW) >= 5:
        return Severity.MEDIUM
    if Severity.LOW in severities:
        return Severity.LOW
    return Severity.NONE


def sort_findings(findings: Iterable[FindingDraft]) -> tuple[FindingDraft, ...]:
    """Partition deterministic and AI findings, then apply a stable fixed order."""
    return tuple(
        sorted(
            findings,
            key=lambda finding: (
                1 if finding.source is FindingSource.AI else 0,
                _SEVERITY_ORDER[finding.severity],
                finding.path,
                -1 if finding.new_line is None else finding.new_line,
                finding.rule_id,
            ),
        )
    )
