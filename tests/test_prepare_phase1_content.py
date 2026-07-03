import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import prepare_phase1_content as prep


class TestSlugify:
    def test_basic(self):
        assert prep.slugify("Falsehoods about Time") == "falsehoods-about-time"

    def test_strips_accents_and_punctuation(self):
        assert prep.slugify("Café “quoted” — naïve!") == "cafe-quoted-naive"

    def test_empty_falls_back(self):
        assert prep.slugify("“”") == "source"

    def test_truncates(self):
        assert len(prep.slugify("x" * 200)) <= 72


class TestCleanMarkdownText:
    def test_strips_links_and_formatting(self):
        text = "**Bold** [label](https://example.com) `code` ![img](https://x/y.png)"
        assert prep.clean_markdown_text(text) == "Bold label code img"

    def test_collapses_whitespace(self):
        assert prep.clean_markdown_text("a\n  b\t c") == "a b c"


class TestDescriptionFromBullet:
    def test_takes_text_after_dash(self):
        line = "- [Title](https://x) - The description part."
        assert prep.description_from_bullet(line) == "The description part."


class TestCanonicalFetchUrl:
    def test_github_blob_to_raw(self):
        url = "https://github.com/google/libphonenumber/blob/master/FALSEHOODS.md"
        assert (
            prep.canonical_fetch_url(url)
            == "https://raw.githubusercontent.com/google/libphonenumber/master/FALSEHOODS.md"
        )

    def test_gist_to_raw(self):
        url = "https://gist.github.com/rgs/6509585"
        assert prep.canonical_fetch_url(url) == "https://gist.githubusercontent.com/rgs/6509585/raw"

    def test_codeberg_src_to_raw(self):
        url = "https://codeberg.org/catseye/The-Dossier/src/branch/master/article/README.md"
        assert (
            prep.canonical_fetch_url(url)
            == "https://codeberg.org/catseye/The-Dossier/raw/branch/master/article/README.md"
        )

    def test_other_urls_pass_through(self):
        url = "https://example.com/a?b=c"
        assert prep.canonical_fetch_url(url) == url


class TestArchiveTargetUrl:
    def test_extracts_original(self):
        url = "https://web.archive.org/web/20200216181551/https://ericasadun.com/post/"
        assert prep.archive_target_url(url) == "https://ericasadun.com/post/"

    def test_non_archive_is_empty(self):
        assert prep.archive_target_url("https://example.com") == ""


def make_entry(url, title="Falsehoods about Widgets", section="Software Engineering"):
    entry = {
        "id": "test",
        "section": section,
        "topic": prep.TOPIC_BY_SECTION.get(section, "excluded"),
        "title": title,
        "link_label": title,
        "original_url": url,
        "fetch_url": prep.canonical_fetch_url(url),
    }
    entry["source_type"] = prep.classify_source_type(entry)
    return entry


class TestClassifySourceType:
    def test_video(self):
        assert make_entry("https://www.youtube.com/watch?v=x")["source_type"] == "video"

    def test_social_post(self):
        assert make_entry("https://twitter.com/a/status/1")["source_type"] == "social-post"

    def test_falsehood_article(self):
        assert make_entry("https://example.com/post")["source_type"] == "falsehood-article"

    def test_github_repository(self):
        entry = make_entry("https://github.com/google/libphonenumber", title="libphonenumber")
        assert entry["source_type"] == "github-repository"


class TestDecideInclusion:
    def test_falsehood_article_included(self):
        entry = make_entry("https://example.com/post")
        decision, _ = prep.decide_inclusion(entry)
        assert decision == "include"

    def test_video_demoted(self):
        entry = make_entry("https://www.youtube.com/watch?v=x")
        decision, _ = prep.decide_inclusion(entry)
        assert decision == "demote"

    def test_book_page_excluded(self):
        entry = make_entry("https://amazon.com/some-book", title="A Book")
        decision, _ = prep.decide_inclusion(entry)
        assert decision == "exclude"


