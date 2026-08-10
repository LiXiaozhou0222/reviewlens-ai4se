from app.diff_parser.parser import AddedLine, parse_unified_diff


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

    assert binary_file.change_type == "binary"
    assert binary_file.new_path == "assets/logo.png"
    assert binary_file.added_lines == ()


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
