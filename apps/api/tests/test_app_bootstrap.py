from fastapi import FastAPI

from app.config.settings import AppSettings
from app.main import create_app


def test_create_app_preserves_explicit_private_mode() -> None:
    app = create_app(AppSettings(mode="private"))

    assert isinstance(app, FastAPI)
    assert app.state.settings.mode == "private"
