"""QB-17 acceptance: arXiv pagination, dedup, and the processed registry."""

import urllib.parse
from datetime import date
from pathlib import Path

import pytest

from quantbench_crew.models import Paper
from quantbench_crew.tools.arxiv_tool import (
    ProcessedRegistry,
    _arxiv_query_url,
    search_arxiv,
)


def _entry(n: int) -> str:
    aid = f"2501.{n:05d}"
    return f"""
  <entry>
    <id>http://arxiv.org/abs/{aid}v1</id>
    <title>Paper {n}</title>
    <summary>Abstract for paper {n}.</summary>
    <author><name>Author {n}</name></author>
    <category term="q-fin.PM"/>
    <published>2025-01-0{(n % 9) + 1}T00:00:00Z</published>
    <link title="pdf" href="http://arxiv.org/pdf/{aid}v1" type="application/pdf"/>
  </entry>"""


def _feed(entries: list[int]) -> bytes:
    body = "".join(_entry(n) for n in entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        f"{body}</feed>"
    ).encode("utf-8")


def _paged_fetcher(all_ids: list[int]):
    """Serve arXiv-style pages keyed by the URL's start/max_results params."""

    calls = {"count": 0}

    def fetch(url: str) -> bytes:
        calls["count"] += 1
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        start = int(params["start"][0])
        size = int(params["max_results"][0])
        return _feed(all_ids[start : start + size])

    return fetch, calls


def test_search_arxiv_paginates_across_pages() -> None:
    fetch, calls = _paged_fetcher([1, 2, 3, 4, 5])

    papers = search_arxiv("momentum", max_results=5, fetcher=fetch, page_size=2, delay=0.0)

    assert [p.title for p in papers] == [f"Paper {n}" for n in (1, 2, 3, 4, 5)]
    assert calls["count"] == 3  # pages at start 0, 2, 4


def test_search_arxiv_dedups_repeated_ids_across_pages() -> None:
    # Page boundaries overlap on id 2; the result set must not repeat it.
    def fetch(url: str) -> bytes:
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        start = int(params["start"][0])
        return _feed([1, 2] if start == 0 else [2, 3])

    papers = search_arxiv("x", max_results=4, fetcher=fetch, page_size=2, delay=0.0)

    titles = [p.title for p in papers]
    assert titles == ["Paper 1", "Paper 2", "Paper 3"]
    assert len(titles) == len(set(titles))


def test_search_arxiv_stops_on_short_page() -> None:
    fetch, calls = _paged_fetcher([1, 2, 3])  # only 3 available, ask for 10

    papers = search_arxiv("x", max_results=10, fetcher=fetch, page_size=5, delay=0.0)

    assert len(papers) == 3
    assert calls["count"] == 1  # short first page ends pagination


def test_first_page_failure_falls_back_to_placeholders() -> None:
    def fetch(url: str) -> bytes:
        raise OSError("network down")

    papers = search_arxiv("x", max_results=3, fetcher=fetch, page_size=2, delay=0.0)

    assert len(papers) == 3
    assert all(p.source == "arxiv-placeholder" for p in papers)


def test_later_page_failure_returns_partial() -> None:
    def fetch(url: str) -> bytes:
        start = int(urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["start"][0])
        if start == 0:
            return _feed([1, 2])
        raise OSError("dropped")

    papers = search_arxiv("x", max_results=6, fetcher=fetch, page_size=2, delay=0.0)

    assert [p.title for p in papers] == ["Paper 1", "Paper 2"]
    assert all(p.source == "arxiv" for p in papers)


def test_query_url_includes_date_window() -> None:
    url = _arxiv_query_url("momentum", start_date=date(2025, 1, 1), end_date=date(2025, 6, 30))
    decoded = urllib.parse.unquote_plus(url)

    assert "submittedDate:[202501010000 TO 202506302359]" in decoded
    assert "cat:q-fin.PM" in decoded


def _paper(title: str, arxiv_id: str = "") -> Paper:
    return Paper(title=title, abstract="a", raw={"arxiv_id": arxiv_id} if arxiv_id else {})


def test_processed_registry_dedups_within_and_across_runs(tmp_path: Path) -> None:
    path = tmp_path / "seen.json"
    papers = [_paper("Momentum", "2501.1"), _paper("Value", "2501.2")]

    registry = ProcessedRegistry(path)
    assert registry.filter_unseen(papers) == papers  # nothing seen yet
    for paper in papers:
        registry.mark(paper)
    registry.save()

    # A fresh registry loaded from disk treats the same window as fully seen.
    reloaded = ProcessedRegistry(path)
    assert reloaded.filter_unseen(papers) == []
    assert reloaded.filter_unseen([_paper("New Paper", "2501.9")]) == [_paper("New Paper", "2501.9")]


def test_processed_registry_keys_on_title_when_no_arxiv_id(tmp_path: Path) -> None:
    registry = ProcessedRegistry(tmp_path / "seen.json")
    registry.mark(_paper("Same Title"))

    # Same normalized title, no id => seen even though it is a different object.
    assert registry.is_seen(_paper("same   title"))
    assert not registry.is_seen(_paper("Different Title"))
