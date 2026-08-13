from pathlib import Path


def test_single_image_serves_web_and_review_api() -> None:
    dockerfile = Path(__file__).resolve().parents[4] / "Dockerfile"

    content = dockerfile.read_text(encoding="utf-8")

    assert "FROM node:" in content
    assert "npm.cmd" not in content
    assert "npm ci" in content
    assert "npm run build" in content
    assert "FROM python:3.12" in content
    assert "COPY --from=web-build /web/dist /app/web" in content
    assert (
        'CMD ["uvicorn", "app.main:create_runtime_app", "--factory", '
        '"--host", "0.0.0.0", "--port", "8080"]'
    ) in content
