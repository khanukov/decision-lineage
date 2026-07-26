# 2. Use plain text logs with a fixed prefix

Date: 2026-01-20

## Status

Superseded by ADR-0003

## Context

Log volume was small and grep was sufficient.

## Decision

Emit plain text logs prefixed with the service name.

## Consequences

Cheap to implement. Hard to query once volume grows.
