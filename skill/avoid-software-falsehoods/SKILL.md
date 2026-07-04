---
name: avoid-software-falsehoods
description: Review and build software while avoiding common false assumptions about time and time zones, names and human identity, email addresses, phone numbers, postal addresses, geography, money and currencies, units of measurement, Unicode and internationalization, URLs and network behavior, and software systems data. Use when designing or reviewing database schemas, validators, parsers, API contracts, data models, forms, tests, migrations, or integrations; when building signup, checkout, payments, scheduling, recurring events, cron jobs, localization, search, pagination, CSV or YAML import, or file path handling; or when checking code for fragile assumptions, edge cases, lossy normalization, identifier collisions, or data-loss risks.
---

# Avoid Software Falsehoods

## Core Workflow

1. Identify the domain surfaces in the request: data model, parser, validator, API contract, UI form, workflow, integration, migration, review target, or test suite.
2. Load only the relevant reference digest files from `references/`. Start with each digest's `Core Rules`, then use `Falsehoods To Avoid` and `Edge Cases` as a checklist, and `Recommended Libraries` when choosing or reviewing dependencies.
3. Preserve user intent and raw input where normalization, parsing, localization, or authority-specific validation could be lossy.
4. Separate display values, canonical comparison values, derived values, source-of-truth records, cached/generated state, and external authority results.
5. Prefer mature libraries, standards, authoritative datasets, and explicit policies over ad hoc regexes, string splitting, implicit defaults, or hidden normalization.
6. Convert each relevant falsehood into concrete design, implementation, or test changes. Name the assumption, the failure mode, and the practical fix.

## Topic Router

- Contact and addressing: read `references/contact-addressing.md` for email addresses, phone numbers, postal addresses, residence, delivery, reachability, and regional defaults.
- Geography and location: read `references/geography-location.md` for coordinates, projections, datums, boundaries, weather, geocoding, maps, and place names.
- Identity and people: read `references/identity-people.md` for names, gender, biometrics, personal identifiers, family relationships, hiring, and human-record matching.
- Measurement: read `references/measurement.md` for units, precision, conversions, tolerances, sensors, rounding, and domain-specific quantities.
- Money and business: read `references/money-business.md` for prices, currencies, ledgers, tax, inventory, company names, IBANs, payment rails, and economic data.
- Software systems and data: read `references/software-systems-data.md` for versions, build systems, CSV/YAML, file paths, caching, state machines, events, search, pagination, randomness, identifiers, and tests.
- Text, internationalization, and typography: read `references/text-i18n-typography.md` for Unicode, locale, casing, sorting, segmentation, escaping, fonts, layout, and display width.
- Time: read `references/time.md` for instants, dates, durations, time zones, calendars, recurrence, clocks, precision, and scheduling.
- Web and networks: read `references/web-networks.md` for URLs, IP addresses, DNS, IDNs, HTML, HTTP, REST APIs, retries, redirects, caching, and distributed behavior.
- Provenance: read `references/source-index.md` only when citations, upstream links, or deeper source material are needed. Each digest ends with a `Sources` section whose `[X0]`-style keys resolve to entries in the source index. Read `references/00-overview.md` for a compact map of all topics.

## Review Guidance

- Prioritize assumptions that can cause data loss, rejected legitimate users, security bugs, financial errors, inaccessible UX, incorrect identity matching, operational outages, or irreversible normalization.
- Check whether validation rejects data before the system has a workflow-specific reason to reject it. Prefer permissive capture plus confirmation when authority-specific proof is unavailable.
- Look for hidden one-to-one assumptions: one person, one name, one address, one email, one currency, one time zone, one coordinate, one canonical URL, one ordered version, or one stable external identifier.
- Check boundary behavior: DST transitions, locale differences, missing fields, duplicate events, retries, stale caches, partial failures, unknown enum values, schema additions, and changed external data.
- Recommend targeted tests or fixtures from the relevant digest. Favor examples that encode the real invariant, such as parser round trips, idempotent retries, skipped/repeated local times, Unicode grapheme handling, currency scale, or mutable pagination.
- Keep review output actionable. State the fragile assumption, why it fails, the likely user or system impact, and the smallest robust change.

## Implementation Guidance

- Model uncertainty explicitly with fields for source, authority, timestamp, precision, locale, time zone, unit, currency, format version, or confidence when those attributes affect correctness.
- Keep raw input when canonicalization is operation-specific. Use separate canonical forms for search, display, security checks, routing, deduplication, and external API submission.
- Use authority-specific validation at the boundary that requires it: postal carriers for shipping, email confirmation for control, payment rails for account syntax, time-zone libraries for civil time, geospatial libraries for containment, and ICU-style libraries for text.
- Add correction and migration paths for mutable facts: names, addresses, currencies, time-zone rules, administrative boundaries, identifiers, package versions, cache schemas, and external registry data.
- Escape output in the target context. Do not treat input rejection as a substitute for HTML, SQL, shell, CSV, JSON, log, terminal, URL, or filename escaping.
- Record explicit policies for ambiguous cases so future maintainers know whether behavior is intentional: month arithmetic, skipped recurrence times, duplicate events, rounding modes, unknown enum handling, path normalization, IDN display, and dedupe thresholds.

## Output Expectations

- Mention which reference topics informed the answer.
- Provide concrete implementation or review guidance instead of broad reminders.
- Include test ideas when a falsehood maps to a likely regression.
- Avoid treating the digests as exhaustive law. Use them to surface fragile assumptions, then adapt the fix to the actual product constraints.
