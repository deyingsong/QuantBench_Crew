"""Paper source adapters.

Provides the local deterministic source, live arXiv search over the q-fin
categories, and PDF caching under ``data/raw/``. Live calls go through an
injectable ``fetcher`` so tests replay recorded feeds offline; when the
network is unavailable the search falls back to deterministic placeholder
records so the dry workflow always runs.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable
from datetime import date
from pathlib import Path

from quantbench_crew.models import Paper

ARXIV_API_URL = "https://export.arxiv.org/api/query"

DEFAULT_PROCESSED_PATH = Path("data/processed/seen_papers.json")
ARXIV_PAGE_SIZE = 100
ARXIV_POLITE_DELAY = 3.0   # arXiv asks for ~3s between requests

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
    query: str,
    max_results: int = 5,
    fetcher: Fetcher | None = None,
    *,
    page_size: int = ARXIV_PAGE_SIZE,
    delay: float = ARXIV_POLITE_DELAY,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Paper]:
    """Search live arXiv q-fin categories, paginating up to ``max_results``.

    Fetches pages of ``page_size`` until enough results accrue or the feed is
    exhausted, deduplicating entries within the result set, with a polite
    inter-page ``delay`` and retry-with-backoff on transient errors. An
    optional ``start_date``/``end_date`` window supports incremental fetches.
    If the *first* page cannot be reached the offline placeholder records are
    returned; a later-page failure returns the results gathered so far.
    """

    fetch = fetcher or _http_get
    page_size = max(1, min(page_size, max_results))
    papers: list[Paper] = []
    seen: set[str] = set()
    start = 0

    while len(papers) < max_results:
        url = _arxiv_query_url(
            query, start=start, page_size=page_size,
            start_date=start_date, end_date=end_date,
        )
        try:
            payload = _fetch_with_retry(fetch, url, delay=delay if start else 0.0)
            page = _parse_arxiv_feed(payload.decode("utf-8"))
        except (OSError, ValueError, ET.ParseError) as exc:
            if not papers:
                print(
                    f"warning: live arXiv search failed ({exc!r}); "
                    "using deterministic offline placeholder records",
                    file=sys.stderr,
                )
                return placeholder_arxiv_papers(query, max_results)
            print(f"warning: arXiv page fetch failed ({exc!r}); returning partial results", file=sys.stderr)
            break

        if not page:
            break
        added = 0
        for paper in page:
            key = _dedup_key(paper)
            if key not in seen:
                seen.add(key)
                papers.append(paper)
                added += 1
        # A full page that contributed nothing new means the feed is only
        # repeating content; stop rather than paginate forever.
        if len(page) < page_size or added == 0:
            break
        start += page_size

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


def _arxiv_query_url(
    query: str,
    start: int = 0,
    page_size: int = ARXIV_PAGE_SIZE,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    categories = " OR ".join(f"cat:{category}" for category in QFIN_CATEGORIES)
    parts = [f"({categories})"]
    if query:
        parts.append(f"all:{query}")
    if start_date is not None or end_date is not None:
        low = f"{start_date:%Y%m%d}0000" if start_date else "190001010000"
        high = f"{end_date:%Y%m%d}2359" if end_date else f"{date.today():%Y%m%d}2359"
        parts.append(f"submittedDate:[{low} TO {high}]")
    search_query = " AND ".join(parts)
    params = urllib.parse.urlencode(
        {
            "search_query": search_query,
            "start": start,
            "max_results": page_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        quote_via=urllib.parse.quote,
    )
    return f"{ARXIV_API_URL}?{params}"


def _fetch_with_retry(
    fetch: Fetcher, url: str, *, retries: int = 3, delay: float = 0.0
) -> bytes:
    """Fetch with polite pre-delay and exponential backoff on OSError."""

    if delay:
        time.sleep(delay)
    last_error: OSError | None = None
    for attempt in range(retries):
        try:
            return fetch(url)
        except OSError as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(min(2.0**attempt, 30.0))
    raise last_error if last_error is not None else OSError("fetch failed")


def _dedup_key(paper: Paper) -> str:
    arxiv_id = str(paper.raw.get("arxiv_id") or "").strip()
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{_title_hash(paper.title)}"


def _title_hash(title: str) -> str:
    normalized = " ".join(title.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


class ProcessedRegistry:
    """Persistent set of already-processed papers for cross-run dedup.

    Keyed by both arXiv id and a normalized-title hash, so a paper is skipped
    on re-ingestion whether or not it carries an arXiv id. The backing JSON
    file is the durable watermark that makes incremental fetching idempotent.
    """

    def __init__(self, path: str | Path = DEFAULT_PROCESSED_PATH) -> None:
        self.path = Path(path)
        self._keys: set[str] = set()
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._keys = set(data.get("keys", []))

    @staticmethod
    def _keys_for(paper: Paper) -> tuple[str, ...]:
        keys = [f"title:{_title_hash(paper.title)}"]
        arxiv_id = str(paper.raw.get("arxiv_id") or "").strip()
        if arxiv_id:
            keys.append(f"arxiv:{arxiv_id}")
        doi = str(paper.raw.get("doi") or "").strip().lower()
        if doi:
            keys.append(f"doi:{doi}")
        return tuple(keys)

    def is_seen(self, paper: Paper) -> bool:
        return any(key in self._keys for key in self._keys_for(paper))

    def mark(self, paper: Paper) -> None:
        self._keys.update(self._keys_for(paper))

    def filter_unseen(self, papers: Iterable[Paper]) -> list[Paper]:
        return [paper for paper in papers if not self.is_seen(paper)]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"keys": sorted(self._keys)}, indent=2) + "\n", encoding="utf-8"
        )


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
