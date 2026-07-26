#!/usr/bin/env python3
"""Answer the questions a directory of ADRs cannot.

README makes a claim: a directory of decision records is a pile, not a graph,
and the difference is five questions a pile cannot answer. Nothing in this
repository answered them, which left the claim resting on the reader's
goodwill. This is the tool that answers them.

    python3 tools/lineage.py                        # all five, over the corpus
    python3 tools/lineage.py --depends-on DL-0004   # one decision's foundations
    python3 tools/lineage.py --stale --as-of 2027-06-01
    python3 tools/lineage.py --inherited            # the acquisition library

Queries, in the order README asks them:

  --depends-on ID   What does this decision silently rest on, transitively?
  --stale           Which accepted decisions are past their review date?
  --evidence ID     Which code resulted from this decision?
  --predictions     Did what we predicted actually happen?
  --controls        Which controls do our decisions implement or weaken?

And one the playbook needs:

  --inherited       What did we absorb, from whom, and how well is it attested?

This reads a corpus and reports. It does not validate — `tools/validate.py`
checks records and graph integrity, and this assumes that has passed. Dangling
references are reported where they affect an answer rather than treated as
errors, because during an incremental import a reference to a record not yet
extracted is the normal case rather than a defect.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guidance only
    sys.exit("PyYAML is required:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent

# `decisions/` only, deliberately. SPEC 2.3 requires ids to be unique within a
# namespace, and `examples/` is a different namespace that happens to use the
# same prefix: both directories contain a DL-0004. Loading them together
# silently resolves one record's `depends_on` to an unrelated record in the
# other, and answers the wrong question convincingly. Pass --path to widen.
DEFAULT_PATHS = ("decisions",)

# SPEC 3.3: producers write one direction, consumers derive the inverse.
INVERSES = {
    "supersedes": "superseded_by",
    "superseded_by": "supersedes",
    "depends_on": "enables",
    "enables": "depends_on",
    "constrains": "constrained_by",
    "constrained_by": "constrains",
    "conflicts_with": "conflicts_with",
}


class Corpus:
    def __init__(self, records: dict[str, dict]):
        self.records = records
        self.relations: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        for identifier, record in records.items():
            for name, targets in (record.get("relations") or {}).items():
                for target in targets or []:
                    self.relations[identifier][name].add(target)
                    inverse = INVERSES.get(name)
                    if inverse:
                        self.relations[target][inverse].add(identifier)

    def related(self, identifier: str, name: str) -> set[str]:
        return self.relations.get(identifier, {}).get(name, set())

    def title(self, identifier: str) -> str:
        record = self.records.get(identifier)
        if record is None:
            return "(not in corpus)"
        return str(record.get("title", ""))

    def known(self, identifier: str) -> bool:
        return identifier in self.records

    def accepted(self) -> list[str]:
        return [i for i, r in self.records.items() if r.get("status") == "accepted"]


def load(paths: list[str]) -> Corpus:
    records: dict[str, dict] = {}
    origins: dict[str, Path] = {}
    collisions: list[tuple[str, Path, Path]] = []
    for entry in paths:
        base = Path(entry)
        if not base.is_absolute():
            base = ROOT / base
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml")))
        else:
            continue
        for file in files:
            try:
                document = yaml.safe_load(file.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if not isinstance(document, dict) or "detected_at" in document:
                continue
            identifier = document.get("id")
            if not identifier:
                continue
            identifier = str(identifier)
            if identifier in records:
                collisions.append((identifier, origins[identifier], file))
                continue
            records[identifier] = document
            origins[identifier] = file

    if collisions:
        print("Two records share an identifier, so this corpus spans more than one namespace.\n")
        for identifier, first, second in collisions:
            print(f"  {identifier}")
            print(f"    kept    {first.relative_to(ROOT) if first.is_relative_to(ROOT) else first}")
            print(f"    ignored {second.relative_to(ROOT) if second.is_relative_to(ROOT) else second}")
        print(
            "\nEvery relation naming a duplicated id resolves to whichever record loaded first,\n"
            "which produces a confident answer to a question nobody asked. Load one namespace\n"
            "at a time, or renumber. Refusing to guess.\n"
        )
        sys.exit(1)

    return Corpus(records)


def as_date(value) -> datetime.date | None:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def transitive(corpus: Corpus, start: str, name: str) -> list[tuple[int, str]]:
    """Breadth-first walk along one relation, returning (depth, id) pairs."""
    seen = {start}
    frontier = [(1, target) for target in sorted(corpus.related(start, name))]
    ordered: list[tuple[int, str]] = []
    while frontier:
        depth, identifier = frontier.pop(0)
        if identifier in seen:
            continue
        seen.add(identifier)
        ordered.append((depth, identifier))
        for target in sorted(corpus.related(identifier, name)):
            frontier.append((depth + 1, target))
    return ordered


def q_depends_on(corpus: Corpus, identifier: str) -> None:
    print(f"What {identifier} rests on")
    print(f"  {identifier}  {corpus.title(identifier)}\n")
    chain = transitive(corpus, identifier, "depends_on")
    if not chain:
        print("  Nothing declared. Either it stands alone, or its dependencies were never written down.")
        return
    for depth, target in chain:
        marker = "" if corpus.known(target) else "   <- not in corpus"
        status = corpus.records.get(target, {}).get("status", "?")
        print(f"  {'  ' * depth}{target}  [{status}]  {corpus.title(target)}{marker}")
    print(
        f"\n  {len(chain)} decision(s) deep. Reversing any of them puts "
        f"{identifier} back in question,\n  which is the part a flat directory hides."
    )


def q_stale(corpus: Corpus, as_of: datetime.date) -> None:
    print(f"Accepted decisions past their review date, as of {as_of.isoformat()}")
    rows = []
    undated = []
    for identifier in sorted(corpus.accepted()):
        review = as_date(corpus.records[identifier].get("review_by"))
        if review is None:
            undated.append(identifier)
        elif review < as_of:
            rows.append((review, identifier, (as_of - review).days))
    if rows:
        for review, identifier, overdue in sorted(rows):
            print(f"  {identifier}  due {review.isoformat()}  {overdue:>5}d overdue  {corpus.title(identifier)}")
    else:
        print("  None.")
    if undated:
        print(f"\n  {len(undated)} accepted decision(s) assert no review date, which claims permanence:")
        for identifier in undated:
            print(f"    {identifier}  {corpus.title(identifier)}")


def q_evidence(corpus: Corpus, identifier: str) -> None:
    record = corpus.records.get(identifier)
    if record is None:
        print(f"{identifier} is not in the corpus.")
        return
    print(f"What resulted from {identifier}")
    print(f"  {corpus.title(identifier)}\n")
    evidence = record.get("evidence") or {}
    if not evidence:
        print("  No evidence recorded. The decision exists; nothing links it to what was built.")
        return
    for kind in ("pull_requests", "commits", "paths", "urls"):
        for item in evidence.get(kind) or []:
            print(f"  {kind[:-1] if kind.endswith('s') else kind:<13} {item}")


def q_predictions(corpus: Corpus) -> None:
    print("Predictions against outcomes")
    held, missed, no_verdict, unchecked = [], [], [], []
    for identifier, record in sorted(corpus.records.items()):
        outcomes = record.get("outcomes") or []
        predicted = bool((record.get("consequences") or {}))
        if not outcomes:
            if predicted:
                unchecked.append(identifier)
            continue
        for outcome in outcomes:
            matched = outcome.get("matched_prediction")
            entry = (identifier, outcome.get("date"), outcome.get("observation", ""))
            if matched is True:
                held.append(entry)
            elif matched is False:
                missed.append(entry)
            else:
                no_verdict.append(entry)
    for label, rows in (
        ("held", held),
        ("did not hold", missed),
        ("were observed without a verdict", no_verdict),
    ):
        print(f"\n  Predictions that {label}: {len(rows)}")
        for identifier, date, observation in rows:
            print(f"    {identifier}  {date}  {' '.join(str(observation).split())[:88]}")
    if no_verdict:
        print(
            "\n  A verdict is optional on purpose. An outcome nobody predicted, or a prediction\n"
            "  nobody has yet been able to check, is more honestly recorded without one than\n"
            "  forced into true or false."
        )
    if unchecked:
        print(
            f"\n  {len(unchecked)} decision(s) predicted consequences and recorded no outcome:"
        )
        for identifier in unchecked:
            print(f"    {identifier}  {corpus.title(identifier)}")
        print(
            "\n  This is the number that matters. A decision log without outcomes cannot tell you\n"
            "  whose reasoning was sound, only what was decided."
        )


def q_controls(corpus: Corpus, framework: str | None) -> None:
    print("Controls touched by decisions" + (f" ({framework})" if framework else ""))
    by_control: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for identifier, record in corpus.records.items():
        for entry in record.get("controls") or []:
            if framework and entry.get("framework") != framework:
                continue
            key = (str(entry.get("framework")), str(entry.get("control")))
            by_control[key].append((identifier, str(entry.get("relationship", "relates_to"))))
    if not by_control:
        print("  None recorded.")
        return
    weakened = []
    for (fw, control), entries in sorted(by_control.items()):
        print(f"\n  {fw} {control}")
        for identifier, relationship in sorted(entries):
            print(f"    {relationship:<12} {identifier}  {corpus.title(identifier)}")
            if relationship == "weakens":
                weakened.append((fw, control, identifier))
    if weakened:
        print(f"\n  {len(weakened)} decision(s) knowingly weaken a control:")
        for fw, control, identifier in weakened:
            print(f"    {fw} {control}  {identifier}")
        print(
            "\n  These are the decisions worth finding later, and the reason `weakens` exists.\n"
            "  A control weakened deliberately and recorded is a position; one weakened and\n"
            "  unrecorded is a finding waiting for an auditor."
        )


def q_inherited(corpus: Corpus) -> None:
    print("Inherited decisions, by source")
    by_source: dict[str, list[str]] = defaultdict(list)
    for identifier, record in corpus.records.items():
        if record.get("origin") == "inherited":
            by_source[str(record.get("origin_source", "(unnamed)"))].append(identifier)
    if not by_source:
        print("  None. Everything in this corpus was decided here.")
        return
    for source, identifiers in sorted(by_source.items()):
        print(f"\n  {source}  ({len(identifiers)} decision(s))")
        counts: dict[str, int] = defaultdict(int)
        for identifier in sorted(identifiers):
            provenance = corpus.records[identifier].get("provenance") or {}
            attestation = provenance.get("attestation")
            if attestation is None:
                attestation = "record_reviewed" if provenance.get("reviewed_by_human") else "none"
            counts[attestation] += 1
            attester = provenance.get("attested_by")
            suffix = f"  <- {attester}" if attester else ""
            print(f"    {identifier}  {attestation:<21} {corpus.title(identifier)}{suffix}")
        if counts.get("none"):
            print(
                f"    {counts['none']} unattested. Nobody has confirmed these, and the people who\n"
                "    could are the ones most likely to have left."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--path", action="append", help="corpus directory; repeatable")
    parser.add_argument("--depends-on", metavar="ID", help="what a decision transitively rests on")
    parser.add_argument("--stale", action="store_true", help="accepted decisions past review_by")
    parser.add_argument("--as-of", help="date for staleness, default today")
    parser.add_argument("--evidence", metavar="ID", help="what resulted from a decision")
    parser.add_argument("--predictions", action="store_true", help="predictions against outcomes")
    parser.add_argument("--controls", nargs="?", const="", metavar="FRAMEWORK", help="controls touched")
    parser.add_argument("--inherited", action="store_true", help="what was absorbed, and how well attested")
    arguments = parser.parse_args()

    corpus = load(arguments.path or list(DEFAULT_PATHS))
    if not corpus.records:
        sys.exit("No decision records found. Use --path to point at a corpus.")

    as_of = as_date(arguments.as_of) or datetime.date.today()
    if arguments.as_of and as_date(arguments.as_of) is None:
        sys.exit(f"--as-of is not an ISO date: {arguments.as_of}")

    selected = any(
        [arguments.depends_on, arguments.stale, arguments.evidence,
         arguments.predictions, arguments.controls is not None, arguments.inherited]
    )

    print(f"{len(corpus.records)} decision record(s)\n")

    if arguments.depends_on:
        q_depends_on(corpus, arguments.depends_on)
    if arguments.evidence:
        q_evidence(corpus, arguments.evidence)
    if arguments.stale or not selected:
        if not selected:
            print("=" * 72)
        q_stale(corpus, as_of)
    if arguments.predictions or not selected:
        if not selected:
            print("\n" + "=" * 72)
        q_predictions(corpus)
    if arguments.controls is not None or not selected:
        if not selected:
            print("\n" + "=" * 72)
        q_controls(corpus, arguments.controls or None)
    if arguments.inherited or not selected:
        if not selected:
            print("\n" + "=" * 72)
        q_inherited(corpus)

    return 0


if __name__ == "__main__":
    sys.exit(main())
