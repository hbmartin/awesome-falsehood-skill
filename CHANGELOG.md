# Changelog

All notable changes to the `avoid-software-falsehoods` skill are documented here.
Releases are tagged `vX.Y.Z`; each release attaches a zipped copy of the skill
directory for pinned installs.

## Unreleased

- Made the skill agent-agnostic: install instructions and packaging for Claude
  Code (`~/.claude/skills`) alongside Codex (`~/.codex/skills`), and a
  trigger description no longer tied to one agent.
- Added `install.sh` with copy and symlink modes, and a tagged-release workflow
  that publishes zip/tarball archives of the skill.
- Added a `Recommended Libraries` section to every topic digest, naming the
  mature libraries the core rules allude to.
- Added `[X0]`-style citation keys to `references/source-index.md` and a
  `Sources` section to every topic digest so review output can cite upstream
  articles without loading the whole index.
- Removed the duplicated `prepared/` copy of the digests; the skill's
  `references/` directory is now the single source of truth. The rebuild
  script writes its machine-generated intermediate notes to `sources/prepared/`
  (untracked) and can no longer clobber curated content.
- Added Wayback Machine fallback to the source-retrieval script for sources
  that fail to fetch directly.
- Replaced inherited repomatic workflows with CI that validates the skill
  (frontmatter, digest structure, citation keys, internal links, size budget)
  and runs the test suite; added tests for the rebuild script.
- Added a weekly upstream-sync workflow that files an issue when new links
  appear in kdeldycke/awesome-falsehood.
- Rewrote contributing guide, issue templates, and PR template for skill
  contributions instead of link-list curation.
