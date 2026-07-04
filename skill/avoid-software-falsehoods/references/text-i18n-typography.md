# Text, Internationalization, and Typography Falsehoods

## Core Rules

- Treat user-visible text as Unicode grapheme clusters with locale, script, direction, encoding, normalization, and rendering context.
- Use locale-aware libraries for case, collation, segmentation, formatting, parsing, pluralization, and display width.
- Store original text; apply normalization intentionally and only for a documented comparison/search purpose.
- Test with multilingual, mixed-script, right-to-left, combining-mark, emoji, malformed, and hostile strings.
- Keep encoding, escaping, normalization, and rendering as separate steps. Fixing one layer does not make the others safe.
- Use ICU or equivalent locale data when casing, sorting, segmenting, formatting dates/numbers, transliterating, or measuring display width.
- Decide what equality means per feature: binary equality, canonical equivalence, search equivalence, visual similarity, and identifier equivalence are different.
- Treat fonts and layout as part of text handling; fallback fonts, shaping engines, ligatures, and line breaking can change user-visible output.

## Falsehoods To Avoid

- Characters are not bytes, code units, code points, glyphs, columns, or user-perceived letters.
- String length, indexing, slicing, upper/lower casing, sorting, regex matching, and display width are not locale-free operations.
- Plain text is not free of encoding, normalization, directionality, fonts, line breaking, or rendering assumptions.
- Languages do not share English grammar, plural categories, word boundaries, name order, punctuation, capitalization, or sentence structure.
- Fonts do not reliably contain every glyph, map one character to one glyph, render the same across platforms, or preserve metrics across fallback.
- Temperature, units, addresses, labels, and other localized fields often require semantic conversion, not string substitution.
- Unicode versions change; new scripts, emoji, properties, and normalization data can alter validation and display over time.
- A code point can be private-use, combining, control-like, default-ignorable, variation-selecting, or meaningful only as part of a sequence.
- Transliteration and romanization are lossy and often many-to-many; they are not stable identifiers.
- Regex character classes, word boundaries, `tolower`, and `toupper` are often ASCII-biased unless configured with locale and Unicode behavior.
- Display truncation by bytes, code units, or code points can split a grapheme cluster or produce broken rendering.
- Language, locale, region, script, keyboard layout, currency, timezone, and UI direction are related but separate preferences.
- User input can be valid Unicode but unsafe in a target context unless escaped for HTML, SQL, shell, CSV, JSON, logs, filenames, and terminals separately.

## Edge Cases

- Combining marks, ligatures, surrogate pairs, zero-width joiners, emoji sequences, regional indicators, and variation selectors break naive substring work.
- Case handling examples such as Turkish dotted/dotless I and German sharp S show that lower/upper/title case are not simple ASCII transforms. [X17]
- Bidirectional text, mixed scripts, homoglyphs, and IDN-like strings can be visually confusing without being invalid.
- Naughty-string corpora and i18n testing datasets are support material for finding assumptions in validation, escaping, storage, and rendering.
- Emoji skin-tone modifiers, family sequences, flags, and ZWJ sequences can be one displayed unit made of many code points.
- Normalization can turn visually similar strings into equal strings, or leave visually similar strings distinct; both outcomes can be correct depending on feature intent.
- Monospace assumptions fail with East Asian wide characters, combining marks, emoji, ligatures, and fallback fonts.
- Line wrapping differs for Thai, Japanese, Chinese, Korean, Arabic, and emoji-heavy text because spaces are not universal word separators.
- Case-insensitive identifiers can collide after Unicode folding even when source strings look distinct.

## Recommended Libraries

- Locale infrastructure: ICU (ICU4C, ICU4J, ICU4X) backed by CLDR data for casing, collation, segmentation, formatting, and transliteration.
- Grapheme segmentation: `Intl.Segmenter` (JavaScript), `unicode-segmentation` (Rust), `grapheme`/`uniseg` libraries (Python, Go) instead of code-point iteration.
- Normalization: standard-library NFC/NFD/NFKC/NFKD (`unicodedata`, `String.prototype.normalize`) applied per documented comparison purpose.
- Messages and plurals: ICU MessageFormat or Fluent instead of string concatenation and hand-rolled plural rules.
- Rendering: HarfBuzz-based shaping and platform text stacks; test fallback fonts and display width with multilingual corpora [X14] and hostile strings [X15].

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Language and grammar: [X1], [X2]
- Plain text and Unicode: [X3], [X4], [X6], [X8], [X9], [X10], [X11]
- Casing: [X17]
- Localization semantics: [X13]
- Fonts and typography: [X16]
- Test corpora and talks: [X5], [X7], [X12], [X14], [X15]
