from pathlib import Path


def test_release_workflow_builds_one_linux_amd64_ghcr_image_from_tags() -> None:
    workflow = (
        Path(__file__).resolve().parents[4]
        / ".github"
        / "workflows"
        / "release.yml"
    ).read_text(encoding="utf-8")

    assert "tags:" in workflow
    assert "linux/amd64" in workflow
    assert "docker/build-push-action" in workflow
    assert "ghcr.io" in workflow
    assert "latest" in workflow
    assert "Dockerfile" in workflow
