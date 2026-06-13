"""Command-line entry point for QuantBench Crew."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from quantbench_crew.agents import (
    QuantBenchAgent,
    QuantCoderAgent,
    QuantReaderAgent,
    QuantReviewerAgent,
    QuantScoutAgent,
)
from quantbench_crew.artifacts import start_run
from quantbench_crew.config import load_config
from quantbench_crew.llm import build_llm_client
from quantbench_crew.models import ReviewReport
from quantbench_crew.skills import resolve_skills
from quantbench_crew.skills.base import RunContext
from quantbench_crew.skills.scout.charter_relevance import load_charter, relevance_boost
from quantbench_crew.skills.scout.relevance_scorer import (
    RelevanceScorerSkill,
    relevance_boost as research_value_boost,
)
from quantbench_crew.tools.arxiv_tool import (
    DEFAULT_PROCESSED_PATH,
    ProcessedRegistry,
    load_local_papers,
    search_arxiv,
)
from quantbench_crew.tools.query_pool import (
    format_query_pools,
    multi_query_search,
    resolve_pool,
)
from quantbench_crew.tools.paper_queue import (
    DEFAULT_QUEUE_PATH,
    ResearchQueue,
    deduplicate_papers,
    filter_by_online_date,
    parse_iso_date,
)
from quantbench_crew.tools.venue_tool import (
    VENUE_GROUPS,
    VENUES,
    expand_source,
    search_venues,
    search_venues_pooled,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    normalized_argv = _with_default_command(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(normalized_argv)

    if args.command == "run":
        reports = run_workflow(args)
        for report in reports:
            print(report.to_markdown())
        return 0

    if args.command == "queries":
        print(format_query_pools())
        return 0
    if args.command == "track":
        print(json.dumps(track_new_papers(args), indent=2, sort_keys=True))
        return 0

    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quantbench",
        description="Run QuantBench Crew research workflows.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser("run", help="Run the paper review workflow.")
    run.add_argument(
        "--source",
        choices=("local", "arxiv", *VENUES, *VENUE_GROUPS),
        default="local",
        help=(
            "Paper source: local JSON, live arXiv (q-fin), a conference "
            "(kdd, icml, iclr, wsdm, aaai, ijcai, www, neurips), a journal "
            "(jf, jfe, rfs), or a group (conferences, journals)."
        ),
    )
    query_group = run.add_mutually_exclusive_group()
    query_group.add_argument("--query", default="quantitative finance")
    query_group.add_argument(
        "--query-pool",
        default=None,
        help=(
            "Search a curated query pool instead of one query: 'auto' (pool "
            "matched to each venue), a pool (roots, finance, general-ai, "
            "core-ml, data-mining), 'pool/category', or 'all'. "
            "List with: quantbench queries."
        ),
    )
    run.add_argument(
        "--year",
        type=int,
        default=None,
        help="Restrict conference/journal sources to one publication year.",
    )
    run.add_argument("--max-papers", type=int, default=2)
    run.add_argument("--paper-json", help="Path to a local JSON list of paper records.")
    run.add_argument("--agents-config", default="configs/agents.yaml")
    run.add_argument("--benchmark-config", default="configs/benchmarks.yaml")
    run.add_argument("--report-dir", default="reports")
    run.add_argument(
        "--write-reports",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Write <slug>.md and the generated <slug>_strategy.py per paper "
            "into --report-dir (on by default; --no-write-reports disables)."
        ),
    )
    run.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory for run manifests; each paper run writes <runs-dir>/<run_id>/manifest.json.",
    )
    run.add_argument(
        "--processed-path",
        default=str(DEFAULT_PROCESSED_PATH),
        help="Persistent processed-paper watermark for cross-run dedup (arxiv source).",
    )
    run.add_argument(
        "--no-dedup",
        action="store_true",
        help="Disable dedup against already-processed papers (arxiv source).",
    )

    track = subparsers.add_parser(
        "track", help="Find papers in an exact online-date window and update Scout's queue."
    )
    track.add_argument(
        "--source",
        action="append",
        choices=("local", "arxiv", *VENUES, *VENUE_GROUPS),
        help=(
            "Assigned source to scan; repeat for several sources. Defaults to "
            "quant_scout.assigned_sources in the agents config."
        ),
    )
    track_query = track.add_mutually_exclusive_group()
    track_query.add_argument("--query", default="quantitative finance")
    track_query.add_argument("--query-pool", default=None)
    track.add_argument("--start-date", required=True, help="Inclusive YYYY-MM-DD online date.")
    track.add_argument("--end-date", required=True, help="Inclusive YYYY-MM-DD online date.")
    track.add_argument("--max-candidates-per-source", type=int, default=100)
    track.add_argument("--max-papers", type=int, default=50, help="Maximum ranked papers to upsert.")
    track.add_argument("--paper-json", help="Local JSON records when --source local is assigned.")
    track.add_argument("--agents-config", default="configs/agents.yaml")
    track.add_argument("--queue-path", default=str(DEFAULT_QUEUE_PATH))

    subparsers.add_parser(
        "queries", help="List the curated query pools usable with --query-pool."
    )
    return parser


def _with_default_command(argv: list[str]) -> list[str]:
    """Treat top-level options as arguments to the default run command."""

    if not argv or argv[0].startswith("-"):
        return ["run", *argv]
    return argv


def run_workflow(args: argparse.Namespace) -> list[ReviewReport]:
    """Run the initial deterministic QuantBench workflow."""

    agents_config = load_config(args.agents_config)
    benchmark_config = load_config(args.benchmark_config)
    scout_keywords = (
        agents_config.get("agents", {})
        .get("quant_scout", {})
        .get("default_keywords")
    )

    registry: ProcessedRegistry | None = None
    venue_keys = expand_source(args.source)
    query_pool = getattr(args, "query_pool", None)
    if args.source == "arxiv":
        if query_pool:
            papers = multi_query_search(
                lambda query, budget: search_arxiv(query, max_results=budget),
                resolve_pool(query_pool),
                args.max_papers,
                delay=0.5,
            )
        else:
            papers = search_arxiv(args.query, max_results=args.max_papers)
    elif venue_keys:
        if query_pool:
            papers = search_venues_pooled(
                venue_keys,
                query_pool,
                max_results=args.max_papers,
                year=getattr(args, "year", None),
            )
        else:
            papers = search_venues(
                venue_keys,
                args.query,
                max_results=args.max_papers,
                year=getattr(args, "year", None),
            )
    else:
        papers = load_local_papers(args.paper_json)

    if args.source != "local" and not getattr(args, "no_dedup", False):
        registry = ProcessedRegistry(getattr(args, "processed_path", DEFAULT_PROCESSED_PATH))
        papers = registry.filter_unseen(papers)

    agent_skills = {
        name: resolve_skills(name, agents_config)
        for name in (
            "quant_scout",
            "quant_reader",
            "quant_coder",
            "quant_bench",
            "quant_reviewer",
        )
    }
    runs_dir = getattr(args, "runs_dir", None)
    if any(agent_skills.values()) and not runs_dir:
        raise ValueError(
            "Enabled skills record results in run manifests; pass --runs-dir "
            "(or disable the skills in the agents config)."
        )

    scout = QuantScoutAgent(
        keywords=scout_keywords,
        skills=agent_skills["quant_scout"],
        charter=load_charter(agents_config),
        relevance_boost=_configured_relevance_boost(agents_config),
    )
    reader = QuantReaderAgent(skills=agent_skills["quant_reader"])
    coder = QuantCoderAgent(skills=agent_skills["quant_coder"])
    bench = QuantBenchAgent(skills=agent_skills["quant_bench"])
    reviewer = QuantReviewerAgent(skills=agent_skills["quant_reviewer"])

    # Volatile inputs (timestamps, run ids) stay out of this hash so reruns
    # on identical inputs produce identical manifest content hashes.
    run_config = {"agents": agents_config, "benchmarks": benchmark_config}

    reports: list[ReviewReport] = []
    strategy_sources: dict[str, str] = {}
    ranked = scout.rank(papers, max_papers=args.max_papers)
    for scored in ranked:
        ctx = None
        manifest = store = None
        if runs_dir:
            manifest, store = start_run(Path(runs_dir), scored.paper.slug, run_config)
            ctx = RunContext(
                run_id=manifest.run_id,
                run_dir=store.run_dir,
                config=agents_config,
                manifest=manifest,
                llm=build_llm_client(agents_config, manifest),
            )

        triage = scout.triage(scored, ctx)
        if triage is not None and not triage.payload.get("passes_gate", True):
            # Gated papers still write their manifest: the triage decision is
            # part of the trial record, not something to discard silently.
            if manifest is not None and store is not None:
                manifest.save(store.run_dir)
            continue

        scout.record_relevance(scored, ctx)
        analysis = reader.analyze(scored.paper, ctx=ctx)
        if scored.relevance is not None:
            analysis = replace(analysis, relevance=scored.relevance)
        implementation_plan = coder.plan(analysis)
        # Close performance-affecting MethodSpec gaps by consulting the Reader
        # before any code is written (no-op unless the skill is enabled).
        coder.consult_reader(analysis, ctx)
        codegen = coder.generate(analysis, implementation_plan, ctx)
        # Synthesize any paper-claimed metric the built-in suite lacks, so
        # the bench can claim-compare it (validated modules become artifacts).
        coder.synthesize_metrics(analysis, ctx)
        if codegen is not None and store is not None:
            code_file = store.run_dir / str(codegen.payload.get("code_path", ""))
            if code_file.is_file():
                strategy_sources[scored.paper.slug] = code_file.read_text(encoding="utf-8")
        benchmark_result = bench.evaluate(
            implementation_plan, analysis=analysis, ctx=ctx
        )
        report = reviewer.review(
            analysis, implementation_plan, benchmark_result, ctx=ctx
        )
        reports.append(report)

        if manifest is not None and store is not None:
            store.write_text("report.md", report.to_markdown())
            manifest.save(store.run_dir)

    if registry is not None:
        # Every ranked paper has now been looked at (processed or gated);
        # mark them so a re-run of the same window fetches nothing new.
        for scored in ranked:
            registry.mark(scored.paper)
        registry.save()

    if args.write_reports:
        write_reports(reports, Path(args.report_dir), strategy_sources)

    return reports


def track_new_papers(args: argparse.Namespace) -> dict[str, object]:
    """Discover, strictly date-filter, rank, and upsert Scout's paper queue."""

    agents_config = load_config(args.agents_config)
    scout_config = (agents_config.get("agents") or {}).get("quant_scout") or {}
    sources = tuple(args.source or scout_config.get("assigned_sources") or ("arxiv",))
    start_date = parse_iso_date(args.start_date, "start-date")
    end_date = parse_iso_date(args.end_date, "end-date")
    if start_date > end_date:
        raise ValueError("start-date must be on or before end-date")

    candidates: list = []
    for source in sources:
        candidates.extend(_discover_for_tracking(source, args, start_date, end_date))
    unique = deduplicate_papers(candidates)
    filtered = filter_by_online_date(unique, start_date, end_date)
    source_counts = Counter(paper.source for paper in candidates)
    source_failures = sorted(
        source.removesuffix("-placeholder")
        for source in source_counts
        if source.endswith("-placeholder")
    )

    scout = QuantScoutAgent(
        keywords=(),
        skills={"relevance_scorer": RelevanceScorerSkill()},
        charter=load_charter(agents_config),
        relevance_boost=1.0,
    )
    ranked = scout.rank(filtered.in_window, max_papers=args.max_papers)
    queue = ResearchQueue(args.queue_path)
    update = queue.upsert(ranked, start_date, end_date)
    queue_path = queue.save()

    return {
        "window": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "sources": list(sources),
        "source_counts": dict(sorted(source_counts.items())),
        "source_failures": source_failures,
        "discovered": len(candidates),
        "unique": len(unique),
        "in_window": len(filtered.in_window),
        "outside_window": len(filtered.outside_window),
        "missing_exact_online_date": len(filtered.missing_exact_date),
        "queue": {
            "path": str(queue_path),
            "added": update.added,
            "updated": update.updated,
            "total": update.total,
        },
        "ranked": [
            {
                "rank": index,
                "title": scored.paper.title,
                "score": round(scored.score, 4),
                "research_value": round(scored.relevance.score, 4)
                if scored.relevance
                else None,
            }
            for index, scored in enumerate(ranked, start=1)
        ],
    }


