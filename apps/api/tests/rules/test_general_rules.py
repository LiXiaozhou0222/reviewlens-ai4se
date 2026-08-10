import importlib
from dataclasses import FrozenInstanceError

import pytest

from app.models.domain import FindingSource, Severity
from app.diff_parser.parser import ParsedDiff, ParsedFile, parse_unified_diff
from app.rules import catalog
from app.rules.catalog import GENERAL_RULES, RULESET_VERSION
from app.rules.engine import scan_gen_005
from app.rules.general import scan_gen_001, scan_gen_002, scan_gen_003, scan_gen_004


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


def test_gen_001_ignores_quoted_environment_variable_reference() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/config/settings.sh b/config/settings.sh",
                "index 1234567..89abcde 100644",
                "--- a/config/settings.sh",
                "+++ b/config/settings.sh",
                "@@ -1 +1,2 @@",
                " DEBUG=false",
                '+PASSWORD="$DB_PASSWORD"',
            ]
        )
    )

    assert scan_gen_001(parsed_diff) == ()


def test_gen_002_finds_added_destructive_command() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/scripts/cleanup.sh b/scripts/cleanup.sh",
                "index 1234567..89abcde 100644",
                "--- a/scripts/cleanup.sh",
                "+++ b/scripts/cleanup.sh",
                "@@ -4,2 +4,3 @@",
                " keep_fixture=true",
                "+rm -rf /tmp/reviewlens-fixture",
                " echo done",
            ]
        )
    )

    findings = scan_gen_002(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "GEN-002"
    assert finding.rule_version == RULESET_VERSION
    assert finding.source is FindingSource.GENERAL_RULE
    assert finding.severity is Severity.HIGH
    assert finding.path == "scripts/cleanup.sh"
    assert finding.new_line == 5
    assert finding.raw_excerpt == "rm -rf /tmp/reviewlens-fixture"
    assert finding.message == "A destructive shell or database operation was added."
    assert finding.suggestion == (
        "Confirm the operation is necessary and add appropriate safeguards."
    )


def test_gen_002_finds_added_drop_table_statement() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/db/migration.sql b/db/migration.sql",
                "index 1234567..89abcde 100644",
                "--- a/db/migration.sql",
                "+++ b/db/migration.sql",
                "@@ -1 +1,2 @@",
                " BEGIN;",
                "+DROP TABLE fixture_table;",
            ]
        )
    )

    findings = scan_gen_002(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "GEN-002"
    assert findings[0].path == "db/migration.sql"
    assert findings[0].new_line == 2
    assert findings[0].raw_excerpt == "DROP TABLE fixture_table;"


def test_gen_002_ignores_rm_without_recursive_force_flags() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/scripts/cleanup.sh b/scripts/cleanup.sh",
                "index 1234567..89abcde 100644",
                "--- a/scripts/cleanup.sh",
                "+++ b/scripts/cleanup.sh",
                "@@ -1 +1,2 @@",
                " keep_fixture=true",
                "+rm fixture.txt",
            ]
        )
    )

    assert scan_gen_002(parsed_diff) == ()


def test_gen_002_ignores_plain_quoted_prose_literal() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/app/messages.py b/app/messages.py",
                "index 1234567..89abcde 100644",
                "--- a/app/messages.py",
                "+++ b/app/messages.py",
                "@@ -1 +1,2 @@",
                " MESSAGE = None",
                '+message = "DROP TABLE is dangerous"',
            ]
        )
    )

    assert scan_gen_002(parsed_diff) == ()


@pytest.mark.parametrize(
    "destructive_text",
    [
        "rm -rf; echo ok",
        "mkfs # explanation",
    ],
)
def test_gen_002_ignores_missing_or_delimited_command_target(
    destructive_text: str,
) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/scripts/cleanup.sh b/scripts/cleanup.sh",
                "index 1234567..89abcde 100644",
                "--- a/scripts/cleanup.sh",
                "+++ b/scripts/cleanup.sh",
                "@@ -1 +1,2 @@",
                " keep_fixture=true",
                f"+{destructive_text}",
            ]
        )
    )

    assert scan_gen_002(parsed_diff) == ()


@pytest.mark.parametrize(
    "destructive_text",
    [
        "DROP TABLE;",
        "TRUNCATE DATABASE # note",
    ],
)
def test_gen_002_ignores_targetless_sql_operation(destructive_text: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/db/migration.sql b/db/migration.sql",
                "index 1234567..89abcde 100644",
                "--- a/db/migration.sql",
                "+++ b/db/migration.sql",
                "@@ -1 +1,2 @@",
                " BEGIN;",
                f"+{destructive_text}",
            ]
        )
    )

    assert scan_gen_002(parsed_diff) == ()


