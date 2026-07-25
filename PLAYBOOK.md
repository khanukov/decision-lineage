# The inheritance playbook

How to take over an engineering system you did not build — through acquisition,
a handover, or a team that left — and end up with something durable rather than
a folder of notes.

This is the workflow the specification was extracted from. The format is what
the playbook writes into; the playbook is why anyone would fill the format in.
Neither is much use without the other, so they live in the same repository.

---

## When it runs

**On a trigger, not continuously.** A deal signs, a system transfers, a team
gives notice. Somewhere between eight and ten times a year for an acquisitive
group, once or twice for everyone else. This is deliberate and it is the single
most important design constraint here.

Continuous monitoring of an engineering organisation is a different thing with a
different risk profile: it needs a standing legal basis, it reads as
surveillance to the people inside it, and it produces a stream nobody has time
to read. A discrete assessment with a stated purpose, a defined scope, a start
and an end is easier to justify, easier to explain, and more likely to be acted
on — because it lands as a report on somebody's desk rather than as a dashboard
nobody opens.

If you find yourself wanting to leave it running, that is a different project.
Do not let it become this one by accident.

## Run it on yourself first

The third artifact below is a comparison against your baseline. Most groups
discover at this point that their baseline exists only as "well, we mostly do
it like this", which cannot be compared against anything.

So the first run is against your own systems. It costs a day, it produces the
baseline as a by-product, it exercises the tooling on data you unambiguously
have the right to process, and it means the first real assessment has something
to compare with. It also tells you which of your own answers are embarrassing,
which is useful before you go and judge somebody else's.

## What it produces

Three artifacts. No dashboard, no score, no ongoing feed.

### 1. The risk read

What you are taking on: knowledge concentration, control state, dependency
health, secrets in history, debt and coupling. Sections K, C and T of
[`playbook/questions.yaml`](playbook/questions.yaml). Almost entirely derived
from the repository, so it costs hours rather than weeks once access exists.

Output: a document, and a set of Signals sharing one `run` identifier.

### 2. The decision inventory

Which of the things this system does were chosen on purpose. Section D. Partly
derived — boundary-altering changes are visible in history — and then finished
by asking someone who was there, because the commit shows *what* changed and
never *why*.

Output: Decision Records with `origin: inherited`, `origin_source` naming the
entity, and `provenance.attestation` recording how much is actually known about
each one.

### 3. The gap list

Where they differ from your baseline, what closing each gap costs, who owns it,
and by when. Section G.

Output: Signals carrying `baseline`, with a `disposition` giving each gap an
owner and a date. A gap with no owner is an observation; a gap with an owner and
a date is a plan.

## The question set is fixed on purpose

[`playbook/questions.yaml`](playbook/questions.yaml) is a stable, numbered set,
and that is the whole compounding mechanism.

Five assessments that asked whatever seemed relevant at the time produce five
essays. Five that asked `K1` and `D3` and `C4` produce a comparison: which
acquired teams had a bus factor of one, which of their decisions turned out to
be deliberate, how often credentials were sitting in history. By the fifth deal
you can tell a new team's answers against four previous ones, and that is
knowledge the group owns rather than knowledge that lived in whoever ran the
last integration.

Append questions between runs. Never renumber, never repurpose an id, never
quietly change what a question means. A drifting id destroys every comparison
that used it, and does so invisibly.

## Attestation, and why the seller is not a neutral source

Section D is answered by people, and for an acquisition those people frequently
have an interest in the answers. A founder under an earn-out has every reason to
describe an accident as a strategy, and no reason to volunteer that a design was
a Friday afternoon expedient nobody revisited.

This is not a reason to skip the interviews — they are the only source for D3,
D4 and D5, and those are the most valuable answers in the set. It is a reason to
record provenance rather than conclusions:

| State | Meaning |
|---|---|
| `attestation: none` | Derived from history. Nobody has confirmed it. |
| `record_reviewed` | Someone read the record and thought it fair. |
| `participant_confirmed` | Someone who was there confirmed the reasoning. `attested_by` names who. |

