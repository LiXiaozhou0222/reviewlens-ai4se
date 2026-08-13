import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import create_health_router
from app.api.admin import create_admin_router
from app.api.reviews import create_reviews_router
from app.config.settings import AppSettings, load_settings
from app.credentials.service import VaultService
from app.observability.logging import request_log_middleware
from app.providers.mock_provider import MockReviewProvider


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.middleware("http")(request_log_middleware)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        _set_error_code(request, "INVALID_REQUEST")
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": "INVALID_REQUEST"}},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, error: StarletteHTTPException
    ) -> JSONResponse:
        detail = error.detail
        if not (isinstance(detail, dict) and isinstance(detail.get("code"), str)):
            detail = {"code": "INVALID_REQUEST"}

        if isinstance(detail, dict) and isinstance(detail.get("code"), str):
            _set_error_code(request, detail["code"])

        return JSONResponse(
            status_code=error.status_code,
            content={"detail": detail},
            headers=error.headers,
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


def _set_error_code(request: Request, error_code: str) -> None:
    request.state.review_metrics = {
        **getattr(request.state, "review_metrics", {}),
        "error_code": error_code,
    }
