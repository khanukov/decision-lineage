# Concept: an engineering decision and control intelligence system

## Version 2 — with an integrated ISO 27001 / ISO 42001 loop

> **Scope note.** This document is the rationale behind the decision-lineage
> specification. It was originally written as an internal design study for a
> multi-entity roll-up operator and has been generalised: company-specific
> figures, targets, and operational detail have been removed. Where the original
> reasoning depended on the roll-up context, that context is described as a
> pattern — an acquiring group that periodically absorbs small engineering teams
> with their own stacks, histories, and security practices.
>
> **On applicability.** The acquisition pattern is the sharpest case, not the
> only one. The condition this document addresses is decision context outrunning
> the people who hold it, and the ordinary cause of that is team fan-out during
> fast growth: one team becomes six, and choices get made in parallel by people
> who cannot all be in the same conversation. An acquisition produces the same
> loss abruptly and at a boundary; growth produces it continuously and
> invisibly. Read the M&A-specific sections as the acute presentation of a
> chronic condition. The parts that do not generalise — Statement of
> Applicability comparison, deal-triggered due diligence — are marked as such.

---

## TL;DR

- **The main change in version 2.** In version 1 the biggest risk to the project
  was not technology but legitimacy. A system that reads git, IAM logs, tickets,
  and transcripts looks like employee surveillance and has no defensible legal
  basis under UK GDPR. ISO 27001 addresses exactly this problem. It converts data
  collection from *worker monitoring* into **continuous production of evidence
  for an ISMS** — with a documented purpose, a bounded scope, defined control
  owners, and an external auditor as the recipient. This changes both the legal
  basis and the internal communication.

- **A side effect, and a serious one.** Roughly 70% of the signals worth
  detecting (code review bypass, force push, disabled CI gates, secrets in code,
  access right changes, configuration drift, shadow IT and shadow AI,
  architectural drift, bus factor) map directly onto specific Annex A controls of
  ISO 27001:2022. A system built for engineering purposes therefore covers a
  significant share of the effort of preparing for certification and for
  surveillance audits.

- **For an acquiring group this is a separate argument.** Every acquisition
  requires extending the ISMS scope (clause 4.3) and assessing gaps against
  Annex A. Today this is done manually and painfully. The system becomes a
  security-side mechanism for M&A integration — something none of the surveyed
  competitors do.

- **The realistic conclusion remains restrained.** ISO does not make the
  unachievable achievable: autonomous assessment of whether a decision was
  *strategically correct* stays out of reach. And ISO 27001 itself turns into
  compliance theatre easily — a separate risk, examined in section 10.

---

## Key findings

1. **The taxonomy of CTO decisions is well studied academically, but
   fragmented.** Formal taxonomies of architectural decisions exist (BTABoK:
   structural, pattern, technology dependency, product/framework, constraint,
   cascade; the taxonomy of Keim, Hey, Sauer and Koziolek, ECSA 2022 / Springer
   2023, reporting F1 up to 92.1% for *detecting that a decision was made* and
   only up to 55.2% for *classifying its type* when processed automatically with
   BERT). Management decisions — hiring, prioritisation, M&A integration — are
   absent from these taxonomies and have to be taken from the engineering
   management literature (Larson; Fournier; Skelton and Pais).

2. **Design rationale capture has failed for thirty years for one reason:
   effort asymmetry.** Zhao et al., "A Novel Approach for Automated Design
   Information Mining from Issue Logs" (DRMiner, ASE 2024, arXiv:2405.19623):
   74% of engineers forget the reasons behind their own decisions and 80% cannot
   reconstruct the reasons behind someone else's, yet capture demands effort
   upstream while the benefit lands downstream — "these systems are not used by
   practising developers". **The only viable path is automatic extraction, not
   manual entry.**

3. **DORA and SPACE are the standard, with well-known criticism attached.**
   McKinsey's August 2023 piece "Yes, you can measure software developer
   productivity" drew a sharp response: Kent Beck — "The report is so absurd and
   naive that it makes no sense to critique it in detail" (Orosz and Beck, The
   Pragmatic Engineer, 29 August 2023); Dan North (4 October 2023) called it a
   "category error". Goodhart's lesson applies: once a metric becomes a target it
   stops being a good metric. **Do not build individual scoring.**

4. **The competitive field splits into five non-overlapping clusters** —
   internal developer platforms and catalogues, software engineering intelligence
   platforms, behavioural code analysis, architectural observability, and AI
   context engines. None of them delivers the whole thing, and none builds the
   loop around an ISMS. A sixth cluster, compliance automation, is added in
   section 8.

5. **The UK ICO's guidance on monitoring workers (3 October 2023) sets hard
   boundaries:** least intrusive means, a mandatory DPIA where processing is
   likely to be high risk, and a lawful basis under Article 6 UK GDPR — consent
   is generally unsuitable in an employment relationship because of the power
   imbalance, which leaves legitimate interests and legal obligation as the
   realistic candidates. Monitoring the content of messages is explicitly called
   high risk and likely to capture special category data.

6. **ISO 27001:2022 is the current edition; there is no "2026 version".**
   93 Annex A controls in four themes: organisational (A.5, 37 controls), people
   (A.6, 8), physical (A.7, 14), technological (A.8, 34). Plus the 2024 climate
   amendment, which auditors now check. The 2013 structure of fourteen domains
   (A.5–A.18) is withdrawn; certificates against it expired after 31 October
   2025. The 2022 edition introduced clause 6.3, "Planning of changes". The key
   nuance: **Annex A is a catalogue, not a checklist.** An organisation does not
   implement all 93 controls but a subset justified by risk assessment and
   recorded in the Statement of Applicability, with exclusions explained.

7. **ISO/IEC 42001:2023 is the first certifiable AI management system standard,
   with 38 Annex A controls.** It is built on the same Harmonised Structure as
   ISO 27001, so clauses 4–10 and the mechanics of the Statement of
   Applicability, internal audit, and management review are shared. Holding
   ISO 27001 reduces the effort for 42001 by roughly a third to a half. Important
   qualification: ISO 42001 **is not a harmonised standard under the EU AI Act**,
   so certification does not by itself confer a presumption of conformity. The
   European work item intended to fill that gap is prEN 18286, still at CEN
   Enquiry stage as of mid-2026.

