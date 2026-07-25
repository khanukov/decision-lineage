# Use structured logging across all services

* Status: accepted
* Deciders: head-of-platform, principal-engineer
* Date: 2026-02-11

## Context and Problem Statement

Log formats diverged across services after two acquisitions. Cross-service
incident investigation requires reading four different formats.

## Considered Options

* JSON logs with a shared field set
* Plain text with a stricter prefix convention
* Per-service format with a translation layer at ingestion

## Decision Outcome

Chosen option: "JSON logs with a shared field set", because it is the only
option that makes cross-service queries work without a translation layer we
would then have to maintain.

### Positive Consequences

* Cross-service incident queries work without preprocessing.
* Field-level redaction becomes possible at the logging library.

### Negative Consequences

* Local development output is less readable without a pretty-printer.
* Every service needs a library upgrade.

## Pros and Cons of the Options

### Plain text with a stricter prefix convention

* Good, because no code changes in most services.
* Bad, because conventions without enforcement drift, which is how we got here.

### Per-service format with a translation layer at ingestion

* Good, because no service changes at all.
* Bad, because the translation layer becomes a permanent tax and a single point
  of failure during incidents.
