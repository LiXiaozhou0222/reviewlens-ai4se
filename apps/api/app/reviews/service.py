from datetime import UTC, datetime
from uuid import UUID

from app.diff_parser.normalizer import normalize_diff
from app.diff_parser.parser import ParsedDiff, parse_unified_diff
from app.models.api import FindingDraft, ReportView
from app.models.domain import AIReviewStatus
from app.providers.base import ProviderReviewResult, ReviewProvider
from app.reviews.redaction import redact_finding
from app.reviews.redaction import redact_provider_payload
from app.rules.dedupe import deduplicate_findings
from app.rules.engine import scan_gen_005
from app.rules.general import (
    scan_gen_001,
    scan_gen_002,
    scan_gen_003,
    scan_gen_004,
)
from app.rules.javascript import (
    scan_js_001,
    scan_js_002,
    scan_js_003,
    scan_js_004,
    scan_js_005,
    scan_js_006,
)
from app.rules.catalog import RULESET_VERSION
from app.rules.risk import calculate_deterministic_risk, sort_findings


APP_VERSION = "0.1.0"


def create_review(
    raw_diff: bytes, *, provider: ReviewProvider | None = None
) -> ReportView:
    """Create one deterministic, in-memory-only report from a unified diff."""
    normalized_diff = normalize_diff(raw_diff)
    parsed_diff = parse_unified_diff(normalized_diff.text)
    deterministic_findings = deduplicate_findings(_scan_rules(parsed_diff))
    ordered_findings = sort_findings(deterministic_findings)
    report_timestamp = _deterministic_timestamp(normalized_diff.sha256)
    ai_status, provider_result = _review_with_provider(provider)
    provider_name = provider_result.provider if provider_result is not None else None
    provider_model = provider_result.model if provider_result is not None else None
    findings = [redact_finding(finding) for finding in ordered_findings]
    if provider_result is not None and provider_result.status is AIReviewStatus.SUCCEEDED:
        findings.extend(provider_result.findings)

    return ReportView(
        report_id=UUID(hex=normalized_diff.sha256[:32]),
        created_at=report_timestamp,
        updated_at=report_timestamp,
        diff_sha256=normalized_diff.sha256,
        deterministic_risk=calculate_deterministic_risk(ordered_findings),
        ai_status=ai_status,
        provider=provider_name,
        model=provider_model,
        ruleset_version=RULESET_VERSION,
        app_version=APP_VERSION,
        findings=findings,
    )


def _review_with_provider(
    provider: ReviewProvider | None,
) -> tuple[AIReviewStatus, ProviderReviewResult | None]:
    if provider is None:
        return AIReviewStatus.NOT_CONFIGURED, None

    try:
        provider_result = provider.review(redact_provider_payload({}))
    except Exception:
        return AIReviewStatus.PROVIDER_UNAVAILABLE, None

    return provider_result.status, provider_result


def _scan_rules(parsed_diff: ParsedDiff) -> tuple[FindingDraft, ...]:
    scanners = (
        scan_gen_001,
        scan_gen_002,
        scan_gen_003,
        scan_gen_004,
        scan_gen_005,
        scan_js_001,
        scan_js_002,
        scan_js_003,
        scan_js_004,
        scan_js_005,
        scan_js_006,
    )
    return tuple(finding for scanner in scanners for finding in scanner(parsed_diff))


def _deterministic_timestamp(diff_sha256: str) -> datetime:
    return datetime.fromtimestamp(int(diff_sha256[:8], 16), tz=UTC)
