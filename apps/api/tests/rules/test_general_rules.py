import importlib
from dataclasses import FrozenInstanceError

import pytest

from app.models.domain import FindingSource, Severity
from app.diff_parser.parser import parse_unified_diff
from app.rules import catalog
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION
from app.rules.general import scan_gen_001


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


def test_gen_001_finds_only_added_credential() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/config/settings.py b/config/settings.py",
                "index 1234567..89abcde 100644",
                "--- a/config/settings.py",
                "+++ b/config/settings.py",
                "@@ -1,2 +1,3 @@",
                " SETTINGS = {}",
                '+API_KEY = "rl_fake_token_12345678"',
                " DEBUG = False",
            ]
        )
    )

    findings = scan_gen_001(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "GEN-001"
    assert finding.rule_version == RULESET_VERSION
    assert finding.source is FindingSource.GENERAL_RULE
    assert finding.severity is Severity.CRITICAL
    assert finding.path == "config/settings.py"
    assert finding.new_line == 2
    assert finding.raw_excerpt == 'API_KEY = "rl_fake_token_12345678"'
    assert finding.message == "A high-confidence credential was added."
    assert finding.suggestion == "Remove the credential and use a secure secret store."


def test_gen_001_ignores_credential_in_hunk_context_line() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/config/settings.py b/config/settings.py",
                "index 1234567..89abcde 100644",
                "--- a/config/settings.py",
                "+++ b/config/settings.py",
                "@@ -1,2 +1,3 @@",
                ' API_KEY = "rl_fake_token_12345678"',
                "+DEBUG = True",
                " LOG_LEVEL = 'info'",
            ]
        )
    )

    assert scan_gen_001(parsed_diff) == ()


def test_gen_001_ignores_added_environment_variable_reference() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/config/settings.py b/config/settings.py",
                "index 1234567..89abcde 100644",
                "--- a/config/settings.py",
                "+++ b/config/settings.py",
                "@@ -1 +1,2 @@",
                " SETTINGS = {}",
                "+API_KEY = process.env.API_KEY",
            ]
        )
    )

    assert scan_gen_001(parsed_diff) == ()


def test_gen_001_ignores_added_template_expression() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/config/settings.py b/config/settings.py",
                "index 1234567..89abcde 100644",
                "--- a/config/settings.py",
                "+++ b/config/settings.py",
                "@@ -1 +1,2 @@",
                " SETTINGS = {}",
                '+API_KEY = "{{ secrets.API_KEY }}"',
            ]
        )
    )

    assert scan_gen_001(parsed_diff) == ()
