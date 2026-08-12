from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from app.models.api import FindingDraft
from app.models.domain import AIReviewStatus


class ProviderReviewResult(BaseModel):
    """Schema-validated intermediate result before secondary redaction."""

    model_config = ConfigDict(extra="forbid")

    status: AIReviewStatus
    provider: str
    model: str
    findings: tuple[FindingDraft, ...]


class ReviewProvider(Protocol):
    """One-shot provider contract for controlled, already-redacted payloads."""

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult: ...
