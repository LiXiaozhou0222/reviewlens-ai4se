import pytest

from app.diff_parser.normalizer import DiffNormalizationError
from app.diff_parser.parser import AddedLine, HunkLine, ParsedHunk, parse_unified_diff
from app.models.errors import PublicErrorCode


def test_rejects_invalid_unified_diff() -> None:
    with pytest.raises(DiffNormalizationError) as error:
        parse_unified_diff("This is plain UTF-8 text, not a Git unified diff.")

    assert error.value.code is PublicErrorCode.INVALID_DIFF_FORMAT


def test_maps_added_line_to_new_file_line_number() -> None:
    parsed = parse_unified_diff(
        """diff --git a/src/example.py b/src/example.py
--- a/src/example.py
+++ b/src/example.py
@@ -10,3 +10,4 @@
 unchanged = True
-obsolete = True
+replacement = True
+++ plus_prefixed = True
 retained = True
"""
    )

    assert parsed.files[0].new_path == "src/example.py"
    assert parsed.files[0].added_lines == (
        AddedLine("replacement = True", 11),
        AddedLine("++ plus_prefixed = True", 12),
    )


def test_renamed_file_has_source_metadata_and_destination_path() -> None:
    parsed = parse_unified_diff(
        """diff --git a/src/old_name.py b/src/new_name.py
similarity index 100%
rename from src/old_name.py
rename to src/new_name.py
"""
    )

    renamed_file = parsed.files[0]

    assert renamed_file.change_type == "renamed"
    assert renamed_file.old_path == "src/old_name.py"
    assert renamed_file.new_path == "src/new_name.py"
    assert renamed_file.added_lines == ()


def test_deleted_file_preserves_source_metadata_without_added_lines() -> None:
    parsed = parse_unified_diff(
        """diff --git a/src/obsolete.py b/src/obsolete.py
deleted file mode 100644
--- a/src/obsolete.py
+++ /dev/null
"""
    )

    deleted_file = parsed.files[0]

    assert deleted_file.change_type == "deleted"
    assert deleted_file.old_path == "src/obsolete.py"
    assert deleted_file.added_lines == ()


def test_binary_file_has_binary_metadata_without_added_lines() -> None:
    parsed = parse_unified_diff(
        """diff --git a/assets/logo.png b/assets/logo.png
index 1111111..2222222 100644
Binary files a/assets/logo.png and b/assets/logo.png differ
"""
    )

    binary_file = parsed.files[0]

    assert binary_file.change_type == "modified"
    assert binary_file.is_binary is True
    assert binary_file.new_path == "assets/logo.png"
    assert binary_file.added_lines == ()


def test_new_binary_file_has_added_status_and_binary_flag() -> None:
    parsed = parse_unified_diff(
        """diff --git a/assets/logo.png b/assets/logo.png
new file mode 100644
index 0000000..2222222
Binary files /dev/null and b/assets/logo.png differ
"""
    )
    parsed_file = parsed.files[0]
    assert parsed_file.change_type == "added"
    assert parsed_file.is_binary is True
    assert parsed_file.old_path is None
    assert parsed_file.new_path == "assets/logo.png"
    assert parsed_file.added_lines == ()


def test_file_header_is_not_an_added_code_line() -> None:
    parsed = parse_unified_diff(
        """diff --git a/src/example.py b/src/example.py
--- a/src/example.py
+++ b/src/example.py
@@ -1 +1,2 @@
 existing = True
+++ content = True
"""
    )

    parsed_file = parsed.files[0]

    assert parsed_file.change_type == "modified"
    assert parsed_file.added_lines == (AddedLine("++ content = True", 2),)


def test_parsed_hunk_retains_context_deleted_added_lines_and_counts() -> None:
    parsed = parse_unified_diff(
        """diff --git a/src/example.py b/src/example.py
--- a/src/example.py
+++ b/src/example.py
@@ -10,2 +10,2 @@
 context = True
-removed = True
+added = True
"""
    )

    parsed_file = parsed.files[0]
    assert parsed_file.hunks == (
        ParsedHunk(
            old_start=10,
            new_start=10,
            lines=(
                HunkLine("context", "context = True", 10, 10),
                HunkLine("deleted", "removed = True", 11, None),
                HunkLine("added", "added = True", None, 11),
            ),
        ),
    )
    assert parsed_file.added_lines == (AddedLine("added = True", 11),)
    assert parsed_file.added_line_count == 1
    assert parsed_file.deleted_line_count == 1
