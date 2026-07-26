# decision-lineage specification

**Version:** `0.1.0-draft`
**Status:** Unstable. Field names and semantics may change without a deprecation period until `1.0.0`.

Key words *MUST*, *SHOULD*, *MAY* are used per [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## 1. Scope

This specification defines two record types and one mapping file format:

- **Decision Record** (§3) — a durable statement of an engineering decision.
- **Signal** (§4) — a machine-detected observation about a system.
- **Control mapping** (§5) — a translation from signal types to an external control framework.

It does not define transport, storage, query interfaces, or detection algorithms.

## 2. General rules

**2.1 Serialisation.** Records *MUST* be valid YAML 1.2 or JSON. YAML is recommended for human-authored and human-reviewed records.

**2.2 File layout.** One record per file is recommended, named `<id>-<slug>.yaml`. Layout is not normative; identifiers are.

**2.3 Identifiers.** Every record *MUST* carry an `id` that is unique and stable within its namespace and *MUST NOT* be reused after deletion. The reference convention is `DL-` followed by a zero-padded integer, but any stable string is permitted.

**2.4 Dates.** All dates *MUST* be ISO 8601. Date-only precision is sufficient for decisions; timestamps are required for signals.

**2.5 Immutability of accepted decisions.** Once a Decision Record has `status: accepted`, its `decision`, `context`, and `options` fields *SHOULD NOT* be edited to reflect a change of position. A changed position is a new record that `supersedes` the old one. Editing to correct errors, add `evidence`, or append `outcomes` is expected and permitted.

**2.6 Unknown fields.** Consumers *MUST* ignore unrecognised fields rather than reject the record. This allows organisation-specific extension without forking the schema.

## 3. Decision Record

### 3.1 Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | See §2.3. |
| `title` | string | Imperative or declarative. Should name the decision, not the problem. |
| `status` | enum | `proposed`, `accepted`, `deprecated`, `superseded`, `rejected`. |
| `decision` | string | What was decided. Required once status is `accepted`. |

### 3.2 Lifecycle

```
proposed ──▶ accepted ──▶ deprecated
    │            │
    ▼            ▼
 rejected    superseded
```

`deprecated` means no longer recommended but not replaced. `superseded` requires at least one entry in `relations.superseded_by`. A record *MUST NOT* be `superseded` without that link.

### 3.3 Optional fields

**`date_decided`** (date) — when the decision was ratified, not when the record was written.

**`review_by`** (date) — the date after which this decision *SHOULD* be re-examined. A decision past its `review_by` with `status: accepted` is **stale**, which is a distinct condition from being wrong. Tooling *SHOULD* surface staleness. Omitting `review_by` asserts the decision is expected to be permanent, which is rarely true.

**`deciders`** (array of string) — roles or identities. Roles are recommended (§ README, Privacy stance).

**`scope`** (object) — what the decision governs. Any of `services`, `repositories`, `teams`, `environments`, each an array of strings. An empty or absent `scope` means organisation-wide, which *SHOULD* be rare.

**`context`** (string) — the forces that made this decision necessary. Should describe constraints, not narrate history.

**`options`** (array of object) — alternatives considered. Each entry:

| Field | Type | Notes |
|---|---|---|
| `name` | string | Required. |
| `chosen` | boolean | At most one option per record may be `true`. |
| `rejected_because` | string | *SHOULD* be present on every option where `chosen` is not `true`. An option without it is decoration. |

A record with exactly one option and no `rejected_because` anywhere is a **weakly-justified decision**. Tooling *MAY* flag this. It is not an error — some decisions genuinely have no alternative — but the distinction is worth surfacing.

**`consequences`** (object) — `positive` and `negative`, each an array of string. These are *predictions* at decision time.

**`relations`** (object) — the lineage graph. Each key is an array of record identifiers:

| Relation | Meaning | Inverse |
|---|---|---|
| `supersedes` | Replaces an earlier decision | `superseded_by` |
| `superseded_by` | Replaced by a later decision | `supersedes` |
| `depends_on` | Would not hold if the referenced decision were reversed | `enables` |
| `enables` | Made the referenced decision possible | `depends_on` |
| `constrains` | Limits the option space of the referenced decision | `constrained_by` |
| `constrained_by` | Option space limited by the referenced decision | `constrains` |
| `conflicts_with` | Cannot both be honoured; symmetric | `conflicts_with` |

Producers *SHOULD* write only one direction; consumers *SHOULD* derive the inverse. `conflicts_with` between two `accepted` records is an unresolved contradiction and *SHOULD* be surfaced prominently.

**`evidence`** (object) — artefacts that resulted from the decision. Any of `pull_requests`, `commits`, `paths`, `urls`, each an array of string. This is the link that makes lineage traceable in the direction decision → code.

**`controls`** (array of object) — each entry has `framework` (string, e.g. `iso27001:2022`), `control` (string, e.g. `A.8.27`), and optional `relationship` with values `implements`, `weakens`, or `relates_to`. `weakens` is important and *SHOULD* be used honestly: decisions that trade away a control are exactly the decisions worth finding later.

**`outcomes`** (array of object) — what actually happened. Each entry has `date`, `observation` (string), and optional `matched_prediction` (boolean). This field is appended over time and is the only feedback mechanism in the specification.

**`provenance`** (object) — how the record itself came to exist:

| Field | Type | Notes |
|---|---|---|
| `extracted_from` | enum | `manual`, `adr`, `pull_request`, `issue`, `transcript`, `chat`, `other`. |
| `extracted_at` | date | |
| `extractor` | string | Tool or model identifier, where applicable. |
| `reviewed_by_human` | boolean | *MUST* be present when `extracted_from` is not `manual`. |
| `confidence` | number | 0–1. Only meaningful for automated extraction. |

**A record with `reviewed_by_human: false` *MUST NOT* be presented as an authoritative decision.** Unreviewed extractions are candidates. Conflating the two destroys trust in the whole log, which is the failure mode this specification exists to avoid.

## 4. Signal

A Signal is an observation, not a judgement.

### 4.1 Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique, stable. |
| `type` | string | See §4.2. |
| `detected_at` | timestamp | ISO 8601 with time. |
| `subject` | object | See §4.3. |
| `deterministic` | boolean | See §4.4. |

### 4.2 Signal types

Reference types. The list is open; implementations *MAY* define others.

| Type | Description |
|---|---|
| `review_bypass` | Change merged without required review |
| `history_rewrite` | Force push to a protected ref |
| `gate_disabled` | CI check or security gate removed or skipped |
| `rule_suppressed` | Linter, SAST, or policy exception added |
| `secret_exposed` | Credential detected in source or history |
| `privilege_change` | Elevation of access rights |
| `config_drift` | Deployed configuration diverges from declared state |
| `architecture_violation` | Dependency or layering rule breached |
| `decision_stale` | Accepted decision past `review_by` |
| `decision_undocumented` | Boundary-altering change with no linked decision |
| `decision_contradiction` | Change conflicts with an accepted decision |
| `duplicate_effort` | Two work items or code paths substantially overlap |
| `knowledge_concentration` | Ownership of an asset concentrated below threshold |
| `shadow_dependency` | Undeclared external service or model in use |

### 4.3 Subject

`subject` *MUST* identify a `kind` and a `ref`. Permitted values of `kind` are `repository`, `service`, `module`, `path`, `pipeline`, `resource`, `work_item`, `decision`.

**`kind` *MUST NOT* be a person.** This specification defines no representation for a human subject of a signal. Implementations that add one are outside the specification.

### 4.4 Determinism

`deterministic: true` asserts that the signal was produced by a rule or metric that will yield the same result given the same inputs. `false` indicates statistical or model-based inference.

Consumers using signals as audit evidence *SHOULD* rely only on deterministic signals. A non-deterministic signal is a lead for a human to follow, not a finding.

### 4.5 Optional fields

**`severity`** (enum) — `info`, `low`, `medium`, `high`, `critical`.

**`confidence`** (number, 0–1) — required in practice when `deterministic` is `false`.

**`relates_to`** (array of string) — Decision Record identifiers.

**`controls`** (array of object) — same shape as §3.3.

**`disposition`** (object) — the resolution of the signal, which is what prevents a signal stream from becoming noise:

| Field | Type | Notes |
|---|---|---|
| `state` | enum | `open`, `nonconformity`, `accepted_risk`, `remediated`, `false_positive`. |
| `owner` | string | Role or identity. |
| `due` | date | |
| `note` | string | |

`accepted_risk` *SHOULD* reference a Decision Record in `relates_to`. Accepting a risk is itself a decision, and recording it as one closes the loop.

## 5. Control mapping files

A mapping file translates signal types into an external framework. Required top-level keys:

| Key | Type | Notes |
|---|---|---|
| `framework` | object | `id`, `edition`, `title`. |
| `disclaimer` | string | *MUST* be present. See §5.1. |
| `mappings` | array | Each entry: `signal_type`, `controls` (array), and optional `notes`. |

Each control entry has `id`, `name`, `evidence` (what the signal demonstrates), and `strength` with values `direct`, `partial`, or `indirect`.

### 5.1 Mandatory disclaimer

Mapping files *MUST* state that they are not a Statement of Applicability, not legal or audit advice, and that control selection is the responsibility of the implementing organisation's risk assessment. This is not a formality: presenting a third-party mapping as a compliance position is actively harmful.

## 6. Conformance

An implementation is **conformant** if it produces records that validate against the schemas in `schema/`, honours §2.5 and §2.6, and does not represent persons as signal subjects (§4.3).

There is currently no conformance test suite. This is a known gap.

## 7. Open questions

Tracked in the issue tracker. The significant ones:

1. Should `relations` support weights or confidence, or is the graph strictly boolean?
2. Is `outcomes` sufficient, or does the specification need explicit prediction–verification pairing?
3. Should mapping files align with OSCAL, and if so at which layer?
4. Is `duplicate_effort` a signal about two subjects, and if so is the single-`subject` model wrong?
5. Should `scope` support negative scoping — "all services except these"?