class TestWaybackFallback:
    def test_wraps_normal_url(self):
        url = "https://medium.com/@x/post"
        assert prep.wayback_fallback_url(url) == f"https://web.archive.org/web/2/{url}"

    def test_skips_archive_urls(self):
        assert prep.wayback_fallback_url("https://web.archive.org/web/2020/https://x.com") == ""

    def test_run_curl_uses_wayback_on_failure(self, monkeypatch):
        calls = []

        def fake_fetch(entry, url):
            calls.append(url)
            if "web.archive.org" in url:
                return {"retrieval_status": "fetched", "raw_path": "sources/raw/x.html"}
            return {"retrieval_status": "http_403", "raw_path": ""}

        monkeypatch.setattr(prep, "fetch_attempt", fake_fetch)
        entry = {"id": "x", "fetch_url": "https://medium.com/@x/post"}
        result = prep.run_curl(entry)
        assert len(calls) == 2
        assert result["retrieval_status"] == "fetched_wayback"
        assert result["wayback_url"] == "https://web.archive.org/web/2/https://medium.com/@x/post"

    def test_run_curl_keeps_direct_success(self, monkeypatch):
        def fake_fetch(entry, url):
            return {"retrieval_status": "fetched", "raw_path": "sources/raw/x.html"}

        monkeypatch.setattr(prep, "fetch_attempt", fake_fetch)
        entry = {"id": "x", "fetch_url": "https://example.com/a"}
        result = prep.run_curl(entry)
        assert result["retrieval_status"] == "fetched"
        assert "wayback_url" not in result

    def test_run_curl_keeps_failure_when_wayback_fails(self, monkeypatch):
        def fake_fetch(entry, url):
            return {"retrieval_status": "http_403", "raw_path": ""}

        monkeypatch.setattr(prep, "fetch_attempt", fake_fetch)
        entry = {"id": "x", "fetch_url": "https://example.com/a"}
        result = prep.run_curl(entry)
        assert result["retrieval_status"] == "http_403"


class TestParseReferenceDoc:
    def test_parses_sections_and_skips_pruned(self, tmp_path, monkeypatch):
        doc = tmp_path / "reference.md"
        doc.write_text(
            textwrap.dedent(
                """\
                # Reference

                ## Dates and Time

                - [Falsehoods about Time](https://example.com/time) - Classic list.
                - [Two links](https://example.com/a) and [again](https://example.com/b) - Both count.
                - No link bullet.
                - [Anchor only](#section) - Skipped.

                ## Cryptocurrency

                - [Pruned](https://example.com/pruned) - Whole section pruned.

                ## Business

                - [`tax`](https://github.com/x/tax) - Pruned by title.
                """
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(prep, "REFERENCE_DOC", doc)
        entries = prep.parse_reference_doc()
        urls = [entry["original_url"] for entry in entries]
        assert "https://example.com/time" in urls
        assert "https://example.com/a" in urls and "https://example.com/b" in urls
        assert "https://example.com/pruned" not in urls
        assert "https://github.com/x/tax" not in urls
        ids = [entry["id"] for entry in entries]
        assert len(ids) == len(set(ids))
        for entry in entries:
            assert entry["decision"] in {"include", "demote", "exclude"}


class TestExtractChecklist:
    def test_picks_bullets_and_falsehood_lines(self):
        markdown = textwrap.dedent(
            """\
            ---
            id: "x"
            ---

            # Title

            - Time zones never change.
            - UTC is always enough for scheduling.

            Programmers assume clocks are monotonic.
            """
        )
        items = prep.extract_checklist(markdown, fallback="fallback text")
        assert "Time zones never change." in items
        assert any("monotonic" in item for item in items)

    def test_falls_back_when_empty(self):
        assert prep.extract_checklist("", "A fallback description.") == [
            "A fallback description."
        ]


class TestDedupe:
    def test_case_insensitive(self):
        assert prep.dedupe(["A b", "a B", "c"]) == ["A b", "c"]


class TestPreparedDirLocation:
    def test_prepared_dir_is_generated_intermediate(self):
        # The curated digests live in the skill references; the script's output
        # must stay under sources/ so a rebuild can never clobber curation.
        assert prep.PREPARED_DIR == prep.SOURCES_DIR / "prepared"