8. **Successful products avoid capture cost through automated extraction**
   (CodeScene works from git history; Unblocked, Topogy, and Faros build a
   knowledge graph from code, tickets, and chat) and avoid resistance through
   team-level rather than individual metrics. vFunction, tellingly, sells
   self-hosted deployment together with ISO 27001 as a selling point — compliance
   is already being used as product positioning in this niche.

---

## 1. A taxonomy of CTO decisions

The table below merges academic taxonomies with engineering management practice.
**[source]** marks material drawn from published work; **[proposed]** marks a
contribution of this document.

| Decision class | Subtypes | Data required | Horizon | Cost of error | ISMS link |
|---|---|---|---|---|---|
| **Architectural** [source: BTABoK; Keim et al.] | Structural, pattern, technology dependency, product/framework, constraint, cascade | Dependency graph, ADRs, architecturally significant requirements | Years | Very high (irreversibility) | A.8.27 Secure system architecture |
| **Platform / build vs buy** [source: IDP literature] | Internal platform vs SaaS, golden paths | Total cost of ownership, platform team headcount | 1–3 years | High | A.5.19–A.5.22 Supplier relationships |
| **Hiring and team structure** [source: Team Topologies; Fournier] | Topology, tech leads, ownership boundaries | Org structure, Conway's law, load | Quarters | High | A.5.2 Roles, A.6.x People |
| **Resource prioritisation** [source: Larson] | Roadmap, effort allocation | Investment split across feature, debt, keep-the-lights-on | Quarters | Medium | Clause 6.2 Objectives |
| **Technical debt** [source: vFunction; CodeScene] | Refactor vs build new | Hotspots, code health, lead time | Months to years | Medium, compounding | A.8.27, A.8.9 |
| **Security and compliance** [source: ICO; ISO] | Threat model, access, GDPR | IAM logs, SAST/DAST, audit | Continuous | Very high (regulatory) | The core of the whole ISMS |
| **Vendors and contractors** [proposed] | SaaS selection, outsourcing | Contracts, spend, dependency | 1–2 years | Medium | A.5.19–A.5.22, A.8.30 |
| **M&A integration** [proposed] | Stack, CRM migration, unification | Technical due diligence, inventory | Quarters | High | Clause 4.3 Scope |
| **Incidents and reliability** [source: DORA/SPACE] | SLOs, on-call, post-mortems | MTTR, change failure rate | Days to weeks | High | A.5.24–A.5.28 Incidents |

---

## 2. What the system should track

**2.1 Strategy drift.** Comparing declared priorities — OKRs and roadmaps in
Jira, Linear, or Notion — against the actual distribution of engineering time.
Faros AI and Jellyfish do this under the names investment allocation and virtual
time cards. **Feasibility: high.** Constraint: it requires a clean mapping from
code to theme, which is usually manual or produced by LLM classification. ISMS
link: clause 6.2 (ISMS objectives must be measurable), clause 9.1.

**2.2 Rushed or unexamined decisions.** Partially detectable: the absence of an
ADR or RFC alongside a significant change — a new dependency, a new layer, a new
persistence entity. These boundary-altering changes are exactly what ArchSteer
turns into a prefilled draft ADR. Re-deciding is detectable as semantic
similarity between a new decision and an already closed ADR. **Feasibility:
medium**; a human is required to judge whether the reasoning was sound. ISMS
link: clause 6.3 Planning of changes, new in the 2022 edition, which requires
that changes to the ISMS be planned rather than spontaneous.

**2.3 Duplicated work.** Semantic similarity across tickets (a bi-encoder for
scale plus a cross-encoder for precision; BERT fine-tuned on Quora Question Pairs
reaches roughly 86% accuracy), across code (MinHash plus embeddings), and across
overlapping dependencies. **Feasibility: medium to high** for tickets, lower for
code. High false-positive risk — at Squarespace and Klaviyo this problem is
solved by humans in an architecture review forum.

**2.4 Security threats, including organisational degradation.** The technical
side is standard: Dependabot, Snyk, secret scanning, SAST. Organisational
degradation — "we gave everyone admin", "we turned off MFA to move faster" — is
visible through IAM audit logs and diffs of configuration and infrastructure as
code. **Feasibility: high for configuration changes.** ISMS link: A.8.2
Privileged access rights, A.5.15–A.5.18, A.8.8, A.8.12.

**2.5 Control bypass.** Detectable deterministically and reliably: force push
(git events API), merge without review (an off-the-shelf LinearB metric),
disabled CI gates (diffing workflow files), linter suppressions (diffing rule
sets), secrets in code, and "temporary" hacks (TODO, HACK, FIXME without a
ticket). Shadow IT and shadow AI show up through billing and network egress;
Topogy positions itself on "no more shadow AI". **Feasibility: high for git and
CI, medium for shadow AI.** ISMS link: **this is the most direct mapping in the
entire system** — A.8.32 Change management, A.8.29 Security testing in
development and acceptance, A.8.28 Secure coding, A.8.4 Access to source code,
A.5.10 Acceptable use.

**2.6 Architectural drift and erosion.** Fitness functions: ArchUnit (Java),
dependency-cruiser (JS/TS), import-linter (Python), NetArchTest (.NET), Deptrac
(PHP). The open-source "Drift — Architectural Erosion Check" on GitHub
Marketplace catches pattern fragmentation, layer violations, temporal coupling,
and churn hotspots. Commercial: ArchSteer (Drift Index), vFunction (architectural
technical debt, Java and .NET, self-hosted, ISO 27001). **Feasibility: high for
rule violations, medium for emergent erosion.** ISMS link: A.8.27.

**2.7 Knowledge concentration, bus factor, silo risk.** Detected well from git
history. CodeScene reports bus factors as low as two or three developers even in
departments of fifty to sixty people, along with knowledge islands (modules where
95%+ of the code was written by one person) and coordination needs. Calyntro does
the same on aggregated git metadata, self-hosted via Docker, without per-author
pricing. **Feasibility: high. For an acquiring group this is priority one:**
acquired teams are small, and their bus factor is almost always one. ISMS link:
A.5.30 ICT readiness for business continuity, A.6.x.

**2.8 Technical debt and its link to delivery slowdown.** CodeScene positions
Code Health as a code-level metric with a claimed link to business outcomes
(not independently verified); vFunction measures architectural technical debt.
The link to slowdown is a correlation between lead time and hotspot activity.
**Feasibility: medium to high.**

---

## 3. Data sources, prioritised and mapped to Annex A

Criticality: **M** = must have, **N** = nice to have, **R** = probably redundant.

