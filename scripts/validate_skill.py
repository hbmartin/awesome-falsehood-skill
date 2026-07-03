#!/usr/bin/env python3
"""Validate the packaged avoid-software-falsehoods skill.

Checks, in order:

1. SKILL.md frontmatter: parseable, `name` matches the skill directory and the
   `[a-z0-9-]` convention, `description` present and within the 1024-character
   limit agent harnesses enforce.
2. Router integrity: every `references/*.md` file mentioned in SKILL.md exists,
   and every file in `references/` is routed to from SKILL.md.
3. Digest structure: every topic digest keeps its required sections.
4. Citations: every `[X0]`-style key used in a digest resolves to exactly one
   entry in `references/source-index.md`.
5. Internal links: relative Markdown links in the README and references resolve
   to files in the repository.
6. Size budget: digests are loaded into agent context, so each file and the
   total reference payload have byte ceilings.

Exit status is non-zero if any check fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill" / "avoid-software-falsehoods"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
SOURCE_INDEX = REFERENCES_DIR / "source-index.md"
README = ROOT / "readme.md"

MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_REFERENCE_FILE_BYTES = 20_000
MAX_REFERENCES_TOTAL_BYTES = 120_000

REQUIRED_DIGEST_SECTIONS = (
    "## Core Rules",
    "## Falsehoods To Avoid",
    "## Edge Cases",
    "## Recommended Libraries",
    "## Sources",
)
NON_DIGEST_FILES = {"00-overview.md", "source-index.md"}

CITATION_KEY_RE = re.compile(r"\[([A-Z]{1,2}\d{1,3})\]")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_frontmatter(errors: list[str]) -> None:
    if not SKILL_MD.exists():
        errors.append(f"Missing {SKILL_MD.relative_to(ROOT)}")
        return
    fields = parse_frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    if fields is None:
        errors.append("SKILL.md frontmatter is missing or unterminated.")
        return
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append("SKILL.md frontmatter is missing `name`.")
    elif name != SKILL_DIR.name:
        errors.append(f"SKILL.md name {name!r} does not match directory {SKILL_DIR.name!r}.")
    elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errors.append(f"SKILL.md name {name!r} is not lowercase-hyphenated.")
    elif len(name) > MAX_NAME_LEN:
        errors.append(f"SKILL.md name is {len(name)} chars (max {MAX_NAME_LEN}).")
    if not description:
        errors.append("SKILL.md frontmatter is missing `description`.")
    elif len(description) > MAX_DESCRIPTION_LEN:
        errors.append(
            f"SKILL.md description is {len(description)} chars (max {MAX_DESCRIPTION_LEN})."
        )


def check_router(errors: list[str]) -> None:
    text = SKILL_MD.read_text(encoding="utf-8") if SKILL_MD.exists() else ""
    routed = set(re.findall(r"`references/([\w.-]+\.md)`", text))
    existing = {path.name for path in REFERENCES_DIR.glob("*.md")}
    for name in sorted(routed - existing):
        errors.append(f"SKILL.md routes to references/{name}, which does not exist.")
    for name in sorted(existing - routed):
        errors.append(f"references/{name} is never routed to from SKILL.md.")


def check_digest_sections(errors: list[str]) -> None:
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        if path.name in NON_DIGEST_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_DIGEST_SECTIONS:
            if f"\n{section}\n" not in f"\n{text}\n":
                errors.append(f"{path.name} is missing required section {section!r}.")


def check_citations(errors: list[str]) -> None:
    if not SOURCE_INDEX.exists():
        errors.append("references/source-index.md is missing.")
        return
    index_text = SOURCE_INDEX.read_text(encoding="utf-8")
    defined: dict[str, int] = {}
    for key in CITATION_KEY_RE.findall(index_text):
        defined[key] = defined.get(key, 0) + 1
    for key, count in sorted(defined.items()):
        if count > 1:
            errors.append(f"Citation key [{key}] is defined {count} times in source-index.md.")
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        if path.name in NON_DIGEST_FILES:
            continue
        for key in set(CITATION_KEY_RE.findall(path.read_text(encoding="utf-8"))):
            if key not in defined:
                errors.append(f"{path.name} cites [{key}], which is not in source-index.md.")


def check_internal_links(errors: list[str]) -> None:
    candidates = [README, SKILL_MD, *sorted(REFERENCES_DIR.glob("*.md"))]
    for path in candidates:
        if not path.exists():
            continue
        for match in MD_LINK_RE.finditer(path.read_text(encoding="utf-8")):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} links to missing file {target}.")


def check_size_budget(errors: list[str]) -> None:
    total = 0
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        size = path.stat().st_size
        total += size
        if size > MAX_REFERENCE_FILE_BYTES:
            errors.append(
                f"{path.name} is {size} bytes (budget {MAX_REFERENCE_FILE_BYTES}); "
                "digests are loaded into agent context, so trim or split it."
            )
    if total > MAX_REFERENCES_TOTAL_BYTES:
        errors.append(
            f"references/ totals {total} bytes (budget {MAX_REFERENCES_TOTAL_BYTES})."
        )


def main() -> int:
    errors: list[str] = []
    check_frontmatter(errors)
    check_router(errors)
    check_digest_sections(errors)
    check_citations(errors)
    check_internal_links(errors)
    check_size_budget(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Skill validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
