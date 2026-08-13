import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import create_health_router
from app.api.admin import create_admin_router
from app.api.reviews import create_reviews_router
from app.config.settings import AppSettings, load_settings
from app.credentials.service import VaultService
from app.observability.logging import request_log_middleware
from app.providers.mock_provider import MockReviewProvider


def create_app(settings: AppSettings, *, web_dist: Path | None = None) -> FastAPI:
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
    if web_dist is not None:
        _mount_web_app(app, web_dist)
    return app


def create_runtime_app() -> FastAPI:
    web_dist = Path("/app/web")
    return create_app(
        load_settings(os.environ), web_dist=web_dist if web_dist.is_dir() else None
    )


def _set_error_code(request: Request, error_code: str) -> None:
    request.state.review_metrics = {
        **getattr(request.state, "review_metrics", {}),
        "error_code": error_code,
    }


def _mount_web_app(app: FastAPI, web_dist: Path) -> None:
    index_path = web_dist / "index.html"
    if not index_path.is_file():
        raise ValueError("Built web assets must include index.html.")

    app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="web-assets")

    @app.get("/{web_path:path}", include_in_schema=False)
    def web_history_fallback(web_path: str) -> FileResponse:
        if web_path.startswith(("api/", "admin/", "health", "ready")):
            raise StarletteHTTPException(status_code=404)
        return FileResponse(index_path)
