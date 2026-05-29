#!/usr/bin/env python3
"""Prepare the phase-1 falsehood source corpus.

This script intentionally does not create SKILL.md or skill metadata. It turns
the legacy Awesome Falsehood reference link index into a local source mirror,
normalized Markdown, agent-facing prepared topic notes, and a
retrieval/filtering report.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import html
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DOC = ROOT / "docs" / "awesome-falsehood-reference.md"
REFERENCE_DOC_REL = REFERENCE_DOC.relative_to(ROOT).as_posix()
SOURCES_DIR = ROOT / "sources"
RAW_DIR = SOURCES_DIR / "raw"
MARKDOWN_DIR = SOURCES_DIR / "markdown"
PREPARED_DIR = ROOT / "prepared"
REPORTS_DIR = ROOT / "reports"

LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")

CONTENT_SECTIONS = {
    "Meta",
    "Arts",
    "Business",
    "Cryptocurrency",
    "Dates and Time",
    "Education",
    "Emails",
    "Geography",
    "Human Identity",
    "Internationalization",
    "Management",
    "Multimedia",
    "Networks",
    "Phone Numbers",
    "Postal Addresses",
    "Science",
    "Society",
    "Software Engineering",
    "Transportation",
    "Typography",
    "Video Games",
    "Web",
}

PRUNED_SECTIONS = {
    "Arts",
    "Cryptocurrency",
    "Multimedia",
    "Transportation",
    "Video Games",
}

PRUNED_TITLES_BY_SECTION = {
    "Business": {"tax"},
    "Geography": {"top 5 most insane kanji place names in japan"},
    "Human Identity": {
        "falsehoods about families",
        "gay marriage: the database engineering perspective",
    },
    "Society": {"falsehoods about political appointments"},
}

EXCLUDED_SECTIONS = set()

TOPIC_BY_SECTION = {
    "Meta": "software-systems-data",
    "Business": "money-business",
    "Dates and Time": "time",
    "Education": "software-systems-data",
    "Emails": "contact-addressing",
    "Geography": "geography-location",
    "Human Identity": "identity-people",
    "Internationalization": "text-i18n-typography",
    "Management": "identity-people",
    "Networks": "web-networks",
    "Phone Numbers": "contact-addressing",
    "Postal Addresses": "contact-addressing",
    "Science": "measurement",
    "Society": "identity-people",
    "Software Engineering": "software-systems-data",
    "Typography": "text-i18n-typography",
    "Web": "web-networks",
}

TOPIC_TITLES = {
    "contact-addressing": "Contact and Addressing Falsehoods",
    "geography-location": "Geography and Location Falsehoods",
    "identity-people": "Identity and People Falsehoods",
    "measurement": "Measurement Falsehoods",
    "money-business": "Money and Business Falsehoods",
    "software-systems-data": "Software, Systems, and Data Falsehoods",
    "text-i18n-typography": "Text, Internationalization, and Typography Falsehoods",
    "time": "Time Falsehoods",
    "web-networks": "Web and Network Falsehoods",
}

GENERIC_IMPLICATIONS = {
    "time": [
        "Do not assume clock arithmetic is linear, stable, or independent of jurisdiction.",
        "Preserve the user intent separately from derived instants when future scheduling matters.",
        "Prefer maintained time-zone and calendar libraries over handcrafted offset logic.",
    ],
    "text-i18n-typography": [
        "Treat user-visible text as Unicode grapheme clusters, not bytes, code units, or code points.",
        "Avoid hard-coded English grammar, casing, collation, width, and direction assumptions.",
        "Use locale-aware libraries and test with multilingual, mixed-script, and malformed inputs.",
    ],
    "identity-people": [
        "Model identity attributes as changeable, optional, culturally variable, and sometimes non-unique.",
        "Avoid using names, gender, biometrics, or family relationships as stable identifiers.",
        "Keep validation permissive unless a specific downstream authority requires a narrower format.",
    ],
    "contact-addressing": [
        "Store contact data as user-provided structured fields plus normalized forms when needed.",
        "Avoid regex-only validation for email, phone, and postal addresses.",
        "Expect regional formats, missing components, multiple valid renderings, and delivery exceptions.",
    ],
    "money-business": [
        "Represent money with decimal/fixed-precision types and explicit currency metadata.",
        "Avoid assuming prices, currencies, inventory, and legal company names are simple strings or scalars.",
        "Keep business identifiers and monetary calculations auditable and resistant to injection-like data.",
    ],
    "geography-location": [
        "Treat places, coordinates, boundaries, weather, and map projections as contextual and time-varying.",
        "Carry coordinate reference systems and units explicitly when exchanging geospatial data.",
        "Avoid assuming names, addresses, and administrative regions map cleanly to one location.",
    ],
    "web-networks": [
        "Parse URLs, HTML, REST interactions, IP addresses, DNS, and IDNs with mature libraries.",
        "Expect normalization, encoding, redirects, caching, and transport behavior to differ by implementation.",
        "Design networked flows for latency, partial failure, retries, duplicate delivery, and inconsistent state.",
    ],
    "software-systems-data": [
        "Avoid assuming formats, versions, paths, caches, state machines, search, pagination, and identifiers are simple.",
        "Prefer specifications, battle-tested libraries, and property/fixture tests for tricky data surfaces.",
        "Make parsing, normalization, and comparison rules explicit and observable.",
    ],
    "measurement": [
        "Preserve units with values and avoid implicit conversion rules.",
        "Expect systems of measurement to vary by locale, discipline, and historical context.",
        "Test conversions, display, and parsing with boundary and mixed-unit examples.",
    ],
}

FALSEHOOD_KEYWORDS = (
    "assume",
    "assumes",
    "believe",
    "falsehood",
    "misconception",
    "myth",
    "not",
    "never",
    "always",
    "only",
    "must",
    "can't",
    "cannot",
    "should",
    "will",
    "won't",
)

NAVIGATION_NOISE = (
    "skip to content",
    "sign in",
    "sign up",
    "subscribe",
    "advertisement",
    "privacy policy",
    "cookie policy",
    "accept cookies",
    "share this",
    "open in app",
    "download",
    "github",
)

MAPBOX_TOKEN_RE = re.compile(rb"\b[sp]k\.eyJ[A-Za-z0-9._-]+")
MAPBOX_TOKEN_REPLACEMENT = b"[REDACTED_MAPBOX_TOKEN]"


def slugify(text: str, max_len: int = 72) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[`'\"“”‘’]", "", ascii_text)
    ascii_text = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return (ascii_text or "source")[:max_len].strip("-") or "source"


def clean_markdown_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"[*_]{1,3}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -")


def description_from_bullet(line: str) -> str:
    text = clean_markdown_text(line.removeprefix("- "))
    if " - " in text:
        return text.split(" - ", 1)[1].strip()
    return text.strip()


def link_context_title(line: str, link_index: int, label: str, first_label: str) -> str:
    before = line.split("[", 1)[0].removeprefix("- ").strip()
    base = before.rstrip(":").strip()
    label = clean_markdown_text(label)
    first_label = clean_markdown_text(first_label)
    if base and label.startswith("#"):
        return f"{base} {label}"
    if link_index == 1:
        return label or base or "Untitled source"
    if base and len(label) <= 8:
        return f"{base} {label}"
    if label:
        return f"{first_label}: {label}"
    return f"{first_label}: supplementary source"


def is_pruned_source(section: str, title: str) -> bool:
    if section in PRUNED_SECTIONS:
        return True
    pruned_titles = PRUNED_TITLES_BY_SECTION.get(section, set())
    return clean_markdown_text(title).lower() in pruned_titles


def parse_reference_doc() -> list[dict]:
    entries: list[dict] = []
    current_section = ""
    bullet_number_by_section: dict[str, int] = {}
    used_ids: set[str] = set()

    for lineno, line in enumerate(REFERENCE_DOC.read_text(encoding="utf-8").splitlines(), 1):
        heading = HEADING_RE.match(line)
        if heading:
            current_section = heading.group(1).strip()
            continue
        if current_section in PRUNED_SECTIONS:
            continue
        if current_section not in CONTENT_SECTIONS or not line.startswith("- "):
            continue
        links = list(LINK_RE.finditer(line))
        if not links:
            continue

        bullet_number_by_section[current_section] = bullet_number_by_section.get(current_section, 0) + 1
        bullet_number = bullet_number_by_section[current_section]
        first_label = links[0].group(1)
        description = description_from_bullet(line)

        for link_index, match in enumerate(links, 1):
            label = clean_markdown_text(match.group(1))
            url = html.unescape(match.group(2).strip())
            if url.startswith("#") or not url.startswith(("http://", "https://")):
                continue
            title = link_context_title(line, link_index, label, first_label)
            if is_pruned_source(current_section, title):
                continue
            base_id = slugify(f"{current_section}-{bullet_number:03d}-{link_index:02d}-{title}")
            source_id = base_id
            suffix = 2
            while source_id in used_ids:
                source_id = f"{base_id}-{suffix}"
                suffix += 1
            used_ids.add(source_id)
            entry = {
                "id": source_id,
                "section": current_section,
                "topic": TOPIC_BY_SECTION.get(current_section, "excluded"),
                "title": title,
                "link_label": label,
                "original_url": url,
                "fetch_url": canonical_fetch_url(url),
                "resolved_url": "",
                "archive_target_url": archive_target_url(url),
                "reference_line": lineno,
                "reference_bullet": clean_markdown_text(line.removeprefix("- ")),
                "description": description,
                "link_index_in_bullet": link_index,
            }
            entry["source_type"] = classify_source_type(entry)
            decision, rationale = decide_inclusion(entry)
            entry["decision"] = decision
            entry["relevance_rationale"] = rationale
            entry["license_rights_note"] = license_note(entry)
            entries.append(entry)
    return entries


def archive_target_url(url: str) -> str:
    parsed = urlparse(url)
    if "web.archive.org" not in parsed.netloc:
        return ""
    match = re.match(r"^/web/\d+/(.+)$", parsed.path)
    if not match:
        return ""
    return match.group(1)


def canonical_fetch_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    if host == "github.com":
        parts = path.strip("/").split("/")
        if len(parts) >= 5 and parts[2] == "blob":
            owner, repo, _, branch = parts[:4]
            rest = "/".join(parts[4:])
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{rest}"
    if host == "gist.github.com":
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return f"https://gist.githubusercontent.com/{parts[0]}/{parts[1]}/raw"
    if host == "codeberg.org":
        parts = path.strip("/").split("/")
        if len(parts) >= 6 and parts[2] == "src" and parts[3] == "branch":
            owner, repo, _, _, branch = parts[:5]
            rest = "/".join(parts[5:])
            return f"https://codeberg.org/{owner}/{repo}/raw/branch/{branch}/{rest}"
    return url


def classify_source_type(entry: dict) -> str:
    url = entry["original_url"]
    fetch_url = entry.get("fetch_url") or url
    title = entry["title"].lower()
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    image_exts = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
    if path.endswith(image_exts):
        return "image"
    if "youtube.com" in host or "youtu.be" in host:
        return "video"
    if any(social in host for social in ("twitter.com", "x.com", "xcancel.com", "nitter.")):
        return "social-post"
    if "web.archive.org" in host:
        return "web-archive"
    if "gist.github" in host:
        return "gist"
    if "raw.githubusercontent.com" in urlparse(fetch_url).netloc.lower():
        return "github-file"
    if host == "github.com":
        if "/blob/" in path:
            return "github-file"
        return "github-repository"
    if path.endswith((".md", ".markdown")):
        return "markdown"
    if path.endswith(".xml"):
        return "xml"
    if "wikipedia.org" in host:
        return "encyclopedia"
    if any(domain in host for domain in ("iana.org", "unicode.org", "hl7.org", "developer.apple.com", "usps.com", "ddex.net", "musicbrainz.org")):
        return "standard-or-reference"
    if "amazon.com" in host:
        return "book-or-commerce-page"
    if "fosdem.org" in host:
        return "conference-page"
    if "0.30000000000000004.com" in host:
        return "interactive-reference"
    if "falsehood" in title or "myth" in title or "misconception" in title:
        return "falsehood-article"
    return "article"


def decide_inclusion(entry: dict) -> tuple[str, str]:
    section = entry["section"]
    title = entry["title"].lower()
    source_type = entry["source_type"]
    url = entry["original_url"].lower()

    if section in EXCLUDED_SECTIONS:
        return "exclude", f"{section} is narrow or low-utility for broad software-agent work under the balanced filter."

    if source_type == "book-or-commerce-page":
        return "exclude", "Book/commerce citation for an anecdote; not a practical falsehood source for agents."

    if source_type in {"video", "social-post", "image"}:
        return "demote", f"{source_type} is kept as metadata-only unless extractable text is available."

    if source_type == "standard-or-reference":
        if "personal names" in title:
            return "include", "This reference contains directly actionable name-modeling guidance."
        return "demote", "Standards/reference pages are mirrored for lookup but are too broad for direct checklist distillation."

    if any(token in title for token in ("libphonenumber", "libaddressinput", "libvldmail", "addressing", "postal-address", " tax", "`tax`")):
        return "demote", "Library/tool link is metadata-only support material."

    if "awesome unicode" in title or "big list of naughty strings" in title or "i18n testing data" in title:
        return "demote", "Large repository/corpus is useful test data but not direct falsehood guidance."

    if source_type == "github-repository":
        if "falsehood" in title:
            return "include", "Repository appears to contain direct falsehood guidance rather than only library/tooling context."
        return "demote", "Repository/library link is useful as tooling context but not a falsehood article to distill."

    if "the system can" in title or "minutiae of company names" in title or "content tagging systems" in title:
        return "demote", "Short social anecdote is relevant but not reliably extractable as standalone guidance."

    if "xkcd" in title:
        return "demote", "Comic/image example is useful metadata but not text content to distill."

    if "problem with time & timezones" in title or "internationalis" in title or "maddening mess" in title or "hi! my name" in title:
        return "demote", "Video or talk page is kept as metadata-only unless transcript text is available."

    if "cldr currency definitions" in title or "time zone database" in title or "usps postal addressing standards" in title:
        return "demote", "Dataset/specification is mirrored for lookup but not distilled as a falsehood article."

    if "source:" in title:
        return "exclude", "Source citation rather than falsehood material."

    if "falsehood" in title or "fallacies" in title or "myth" in title or "misconception" in title:
        return "include", "Falsehood-oriented source with broadly applicable implementation risk."

    if section in {
        "Business",
        "Dates and Time",
        "Education",
        "Emails",
        "Geography",
        "Human Identity",
        "Internationalization",
        "Management",
        "Networks",
        "Phone Numbers",
        "Postal Addresses",
        "Science",
        "Society",
        "Software Engineering",
        "Typography",
        "Web",
    }:
        return "include", f"{section} topic maps to common software-agent data, parsing, validation, or modeling work."

    return "exclude", "Does not meet the balanced broad-utility threshold."


def license_note(entry: dict) -> str:
    source_type = entry["source_type"]
    host = urlparse(entry["original_url"]).netloc.lower()
    if source_type in {"github-file", "github-repository", "gist"}:
        return "Check repository or gist license before redistribution; mirrored locally for phase-1 review."
    if source_type == "web-archive":
        return "Archived third-party content; original rights apply. Preserve citation and review before bundling."
    if source_type in {"video", "social-post", "image", "book-or-commerce-page"}:
        return "Third-party media/page; metadata only unless terms permit reuse."
    if "wikipedia.org" in host:
        return "Wikipedia content typically uses CC BY-SA/GFDL terms; verify page-specific license before redistribution."
    if source_type == "standard-or-reference":
        return "Official reference/specification; use as cited reference and verify redistribution terms."
    return "Third-party article; mirrored locally for review. Summarize or verify license before bundling."


def path_for_raw(entry: dict, content_type: str = "") -> Path:
    ext = extension_for(entry, content_type)
    return RAW_DIR / f"{entry['id']}{ext}"


def extension_for(entry: dict, content_type: str = "") -> str:
    parsed = urlparse(entry.get("fetch_url") or entry["original_url"])
    guessed = Path(parsed.path).suffix.lower()
    if guessed in {".md", ".markdown", ".html", ".htm", ".xml", ".txt", ".json", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}:
        return ".md" if guessed == ".markdown" else guessed
    if content_type:
        guessed_by_type = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
        if guessed_by_type:
            if guessed_by_type == ".jpe":
                return ".jpg"
            return guessed_by_type
    if entry["source_type"] in {"github-file", "gist", "markdown"}:
        return ".md"
    if entry["source_type"] == "xml":
        return ".xml"
    if entry["source_type"] == "image":
        return ".bin"
    return ".html"


def run_curl(entry: dict) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    headers_path = RAW_DIR / f"{entry['id']}.headers"
    temp_path = RAW_DIR / f"{entry['id']}.download"
    url = entry["fetch_url"]
    command = [
        "curl",
        "-L",
        "--silent",
        "--show-error",
        "--max-time",
        "45",
        "--connect-timeout",
        "12",
        "--retry",
        "1",
        "-A",
        "Mozilla/5.0 (compatible; falsehood-phase1-prep/1.0)",
        "-D",
        str(headers_path),
        "-o",
        str(temp_path),
        "-w",
        "%{http_code}\t%{url_effective}\t%{content_type}",
        url,
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.strip()
    parts = stdout.split("\t") if stdout else []
    http_status = parts[0] if len(parts) >= 1 else "000"
    resolved_url = parts[1] if len(parts) >= 2 else ""
    content_type = parts[2] if len(parts) >= 3 else ""
    raw_path = path_for_raw(entry, content_type)
    if temp_path.exists():
        temp_path.replace(raw_path)

    if raw_path.exists():
        redact_sensitive_tokens(raw_path)
    size = raw_path.stat().st_size if raw_path.exists() else 0
    status_code = int(http_status) if http_status.isdigit() else 0
    if result.returncode == 0 and 200 <= status_code < 400 and size > 0:
        retrieval_status = "fetched"
    elif result.returncode == 0 and size > 0:
        retrieval_status = f"http_{http_status}"
    else:
        retrieval_status = f"failed: {result.stderr.strip() or 'curl failed'}"

    entry.update(
        {
            "resolved_url": resolved_url,
            "http_status": http_status,
            "content_type": content_type,
            "retrieval_status": retrieval_status,
            "raw_path": relative_path(raw_path) if raw_path.exists() else "",
            "headers_path": relative_path(headers_path) if headers_path.exists() else "",
            "raw_bytes": size,
        }
    )
    return entry


def redact_sensitive_tokens(path: Path) -> int:
    data = path.read_bytes()
    redacted, count = MAPBOX_TOKEN_RE.subn(MAPBOX_TOKEN_REPLACEMENT, data)
    if count:
        path.write_bytes(redacted)
    return count


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def decode_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def convert_entry(entry: dict) -> dict:
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    md_path = MARKDOWN_DIR / f"{entry['id']}.md"
    raw_rel = entry.get("raw_path", "")
    if not raw_rel:
        entry["markdown_path"] = ""
        return entry

    raw_path = ROOT / raw_rel
    source_type = entry["source_type"]
    ext = raw_path.suffix.lower()
    content_type = entry.get("content_type", "")
    metadata = source_metadata_block(entry)

    if source_type == "image" or ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bin"}:
        body = f"{metadata}\n\nImage/media source mirrored at `{relative_path(raw_path)}`. No text extraction was attempted.\n"
    elif ext in {".md", ".txt"} or source_type in {"github-file", "gist", "markdown"}:
        body = f"{metadata}\n\n{decode_text(raw_path).strip()}\n"
    elif ext == ".xml" or "xml" in content_type:
        body = f"{metadata}\n\n```xml\n{decode_text(raw_path).strip()}\n```\n"
    else:
        converted = pandoc_html_to_markdown(raw_path)
        if not converted:
            converted = fallback_html_to_markdown(raw_path)
        body = f"{metadata}\n\n{clean_converted_markdown(converted).strip()}\n"

    md_path.write_text(body.rstrip() + "\n", encoding="utf-8")
    entry["markdown_path"] = relative_path(md_path)
    return entry


def source_metadata_block(entry: dict) -> str:
    fields = {
        "id": entry["id"],
        "title": entry["title"],
        "section": entry["section"],
        "decision": entry["decision"],
        "source_type": entry["source_type"],
        "original_url": entry["original_url"],
        "resolved_url": entry.get("resolved_url") or entry.get("fetch_url") or "",
        "retrieval_status": entry.get("retrieval_status", ""),
        "license_rights_note": entry.get("license_rights_note", ""),
    }
    lines = ["---"]
    lines.extend(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items())
    lines.append("---")
    return "\n".join(lines)


def pandoc_html_to_markdown(path: Path) -> str:
    if not shutil.which("pandoc"):
        return ""
    try:
        result = subprocess.run(
            ["pandoc", "-f", "html", "-t", "gfm", "--wrap=none", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=40,
        )
    except subprocess.TimeoutExpired:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def fallback_html_to_markdown(path: Path) -> str:
    text = decode_text(path)
    text = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", text)
    text = re.sub(r"(?is)</(h[1-6]|p|li|blockquote|pre|tr|div)>", "\n", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_converted_markdown(text: str) -> str:
    cleaned_lines: list[str] = []
    blank_seen = False
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            if not blank_seen:
                cleaned_lines.append("")
            blank_seen = True
            continue
        blank_seen = False
        if len(stripped) <= 40 and any(noise == lower for noise in NAVIGATION_NOISE):
            continue
        if stripped.startswith("[!") or stripped.startswith("!["):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def extract_checklist(markdown: str, fallback: str) -> list[str]:
    markdown = strip_source_metadata(markdown)
    candidates: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("---") or line.startswith("#"):
            continue
        if re.match(r"^[-*+]\s+", line) or re.match(r"^\d+[.)]\s+", line):
            item = re.sub(r"^[-*+]\s+|^\d+[.)]\s+", "", line).strip()
            item = clean_prepared_item(item)
            if is_useful_falsehood_item(item):
                candidates.append(item)
        elif len(line) < 180 and any(keyword in line.lower() for keyword in FALSEHOOD_KEYWORDS):
            item = clean_prepared_item(line)
            if is_useful_falsehood_item(item):
                candidates.append(item)
        if len(candidates) >= 14:
            break
    if not candidates and fallback:
        candidates.append(clean_prepared_item(fallback))
    return dedupe(candidates)[:12]


def clean_prepared_item(text: str) -> str:
    text = re.sub(r"\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\\", "")
    text = re.sub(r"\s+", " ", text).strip(" -*_`")
    return text[:260].rstrip()


def is_useful_falsehood_item(item: str) -> bool:
    if len(item) < 8:
        return False
    lower = item.lower()
    if any(noise in lower for noise in ("cookie", "privacy policy", "advertisement", "skip to", "sign in")):
        return False
    if item.count("|") > 4:
        return False
    return True


def extract_examples(markdown: str, fallback: str) -> list[str]:
    markdown = strip_source_metadata(markdown)
    examples: list[str] = []
    for raw_line in markdown.splitlines():
        line = clean_prepared_item(raw_line)
        if not line or len(line) < 18:
            continue
        lower = line.lower()
        if any(token in lower for token in ("for example", "e.g.", "example", "such as", "can be", "allowed", "valid", "invalid")):
            examples.append(line)
        if len(examples) >= 8:
            break
    if not examples and fallback:
        examples.append(clean_prepared_item(fallback))
    return dedupe(examples)[:6]


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def strip_source_metadata(markdown: str) -> str:
    if not markdown.startswith("---"):
        return markdown
    parts = markdown.split("---", 2)
    if len(parts) == 3:
        return parts[2].lstrip()
    return markdown


def load_markdown_for(entry: dict) -> str:
    md_rel = entry.get("markdown_path")
    if not md_rel:
        return ""
    path = ROOT / md_rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_prepared_files(entries: list[dict]) -> None:
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        if entry["decision"] in {"include", "demote"} and entry["topic"] in TOPIC_TITLES:
            grouped.setdefault(entry["topic"], []).append(entry)

    overview_lines = [
        "# Prepared Falsehood Corpus Overview",
        "",
        f"Phase-1 agent-facing notes generated from `{REFERENCE_DOC_REL}` linked sources.",
        "",
        "This directory intentionally contains prepared content only; it is not a skill definition.",
        "",
        "## Topics",
        "",
    ]
    for topic in sorted(grouped):
        topic_path = f"{topic}.md"
        count_include = sum(1 for e in grouped[topic] if e["decision"] == "include")
        count_demote = sum(1 for e in grouped[topic] if e["decision"] == "demote")
        overview_lines.append(f"- [{TOPIC_TITLES[topic]}]({topic_path}) - {count_include} included, {count_demote} metadata-only.")
    (PREPARED_DIR / "00-overview.md").write_text("\n".join(overview_lines).rstrip() + "\n", encoding="utf-8")

    for topic, topic_entries in sorted(grouped.items()):
        lines = [
            f"# {TOPIC_TITLES[topic]}",
            "",
            "Each source is normalized for agent consumption with source metadata, extracted checklist items, implementation implications, examples, and citation.",
            "",
        ]
        for entry in sorted(topic_entries, key=lambda e: (e["section"], e["reference_line"], e["link_index_in_bullet"])):
            lines.extend(prepared_block(entry))
        (PREPARED_DIR / f"{topic}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def prepared_block(entry: dict) -> list[str]:
    markdown = load_markdown_for(entry)
    checklist = extract_checklist(markdown, entry.get("description", ""))
    examples = extract_examples(markdown, entry.get("description", ""))
    implications = GENERIC_IMPLICATIONS.get(entry["topic"], GENERIC_IMPLICATIONS["software-systems-data"])

    lines = [
        f"## {entry['title']}",
        "",
        f"- **Source id:** `{entry['id']}`",
        f"- **Section:** {entry['section']}",
        f"- **Decision:** {entry['decision']}",
        f"- **Source type:** {entry['source_type']}",
        f"- **Original source:** {entry['original_url']}",
        f"- **Local mirror:** `{entry.get('markdown_path') or entry.get('raw_path') or 'unavailable'}`",
        f"- **Rights note:** {entry['license_rights_note']}",
        "",
    ]
    if entry["decision"] == "demote":
        lines.extend(
            [
                "### Metadata-Only Rationale",
                "",
                f"- {entry['relevance_rationale']}",
                "",
            ]
        )
    lines.extend(["### Falsehood Checklist", ""])
    for item in checklist:
        lines.append(f"- {item}")
    lines.extend(["", "### Agent Implementation Implications", ""])
    for item in implications:
        lines.append(f"- {item}")
    lines.extend(["", "### Edge Cases and Examples", ""])
    for item in examples:
        lines.append(f"- {item}")
    lines.extend(["", "### Citation", "", f"- {entry['title']}: {entry['original_url']}", ""])
    return lines


def write_manifest(entries: list[dict]) -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "reference_doc": REFERENCE_DOC_REL,
        "entry_count": len(entries),
        "entries": entries,
    }
    (SOURCES_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Manifest",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "| ID | Section | Decision | Type | Status | Title |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        title = entry["title"].replace("|", "\\|")
        lines.append(
            f"| `{entry['id']}` | {entry['section']} | {entry['decision']} | {entry['source_type']} | {entry.get('retrieval_status', '')} | {title} |"
        )
    (SOURCES_DIR / "manifest.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_report(entries: list[dict], validation: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).isoformat()
    by_decision = count_by(entries, "decision")
    by_section = count_by(entries, "section")
    by_status = count_by(entries, "retrieval_status")
    failures = [e for e in entries if not e.get("retrieval_status", "").startswith("fetched")]
    license_notes = count_by(entries, "license_rights_note")

    lines = [
        "# Phase 1 Retrieval and Filtering Report",
        "",
        f"Generated: {generated}",
        "",
        "## Summary",
        "",
        f"- Reference content links represented: {len(entries)}",
        f"- Included: {by_decision.get('include', 0)}",
        f"- Metadata-only/demoted: {by_decision.get('demote', 0)}",
        f"- Excluded: {by_decision.get('exclude', 0)}",
        f"- Validation status: {'passed' if validation['passed'] else 'failed'}",
        "",
        "## Counts by Section",
        "",
    ]
    for key, count in sorted(by_section.items()):
        lines.append(f"- {key}: {count}")
    lines.extend(["", "## Counts by Retrieval Status", ""])
    for key, count in sorted(by_status.items()):
        lines.append(f"- {key or 'not attempted'}: {count}")
    lines.extend(["", "## Failed or Non-200 Retrievals", ""])
    if failures:
        for entry in failures:
            lines.append(f"- `{entry['id']}` {entry['title']} - {entry.get('retrieval_status', 'unknown')} - {entry['original_url']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Rights and License Notes", ""])
    for note, count in sorted(license_notes.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"- {count}: {note}")
    lines.extend(["", "## Validation Details", ""])
    if validation["errors"]:
        for error in validation["errors"]:
            lines.append(f"- ERROR: {error}")
    else:
        lines.append("- No validation errors.")
    if validation["warnings"]:
        for warning in validation["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- No validation warnings.")
    (REPORTS_DIR / "phase1-retrieval-report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def count_by(entries: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        value = str(entry.get(key, ""))
        counts[value] = counts.get(value, 0) + 1
    return counts


def validate(entries: list[dict]) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    ids = [entry["id"] for entry in entries]
    if len(ids) != len(set(ids)):
        errors.append("Manifest IDs are not unique.")

    for entry in entries:
        if entry["decision"] not in {"include", "exclude", "demote"}:
            errors.append(f"{entry['id']} has invalid decision {entry['decision']!r}.")
        if not entry.get("retrieval_status"):
            errors.append(f"{entry['id']} has no retrieval status.")
        if entry.get("retrieval_status", "").startswith("fetched"):
            raw_path = ROOT / entry.get("raw_path", "")
            markdown_path = ROOT / entry.get("markdown_path", "")
            if not raw_path.exists() or raw_path.stat().st_size == 0:
                errors.append(f"{entry['id']} fetched but raw file is missing or empty.")
            if not markdown_path.exists() or markdown_path.stat().st_size == 0:
                errors.append(f"{entry['id']} fetched but converted Markdown is missing or empty.")
        elif not entry.get("retrieval_status", "").startswith(("failed:", "http_")):
            warnings.append(f"{entry['id']} has unusual retrieval status {entry.get('retrieval_status')!r}.")

    for path in PREPARED_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name != "00-overview.md":
            for heading in ("### Falsehood Checklist", "### Agent Implementation Implications", "### Edge Cases and Examples", "### Citation"):
                if heading not in text:
                    errors.append(f"{relative_path(path)} is missing {heading}.")
        if re.search(r"(?i)accept cookies|skip to content\s*$|advertisement", text):
            warnings.append(f"{relative_path(path)} may contain navigation or ad boilerplate.")

    for topic in TOPIC_TITLES:
        path = PREPARED_DIR / f"{topic}.md"
        if any(e["topic"] == topic and e["decision"] in {"include", "demote"} for e in entries) and not path.exists():
            errors.append(f"Prepared topic file missing: {relative_path(path)}.")

    return {"passed": not errors, "errors": errors, "warnings": warnings}


def clean_generated_dirs() -> None:
    for path in (SOURCES_DIR, PREPARED_DIR, REPORTS_DIR):
        if path.exists():
            shutil.rmtree(path)
    for path in (RAW_DIR, MARKDOWN_DIR, PREPARED_DIR, REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def prepare(fetch_workers: int) -> int:
    if not REFERENCE_DOC.exists():
        print(f"Missing reference doc: {REFERENCE_DOC}", file=sys.stderr)
        return 2

    clean_generated_dirs()
    entries = parse_reference_doc()
    print(f"Parsed {len(entries)} reference content links.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=fetch_workers) as executor:
        future_by_id = {executor.submit(run_curl, entry): entry["id"] for entry in entries}
        fetched: list[dict] = []
        for completed, future in enumerate(concurrent.futures.as_completed(future_by_id), 1):
            entry = future.result()
            fetched.append(entry)
            if completed % 10 == 0 or completed == len(entries):
                print(f"Fetched {completed}/{len(entries)} sources.")

    entries_by_id = {entry["id"]: entry for entry in fetched}
    ordered_entries = [entries_by_id[entry["id"]] for entry in entries]

    converted: list[dict] = []
    for entry in ordered_entries:
        converted.append(convert_entry(entry))
    write_manifest(converted)
    write_prepared_files(converted)
    validation = validate(converted)
    write_report(converted, validation)

    print(f"Wrote {relative_path(SOURCES_DIR / 'manifest.json')}.")
    print(f"Wrote {relative_path(REPORTS_DIR / 'phase1-retrieval-report.md')}.")
    print(f"Validation {'passed' if validation['passed'] else 'failed'} with {len(validation['errors'])} errors and {len(validation['warnings'])} warnings.")
    return 0 if validation["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-workers", type=int, default=6, help="Concurrent fetch workers.")
    args = parser.parse_args()
    return prepare(max(1, args.fetch_workers))


if __name__ == "__main__":
    raise SystemExit(main())
