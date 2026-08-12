from collections.abc import Mapping
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.diff_parser.normalizer import normalize_diff
from app.diff_parser.parser import ParsedDiff, parse_unified_diff
from app.models.api import FindingDraft, ReportView, SanitizedFinding
from app.models.domain import AIReviewStatus, FindingSource
from app.providers.base import ProviderReviewResult, ReviewProvider
from app.reviews.redaction import (
    ALLOWED_PROVIDER_FINDING_CONTRACTS,
    REDACTED_CREDENTIAL,
    REDACTED_PROVIDER_MESSAGE,
    REDACTED_PROVIDER_SUGGESTION,
    REDACTION_VERSION,
    redact_finding,
    redact_provider_payload,
)
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
    sanitized_deterministic = [redact_finding(finding) for finding in ordered_findings]
    provider_payload = _build_provider_payload(parsed_diff, sanitized_deterministic)
    ai_status, provider_result = _review_with_provider(provider, provider_payload)
    provider_name = provider_result.provider if provider_result is not None else None
    provider_model = provider_result.model if provider_result is not None else None
    findings = list(sanitized_deterministic)
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
    payload: dict[str, object],
) -> tuple[AIReviewStatus, ProviderReviewResult | None]:
    if provider is None:
        return AIReviewStatus.NOT_CONFIGURED, None

    try:
        provider_result = provider.review(redact_provider_payload(payload))
    except Exception:
        return AIReviewStatus.PROVIDER_UNAVAILABLE, None

    try:
        plain_result = _to_plain_provider_data(provider_result)
        validated_result = ProviderReviewResult.model_validate(plain_result)
    except Exception:
        # Provider-owned objects, mappings, and model internals are untrusted.
        return AIReviewStatus.INVALID_RESPONSE, None

    try:
        identity_matches = (
            validated_result.provider == provider.provider_name
            and validated_result.model == provider.model_name
        )
    except Exception:
        identity_matches = False
    if not identity_matches:
        return AIReviewStatus.INVALID_RESPONSE, None

    if not all(_is_safe_ai_finding(finding) for finding in validated_result.findings):
        return AIReviewStatus.INVALID_RESPONSE, None

    return validated_result.status, validated_result


def _to_plain_provider_data(
    value: object,
    *,
    _active_containers: set[int] | None = None,
) -> object:
    """Lower an untrusted result before canonical ProviderReviewResult validation.

    ``model_construct`` can create invalid models and normal validation may trust an
    existing model instance.  Reading model storage directly also avoids relying on
    ``model_dump``, which can fail while walking forged nested values.
    """

    if isinstance(value, Enum):
        return _to_plain_provider_data(
            value.value,
            _active_containers=_active_containers,
        )
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    active = _active_containers if _active_containers is not None else set()
    raw_value: object = vars(value) if isinstance(value, BaseModel) else value

    if isinstance(raw_value, Mapping):
        identity = id(raw_value)
        if identity in active:
            raise ValueError("cyclic provider result")
        active.add(identity)
        try:
            return {
                _to_plain_provider_data(key, _active_containers=active):
                _to_plain_provider_data(item, _active_containers=active)
                for key, item in raw_value.items()
            }
        finally:
            active.remove(identity)

    if isinstance(raw_value, (list, tuple)):
        identity = id(raw_value)
        if identity in active:
            raise ValueError("cyclic provider result")
        active.add(identity)
        try:
            return [
                _to_plain_provider_data(item, _active_containers=active)
                for item in raw_value
            ]
        finally:
            active.remove(identity)

    raise TypeError("provider result contains unsupported data")


def _build_provider_payload(
    parsed_diff: ParsedDiff,
    deterministic_findings: list[SanitizedFinding],
) -> dict[str, object]:
    return {
        "files": [
            {
                "path": parsed_file.new_path,
                "change_type": parsed_file.change_type,
                "added_line_count": parsed_file.added_line_count,
                "deleted_line_count": parsed_file.deleted_line_count,
            }
            for parsed_file in parsed_diff.files
        ],
        "deterministic_findings": [
            {
                "rule_id": finding.rule_id,
                "severity": finding.severity.value,
                "path": finding.path,
                "new_line": finding.new_line,
                "redaction_category": finding.redaction_category,
            }
            for finding in deterministic_findings
        ],
    }


def _is_safe_ai_finding(finding: SanitizedFinding) -> bool:
    return (
        finding.source is FindingSource.AI
        and finding.redacted is True
        and finding.redaction_version == REDACTION_VERSION
        and finding.redaction_category == "provider_text"
        and finding.excerpt == REDACTED_CREDENTIAL
        and finding.message == REDACTED_PROVIDER_MESSAGE
        and finding.suggestion == REDACTED_PROVIDER_SUGGESTION
        and (finding.rule_id, finding.rule_version, finding.path)
        in ALLOWED_PROVIDER_FINDING_CONTRACTS
    )


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
