from pathlib import Path


def test_makefile_exposes_real_install_test_lint_and_build_commands() -> None:
    makefile = Path(__file__).resolve().parents[4] / "Makefile"

    content = makefile.read_text(encoding="utf-8")

    for target in ("install:", "test:", "lint:", "build:"):
        assert target in content
    assert "apps/api/requirements.lock" in content
    assert "apps/web && npm ci" in content
    assert "python -m pytest -q" in content
    assert "npm run test -- --run" in content
    assert "npm run typecheck" in content
    assert "npm run build" in content
    assert "docker buildx build --platform linux/amd64" in content
