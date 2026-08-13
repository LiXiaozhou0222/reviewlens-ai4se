from dataclasses import dataclass

from app.models.domain import FindingSource, Severity

RULESET_VERSION = "1.0.0"


@dataclass(frozen=True)
class RuleMetadata:
    rule_id: str
    name: str
    source: FindingSource
    severity: Severity
    category: str
    scope: str
    message: str
    suggestion: str


GENERAL_RULES = (
    RuleMetadata(
        rule_id="GEN-001",
        name="High-confidence credential",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.CRITICAL,
        category="general",
        scope="added-line",
        message="A high-confidence credential was added.",
        suggestion="Remove the credential and use a secure secret store.",
    ),
    RuleMetadata(
        rule_id="GEN-002",
        name="Destructive shell or database operation",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.HIGH,
        category="general",
        scope="added-line",
        message="A destructive shell or database operation was added.",
        suggestion="Confirm the operation is necessary and add appropriate safeguards.",
    ),
    RuleMetadata(
        rule_id="GEN-003",
        name="Maintenance marker",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.LOW,
        category="general",
        scope="added-line",
        message="A TODO, FIXME, or HACK marker was added.",
        suggestion="Resolve the work item or track it outside the code change.",
    ),
    RuleMetadata(
        rule_id="GEN-004",
        name="Non-loopback HTTP address",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.MEDIUM,
        category="general",
        scope="added-line",
        message="A non-loopback plain HTTP address was added.",
        suggestion="Use HTTPS unless plain HTTP is explicitly required.",
    ),
    RuleMetadata(
        rule_id="GEN-005",
        name="Large file change",
        source=FindingSource.GENERAL_RULE,
        severity=Severity.MEDIUM,
        category="general",
        scope="file-level",
        message="A single text file has a large change size.",
        suggestion="Consider splitting the change into smaller, reviewable pieces.",
    ),
)
