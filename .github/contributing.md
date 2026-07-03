# Contributing

Thanks for helping improve the `avoid-software-falsehoods` skill! This repository packages curated falsehood knowledge as an agent skill, so contributions are about improving the digests, the skill definition, and the tooling around them — not about curating a link list.

## What to contribute

- **Digest improvements**: add a missing falsehood, edge case, core rule, or library recommendation to a topic digest under `skill/avoid-software-falsehoods/references/`. Keep bullets concise, actionable, and phrased so an agent can turn them into design or review guidance.
- **New sources**: if an article documents falsehoods not yet covered, add it to `docs/awesome-falsehood-reference.md` (the rebuild input), add a keyed entry to `references/source-index.md`, and distill its unique guidance into the relevant digest.
- **Skill definition**: improvements to `SKILL.md` routing, trigger description, review guidance, or output expectations.
- **Tooling**: fixes to `scripts/`, CI validation, or the install flow.

## Guidelines

- **Digests are the product.** They are hand-curated, compact, and loaded into agent context, so every line costs tokens. Prefer merging a new falsehood into an existing bullet over adding a near-duplicate. CI enforces a per-file size budget.
- **Keep the digest structure.** Every topic digest must keep its `Core Rules`, `Falsehoods To Avoid`, and `Edge Cases` sections (plus `Recommended Libraries` and `Sources` where present). CI validates this.
- **Cite sources.** New falsehood material should trace back to an entry in `references/source-index.md`. Use the `[X0]`-style citation keys.
- **Don't regenerate over curation.** `scripts/prepare_phase1_content.py` produces machine-generated intermediate notes under `sources/`; it does not (and must not) overwrite the curated digests.
- Check your spelling and grammar, and run the validation locally before opening a PR:

  ```sh
  python3 scripts/validate_skill.py
  python3 -m pytest tests/
  ```

## Pull requests and issues

- Search past issues and pull requests before opening a new one.
- Keep pull requests focused: one topic digest, one tooling change, or one skill-definition change per PR where practical.
- Explain the failure mode a new falsehood prevents — what breaks when a developer believes it.
- Follow the [Code of Conduct](code-of-conduct.md).
