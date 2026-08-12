from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import health as health_api
from app.config.settings import AppSettings
from app.credentials.service import VaultService
from app.main import create_app


@pytest.mark.parametrize("mode", ["private", "demo"])
def test_health_reports_process_liveness_with_a_minimal_public_response(
    mode: str,
) -> None:
    response = TestClient(create_app(AppSettings(mode=mode))).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("mode", ["private", "demo"])
def test_ready_accepts_reviews_in_both_supported_modes(mode: str) -> None:
    response = TestClient(create_app(AppSettings(mode=mode))).get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_is_available_when_vault_is_locked(tmp_path: Path) -> None:
    fake_api_key = "rl_fake_api_secret_T12_1_LOCKED"
    vault_path = tmp_path / "private" / "credentials" / "vault.json"
    vault_service = VaultService(vault_path)
    vault_service.initialize(
        master_password="fake-master-password-T12-1",
        api_key=fake_api_key,
        model="fake-model-T12-1",
    )
    assert vault_service.is_unlocked is False

    app = create_app(AppSettings(mode="private"))
    app.state.vault_service = vault_service
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    assert fake_api_key not in response.text
    assert str(vault_path) not in response.text
    assert "traceback" not in response.text.casefold()


@pytest.mark.parametrize("catalog_name", ["GENERAL_RULES", "JAVASCRIPT_RULES"])
def test_ready_rejects_an_incomplete_deterministic_ruleset(
    monkeypatch: pytest.MonkeyPatch,
    catalog_name: str,
) -> None:
    monkeypatch.setattr(health_api, catalog_name, (), raising=False)

    response = TestClient(create_app(AppSettings(mode="demo"))).get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


@pytest.mark.parametrize("catalog_name", ["GENERAL_RULES", "JAVASCRIPT_RULES"])
def test_ready_rejects_a_ruleset_missing_one_required_rule(
    monkeypatch: pytest.MonkeyPatch,
    catalog_name: str,
) -> None:
    catalog = getattr(health_api, catalog_name)
    monkeypatch.setattr(health_api, catalog_name, catalog[:-1])

    response = TestClient(create_app(AppSettings(mode="private"))).get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
