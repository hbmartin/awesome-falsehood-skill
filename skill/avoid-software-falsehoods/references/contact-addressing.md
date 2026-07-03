# Contact and Addressing Falsehoods

## Core Rules

- Accept user contact data as messy, regional, and time-varying; store the original input plus any normalized form you derive.
- Use dedicated parsers or authoritative delivery/verification flows for email, phone, and postal data; avoid regex-only validation.
- Treat reachability as separate from syntax: a valid-looking address or number can be unreachable, reassigned, shared, temporary, or blocked.
- Keep formatting, validation, and delivery concerns separate so strict downstream requirements do not corrupt user-entered data.
- Prefer permissive capture with clear confirmation over rejecting unusual but legitimate identifiers.
- Store enough structure for the workflow at hand, but keep a raw display value where users or postal authorities care about original spelling, ordering, spacing, or punctuation.
- Design update flows for contact data. People move, addresses are reformatted by authorities, phone numbers are ported or reassigned, and email domains expire or change ownership.
- When you need proof of control, send a confirmation or use a carrier, postal, or provider API. Syntax validation is only a preflight check.
- Treat regional defaults as defaults, not facts. Country, locale, script, and delivery network can differ from the user's UI language, IP geolocation, billing address, or legal residence.

## Falsehoods To Avoid

- Email addresses are not just one simple `local@domain` pattern; quoted local parts, multiple `@` characters, unusual punctuation, internationalized domains, and domain literals exist.
- Email identity is not one-to-one: people can have none, one, many, shared, reassigned, role-based, or changing addresses.
- Phone numbers are not globally uniform identifiers; they can vary in length, formatting, country meaning, reachability, portability, reassignment, and SMS support.
- Postal addresses are not required to have every familiar component: street, house number, city, postal code, state, country, and recipient name can be missing, ambiguous, duplicated, or informal.
- Residence and delivery are different concepts; a person can live somewhere, receive mail elsewhere, have no fixed address, or rely on landmarks and local knowledge.
- Address normalization is lossy when it forces regional formats into a single schema.
- A single postal code can represent one building, many streets, a route, a business, a PO box range, or no useful location at all.
- Country calling codes, national destination codes, extensions, short codes, emergency numbers, and premium-rate numbers do not fit one phone-number length or purpose.
- `+` is not decoration in phone numbers, and leading zeros may be meaningful in national formats while omitted in international formats.
- Email local parts can be case-sensitive by specification even if most providers treat them case-insensitively; provider-specific aliasing with dots or plus tags is not universal.
- MX records, deliverability, spam filtering, greylisting, catch-all domains, and bounce handling make email validity time-dependent and operational.
- A form label such as "address line 2" can encode local assumptions. Some regions need building, entrance, floor, apartment, district, province, prefecture, island, delivery route, or landmark fields.
- Normalizing an address for shipping can be wrong for taxation, identity proofing, emergency service dispatch, or user-facing display.

## Edge Cases

- Valid email examples can include quoted spaces, unusual symbols, source routing remnants, internationalized domains, and addresses that many providers still reject operationally.
- Costa Rican landmark-based directions, Icelandic map-only addressing, UK property oddities, and Smokey Bear having ZIP Code `20252` all break standard address assumptions. [C14], [C15], [C16], [C17]
- Japanese postal CSV data and USPS Publication 28 show that even official address data has formatting and normalization traps. [C19], [C20]
- Libraries such as `libphonenumber`, `libaddressinput`, `addressing`, `postal-address`, and `libvldmail` are support tools, not proof that validation is universal or permanent.
- Quoted email local parts can contain spaces or an `@`; splitting on the first `@` is wrong when quoted strings are allowed.
- A domain literal such as an IP address can be syntactically valid in an email address, even if many real systems reject it.
- A phone number can be valid but unable to receive SMS, or can receive SMS while belonging to a shared service, call center, or recycled user.
- Some addresses are deliverable only because local carriers know the recipient, landmark, route, or institution; automated geocoding may fail while mail still arrives.
- Imported address datasets often contain abbreviations, legacy spellings, mixed scripts, unofficial local names, or administrative changes that are still useful to carriers.

## Recommended Libraries

- Phone numbers: Google `libphonenumber` [C7] or its maintained ports (Python [C10], PHP [C11], C# [C8], iOS [C9]) for parsing, formatting, and metadata — paired with SMS or call verification when you need proof of control.
- Postal addresses: `libaddressinput` [C21] for per-country form layouts; `addressing` [C22], `postal-address` [C23], or `address` [C24] for formatting and subdivision metadata; `libpostal` for parsing free-form input; carrier or postal APIs (USPS, Royal Mail, national posts) when deliverability actually matters.
- Email: maintained RFC-aware validators such as `libvldmail` [C5] only as a preflight check; a confirmation message is the real validity test.

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Email: [C1], [C2], [C3], [C4]
- Phone numbers: [C6]
- Postal addresses, residence, and delivery: [C12], [C13], [C14], [C15], [C16], [C17], [C18], [C19], [C20]
- Support libraries: [C5], [C7], [C8], [C9], [C10], [C11], [C21], [C22], [C23], [C24]
