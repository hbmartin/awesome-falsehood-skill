# Avoid Software Falsehoods Skill

[![CI](https://github.com/hbmartin/awesome-falsehood-skill/actions/workflows/ci.yaml/badge.svg)](https://github.com/hbmartin/awesome-falsehood-skill/actions/workflows/ci.yaml)

This repository packages `avoid-software-falsehoods`, an agent skill for finding fragile assumptions in software designs and code. It distills the [Awesome Falsehood](https://github.com/kdeldycke/awesome-falsehood) corpus into compact, citation-keyed topic digests that agents load on demand while reviewing schemas, validators, parsers, APIs, data models, tests, migrations, UX flows, and integrations — anywhere real-world data breaks simple rules.

It works with any agent that reads `SKILL.md`-style skills, including Claude Code and Codex.

The legacy Awesome Falsehood link index is kept as rebuild input in [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md).

## What it catches

A change like this usually sails through review:

```python
# Schedule the next daily digest "at the same time tomorrow".
next_run = last_run + timedelta(hours=24)
```

With the skill loaded, the agent flags it from the time digest's core rules: adding 24 hours is not "tomorrow at the same local time". Across a DST transition the digest silently drifts an hour, and for users in a zone like `Australia/Lord_Howe` the shift is 30 minutes. The suggested fix is calendar arithmetic in the user's zone (advance the civil date, re-resolve the wall time, and define a policy for skipped or repeated local times) plus a regression test pinned to a DST boundary — with citations back to the upstream articles that document the failure mode.

## Install

Clone and run the installer; it detects Claude Code (`~/.claude/skills`) and Codex (`~/.codex/skills`) and installs for whichever is present:

```sh
git clone https://github.com/hbmartin/awesome-falsehood-skill.git
cd awesome-falsehood-skill
./install.sh            # or --claude / --codex / --all
```

For local development, symlink instead of copying so edits are picked up:

```sh
./install.sh --symlink --claude
```

Manual install is just a copy of the skill directory:

```sh
# Claude Code
mkdir -p "$HOME/.claude/skills"
cp -R skill/avoid-software-falsehoods "$HOME/.claude/skills/"

# Codex
mkdir -p "$HOME/.codex/skills"
cp -R skill/avoid-software-falsehoods "$HOME/.codex/skills/"
```

Pinned installs: each [release](https://github.com/hbmartin/awesome-falsehood-skill/releases) attaches a zip/tarball of the skill directory that unpacks straight into a skills folder.

Restart your agent after installing or updating so it reloads skill metadata.

## Use

The skill triggers automatically when a request involves risky assumptions about time, identity, contact data, geography, money, measurement, text, internationalization, web and network behavior, or software systems.

You can also invoke it explicitly. In Claude Code:

```text
Use the avoid-software-falsehoods skill to review this signup schema.
```

In Codex:

```text
Use $avoid-software-falsehoods to review this booking API for time zone and recurrence edge cases.
```

Good prompts are concrete about the surface being reviewed:

```text
Use the avoid-software-falsehoods skill to suggest tests for this address normalization function.
```

```text
Use the avoid-software-falsehoods skill to check this payment data model for currency and rounding assumptions.
```

## What it covers

- Contact and addressing: email, phone numbers, postal addresses, residence, delivery, and regional defaults.
- Geography and location: coordinates, projections, datums, boundaries, weather, maps, and place names.
- Identity and people: names, gender, biometrics, personal identifiers, family relationships, hiring, and record matching.
- Measurement: units, precision, conversions, tolerances, sensors, rounding, and domain-specific quantities.
- Money and business: prices, currencies, ledgers, tax, inventory, company names, IBANs, and payment rails.
- Software systems and data: versions, build systems, CSV/YAML, file paths, caching, events, search, pagination, randomness, identifiers, and tests.
- Text, internationalization, and typography: Unicode, locale, casing, sorting, segmentation, escaping, fonts, layout, and display width.
- Time: instants, dates, durations, time zones, calendars, recurrence, clocks, precision, and scheduling.
- Web and networks: URLs, IP addresses, DNS, IDNs, HTML, HTTP, REST APIs, retries, redirects, caching, and distributed behavior.

Each topic digest carries `Core Rules`, `Falsehoods To Avoid`, `Edge Cases`, `Recommended Libraries` (the mature libraries the rules allude to), and a `Sources` section whose citation keys resolve in the [source index](skill/avoid-software-falsehoods/references/source-index.md).

## Repository layout

- [skill/avoid-software-falsehoods/SKILL.md](skill/avoid-software-falsehoods/SKILL.md) is the skill entry point.
- [skill/avoid-software-falsehoods/references](skill/avoid-software-falsehoods/references) contains the curated topic digests, loaded only when relevant. This is the single source of truth for digest content.
- [skill/avoid-software-falsehoods/agents/openai.yaml](skill/avoid-software-falsehoods/agents/openai.yaml) contains Codex UI metadata.
- [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md) keeps the original link list as provenance and rebuild input.
- [scripts/prepare_phase1_content.py](scripts/prepare_phase1_content.py) rebuilds the machine-generated source corpus; [scripts/validate_skill.py](scripts/validate_skill.py) validates the packaged skill; [scripts/check_upstream.py](scripts/check_upstream.py) diffs against upstream Awesome Falsehood.
- [tests](tests) covers the scripts; CI runs validation and tests on every push and pull request.
- [CHANGELOG.md](CHANGELOG.md) tracks releases.

## Rebuild reference content

The curated digests under `skill/avoid-software-falsehoods/references/` are maintained by hand and are never overwritten by tooling. To regenerate the machine-generated source mirror, intermediate notes, and retrieval report from the reference link index:

```sh
python3 scripts/prepare_phase1_content.py
```

The script reads [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md), writes `sources/` (including untracked `sources/raw/`, `sources/markdown/`, and `sources/prepared/`) and `reports/`, then validates the generated output. Sources that fail to fetch directly are retried automatically through the Wayback Machine and marked `fetched_wayback` in the manifest.

A weekly workflow diffs the upstream [Awesome Falsehood](https://github.com/kdeldycke/awesome-falsehood) list and files an issue when new falsehood links appear, so digest coverage can keep up.

## Contributing

See the [contributing guide](.github/contributing.md): digest improvements, new sources, and tooling fixes are all welcome. Run `python3 scripts/validate_skill.py` and `python3 -m pytest tests/` before opening a PR.

## License

See [license](license).