`participant_confirmed` is a claim about where the account came from, not a
guarantee that it is true. Recording who said it is what lets a reader two years
later weigh it themselves. A record that flattens all three states into
"documented" is worse than no record, because it launders an interested account
into an established fact.

## The legal boundary

The riskiest of the three artifacts is not the one people expect.

**The risk read processes personal data belonging to people who do not work for
you.** Commit authorship identifies individuals. Bus factor derived from author
names is processing of their personal data. They are not your employees, they
have had no notice from you, and your basis is the acquirer's legitimate
interest in the transaction. Both you and the target are controllers, and both
need a lawful basis for the disclosure.

Practical consequences, none of which are legal advice and all of which want a
data protection lawyer before the first run:

- Complete a DPIA before the first assessment, not before the first deal that
  makes you nervous.
- Keep raw material — cloned repositories, exports, transcripts — only until
  completion, then delete it. Derived records persist; sources do not.
- Have the seller notify their team that technical due diligence is happening.
  A line in the transaction documents costs nothing and fixes the notice
  problem at its source.
- Liability for the target's data protection failures transfers to you on
  completion, which is why question T4 is in the set even though it is not an
  engineering question.

The decision inventory and the gap list are much cleaner: both are about the
system, not about the people who built it.

## What this deliberately does not do

- **No scoring of the acquired team.** Bus factor and review discipline describe
  the system; the temptation after completion is to read them as an assessment
  of the engineers you just bought. That is a different activity, it poisons the
  integration it was meant to help, and the specification refuses to represent
  it: a Signal's subject cannot be a person.
- **No continuous monitoring.** See the trigger, above.
- **No strategy drift, no investment allocation, no productivity metrics.** All
  of those are continuous, all are about people at some remove, and none of them
  helps you take over a system.
- **No compliance evidence engine.** Signals map to controls if you want them
  to, and the mapping is optional and versioned. If the report starts containing
  more about controls than about architecture and risk, the exercise has been
  captured and should be pulled back.

## Timing, honestly

Repository access before exclusivity is rare, and asking for it early sometimes
costs goodwill you need elsewhere. Expect the risk read to land in confirmatory
diligence or shortly after signing.

That means it informs the integration plan, retention decisions, and possibly
escrow or a retention holdback — but usually not the opening price. Designing
this for pre-LOI access will disappoint. Designing it to be the first week of
integration will not.

The decision inventory has the opposite timing problem: it is best done while
the people who made the decisions are still reachable, which is a window that
closes fast after completion. If you can only do one thing in the first month,
do section D.

## How it writes into the format

```yaml
# A signal from the risk read
run: dd-agency-north-2026-06        # groups everything from this assessment
baseline: group-engineering-standard-v3   # only on gap-list signals
subject:
  kind: repository                  # never a person
  ref: agency-north/lettings-portal
```

```yaml
# A decision from the inventory
origin: inherited
origin_source: agency-north         # an organisation, never a person
provenance:
  extracted_from: transcript
  attestation: participant_confirmed
  attested_by: former-technical-lead-agency-north
```

Start the inventory by importing whatever ADRs already exist:

```bash
python3 tools/adr_import.py ../agency-north/doc/adr \
    --origin inherited --origin-source agency-north --out records/agency-north
```

Everything that comes out carries `attestation: none`. Section D is the work of
raising some of those to `participant_confirmed` before the people who could do
it have left.

See [`examples/DL-0021-inherited-crm-schema.yaml`](examples/DL-0021-inherited-crm-schema.yaml)
for a finished record from this workflow.

## After the fifth one

The library is the point. Not any individual assessment — those get read once
and filed — but the accumulated answers to the same questions across every team
the group has absorbed.

What it gives you: a prior. When the sixth target says their CRM schema is
deliberate, you have four previous answers to the same question and a sense of
how often that turns out to be true. When you are estimating integration cost,
you have five previous estimates and five actual outcomes, recorded as
`outcomes` on the decisions that predicted them.

That is the only compounding asset in this whole design, and it exists only if
the questions stayed the same.
