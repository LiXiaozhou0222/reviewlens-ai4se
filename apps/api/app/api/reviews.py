from fastapi import APIRouter, HTTPException, Request, status

from app.diff_parser.normalizer import DiffNormalizationError
from app.models.api import ReportView
from app.models.errors import PublicErrorCode
from app.providers.base import ReviewProvider
from app.reviews.service import create_review


_PAYLOAD_TOO_LARGE_CODES = {
    PublicErrorCode.INPUT_TOO_LARGE,
    PublicErrorCode.LINE_LIMIT_EXCEEDED,
}


def create_reviews_router(*, provider: ReviewProvider | None) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["reviews"])

    @router.post("/reviews", response_model=ReportView)
    async def post_review(request: Request) -> ReportView:
        raw_diff = await request.body()
        try:
            return create_review(raw_diff, provider=provider)
        except DiffNormalizationError as error:
            response_status = (
                status.HTTP_413_CONTENT_TOO_LARGE
                if error.code in _PAYLOAD_TOO_LARGE_CODES
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(
                status_code=response_status,
                detail={"code": error.code.value},
            ) from None

    return router