| Source | Signal | Serves | Criticality | Access | Integration | Risk | Annex A controls |
|---|---|---|---|---|---|---|---|
| **Git / GitHub / GitLab** | Commits, PRs, reviews, CODEOWNERS, force push | 2.2, 2.3, 2.5, 2.6, 2.7, 2.8 | **M** | Read-only, metadata plus diffs | REST/GraphQL, webhooks, MCP | Medium (code is IP) | A.8.4, A.8.28, A.8.32, A.8.25 |
| **Trackers (Jira / Linear)** | Epics, tickets, statuses | 2.1, 2.3 | **M** | Read-only | API, webhooks | Low | A.8.32, clause 6.3 |
| **CI/CD (Actions / Argo)** | DORA metrics, gate diffs | 2.5, 2.8 | **M** | Read-only | API, webhooks | Low | A.8.29, A.8.31, A.8.32 |
| **Docs / knowledge base (Notion, Confluence, ADR repo)** | Decisions, RFCs, goals | 2.1, 2.2 | **M** | Read-only | API, MCP | Medium | Clause 7.5 Documented information |
| **IAM / SSO / audit logs** | Rights, MFA, privileges | 2.4, 2.5 | **M** | Audit events | API | Medium | A.5.15–A.5.18, A.8.2 |
| **Security (Snyk, Dependabot, secret scanning)** | Vulnerabilities, secrets | 2.4 | **M** | Metadata | API | Medium | A.8.8, A.8.12 |
| **Cloud / IaC (billing, Terraform state)** | Spend, config drift, shadow IT | 2.4, 2.5 | **N** (becomes **M** under ISO) | Read-only | API | Medium | A.8.9, A.5.23, A.8.19 |
| **Observability / incidents (Datadog, Sentry, PagerDuty)** | Incidents, post-mortems, MTTR | 2.8 | **N** | Metadata | API | Low | A.5.24–A.5.28, A.8.15, A.8.16 |
| **Slack (public channels)** | Decisions made in conversation, workarounds | 2.1, 2.2, 2.5 | **N** | Metadata plus public content | API, MCP | **High** | Clause 7.5 |
| **Email** | — | — | **R** | — | — | **Very high** | — |
| **Call transcripts** | Decisions made verbally | 2.1, 2.2 | **N** | With notice and consent; extracted decisions only | API | **High** | Clause 7.5, A.5.34 |
| **HR / People** | Org structure, roles, departures | 2.7 | **N** | Metadata, aggregated | API | **High** | A.6.1–A.6.5, A.5.34 |
| **Finance / procurement** | Budgets, SaaS spend, vendors | Vendors, shadow IT | **N** | Aggregated | Export | Medium | A.5.19–A.5.22 |
| **CRM / product analytics** | Link between engineering and business | 2.1 | **N** | Aggregated | API | Medium | — |
| **Figma / product specs** | Product artifacts | 2.2 | **R** | Read-only | API | Low | A.8.26 |
| **Technical due diligence on acquisitions** | Stack, debt, process | M&A | **M** for an acquirer | Documents | Parsing plus manual entry | Medium | Clause 4.3, A.5.19–A.5.22 |

**Email: do not connect it.** The ICO treats monitoring of message content as
high risk, likely to capture special category data, requiring an Article 9
condition in addition to an Article 6 basis and a mandatory DPIA. Nearly all of
the signal being sought is duplicated in Slack, tickets, and documents at
incomparably lower risk.

**Call transcripts are the only source of verbally made decisions.** The signal
is unique, but it requires explicit notice and consent, extraction of decisions
only rather than retention of full transcripts, and redaction of personal data.
LLM extraction works — map-reduce over speaker turns — but degrades in the middle
of long transcripts (the lost-in-the-middle effect). Track edit rate, owner
resolution accuracy, and deadline parsability.

---

## 4. Privacy and trust: the line between assisting a CTO and surveilling staff

Requirements from the UK ICO guidance of 3 October 2023:

- **Least intrusive means** capable of achieving the purpose.
- **A DPIA** wherever processing is likely to result in high risk, and the
  guidance treats remote workers as a case deserving particular care, since
  people working from home have a higher expectation of privacy.
- **A lawful basis** under Article 6 UK GDPR. Consent in an employment
  relationship is generally unsuitable because of the power imbalance; the
  realistic candidates are legitimate interests and legal obligation.
- **Constraints on solely automated decisions.** Note that UK law moved here:
  the Data (Use and Access) Act 2025 replaced Article 22 with Articles 22A–22D,
  in force 5 February 2026. The blanket prohibition on solely automated decisions
  with legal or similarly significant effects has become a safeguards regime for
  ordinary personal data — the data subject must be informed, able to make
  representations, able to obtain human intervention, and able to contest the
  decision. Special category data remains restricted. The practical rule for this
  system is unchanged: no automated escalation of an individual to a disciplinary
  process on the basis of an algorithmic score.
- **Function creep is prohibited:** data collected for one purpose may not be
  repurposed for another.

**Design principles [proposed]:**

1. **Team-level metrics by default, never individual.**
2. **Self-hosted** — data does not leave the organisation's infrastructure.
3. **Signals about the system, not about people.** "Module X has a bus factor of
   one" is acceptable. "Engineer X is slow" is not.
4. **Transparency:** staff know what is collected and why, and can see it
   themselves.
5. **A human in the loop** everywhere data influences decisions about people.

---

## 5. ISO 27001 as the load-bearing structure

### 5.1 Why this solves the project's central problem

In version 1 the weakest point was legitimacy. The system reads git, IAM logs,
tickets, configurations, and possibly transcripts. Under UK GDPR that is
processing, including processing of employees' personal data. The first question
from an auditor — or from any unhappy employee — is: **on what basis and for what
purpose?**

The answer "so the CTO can make better decisions" is legally weak and culturally
toxic. It is an unbounded purpose, proportionality cannot be derived from it, and
it reads as supervision.

The answer "for continuous monitoring of the effectiveness of information
security controls within an ISMS certified to ISO 27001" is a different
conversation:

- **The purpose is defined and bounded.** It is set by the ISMS scope and the
  Statement of Applicability. Which data are needed and which are not follows
  automatically, which means the ICO's least-intrusive-means requirement is met
  by construction rather than by assertion.
- **The lawful basis is stronger.** Legitimate interests under Article 6(1)(f)
  is easier to argue in a legitimate interests assessment when the interest is
  conformity with an external standard and contractual obligations to customers
  and investors, rather than an abstract interest in "performance management".
  Part of the processing may also rest on legal obligation.
