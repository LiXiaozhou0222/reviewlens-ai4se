import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.health import create_health_router
from app.api.admin import create_admin_router
from app.api.reviews import create_reviews_router
from app.config.settings import AppSettings, load_settings
from app.credentials.service import VaultService
from app.providers.mock_provider import MockReviewProvider


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: object, _error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": "INVALID_REQUEST"}},
        )

    app.state.settings = settings
    provider = MockReviewProvider() if settings.mode == "demo" else None
    app.include_router(create_health_router(settings=settings))
    app.include_router(create_reviews_router(provider=provider))
    if settings.mode == "private":
        app.state.vault_service = VaultService(
            Path("data") / "credentials" / "vault.json"
        )
        app.include_router(create_admin_router())
    return app


def create_runtime_app() -> FastAPI:
    return create_app(load_settings(os.environ))
