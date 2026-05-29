# Identity and People Falsehoods

## Core Rules

- Model human attributes as optional, mutable, culturally variable, and sometimes sensitive.
- Never use names, gender, biometrics, family relationships, employer history, or email-like handles as stable identifiers.
- Separate display, legal, preferred, searchable, and machine identifiers; each has different constraints.
- Make validation permissive by default and narrow it only for a specific authority or workflow requirement.
- Design for correction, privacy, and change over time.
- Let users control display names where possible, but store the specific name form required by legal, payroll, travel, healthcare, or billing systems separately.
- Avoid deriving demographic facts from names, titles, pronouns, photos, voice, biometrics, or documents unless the workflow explicitly requires and explains it.
- Make identity records mergeable and splittable. Duplicates, shared devices, aliases, guardians, dependents, and mistaken matches are normal operational cases.
- Treat identity data as high-risk personal data: minimize collection, log access carefully, and provide correction paths.

## Falsehoods To Avoid

- Names do not have a universal first/middle/last structure, fixed order, ASCII spelling, maximum length, gender signal, uniqueness, or permanence.
- A person may have no name, multiple names, one-word names, names containing punctuation or control-looking strings such as `Null`, and names that change by context.
- Gender is not binary, immutable, inferable from name/body/voice, or safe to require without a reason.
- Biometrics are not unique, stable, secret, revocable, always present, or consistently captured across devices and environments.
- Applicants and workers do not have linear, gap-free, single-country, single-employer histories.
- Demographic assumptions about women in tech and other groups create biased systems and bad product decisions.
- A legal name is not necessarily the name a person uses, and a government document can be stale, wrong, transliterated, abbreviated, or incompatible with another authority's format.
- Family relationships are not always biological, legal, unique, current, or expressible as simple parent, spouse, and child rows.
- National IDs, healthcare identifiers, employee IDs, and account IDs can be missing, duplicated, reassigned, merged, fraudulently used, or scoped to a jurisdiction.
- Age, birth date, birthplace, nationality, citizenship, residence, and work authorization are separate attributes and can change or conflict across documents.
- A person can be represented by a guardian, caregiver, executor, organization, household, role account, or delegated agent.
- Search and dedupe on human identity should rank candidates and explain evidence instead of silently collapsing records.

## Edge Cases

- `Null`, SQL-looking names, long names, single-character names, patronymics, mononyms, particles, and reordered name parts are real data, not attacks by default.
- Localized name formatters and healthcare-style name models exist because display names and legal/person-record names are richer than one string field.
- Biometric matching can fail for injury, disability, age, sensor quality, duplicate templates, coercion, or enrollment drift.
- XKCD-style injection names are useful reminders to escape output, but escaping is separate from rejecting real names.
- A name can contain apostrophes, hyphens, spaces, prefixes, suffixes, particles, honorifics, emoji-like characters, non-Latin scripts, or characters that look like markup.
- A user can need different pronouns, names, or privacy levels in different contexts, such as legal paperwork, support tickets, public profiles, and family-facing views.
- Background-check and hiring systems fail when they require continuous employment, one institution per date range, one country, or Western address/name conventions.
- Biometric identifiers cannot be rotated like passwords after compromise; fallback and revocation policies need to exist before enrollment.

