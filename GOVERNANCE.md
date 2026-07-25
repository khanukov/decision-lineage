# Governance

## Current state

One maintainer. Decisions are made by the maintainer after public discussion in issues.

This is stated plainly rather than dressed up as a committee, because a specification governed by one person is a legitimate risk for anyone considering adopting it, and pretending otherwise would be worse than admitting it.

It is worth naming the shape of that risk precisely, since this specification exists partly to make such risks visible. **The bus factor of this project is one.** Every decision is held by a single person, and if that person stops, the project stops. That is exactly the condition a Decision Record is meant to expose in someone else's system, and it would be dishonest to measure it elsewhere and not here.

## What this means in practice

- Every substantive change is discussed in a public issue before merge.
- Rationale for accepted changes is recorded in `decisions/`, using this specification's own format. That archive is the mitigation for the bus factor above: it does not replace a maintainer, but it means a successor inherits the reasoning and not only the artefacts.
- Rejections get a reason, in writing.
- Normative changes carry a conformance fixture in the same pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Becoming a committer

There are none yet. The process is written down anyway, because a project that decides how to admit people only once someone wants in is making that decision under pressure.

A committer may change specification content and is expected to triage issues and review pull requests. Nomination is by an existing committer. A nomination passes if it collects at least three supporting votes and no vetoes within three days; sustaining a veto requires a majority. While there is one maintainer, the maintainer's decision stands in for the vote, and every such appointment is recorded in `decisions/` with its reasoning.

This mirrors the [OpenLineage committer process](https://github.com/OpenLineage/OpenLineage/blob/main/GOVERNANCE.md) deliberately. It is a model that has carried a specification from one company to a foundation, and inventing a different one here would be novelty for its own sake.

A committer who can no longer participate may take emeritus status, and may return later by the same vote.

## Moving to neutral governance

An earlier version of this document said governance would broaden once "more than one organisation" had adopted the specification. That trigger pointed the wrong way, and the correction is recorded here rather than quietly edited in.

**Neutrality has to precede adoption, not follow it.** No vendor builds on a format controlled by one person at another company: the format can be changed under them at any time, and there is no forum in which to object. If neutrality waits for adopters, the adopters do not arrive and the trigger never fires.

The commitment is therefore unconditional rather than contingent:

- **Control of this specification will not be used as commercial leverage.** No feature is gated, no adopter is favoured, and no change is timed to advantage one implementation over another.
- **Any second organisation contributing substantively is offered a committer seat**, rather than being asked to demonstrate adoption first.
- **The project seeks a neutral home** — a foundation of the kind that hosts comparable specifications — rather than waiting to be invited. For reference, OpenLineage entered LF AI & Data as an incubation-stage project in 2021 and graduated in 2023. Incubation is entered early and on purpose, not once a project has already succeeded.
- **If this specification is still governed by one person twelve months after `1.0.0`, this plan has failed**, and that outcome will be written up in `decisions/` as a superseding record rather than left unmentioned.

## Versioning

The specification uses semantic versioning:

- `0.x` — breaking changes permitted with justification.
- `1.0.0` onwards — breaking changes require a major version and a migration note.

The current version is recorded at the top of [SPEC.md](SPEC.md).

A change is breaking when a record that validated before stops validating, or when a record that was rejected before becomes valid. Adding an optional field is not breaking: consumers are required to ignore fields they do not recognise (SPEC §2.6), and that rule exists precisely so the model can grow without a major version each time.

## Conflict resolution

Technical disagreements are worked out between the people involved wherever possible. Where they cannot be, committers decide by simple majority, one vote each. Until there is more than one committer the maintainer decides and records the reasoning, and any adopter who disagrees has the fork right below.

## Trademark and forks

There is no trademark. Fork it. If a fork is better, the correct outcome is that the fork wins.

The fork right is the real check on a single maintainer, and it only works while forking stays cheap. That is why the specification, schemas, fixtures and conformance suite all live in this repository under Apache 2.0, with no dependency on a service any maintainer could withdraw.
