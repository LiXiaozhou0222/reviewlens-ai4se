from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config.settings import AppSettings
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION
from app.rules.javascript import JAVASCRIPT_RULES


_EXPECTED_GENERAL_RULE_IDS = tuple(f"GEN-{number:03d}" for number in range(1, 6))
_EXPECTED_JAVASCRIPT_RULE_IDS = tuple(f"JS-{number:03d}" for number in range(1, 7))


def create_health_router(*, settings: AppSettings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/ready")
    def ready() -> JSONResponse:
        if not _deterministic_review_is_ready(settings):
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready"},
            )
        return JSONResponse(content={"status": "ready", "mode": settings.mode})

    return router


def _deterministic_review_is_ready(settings: AppSettings) -> bool:
    return (
        settings.mode in {"private", "demo"}
        and bool(RULESET_VERSION)
        and tuple(rule.rule_id for rule in GENERAL_RULES) == _EXPECTED_GENERAL_RULE_IDS
        and tuple(rule.rule_id for rule in JAVASCRIPT_RULES)
        == _EXPECTED_JAVASCRIPT_RULE_IDS
    )
