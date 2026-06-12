"""Curated query pool for paper discovery, matched to source semantics.

Four source-specific pools plus high-yield root words. Selector grammar for
``--query-pool``:

- ``auto`` — use the pool matched to each venue being searched (finance
  journals -> finance; AAAI/IJCAI -> general-ai; ICML/ICLR/NeurIPS ->
  core-ml; KDD/WSDM/WWW -> data-mining; arXiv and anything unmapped ->
  roots);
- ``roots`` | ``finance`` | ``general-ai`` | ``core-ml`` | ``data-mining`` —
  every term in that pool;
- ``<pool>/<category>`` — one category (e.g. ``core-ml/foundation-sequence``);
- ``all`` — everything.

Parenthetical acronyms from the source taxonomy are folded into the plain
phrase (search engines tokenize them away), and the "time series or
time-series" root is a single term — both backends tokenize the hyphen.
Remember conference (DBLP) queries match *titles*, so multi-word pool terms
naturally act as precise title filters there, while journal/arXiv backends
match full metadata.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import replace

from quantbench_crew.models import Paper
from quantbench_crew.tools.arxiv_tool import _title_hash

ROOT_WORDS: tuple[str, ...] = (
    "portfolio",
    "asset pricing",
    "time series",
    "trading",
    "stock",
    "volatility",
    "alpha",
)

# pool -> category -> terms (taxonomy as specified by the operator).
QUERY_POOLS: dict[str, dict[str, tuple[str, ...]]] = {
    "roots": {"high-yield": ROOT_WORDS},
    "finance": {  # Top-tier finance journals (JF, JFE, RFS)
        "asset-pricing-factors": (
            "empirical asset pricing",
            "factor models",
            "cross-sectional equity returns",
            "formulaic alpha factor mining",
        ),
        "market-mechanics": (
            "market microstructure",
            "limit order book",
            "market efficiency",
            "volatility contagion",
            "liquidity constraints",
        ),
        "trading-strategies": (
            "momentum strategy",
            "trend-following",
            "mean-variance optimization",
            "risk-adjusted return",
            "arbitrage",
        ),
        "ml-intersections": (
            "machine learning in asset pricing",
            "textual analysis in finance",
            "nonstationarity",
        ),
    },
    "general-ai": {  # AAAI, IJCAI
        "agents-multi-agent": (
            "LLM trading bot",
            "multi-agent simulation",
            "agentic AI",
            "autonomous trading agents",
            "ensemble imitation learning",
        ),
        "reasoning-heuristics": (
            "time-series reasoning",
            "knowledge graphs",
            "explainable AI in finance",
            "skill distillation",
            "grammar-guided search",
        ),
        "strategy-decision": (
            "Q-learning",
            "imitation learning",
            "algorithmic trading",
            "alpha factor mining",
            "systematic factor investing",
        ),
    },
    "core-ml": {  # ICML, ICLR, NeurIPS
        "foundation-sequence": (
            "time series foundation models",
            "state space models",
            "Mamba",
            "multimodal foundation model",
            "transformer architecture",
            "continuous-time models",
        ),
        "generative-synthetic": (
            "generative diffusion models",
            "conditional autoencoders",
            "variational autoencoders",
            "GANs for time-series",
            "data augmentation",
        ),
        "advanced-optimization": (
            "deep reinforcement learning",
            "Bayesian optimization",
            "numerical optimization",
            "portfolio optimization",
            "predict-then-optimize",
        ),
        "theory-physics": (
            "Kolmogorov-Arnold networks",
            "physics-informed neural networks",
            "Hawkes processes",
            "stochastic volatility modeling",
        ),
    },
    "data-mining": {  # KDD, WSDM, ACM Web Conference
        "graph-network": (
            "graph neural networks",
            "stock correlation networks",
            "hypergraph",
            "co-occurrence graph",
            "spatiotemporal graphs",
        ),
        "web-text-mining": (
            "sentiment analysis",
            "financial news integration",
            "event-driven trading",
            "web-mined hypothesis generation",
            "topic modeling in finance",
        ),
        "applied-forecasting": (
            "spatiotemporal time series",
            "dynamic stock recommendation",
            "cross-sectional asset retrieval",
            "lead-lag dependencies",
        ),
    },
}

POOL_FOR_VENUE: dict[str, str] = {
    "jf": "finance",
    "jfe": "finance",
    "rfs": "finance",
    "aaai": "general-ai",
    "ijcai": "general-ai",
    "icml": "core-ml",
    "iclr": "core-ml",
    "neurips": "core-ml",
    "kdd": "data-mining",
    "wsdm": "data-mining",
    "www": "data-mining",
}


def pool_terms(pool: str, category: str | None = None) -> tuple[str, ...]:
    """All terms of a pool, or of one of its categories."""

    categories = QUERY_POOLS.get(pool)
    if categories is None:
        raise ValueError(f"unknown query pool {pool!r}; expected one of {sorted(QUERY_POOLS)}")
    if category is None:
        return tuple(term for terms in categories.values() for term in terms)
    if category not in categories:
        raise ValueError(
            f"unknown category {category!r} in pool {pool!r}; "
            f"expected one of {sorted(categories)}"
        )
    return categories[category]


def resolve_pool(selector: str, venue: str | None = None) -> tuple[str, ...]:
    """Resolve a ``--query-pool`` selector to concrete query terms."""

    selector = selector.strip().lower()
    if selector == "auto":
        return pool_terms(POOL_FOR_VENUE.get(venue or "", "roots"))
    if selector == "all":
        return tuple(term for pool in QUERY_POOLS for term in pool_terms(pool))
    if "/" in selector:
        pool, category = selector.split("/", 1)
        return pool_terms(pool, category)
    return pool_terms(selector)


def multi_query_search(
    search_fn: Callable[[str, int], list[Paper]],
    terms: Iterable[str],
    max_results: int,
    delay: float = 0.0,
) -> list[Paper]:
    """Fan a result budget across pool terms with cross-term dedup.

    Iterates terms in declared order — at most ``max_results`` of them, one
    result each, when the pool is larger than the budget — deduplicates by
    DOI/arXiv id/normalized title, annotates each hit with the term that
    found it (``raw["query"]``), and stops as soon as the budget fills.
    """

    used_terms = list(terms)[: max(1, max_results)]
    if not used_terms:
        return []
    per_term = max(1, max_results // len(used_terms))

    papers: list[Paper] = []
    seen: set[str] = set()
    for index, term in enumerate(used_terms):
        if len(papers) >= max_results:
            break
        if delay and index:
            time.sleep(delay)
        for paper in search_fn(term, per_term):
            key = _identity(paper)
            if key in seen:
                continue
            seen.add(key)
            papers.append(replace(paper, raw={**paper.raw, "query": term}))
            if len(papers) >= max_results:
                break
    return papers


def format_query_pools() -> str:
    """Human-readable listing for the ``quantbench queries`` subcommand."""

    lines = ["Query pools (use with --query-pool; e.g. auto, core-ml, finance/market-mechanics)", ""]
    for pool, categories in QUERY_POOLS.items():
        venues = sorted(v for v, p in POOL_FOR_VENUE.items() if p == pool)
        suffix = f"  [auto for: {', '.join(venues)}]" if venues else "  [auto fallback]"
        lines.append(f"{pool}{suffix}")
        for category, terms in categories.items():
            lines.append(f"  {pool}/{category}")
            for term in terms:
                lines.append(f"    - {term}")
        lines.append("")
    return "\n".join(lines)


def _identity(paper: Paper) -> str:
    doi = str(paper.raw.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    arxiv_id = str(paper.raw.get("arxiv_id") or "").strip()
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{_title_hash(paper.title)}"
