#!/usr/bin/env python3
"""Enforce the English-only policy for this repository.

The check scans repository content for characters belonging to non-Latin
writing systems. It is a mechanical proxy for "this repository is written in
English": it cannot tell English from French, but it reliably catches text left
in Cyrillic, Greek, CJK, Hebrew, Arabic and similar scripts, and it catches
homoglyph characters that look Latin but are not.

Usage:

    python3 tools/check_language.py                 # all git-tracked files
    python3 tools/check_language.py path/to/file    # explicit paths
    python3 tools/check_language.py --staged        # files staged for commit
    python3 tools/check_language.py --list-ranges   # show what is rejected

Exit status is 0 when clean and 1 when violations are found.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Codepoint ranges that must not appear in repository content. Each entry is
# (first, last, script name, minimum run length).
#
# A minimum run length of 1 means a single character is a violation. Greek uses
# 2 because isolated Greek letters are legitimate mathematical notation
# (lambda, sigma, mu, delta), while two or more in a row indicate Greek prose.
BLOCKED_RANGES: tuple[tuple[int, int, str, int], ...] = (
    (0x0400, 0x04FF, "Cyrillic", 1),
    (0x0500, 0x052F, "Cyrillic Supplement", 1),
    (0x2DE0, 0x2DFF, "Cyrillic Extended-A", 1),
    (0xA640, 0xA69F, "Cyrillic Extended-B", 1),
    (0x1C80, 0x1C8F, "Cyrillic Extended-C", 1),
    (0x0530, 0x058F, "Armenian", 1),
    (0x0590, 0x05FF, "Hebrew", 1),
    (0x0600, 0x06FF, "Arabic", 1),
    (0x0700, 0x074F, "Syriac", 1),
    (0x0750, 0x077F, "Arabic Supplement", 1),
    (0x0900, 0x097F, "Devanagari", 1),
    (0x0980, 0x09FF, "Bengali", 1),
    (0x0E00, 0x0E7F, "Thai", 1),
    (0x10A0, 0x10FF, "Georgian", 1),
    (0x1100, 0x11FF, "Hangul Jamo", 1),
    (0x3040, 0x309F, "Hiragana", 1),
    (0x30A0, 0x30FF, "Katakana", 1),
    (0x3400, 0x4DBF, "CJK Extension A", 1),
    (0x4E00, 0x9FFF, "CJK Unified Ideographs", 1),
    (0xAC00, 0xD7AF, "Hangul Syllables", 1),
    (0xF900, 0xFAFF, "CJK Compatibility Ideographs", 1),
    (0x0370, 0x03FF, "Greek", 2),
    (0x1F00, 0x1FFF, "Greek Extended", 2),
)

# Paths excluded from the scan. Vendored dependencies, lockfiles and binary
# assets are not authored content. Extend via a .languageignore file.
DEFAULT_IGNORED_PREFIXES: tuple[str, ...] = (
    ".git/",
    "node_modules/",
    "vendor/",
    "third_party/",
    "dist/",
    "build/",
)

DEFAULT_IGNORED_SUFFIXES: tuple[str, ...] = (
    ".lock",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".zip",
    ".gz",
    ".tar",
    ".bin",
    ".so",
    ".dylib",
    ".dll",
)

MAX_SNIPPET_LENGTH = 100


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    column: int
    script: str
    text: str
    snippet: str

    def render(self) -> str:
        location = f"{self.path}:{self.line}:{self.column}"
        codepoints = " ".join(f"U+{ord(char):04X}" for char in self.text)
        names = ", ".join(_character_name(char) for char in self.text)
        return (
            f"{location}: {self.script} text {self.text!r} ({codepoints})\n"
            f"    characters: {names}\n"
            f"    context:    {self.snippet}"
        )


def _character_name(char: str) -> str:
    try:
        return unicodedata.name(char)
    except ValueError:
        return f"U+{ord(char):04X}"


def _script_for(codepoint: int) -> tuple[str, int] | None:
    for first, last, script, minimum_run in BLOCKED_RANGES:
        if first <= codepoint <= last:
            return script, minimum_run
    return None


def _load_ignore_patterns(root: Path) -> list[str]:
    ignore_file = root / ".languageignore"
    if not ignore_file.is_file():
        return []
    patterns = []
    for raw_line in ignore_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def _is_ignored(path: str, extra_patterns: list[str]) -> bool:
    if path.startswith(DEFAULT_IGNORED_PREFIXES):
        return True
    if path.endswith(DEFAULT_IGNORED_SUFFIXES):
        return True
    return any(Path(path).match(pattern) for pattern in extra_patterns)


def _git_files(root: Path, staged: bool) -> list[str]:
    if staged:
        command = ["git", "-C", str(root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    else:
        command = ["git", "-C", str(root), "ls-files"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"error: could not list files via git: {error}", file=sys.stderr)
        return []
    return [line for line in result.stdout.splitlines() if line]


def _read_text(path: Path) -> str | None:
    """Return file contents, or None when the file is binary or unreadable."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _scan_line(path: str, line_number: int, line: str) -> list[Violation]:
    violations: list[Violation] = []
    index = 0
    length = len(line)
    while index < length:
        match = _script_for(ord(line[index]))
        if match is None:
            index += 1
            continue
        script, minimum_run = match
        run_end = index
        while run_end < length:
            next_match = _script_for(ord(line[run_end]))
            if next_match is None or next_match[0] != script:
                break
            run_end += 1
        run = line[index:run_end]
        if len(run) >= minimum_run:
            violations.append(
                Violation(
                    path=path,
                    line=line_number,
                    column=index + 1,
                    script=script,
                    text=run,
                    snippet=_snippet(line, index, run_end),
                )
            )
        index = run_end
    return violations


