"""Loopback-only private Vault management routes."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.credentials.service import VaultService, VaultUnlockError


class InitializeVaultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    master_password: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    model: str = Field(min_length=1)


class UnlockVaultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    master_password: str = Field(min_length=1)


class UpdateVaultRequest(InitializeVaultRequest):
    pass


def create_admin_router() -> APIRouter:
    """Build the private admin router; the app state supplies the Vault service."""
    router = APIRouter(prefix="/admin/v1/vault", tags=["admin-vault"])

    def vault_service(request: Request) -> VaultService:
        service = getattr(request.app.state, "vault_service", None)
        if not isinstance(service, VaultService):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "VAULT_UNAVAILABLE"},
            )
        return service

    service_dependency = Annotated[VaultService, Depends(vault_service)]

    @router.get("/status")
    def get_status(service: service_dependency) -> dict[str, str | bool | None]:
        return service.status()

    @router.post("/initialize", status_code=status.HTTP_204_NO_CONTENT)
    def initialize(
        payload: InitializeVaultRequest, service: service_dependency
    ) -> Response:
        _run_vault_operation(
            lambda: service.initialize(
                master_password=payload.master_password,
                api_key=payload.api_key,
                model=payload.model,
            )
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/unlock", status_code=status.HTTP_204_NO_CONTENT)
    def unlock(payload: UnlockVaultRequest, service: service_dependency) -> Response:
        _run_vault_operation(
            lambda: service.unlock(master_password=payload.master_password)
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/lock", status_code=status.HTTP_204_NO_CONTENT)
    def lock(service: service_dependency) -> Response:
        service.lock()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/update", status_code=status.HTTP_204_NO_CONTENT)
    def update(payload: UpdateVaultRequest, service: service_dependency) -> Response:
        _run_vault_operation(
            lambda: service.update(
                master_password=payload.master_password,
                api_key=payload.api_key,
                model=payload.model,
            )
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
    def clear(payload: UnlockVaultRequest, service: service_dependency) -> Response:
        _run_vault_operation(
            lambda: service.clear(master_password=payload.master_password)
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


def _run_vault_operation(operation: Callable[[], None]) -> None:
    try:
        operation()
    except VaultUnlockError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "VAULT_OPERATION_FAILED"},
        ) from None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "VAULT_OPERATION_FAILED"},
        ) from None
