from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.domain import AIReviewStatus, FindingSource, Severity


class FindingDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_version: str
    source: FindingSource
    severity: Severity
    path: str
    new_line: int | None
    raw_excerpt: str
    message: str
    suggestion: str


class SanitizedFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_version: str
    source: FindingSource
    severity: Severity
    path: str
    new_line: int | None
    excerpt: str
    message: str
    suggestion: str
    redacted: bool
    redaction_version: str
    redaction_category: str | None


class ReportView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: UUID
    created_at: datetime
    updated_at: datetime
    diff_sha256: str
    deterministic_risk: Severity
    ai_status: AIReviewStatus
    provider: str | None
    model: str | None
    ruleset_version: str
    app_version: str
    findings: list[SanitizedFinding]