def _discover_for_tracking(
    source: str, args: argparse.Namespace, start_date: date, end_date: date
) -> list:
    """Fetch a bounded candidate set from one assigned source."""

    budget = max(1, args.max_candidates_per_source)
    query_pool = getattr(args, "query_pool", None)
    if source == "local":
        return load_local_papers(args.paper_json)
    if source == "arxiv":
        if query_pool:
            return multi_query_search(
                lambda query, per_query: search_arxiv(
                    query,
                    max_results=per_query,
                    start_date=start_date,
                    end_date=end_date,
                ),
                resolve_pool(query_pool),
                budget,
                delay=0.5,
            )
        return search_arxiv(
            args.query,
            max_results=budget,
            start_date=start_date,
            end_date=end_date,
        )

    venue_keys = expand_source(source)
    if not venue_keys:
        return []
    if all(VENUES[venue]["kind"] == "journal" for venue in venue_keys):
        if query_pool:
            return search_venues_pooled(
                venue_keys,
                query_pool,
                max_results=budget,
                start_date=start_date,
                end_date=end_date,
            )
        return search_venues(
            venue_keys,
            args.query,
            max_results=budget,
            start_date=start_date,
            end_date=end_date,
        )

    papers = []
    for year in range(start_date.year, end_date.year + 1):
        if query_pool:
            papers.extend(
                search_venues_pooled(
                    venue_keys,
                    query_pool,
                    max_results=budget,
                    year=year,
                )
            )
        else:
            papers.extend(
                search_venues(venue_keys, args.query, max_results=budget, year=year)
            )
    return papers


def _configured_relevance_boost(config: Mapping[str, Any]) -> float:
    scout = (config.get("agents") or {}).get("quant_scout") or {}
    skills = scout.get("skills") or {}
    scorer = skills.get("relevance_scorer") or {}
    if scorer.get("enabled", False):
        return research_value_boost(config)
    return relevance_boost(config)


def write_reports(
    reports: list[ReviewReport],
    report_dir: Path,
    strategy_sources: dict[str, str] | None = None,
) -> None:
    """Write each paper's review markdown and its generated strategy module."""

    report_dir.mkdir(parents=True, exist_ok=True)
    for report in reports:
        slug = report.paper.slug
        path = report_dir / f"{slug}.md"
        path.write_text(report.to_markdown(), encoding="utf-8")
        source = (strategy_sources or {}).get(slug)
        if source:
            (report_dir / f"{slug}_strategy.py").write_text(source, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
