#!/usr/bin/env python3
"""Validate decision-lineage records against the schemas.

Usage:
    python3 tools/validate.py [paths...]

With no arguments, validates everything under examples/ and decisions/.
Exits non-zero on failure so it can be used in CI.
"""
import sys
import json
import pathlib
import datetime

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  pip install pyyaml jsonschema")
try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("jsonschema is required:  pip install pyyaml jsonschema")

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_schema(name):
    with open(ROOT / "schema" / name) as fh:
        return Draft202012Validator(json.load(fh))


DECISION = load_schema("decision-record.schema.json")
SIGNAL = load_schema("signal.schema.json")


def normalise(node):
    """YAML parses unquoted ISO dates into date objects. The spec stores
    them as ISO 8601 strings, so coerce before validating."""
    if isinstance(node, dict):
        return {k: normalise(v) for k, v in node.items()}
    if isinstance(node, list):
        return [normalise(v) for v in node]
    if isinstance(node, (datetime.date, datetime.datetime)):
        return node.isoformat()
    return node


def pick_validator(doc, path):
    """Signals carry detected_at; decisions carry status."""
    if "detected_at" in doc or path.name.startswith("signal"):
        return SIGNAL, "signal"
    return DECISION, "decision"


def extra_checks(doc, kind):
    """Rules the schema cannot express cleanly."""
    warnings = []
    if kind == "decision":
        opts = doc.get("options") or []
        chosen = [o for o in opts if o.get("chosen")]
        if len(chosen) > 1:
            return ["more than one option marked chosen"], warnings
        if opts and not any(o.get("rejected_because") for o in opts):
            warnings.append("weakly-justified: no option records rejected_because")
        if doc.get("status") == "accepted" and "review_by" not in doc:
            warnings.append("no review_by: decision asserted as permanent")
        prov = doc.get("provenance") or {}
        if prov.get("extracted_from", "manual") != "manual":
            if effective_attestation(prov) == "none":
                warnings.append("extracted record with no attestation: candidate only")
            if "attestation" not in prov:
                warnings.append("reviewed_by_human is deprecated: use provenance.attestation")
        if doc.get("origin") == "inherited":
            warnings.append(
                f"inherited from {doc.get('origin_source')!r}: check this names an "
                "organisation and not a person"
            )
    return [], warnings


def effective_attestation(provenance):
    """Resolve attestation, falling back to the deprecated boolean (SPEC 3.3)."""
    if "attestation" in provenance:
        return provenance["attestation"]
    return "record_reviewed" if provenance.get("reviewed_by_human") else "none"


def main(argv):
    targets = []
    if argv:
        targets = [pathlib.Path(a) for a in argv]
    else:
        for d in ("examples", "decisions"):
            targets.extend(sorted((ROOT / d).glob("*.y*ml")))

    failed = 0
    for path in targets:
        with open(path) as fh:
            doc = yaml.safe_load(fh)
        if doc is None:
            print(f"SKIP  {path.name}  (empty)")
            continue
        doc = normalise(doc)
        validator, kind = pick_validator(doc, path)
        errors = [f"{'.'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
                  for e in validator.iter_errors(doc)]
        hard, warnings = extra_checks(doc, kind)
        errors.extend(hard)

        if errors:
            failed += 1
            print(f"FAIL  {path.name}  [{kind}]")
            for e in errors:
                print(f"        {e}")
        else:
            print(f"OK    {path.name}  [{kind}]")
        for w in warnings:
            print(f"  warn  {w}")

    print(f"\n{len(targets) - failed}/{len(targets)} valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
