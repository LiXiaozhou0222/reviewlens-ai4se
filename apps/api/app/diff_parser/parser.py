from dataclasses import dataclass
import re
from typing import Literal

from app.diff_parser.normalizer import DiffNormalizationError
from app.models.errors import PublicErrorCode


@dataclass(frozen=True)
class AddedLine:
    content: str
    new_line: int


@dataclass(frozen=True)
class HunkLine:
    kind: Literal["context", "added", "deleted"]
    content: str
    old_line: int | None
    new_line: int | None


@dataclass(frozen=True)
class ParsedHunk:
    old_start: int
    new_start: int
    lines: tuple[HunkLine, ...]


@dataclass(frozen=True)
class ParsedFile:
    new_path: str
    added_lines: tuple[AddedLine, ...]
    change_type: Literal["added", "modified", "deleted", "renamed"] = "modified"
    is_binary: bool = False
    old_path: str | None = None
    hunks: tuple[ParsedHunk, ...] = ()
    added_line_count: int = 0
    deleted_line_count: int = 0


@dataclass(frozen=True)
class ParsedDiff:
    files: tuple[ParsedFile, ...]


_HUNK_HEADER = re.compile(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
_GIT_DIFF_HEADER = re.compile(r"diff --git a/\S+ b/\S+$")


def parse_unified_diff(text: str) -> ParsedDiff:
    if not any(_GIT_DIFF_HEADER.fullmatch(line) for line in text.split("\n")):
        raise DiffNormalizationError(PublicErrorCode.INVALID_DIFF_FORMAT)

    files: list[ParsedFile] = []
    new_path: str | None = None
    old_path: str | None = None
    change_type: Literal["added", "modified", "deleted", "renamed"] = "modified"
    is_binary = False
    added_lines: list[AddedLine] = []
    hunks: list[ParsedHunk] = []
    hunk_lines: list[HunkLine] | None = None
    hunk_old_start: int | None = None
    hunk_new_start: int | None = None
    old_line: int | None = None
    new_line: int | None = None

    def finish_hunk() -> None:
        nonlocal hunk_lines, hunk_old_start, hunk_new_start
        if hunk_lines is not None and hunk_old_start is not None and hunk_new_start is not None:
            hunks.append(ParsedHunk(hunk_old_start, hunk_new_start, tuple(hunk_lines)))
        hunk_lines = None
        hunk_old_start = None
        hunk_new_start = None

    def finish_file() -> None:
        if new_path is not None:
            finish_hunk()
            if not (
                hunks
                or change_type in {"renamed", "deleted"}
                or is_binary
            ):
                raise DiffNormalizationError(PublicErrorCode.INVALID_DIFF_FORMAT)
            files.append(
                ParsedFile(
                    new_path,
                    tuple(added_lines),
                    change_type=change_type,
                    is_binary=is_binary,
                    old_path=old_path,
                    hunks=tuple(hunks),
                    added_line_count=sum(
                        hunk_line.kind == "added"
                        for parsed_hunk in hunks
                        for hunk_line in parsed_hunk.lines
                    ),
                    deleted_line_count=sum(
                        hunk_line.kind == "deleted"
                        for parsed_hunk in hunks
                        for hunk_line in parsed_hunk.lines
                    ),
                )
            )

    for line in text.split("\n"):
        if _GIT_DIFF_HEADER.fullmatch(line):
            finish_file()
            paths = line.split()
            old_path = paths[2].removeprefix("a/")
            new_path = paths[3].removeprefix("b/")
            change_type = "modified"
            is_binary = False
            added_lines = []
            hunks = []
            hunk_lines = None
            hunk_old_start = None
            hunk_new_start = None
            old_line = None
            new_line = None
            continue

        if line.startswith("+++ b/") and new_line is None:
            new_path = line[4:].removeprefix("b/")
            continue

        if line.startswith("--- a/") and new_line is None:
            old_path = line[4:].removeprefix("a/")
            continue

        if line == "--- /dev/null" and new_line is None:
            change_type = "added"
            old_path = None
            continue

        if line.startswith("new file mode "):
            change_type = "added"
            old_path = None
            continue

        if line.startswith("deleted file mode "):
            change_type = "deleted"
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
            is_binary = True
            continue

        hunk = _HUNK_HEADER.match(line)
        if hunk:
            finish_hunk()
            hunk_old_start = int(hunk.group(1))
            hunk_new_start = int(hunk.group(2))
            old_line = hunk_old_start
            new_line = hunk_new_start
            hunk_lines = []
            continue

        if hunk_lines is None or old_line is None or new_line is None:
            continue

        if line.startswith("+"):
            added_lines.append(AddedLine(line[1:], new_line))
            hunk_lines.append(HunkLine("added", line[1:], None, new_line))
            new_line += 1
        elif line.startswith("-"):
            hunk_lines.append(HunkLine("deleted", line[1:], old_line, None))
            old_line += 1
        elif line.startswith(" "):
            hunk_lines.append(HunkLine("context", line[1:], old_line, new_line))
            old_line += 1
            new_line += 1

    finish_file()

    return ParsedDiff(tuple(files))
