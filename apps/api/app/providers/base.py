from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from app.models.api import SanitizedFinding
from app.models.domain import AIReviewStatus


class ProviderReviewResult(BaseModel):
    """Public-safe provider result after schema validation and redaction."""

    model_config = ConfigDict(extra="forbid")

    status: AIReviewStatus
    provider: str
    model: str
    findings: tuple[SanitizedFinding, ...]


class ReviewProvider(Protocol):
    """One-shot provider contract for controlled, already-redacted payloads."""

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult: ...
