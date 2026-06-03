"""Paper source adapters.

The first version provides a local deterministic source and a placeholder arXiv
adapter shape. Network-backed arXiv search can be added behind this module
without changing the agent workflow.
"""

from __future__ import annotations

import json
from pathlib import Path

from quantbench_crew.models import Paper


def load_local_papers(path: str | Path | None = None) -> list[Paper]:
    """Load paper metadata from JSON, or return built-in seed records."""

    if path is None:
        return sample_papers()

    source_path = Path(path)
    records = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Local paper source must be a JSON list of records.")
    return [paper_from_record(record, source=str(source_path)) for record in records]


def search_arxiv(query: str, max_results: int = 5) -> list[Paper]:
    """Return deterministic placeholder arXiv-style records for offline runs."""

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


def _as_sequence(value: object) -> tuple[object, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value,)
