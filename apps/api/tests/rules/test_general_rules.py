import importlib
from dataclasses import FrozenInstanceError

import pytest

from app.models.domain import FindingSource, Severity
from app.rules import catalog
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION


def test_ruleset_catalog_is_fixed() -> None:
    assert RULESET_VERSION == "1.0.0"
    assert isinstance(GENERAL_RULES, tuple)
    assert [rule.rule_id for rule in GENERAL_RULES] == [
        "GEN-001",
        "GEN-002",
        "GEN-003",
        "GEN-004",
        "GEN-005",
    ]

    expected_metadata = {
        "GEN-001": (FindingSource.GENERAL_RULE, Severity.CRITICAL, "added-line"),
        "GEN-002": (FindingSource.GENERAL_RULE, Severity.HIGH, "added-line"),
        "GEN-003": (FindingSource.GENERAL_RULE, Severity.LOW, "added-line"),
        "GEN-004": (FindingSource.GENERAL_RULE, Severity.MEDIUM, "added-line"),
        "GEN-005": (FindingSource.GENERAL_RULE, Severity.MEDIUM, "file-level"),
    }
    assert {
        rule.rule_id: (rule.source, rule.severity, rule.scope)
        for rule in GENERAL_RULES
    } == expected_metadata
    assert all(rule.category == "general" for rule in GENERAL_RULES)
    assert all(rule.name and rule.message and rule.suggestion for rule in GENERAL_RULES)

    with pytest.raises(FrozenInstanceError):
        GENERAL_RULES[0].severity = Severity.LOW


def test_ruleset_catalog_ignores_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REVIEWLENS_RULESET_VERSION", "99.99.99")
    monkeypatch.setenv("REVIEWLENS_RULE_CATALOG", "GEN-999")

    reloaded_catalog = importlib.reload(catalog)

    assert reloaded_catalog.RULESET_VERSION == "1.0.0"
    assert [rule.rule_id for rule in reloaded_catalog.GENERAL_RULES] == [
        "GEN-001",
        "GEN-002",
        "GEN-003",
        "GEN-004",
        "GEN-005",
    ]
