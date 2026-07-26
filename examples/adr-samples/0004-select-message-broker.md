---
status: proposed
date: 2026-03-02
decision-makers:
  - head-of-platform
  - staff-engineer
consulted:
  - security
---

# Select the message broker for cross-domain events

## Context and Problem Statement

The tenancy and billing split needs an asynchronous boundary. We have no broker
in production today.

## Considered Options

* Managed queue from the existing cloud provider
* Self-hosted broker on the platform cluster

## Decision Outcome

Chosen option: "Managed queue from the existing cloud provider", because the
platform team is four people and operating a broker is a full-time concern.

### Consequences

* Good, because no new operational surface for a small team.
* Bad, because provider lock-in on the event schema and delivery semantics.
