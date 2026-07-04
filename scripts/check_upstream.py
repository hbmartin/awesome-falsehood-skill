#!/usr/bin/env python3
"""Report falsehood links present upstream but missing from this repo.

Fetches the upstream Awesome Falsehood readme (kdeldycke/awesome-falsehood),
extracts content links section by section, and diffs them against the local
rebuild input at docs/awesome-falsehood-reference.md. Sections and titles this
project intentionally prunes are skipped, so output is only genuinely new
material worth distilling into the skill digests.

Prints a Markdown bullet list of new links (grouped by section) to stdout, or
nothing when the repo is up to date. Exit code is 0 either way; pass
--fail-on-new to exit 1 when new links exist (useful for CI gating).
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prepare_phase1_content as prep

UPSTREAM_README_URL = (
    "https://raw.githubusercontent.com/kdeldycke/awesome-falsehood/main/readme.md"
)


def extract_links(text: str) -> dict[str, list[tuple[str, str]]]:
    """Return {section: [(title, url), ...]} for content sections, minus pruned entries."""
    links: dict[str, list[tuple[str, str]]] = {}
    current_section = ""
    for line in text.splitlines():
        heading = prep.HEADING_RE.match(line)
        if heading:
            current_section = heading.group(1).strip()
            continue
        if current_section not in prep.CONTENT_SECTIONS:
            continue
        if current_section in prep.PRUNED_SECTIONS:
            continue
        if not line.startswith("- "):
            continue
        for match in prep.LINK_RE.finditer(line):
            title = prep.clean_markdown_text(match.group(1))
            url = match.group(2).strip()
            if not url.startswith(("http://", "https://")):
                continue
            if prep.is_pruned_source(current_section, title):
                continue
            links.setdefault(current_section, []).append((title, url))
    return links


def normalize_url(url: str) -> str:
    return url.rstrip("/").replace("http://", "https://").lower()


def fetch_upstream(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def find_new_links(upstream_text: str, local_text: str) -> dict[str, list[tuple[str, str]]]:
    local_urls = {
        normalize_url(url)
        for entries in extract_links(local_text).values()
        for _, url in entries
    }
    new: dict[str, list[tuple[str, str]]] = {}
    for section, entries in extract_links(upstream_text).items():
        for title, url in entries:
            if normalize_url(url) not in local_urls:
                new.setdefault(section, []).append((title, url))
    return new


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-url", default=UPSTREAM_README_URL)
    parser.add_argument(
        "--fail-on-new",
        action="store_true",
        help="Exit 1 when new upstream links are found.",
    )
    args = parser.parse_args()

    local_text = prep.REFERENCE_DOC.read_text(encoding="utf-8")
    upstream_text = fetch_upstream(args.upstream_url)
    new = find_new_links(upstream_text, local_text)

    if not new:
        print("", end="")
        return 0

    lines = [
        "New links found in [kdeldycke/awesome-falsehood](https://github.com/kdeldycke/awesome-falsehood)",
        "that are not yet in `docs/awesome-falsehood-reference.md`:",
        "",
    ]
    for section in sorted(new):
        lines.append(f"### {section}")
        lines.append("")
        for title, url in new[section]:
            lines.append(f"- [{title}]({url})")
        lines.append("")
    lines.append(
        "To fold one in: add it to `docs/awesome-falsehood-reference.md`, add a keyed entry "
        "to `skill/avoid-software-falsehoods/references/source-index.md`, and distill its "
        "unique guidance into the matching topic digest."
    )
    print("\n".join(lines))
    return 1 if args.fail_on_new else 0


if __name__ == "__main__":
    raise SystemExit(main())
