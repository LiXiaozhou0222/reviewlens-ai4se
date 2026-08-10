from app.diff_parser.parser import parse_unified_diff


def test_maps_added_line_to_new_file_line_number() -> None:
    parsed = parse_unified_diff(
        """\\
diff --git a/src/example.py b/src/example.py
--- a/src/example.py
+++ b/src/example.py
@@ -10,3 +10,3 @@
 unchanged = True
-obsolete = True
+replacement = True
 retained = True
"""
    )

    assert parsed.files[0].new_path == "src/example.py"
    assert parsed.files[0].added_lines[0].content == "replacement = True"
    assert parsed.files[0].added_lines[0].new_line == 11
