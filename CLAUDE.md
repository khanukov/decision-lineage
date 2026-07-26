# Repository conventions

## Language policy: English only

**Every artifact in this repository is written in English.** No exceptions.

This covers source code, comments and identifiers; documentation, the
specification, decision records and README files; commit messages, branch and
tag names; pull request titles and descriptions; issue text and review comments;
test names and fixture data; file and directory names; configuration, CI
definitions, and error and log messages.

The policy is enforced by `tools/check_language.py`, which runs in CI
(`.github/workflows/language-check.yml`). It rejects text in non-Latin scripts —
Cyrillic, Greek prose, CJK, Hebrew, Arabic and others — and catches homoglyphs, a
character rendering identically to a Latin one, which are a real source of
hard-to-debug failures and a supply-chain risk.

Passing the check is necessary and not sufficient: Latin-script text can still
be non-English. The intent is that any engineer, auditor or contributor anywhere
reads every artifact here without translation.

Rationale is recorded in `decisions/DL-0013`.

### Working in another language

Conversation, meetings and drafts happen in any language. The moment content
enters the repository — as a commit, a pull request, or an issue — it is in
English. Translate before committing, not after.

## Repository structure

```
SPEC.md          The specification
PLAYBOOK.md      The inheritance workflow it was extracted from (non-normative)
INTEGRATIONS.md  How to run this inside tools people already use
schema/          JSON Schemas for both record types
conformance/     Fixtures and manifest for testing any implementation
decisions/       This repository's own decisions, in this repository's format
examples/        Illustrative records; a separate namespace from decisions/
mappings/        Optional signal-to-control-framework mappings
playbook/        The fixed question set and its lock
docs/            Rationale documents
tools/           Validator, conformance runner, ADR importer, corpus checks
```

## Working agreements for automated agents

- Never introduce non-English content, including in temporary or example files.
- Run the gates before committing:
  `validate.py`, `conformance.py`, `playbook_lock.py --check`, `history_check.py`,
  `lineage.py`, `check_language.py`.
- A decision that shapes this repository gets a record in `decisions/`, in this
  repository's own format. Accepted records keep their reasoning: correct an
  error freely, but change a position by writing a new record that supersedes
  the old one.
- Every normative change to `SPEC.md` carries a conformance fixture in the same
  change. Rules stated as *SHOULD* must not get fixtures; put those in
  `validate.py` as warnings.
- This repository is public. Do not commit employer-identifying operational
  detail: internal headcount, named acquisition targets, internal risk or
  security assessments, customer names, or unannounced plans.