- **Function creep is blocked structurally.** The Statement of Applicability
  records why each data type is collected. Using that data in a performance
  review is a direct violation of the organisation's own ISMS, and internal audit
  can check it.
- **Internal communication changes completely.** "We are deploying a system that
  tracks who bypasses code review" is a conflict. "We are automating evidence
  collection for controls A.8.32 and A.8.29 so nobody has to assemble it by hand
  before the audit" is relief from routine work. The second framing is true, and
  it is the one to use.
- **The recipient of the signal becomes external rather than internal.**
  Psychologically this matters: the system works for the auditor and the
  certificate, not for the boss.

**The limitation to state up front.** ISO 27001 does not override UK GDPR and
does not issue a licence to monitor. The opposite: A.5.31 requires compliance
with legal and regulatory requirements, and A.5.34 explicitly requires privacy
and protection of PII — including employees' PII. The standard simultaneously
supplies a justification and imposes a boundary. That is convenient, because the
boundary is external and cannot be quietly widened.

**One qualification that is easy to lose.** Certification is not itself a
legitimate interest, and an ISMS does not require any per-developer signal. The
ISO framing therefore covers a *subset* of what an engineering intelligence
system might want to collect. Anything outside that subset needs its own
justification, or should not be collected.

### 5.2 Mapping signals to Annex A controls (ISO 27001:2022)

This is the core of the version 2 logic. Nearly everything worth detecting is
already in the Annex A catalogue: the work is not inventing requirements but
automating evidence for requirements that already exist.

| System signal (section 2) | Annex A controls | What the system gives an auditor |
|---|---|---|
| Merge without review, force push | **A.8.32** Change management | Continuous evidence that changes go through a controlled process, plus a list of exceptions with justifications |
| Disabled CI gates, skipped tests | **A.8.29** Security testing in development and acceptance | A record of gate state over time rather than a screenshot taken on audit day |
| Linter suppressions, SAST suppressions | **A.8.28** Secure coding | A register of suppressions with an owner and an expiry |
| Secrets in code | **A.8.12** Data leakage prevention | Time to detection and time to remediation |
| Repository access rights | **A.8.4** Access to source code | The actual access list rather than the declared one |
| Admin grants, MFA disabled | **A.8.2** Privileged access rights, **A.5.15–A.5.18** | An audit trail of privilege changes |
| Configuration drift, IaC diffs | **A.8.9** Configuration management (new in 2022) | Deviation of actual configuration from the baseline |
| Shadow IT and shadow AI | **A.5.10** Acceptable use, **A.8.19** Installation of software, **A.5.23** Cloud services | An inventory of services actually in use |
| Dependency vulnerabilities | **A.8.8** Management of technical vulnerabilities | Remediation SLAs by severity |
| Graph of services, repositories, owners | **A.5.9** Inventory of assets, **A.5.2** Roles and responsibilities | A live asset register — usually the most painful ISMS artifact |
| Architectural drift | **A.8.27** Secure system architecture and engineering principles | Evidence that principles are not merely written down but observed |
| Bus factor, knowledge islands | **A.5.30** ICT readiness for business continuity | Dependency on key people as a measurable risk |
| Vendors, contractors, SaaS spend | **A.5.19–A.5.22** Supplier relationships, **A.8.30** Outsourced development | A supplier register and actual dependency |
| The system's own event log | **A.8.15** Logging, **A.8.16** Monitoring activities | The monitoring mechanism itself as a control |
| Decision memory | **Clause 7.5** Documented information | Decisions with versioning and a lifecycle |
| Incidents and post-mortems | **A.5.24–A.5.28** Incident management | The link between an incident and the decision that led to it |

An important qualification: **automatically collected evidence is not the same
as evidence an auditor accepts.** Auditors check for the existence of a process,
not only of an artifact. A documented process is required: who looks at the
signals, how often, what they do when something deviates, and how the corrective
action is recorded. Without that, the system is a dashboard, not an evidence
base.

### 5.3 Clauses 4–10 as the system's operating loop

In version 1 the feedback layer was the weakest part of the design. ISO 27001
gives it a ready-made form — the plan-do-check-act cycle.

| Clause | Requirement | What the system does |
|---|---|---|
| **4.3** Scope | Define the ISMS scope | The asset graph defines the actual scope; on acquisition the graph extends |
| **6.1.2 / 6.1.3** Risk assessment and treatment | Assess and treat risks | System signals — bus factor, drift, technical debt — feed the risk register with numeric values |
| **6.2** Objectives | Measurable security objectives | System metrics become target values |
| **6.3** Planning of changes (new in 2022) | Changes are planned | Detecting unplanned changes is a direct nonconformity |
| **7.5** Documented information | Documented information under control | Decision memory with versioning |
| **9.1** Monitoring, measurement, analysis, evaluation | Monitor effectiveness | The metric layer in full |
| **9.2** Internal audit | Internal audit | Continuous evidence instead of a scramble before the audit |
| **9.3** Management review | Management review | A weekly digest and a quarterly board-level review |
| **10.1 / 10.2** Nonconformity and corrective action | Nonconformities and corrective actions | Every detected bypass is a nonconformity with traceable remediation |

The practical consequence: **a detected control bypass must not be merely an
alert. It must be a nonconformity with an owner, a deadline, and a corrective
action.** This is simultaneously a requirement of the standard and the answer to
alert fatigue — the signal acquires a defined fate rather than only a
notification.

### 5.4 M&A: extending ISMS scope as a differentiator

For an acquiring group this is the most valuable part, and none of the
competitors do it.

Each acquisition means new assets, new suppliers, new staff, a new stack, and a
new — or absent — security practice. Under ISO 27001 this requires revisiting the
scope (clause 4.3), updating the risk assessment (6.1.2), possibly updating the
Statement of Applicability, and bringing new suppliers into A.5.19–A.5.22.
Today this is done manually, slowly, and usually months late.

**What the system can do [proposed]:**

1. **Before the deal — technical and security due diligence.** Read-only access
   to the target's repositories, where the deal permits it, yields within hours:
   bus factor, dependency health, secrets in history, review process quality, and
   the size of the technical debt. That is concrete input to valuation and to the
   integration plan.
2. **After the deal — automatic gap assessment.** Comparing the acquired
   company's actual state against the acquirer's Statement of Applicability:
   which applicable controls are missing, how large the gap is, what can be closed
   by configuration, and what needs people and time.
