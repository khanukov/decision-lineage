# Integrations

A format is adopted through tools people already run, not by being read. This
file lists what exists, what it costs to wire up, and — because the distinction
matters — which direction each integration runs in.

## Two directions, and why only one of them is here

**Pull.** This repository reads formats other tools produce. Everything below is
pull, and all of it can be built here without anyone else's agreement.

**Push.** Another tool emits decision-lineage records natively. None of this
exists, and none of it can be built here: it needs a change in someone else's
codebase, which needs their maintainers to want it.

Push is what actually drives adoption. OpenLineage did not spread because people
adopted its specification; it spread because Airflow shipped an OpenLineage
provider and turning it on became a configuration flag. Until an ADR tool emits
this format natively, everything here is a way to try the model, not a way to
live in it. That gap is the honest state of the project and is tracked in
CHANGELOG under Open.

---

## GitHub Actions

The lowest-friction way to run any of this in a repository that already has CI.

**Validate records on every push:**

```yaml
- uses: khanukov/decision-lineage@main
  with:
    mode: validate
    path: "decisions/*.yaml"
```

**Import an existing ADR directory and check the result:**

```yaml
- uses: khanukov/decision-lineage@main
  with:
    mode: import
    path: doc/adr
    out: records
```

Without `out`, import runs in report mode and writes nothing — useful as a
first look at what a repository's ADRs contain.

**Import another organisation's ADRs during an integration:**

```yaml
- uses: khanukov/decision-lineage@main
  with:
    mode: import
    path: acquired/doc/adr
    out: records/agency-north
    origin: inherited
    origin-source: agency-north
```

**Prove an implementation is conformant:**

```yaml
- uses: khanukov/decision-lineage@main
  with:
    mode: conformance
    command: "myimpl check {file}"
```

The conformance runner executes from the action's own directory, so `command`
must name something on `PATH` or use an absolute path.

Pin to a tag rather than `main` once tags exist. `main` is honest about the
current state: there is no release yet.

## pre-commit

No package to install, because this repository is not published to PyPI (see
`decisions/DL-0005`). Use a local hook:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: decision-lineage-validate
        name: validate decision records
        entry: python3 tools/validate.py
        language: system
        files: ^decisions/.*\.ya?ml$
        additional_dependencies: []
```

This assumes the scripts are vendored into your repository. If that is
unappealing, the GitHub Action above needs nothing vendored.

---

## adr-tools

[adr-tools](https://github.com/npryce/adr-tools) writes Nygard-format ADRs into
`doc/adr` and is the lowest-friction way to start keeping ADRs at all.

```bash
python3 tools/adr_import.py doc/adr --report
python3 tools/adr_import.py doc/adr --out records/
```

Status lines including `Superseded by ADR-0005` become
`relations.superseded_by`. A `Superseded` status with no traceable successor
imports as `deprecated` with a warning, because the specification does not allow
a superseded record without the link and inventing one would be worse than
weakening the claim.

## log4brains

[log4brains](https://github.com/thomvaill/log4brains) uses MADR as its default
template and keeps ADRs in markdown in the repository, usually under `docs/adr`.

```bash
python3 tools/adr_import.py docs/adr --out records/
```

MADR 2.x bulleted headers (`* Status: accepted`) and MADR 3.x/4.x YAML
frontmatter are both read. Per-option `Bad, because …` bullets under
`Pros and Cons of the Options` become `rejected_because`, which is the field
that carries most of an ADR's value.

log4brains also writes ADRs describing log4brains itself, and those import like
any other.

## Backstage

The [ADR plugin](https://github.com/backstage/community-plugins/tree/main/workspaces/adr/plugins/adr)
parses MADR 2.x and 3.x by default and surfaces ADRs against catalog entities.

Two integration points exist, in increasing order of value and difficulty:

1. **Pull, today.** Point the importer at the same directories the plugin reads.
   Decision records and the Backstage view coexist; neither knows about the
   other.

2. **Push, requiring Backstage-side work.** The ADR backend exposes an extension
   point for registering a custom parser. A parser that emitted decision-lineage
   records — rather than the plugin's internal shape — would make Backstage the
   first native producer, and would give the catalog entity a decision graph
   rather than a document list. This is the single highest-value integration
   available and it cannot be written in this repository.

## Listing

[adr.github.io/adr-tooling](https://adr.github.io/adr-tooling/) is the canonical
directory of decision-capturing tools, and is where people look before choosing
one. Being absent from it is a distribution problem, not a quality one. Adding
an entry is a pull request to that repository.

---

## What is missing

Ordered by how much adoption each would unlock:

1. **A native producer.** Any ADR tool emitting decision-lineage records
   directly. Backstage's parser extension point is the most tractable target.
2. **A consumer worth pointing at.** Records validate and then sit in a
   directory. Nothing renders the graph, answers "what does this decision depend
   on", or shows what is stale. A reference consumer belongs in a separate
   repository, per `decisions/DL-0001`.
3. **A published package.** `pipx install decision-lineage` would make the tools
   usable without vendoring or a GitHub Action, and would make the pre-commit
   hook a three-line entry. Deferred deliberately; see `decisions/DL-0005`.
4. **A listing on adr.github.io.** Cheap, and the first place anyone looks.
