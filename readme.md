# Avoid Software Falsehoods Skill

This repository packages `avoid-software-falsehoods`, a Codex skill for finding fragile assumptions in software designs and code. It helps review schemas, validators, parsers, APIs, data models, tests, migrations, UX flows, integrations, and other areas where real-world data breaks simple rules.

The legacy Awesome Falsehood link index is kept only as reference material in [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md). The root README now documents the skill and how to use it.

## Install

Install the skill by copying the skill directory into your local Codex skills folder:

```sh
mkdir -p "$HOME/.codex/skills/avoid-software-falsehoods"
cp -R skill/avoid-software-falsehoods/. "$HOME/.codex/skills/avoid-software-falsehoods/"
```

For local development, you can symlink the skill instead:

```sh
mkdir -p "$HOME/.codex/skills"
ln -sfn "$PWD/skill/avoid-software-falsehoods" "$HOME/.codex/skills/avoid-software-falsehoods"
```

Restart Codex after installing or updating the skill so it reloads the skill metadata.

## Use

The skill can trigger automatically when a request involves risky assumptions about time, identity, contact data, geography, money, measurement, text, internationalization, web and network behavior, or software systems.

You can also invoke it explicitly:

```text
Use $avoid-software-falsehoods to review this signup schema.
```

Good prompts are concrete about the surface being reviewed:

```text
Use $avoid-software-falsehoods to review this booking API for time zone and recurrence edge cases.
```

```text
Use $avoid-software-falsehoods to suggest tests for this address normalization function.
```

```text
Use $avoid-software-falsehoods to check this payment data model for currency and rounding assumptions.
```

## What It Covers

- Contact and addressing: email, phone numbers, postal addresses, residence, delivery, and regional defaults.
- Geography and location: coordinates, projections, datums, boundaries, weather, maps, and place names.
- Identity and people: names, gender, biometrics, personal identifiers, family relationships, hiring, and record matching.
- Measurement: units, precision, conversions, tolerances, sensors, rounding, and domain-specific quantities.
- Money and business: prices, currencies, ledgers, tax, inventory, company names, IBANs, and payment rails.
- Software systems and data: versions, build systems, CSV/YAML, file paths, caching, events, search, pagination, randomness, identifiers, and tests.
- Text, internationalization, and typography: Unicode, locale, casing, sorting, segmentation, escaping, fonts, layout, and display width.
- Time: instants, dates, durations, time zones, calendars, recurrence, clocks, precision, and scheduling.
- Web and networks: URLs, IP addresses, DNS, IDNs, HTML, HTTP, REST APIs, retries, redirects, caching, and distributed behavior.

## Repository Layout

- [skill/avoid-software-falsehoods/SKILL.md](skill/avoid-software-falsehoods/SKILL.md) is the skill entry point.
- [skill/avoid-software-falsehoods/references](skill/avoid-software-falsehoods/references) contains compact topic digests loaded only when relevant.
- [skill/avoid-software-falsehoods/agents/openai.yaml](skill/avoid-software-falsehoods/agents/openai.yaml) contains UI metadata.
- [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md) keeps the original link list as provenance and rebuild input.
- [scripts/prepare_phase1_content.py](scripts/prepare_phase1_content.py) rebuilds the prepared corpus from the reference link index.

## Rebuild Reference Content

The prepared corpus is already checked in under `prepared/` and copied into the skill references under `skill/avoid-software-falsehoods/references/`. To regenerate the source mirror, prepared notes, and retrieval report from the reference link index:

```sh
python3 scripts/prepare_phase1_content.py
```

The script reads [docs/awesome-falsehood-reference.md](docs/awesome-falsehood-reference.md), writes `sources/`, `prepared/`, and `reports/`, then validates the generated output.

## License

See [license](license).
