"""Command-line entry point for QuantBench Crew."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

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
        relevance_boost=relevance_boost(agents_config),
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
