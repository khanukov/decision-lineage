# Contributing

This is a specification, so the most valuable contributions are arguments, not code.

## Most useful right now

1. **A decision your organisation actually made that this model cannot represent.** Open an issue with the decision (redacted as needed) and where the model breaks. This is the highest-value contribution and there is no close second.
2. **A field that is specified but would never be filled in practice.** Specifications rot by accumulating fields nobody uses. Arguing for removal is as useful as arguing for addition.
3. **Disagreement with `mappings/iso27001-2022.yaml` from anyone who has been through a certification audit.** Especially if an auditor rejected something the mapping claims is direct evidence.
4. **Answers to the open questions in [SPEC.md](SPEC.md) §7.**

## Changes to the specification

Substantive changes need an issue before a pull request. The issue should state the problem, not the proposed field. Fields proposed without a stated problem will be asked for the problem.

While the version is `0.x`, breaking changes are acceptable if justified. After `1.0.0` they will not be.

## Changes to code

Tooling in `tools/` has no dependencies beyond `pyyaml` and `jsonschema` and should stay that way. Run all three before opening a pull request:

```bash
pip install pyyaml jsonschema
python3 tools/validate.py                                          # examples and decisions
python3 tools/conformance.py                                       # normative rules
python3 tools/adr_import.py examples/adr-samples --out /tmp/out \
  && python3 tools/validate.py /tmp/out/*.yaml                     # importer round trip
```

Every schema change needs a corresponding example that exercises it. CI validates `examples/` and `decisions/` on every push.

**Every normative change needs a conformance case.** If a pull request adds, removes, or alters a *MUST* or *MUST NOT*, it adds or updates a fixture in `conformance/` and its manifest entry in the same change. A normative rule with no fixture is a rule nobody can be held to, and the suite is the only thing standing between "supports decision-lineage" and a claim that means something.

**Changing a playbook question requires updating its lock.** `playbook/questions.yaml` is a fixed, numbered set, and its value comes entirely from ids meaning the same thing across assessments. Appending is free. Rewording or removing an existing question invalidates every comparison drawn from it, so `tools/playbook_lock.py --check` fails until you run `--update` in the same commit and say in the message what happens to assessments that already answered the old wording.

Rules stated as *SHOULD* must **not** get conformance cases. An implementation that warns on a *SHOULD*, errors on it, or ignores it is equally conformant, so a fixture would fail correct implementations. Put *SHOULD* checks in `tools/validate.py` as warnings instead.

## Dogfooding

Decisions about this specification live in `decisions/`, in the format this specification defines. If you propose a change to the model, the accompanying decision record is the argument.

## Tone

Technical disagreement is welcome and expected. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the rest.
