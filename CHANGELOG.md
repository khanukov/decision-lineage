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

### Changed
- SPEC.md §6 now defines how conformance is checked and what it does not cover.

### Open
- OSCAL alignment undecided.
- Open questions in SPEC.md §7.
- Conformance suite does not cover §2.5; it needs a two-revision fixture format.
- `CODE_OF_CONDUCT.md` is linked from CONTRIBUTING.md but does not exist.
