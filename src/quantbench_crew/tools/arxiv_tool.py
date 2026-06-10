"""Paper source adapters.

Provides the local deterministic source, live arXiv search over the q-fin
categories, and PDF caching under ``data/raw/``. Live calls go through an
injectable ``fetcher`` so tests replay recorded feeds offline; when the
network is unavailable the search falls back to deterministic placeholder
records so the dry workflow always runs.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import date
from pathlib import Path

from quantbench_crew.models import Paper

ARXIV_API_URL = "https://export.arxiv.org/api/query"

# Explicit q-fin subcategories (the arXiv API has no reliable cat wildcard).
QFIN_CATEGORIES = (
    "q-fin.CP",
    "q-fin.EC",
    "q-fin.GN",
    "q-fin.MF",
    "q-fin.PM",
    "q-fin.PR",
    "q-fin.RM",
    "q-fin.ST",
    "q-fin.TR",
)

DEFAULT_PDF_CACHE_DIR = Path("data/raw")

_ATOM = {"atom": "http://www.w3.org/2005/Atom"}

Fetcher = Callable[[str], bytes]


def load_local_papers(path: str | Path | None = None) -> list[Paper]:
    """Load paper metadata from JSON, or return built-in seed records."""

    if path is None:
        return sample_papers()

    source_path = Path(path)
    records = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Local paper source must be a JSON list of records.")
    return [paper_from_record(record, source=str(source_path)) for record in records]


def search_arxiv(
    query: str, max_results: int = 5, fetcher: Fetcher | None = None
) -> list[Paper]:
    """Search live arXiv q-fin categories; fall back to offline placeholders.

    An empty live result list is returned as-is (a legitimate answer); the
    placeholder fallback engages only when the API cannot be reached or its
    response cannot be parsed.
    """

    url = _arxiv_query_url(query, max_results)
    try:
        payload = (fetcher or _http_get)(url)
        papers = _parse_arxiv_feed(payload.decode("utf-8"))
    except (OSError, ValueError, ET.ParseError) as exc:
        print(
            f"warning: live arXiv search failed ({exc!r}); "
            "using deterministic offline placeholder records",
            file=sys.stderr,
        )
        return placeholder_arxiv_papers(query, max_results)
    return papers[:max_results]


def cache_pdf(
    paper: Paper,
    cache_dir: str | Path = DEFAULT_PDF_CACHE_DIR,
    fetcher: Fetcher | None = None,
) -> Path | None:
    """Download the paper's PDF into the cache, returning the local path.

    A previously cached file is returned without touching the network, which
    keeps reruns deterministic and offline. Returns None when the paper has
    no derivable PDF URL, the download fails, or the response is not a PDF.
    """

    pdf_url = _pdf_url(paper)
    target = Path(cache_dir) / f"{_pdf_basename(paper)}.pdf"
    if target.exists():
        return target
    if pdf_url is None:
        return None

    try:
        payload = (fetcher or _http_get)(pdf_url)
    except OSError as exc:
        print(f"warning: PDF download failed for {pdf_url} ({exc!r})", file=sys.stderr)
        return None
    if not payload.startswith(b"%PDF"):
        print(f"warning: {pdf_url} did not return a PDF; not caching", file=sys.stderr)
        return None

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return target


def paper_from_record(record: dict[str, object], source: str = "local") -> Paper:
    """Create a Paper from a loose metadata dictionary."""

    title = str(record.get("title") or "Untitled paper")
    abstract = str(record.get("abstract") or record.get("summary") or "")
    authors_value = record.get("authors") or ()
    keywords_value = record.get("keywords") or ()

    return Paper(
        title=title,
        abstract=abstract,
        authors=tuple(str(author) for author in _as_sequence(authors_value)),
        source=str(record.get("source") or source),
        url=str(record["url"]) if record.get("url") else None,
        keywords=tuple(str(keyword) for keyword in _as_sequence(keywords_value)),
        raw=dict(record),
    )


def sample_papers() -> list[Paper]:
    """Seed records used by the initial dry workflow."""

    return [
        Paper(
            title="Machine Learning for Asset Pricing Benchmarks",
            abstract=(
                "We study machine learning forecasts for equity returns using CRSP-like "
                "monthly data and compare portfolio Sharpe, turnover, and drawdown "
                "against simple baselines."
            ),
            authors=("Researcher A", "Researcher B"),
            source="sample",
            keywords=("asset pricing", "machine learning", "portfolio"),
        ),
        Paper(
            title="Liquidity Risk and Intraday Market Microstructure",
            abstract=(
                "This paper evaluates liquidity risk using intraday returns and market "
                "microstructure features, with robustness checks for volatility regimes."
            ),
            authors=("Researcher C",),
            source="sample",
            keywords=("risk", "market microstructure"),
        ),
    ]


def placeholder_arxiv_papers(query: str, max_results: int = 5) -> list[Paper]:
    """Deterministic offline stand-ins for live arXiv results."""

    return [
        Paper(
            title=f"arXiv candidate for {query}",
            abstract=(
                "A placeholder quantitative finance paper record about forecasting, "
                "portfolio evaluation, and benchmark-driven research."
            ),
            authors=("Unknown",),
            source="arxiv-placeholder",
            url=None,
            keywords=("quantitative finance", "forecasting", "portfolio"),
        )
        for _ in range(max_results)
    ]


def _arxiv_query_url(query: str, max_results: int) -> str:
    categories = " OR ".join(f"cat:{category}" for category in QFIN_CATEGORIES)
    search_query = f"({categories}) AND all:{query}"
    params = urllib.parse.urlencode(
        {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        quote_via=urllib.parse.quote,
    )
    return f"{ARXIV_API_URL}?{params}"


def _parse_arxiv_feed(xml_text: str) -> list[Paper]:
    root = ET.fromstring(xml_text)
    papers: list[Paper] = []
    for entry in root.findall("atom:entry", _ATOM):
        entry_id = _text(entry, "atom:id")
        title = " ".join(_text(entry, "atom:title").split())
        abstract = " ".join(_text(entry, "atom:summary").split())
        authors = tuple(
            _text(author, "atom:name")
            for author in entry.findall("atom:author", _ATOM)
        )
        categories = tuple(
            element.get("term", "")
            for element in entry.findall("atom:category", _ATOM)
            if element.get("term")
        )
        published = _parse_date(_text(entry, "atom:published"))
        pdf_url = _entry_pdf_url(entry, entry_id)

        papers.append(
            Paper(
                title=title or "Untitled arXiv entry",
                abstract=abstract,
                authors=authors,
                source="arxiv",
                url=entry_id or None,
                published=published,
                keywords=categories,
                raw={
                    "entry_id": entry_id,
                    "arxiv_id": _arxiv_id_from_entry_id(entry_id),
                    "pdf_url": pdf_url,
                    "categories": list(categories),
                },
            )
        )
    return papers


def _entry_pdf_url(entry: ET.Element, entry_id: str) -> str | None:
    for link in entry.findall("atom:link", _ATOM):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            href = link.get("href")
            if href:
                return href
    if "arxiv.org/abs/" in entry_id:
        return entry_id.replace("/abs/", "/pdf/")
    return None


def _arxiv_id_from_entry_id(entry_id: str) -> str:
    marker = "arxiv.org/abs/"
    if marker in entry_id:
        return entry_id.split(marker, 1)[1]
    return entry_id


def _pdf_url(paper: Paper) -> str | None:
    raw_url = paper.raw.get("pdf_url")
    if raw_url:
        return str(raw_url)
    if paper.url and "arxiv.org/abs/" in paper.url:
        return paper.url.replace("/abs/", "/pdf/")
    return None


def _pdf_basename(paper: Paper) -> str:
    arxiv_id = str(paper.raw.get("arxiv_id") or "")
    if arxiv_id:
        return arxiv_id.replace("/", "-")
    return paper.slug


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _text(element: ET.Element, path: str) -> str:
    found = element.find(path, _ATOM)
    return (found.text or "").strip() if found is not None else ""


def _http_get(url: str, timeout: float = 30.0) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "quantbench-crew/0.1 (research pipeline)"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _as_sequence(value: object) -> tuple[object, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value,)
