# Money and Business Falsehoods

## Core Rules

- Represent money with decimal or fixed-precision amounts plus explicit currency and effective-date metadata.
- Keep business identifiers, company names, and payment/account numbers as user data that must be escaped, audited, and validated only against the right authority.
- Separate display price, charged amount, taxes, discounts, inventory state, settlement currency, and accounting ledger entries.
- Design financial paths for reversals, corrections, range limits, legal rules, and human review.
- Store monetary values with scale and currency at every boundary: database schema, API payload, queue message, log event, CSV export, and UI formatter.
- Keep calculations reproducible. Record exchange rate source, timestamp, rounding mode, tax jurisdiction, discount rule, and invoice version.
- Escape business names and identifiers in every output context; legal registries can contain strings that look like HTML, SQL, shell syntax, or template markers.
- Use ledger-style append-only records for financial changes where possible; never rely only on mutable balances.

## Falsehoods To Avoid

- Prices are not just numbers: they can be negative, zero, rounded, tax-inclusive, tax-exclusive, localized, discounted, unavailable, or currency-dependent.
- Currencies are not fixed to two decimal places, one symbol, one country, one validity period, or non-overlapping histories.
- Floating point and integer penny splits can both fail if units, scaling, and boundaries are unclear.
- IBANs and business identifiers are not universal, self-validating, immutable, or sufficient proof of ownership.
- Company names can contain punctuation, markup-looking text, SQL-looking text, legal suffix quirks, and jurisdiction-specific forms.
- Markets are not perfectly rational, inventory is not always countable, and economic data has policy and timing assumptions.
- Currency symbols are ambiguous: `$`, `kr`, `£`, `¥`, and similar symbols can map to multiple currencies.
- Currency minor units are not always two decimal places, and cash rounding can differ from electronic accounting precision.
- A price can be per unit, tiered, metered, bundled, tax-inclusive, tax-exclusive, suggested, negotiated, promotional, expired, or region-locked.
- Inventory can be fractional, reserved, backordered, perishable, consigned, virtual, duplicated across warehouses, or temporarily oversold.
- Bank account formats, checksums, and payment rails prove syntax, not ownership, availability, fraud status, or settlement success.
- Business names and legal entities can change, merge, split, operate under trade names, or have conflicting registry and tax records.
- Economic indicators are revised, seasonally adjusted, policy-defined, and collected on schedules that may not match product reporting needs.

## Edge Cases

- Missing decimal points caused 100x overcharges in postage/accounting anecdotes; the bug class is unit confusion, not just bad UI. [B5]
- A system can fail at unexpectedly large compensation, credit, coupon, or ledger values when upper bounds are assumed informally. [B6], [B8]
- UK company names with `<`, `>`, quotes, semicolons, ampersands, and SQL-looking strings demonstrate why output escaping cannot be skipped. [B9], [B10]
- CLDR currency validity ranges can overlap because political and monetary transitions are not clean database intervals. [B12]
- A coupon, credit, refund, or chargeback can exceed the original item price if fees, shipping, currency conversion, or manual adjustment are involved.
- Decimal math still fails if code mixes major units and minor units, or serializes `amount: 100` without declaring whether that means dollars or cents.
- Exchange rates create timing questions: authorization, capture, refund, invoice, settlement, accounting close, and user display can all use different rates.
- Company-name normalization for matching can erase legally meaningful punctuation, articles, suffixes, accents, or abbreviations.

## Recommended Libraries

- Amounts: decimal or fixed-point types (`java.math.BigDecimal`, Python `decimal`, C# `decimal`, `big.js`/`decimal.js`) or integer minor units with an explicit scale — never binary floats.
- Money types: `joda-money`, `py-moneyed`, `dinero.js`, RubyMoney, or equivalents that pair the amount with a currency and an explicit rounding mode.
- Currency metadata: ISO 4217 plus CLDR supplemental currency data for minor units, symbols, and validity ranges [B12].
- Bank identifiers: IBAN validators such as `php-iban` [B3] or `schwifty` (Python) for syntax and checksum only — ownership and reachability need the payment rail.
- Ledgers: double-entry, append-only ledger patterns or dedicated ledger stores instead of mutable balance columns.

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Prices and shopping: [B1], [B2]
- Currencies: [B12]
- IBANs and payment identifiers: [B3]
- Economics: [B4]
- Failure anecdotes: [B5], [B6], [B7], [B8]
- Company names and escaping: [B9], [B10], [B11]
