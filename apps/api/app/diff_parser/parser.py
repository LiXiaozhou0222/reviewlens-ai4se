from dataclasses import dataclass
import re


@dataclass(frozen=True)
class AddedLine:
    content: str
    new_line: int


@dataclass(frozen=True)
class ParsedFile:
    new_path: str
    added_lines: tuple[AddedLine, ...]
    change_type: str = "modified"
    old_path: str | None = None


@dataclass(frozen=True)
class ParsedDiff:
    files: tuple[ParsedFile, ...]


_HUNK_HEADER = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_unified_diff(text: str) -> ParsedDiff:
    files: list[ParsedFile] = []
    new_path: str | None = None
    old_path: str | None = None
    change_type = "modified"
    added_lines: list[AddedLine] = []
    new_line: int | None = None

    def finish_file() -> None:
        if new_path is not None:
            files.append(
                ParsedFile(
                    new_path,
                    tuple(added_lines),
                    change_type=change_type,
                    old_path=old_path,
                )
            )

    for line in text.splitlines():
        if line.startswith("diff --git "):
            finish_file()
            paths = line.split()
            old_path = paths[2].removeprefix("a/")
            new_path = paths[3].removeprefix("b/")
            change_type = "modified"
            added_lines = []
            new_line = None
            continue

        if line.startswith("+++ b/") and new_line is None:
            new_path = line[4:].removeprefix("b/")
            continue

        if line.startswith("--- a/") and new_line is None:
            old_path = line[4:].removeprefix("a/")
            continue

        if line == "+++ /dev/null" and new_line is None:
            change_type = "deleted"
            continue

        if line.startswith("rename from "):
            change_type = "renamed"
            old_path = line.removeprefix("rename from ")
            continue

        if line.startswith("rename to "):
            change_type = "renamed"
            new_path = line.removeprefix("rename to ")
            continue

        if line.startswith("Binary files ") and line.endswith(" differ"):
            change_type = "binary"
            continue

        hunk = _HUNK_HEADER.match(line)
        if hunk:
            new_line = int(hunk.group(1))
            continue

        if new_line is None:
            continue

        if line.startswith("+"):
            added_lines.append(AddedLine(line[1:], new_line))
            new_line += 1
        elif line.startswith(" "):
            new_line += 1

    finish_file()

    return ParsedDiff(tuple(files))
