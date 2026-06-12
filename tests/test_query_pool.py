"""Curated query pool: taxonomy integrity, selectors, fan-out, CLI wiring."""

import pytest

from quantbench_crew.main import build_parser, main
from quantbench_crew.models import Paper
from quantbench_crew.tools.query_pool import (
    POOL_FOR_VENUE,
    QUERY_POOLS,
    ROOT_WORDS,
    format_query_pools,
    multi_query_search,
    pool_terms,
    resolve_pool,
)
from quantbench_crew.tools.venue_tool import VENUES, search_venues_pooled


# --- taxonomy integrity --------------------------------------------------------

def test_root_words_match_specification() -> None:
    assert ROOT_WORDS == (
        "portfolio", "asset pricing", "time series", "trading",
        "stock", "volatility", "alpha",
    )


def test_pool_categories_match_specification() -> None:
    assert set(QUERY_POOLS) == {"roots", "finance", "general-ai", "core-ml", "data-mining"}
    assert set(QUERY_POOLS["finance"]) == {
        "asset-pricing-factors", "market-mechanics", "trading-strategies", "ml-intersections",
    }
    assert set(QUERY_POOLS["general-ai"]) == {
        "agents-multi-agent", "reasoning-heuristics", "strategy-decision",
    }
    assert set(QUERY_POOLS["core-ml"]) == {
        "foundation-sequence", "generative-synthetic", "advanced-optimization", "theory-physics",
    }
    assert set(QUERY_POOLS["data-mining"]) == {
        "graph-network", "web-text-mining", "applied-forecasting",
    }


def test_spot_check_terms_from_each_pool() -> None:
    assert "formulaic alpha factor mining" in pool_terms("finance", "asset-pricing-factors")
    assert "limit order book" in pool_terms("finance", "market-mechanics")
    assert "LLM trading bot" in pool_terms("general-ai", "agents-multi-agent")
    assert "Mamba" in pool_terms("core-ml", "foundation-sequence")
    assert "Kolmogorov-Arnold networks" in pool_terms("core-ml", "theory-physics")
    assert "lead-lag dependencies" in pool_terms("data-mining", "applied-forecasting")


def test_every_venue_has_a_matched_pool() -> None:
    assert set(POOL_FOR_VENUE) == set(VENUES)
    assert POOL_FOR_VENUE["jfe"] == "finance"
    assert POOL_FOR_VENUE["aaai"] == "general-ai"
    assert POOL_FOR_VENUE["neurips"] == "core-ml"
    assert POOL_FOR_VENUE["kdd"] == "data-mining"


# --- selector grammar -----------------------------------------------------------

def test_resolve_pool_selectors() -> None:
    assert resolve_pool("roots") == ROOT_WORDS
    assert resolve_pool("finance/market-mechanics")[0] == "market microstructure"
    assert len(resolve_pool("all")) == sum(
        len(terms) for pool in QUERY_POOLS.values() for terms in pool.values()
    )


def test_resolve_pool_auto_is_venue_aware() -> None:
    assert resolve_pool("auto", venue="rfs") == pool_terms("finance")
    assert resolve_pool("auto", venue="icml") == pool_terms("core-ml")
    assert resolve_pool("auto", venue=None) == ROOT_WORDS  # arXiv / unmapped


def test_resolve_pool_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown query pool"):
        resolve_pool("astrology")
    with pytest.raises(ValueError, match="unknown category"):
        resolve_pool("finance/astrology")


# --- fan-out mechanics -----------------------------------------------------------

def _paper(title: str, doi: str = "") -> Paper:
    return Paper(title=title, abstract="", raw={"doi": doi} if doi else {})


def test_multi_query_search_fans_out_and_annotates() -> None:
    calls: list[tuple[str, int]] = []

    def search(query: str, budget: int) -> list[Paper]:
        calls.append((query, budget))
        return [_paper(f"{query} paper")]

    papers = multi_query_search(search, ("alpha", "beta", "gamma"), max_results=3)

    assert [p.title for p in papers] == ["alpha paper", "beta paper", "gamma paper"]
    assert [p.raw["query"] for p in papers] == ["alpha", "beta", "gamma"]
    assert all(budget == 1 for _, budget in calls)


def test_multi_query_search_dedups_across_terms() -> None:
    def search(query: str, budget: int) -> list[Paper]:
        return [_paper("Same Hit", doi="10.1/same")]

    papers = multi_query_search(search, ("a", "b", "c"), max_results=5)

    assert len(papers) == 1
    assert papers[0].raw["query"] == "a"  # first term wins


def test_multi_query_search_caps_terms_at_budget() -> None:
    seen: list[str] = []

    def search(query: str, budget: int) -> list[Paper]:
        seen.append(query)
        return [_paper(f"{query}-1"), _paper(f"{query}-2")]

    papers = multi_query_search(search, tuple(f"t{i}" for i in range(20)), max_results=2)

    assert len(papers) == 2
    assert len(seen) <= 2  # never issues more requests than the budget


def test_search_venues_pooled_uses_each_venues_pool() -> None:
    queries_by_venue: dict[str, list[str]] = {}

    def fetch(url: str) -> bytes:
        # Return empty payloads; we only inspect which queries were issued.
        if "dblp.org" in url:
            import urllib.parse

            q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["q"][0]
            term, stream = q.rsplit(" streamid:", 1)
            queries_by_venue.setdefault(stream.rstrip(":"), []).append(term)
            return b'{"result": {"hits": {"@total": "0", "hit": []}}}'
        return b'{"meta": {"count": 0}, "results": []}'

    search_venues_pooled(("neurips", "kdd"), "auto", max_results=4, fetcher=fetch)

    assert queries_by_venue["conf/nips"][0] in pool_terms("core-ml")
    assert queries_by_venue["conf/kdd"][0] in pool_terms("data-mining")


# --- CLI wiring -------------------------------------------------------------------

def test_cli_query_and_pool_are_mutually_exclusive(capsys) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "--query", "x", "--query-pool", "roots"])
    capsys.readouterr()


def test_queries_subcommand_lists_pools(capsys) -> None:
    exit_code = main(["queries"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "finance/market-mechanics" in out
    assert "Mamba" in out
    assert "auto for: jf, jfe, rfs" in out
