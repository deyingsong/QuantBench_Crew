import logging
from datetime import date
from pathlib import Path

from quantbench_crew.models import Paper
from quantbench_crew.tools.arxiv_tool import cache_pdf, load_local_papers, search_arxiv

FEED = (Path(__file__).parent / "fixtures" / "arxiv_feed.xml").read_text(encoding="utf-8")


def test_search_arxiv_parses_live_feed() -> None:
    requested: list[str] = []

    def fetcher(url: str) -> bytes:
        requested.append(url)
        return FEED.encode("utf-8")

    papers = search_arxiv("momentum", max_results=5, fetcher=fetcher)

    assert len(papers) == 2
    first = papers[0]
    assert first.title == "Momentum Everywhere: Evidence from Factor Portfolios"
    assert first.source == "arxiv"
    assert first.url == "http://arxiv.org/abs/2401.01234v2"
    assert first.published == date(2024, 1, 3)
    assert first.authors == ("Alice Quant", "Bob Researcher")
    assert "q-fin.PM" in first.keywords
    assert first.raw["arxiv_id"] == "2401.01234v2"
    assert first.raw["pdf_url"] == "http://arxiv.org/pdf/2401.01234v2"
    # Query targets the q-fin categories and respects max_results.
    assert "q-fin.PM" in requested[0]
    assert "max_results=5" in requested[0]


def test_search_arxiv_derives_pdf_url_when_link_missing() -> None:
    papers = search_arxiv("momentum", fetcher=lambda url: FEED.encode("utf-8"))

    second = papers[1]
    assert second.raw["pdf_url"] == "http://arxiv.org/pdf/2402.04567v1"


def test_search_arxiv_truncates_to_max_results() -> None:
    papers = search_arxiv("momentum", max_results=1, fetcher=lambda url: FEED.encode("utf-8"))

    assert len(papers) == 1


def test_search_arxiv_falls_back_offline(caplog) -> None:
    def failing_fetcher(url: str) -> bytes:
        raise OSError("network unreachable")

    with caplog.at_level(logging.WARNING):
        papers = search_arxiv("momentum", max_results=3, fetcher=failing_fetcher)

    assert len(papers) == 3
    assert all(paper.source == "arxiv-placeholder" for paper in papers)
    assert "live arXiv search failed" in caplog.text


def test_cache_pdf_downloads_and_reuses_cache(tmp_path: Path) -> None:
    paper = search_arxiv("momentum", fetcher=lambda url: FEED.encode("utf-8"))[0]
    calls: list[str] = []

    def pdf_fetcher(url: str) -> bytes:
        calls.append(url)
        return b"%PDF-1.4 fake body"

    first = cache_pdf(paper, cache_dir=tmp_path, fetcher=pdf_fetcher)

    assert first is not None
    assert first.name == "2401.01234v2.pdf"
    assert first.read_bytes().startswith(b"%PDF")
    assert calls == ["http://arxiv.org/pdf/2401.01234v2"]

    def must_not_fetch(url: str) -> bytes:
        raise AssertionError("cache hit must not touch the network")

    second = cache_pdf(paper, cache_dir=tmp_path, fetcher=must_not_fetch)
    assert second == first


def test_cache_pdf_rejects_non_pdf_responses(tmp_path: Path, caplog) -> None:
    paper = search_arxiv("momentum", fetcher=lambda url: FEED.encode("utf-8"))[0]

    with caplog.at_level(logging.WARNING):
        result = cache_pdf(paper, cache_dir=tmp_path, fetcher=lambda url: b"<html>error</html>")

    assert result is None
    assert list(tmp_path.iterdir()) == []
    assert "did not return a PDF" in caplog.text


def test_cache_pdf_returns_none_without_url(tmp_path: Path) -> None:
    paper = Paper(title="No URL", abstract="")

    assert cache_pdf(paper, cache_dir=tmp_path) is None


def test_golden_paper_fixture_loads() -> None:
    papers = load_local_papers(Path(__file__).parent / "fixtures" / "golden_paper.json")

    assert len(papers) == 1
    assert "Momentum" in papers[0].title
