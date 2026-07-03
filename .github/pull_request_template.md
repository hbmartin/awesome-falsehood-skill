### What does this change?

<!-- Digest content, skill definition, tooling, docs? Summarize the change. -->

### Why?

<!--

For digest content: state the falsehood being added or corrected and the failure
mode it prevents — what breaks when code relies on the false assumption.

For tooling/skill changes: describe the problem being fixed.

-->

### Self checks

- [ ] `python3 scripts/validate_skill.py` passes
- [ ] `python3 -m pytest tests/` passes
- [ ] New falsehood material cites a source in `references/source-index.md` (if applicable)
- [ ] I have read the [Contributing guide](https://github.com/hbmartin/awesome-falsehood-skill/blob/main/.github/contributing.md)
