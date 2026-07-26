# Security

This repository contains a specification, schemas, and a validation script. It has no runtime, no network access, and no deployment.

## Reporting

For an issue in `tools/validate.py` or the schemas, open a normal issue — there is no sensitive attack surface here.

For a flaw in the specification with security consequences — for example, a field that encourages implementers to store data they should not, or a mapping that would mislead an audit — please open an issue and label it `security`. That class of problem matters more here than code defects.

## A note for implementers

An implementation of this specification aggregates a map of an organisation's weak points: where reviews are skipped, which assets have concentrated ownership, which controls have been knowingly weakened. That aggregate is a higher-value target than any of its inputs.

Implementations should be in scope of their own information security management system, should keep raw source material (transcripts, chat logs) for a short retention period while keeping derived records, and should log access to themselves — including administrator access.
