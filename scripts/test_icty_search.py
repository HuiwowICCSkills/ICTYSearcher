"""Offline tests for ICTYSearcher."""
from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import icty_adapter as adapter  # noqa: E402


class FakeHttp:
    def __init__(self, html):
        self.html = html
        self.evidence = []

    def soup(self, url, params=None, headers=None):
        return BeautifulSoup(self.html, "html.parser"), {
            "source_url": "https://www.icty.org/en/search-results",
            "http_status": 200, "content_type": "text/html", "bytes": 100,
            "retrieved_at": "2026-11-09T00:00:00Z", "sha256": "0" * 64,
        }


def args(**kwargs):
    base = dict(limit=2, offset=0, cache=".cache", offline=False, cache_ttl=0, timeout=30)
    base.update(kwargs)
    return argparse.Namespace(**base)


class IctyTests(unittest.TestCase):
    def test_search_parses_case_and_press_links(self):
        html = """
        <html><head><title>Search Results</title></head><body>
        <div class="search-results">
          <h3><a href="/en/case/karadzic">Karadžić (IT-95-5/18)</a></h3>
          <h3><a href="/en/press/statement">Statement</a></h3>
        </div></body></html>
        """
        out = adapter.search("Karadzic", args(), FakeHttp(html))
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["results"][0]["section"], "case-page")
        self.assertEqual(out["results"][1]["section"], "press-release")


if __name__ == "__main__":
    unittest.main()
