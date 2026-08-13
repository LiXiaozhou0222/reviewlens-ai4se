from app.models.api import FindingDraft


def deduplicate_findings(
    findings: tuple[FindingDraft, ...],
) -> tuple[FindingDraft, ...]:
    """Keep the first finding for each stable rule-location-content key."""
    unique_findings: list[FindingDraft] = []
    seen_keys: set[tuple[str, str, int | None, str, int | None]] = set()

    for finding in findings:
        key = (
            finding.rule_id,
            finding.path,
            finding.new_line,
            " ".join(finding.raw_excerpt.split()),
            finding.match_start,
        )
        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_findings.append(finding)

    return tuple(unique_findings)
