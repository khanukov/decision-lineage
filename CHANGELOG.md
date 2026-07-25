# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning per [GOVERNANCE.md](GOVERNANCE.md).

## [0.1.0-draft] — unreleased

Initial draft. Nothing here is stable.

### Added
- Decision Record model: lifecycle, `relations` graph, `review_by` expiry, `outcomes`, `provenance`.
- Signal model: reference types, asset-only subjects, `deterministic` flag, `disposition`.
- Control mapping file format and `mappings/iso27001-2022.yaml`.
- JSON Schemas for both record types.
- `tools/validate.py` and CI validation of `examples/` and `decisions/`.
- Conformance suite: 23 fixtures under `conformance/`, a manifest binding each to a
  normative rule, and `tools/conformance.py`, which tests any implementation through
  its exit status rather than its internals.
- `tools/adr_import.py`: converts existing Nygard, MADR 2.x and MADR 3.x/4.x ADRs
  into Decision Records. Emitted records always validate and always carry
  `provenance.reviewed_by_human: false`.
- `examples/adr-samples/`: source ADRs in four dialects plus two degenerate cases,
  used as importer fixtures.

- Decision Record: `origin` and `origin_source`, separating an organisation's own
  decisions from decisions inherited through acquisition or handover.
- Decision Record: `provenance.attestation` (`none`, `record_reviewed`,
  `participant_confirmed`) with `attested_by`, distinguishing a record somebody
  read from a record somebody who was present confirmed.
- Signal: `run` and `baseline`, for assessments performed as discrete exercises
  rather than continuous detection.
- `CODE_OF_CONDUCT.md`, adopting Contributor Covenant 2.1 by reference.
- `tools/adr_import.py --origin inherited --origin-source`, for importing the
  ADRs of an organisation being acquired or a system being taken over.
- `action.yml`: a composite GitHub Action covering validation, ADR import and
  conformance, so none of it requires cloning this repository.
- `INTEGRATIONS.md`: wiring for adr-tools, log4brains, Backstage, pre-commit and
  CI, and an explicit account of which direction each integration runs in.
- `PLAYBOOK.md` and `playbook/questions.yaml`: the inheritance workflow the
  specification was extracted from, with a fixed 22-question set. Non-normative.
- `tools/playbook_lock.py`: fails CI when an existing question's wording changes
  or an id disappears, since either silently invalidates comparisons drawn
  across assessments. Appending questions stays free.
- `tools/history_check.py`: reads git history and reports where an accepted
  record's `decision`, `context` or `options` were edited in place (SPEC 2.5).
  Reports rather than fails, because the rule is a SHOULD NOT and correcting a
  genuine error is expected.

### Changed
- SPEC.md §6 now defines how conformance is checked and what it does not cover.
- GOVERNANCE.md: the trigger for broadening governance pointed the wrong way —
  neutrality now precedes adoption instead of waiting for it. Adds a committer
  process, a stated bus factor of one, and a time-bound commitment to seek a
  neutral home.
- SECURITY.md describes what each of the three scripts reads and executes.
- `tools/adr_import.py` emits `provenance.attestation: none` rather than the
  deprecated `reviewed_by_human: false`; the `--emit-attestation` flag is gone,
  since the field is now specified.

### Deprecated
- `provenance.reviewed_by_human`. Still accepted, and still required when
  `attestation` is absent and the record was extracted. Removal awaits a major
  version. Equivalence: `false` means `none`, `true` means `record_reviewed`.

### Fixed
- INTEGRATIONS.md claimed the Backstage ADR plugin's custom-parser extension
  point was a route to a native producer of this format. It is not:
  `AdrInfoParser` returns `title`, `status` and `date` only, and is an input
  parser, so it can make Backstage a consumer and never a producer. The section
  now carries the real API, what a module built on it does and does not
  preserve, and where it should live. Recorded in `decisions/DL-0007`.

### Open
- OSCAL alignment undecided.
- Open questions in SPEC.md §7.
- Conformance suite does not cover §2.5; it needs a two-revision fixture format.
- `origin_source` naming an organisation rather than a person is normative but
  unenforceable by schema; only its presence is checkable.
- No *native producer*, and no identified route to one. Nothing outside this
  repository emits decision-lineage records; the importer reads other formats,
  which is the opposite direction and a weaker one. Backstage's extension point
  turned out to be an input parser; adr-tools and log4brains are authoring tools
  whose output format is the thing they exist to define. This is the largest
  remaining gap and it currently has no plan.
- No consumer. Records validate and then sit in a directory; nothing renders the
  lineage graph or answers what is stale.
- Not listed at adr.github.io/adr-tooling, which is where people look first.
- No tagged release, so `uses: khanukov/decision-lineage@main` cannot be pinned.
