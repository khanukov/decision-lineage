#!/usr/bin/env python3
"""Run the existing importer, validator, and queries on bundled example data.

No credentials, model calls, or production data are needed. Dependencies must
already be installed: pip install pyyaml jsonschema.
"""

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent


def run(title, *arguments):
    print(f"\n--- {title} ---", flush=True)
    subprocess.run([sys.executable, *map(str, arguments)], cwd=ROOT, check=True)


def main():
    print("decision-lineage: from existing ADRs to inspectable decisions", flush=True)
    print("Bundled examples only. Imported records remain unreviewed candidates.", flush=True)
    with tempfile.TemporaryDirectory(prefix="decision-lineage-demo-") as directory:
        destination = Path(directory)
        run("1. Import six sample ADRs", "tools/adr_import.py",
            "examples/adr-samples", "--out", destination)
        run("2. Validate the imported records", "tools/validate.py",
            *sorted(destination.glob("*.yaml")))

    # The maintained decision corpus and the examples are distinct namespaces.
    # Query them separately; combining their repeated ids gives wrong answers.
    run("3. Trace a real project decision", "tools/lineage.py",
        "--depends-on", "DL-0007")
    run("4. Find overdue reviews in the illustrative corpus", "tools/lineage.py",
        "--path", "examples", "--stale", "--as-of", "2027-06-01")
    run("5. Inspect illustrative control relationships", "tools/lineage.py",
        "--path", "examples", "--controls")
    print("\nDemo complete. Temporary imports were removed; repository files were unchanged.",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
