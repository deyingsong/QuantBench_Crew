"""Conference/journal sources: DBLP + OpenAlex adapters, offline."""

import json
from pathlib import Path

import pytest

from quantbench_crew.models import Paper
from quantbench_crew.tools.arxiv_tool import ProcessedRegistry
from quantbench_crew.tools.venue_tool import (
    VENUE_GROUPS,
    VENUES,
    _abstract_from_inverted_index,
    expand_source,
    placeholder_venue_papers,
    search_venue,
    search_venues,
)


def _dblp_payload(entries):
    return json.dumps(
        {"result": {"hits": {"@total": str(len(entries)), "hit": entries}}}
    ).encode()


def _dblp_hit(title, year, doi, venue="KDD"):
    return {
        "info": {
            "title": title,
            "year": str(year),
            "doi": doi,
            "venue": venue,
            "ee": f"https://doi.org/{doi}" if doi else "",
            "key": f"conf/kdd/{title[:8]}",
            "authors": {"author": [{"text": "Ada Lovelace"}, {"text": "Alan Turing"}]},
        }
    }


def _openalex_payload(works):
    return json.dumps({"meta": {"count": len(works)}, "results": works}).encode()


def _openalex_work(doi, title="Enriched", abstract_words=("Deep", "momentum"), oa=True):
    return {
        "id": "https://openalex.org/W1",
        "title": title,
        "doi": f"https://doi.org/{doi}",
        "publication_year": 2024,
        "publication_date": "2024-08-25",
        "abstract_inverted_index": {w: [i] for i, w in enumerate(abstract_words)},
        "open_access": {"oa_url": "https://example.org/paper.pdf"} if oa else {},
        "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
    }


# --- registry and groups -------------------------------------------------------

def test_all_requested_venues_are_registered() -> None:
    assert set(VENUE_GROUPS["conferences"]) == {
        "kdd", "icml", "iclr", "wsdm", "aaai", "ijcai", "www", "neurips"
    }
    assert set(VENUE_GROUPS["journals"]) == {"jf", "jfe", "rfs"}
    for key in (*VENUE_GROUPS["conferences"], *VENUE_GROUPS["journals"]):
        assert key in VENUES


def test_expand_source_resolves_keys_and_groups() -> None:
    assert expand_source("kdd") == ("kdd",)
    assert expand_source("journals") == ("jf", "jfe", "rfs")
    assert expand_source("local") == ()
    assert expand_source("arxiv") == ()


def test_unknown_venue_raises() -> None:
    with pytest.raises(ValueError, match="unknown venue"):
        search_venue("nature", "q")


# --- conference path (DBLP + enrichment) ----------------------------------------

def test_conference_search_parses_dblp_and_enriches() -> None:
    calls = []

    def fetch(url: str) -> bytes:
        calls.append(url)
        if "dblp.org" in url:
            return _dblp_payload([_dblp_hit("Momentum Nets.", 2024, "10.1145/1.1")])
        return _openalex_payload([_openalex_work("10.1145/1.1")])

    papers = search_venue("kdd", "momentum", max_results=3, fetcher=fetch)

    assert len(papers) == 1
    paper = papers[0]
    assert paper.source == "kdd"
    assert paper.title == "Momentum Nets"  # trailing period stripped
    assert paper.authors == ("Ada Lovelace", "Alan Turing")
    assert paper.abstract == "Deep momentum"          # enriched from OpenAlex
    assert paper.raw["pdf_url"].endswith("paper.pdf")  # feeds pdf_acquisition
    assert paper.raw["doi"] == "10.1145/1.1"
    assert "streamid%3Aconf/kdd%3A" in calls[0]        # canonical stream filter
    assert len(calls) == 2                              # one batched enrichment


def test_conference_year_filter_is_client_side() -> None:
    def fetch(url: str) -> bytes:
        if "dblp.org" in url:
            return _dblp_payload(
                [
                    _dblp_hit("Old", 2019, "10.1/old"),
                    _dblp_hit("New", 2024, "10.1/new"),
                ]
            )
        return _openalex_payload([])

    papers = search_venue("neurips", "q", max_results=5, fetcher=fetch, year=2024)

    assert [p.title for p in papers] == ["New"]
    assert papers[0].published.year == 2024


def test_enrichment_failure_keeps_dblp_records() -> None:
    def fetch(url: str) -> bytes:
        if "dblp.org" in url:
            return _dblp_payload([_dblp_hit("Solo", 2023, "10.1/solo")])
        raise OSError("openalex down")

    papers = search_venue("icml", "q", fetcher=fetch)

    assert len(papers) == 1
    assert papers[0].abstract == ""  # un-enriched, but the record survives


# --- journal path (OpenAlex ISSN) ------------------------------------------------

def test_journal_search_filters_by_issn_and_builds_abstract() -> None:
    seen = {}

    def fetch(url: str) -> bytes:
        seen["url"] = url
        return _openalex_payload(
            [_openalex_work("10.1111/jofi.1", title="Factor Zoo Revisited")]
        )

    papers = search_venue("jf", "factor zoo", max_results=2, fetcher=fetch, year=2024)

    assert "0022-1082" in seen["url"]                 # JF ISSN filter
    assert "publication_year%3A2024" in seen["url"]   # server-side year filter
    paper = papers[0]
    assert paper.source == "jf"
    assert paper.title == "Factor Zoo Revisited"
    assert paper.abstract == "Deep momentum"
    assert paper.raw["venue"] == "The Journal of Finance"


# --- fallbacks and fan-out -------------------------------------------------------

def test_network_failure_falls_back_to_placeholders() -> None:
    def fetch(url: str) -> bytes:
        raise OSError("offline")

    papers = search_venue("rfs", "volatility", max_results=3, fetcher=fetch)

    assert len(papers) == 3
    assert all(p.source == "rfs-placeholder" for p in papers)


def test_search_venues_splits_budget_across_group() -> None:
    def fetch(url: str) -> bytes:
        if "dblp.org" in url:
            return _dblp_payload([_dblp_hit("Hit", 2024, "")])
        return _openalex_payload([])

    papers = search_venues(VENUE_GROUPS["conferences"], "q", max_results=8, fetcher=fetch)

    assert len(papers) == 8
    assert {p.source for p in papers} == set(VENUE_GROUPS["conferences"])


def test_placeholders_are_deterministic() -> None:
    assert placeholder_venue_papers("jfe", "x", 2) == placeholder_venue_papers("jfe", "x", 2)


def test_abstract_inverted_index_reconstruction() -> None:
    index = {"world": [1], "hello": [0], "again": [2, 3]}
    assert _abstract_from_inverted_index(index) == "hello world again again"
    assert _abstract_from_inverted_index(None) == ""


def test_processed_registry_dedups_on_doi(tmp_path: Path) -> None:
    registry = ProcessedRegistry(tmp_path / "seen.json")
    first = Paper(title="A Title", abstract="", raw={"doi": "10.1145/X.Y"})
    registry.mark(first)

    # Same DOI under a different title (e.g. DBLP vs publisher casing) is seen.
    same_doi = Paper(title="A TITLE (extended)", abstract="", raw={"doi": "10.1145/x.y"})
    assert registry.is_seen(same_doi)
