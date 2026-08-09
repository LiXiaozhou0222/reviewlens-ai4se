from fastapi import FastAPI
from pydantic import ValidationError
import pytest

from app.config.settings import AppSettings, load_settings
from app.main import create_app


def test_create_app_preserves_explicit_private_mode() -> None:
    app = create_app(AppSettings(mode="private"))

    assert isinstance(app, FastAPI)
    assert app.state.settings.mode == "private"


def test_load_settings_rejects_unknown_app_mode() -> None:
    with pytest.raises(ValidationError):
        load_settings({"APP_MODE": "shared"})


@pytest.mark.parametrize("app_mode", ["private", "demo"])
def test_load_settings_accepts_valid_app_mode(app_mode: str) -> None:
    settings = load_settings({"APP_MODE": app_mode})

    assert settings.mode == app_mode
