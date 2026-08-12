import pytest
from fastapi.testclient import TestClient

from app.config.settings import AppSettings
from app.diff_parser.normalizer import MAX_DIFF_BYTES, MAX_DIFF_LINES
from app.main import create_app
from app.models.api import ReportView
from app.models.domain import AIReviewStatus, Severity
from app.models.errors import PublicErrorCode


def _credential_diff(secret: str = "rl_fake_api_secret_T11_1_Q7XZ") -> bytes:
    return (
        "diff --git a/src/settings.py b/src/settings.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1 @@\n"
        f'+API_KEY = "{secret}"\n'
    ).encode("utf-8")


def test_post_review_returns_sanitized_report() -> None:
    fake_secret = "rl_fake_api_secret_T11_1_Q7XZ"
    client = TestClient(create_app(AppSettings(mode="private")))

    response = client.post(
        "/api/v1/reviews",
        content=_credential_diff(fake_secret),
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    report = ReportView.model_validate(response.json())
    assert report.deterministic_risk is Severity.CRITICAL
    assert report.ai_status is AIReviewStatus.NOT_CONFIGURED
    assert [finding.rule_id for finding in report.findings] == ["GEN-001"]
    assert all(finding.redacted for finding in report.findings)

    serialized = response.text
    assert fake_secret not in serialized
    assert "API_KEY" not in serialized
    assert "raw_excerpt" not in serialized


@pytest.mark.parametrize(
    ("payload", "expected_status", "expected_code"),
    [
        (b"", 400, PublicErrorCode.INPUT_EMPTY),
        (b"\xff\xfe", 400, PublicErrorCode.INVALID_UTF8),
        (b"not a unified diff", 400, PublicErrorCode.INVALID_DIFF_FORMAT),
        (
            b"diff --git a/a b/a\n",
            400,
            PublicErrorCode.INVALID_DIFF_FORMAT,
        ),
        (
            b"x" * (MAX_DIFF_BYTES + 1),
            413,
            PublicErrorCode.INPUT_TOO_LARGE,
        ),
        (
            ("diff --git a/a b/a\n" + "\n" * MAX_DIFF_LINES).encode("utf-8"),
            413,
            PublicErrorCode.LINE_LIMIT_EXCEEDED,
        ),
    ],
    ids=[
        "empty",
        "invalid-utf8",
        "invalid-format",
        "header-only",
        "byte-limit",
        "line-limit",
    ],
)
def test_post_review_maps_input_errors_to_public_codes(
    payload: bytes,
    expected_status: int,
    expected_code: PublicErrorCode,
) -> None:
    client = TestClient(create_app(AppSettings(mode="private")))

    response = client.post(
        "/api/v1/reviews",
        content=payload,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": {"code": expected_code.value}}
    assert "traceback" not in response.text.lower()
