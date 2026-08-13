from pathlib import Path


def test_ci_definitions_run_mock_backed_unified_tests() -> None:
    repository_root = Path(__file__).resolve().parents[4]
    github = (repository_root / ".github" / "workflows" / "test.yml").read_text(
        encoding="utf-8"
    )
    gitlab = (repository_root / ".gitlab-ci.yml").read_text(encoding="utf-8")

    for workflow in (github, gitlab):
        assert "make test" in workflow
        assert "APP_MODE: demo" in workflow
        assert "OPENAI_API_KEY" not in workflow

    assert "pull_request:" in github
    assert "unit-test:" in gitlab
    assert "NODE_VERSION: 22.16.0" in gitlab
