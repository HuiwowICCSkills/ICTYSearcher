#!/usr/bin/env python3
"""ICTY official site adapter for ICTYSearcher."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from skillkit import HTTP, RetrievalError, clean, pdf_pages, result

PROG = "icty_search.py"
DESCRIPTION = "Search the official ICTY case and public legacy document site."
CACHE_DEFAULT = ".icty-cache"
FETCH_TIMEOUT_DEFAULT = 300

SEARCH_URL = "https://www.icty.org/en/search-results"
ROOT = "https://www.icty.org/"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/155.0.0.0 Safari/537.36"
)
RESULTS_PER_PAGE = 20


def _headers() -> dict[str, str]:
    return {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def make_http(args: argparse.Namespace) -> HTTP:
    return HTTP(
        args.cache,
        offline=args.offline,
        ttl=args.cache_ttl,
        timeout=args.timeout,
        user_agent=UA,
    )


def add_search_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=10, help="1..50 (default 10)")
    parser.add_argument("--offset", type=int, default=0, help=">= 0 (default 0)")


def add_fetch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text-out", help="Write extracted page text here")
    parser.add_argument("--pdf-out", help="Write a PDF response here")
    parser.add_argument("--max-mb", type=int, default=250, help="Maximum response size in MiB")


def _section(url: str) -> str:
    if "/en/case/" in url:
        return "case-page"
    if "/en/press/" in url:
        return "press-release"
    if "/en/indictment" in url or "/en/judgement" in url:
        return "document-page"
    return "other"


def search(query: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("A non-empty query is required")
    if not 1 <= args.limit <= 50:
        raise ValueError("limit must be 1..50")
    if args.offset < 0:
        raise ValueError("offset must be >= 0")
    page = args.offset // RESULTS_PER_PAGE
    within = args.offset % RESULTS_PER_PAGE
    soup, meta = http.soup(
        SEARCH_URL,
        {"as_q": query, "page": page},
        headers=_headers(),
    )
    anchors = soup.select(".search-results h3 a, .search-result h3 a")
    if not anchors:
        # A zero-hit page has no result list; distinguish it from a broken page by title.
        if "search results" not in (soup.title.get_text(" ", strip=True).lower() if soup.title else ""):
            raise RetrievalError("ICTY search results page lost its result list or title")
    rows = []
    for anchor in anchors:
        href = urljoin(meta["source_url"], anchor["href"])
        rows.append(
            result(
                anchor.get_text(" ", strip=True),
                href,
                "icty-site-search",
                "",
                section=_section(href),
                access="official ICTY site search result; page text must be fetched separately",
                content_scope="site search record, not the linked judgment or press release text",
            )
        )
    selected = rows[within : within + args.limit]
    total = len(rows) if anchors else 0
    return {
        "status": "ok" if rows or total == 0 else "no-results-in-queried-index",
        "query": query,
        "total": total,
        "results": selected,
        "pagination": {
            "offset": args.offset,
            "limit": args.limit,
            "page": page + 1,
            "page_size": RESULTS_PER_PAGE,
            "next_offset": args.offset + len(selected) if selected and len(anchors) == RESULTS_PER_PAGE else None,
        },
        "scope": "Official ICTY site search (cases, press releases and legacy pages); not a full-text judgment database",
        "evidence": http.evidence,
    }


def fetch(locator: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    parsed = urlparse(locator)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in {"www.icty.org", "icty.org"}:
        raise ValueError("fetch expects an https://www.icty.org/ URL")
    max_bytes = args.max_mb * 1024 * 1024
    body, meta = http.get(locator, headers=_headers())
    if len(body) > max_bytes:
        raise RetrievalError(f"Response exceeds --max-mb ({args.max_mb} MiB)")
    if body.startswith(b"%PDF"):
        pages = pdf_pages(body)
        text = "\n\n".join(f"@@PAGE {p['page']}@@\n{p['text']}" for p in pages)
        if args.pdf_out:
            Path(args.pdf_out).write_bytes(body)
        if args.text_out:
            Path(args.text_out).write_text(text, encoding="utf-8")
        return {
            "status": "ok",
            "url": meta["source_url"],
            "pages": len(pages),
            "needs_ocr": not any(p["text"].strip() for p in pages),
            "page_text": pages,
            "pdf_out": str(Path(args.pdf_out).resolve()) if args.pdf_out else None,
            "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
            "sha256": meta["sha256"],
            "retrieved_at": meta["retrieved_at"],
        }
    soup = BeautifulSoup(body, "html.parser")
    container = None
    for selector in ("article", "main", "#content", ".content", "body"):
        candidate = soup.select_one(selector)
        if candidate and len(candidate.get_text(" ", strip=True)) > 100:
            container = candidate
            break
    container = container or soup.body or soup
    for node in container.select("script, style, nav, header, footer, input, select, button, textarea, noscript"):
        node.decompose()
    text = container.get_text("\n", strip=True)
    if len(text) < 100:
        raise RetrievalError("Insufficient ICTY page text")
    links = []
    seen = set()
    for anchor in container.select("a[href]"):
        href = urljoin(meta["source_url"], anchor["href"])
        if href in seen:
            continue
        seen.add(href)
        links.append({"text": clean(anchor.get_text(" ", strip=True)), "url": href})
    if args.text_out:
        Path(args.text_out).write_text(text, encoding="utf-8")
    return {
        "status": "ok",
        "url": meta["source_url"],
        "title": clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
        "text": text,
        "text_characters": len(text),
        "document_links": links,
        "content_scope": "ICTY official page text; linked PDFs must be fetched separately",
        "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
        "sha256": meta["sha256"],
        "retrieved_at": meta["retrieved_at"],
    }


def doctor(args: argparse.Namespace) -> dict[str, Any]:
    checks = [
        {"check": "python", "ok": True, "detail": "Python runtime available"},
        {"check": "requests", "ok": True, "detail": "requests importable"},
        {"check": "beautifulsoup4", "ok": True, "detail": "bs4 importable"},
    ]
    if args.no_probe:
        return {"ok": True, "status": "ok (probes skipped)", "checks": checks}
    http = make_http(args)
    try:
        soup, meta = http.soup(SEARCH_URL, {"as_q": "Karadzic", "page": 0}, headers=_headers())
        anchors = soup.select(".search-results h3 a, .search-result h3 a")
        checks.append(
            {
                "check": "ICTY site search",
                "ok": bool(anchors),
                "results": len(anchors),
                "http_status": meta["http_status"],
                "bytes": meta["bytes"],
            }
        )
        ok = bool(anchors)
    except Exception as exc:
        checks.append({"check": "ICTY site search", "ok": False, "error": f"{type(exc).__name__}: {exc}"})
        ok = False
    return {"ok": ok, "status": "ok" if ok else "error", "checks": checks, "catalog": {"search_url": SEARCH_URL}}
