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

### Open
- OSCAL alignment undecided.
- Open questions in SPEC.md §7.
- Conformance suite does not cover §2.5; it needs a two-revision fixture format.
- `origin_source` naming an organisation rather than a person is normative but
  unenforceable by schema; only its presence is checkable.
- No integration yet with the ADR tooling teams already run (adr-tools,
  log4brains, the Backstage ADR plugin). Adoption arrives through tools people
  already use, so this is the largest remaining gap.
