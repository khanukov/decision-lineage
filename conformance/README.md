# Conformance suite

A claim that a tool "supports decision-lineage" is worth nothing unless it can
be checked. This suite is how it gets checked.

It is a corpus of fixtures plus a manifest stating, for each one, whether a
conformant implementation must accept or reject it. The runner knows nothing
about any implementation: it invokes a command per fixture and reads the exit
status. Zero means accepted, non-zero means rejected.

## Running it

Against the reference validator in this repository:

```bash
pip install pyyaml jsonschema
python3 tools/conformance.py
```

Against your own implementation:

```bash
python3 tools/conformance.py --command "node dist/validate.js {file}"
python3 tools/conformance.py --command "myimpl check --quiet {file}"
```

The only contract is the exit status. Your implementation may print whatever it
likes.

Useful flags:

```bash
python3 tools/conformance.py --rule 4.3      # only the person-subject rule
python3 tools/conformance.py --case CF-R-008 # one case
python3 tools/conformance.py --verbose       # show output from passing cases too
```

## What conformance means here

Per [SPEC.md](../SPEC.md) §6, an implementation is conformant if it produces
records that validate against the schemas, honours §2.5 and §2.6, and does not
represent persons as signal subjects.

This suite tests **normative rules only** — the MUST and MUST NOT statements.
Rules stated as SHOULD are deliberately absent. An implementation that warns on
a SHOULD, errors on it, or ignores it is equally conformant, so a SHOULD cannot
be a conformance case. `tools/validate.py` emits warnings for several of them;
those warnings are advice, not verdicts, and the runner ignores them.

Two failure directions matter equally:

- A fixture in `invalid/` that your implementation **accepts** means you are
  permissive where the specification is normative. Records you emit may be
  rejected elsewhere.
- A fixture in `valid/` that your implementation **rejects** means you are
  stricter than the specification allows. Records emitted elsewhere will be
  rejected by you. This breaks interoperability just as badly, and is the more
  common mistake.

## The case that matters most

`CF-R-008` and `CF-R-009` assert that the subject of a Signal cannot be a
person, under that name or any synonym for it. This is the constraint that
separates a system which finds risk in assets from a system which scores
employees. An implementation that accepts those fixtures is not conformant no
matter how well it handles everything else, and it should not describe itself as
implementing this specification.

## Publishing a conformance claim

Run the suite and publish the output. It names the spec version, the command
under test, and every rule exercised. That is a checkable claim; "supports
decision-lineage" on a feature page is not.

## Known gaps in the suite

Honest ones, so that a passing run is not read as more than it is.

1. **Coverage is of normative rules, not of the model.** §2.5 (accepted records
   are immutable in their reasoning) is a rule about how a corpus changes over
   time and cannot be tested by validating a single file. It needs a
   two-revision fixture and a diffing runner, which do not exist yet.

2. **The reference validator's record-type discrimination is heuristic**, and
   this suite works around it rather than exposing it. `tools/validate.py`
   decides whether a file is a decision or a signal by looking for
   `detected_at` or a `signal` filename prefix. A Signal that is missing
   `detected_at` and is not named `signal-*` is therefore validated as a
   Decision Record: it is still rejected, but for the wrong reason, and a
   `subject.kind: person` violation in such a file is never reached. Signal
   fixtures here are named `signal-*` so that they route correctly. An explicit
   `record_type` discriminator on the record would remove the heuristic and the
   workaround together.

3. **No round-trip cases.** Nothing yet asserts that a producer and a consumer
   agree on a record after a serialise/parse cycle, which is where formats
   usually diverge in practice.

4. **Fixtures are minimal by design.** Each is thin so that exactly one rule is
   under test. They are not examples of well-written decision records; see
   [`examples/`](../examples/) for those.

5. **Two normative rules are unenforceable by any validator**, and no fixture
   can stand in for them. `origin_source` must name an organisation and never a
   person (§3.3), and a record whose attestation is `none` must not be
   *presented* as authoritative (§3.3). Both are constraints on what a producer
   means and what a consumer displays, not on the bytes in the file. A
   conformant implementation can still violate the intent of the specification
   here, and a passing run does not say otherwise.
