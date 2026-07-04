# Software, Systems, and Data Falsehoods

## Core Rules

- Prefer specifications, mature libraries, and property/fixture tests for tricky formats, identifiers, parsers, and distributed workflows.
- Make parsing, normalization, comparison, ordering, retries, and idempotency rules explicit and observable.
- Treat versions, paths, caches, state machines, search indexes, events, and identifiers as domain models, not plain strings.
- Keep source-of-truth, generated state, cached state, and user-visible state separate.
- Design software processes for partial failure, stale data, concurrency, undefined behavior, and human/social process gaps.
- Fail closed for ambiguous parsing only where rejection is safe; otherwise capture raw input, explain uncertainty, and require confirmation.
- Encode invariants in tests and types when possible: parser round trips, idempotent handlers, ordering guarantees, retry behavior, and serialization compatibility.
- Record provenance for derived data. Generated files, caches, indexes, package locks, and normalized identifiers should say what produced them and when.
- Prefer explicit state transitions over boolean flags when workflows have retries, cancellation, partial completion, or manual overrides.
- Make operational behavior inspectable: log parse modes, schema versions, clock sources, dependency resolution, cache hits, and external IDs.

## Falsehoods To Avoid

- Versions are not always numeric, ordered, unique, immutable, comparable, released once, or tied to exactly one artifact.
- Build systems do not run in clean, deterministic, local, single-language worlds; environment, paths, clocks, caches, generated files, and networks leak in.
- Undefined behavior, null pointers, CPU caches, garbage collection, randomness, and file modification times do not behave like simple source-code abstractions.
- CSV, YAML, package metadata, file paths, search queries, pagination cursors, autocomplete inputs, and content tags all have format-specific edge cases.
- State machines and event-driven systems need explicit states, duplicate handling, ordering expectations, replay behavior, and failure recovery.
- DOIs, CVEs, usernames, and other identifiers are not always stable, unique, canonical, dereferenceable, case-normalized, or controlled by one authority.
- Testing does not prove absence of bugs, production equivalence, user behavior, or future correctness.
- Education, job title, seniority, or familiar terminology does not guarantee shared understanding of computing concepts.
- SemVer, calendar versions, prereleases, epochs, build metadata, distro revisions, and vendor-patched releases do not share one ordering model.
- Build reproducibility can be broken by absolute paths, locale, environment variables, network fetches, file ordering, timestamps, CPU features, and undeclared tools.
- Cache correctness is not just key lookup: invalidation, eviction, stampede control, serialization format, dependency changes, and negative caching all matter.
- CSV is not simply comma-split text; quoting, embedded newlines, encodings, delimiters, formulas, BOMs, headers, and spreadsheet interpretation change behavior.
- YAML is not just JSON with comments; implicit typing, anchors, merge keys, duplicate keys, and parser version differences can change meaning.
- Pagination is not stable when records are inserted, deleted, resorted, filtered, or permissioned between requests.
- Event-driven systems do not guarantee exactly-once processing unless the whole path is built around idempotency, dedupe keys, durable state, and replay semantics.
- Randomness APIs differ by platform and purpose; simulation randomness, cryptographic randomness, and unique ID generation have different requirements.
- Autocomplete and search can leak private data through suggestions, ranking, logs, typo correction, and prefix matching.
- Identifier display and identifier comparison can have different canonical forms; never assume what users paste is already normalized.

## Edge Cases

- Floating point examples such as `0.1 + 0.2 != 0.3` are expected representation behavior, not language breakage. [S25]
- Windows paths, Unix paths, UNC paths, reserved names, symlinks, normalization, case sensitivity, and mount behavior break portable string assumptions.
- YAML can turn strings into numbers, booleans, timestamps, or non-string keys unless parsers and schemas are chosen carefully. [S26]
- `mtime` comparison can miss changes or invent changes because clocks, resolution, filesystems, and copy tools differ. [S23]
- Search behavior depends on tokenization, stemming, stop words, analyzers, highlighting, ranking, pagination, and index freshness.
- Package managers and build tools can disagree about names, versions, dependency resolution, lockfiles, and platform compatibility.
- Path gotchas include reserved device names, trailing dots/spaces, Unicode normalization, symlink loops, hard links, network mounts, case folding, and maximum path lengths.
- Null pointer behavior differs across language, optimizer, ABI, memory model, provenance rules, and hardware fault behavior.
- Garbage collection can pause, move, finalize late, interact with native resources, and fail to match object lifetime expectations.
- CPU caches and memory models make "it worked in a single-threaded test" weak evidence for concurrent correctness.
- CVE records can be disputed, duplicated, delayed, rejected, rescored, or refer to a vulnerability whose affected range is still unclear.
- DOI resolution can redirect, break, change landing pages, contain case or punctuation surprises, and identify non-paper artifacts.
- State machines fail when invalid states are representable, transitions are implicit, or persistence captures a half-transition.
- Tests that rely on time, network order, filesystem order, random seeds, or external package state are often nondeterministic.

## Recommended Libraries

- Versions: the SemVer reference parsers, `packaging.version` (Python), `semver` (Rust/JS), plus explicit policies for epochs, prereleases, and distro revisions [S6].
- CSV: real CSV parsers (Python `csv`, Papa Parse, univocity, Rust `csv`) with explicit dialect, encoding, and quoting settings [S11].
- YAML: YAML 1.2 parsers or safe-loading modes (`yaml.safe_load`, StrictYAML) with schemas to defuse implicit typing [S26].
- Paths: standard-library path types (`pathlib`, `std::path`, `java.nio.file.Path`) over string concatenation [S18], [S19].
- Randomness and IDs: CSPRNG APIs (`secrets`, `crypto.randomBytes`, `getrandom`) for anything security-relevant [S20]; UUID/ULID/KSUID libraries for identifiers.
- Retries and events: idempotency keys, dedupe stores, and clients or brokers whose at-least-once semantics are made explicit [S28].

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Meta and general programming: [S1], [S2], [S3], [S4], [S5]
- Versions, builds, and packages: [S6], [S7], [S12]
- Language and runtime behavior: [S8], [S9], [S10], [S17], [S25]
- Formats and paths: [S11], [S18], [S19], [S23], [S26]
- Search, pagination, autocomplete, tagging: [S14], [S15], [S16], [S24], [S27]
- State, events, randomness: [S20], [S21], [S28]
- Identifiers, testing, and process: [S13], [S22], [S29], [S30]
