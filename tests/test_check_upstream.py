import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_upstream as cu

UPSTREAM = textwrap.dedent(
    """\
    # Awesome Falsehood

    ## Dates and Time

    - [Falsehoods about Time](https://example.com/time) - Classic.
    - [Brand New Article](https://example.com/new) - Not yet local.

    ## Cryptocurrency

    - [Pruned Section Link](https://example.com/crypto) - Ignored.

    ## Not A Content Section

    - [Badge](https://example.com/badge) - Ignored.
    """
)

LOCAL = textwrap.dedent(
    """\
    # Reference

    ## Dates and Time

    - [Falsehoods about Time](http://example.com/time/) - Same link, http + trailing slash.
    """
)


class TestExtractLinks:
    def test_skips_pruned_and_non_content_sections(self):
        links = cu.extract_links(UPSTREAM)
        assert set(links) == {"Dates and Time"}
        urls = [url for _, url in links["Dates and Time"]]
        assert urls == ["https://example.com/time", "https://example.com/new"]


class TestNormalizeUrl:
    def test_scheme_slash_case_insensitive(self):
        assert cu.normalize_url("http://Example.com/Time/") == cu.normalize_url(
            "https://example.com/time"
        )


class TestFindNewLinks:
    def test_reports_only_genuinely_new(self):
        new = cu.find_new_links(UPSTREAM, LOCAL)
        assert set(new) == {"Dates and Time"}
        assert new["Dates and Time"] == [("Brand New Article", "https://example.com/new")]

    def test_empty_when_in_sync(self):
        assert cu.find_new_links(LOCAL, UPSTREAM) == {}
