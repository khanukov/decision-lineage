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

`tools/validate.py` has no dependencies beyond `pyyaml` and `jsonschema` and should stay that way. Run it before opening a pull request:

```bash
pip install pyyaml jsonschema
python3 tools/validate.py
```

Every schema change needs a corresponding example that exercises it. CI validates `examples/` and `decisions/` on every push.

## Dogfooding

Decisions about this specification live in `decisions/`, in the format this specification defines. If you propose a change to the model, the accompanying decision record is the argument.

## Tone

Technical disagreement is welcome and expected. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the rest.
