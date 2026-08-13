"""Structured, allowlist-only request logging."""

import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.reviews.service import APP_VERSION
from app.rules.catalog import RULESET_VERSION


REQUEST_LOGGER = logging.getLogger("reviewlens.request")
_ALLOWED_HTTP_METHODS = frozenset(
    {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
)


def input_size_bucket(byte_count: int) -> str:
    if byte_count <= 10_240:
        return "0-10KB"
    if byte_count <= 102_400:
        return "10-100KB"
    if byte_count <= 512_000:
        return "100-500KB"
    return ">500KB"


async def request_log_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = time.perf_counter()
    request_id = _safe_request_id(request.headers.get("x-request-id"))
    request.state.request_id = request_id
    response: Response | None = None
    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse(
            status_code=500,
            content={"detail": {"code": "INTERNAL_ERROR"}},
        )
        request.state.review_metrics = {
            **getattr(request.state, "review_metrics", {}),
            "error_code": "INTERNAL_ERROR",
        }
    finally:
        response.headers["x-request-id"] = request_id
        _log_request(request, request_id, response.status_code, started)
    return response


def _safe_request_id(header_value: str | None) -> str:
    if header_value is not None:
        try:
            return str(UUID(header_value))
        except ValueError:
            pass
    return str(uuid4())


def _log_request(
    request: Request,
    request_id: str,
    status_code: int,
    started: float,
) -> None:
    request_metrics = getattr(request.state, "review_metrics", {})
    event: dict[str, Any] = {
        "event": "request_completed",
        "request_id": request_id,
        "mode": request.app.state.settings.mode,
        "endpoint": _safe_endpoint(request),
        "status_code": status_code,
        "input_size_bucket": request_metrics.get("input_size_bucket"),
        "file_count": request_metrics.get("file_count"),
        "ai_status": request_metrics.get("ai_status"),
        "error_code": request_metrics.get("error_code"),
        "ruleset_version": RULESET_VERSION,
        "app_version": APP_VERSION,
        "duration_ms": max(0, int((time.perf_counter() - started) * 1000)),
    }
    REQUEST_LOGGER.info(json.dumps(event, separators=(",", ":"), sort_keys=True))


def _safe_endpoint(request: Request) -> str:
    route_path = getattr(request.scope.get("route"), "path", None)
    method = request.method if request.method in _ALLOWED_HTTP_METHODS else "<other>"
    if isinstance(route_path, str):
        return f"{method} {route_path}"
    return f"{method} <unmatched>"