3. **Tracking gap closure.** Each gap is a nonconformity with an owner and a
   deadline (clause 10.2). Integration progress becomes measurable rather than
   felt.
4. **Retrospective decision inventory.** The Azure Well-Architected guidance
   recommends retroactive ADRs for brownfield systems. It fits here exactly: why
   this CRM, this data schema, this stack. Without it, an acquirer rebuilds what
   was done deliberately and preserves what was an accident.
5. **A single Statement of Applicability for the group with local exceptions.**
   One standard, documented and justified deviations per entity, and a visible
   convergence deadline.

This turns the ISMS from overhead into an operational integration instrument —
which, for a group planning further acquisitions and answering to institutional
investors, has direct monetary value.

### 5.5 The system itself must be inside the ISMS scope

A meta-level point that is easy to miss. A system aggregating code, tickets, IAM
logs, configurations, and possibly transcripts becomes **one of the most valuable
attack targets in the company**. Compromising it hands an attacker a map of
everything: where the weak points are, who holds which privileges, where review
is absent, and who is the sole holder of knowledge about a critical module.

Requirements for the system itself:

- **Self-hosted is not a preference but an argument under the standard.** It
  removes the need to assess the system as a cloud supplier (A.5.23) and sharply
  simplifies A.5.19–A.5.22. This is probably why vFunction sells self-hosted
  deployment alongside ISO 27001.
- **A.5.15 / A.8.2** — strict access control to the system itself; reading
  signals is not the same permission as reading raw data.
- **A.8.11 Data masking** — masking PII during extraction from transcripts and
  communications.
- **A.8.10 Information deletion** — a retention policy: raw transcripts are
  deleted, extracted decisions are kept. This is also the GDPR data minimisation
  requirement.
- **A.8.15 / A.8.16** — logging access to the system itself, including access by
  the CTO.
- **A.5.34** — privacy and protection of PII, including employees' PII, as an
  explicit control.

The working rule: **raw data lives briefly, derived signals live long.** This
simultaneously reduces compromise risk, simplifies the GDPR justification, and
cuts storage volume.

### 5.6 ISO 42001 as a natural continuation

For a company positioning itself as AI-native this is not an optional extra.

ISO/IEC 42001:2023 is the first certifiable AI management system standard, with
38 Annex A controls. It shares the Harmonised Structure, so clauses 4–10 and the
mechanics of the Statement of Applicability, internal audit, and management
review are common with ISO 27001. Holding ISO 27001 reduces the effort by roughly
a third to a half.

What from this system feeds directly into the 42001 loop:

- **An inventory of AI systems and models** — a mandatory requirement for
  certification. Shadow AI detection is the mechanism that populates it.
- **Tracking what AI agents do in the codebase** — precisely Topogy's
  positioning. For 42001 this is evidence of human oversight and traceability.
- **AI debt inherited through acquisitions** — buying a company means inheriting
  its AI tools and models, frequently undocumented. For 42001 that is an
  extension of the AIMS scope.
- **Decisions about model and provider selection** — decision memory satisfies
  the documentation requirement.

Honest qualifications. As of mid-2026 ISO 42001 **is not harmonised under the
EU AI Act**, so certification confers no presumption of conformity; the
harmonised route runs through CEN-CENELEC JTC 21, and the relevant work item,
prEN 18286, is still at Enquiry stage. The AI Act timetable also moved: under the
Digital Omnibus on AI, approved by the Council on 29 June 2026, obligations for
stand-alone Annex III high-risk systems are deferred to 2 December 2027 and for
AI embedded in Annex I regulated products to 2 August 2028, while the Article 50
transparency obligations were not deferred. Whether the EU AI Act applies at all
to a given company is a separate question for a lawyer rather than an assumption
— a UK-only operator faces a different regulatory surface.

On market demand, be careful: some consultancies estimate that ISO 42001 appears
in roughly 40% of enterprise AI tenders in the EU and around 25% in North America
by mid-2026, but that figure comes from certification vendors, an interested
party. Verify it against your own pipeline, not their blogs.

Also worth noting: for governance of *employee* data specifically, ISO/IEC
27701:2025 may be a better fit than 42001. The 2025 edition became a standalone
management system standard, certifiable without an ISMS, and is aimed directly at
PII controllers and processors.

### 5.7 Honest criticism of ISO 27001 in this context

A mandatory section; without it the picture is unbalanced.

1. **ISO 27001 is easy to game through scope.** An organisation can certify one
   product, one team, one data centre, and put the logo on the whole website. A
   certificate does not mean a company is secure; it means there is an auditable
   security management process within a declared scope. Treat it as a checkbox
   and the system becomes a generator of evidence for theatre.
2. **Risk of priority inversion.** The most likely failure mode: a system
   conceived as an engineering instrument gradually optimises for the audit.
   Signals useful to an auditor start crowding out signals useful to a CTO. This
   is the same pattern that makes governance tooling widely disliked. The
   antidote: **engineering value is primary, the compliance output is a
   by-product.** If the digest contains more about controls than about
   architecture and risk, the project has lost its heading.
3. **Automated evidence is not guaranteed to be accepted.** Auditors differ, and
   some require a documented process around the artifact rather than the artifact
   itself. Build in the process scaffolding, not just the detection.
4. **The cost is real.** Certification for a company of this size means tens of
   thousands of pounds to the certification body plus substantial internal time,
   plus surveillance audits in years one and two and recertification in year
   three. ISO 42001 is a comparable order of magnitude — public estimates for
   initial certification run from roughly ten to fifty thousand dollars depending
   on scope.
5. **Annex A is deliberately generic.** Mapping automated signals to controls
   requires judgement, and that judgement has to be defended in front of an
   auditor. The table in section 5.2 is a proposal, not a Statement of
   Applicability.
6. **Compliance must not become a Trojan horse for monitoring.** Collecting
   individual productivity metrics under an ISO 27001 flag would breach GDPR,
   breach A.5.34, and destroy trust — the worst available outcome.

---

## 6. People and the organisational loop

**Roles in the loop [proposed, informed by Team Topologies and RFC practice]:**

- **Required:** VP Engineering or Head of Engineering, tech leads,
  staff and principal engineers as design outcome facilitators rather than
  approvers, and Head of Security or IT Operations.
- **Control owners.** ISO 27001 requires assigned responsibility (A.5.2). Every
  automated control needs a named owner who receives the signal and is obliged to
  respond. This is not bureaucracy: without it signals go nowhere, which is what
  kills most systems of this kind.
