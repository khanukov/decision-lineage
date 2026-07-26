# Security

This repository contains a specification, schemas, and three local scripts. It has no runtime, no network access, and no deployment.

## The scripts, and what they touch

- `tools/validate.py` reads YAML you point it at. Parsing is `yaml.safe_load`, so a record cannot construct Python objects.
- `tools/adr_import.py` reads markdown and YAML frontmatter from a directory you choose, which in normal use is somebody else's repository. Frontmatter is parsed with `yaml.safe_load` and everything else with regular expressions; a malicious ADR can produce a misleading record but not execute anything. It writes only into the `--out` directory you name.
- `tools/conformance.py` executes the command you give it, once per fixture, through a shell. That is the entire point of the tool — it tests an implementation it knows nothing about — but it means the command is trusted input. Fixture paths are shell-quoted before substitution. Do not point it at a command assembled from an untrusted source.

## Reporting

For an issue in the scripts or the schemas, open a normal issue — there is no sensitive attack surface here.

For a flaw in the specification with security consequences — for example, a field that encourages implementers to store data they should not, or a mapping that would mislead an audit — please open an issue and label it `security`. That class of problem matters more here than code defects.

## A note for implementers

An implementation of this specification aggregates a map of an organisation's weak points: where reviews are skipped, which assets have concentrated ownership, which controls have been knowingly weakened. That aggregate is a higher-value target than any of its inputs.

Implementations should be in scope of their own information security management system, should keep raw source material (transcripts, chat logs) for a short retention period while keeping derived records, and should log access to themselves — including administrator access.
