#!/usr/bin/env python3
"""Convert an existing directory of ADRs into decision-lineage records.

This is the zero-commitment entry point to the specification. It reads ADRs a
team already has, in the formats they are already written in, and emits
Decision Records. Nobody has to change how they work to try the model.

Supported inputs:

  * Nygard ADRs, as produced by adr-tools
  * MADR 2.x, with the bulleted status header
  * MADR 3.x and 4.x, with YAML frontmatter
  * log4brains output, which is MADR with extra frontmatter keys

Usage:

    python3 tools/adr_import.py doc/adr --out records/
    python3 tools/adr_import.py doc/adr --report        # what was found, no writes
    python3 tools/adr_import.py doc/adr --id-prefix ADR-

Two guarantees, because they are what make the output usable:

1. **Every emitted record validates.** Where the source cannot support a claim,
   the importer weakens the claim rather than emitting an invalid record. An
   ADR whose status says accepted but whose decision cannot be located is
   emitted as `proposed`, not as an accepted record with an empty decision.

2. **Nothing is presented as authoritative.** Imported records carry
   `provenance.attestation: none`. Per SPEC 3.3 they are candidates until
   someone curates them. The importer has no option to claim otherwise: it
   cannot review a record, and it certainly cannot confirm one with a person
   who took part.

Importing another organisation's ADRs — a company being acquired, a system
being taken over — is the case this was built for. Use `--origin inherited`
with `--origin-source` so that the resulting records stay distinguishable from
decisions your own organisation made:

    python3 tools/adr_import.py ../agency-north/doc/adr \\
        --origin inherited --origin-source agency-north --out records/

`--origin-source` names an organisation or team. It must never name a person;
see SPEC 3.3.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guidance only
    sys.exit("PyYAML is required:  pip install pyyaml")

EXTRACTOR = "adr_import.py/0.1.0"

# Heading aliases across the ADR dialects. Compared case-insensitively after
# stripping punctuation.
SECTION_ALIASES = {
    "context": {
        "context",
        "context and problem statement",
        "problem",
        "problem statement",
        "background",
    },
    "decision": {
        "decision",
        "decision outcome",
        "the decision",
        "resolution",
    },
    "consequences": {"consequences", "results", "outcome"},
    "positive": {"positive consequences", "positive", "pros", "good"},
    "negative": {"negative consequences", "negative", "cons", "bad", "risks"},
    "options": {
        "considered options",
        "options considered",
        "alternatives",
        "alternatives considered",
        "options",
    },
    "status": {"status"},
    "drivers": {"decision drivers", "drivers", "forces"},
    "pros_and_cons": {"pros and cons of the options", "pros and cons"},
}

STATUS_MAP = {
    "accepted": "accepted",
    "approved": "accepted",
    "adopted": "accepted",
    "done": "accepted",
    "proposed": "proposed",
    "draft": "proposed",
    "pending": "proposed",
    "wip": "proposed",
    "under review": "proposed",
    "rejected": "rejected",
    "declined": "rejected",
    "deprecated": "deprecated",
    "obsolete": "deprecated",
    "retired": "deprecated",
    "superseded": "superseded",
    "superceded": "superseded",
}

REFERENCE_PATTERN = re.compile(r"\b(?:ADR[-\s]?|DL[-\s]?)?(\d{1,5})\b")
CHOSEN_PATTERN = re.compile(
    r"chosen option\s*:?\s*[\"'“]?(?P<name>[^\"'”\n,\.]+)", re.IGNORECASE
)
DATE_LINE_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?date\s*:\s*(?P<date>.+?)\s*$", re.IGNORECASE)
BULLET_META_PATTERN = re.compile(
    r"^\s*[-*]\s*(?P<key>status|deciders|decision-makers|date|consulted|informed)\s*:\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)
ISO_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


@dataclass
class ImportedRecord:
    source: Path
    record: dict
    warnings: list[str] = field(default_factory=list)
    found: list[str] = field(default_factory=list)


def normalise_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", text.strip().lower()).strip()


def section_key(heading: str) -> str | None:
    normalised = normalise_heading(heading)
    for key, aliases in SECTION_ALIASES.items():
        if normalised in aliases:
            return key
    return None


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter, body). Frontmatter is empty when absent."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n")
    if parts[0].strip() != "---":
        return {}, text
    for index in range(1, len(parts)):
        if parts[index].strip() in ("---", "..."):
            raw = "\n".join(parts[1:index])
            try:
                loaded = yaml.safe_load(raw) or {}
            except yaml.YAMLError:
                return {}, text
            if not isinstance(loaded, dict):
                return {}, text
            return loaded, "\n".join(parts[index + 1 :])
    return {}, text


def parse_sections(body: str) -> tuple[str, dict[str, str], dict[str, str]]:
    """Return (title, sections keyed by canonical name, raw headings kept verbatim)."""
    title = ""
    sections: dict[str, list[str]] = {}
    raw_sections: dict[str, list[str]] = {}
    current_key: str | None = None
    current_raw: str | None = None

    for line in body.split("\n"):
        heading = re.match(r"^(#{1,6})\s+(?P<text>.+?)\s*#*\s*$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group("text")
            if level == 1 and not title:
                title = text
                current_key = None
                current_raw = None
                continue
            current_key = section_key(text)
            current_raw = text.strip()
            sections.setdefault(current_key, []) if current_key else None
            raw_sections.setdefault(current_raw, [])
            continue
        if current_key:
            sections.setdefault(current_key, []).append(line)
        if current_raw:
            raw_sections.setdefault(current_raw, []).append(line)

    collapsed = {key: "\n".join(lines).strip() for key, lines in sections.items()}
    collapsed_raw = {key: "\n".join(lines).strip() for key, lines in raw_sections.items()}
    return title.strip(), collapsed, collapsed_raw


def clean_title(title: str) -> str:
    """Strip the leading ADR number that adr-tools writes into the heading."""
    return re.sub(r"^\s*\d{1,5}[\.\)]\s*", "", title).strip()


def bullet_items(text: str) -> list[str]:
    """Extract list items, joining wrapped continuation lines.

    ADRs written to a column limit wrap their bullets, and treating only the
    first line as the item silently truncates the reasoning — which is the one
    part of an ADR worth importing.
    """
    items: list[str] = []
    current: list[str] | None = None

    def flush() -> None:
        if not current:
            return
        item = " ".join(part.strip() for part in current).strip()
        item = re.sub(r"^\[(?P<inner>.+?)\]\(.*?\)$", r"\g<inner>", item)
        item = item.strip("\"'`“”")
        if item:
            items.append(item)

    for line in text.split("\n"):
        bullet = re.match(r"^\s*[-*+]\s+(?P<item>.+?)\s*$", line)
        if bullet:
            flush()
            current = [bullet.group("item")]
            continue
        if current is not None:
            if not line.strip() or line.lstrip().startswith("#"):
                flush()
                current = None
            else:
                current.append(line)
    flush()
    return items


def paragraph(text: str) -> str:
    """Collapse a section into a single prose block, dropping bullet markers."""
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line and not line.startswith("#")]
    lines = [re.sub(r"^[-*+]\s+", "", line) for line in lines]
    return " ".join(lines).strip()


def extract_status(frontmatter: dict, sections: dict, body: str) -> tuple[str, list[str], list[str]]:
    """Return (raw status text, superseded_by refs, supersedes refs)."""
    raw = ""
    if "status" in frontmatter and frontmatter["status"]:
        raw = str(frontmatter["status"])
    elif "status" in sections:
        raw = sections["status"]
    else:
        for line in body.split("\n"):
            match = BULLET_META_PATTERN.match(line)
            if match and match.group("key").lower() == "status":
                raw = match.group("value")
                break

    superseded_by: list[str] = []
    supersedes: list[str] = []
    lowered = raw.lower()
    if "supersed" in lowered or "superced" in lowered:
        for line in raw.split("\n"):
            low = line.lower()
            targets = REFERENCE_PATTERN.findall(line)
            if not targets:
                continue
            if "supersedes" in low or "replaces" in low:
                supersedes.extend(targets)
            elif "superseded by" in low or "superceded by" in low or "replaced by" in low:
                superseded_by.extend(targets)
    return raw.strip(), superseded_by, supersedes


def extract_date(frontmatter: dict, body: str) -> str | None:
    for key in ("date", "date_decided", "decided"):
        if frontmatter.get(key):
            value = frontmatter[key]
            if isinstance(value, (datetime.date, datetime.datetime)):
                return value.date().isoformat() if isinstance(value, datetime.datetime) else value.isoformat()
            found = ISO_DATE_PATTERN.search(str(value))
            if found:
                return found.group(1)
    for line in body.split("\n")[:40]:
        match = DATE_LINE_PATTERN.match(line)
        if match:
            found = ISO_DATE_PATTERN.search(match.group("date"))
            if found:
                return found.group(1)
    return None


def extract_deciders(frontmatter: dict, body: str) -> list[str]:
    raw = None
    for key in ("deciders", "decision-makers", "decision_makers"):
        if frontmatter.get(key):
            raw = frontmatter[key]
            break
    if raw is None:
        for line in body.split("\n")[:40]:
            match = BULLET_META_PATTERN.match(line)
            if match and match.group("key").lower() in ("deciders", "decision-makers"):
                raw = match.group("value")
                break
    if raw is None:
        return []
    if isinstance(raw, list):
        values = [str(item).strip() for item in raw]
    else:
        values = [part.strip() for part in re.split(r"[,;]", str(raw))]
    return [value for value in values if value]


def extract_options(sections: dict, raw_sections: dict) -> list[dict]:
    names = bullet_items(sections.get("options", ""))
    if not names:
        return []

    chosen_name = None
    outcome = sections.get("decision", "")
    match = CHOSEN_PATTERN.search(outcome)
    if match:
        chosen_name = match.group("name").strip().strip("\"'`")

    options = []
    for name in names:
        option: dict = {"name": name}
        if chosen_name and name.lower().startswith(chosen_name.lower()[:40]):
            option["chosen"] = True
        else:
            reason = negative_reason_for(name, raw_sections)
            if reason:
                option["rejected_because"] = reason
        options.append(option)

    if chosen_name and not any(o.get("chosen") for o in options):
        options.append({"name": chosen_name, "chosen": True})
    return options


def negative_reason_for(option_name: str, raw_sections: dict) -> str | None:
    """MADR records per-option pros and cons under a heading named for the option."""
    for heading, content in raw_sections.items():
        if normalise_heading(heading) != normalise_heading(option_name):
            continue
        reasons = []
        for item in bullet_items(content):
            low = item.lower()
            if low.startswith("bad,") or low.startswith("bad ") or low.startswith("con"):
                reasons.append(re.sub(r"^(bad,?|cons?:?)\s*", "", item, flags=re.IGNORECASE).strip())
        if reasons:
            return " ".join(reasons)
    return None


def extract_consequences(sections: dict) -> dict:
    positive = bullet_items(sections.get("positive", ""))
    negative = bullet_items(sections.get("negative", ""))

    if not positive and not negative and sections.get("consequences"):
        for item in bullet_items(sections["consequences"]):
            low = item.lower()
            if low.startswith("good"):
                positive.append(re.sub(r"^good,?\s*", "", item, flags=re.IGNORECASE).strip())
            elif low.startswith("bad"):
                negative.append(re.sub(r"^bad,?\s*", "", item, flags=re.IGNORECASE).strip())

    consequences = {}
    if positive:
        consequences["positive"] = positive
    if negative:
        consequences["negative"] = negative
    return consequences


def derive_id(path: Path, prefix: str) -> str:
    match = re.match(r"^(\d{1,5})[-_]", path.stem)
    if match:
        return f"{prefix}{int(match.group(1)):04d}"
    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return f"{prefix}{slug}"


def derive_prefix(origin_source: str) -> str:
    """Turn an origin source into an identifier prefix (SPEC 2.3)."""
    slug = re.sub(r"[^A-Za-z0-9]+", "-", origin_source).strip("-").upper()
    return f"{slug}-" if slug else "DL-"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "record"


def convert(path: Path, prefix: str, origin: str | None, origin_source: str | None) -> ImportedRecord:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = split_frontmatter(text)
    title, sections, raw_sections = parse_sections(body)
    warnings: list[str] = []
    found: list[str] = []

    title = clean_title(title) or clean_title(path.stem.replace("-", " "))
    record: dict = {"id": derive_id(path, prefix), "title": title}

    raw_status, superseded_by, supersedes = extract_status(frontmatter, sections, body)
    status_key = normalise_heading(raw_status.split("\n")[0])[:40] if raw_status else ""
    status = None
    for key, mapped in STATUS_MAP.items():
        if status_key.startswith(key):
            status = mapped
            break
    if status is None:
        status = "proposed"
        if raw_status:
            warnings.append(f"unrecognised status {raw_status.splitlines()[0]!r}, imported as proposed")
        else:
            warnings.append("no status found, imported as proposed")
    else:
        found.append("status")

    decision_text = paragraph(sections.get("decision", ""))
    if decision_text:
        found.append("decision")

    # Guarantee 1: weaken the claim rather than emit an invalid record.
    if status == "accepted" and not decision_text:
        status = "proposed"
        warnings.append("status accepted but no decision text found, imported as proposed")
    if status == "superseded" and not superseded_by:
        status = "deprecated"
        warnings.append(
            "status superseded but no superseding reference found, imported as deprecated "
            "(no longer recommended, replacement unknown)"
        )

    record["status"] = status
    if decision_text:
        record["decision"] = decision_text

    date_decided = extract_date(frontmatter, body)
    if date_decided:
        record["date_decided"] = date_decided
        found.append("date")

    deciders = extract_deciders(frontmatter, body)
    if deciders:
        record["deciders"] = deciders
        found.append("deciders")

    context_text = paragraph(sections.get("context", ""))
    if context_text:
        record["context"] = context_text
        found.append("context")

    options = extract_options(sections, raw_sections)
    if options:
        record["options"] = options
        found.append("options")
        if not any(option.get("rejected_because") for option in options):
            warnings.append("options found but no rejection reasons: weakly-justified on import")

    consequences = extract_consequences(sections)
    if consequences:
        record["consequences"] = consequences
        found.append("consequences")

    relations: dict = {}
    if superseded_by:
        relations["superseded_by"] = [f"{prefix}{int(ref):04d}" for ref in superseded_by]
    if supersedes:
        relations["supersedes"] = [f"{prefix}{int(ref):04d}" for ref in supersedes]
    if relations:
        record["relations"] = relations
        found.append("relations")

    if origin:
        record["origin"] = origin
        if origin_source:
            record["origin_source"] = origin_source

    expected = ["status", "decision", "context", "date", "options", "consequences"]
    confidence = round(len([key for key in found if key in expected]) / len(expected), 2)

    record["provenance"] = {
        "extracted_from": "adr",
        "extracted_at": datetime.date.today().isoformat(),
        "extractor": EXTRACTOR,
        "attestation": "none",
        "confidence": confidence,
    }

    return ImportedRecord(source=path, record=record, warnings=warnings, found=found)


def dump(record: dict) -> str:
    header = (
        "# Imported from an ADR by tools/adr_import.py.\n"
        "# provenance.attestation is none: this is a candidate, not an authoritative\n"
        "# decision (SPEC 3.3). Curate before relying on it.\n"
    )
    return header + yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=88)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", help="directory containing ADR markdown files, or a single file")
    parser.add_argument("--out", help="directory to write records into; omit to print to stdout")
    parser.add_argument(
        "--id-prefix",
        help=(
            "identifier prefix. Defaults to DL- for your own decisions, and to a prefix "
            "derived from --origin-source for inherited ones, so that two acquisitions "
            "each numbering from one do not collide (SPEC 2.3)"
        ),
    )
    parser.add_argument("--report", action="store_true", help="summarise what was extracted, write nothing")
    parser.add_argument(
        "--origin",
        choices=["own", "inherited"],
        help="mark the imported decisions as your organisation's own or as inherited",
    )
    parser.add_argument(
        "--origin-source",
        help="organisation, team or acquired entity the decisions came from. Never a person (SPEC 3.3)",
    )
    arguments = parser.parse_args()

    if arguments.origin == "inherited" and not arguments.origin_source:
        sys.exit(
            "--origin inherited requires --origin-source.\n"
            "An inherited decision with no named source cannot be told apart from an\n"
            "own decision nobody has examined, which is the distinction it exists to draw."
        )
    if arguments.origin_source and not arguments.origin:
        sys.exit("--origin-source requires --origin inherited")

    id_prefix = arguments.id_prefix
    if id_prefix is None:
        if arguments.origin == "inherited":
            # SPEC 2.3: two acquisitions each numbering their ADRs from one will
            # collide under a shared prefix, and the collision surfaces later as a
            # relation quietly resolving to the wrong record.
            id_prefix = derive_prefix(arguments.origin_source)
            print(f"Deriving identifier prefix {id_prefix!r} from --origin-source.", file=sys.stderr)
            print("Pass --id-prefix to override.", file=sys.stderr)
        else:
            id_prefix = "DL-"

    source = Path(arguments.source)
    if source.is_file():
        paths = [source]
    elif source.is_dir():
        paths = sorted(p for p in source.glob("*.md") if not p.name.lower().startswith("readme"))
    else:
        sys.exit(f"not found: {source}")

    if not paths:
        sys.exit(f"no ADR markdown files found in {source}")

    imported = [
        convert(path, id_prefix, arguments.origin, arguments.origin_source) for path in paths
    ]

    if arguments.report:
        print(f"{'source':38}  {'id':12}  {'status':10}  conf  fields")
        for item in imported:
            print(
                f"{item.source.name[:38]:38}  {item.record['id']:12}  "
                f"{item.record['status']:10}  {item.record['provenance']['confidence']:.2f}  "
                f"{','.join(item.found) or '-'}"
            )
            for warning in item.warnings:
                print(f"{'':38}  warn: {warning}")
        low = [i for i in imported if i.record["provenance"]["confidence"] < 0.5]
        print(f"\n{len(imported)} record(s); {len(low)} below 0.5 confidence and worth reading first")
        return 0

    if arguments.out:
        out_dir = Path(arguments.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        for item in imported:
            name = f"{item.record['id']}-{slugify(item.record['title'])}.yaml"
            (out_dir / name).write_text(dump(item.record), encoding="utf-8")
            for warning in item.warnings:
                print(f"warn  {item.source.name}: {warning}", file=sys.stderr)
        print(f"Wrote {len(imported)} record(s) to {out_dir}/")
        print("All records are unreviewed candidates. Curate before relying on them.")
    else:
        for item in imported:
            print("---")
            print(dump(item.record), end="")
            for warning in item.warnings:
                print(f"# warn: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
