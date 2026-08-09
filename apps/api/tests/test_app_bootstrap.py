from fastapi import FastAPI
import pytest

from app.config.settings import AppSettings, load_settings
from app.main import create_app


def test_create_app_preserves_explicit_private_mode() -> None:
    app = create_app(AppSettings(mode="private"))

    assert isinstance(app, FastAPI)
    assert app.state.settings.mode == "private"


def test_load_settings_rejects_unknown_app_mode() -> None:
    invalid_mode = "untrusted-public-mode"

    with pytest.raises(ValueError) as error:
        load_settings({"APP_MODE": invalid_mode})

    assert str(error.value) == "APP_MODE must be explicitly set to 'private' or 'demo'."
    assert invalid_mode not in str(error.value)


def test_load_settings_rejects_missing_app_mode() -> None:
    with pytest.raises(ValueError) as error:
        load_settings({})

    assert str(error.value) == "APP_MODE must be explicitly set to 'private' or 'demo'."


@pytest.mark.parametrize("app_mode", ["private", "demo"])
def test_load_settings_accepts_valid_app_mode(app_mode: str) -> None:
    settings = load_settings({"APP_MODE": app_mode})

    assert settings.mode == app_mode
