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

### Open
- No conformance test suite.
- OSCAL alignment undecided.
- Open questions in SPEC.md §7.
