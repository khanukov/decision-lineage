# decision-lineage

An open specification for engineering decision lineage — linking architectural decisions to the code, controls, and outcomes that follow from them.

**Status: `v0.1.0-draft`.** Unstable. Breaking changes are expected. Nothing here is a standard yet; it is a proposal looking for critique.

---

## The problem

Engineering organisations do not lose decisions because nobody writes them down. They lose them because writing them down is work done by the person who already knows the answer, for the benefit of someone who does not exist yet.

The research on this is unambiguous and old. Zhao et al. (*A Novel Approach for Automated Design Information Mining from Issue Logs*, ASE 2024, [arXiv:2405.19623](https://arxiv.org/abs/2405.19623)) report that roughly 74% of engineers cannot recall the reasoning behind their own past decisions, and around 80% cannot reconstruct the reasoning behind decisions made by others. Thirty years of design-rationale tooling — IBIS, QOC, DRed, IDEF6 — failed for the same structural reason: capture cost falls upstream, benefit falls downstream.

Architecture Decision Records (ADRs) are the one format that partially survived, because they are cheap and live next to the code. But a directory of ADRs is a pile, not a graph. It cannot answer:

- Which decisions does this one silently depend on?
- Is this decision still true, or did we quietly stop honouring it two years ago?
- Which code actually resulted from this decision?
- Did the thing we predicted would happen, happen?
- Which of our security controls does this decision implement or weaken?

`decision-lineage` is an attempt to specify the smallest data model that can answer those questions, and to make it machine-readable so that records can be **extracted** rather than authored.

## What this is

A specification with three parts:

1. **Decision Record** — a decision, its context, the alternatives rejected, its scope, its expiry, and its relations to other decisions. A superset of ADR, deliberately convertible from it.
2. **Signal** — a machine-detected observation about a system (a bypassed review, an architectural violation, a knowledge concentration risk) that can be linked to decisions and to controls.
3. **Mappings** — optional, versioned files translating signal types into control frameworks. `mappings/iso27001-2022.yaml` is the first.

Plus JSON Schemas, examples, a validator, an importer for existing ADRs, and a conformance suite.

## Try it on ADRs you already have

The claim above — that decisions can be extracted rather than authored — should cost you one command to check, not a change of practice:

```bash
pip install pyyaml jsonschema
python3 tools/adr_import.py path/to/your/doc/adr --report
```

That reads Nygard, MADR 2.x and MADR 3.x/4.x ADRs as they are, and prints what it could extract from each and how confident it is. Add `--out records/` to write Decision Records.

Imported records always validate, and always carry `provenance.reviewed_by_human: false`. They are candidates, not decisions, until someone curates them — see [SPEC.md](SPEC.md) §3.3. Where a source cannot support a claim the importer weakens the claim rather than emitting an invalid record: an ADR marked accepted whose decision text cannot be located is imported as `proposed`, and one marked superseded with no traceable successor is imported as `deprecated`, both with a warning.

## Checking an implementation

```bash
python3 tools/conformance.py                                  # the reference validator
python3 tools/conformance.py --command "myimpl check {file}"  # yours
```

The runner reads only the exit status, so an implementation in any language is testable without modification. See [`conformance/`](conformance/) for what is covered and what is not.

## Running it where you already work

All three commands are also a GitHub Action, so trying this costs four lines in a workflow rather than a clone:

```yaml
- uses: khanukov/decision-lineage@main
  with:
    mode: import
    path: doc/adr
```

[INTEGRATIONS.md](INTEGRATIONS.md) covers adr-tools, log4brains, Backstage, pre-commit and CI — and is explicit about the direction each integration runs in. Everything that exists today reads formats other tools produce. No tool yet *emits* this format natively, which is the thing that would actually drive adoption, and it needs work in someone else's codebase rather than this one.

## What this is not

Being explicit, because the surrounding space is full of overclaiming:

- **Not a product.** The code here is a validator, an ADR importer, and a conformance runner — tooling that exists to make the format checkable and enterable. Nothing here stores records, serves them, queries them, or shows them to anyone. A system that does those things is an implementation, and belongs in its own repository.
- **Not a productivity measurement system.** The schema is deliberately built so that the subject of a signal is an asset — a repository, a service, a module — and not a person. See [Privacy stance](#privacy-stance).
- **Not a compliance product.** The ISO mapping is a starting point for discussion with an auditor, not a Statement of Applicability. See the disclaimer in the mapping file.
- **Not an "AI CTO."** Nothing here makes decisions or evaluates whether a decision was correct. It records decisions, tracks whether they are still honoured, and links them to consequences. Judging strategy remains a human problem.
- **Not stable.** v0.1.0-draft means v0.1.0-draft.

## The workflow this came out of

[PLAYBOOK.md](PLAYBOOK.md) describes taking over an engineering system you did not build — through acquisition, handover, or a team that left — and what to do in the first month. It is non-normative: the specification says what a record means, the playbook is one workflow that produces them.

It is here because several fields are hard to justify in the abstract and obvious in context. `origin`, `attestation`, `run` and `baseline` read as overhead until you are looking at an inherited codebase trying to work out which of its choices anyone made on purpose.

[`playbook/questions.yaml`](playbook/questions.yaml) is a fixed, numbered set of 22 questions, and fixed is the entire point: assessments that asked the same questions compare with each other, assessments that asked whatever seemed relevant at the time do not. `tools/playbook_lock.py` enforces that in CI, because rewording a question invalidates every comparison drawn from it and does so invisibly.

## Why not just use ADRs?

ADRs remain excellent and this specification is designed to be a strict superset — any ADR converts to a Decision Record with empty optional fields. Five additions:

| Addition | Why |
|---|---|
| `relations` | Decisions form a graph: `supersedes`, `depends_on`, `constrains`, `conflicts_with`. A flat directory hides the graph. |
| `review_by` | Decisions expire. An ADR from 2019 asserting "we use REST" is not documentation, it is archaeology. An explicit review date makes staleness detectable rather than assumed. |
| `outcomes` | The consequences an ADR predicts are almost never checked against what happened. Without this, there is no feedback loop and no way to learn which reasoning was sound. |
| `provenance` | If records are auto-extracted from pull requests, issue logs, or meeting transcripts, then the provenance of the record itself is first-class information. A record extracted by a language model and never reviewed by a human is not equivalent to one ratified in a review. Mixing the two silently is how a decision log becomes untrustworthy. |
| `controls` | An architectural decision is frequently also a control decision. Recording that link once removes a large amount of duplicated compliance work later. |

## Core model

```
Decision ──supersedes──▶ Decision
    │
    ├──scope──▶ Asset (service, repository, team)
    ├──evidence──▶ Code (pull request, commit, path)
    ├──controls──▶ Control (framework, id)
    └──outcomes──▶ Observation (date, what actually happened)

Signal ──subject──▶ Asset
    ├──relates_to──▶ Decision
    └──controls──▶ Control
```

Two entities, four link types, one optional mapping layer. Deliberately small.

## Example

```yaml
id: DL-0004
title: PostgreSQL as the store for the landlord data service
status: accepted
date_decided: 2026-03-11
review_by: 2027-03-11
deciders: [head-of-platform, cto]

scope:
  services: [landlord-data-service]
  repositories: [platform/landlord-data]

context: >
  Portfolio-level preference scoping requires transactional
  consistency across preference and property-link writes.

options:
  - name: PostgreSQL
    chosen: true
  - name: DynamoDB
    rejected_because: >
      No multi-item transactional guarantee at the access
      pattern we need; XOR constraint on property_links
      would move into application code.

consequences:
  negative:
    - Vertical scaling ceiling accepted for now.

relations:
  depends_on: [DL-0002]
  constrains: [DL-0009]

evidence:
  pull_requests: ["platform/landlord-data#231"]

controls:
  - framework: iso27001:2022
    control: A.8.27

provenance:
  extracted_from: pull_request
  reviewed_by_human: true
```

See [`examples/`](examples/) for complete records and [`SPEC.md`](SPEC.md) for field definitions.

## Privacy stance

This matters more than it usually does for a data format, because the same data that answers "is this decision still honoured" can trivially be turned into per-person surveillance.

The specification takes three positions:

1. **The subject of a Signal is an asset, not a person.** There is no `subject.person` field. This is a deliberate omission, not an oversight.
2. **`deciders` accepts roles as well as identities**, and roles are recommended. `head-of-platform` is more durable and less personal than a name.
3. **Provenance is required where records are extracted from human communication.** If a record came from a meeting transcript, that is recorded, so that retention policies can treat the source and the derived record differently.
4. **`origin_source` names an organisation, never a person.** A decision inherited through an acquisition is attributed to the entity it came from — `agency-north` — because attributing it to individuals turns an integration record into an assessment of the people who were acquired.

There is one place a person may legitimately appear, and the distinction is worth stating because it is easy to read as inconsistency. `deciders` and `provenance.attested_by` may carry an identity; a Signal's `subject` may not. Accountability for a decision someone made, and observation of a person's behaviour, are different activities. The first is what a decision record is for. The second is what this specification refuses to represent. Roles are still recommended in both fields where a role will do.

Implementers operating under GDPR or UK GDPR should read the UK ICO's [guidance on monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/) before connecting any source that touches employee data. A DPIA is likely mandatory. This specification does not constitute legal advice and does not make any processing lawful.

## Compliance mappings

`mappings/iso27001-2022.yaml` maps signal types to Annex A controls of ISO/IEC 27001:2022 — for example, a bypassed pull-request review as evidence relating to A.8.32 (Change management), or a disabled CI security gate to A.8.29.

Read the disclaimer at the top of that file. Annex A is a catalogue from which controls are selected by risk assessment, not a checklist, and a mapping produced by a third party is not a Statement of Applicability. Auditors may reasonably reject any given mapping.

Mappings are separate, versioned files precisely because frameworks are revised and this repository should not be tied to any single edition of any single standard.

## Prior art

This specification would be pointless without the following, and borrows from all of them:

- **[Architecture Decision Records](https://adr.github.io/)** — Michael Nygard's original format, MADR, and the Y-statement. The direct ancestor.
- **[OpenLineage](https://openlineage.io/)** — the model for how an open specification, rather than a product, becomes a de-facto standard in an adjacent problem space.
- **[Backstage](https://backstage.io/)** — established that a service catalogue with real ownership data is worth maintaining.
- **[CodeScene](https://codescene.com/)** — behavioural code analysis; the source of the insight that git history alone reveals knowledge concentration.
- **[OSCAL](https://pages.nist.gov/OSCAL/)** — machine-readable control catalogues. Alignment with OSCAL is an open question tracked in the issues.
- **Zhao et al., ASE 2024** — the empirical case that automated extraction, not authoring, is the only viable path.

## Contributing

The most useful contributions right now are not code. They are:

- A decision your organisation made that this model cannot represent.
- A field that is specified here and would never be filled in practice.
- A disagreement with the ISO mapping from anyone who has been through a certification audit.

See [CONTRIBUTING.md](CONTRIBUTING.md). Governance is described in [GOVERNANCE.md](GOVERNANCE.md) and is currently honest about being one person.

## License

Apache License 2.0. See [LICENSE](LICENSE).
