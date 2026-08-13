from fastapi import APIRouter, HTTPException, Request, status

from app.diff_parser.normalizer import DiffNormalizationError
from app.models.api import ReportView
from app.models.errors import PublicErrorCode
from app.observability.logging import input_size_bucket
from app.providers.base import ReviewProvider
from app.reviews.service import create_review_with_metrics


_PAYLOAD_TOO_LARGE_CODES = {
    PublicErrorCode.INPUT_TOO_LARGE,
    PublicErrorCode.LINE_LIMIT_EXCEEDED,
}


def create_reviews_router(*, provider: ReviewProvider | None) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["reviews"])

    @router.post("/reviews", response_model=ReportView)
    async def post_review(request: Request) -> ReportView:
        raw_diff = await request.body()
        request.state.review_metrics = {
            "input_size_bucket": input_size_bucket(len(raw_diff)),
            "file_count": 0,
            "ai_status": None,
            "error_code": None,
        }
        try:
            result = create_review_with_metrics(raw_diff, provider=provider)
            request.state.review_metrics.update(
                file_count=result.file_count,
                ai_status=result.report.ai_status.value,
            )
            return result.report
        except DiffNormalizationError as error:
            request.state.review_metrics["error_code"] = error.code.value
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
