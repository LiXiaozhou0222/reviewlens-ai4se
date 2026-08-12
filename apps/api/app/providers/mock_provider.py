from collections.abc import Mapping

from app.models.api import FindingDraft
from app.models.domain import AIReviewStatus, FindingSource, Severity
from app.providers.base import ProviderReviewResult
from app.reviews.redaction import redact_ai_finding


MOCK_PROVIDER_NAME = "mock"
MOCK_MODEL_NAME = "mock-reviewlens-v1"


class MockReviewProvider:
    """Deterministic, offline provider for demo, CI, and local development."""

    def review(self, payload: Mapping[str, object]) -> ProviderReviewResult:
        """Return controlled synthetic data without reading untrusted payload text."""

        del payload
        return ProviderReviewResult(
            status=AIReviewStatus.SUCCEEDED,
            provider=MOCK_PROVIDER_NAME,
            model=MOCK_MODEL_NAME,
            findings=(
                redact_ai_finding(
                    FindingDraft(
                        rule_id="AI-MOCK-001",
                        rule_version="1.0.0",
                        source=FindingSource.AI,
                        severity=Severity.LOW,
                        path="mock/synthetic-review",
                        new_line=None,
                        raw_excerpt="Synthetic mock finding.",
                        message="Mock provider supplied a synthetic review suggestion.",
                        suggestion=(
                            "Review deterministic findings before applying changes."
                        ),
                    )
                ),
            ),
        )
