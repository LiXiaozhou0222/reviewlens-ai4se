import os

from fastapi import FastAPI

from app.api.health import create_health_router
from app.api.reviews import create_reviews_router
from app.config.settings import AppSettings, load_settings
from app.providers.mock_provider import MockReviewProvider


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.state.settings = settings
    provider = MockReviewProvider() if settings.mode == "demo" else None
    app.include_router(create_health_router(settings=settings))
    app.include_router(create_reviews_router(provider=provider))
    return app


def create_runtime_app() -> FastAPI:
    return create_app(load_settings(os.environ))
