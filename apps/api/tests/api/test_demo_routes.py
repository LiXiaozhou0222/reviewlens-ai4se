from fastapi.testclient import TestClient

from app.config.settings import AppSettings
from app.main import create_app
from app.models.api import ReportView
from app.models.domain import AIReviewStatus


def _valid_diff() -> bytes:
    return (
        "diff --git a/src/example.ts b/src/example.ts\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/example.ts\n"
        "+++ b/src/example.ts\n"
        "@@ -0,0 +1 @@\n"
        '+console.log("review me")\n'
    ).encode("utf-8")


def test_review_route_is_available_in_demo_and_private_modes() -> None:
    demo_response = TestClient(create_app(AppSettings(mode="demo"))).post(
        "/api/v1/reviews",
        content=_valid_diff(),
        headers={"content-type": "application/octet-stream"},
    )
    private_response = TestClient(create_app(AppSettings(mode="private"))).post(
        "/api/v1/reviews",
        content=_valid_diff(),
        headers={"content-type": "application/octet-stream"},
    )

    assert demo_response.status_code == 200
    assert private_response.status_code == 200
    assert ReportView.model_validate(demo_response.json()).ai_status is AIReviewStatus.SUCCEEDED
    assert (
        ReportView.model_validate(private_response.json()).ai_status
        is AIReviewStatus.NOT_CONFIGURED
    )


def test_demo_registers_no_private_or_vault_routes() -> None:
    app = create_app(AppSettings(mode="demo"))

    registered_paths = set(app.openapi()["paths"])

    assert "/api/v1/reviews" in registered_paths
    assert not any(path.startswith("/admin/") for path in registered_paths)
    assert not any("vault" in path.lower() for path in registered_paths)
