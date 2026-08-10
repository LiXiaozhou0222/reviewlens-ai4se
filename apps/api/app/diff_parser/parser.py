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


@dataclass(frozen=True)
class ParsedDiff:
    files: tuple[ParsedFile, ...]


_HUNK_HEADER = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_unified_diff(text: str) -> ParsedDiff:
    files: list[ParsedFile] = []
    new_path: str | None = None
    added_lines: list[AddedLine] = []
    new_line: int | None = None

    for line in text.splitlines():
        if line.startswith("diff --git "):
            new_line = None
            continue

        if line.startswith("+++ b/") and new_line is None:
            if new_path is not None:
                files.append(ParsedFile(new_path, tuple(added_lines)))
            new_path = line[4:].removeprefix("b/")
            added_lines = []
            new_line = None
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

    if new_path is not None:
        files.append(ParsedFile(new_path, tuple(added_lines)))

    return ParsedDiff(tuple(files))
