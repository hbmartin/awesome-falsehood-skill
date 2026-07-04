# Measurement Falsehoods

## Core Rules

- Store numbers with explicit units, precision, and measurement context.
- Use unit-aware libraries for conversion, comparison, display, and parsing.
- Preserve source values when converting so rounding and presentation do not destroy auditability.
- Separate measured value, displayed value, rounded value, tolerance, and regulatory reporting value.
- Record whether a quantity is exact, estimated, nominal, calibrated, user-entered, sensor-derived, or computed from other values.
- Treat dimensions as part of type safety. Length, area, volume, mass, force, pressure, energy, power, and temperature are not interchangeable even when represented as numbers.

## Falsehoods To Avoid

- There is no single universal unit system for length, mass, volume, temperature, pressure, energy, or other measurements.
- Unit names and symbols are not always unambiguous, locale-independent, or safely parseable as plain text.
- Conversions are not always exact, linear, reversible, or appropriate without context.
- Prefixes and abbreviations can collide: `m`, `M`, `min`, `mi`, `lb`, `oz`, `pt`, and `ton` are not safe without a unit vocabulary.
- Rounding rules depend on domain. Manufacturing tolerances, medicine, shipping, recipes, science, and accounting can require different precision policies.
- User locale affects decimal separators, thousands separators, unit preferences, paper sizes, temperature display, and direction of conversion.
- A sensor reading can include calibration drift, sampling interval, noise, missing values, and an uncertainty range.

## Edge Cases

- Temperature values and temperature differences localize differently; `20 C` and a `20 C` change are not the same conversion problem.
- Historical, industry-specific, and regional units can share names while meaning different quantities.
- A value like `1/2 cup`, `2 by 4`, `5' 11"`, or `100 km/h` carries parsing conventions beyond a decimal number.
- Shipping dimensions often require packed size, unpacked size, dimensional weight, actual weight, and carrier-specific rounding.
- Medical and laboratory units can be per-volume, per-mass, molar, activity-based, or normalized to body surface area.

## Recommended Libraries

- Unit-aware quantities: `pint` (Python), JSR-385 / Indriya (Java), UnitsNet (.NET), `js-quantities` or `mathjs` units (JavaScript), `uom` (Rust) instead of bare numbers.
- Medical and laboratory units: UCUM codes with validated conversion tables rather than ad hoc unit strings.
- Locale-aware display: CLDR/ICU number and measurement formatters for separators, symbols, and preferred unit systems.

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Systems of measurement: [M1]
- Localized temperature conversion: [X13] (indexed under text and internationalization)
