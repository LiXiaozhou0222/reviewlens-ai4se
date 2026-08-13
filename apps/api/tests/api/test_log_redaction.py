import json
import logging

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.config.settings import AppSettings
from app.main import create_app


def _credential_diff(secret: str) -> bytes:
    return (
        "diff --git a/src/settings.py b/src/settings.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/settings.py\n"
        "+++ b/src/settings.py\n"
        "@@ -0,0 +1 @@\n"
        f'+API_KEY = \"{secret}\"\n'
    ).encode("utf-8")


def test_structured_log_excludes_diff_and_secret(caplog) -> None:
    secret = "rl_fake_secret_T12_5_NEVER_LOG"
    request_id = "12345678-1234-4234-9234-123456789abc"
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post(
            "/api/v1/reviews",
            content=_credential_diff(secret),
            headers={"x-request-id": request_id},
        )

    assert response.status_code == 200
    records = [json.loads(record.message) for record in caplog.records]
    assert records == [
        {
            "event": "request_completed",
            "request_id": request_id,
            "mode": "private",
            "endpoint": "POST /api/v1/reviews",
            "status_code": 200,
            "input_size_bucket": "0-10KB",
            "file_count": 1,
            "ai_status": "NOT_CONFIGURED",
            "error_code": None,
            "ruleset_version": "1.0.0",
            "app_version": "0.1.0",
            "duration_ms": records[0]["duration_ms"],
        }
    ]
    assert response.headers["x-request-id"] == request_id
    assert isinstance(records[0]["duration_ms"], int)
    assert records[0]["duration_ms"] >= 0
    serialized = "\n".join(record.message for record in caplog.records)
    assert secret not in serialized
    assert "API_KEY" not in serialized
    assert "src/settings.py" not in serialized


def test_invalid_review_logs_public_error_without_body(caplog) -> None:
    secret = "invalid-body-secret-T12-5"
    client = TestClient(create_app(AppSettings(mode="demo")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post("/api/v1/reviews", content=secret.encode())

    assert response.status_code == 400
    record = json.loads(caplog.records[-1].message)
    assert record["error_code"] == "INVALID_DIFF_FORMAT"
    assert record["file_count"] == 0
    assert record["ai_status"] is None
    assert secret not in caplog.records[-1].message


def test_untrusted_request_id_is_not_logged_or_echoed(caplog) -> None:
    secret = "rl_fake_secret_from_request_id_T12_5"
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post(
            "/api/v1/reviews",
            content=_credential_diff("safe-fixture-secret"),
            headers={"x-request-id": secret},
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] != secret
    record = json.loads(caplog.records[-1].message)
    assert record["request_id"] == response.headers["x-request-id"]
    serialized = "\n".join(record.message for record in caplog.records)
    assert secret not in serialized


def test_unhandled_error_still_logs_and_returns_request_id(caplog) -> None:
    app = create_app(AppSettings(mode="private"))
    router = APIRouter()

    @router.get("/boom")
    async def boom() -> None:
        raise RuntimeError("internal failure")

    app.include_router(router)
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.headers["x-request-id"]
    record = json.loads(caplog.records[-1].message)
    assert record["request_id"] == response.headers["x-request-id"]
    assert record["status_code"] == 500
    assert record["error_code"] == "INTERNAL_ERROR"


def test_unmatched_path_does_not_log_user_controlled_path(caplog) -> None:
    secret = "SECRET_PATH_T12_5_DO_NOT_LOG"
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.get(f"/api/v1/reviews/{secret}")

    assert response.status_code == 404
    assert response.json() == {"detail": {"code": "INVALID_REQUEST"}}
    record = json.loads(caplog.records[-1].message)
    assert record["endpoint"] == "GET <unmatched>"
    assert record["error_code"] == "INVALID_REQUEST"
    assert secret not in caplog.records[-1].message


def test_validation_error_logs_public_error_code(caplog) -> None:
    secret = "SECRET_VALIDATION_T12_5_DO_NOT_LOG"
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post(
            "/admin/v1/vault/unlock",
            json={"master_password": [secret]},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": {"code": "INVALID_REQUEST"}}
    record = json.loads(caplog.records[-1].message)
    assert record["endpoint"] == "POST /admin/v1/vault/unlock"
    assert record["error_code"] == "INVALID_REQUEST"
    assert secret not in caplog.records[-1].message


def test_custom_http_method_does_not_enter_request_log(caplog) -> None:
    secret = "SECRET_METHOD_T12_5_DO_NOT_LOG"
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.request(secret, "/health")

    assert response.status_code == 405
    record = json.loads(caplog.records[-1].message)
    assert record["endpoint"] == "<other> /health"
    assert secret not in caplog.records[-1].message


def test_method_not_allowed_uses_public_error_and_preserves_allow_header(caplog) -> None:
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post("/health")

    assert response.status_code == 405
    assert response.json() == {"detail": {"code": "INVALID_REQUEST"}}
    assert response.headers["allow"] == "GET"
    assert response.headers["x-request-id"]
    record = json.loads(caplog.records[-1].message)
    assert record["endpoint"] == "POST /health"
    assert record["error_code"] == "INVALID_REQUEST"
    assert record["request_id"] == response.headers["x-request-id"]


def test_oversize_diff_logs_over_limit_bucket_without_body(caplog) -> None:
    secret = "SECRET_OVERSIZE_T12_5_DO_NOT_LOG"
    payload = (secret + "x" * (512_001 - len(secret))).encode("utf-8")
    client = TestClient(create_app(AppSettings(mode="private")))

    with caplog.at_level(logging.INFO, logger="reviewlens.request"):
        response = client.post("/api/v1/reviews", content=payload)

    assert response.status_code == 413
    record = json.loads(caplog.records[-1].message)
    assert record["input_size_bucket"] == ">500KB"
    assert record["error_code"] == "INPUT_TOO_LARGE"
    assert secret not in caplog.records[-1].message
