from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import AppSettings
from app.credentials.service import VaultService
from app.main import create_app


MASTER_PASSWORD = "test-only-admin-password"
FAKE_API_KEY = "fake-api-key-ending-9F2A"
REPLACEMENT_API_KEY = "replacement-key-ending-7B3C"


def _private_client(tmp_path: Path) -> TestClient:
    app = create_app(AppSettings(mode="private"))
    app.state.vault_service = VaultService(tmp_path / "credentials" / "vault.json")
    return TestClient(app)


def test_demo_registers_no_vault_route() -> None:
    app = create_app(AppSettings(mode="demo"))

    paths = set(app.openapi()["paths"])

    assert not any(path.startswith("/admin/v1/vault/") for path in paths)


def test_private_registers_only_vault_admin_routes(tmp_path: Path) -> None:
    app = create_app(AppSettings(mode="private"))

    paths = set(app.openapi()["paths"])

    assert {
        "/admin/v1/vault/status",
        "/admin/v1/vault/initialize",
        "/admin/v1/vault/unlock",
        "/admin/v1/vault/lock",
        "/admin/v1/vault/update",
        "/admin/v1/vault/clear",
    } <= paths
    assert not any(path.startswith("/api/v1/") and "vault" in path for path in paths)


def test_private_status_is_masked_and_never_returns_api_key(tmp_path: Path) -> None:
    client = _private_client(tmp_path)
    client.app.state.vault_service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )

    response = client.get("/admin/v1/vault/status")

    assert response.status_code == 200
    assert response.json() == {
        "exists": True,
        "unlocked": False,
        "provider": "openai",
        "model": "gpt-test-model",
        "masked_api_key": "••••9F2A",
    }
    assert FAKE_API_KEY not in response.text


def test_private_lifecycle_routes_delegate_to_vault_service(tmp_path: Path) -> None:
    client = _private_client(tmp_path)

    initialize = client.post(
        "/admin/v1/vault/initialize",
        json={
            "master_password": MASTER_PASSWORD,
            "api_key": FAKE_API_KEY,
            "model": "gpt-test-model",
        },
    )
    assert initialize.status_code == 204

    unlock = client.post(
        "/admin/v1/vault/unlock", json={"master_password": MASTER_PASSWORD}
    )
    assert unlock.status_code == 204
    assert client.get("/admin/v1/vault/status").json()["unlocked"] is True

    update = client.post(
        "/admin/v1/vault/update",
        json={
            "master_password": MASTER_PASSWORD,
            "api_key": REPLACEMENT_API_KEY,
            "model": "gpt-replacement-model",
        },
    )
    assert update.status_code == 204
    assert client.get("/admin/v1/vault/status").json()["unlocked"] is False

    unlock_again = client.post(
        "/admin/v1/vault/unlock", json={"master_password": MASTER_PASSWORD}
    )
    assert unlock_again.status_code == 204
    assert client.post("/admin/v1/vault/lock").status_code == 204
    assert client.post(
        "/admin/v1/vault/clear", json={"master_password": MASTER_PASSWORD}
    ).status_code == 204
    assert client.get("/admin/v1/vault/status").json()["exists"] is False


def test_admin_wrong_password_has_stable_error_without_internal_details(
    tmp_path: Path,
) -> None:
    client = _private_client(tmp_path)
    client.app.state.vault_service.initialize(
        master_password=MASTER_PASSWORD,
        api_key=FAKE_API_KEY,
        model="gpt-test-model",
    )

    response = client.post(
        "/admin/v1/vault/unlock", json={"master_password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": {"code": "VAULT_OPERATION_FAILED"}}
    assert "Vault unlock failed" not in response.text
    assert "Traceback" not in response.text


def test_admin_validation_error_does_not_echo_credentials(tmp_path: Path) -> None:
    client = _private_client(tmp_path)
    submitted_secret = "SECRET-MASTER-DO-NOT-ECHO"

    response = client.post(
        "/admin/v1/vault/unlock", json={"master_password": [submitted_secret]}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": {"code": "INVALID_REQUEST"}}
    assert submitted_secret not in response.text
