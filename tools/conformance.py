#!/usr/bin/env python3
"""Run the decision-lineage conformance suite against any implementation.

The suite is a corpus of fixtures and a manifest saying, for each one, whether a
conformant implementation must accept or reject it. The runner knows nothing
about how an implementation works: it invokes a command per fixture and reads
the exit status. Zero means accepted, non-zero means rejected.

    python3 tools/conformance.py
    python3 tools/conformance.py --command "node validate.js {file}"
    python3 tools/conformance.py --command "myimpl check --quiet {file}"
    python3 tools/conformance.py --rule 4.3          # only the person-subject rule
    python3 tools/conformance.py --verbose           # show output of failing cases

Exits 0 when every case matches its expectation and 1 otherwise, so it can gate
a release. A third-party implementation claiming conformance should publish the
output of this command.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guidance only
    sys.exit("PyYAML is required:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "conformance" / "manifest.yaml"
DEFAULT_COMMAND = "python3 tools/validate.py {file}"
CASE_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class Result:
    case_id: str
    rule: str
    path: str
    expected: str
    actual: str
    exit_code: int
    output: str

    @property
    def passed(self) -> bool:
        return self.expected == self.actual


def load_manifest(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"manifest not found: {path}")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run_case(case: dict, command: str, manifest_dir: Path) -> Result:
    fixture = (manifest_dir / case["file"]).resolve()
    if not fixture.is_file():
        return Result(
            case_id=case["id"],
            rule=str(case.get("rule", "?")),
            path=case["file"],
            expected=case["expect"],
            actual="missing",
            exit_code=-1,
            output=f"fixture not found: {fixture}",
        )

    rendered = command.format(file=shlex.quote(str(fixture)))
    try:
        completed = subprocess.run(
            rendered,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=CASE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return Result(
            case_id=case["id"],
            rule=str(case.get("rule", "?")),
            path=case["file"],
            expected=case["expect"],
            actual="timeout",
            exit_code=-1,
            output=f"command exceeded {CASE_TIMEOUT_SECONDS}s",
        )

    actual = "accept" if completed.returncode == 0 else "reject"
    return Result(
        case_id=case["id"],
        rule=str(case.get("rule", "?")),
        path=case["file"],
        expected=case["expect"],
        actual=actual,
        exit_code=completed.returncode,
        output=(completed.stdout + completed.stderr).strip(),
    )


def report(results: list[Result], verbose: bool) -> None:
    for result in results:
        mark = "pass" if result.passed else "FAIL"
        print(f"  {mark}  {result.case_id}  [SPEC {result.rule}]  {result.path}")
        if not result.passed:
            print(f"        expected {result.expected}, got {result.actual} (exit {result.exit_code})")
        if result.output and (verbose or not result.passed):
            for line in result.output.splitlines():
                print(f"        | {line}")


def summarise(results: list[Result]) -> int:
    failures = [r for r in results if not r.passed]
    rules = sorted({r.rule for r in results}, key=_rule_sort_key)
    print()
    print(f"Rules exercised: {', '.join('SPEC ' + rule for rule in rules)}")
    print(f"{len(results) - len(failures)}/{len(results)} cases match the manifest")

    if not failures:
        print("\nCONFORMANT against decision-lineage conformance suite.")
        return 0

    print("\nNOT CONFORMANT. Failing cases:")
    for failure in failures:
        print(f"  {failure.case_id}  SPEC {failure.rule}  expected {failure.expected}, got {failure.actual}")
    print(
        "\nA fixture in invalid/ that was accepted means the implementation is "
        "permissive where the specification is normative.\n"
        "A fixture in valid/ that was rejected means it is stricter than the "
        "specification allows, which breaks interoperability just as badly."
    )
    return 1


def _rule_sort_key(rule: str) -> tuple:
    try:
        return tuple(int(part) for part in rule.split("."))
    except ValueError:
        return (99, rule)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--command",
        default=DEFAULT_COMMAND,
        help="command run per fixture; {file} is substituted. Exit 0 means accepted.",
    )
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="path to manifest.yaml")
    parser.add_argument("--rule", help="run only cases for this SPEC rule, e.g. 4.3")
    parser.add_argument("--case", help="run only this case id, e.g. CF-R-008")
    parser.add_argument("--verbose", action="store_true", help="show command output for passing cases too")
    arguments = parser.parse_args()

    if "{file}" not in arguments.command:
        sys.exit("--command must contain the {file} placeholder")

    manifest_path = Path(arguments.manifest).resolve()
    manifest = load_manifest(manifest_path)
    suite = manifest.get("suite", {})
    cases = manifest.get("cases") or []

    if arguments.rule:
        cases = [c for c in cases if str(c.get("rule")) == arguments.rule]
    if arguments.case:
        cases = [c for c in cases if c.get("id") == arguments.case]
    if not cases:
        sys.exit("no cases selected")

    print(f"{suite.get('name', 'conformance suite')}  (spec {suite.get('spec_version', 'unknown')})")
    print(f"implementation under test: {arguments.command}")
    print()

    results = [run_case(case, arguments.command, manifest_path.parent) for case in cases]
    report(results, arguments.verbose)
    return summarise(results)


if __name__ == "__main__":
    sys.exit(main())