def test_gen_003_finds_added_todo_marker() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/widget.ts b/src/widget.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/widget.ts",
                "+++ b/src/widget.ts",
                "@@ -7,2 +7,3 @@",
                " export const widget = true;",
                "+// TODO: replace this fixture",
                " export const enabled = false;",
            ]
        )
    )

    findings = scan_gen_003(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "GEN-003"
    assert finding.rule_version == RULESET_VERSION
    assert finding.source is FindingSource.GENERAL_RULE
    assert finding.severity is Severity.LOW
    assert finding.path == "src/widget.ts"
    assert finding.new_line == 8
    assert finding.raw_excerpt == "// TODO: replace this fixture"
    assert finding.message == "A TODO, FIXME, or HACK marker was added."
    assert finding.suggestion == (
        "Resolve the work item or track it outside the code change."
    )


@pytest.mark.parametrize("marker", ["FIXME", "HACK"])
def test_gen_003_finds_added_fixme_or_hack_marker(marker: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/widget.ts b/src/widget.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/widget.ts",
                "+++ b/src/widget.ts",
                "@@ -1 +1,2 @@",
                " export const widget = true;",
                f"+// {marker} replace this fixture",
            ]
        )
    )

    findings = scan_gen_003(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "GEN-003"
    assert findings[0].raw_excerpt == f"// {marker} replace this fixture"


def test_gen_003_ignores_marker_substring_in_added_identifier() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/widget.ts b/src/widget.ts",
                "index 1234567..89abcde 100644",
                "--- a/src/widget.ts",
                "+++ b/src/widget.ts",
                "@@ -1 +1,2 @@",
                " export const widget = true;",
                "+const hacker = true;",
            ]
        )
    )

    assert scan_gen_003(parsed_diff) == ()


def test_gen_004_finds_added_non_loopback_http_address() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.py b/src/client.py",
                "index 1234567..89abcde 100644",
                "--- a/src/client.py",
                "+++ b/src/client.py",
                "@@ -8,2 +8,3 @@",
                " timeout = 5",
                '+API_URL = "http://example.test/api"',
                " retries = 3",
            ]
        )
    )

    findings = scan_gen_004(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "GEN-004"
    assert finding.rule_version == RULESET_VERSION
    assert finding.source is FindingSource.GENERAL_RULE
    assert finding.severity is Severity.MEDIUM
    assert finding.path == "src/client.py"
    assert finding.new_line == 9
    assert finding.raw_excerpt == 'API_URL = "http://example.test/api"'
    assert finding.message == "A non-loopback plain HTTP address was added."
    assert finding.suggestion == "Use HTTPS unless plain HTTP is explicitly required."


@pytest.mark.parametrize(
    "address",
    [
        "http://localhost/api",
        "http://LOCALHOST/api",
        "http://127.0.0.1/api",
        "http://[::1]/api",
        "http://::1/api",
    ],
)
def test_gen_004_ignores_loopback_http(address: str) -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.py b/src/client.py",
                "index 1234567..89abcde 100644",
                "--- a/src/client.py",
                "+++ b/src/client.py",
                "@@ -1 +1,2 @@",
                " timeout = 5",
                f'+API_URL = "{address}"',
            ]
        )
    )

    assert scan_gen_004(parsed_diff) == ()


def test_gen_004_ignores_added_https_address() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.py b/src/client.py",
                "index 1234567..89abcde 100644",
                "--- a/src/client.py",
                "+++ b/src/client.py",
                "@@ -1 +1,2 @@",
                " timeout = 5",
                '+API_URL = "https://example.test/api"',
            ]
        )
    )

    assert scan_gen_004(parsed_diff) == ()


def test_gen_004_ignores_template_environment_host() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.py b/src/client.py",
                "index 1234567..89abcde 100644",
                "--- a/src/client.py",
                "+++ b/src/client.py",
                "@@ -1 +1,2 @@",
                " timeout = 5",
                '+API_URL = "http://${HOST}/api"',
            ]
        )
    )

    assert scan_gen_004(parsed_diff) == ()


def test_gen_004_finds_localhost_subdomain_http_address() -> None:
    parsed_diff = parse_unified_diff(
        "\n".join(
            [
                "diff --git a/src/client.py b/src/client.py",
                "index 1234567..89abcde 100644",
                "--- a/src/client.py",
                "+++ b/src/client.py",
                "@@ -1 +1,2 @@",
                " timeout = 5",
                '+API_URL = "http://localhost.example.test/api"',
            ]
        )
    )

    findings = scan_gen_004(parsed_diff)

    assert len(findings) == 1
    assert findings[0].rule_id == "GEN-004"
    assert findings[0].raw_excerpt == 'API_URL = "http://localhost.example.test/api"'


def test_gen_005_is_file_level() -> None:
    parsed_diff = ParsedDiff(
        files=(
            ParsedFile(
                new_path="src/large_change.py",
                added_lines=(),
                added_line_count=250,
                deleted_line_count=250,
            ),
            ParsedFile(
                new_path="src/small_change.py",
                added_lines=(),
                added_line_count=499,
                deleted_line_count=0,
            ),
            ParsedFile(
                new_path="assets/large_change.bin",
                added_lines=(),
                is_binary=True,
                added_line_count=500,
                deleted_line_count=0,
            ),
        )
    )

    findings = scan_gen_005(parsed_diff)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "GEN-005"
    assert finding.rule_version == RULESET_VERSION
    assert finding.source is FindingSource.GENERAL_RULE
    assert finding.severity is Severity.MEDIUM
    assert finding.path == "src/large_change.py"
    assert finding.new_line is None
    assert finding.raw_excerpt == ""
    assert finding.message == "A single text file has a large change size."
    assert finding.suggestion == (
        "Consider splitting the change into smaller, reviewable pieces."
    )
