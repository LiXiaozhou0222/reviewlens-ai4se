import os

from fastapi import FastAPI

from app.config.settings import AppSettings, load_settings


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.state.settings = settings
    return app


def create_runtime_app() -> FastAPI:
    return create_app(load_settings(os.environ))