def _snippet(line: str, start: int, end: int) -> str:
    left = max(0, start - 30)
    right = min(len(line), end + 30)
    prefix = "..." if left > 0 else ""
    suffix = "..." if right < len(line) else ""
    return f"{prefix}{line[left:right].strip()}{suffix}"


def check_path(root: Path, relative_path: str) -> list[Violation]:
    violations = _scan_line(relative_path, 0, relative_path)
    violations = [
        Violation(
            path=violation.path,
            line=0,
            column=violation.column,
            script=violation.script,
            text=violation.text,
            snippet="file name",
        )
        for violation in violations
    ]

    content = _read_text(root / relative_path)
    if content is None:
        return violations

    for line_number, line in enumerate(content.splitlines(), start=1):
        violations.extend(_scan_line(relative_path, line_number, line))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="files to check; defaults to all git-tracked files")
    parser.add_argument("--staged", action="store_true", help="check files staged for commit")
    parser.add_argument("--list-ranges", action="store_true", help="print the rejected codepoint ranges and exit")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    arguments = parser.parse_args()

    if arguments.list_ranges:
        for first, last, script, minimum_run in BLOCKED_RANGES:
            qualifier = "" if minimum_run == 1 else f" (runs of {minimum_run}+ only)"
            print(f"U+{first:04X}-U+{last:04X}  {script}{qualifier}")
        return 0

    root = Path(arguments.root).resolve()
    candidates = arguments.paths or _git_files(root, arguments.staged)
    ignore_patterns = _load_ignore_patterns(root)

    violations: list[Violation] = []
    checked = 0
    for candidate in candidates:
        relative_path = candidate
        if Path(candidate).is_absolute():
            try:
                relative_path = str(Path(candidate).resolve().relative_to(root))
            except ValueError:
                relative_path = candidate
        if _is_ignored(relative_path, ignore_patterns):
            continue
        if not (root / relative_path).is_file():
            continue
        checked += 1
        violations.extend(check_path(root, relative_path))

    if not violations:
        print(f"Language check passed: {checked} file(s) contain English-only content.")
        return 0

    print(f"Language check failed: {len(violations)} violation(s) in {checked} file(s) checked.\n")
    for violation in violations:
        print(violation.render())
        print()
    print("This repository is English only. See CLAUDE.md and docs/adr/0001-english-only-repository.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
