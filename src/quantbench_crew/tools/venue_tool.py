"""Conference and journal paper sources (beyond arXiv).

Two metadata backends, each behind an injectable fetcher so tests replay
recorded JSON offline:

- **Conferences** (KDD, ICML, ICLR, WSDM, AAAI, IJCAI, ACM Web Conference,
  NeurIPS) — DBLP's publication search filtered by the venue's canonical
  stream id (``streamid:conf/kdd:`` ...). DBLP has no abstracts, so hits with
  DOIs are enriched in ONE batched OpenAlex request (``filter=doi:a|b|...``)
  that fills abstracts and open-access PDF URLs where available.
- **Journals** (Journal of Finance, Journal of Financial Economics, Review of
  Financial Studies) — OpenAlex works search filtered by the journal's ISSN,
  with abstracts reconstructed from ``abstract_inverted_index``. The current
  API key is read from ``OPENALEX_API_KEY`` when available.

Failures fall back to deterministic offline placeholder records, mirroring
the arXiv source, so the workflow always runs.
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from datetime import date
from typing import Any

from quantbench_crew.models import Paper
from quantbench_crew.tools.arxiv_tool import Fetcher, _http_get

DBLP_API_URL = "https://dblp.org/search/publ/api"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"
OPENALEX_API_KEY_ENV = "OPENALEX_API_KEY"

# venue key -> spec. Conference stream ids are DBLP's canonical streams;
# journal ISSNs were verified against OpenAlex live (JF/JFE/RFS).
VENUES: dict[str, dict[str, str]] = {
    "kdd": {"kind": "conference", "stream": "conf/kdd", "label": "ACM SIGKDD Conference (KDD)"},
    "icml": {"kind": "conference", "stream": "conf/icml", "label": "International Conference on Machine Learning"},
    "iclr": {"kind": "conference", "stream": "conf/iclr", "label": "International Conference on Learning Representations"},
    "wsdm": {"kind": "conference", "stream": "conf/wsdm", "label": "ACM Conference on Web Search and Data Mining"},
    "aaai": {"kind": "conference", "stream": "conf/aaai", "label": "AAAI Conference on Artificial Intelligence"},
    "ijcai": {"kind": "conference", "stream": "conf/ijcai", "label": "International Joint Conference on AI"},
    "www": {"kind": "conference", "stream": "conf/www", "label": "ACM Web Conference (WWW)"},
    "neurips": {"kind": "conference", "stream": "conf/nips", "label": "Neural Information Processing Systems"},
    "jf": {"kind": "journal", "issn": "0022-1082", "label": "The Journal of Finance"},
    "jfe": {"kind": "journal", "issn": "0304-405X", "label": "Journal of Financial Economics"},
    "rfs": {"kind": "journal", "issn": "0893-9454", "label": "Review of Financial Studies"},
}

VENUE_GROUPS: dict[str, tuple[str, ...]] = {
    "conferences": ("kdd", "icml", "iclr", "wsdm", "aaai", "ijcai", "www", "neurips"),
    "journals": ("jf", "jfe", "rfs"),
}


def search_venue(
    venue: str,
    query: str,
    max_results: int = 5,
    fetcher: Fetcher | None = None,
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Paper]:
    """Search one venue; deterministic placeholders on network failure."""

    spec = VENUES.get(venue)
    if spec is None:
        raise ValueError(f"unknown venue {venue!r}; expected one of {sorted(VENUES)}")
    fetch = fetcher or _http_get
    try:
        if spec["kind"] == "journal":
            return _search_openalex_journal(
                spec, venue, query, max_results, fetch, year, start_date, end_date
            )
        return _search_dblp_conference(spec, venue, query, max_results, fetch, year)
    except (OSError, ValueError, KeyError) as exc:
        print(
            f"warning: live {venue} search failed ({exc!r}); "
            "using deterministic offline placeholder records",
            file=sys.stderr,
        )
        return placeholder_venue_papers(venue, query, max_results)


def search_venues(
    venues: tuple[str, ...] | list[str],
    query: str,
    max_results: int = 5,
    fetcher: Fetcher | None = None,
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Paper]:
    """Search several venues, splitting the budget roughly evenly."""

    if not venues:
        return []
    per_venue = max(1, max_results // len(venues))
    papers: list[Paper] = []
    for venue in venues:
        papers.extend(
            search_venue(
                venue, query, per_venue, fetcher, year, start_date, end_date
            )
        )
    return papers[:max_results]


def expand_source(source: str) -> tuple[str, ...]:
    """Resolve a CLI source name to the venue keys it covers."""

    if source in VENUE_GROUPS:
        return VENUE_GROUPS[source]
    if source in VENUES:
        return (source,)
    return ()


def search_venues_pooled(
    venues: tuple[str, ...] | list[str],
    pool_selector: str,
    max_results: int = 5,
    fetcher: Fetcher | None = None,
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Paper]:
    """Search venues with a query-pool selector instead of one query.

    The budget splits across venues as in :func:`search_venues`; within each
    venue the pool resolves venue-aware (``auto`` picks the venue's matched
    pool) and fans out across terms with cross-term dedup.
    """

    from quantbench_crew.tools.query_pool import multi_query_search, resolve_pool

    if not venues:
        return []
    per_venue = max(1, max_results // len(venues))
    papers: list[Paper] = []
    for venue in venues:
        terms = resolve_pool(pool_selector, venue=venue)
        papers.extend(
            multi_query_search(
                lambda query, budget, _v=venue: search_venue(
                    _v, query, budget, fetcher, year, start_date, end_date
                ),
                terms,
                per_venue,
                delay=0.4 if fetcher is None else 0.0,
            )
        )
    return papers[:max_results]


def placeholder_venue_papers(venue: str, query: str, max_results: int = 5) -> list[Paper]:
    """Deterministic offline stand-ins for live venue results."""

    label = VENUES.get(venue, {}).get("label", venue)
    return [
        Paper(
            title=f"{label} candidate for {query}",
            abstract=(
                "A placeholder quantitative research record about forecasting, "
                "portfolio evaluation, and benchmark-driven research."
            ),
            authors=("Unknown",),
            source=f"{venue}-placeholder",
            url=None,
            keywords=("quantitative finance", "machine learning"),
        )
        for _ in range(max_results)
    ]


# --- DBLP conferences ---------------------------------------------------------

def _search_dblp_conference(
    spec: dict[str, str], venue: str, query: str, max_results: int,
    fetch: Fetcher, year: int | None,
) -> list[Paper]:
    q = f"{query} streamid:{spec['stream']}:"
    # The year filter is client-side (DBLP has no year parameter), so
    # over-fetch generously when a year is requested.
    hits_wanted = 100 if year else max_results
    url = (
        f"{DBLP_API_URL}?format=json&h={min(hits_wanted, 100)}"
        f"&q={urllib.parse.quote(q)}"
    )
    payload = _json(fetch(url))
    hits = ((payload.get("result") or {}).get("hits") or {}).get("hit") or []

    papers: list[Paper] = []
    for hit in hits:
        info = hit.get("info") or {}
        hit_year = _to_int(info.get("year"))
        if year is not None and hit_year != year:
            continue
        papers.append(
            Paper(
                title=str(info.get("title") or "Untitled").rstrip("."),
                abstract="",  # DBLP carries no abstracts; enriched below
                authors=_dblp_authors(info),
                source=venue,
                url=str(info.get("ee") or info.get("url") or "") or None,
                published=date(hit_year, 1, 1) if hit_year else None,
                keywords=(spec["label"],),
                raw={
                    "venue": str(info.get("venue") or spec["label"]),
                    "doi": str(info.get("doi") or ""),
                    "dblp_key": str(info.get("key") or ""),
                    "year": hit_year,
                    "date_precision": "year",
                },
            )
        )
        if len(papers) >= max_results:
            break
    return _enrich_with_openalex(papers, fetch)


def _dblp_authors(info: dict[str, Any]) -> tuple[str, ...]:
    authors = ((info.get("authors") or {}).get("author")) or []
    if isinstance(authors, dict):  # single author comes as a bare object
        authors = [authors]
    return tuple(str(a.get("text", a)) if isinstance(a, dict) else str(a) for a in authors)


def _enrich_with_openalex(papers: list[Paper], fetch: Fetcher) -> list[Paper]:
    """Fill abstracts/OA PDFs for DOI-bearing hits in one batched request.

    Best-effort: enrichment failure leaves the DBLP records untouched rather
    than failing the search.
    """

    dois = [p.raw["doi"].lower() for p in papers if p.raw.get("doi")]
    if not dois:
        return papers
    url = _with_openalex_api_key(
        f"{OPENALEX_WORKS_URL}?per_page=50&filter="
        + urllib.parse.quote("doi:" + "|".join(dois[:50]))
    )
    try:
        results = _json(fetch(url)).get("results") or []
    except (OSError, ValueError) as exc:
        print(f"warning: OpenAlex enrichment failed ({exc!r})", file=sys.stderr)
        return papers

    by_doi = {
        (work.get("doi") or "").removeprefix("https://doi.org/").lower(): work
        for work in results
    }
    enriched: list[Paper] = []
    for paper in papers:
        work = by_doi.get(paper.raw.get("doi", "").lower())
        if work is None:
            enriched.append(paper)
            continue
        abstract = _abstract_from_inverted_index(work.get("abstract_inverted_index"))
        oa_url = (work.get("open_access") or {}).get("oa_url") or ""
        raw = dict(paper.raw)
        if oa_url:
            raw["pdf_url"] = oa_url  # picked up by the pdf_acquisition skill
        raw["openalex_id"] = str(work.get("id") or "")
        enriched.append(
            Paper(
                title=paper.title,
                abstract=abstract or paper.abstract,
                authors=paper.authors,
                source=paper.source,
                url=paper.url,
                published=paper.published,
                keywords=paper.keywords,
                raw=raw,
            )
        )
    return enriched


# --- OpenAlex journals ----------------------------------------------------------

def _search_openalex_journal(
    spec: dict[str, str], venue: str, query: str, max_results: int,
    fetch: Fetcher, year: int | None, start_date: date | None, end_date: date | None,
) -> list[Paper]:
    filters = [f"primary_location.source.issn:{spec['issn']}"]
    if year is not None:
        filters.append(f"publication_year:{year}")
    if start_date is not None:
        filters.append(f"from_publication_date:{start_date.isoformat()}")
    if end_date is not None:
        filters.append(f"to_publication_date:{end_date.isoformat()}")
    url = _with_openalex_api_key(
        f"{OPENALEX_WORKS_URL}?per_page={min(max_results, 50)}"
        f"&search={urllib.parse.quote(query)}"
        f"&filter={urllib.parse.quote(','.join(filters))}"
    )
    results = _json(fetch(url)).get("results") or []

    papers: list[Paper] = []
    for work in results[:max_results]:
        doi = (work.get("doi") or "").removeprefix("https://doi.org/")
        oa_url = (work.get("open_access") or {}).get("oa_url") or ""
        raw: dict[str, Any] = {
            "venue": spec["label"],
            "doi": doi,
            "openalex_id": str(work.get("id") or ""),
            "year": work.get("publication_year"),
            "date_precision": "day",
        }
        if oa_url:
            raw["pdf_url"] = oa_url
        papers.append(
            Paper(
                title=str(work.get("title") or "Untitled"),
                abstract=_abstract_from_inverted_index(work.get("abstract_inverted_index")),
                authors=tuple(
                    str(((a.get("author") or {}).get("display_name")) or "")
                    for a in work.get("authorships") or []
                ),
                source=venue,
                url=(work.get("doi") or None),
                published=_parse_iso_date(work.get("publication_date")),
                keywords=(spec["label"],),
                raw=raw,
            )
        )
    return papers


def _abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str:
    """Rebuild abstract text from OpenAlex's inverted word index."""

    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, slots in index.items():
        positions.extend((slot, word) for slot in slots)
    return " ".join(word for _, word in sorted(positions))


def _with_openalex_api_key(url: str) -> str:
    """Attach the current OpenAlex API key when configured."""

    key = os.getenv(OPENALEX_API_KEY_ENV, "").strip()
    if not key:
        return url
    return f"{url}&api_key={urllib.parse.quote(key)}"


def _parse_iso_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json(payload: bytes) -> dict[str, Any]:
    import json

    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("venue API returned a non-object JSON payload")
    return data
