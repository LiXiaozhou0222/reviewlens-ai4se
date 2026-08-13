from pathlib import Path


def test_documentation_describes_real_local_state_without_fabricated_evidence() -> None:
    root = Path(__file__).resolve().parents[4]
    readme = (root / "README.md").read_text(encoding="utf-8")
    reflection_evidence = (root / "docs" / "reflection-evidence.md").read_text(
        encoding="utf-8"
    )
    verifier = (root / "scripts" / "verify-documentation.ps1").read_text(
        encoding="utf-8"
    )

    for heading in ("## 安装", "## 运行", "## 安全边界", "## 已知限制"):
        assert heading in readme
    assert "ghcr.io/lixiaozhou0222/reviewlens:0.1.0" in readme
    assert "https://reviewlens-demo-production.up.railway.app" in readme
    assert "REFLECTION.md" in reflection_evidence
    assert "does not author" in reflection_evidence
    assert "ghcr.io/" in verifier
    assert "https://" in verifier
