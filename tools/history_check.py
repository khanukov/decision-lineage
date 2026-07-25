#!/usr/bin/env python3
"""Report edits to the reasoning of accepted decisions (SPEC 2.5).

Once a record is accepted, its `decision`, `context` and `options` are meant to
stay put. A changed position is a new record that supersedes the old one, not a
quiet rewrite of the old one. Appending `outcomes`, adding `evidence`, fixing a
typo — all expected and all fine.

This rule is what makes a decision archive worth keeping. An archive that is
edited to match current opinion records only current opinion, and the whole
reason to read a two-year-old record is to find out what people believed two
years ago, including where they were wrong.

Nothing else checks it. A validator sees one file at one moment and cannot know
what that file said last year, so this reads git history instead:

    python3 tools/history_check.py                       # decisions/ and examples/
    python3 tools/history_check.py --path records/       # somewhere else
    python3 tools/history_check.py --since 2026-01-01

SPEC 2.5 is a SHOULD NOT, deliberately: a record accepted with a genuine error
in its reasoning is better corrected than preserved. So this reports and does
not fail, unless --strict is given. What it produces is a list for a human to
look at, in which most entries will be fine and one occasionally will not.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guidance only
    sys.exit("PyYAML is required:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
WATCHED_FIELDS = ("decision", "context", "options")
DEFAULT_PATHS = ("decisions", "examples")


@dataclass(frozen=True)
class Edit:
    path: str
    record_id: str
    field: str
    old_commit: str
    new_commit: str
    subject: str
    before: str
    after: str


def git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def revisions(path: str, since: str | None) -> list[tuple[str, str]]:
    """Commits touching a path, oldest first, as (sha, subject)."""
    arguments = ["log", "--reverse", "--format=%H%x00%s"]
    if since:
        arguments.append(f"--since={since}")
    arguments += ["--", path]
    output = git(*arguments)
    entries = []
    for line in output.splitlines():
        if "\0" in line:
            sha, _, subject = line.partition("\0")
            entries.append((sha, subject))
    return entries


def load_at(sha: str, path: str) -> dict | None:
    blob = git("show", f"{sha}:{path}")
    if not blob.strip():
        return None
    try:
        document = yaml.safe_load(blob)
    except yaml.YAMLError:
        return None
    return document if isinstance(document, dict) else None


def render(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    return yaml.safe_dump(value, sort_keys=False, width=10_000).strip()


def truncate(text: str, limit: int = 96) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def tracked_files(paths: list[str]) -> list[str]:
    output = git("ls-files", "--", *paths)
    return [line for line in output.splitlines() if line.endswith((".yaml", ".yml"))]


def inspect(path: str, since: str | None) -> list[Edit]:
    history = revisions(path, since)
    edits: list[Edit] = []
    previous: dict | None = None
    previous_sha = ""

    for sha, subject in history:
        current = load_at(sha, path)
        if current is None:
            previous, previous_sha = None, sha
            continue
        if previous is not None and previous.get("status") == "accepted":
            for field in WATCHED_FIELDS:
                before, after = render(previous.get(field)), render(current.get(field))
                if before != after and before:
                    edits.append(
                        Edit(
                            path=path,
                            record_id=str(current.get("id", "?")),
                            field=field,
                            old_commit=previous_sha[:9],
                            new_commit=sha[:9],
                            subject=subject,
                            before=before,
                            after=after,
                        )
                    )
        previous, previous_sha = current, sha
    return edits


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--path", action="append", help="directory to inspect; repeatable")
    parser.add_argument("--since", help="only consider commits after this date")
    parser.add_argument("--strict", action="store_true", help="exit non-zero when edits are found")
    parser.add_argument("--verbose", action="store_true", help="show the before and after text")
    arguments = parser.parse_args()

    if not git("rev-parse", "--git-dir").strip():
        sys.exit("not a git repository, or git is unavailable")

    paths = arguments.path or list(DEFAULT_PATHS)
    files = tracked_files(paths)
    if not files:
        print(f"No tracked records under {', '.join(paths)}.")
        return 0

    edits = [edit for file in files for edit in inspect(file, arguments.since)]

    if not edits:
        print(f"Checked {len(files)} record(s). No accepted reasoning was edited in place.")
        return 0

    print(f"Checked {len(files)} record(s). {len(edits)} edit(s) to accepted reasoning:\n")
    for edit in edits:
        print(f"  {edit.record_id}  {edit.field}  {edit.old_commit}..{edit.new_commit}  {edit.path}")
        print(f"        in: {truncate(edit.subject, 70)}")
        if arguments.verbose:
            print(f"        was:  {truncate(edit.before, 140)}")
            print(f"        now:  {truncate(edit.after, 140)}")
        print()

    print(
        "SPEC 2.5 is a SHOULD NOT, so none of these is automatically wrong. Correcting an\n"
        "error in an accepted record is expected. Changing a position is not: that is a new\n"
        "record superseding the old one, and the difference is visible only to a reader who\n"
        "knows what changed. Each entry above wants one of those two answers."
    )
    return 1 if arguments.strict else 0


if __name__ == "__main__":
    sys.exit(main())