- **An ISMS manager, or Head of IT Operations and Security,** is the central
  figure in the version 2 design. This person, not the CTO, should be the primary
  recipient of compliance signals. The separation matters structurally
  (independence of internal audit, clause 9.2) and culturally.
- **Product loop:** CPO/COO and product leads, to connect engineering to
  strategy.
- **Executive:** CEO and CTO as recipients of aggregated signals and
  participants in the management review (clause 9.3).
- **Finance:** for vendor and budget decisions, A.5.19–A.5.22.

**What is acceptable to hold about people:**

- **Acceptable:** areas of responsibility (from CODEOWNERS), formal expertise,
  authorship history of ADRs and RFCs.
- **With care:** load, and only at team level.
- **Not automatically:** "decision-making style", "speed". That is profiling and
  carries risk under the automated decision-making rules.

**How companies with strong cultures handle this:** Google (design docs); Uber
(RFCs until around 2019, then a tiered Engineering Planning Process with a single
store — a reform driven by senior engineers being overwhelmed by hundreds of RFCs
a week); Squarespace (architecture review twice a week, with the status "not yet"
instead of "rejected"; the key insight is that standing reviewers notice overlaps
and incompatible initiatives, which is the duplicate-detection problem solved by
humans); Klaviyo (600+ RFCs, an architecture review board); Sourcegraph (all RFCs
public internally).

**Specific to an acquiring group:** an onboarding mode is needed for acquired
teams — retrospective decision inventory, mapping their stack onto the shared
graph, surfacing conflicting decisions, and gap assessment against the Statement
of Applicability.

---

## 7. System architecture by layer

**Layer 1 — collection.** Connectors over APIs and webhooks with incremental
synchronisation that does not overload the sources. MCP connectors for LLM
access. Self-hosted deployment.

**Layer 2 — knowledge representation: a hybrid of graph plus event log.**

- **Knowledge graph** for entities and relationships: services, repositories,
  teams, people, decisions, objectives, incidents, vendors, and ISMS controls and
  assets. The asset graph doubles as the A.5.9 inventory of assets, usually the
  most painful ISMS artifact to maintain.
- **Event log** for time-based signals: deployments, force pushes, incidents,
  permission changes. This is also A.8.15 Logging and A.8.16 Monitoring
  activities.
- Rationale for the hybrid: the graph answers "what is connected to what and who
  owns it", the log answers "what happened and when". Drift and bypasses are
  detected from the log; bus factor and duplication from the graph.

**Layer 3 — analysis, in two sub-layers.**

- **Deterministic** (rules, metrics, fitness functions): DORA, force push, merge
  without review, gate bypass, bus factor, hotspots, dependency violations,
  configuration diffs. Fast, cheap, explainable, and it does not hallucinate.
  **Only this layer is fit for compliance purposes** — evidence must be
  reproducible.
- **LLM** (only where genuinely needed): semantic similarity of tasks,
  extraction of decisions from text and transcripts, classification of code to
  strategic theme, assessment of whether reasoning is present. Expensive,
  requires verification, use sparingly.

**Layer 4 — decision memory (the core).** Stores the decision, its context, the
alternatives considered, the reasoning, an expected shelf life, and links to
other decisions and to subsequent code and outcomes. The governing principle is
**automatic extraction** from ADR repositories, RFCs, PR descriptions, and
transcripts — not asking people to write things down. The format is an extended
ADR (Nygard, MADR, or Y-statement). Lifecycle: Proposed → Accepted → Deprecated
or Superseded; accepted records are immutable and changes are made through new
records. This is also clause 7.5.

**Layer 5 — recommendations and ranking.** A recommendation, not a dashboard.
Ranked by severity times confidence times irreversibility, with a configurable
severity threshold. **Two output channels:** engineering (CTO, tech leads — risk,
architecture, duplication) and compliance (ISMS manager — nonconformities,
evidence). Different recipients, different cadence, different language.

**Layer 6 — feedback as PDCA.** Formalised through clauses 9.1 → 9.2 → 9.3 →
10.1/10.2. A signal flagged as a nonconformity acquires an owner, a deadline, and
a corrective action, and the result feeds back into the risk assessment. Plus
simple explicit feedback from the CTO on signal usefulness, used to tune
thresholds.

**Agent architecture [proposed].** Specialised analysis agents rather than a
monolith: DriftAgent (strategy), BypassAgent (control bypass), KnowledgeRiskAgent
(bus factor), DuplicationAgent, ArchitectureAgent, SecurityAgent, DecisionAgent
(decision extraction), and ControlEvidenceAgent (mapping signals to Statement of
Applicability controls). Each reads from the graph and the log and writes signals
in a common format. The open interface for third-party analysers is the part
worth open-sourcing.

---

## 8. Competitive landscape

