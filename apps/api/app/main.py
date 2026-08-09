from fastapi import FastAPI

from app.config.settings import AppSettings


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.state.settings = settings
    return app