| Product | What it does | Audience | Deployment | Pricing | Covers | Does not cover |
|---|---|---|---|---|---|---|
| **Backstage (Spotify)** | IDP framework, service catalogue | Platform teams, 200+ engineers | Self-hosted, open source | Free plus 2+ FTE to maintain | Catalogue, ownership, partly A.5.9 | Decisions, drift, bypass, ISMS |
| **Cortex / OpsLevel** | Catalogue plus scorecards plus gates | Engineering leadership | SaaS | Per user, enterprise custom | Standards, ownership | Decision memory, strategy |
| **Port** | IDP with fast time to value | 50–2000 engineers | SaaS | Per service | Catalogue, self-service | Same |
| **Jellyfish** | Investment allocation, board reporting | VP/CTO | SaaS | Roughly $100K+/year enterprise | Engineering-to-business linkage (2.1) | Bypass, drift, decisions |
| **LinearB** | DORA plus gitStream, merge-without-review | Engineering managers, 30–200 engineers | SaaS | Free tier plus roughly $20–50/dev/month | 2.5 partially, DORA | Strategy, decisions, ISMS |
| **Swarmia** | DORA/SPACE, team metrics | Teams | SaaS | Free to 9 devs; $20–39/dev/month | Metrics plus a privacy model | Decisions, bypass, drift |
| **DX (getdx)** | SPACE-based developer experience | Engineering leadership | SaaS | — | DevEx metrics | Same |
| **Faros AI** | SDLC knowledge graph, AI ROI, 100+ integrations | Enterprise | SaaS/hybrid | — | Graph plus metrics plus investment | Decision memory, bypass, ISMS |
| **CodeScene** | Behavioural code analysis: bus factor, hotspots, Code Health, PR gates | Engineering leadership | SaaS / self-hosted | — | 2.6, 2.7, 2.8 | Strategy, decisions, communications |
| **vFunction** | Architectural observability, architectural technical debt (Java/.NET) | Enterprise architects | Self-hosted, ISO 27001 | — | 2.6, technical debt | People, decisions, strategy |
| **ArchSteer** | Auto-ADR from boundary changes, Drift Index, agent steering | Teams working with AI agents | — | — | 2.2, 2.6 | Strategy, people, non-code bypass |
| **Syntaxa** | Architectural intelligence (early stage) | Engineering teams | — | — | Architectural intelligence | Little public information |
| **Calyntro** | Repository intelligence: knowledge risk, coupling, drift | CTO / engineering managers | Self-hosted (Docker) | No per-author pricing | 2.7, 2.6, privacy posture | Strategy, decisions, ISMS |
| **Topogy** | Context layer for AI-native engineering, shadow AI visibility | AI-native teams | — | — | Graph plus drift plus shadow AI | Decision memory, strategy |
| **Unblocked / Greptile** | Knowledge graph over code, Slack, Jira; "why is the code like this" | Engineers, review | SaaS | Greptile roughly $1/review above the included tier | Decision context, duplication | Metrics, strategy, ISMS |
| **Vanta / Drata / Sprinto / Hicomply** | Compliance automation: evidence collection, 30+ frameworks, 200+ integrations | Compliance, CISO | SaaS | Per employee | Compliance evidence, Statement of Applicability | Architecture, decisions, engineering risk, strategy |

**Conclusion.** The field now divides into six clusters, and adding the sixth —
compliance automation — makes the niche clearer rather than weaker. Vanta and
Drata collect control evidence but know nothing about architecture, decisions, or
engineering risk. CodeScene and vFunction know about architecture but produce no
compliance evidence. **The intersection — engineering intelligence that doubles
as ISMS evidence — is unoccupied.** That is a more defensible position than "one
more AI tool for engineering metrics", because it has externally driven,
regulation-backed demand.

The counter-argument deserves equal weight: the compliance vendors have the
buyer relationship, the auditor relationships, and the framework breadth, and
the engineering intelligence vendors have the data. An unoccupied intersection is
sometimes unoccupied because neither side needs to cross it to win.

---

## 9. Research landscape and criticism

**Design rationale capture — a history of failure.** IBIS, QOC, DRed, IDEF6,
KAPTUR/STARS. The conclusion is unambiguous: not used by practitioners (Zhao et
al., ASE 2024). The cause is effort asymmetry — capture costs time upstream while
the benefit accrues downstream. 74% forget their own reasoning; 80% cannot
reconstruct someone else's. **The only workable path is automatic extraction.**
ArchSteer inverts authorship: the system writes, the human curates.

**DORA/SPACE and its critics.** DORA supplies four delivery metrics; SPACE
(2021) supplies five dimensions but almost no guidance on which metrics to use.
McKinsey (2023) measured mostly effort and output. Beck: the report is so absurd
and naive that detailed critique is pointless. North: a category error —
measuring an individual developer's contribution makes as little sense as
measuring one piston's contribution to an engine. Goodhart's lesson: story points
inflate, PRs get split, lines of code grow, coverage covers empty tests.

**Duplication and semantic similarity.** BERT fine-tuned on Quora Question Pairs
reaches roughly 86% accuracy; bi-encoders for scale, cross-encoders for
precision; MinHash for near-duplicate code.

**Extracting decisions from communications.** LLM pipelines with map-reduce over
speaker turns work but degrade in the middle of long transcripts
(lost-in-the-middle). Quality metrics: edit rate, owner resolution accuracy,
deadline parsability.

**Compliance automation literature.** Continuous compliance and
compliance-as-code are actively developing practices — OSCAL from NIST as a
machine-readable control format, Open Policy Agent for policy-as-code. OSCAL is
worth studying as a possible format for the control layer: compatibility would
extend applicability well beyond one company. Note the adoption caveat, though —
FedRAMP RFC-0024 mandates machine-readable authorisation packages by September
2026, yet in 2025 FedRAMP processed over a hundred Rev5 authorisations without a
single OSCAL submission. Machine-readable control formats have a mandate problem,
not only a tooling problem.

**Prior art on the decision format.** Structured MADR extends MADR with YAML
frontmatter for machine-readable metadata, option analysis with risk assessment,
and audit sections for compliance tracking. Any new decision-record format should
start from what already exists rather than beside it.

---

## 10. Risks and honest criticism

1. **Capture cost exceeding benefit — risk number one.** Thirty years of design
   rationale capture failures. Mitigation: zero manual entry, everything
   extracted automatically, first value within the first month.
2. **Alert fatigue.** Mitigation: ranking by severity times confidence times
   irreversibility, a configurable threshold, a weekly digest instead of a
   stream, **and a mandatory fate for every signal** — owner, deadline, and
   corrective action under clause 10.2.
3. **Perception as surveillance.** Mitigation: team metrics, self-hosted,
   transparency, DPIA, human in the loop, never in performance review — and
   **the ISO framing as the primary means of communication** (section 5.1).
4. **Metric gaming.** Mitigation: metrics diagnose systems, not people; team
   level only.
5. **LLM hallucination.** Mitigation: deterministic by default, LLM output
   verified by a human, mandatory source citation. **Do not use LLMs for
   compliance evidence at all** — evidence must be reproducible.
6. **Priority inversion towards compliance.** The likeliest way to spoil the
   project: the system starts optimising for the audit and loses engineering
   value. The indicator of drift is a digest containing more about controls than
   about architecture and risk.
7. **Compliance theatre.** ISO 27001 is gameable through scope narrowing. A
   certificate is evidence of a process within a declared scope, not evidence of
   security.
8. **The system as an attack target.** It is an aggregated map of the company's
   weak points. It must sit inside the ISMS scope with the full set of controls
   (section 5.5).
9. **Acquisitions amplify everything.** Every acquisition brings a new stack,
   someone else's decisions or none at all, a different security culture, and an
   ISMS scope extension. The system has to digest that rather than break on it.

**What is genuinely automatable today:** DORA metrics; bus factor and knowledge
risk; bypass detection (force push, merge without review, gates); hotspots and
technical debt; architectural drift through fitness functions; ticket
duplication; ADR extraction from PRs; evidence collection for technical Annex A
controls.

**What requires a human in the loop:** judging whether reasoning was sound;
judging "rushed"; prioritising signals that touch people; decisions about
strategy drift; mapping signals to Statement of Applicability controls.

**What is still fantasy:** autonomous assessment of whether a decision was
strategically correct; full replacement of an architecture review board; fully
automated certification.

---

## 11. Rollout plan

**Stage 1 — first month. Cheap value from git.**
Connect only git, the issue tracker, and CI/CD. Deliver: bus factor and knowledge
islands across all repositories (critical for an acquirer — where knowledge is
concentrated in acquired teams), DORA by team, bypass detection (force push,
merge without review, disabled gates), and hotspots. Self-hosted, team-level
metrics.
**In parallel:** a draft mapping of the signals already collected onto Annex A
controls — with no ISMS implementation at all, simply to see how much of the
evidence base comes for free. A cheap experiment with high information value.
**Gate to the next stage:** signals from stage 1 demonstrably influenced at least
two or three real decisions.

**Stage 2 — second quarter. Graph, decision memory, ISMS loop.**
Knowledge graph (services, repositories, teams, people, decisions) plus automatic
ADR extraction from PRs, Notion, and Confluence. Strategy drift (mapping epics to
strategic themes). IAM audit and IaC drift.
**Plus:** the asset graph is formalised as the A.5.9 register; control owners are
assigned; detected bypasses become nonconformities with corrective actions; a
DPIA is completed before any employee data is connected. An onboarding mode for
acquired teams with gap assessment against the Statement of Applicability.
**Gate:** decision memory fills without manual entry; strategy drift caught at
least one real divergence; the ISMS loop passed internal audit.

**Stage 3 — one-year horizon. LLM layer, transcripts, ISO 42001.**
Task duplication via embeddings, extraction of verbal decisions from transcripts
(with DPIA and consent), public Slack channels. Agent architecture with an open
analyser interface.
**Plus:** an inventory of AI systems and models as the basis of an AIMS under
ISO 42001; tracking AI agent activity in the codebase as evidence of human
oversight.
**Gate:** false positive rate on LLM-derived signals no higher than roughly 20%,
otherwise roll back.

**What changes course:** if capture requires manual entry, return to automatic
extraction; if staff perceive surveillance, remove the source rather than
"explain" it; if alert fatigue appears, raise the threshold rather than adding
filters on top of noise; if the digest has become a compliance report, restore
the engineering priority.

---

## 12. Open-source strategy

Open the **specification and the protocol**, not the product:

1. **A format for the engineering system graph** — entities and relationships,
   including assets and controls.
2. **A format for decision memory** — an extended ADR with links, expected shelf
   life, and lifecycle. Start from Structured MADR rather than beside it.
3. **An analyser agent interface** — how an analyser emits a signal.
4. **A signal-to-control mapping** — an open, discussable, versioned table
   mapping engineering signals to Annex A controls. OSCAL compatibility would
   make it applicable far beyond one company.

Rationale: this repeats the success model of Backstage (a framework, not a
product) and of ADRs (adr.github.io — a specification). A finished open-source
product competes with vendors and demands continuous maintenance; an open
protocol gathers a community around a standard.

**Item 4 is the most viral element.** "The missing standard for engineering
decision memory" interests a niche of practitioners and researchers. "An open
mapping of engineering signals to ISO 27001 controls" interests a much broader
and paying audience: everyone going through certification and assembling evidence
by hand. That is an area with real pain, real money, and no open standard.
Realistic expectation: niche but loyal and professionally motivated attention —
materially better than "one more engineering metrics tool", and materially worse
than a movement. Open standards need a maintainer with time; budget for that or
publish it as an artifact rather than a project.

---

## Caveats

- Some product information comes from vendors' own websites and is marketing.
  CodeScene's claims about a validated link between Code Health and business
  outcomes, and vFunction's claim to primacy in architectural observability, are
  not independently verified.
- Automatic classification of the *type* of an architectural decision reaches F1
  of roughly 55.2% (Keim et al.) and is usable only as a hint to a human;
  detecting that a decision was made at all reaches 92.1%.
- The mapping of signals to Annex A controls in section 5.2 is **a design
  proposal, not a Statement of Applicability.** A Statement of Applicability is
  built from risk assessment and scope, not from available tooling. An auditor
  may disagree with parts of the mapping.
- The ICO guidance discussion and the UK GDPR commentary are not legal advice.
  Before collecting any data about workers, complete a DPIA and take an opinion
  from a UK data protection lawyer. The applicability of the EU AI Act to any
  particular company is a separate question for a lawyer.
- Certification cost estimates are public reference points with a wide spread,
  depending on scope and certification body.
- The figure for the share of tenders asking about ISO 42001 comes from
  certification service providers, an interested party.
- All items marked [proposed] and all feasibility ratings are design judgement
  based on the approaches surveyed, not the result of a pilot.

---

## Editorial notes on this version

This English document corrects several factual points that were stated
differently in the original Russian draft:

1. **EU AI Act timetable.** The draft stated that high-risk obligations took
   effect on 2 August 2026. Under the Digital Omnibus on AI, given final Council
   approval on 29 June 2026, stand-alone Annex III high-risk obligations are
   deferred to 2 December 2027 and Annex I product-embedded ones to 2 August
   2028. Article 50 transparency obligations were not deferred.
2. **UK automated decision-making.** The draft described an Article 22
   prohibition on solely automated decisions. Section 80 of the Data (Use and
   Access) Act 2025 replaced Article 22 with Articles 22A–22D, in force
   5 February 2026, converting the prohibition into a safeguards regime for
   ordinary personal data. The practical design rule in section 4 is unchanged.
3. **ISO 42001 harmonisation.** The specific European work item, prEN 18286, is
   named; it is at CEN Enquiry stage and is the route to a presumption of
   conformity, which ISO 42001 does not provide.
4. **ISO 27701:2025** is added in section 5.6 as a standalone, separately
   certifiable privacy management standard, which is arguably a closer fit than
   ISO 42001 for the employee-data question this document raises.
5. **Prior art** on machine-readable decision records (Structured MADR) and on
   OSCAL adoption is added to sections 9 and 12, because both bear directly on
   the open-standard proposal.
6. **Company-specific material removed.** Headcount, funding, property counts,
   acquisition counts, named markets, and internal targets have been generalised
   to the roll-up pattern, since this repository is public.
