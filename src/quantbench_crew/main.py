"""Command-line entry point for QuantBench Crew."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, replace
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
from quantbench_crew.config import init_env_file, load_config, load_env_file
from quantbench_crew.feedback import (
    ingest_report_feedback,
    merge_preserved_feedback,
    report_metadata,
)
from quantbench_crew.llm import build_llm_client
from quantbench_crew.memory import (
    DEFAULT_ARCHIVE_DIR,
    DEFAULT_MEMORY_PATH,
    SQLiteMemoryStore,
)
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

    if args.command == "init":
        env_path = init_env_file(args.env_file, template=args.template, force=args.force)
        print(
            f"Created {env_path}. Add your API keys there, then run "
            "`quantbench run ...`. Leave keys blank to use offline fallbacks."
        )
        return 0

    load_env_file(getattr(args, "env_file", ".env"))

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
    if args.command == "feedback":
        return _run_feedback_command(args)
    if args.command == "memory":
        return _run_memory_command(args)

    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quantbench",
        description="Run QuantBench Crew research workflows.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init = subparsers.add_parser(
        "init", help="Create a local .env file for API keys from .env.example."
    )
    init.add_argument(
        "--env-file",
        default=".env",
        help="Path to create for local secrets and workflow defaults.",
    )
    init.add_argument(
        "--template",
        default=".env.example",
        help="Template dotenv file to copy.",
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing env file.",
    )

    run = subparsers.add_parser("run", help="Run the paper review workflow.")
    run.add_argument(
        "--env-file",
        default=".env",
        help="Load API keys and workflow defaults from this dotenv file.",
    )
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
    run.add_argument(
        "--use-memory",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Enable approved persistent-memory recall for this run. When omitted, "
            "the top-level memory.enabled setting in agents.yaml is used."
        ),
    )
    run.add_argument(
        "--memory-db",
        default=None,
        help="SQLite memory database path (defaults to config or data/quantbench_memory.sqlite3).",
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
    track.add_argument(
        "--env-file",
        default=".env",
        help="Load API keys and workflow defaults from this dotenv file.",
    )

    subparsers.add_parser(
        "queries", help="List the curated query pools usable with --query-pool."
    )

    feedback = subparsers.add_parser(
        "feedback", help="Ingest and govern human proofreading notes."
    )
    feedback_sub = feedback.add_subparsers(dest="feedback_command", required=True)
    feedback_ingest = feedback_sub.add_parser(
        "ingest", help="Extract notes from one or more Markdown reports."
    )
    feedback_ingest.add_argument("reports", nargs="+")
    feedback_ingest.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    feedback_ingest.add_argument(
        "--category",
        choices=("factual_correction", "method_gap", "bug", "style", "process_guidance"),
        default="",
    )
    feedback_ingest.add_argument(
        "--scope", choices=("global", "agent", "paper", "agent_paper"), default=""
    )
    feedback_ingest.add_argument("--scope-key", default="")
    feedback_ingest.add_argument("--agent", choices=(
        "quant_scout",
        "quant_reader",
        "quant_coder",
        "quant_bench",
        "quant_reviewer",
    ), default="")

    feedback_list = feedback_sub.add_parser("list", help="List feedback records.")
    feedback_list.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    feedback_list.add_argument(
        "--status", choices=("new", "proposed", "approved", "rejected"), default=""
    )

    feedback_approve = feedback_sub.add_parser(
        "approve", help="Approve feedback and promote it into active memory."
    )
    feedback_approve.add_argument("feedback_id")
    feedback_approve.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    feedback_approve.add_argument("--reviewer", default="")
    feedback_approve.add_argument("--importance", type=float, default=0.8)

    feedback_reject = feedback_sub.add_parser(
        "reject", help="Reject a proposed feedback record."
    )
    feedback_reject.add_argument("feedback_id")
    feedback_reject.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    feedback_reject.add_argument("--reviewer", default="")

    memory = subparsers.add_parser(
        "memory", help="Inspect and maintain persistent agent memory."
    )
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)
    memory_inspect = memory_sub.add_parser("inspect", help="Show database counts.")
    memory_inspect.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))

    memory_add = memory_sub.add_parser("remember", help="Add an explicit memory record.")
    memory_add.add_argument("content")
    memory_add.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    memory_add.add_argument(
        "--kind", choices=("episodic", "semantic", "procedural", "prospective"),
        default="semantic",
    )
    memory_add.add_argument(
        "--scope", choices=("global", "agent", "paper", "agent_paper"), default="global"
    )
    memory_add.add_argument("--scope-key", default="")
    memory_add.add_argument(
        "--status", choices=("proposed", "approved"), default="proposed"
    )
    memory_add.add_argument("--importance", type=float, default=0.5)
    memory_add.add_argument("--tag", action="append", default=[])

    memory_approve = memory_sub.add_parser(
        "approve", help="Promote a proposed memory into active recall."
    )
    memory_approve.add_argument("memory_id")
    memory_approve.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))

    memory_recall = memory_sub.add_parser("recall", help="Preview scoped approved recall.")
    memory_recall.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    memory_recall.add_argument("--agent", required=True, choices=(
        "quant_scout",
        "quant_reader",
        "quant_coder",
        "quant_bench",
        "quant_reviewer",
    ))
    memory_recall.add_argument("--paper-slug", default="")
    memory_recall.add_argument("--query", default="")
    memory_recall.add_argument("--limit", type=int, default=8)

    memory_consolidate = memory_sub.add_parser(
        "consolidate", help="Create a deterministic monthly consolidation digest."
    )
    memory_consolidate.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    memory_consolidate.add_argument("--month", required=True, help="Month in YYYY-MM form.")

    memory_archive = memory_sub.add_parser(
        "archive", help="Archive cold events and inactive memories."
    )
    memory_archive.add_argument("--db", default=str(DEFAULT_MEMORY_PATH))
    memory_archive.add_argument("--older-than-days", type=int, default=90)
    memory_archive.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
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
        discovered_count = len(papers)
        papers = registry.filter_unseen(papers)
        if discovered_count and not papers:
            print(
                "No new papers to review after deduplication against "
                f"{registry.path}. Use --no-dedup to rerun the same papers, "
                "or pass --processed-path to use a fresh watermark.",
                file=sys.stderr,
            )

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
    memory_config = agents_config.get("memory") or {}
    requested_memory = getattr(args, "use_memory", None)
    memory_enabled = (
        bool(memory_config.get("enabled", False))
        if requested_memory is None
        else bool(requested_memory)
    )
    memory_path = (
        getattr(args, "memory_db", None)
        or memory_config.get("path")
        or str(DEFAULT_MEMORY_PATH)
    )
    memory_store = SQLiteMemoryStore(memory_path) if memory_enabled else None
    if memory_store is not None:
        run_config["memory"] = {
            "enabled": True,
            "path": str(memory_path),
            "recall_limit": int(memory_config.get("recall_limit", 8)),
        }

    reports: list[ReviewReport] = []
    strategy_sources: dict[str, str] = {}
    ranked = scout.rank(papers, max_papers=args.max_papers)
    for scored in ranked:
        ctx = None
        manifest = store = None
        if runs_dir:
            manifest, store = start_run(Path(runs_dir), scored.paper.slug, run_config)
            recalled = {}
            if memory_store is not None:
                memory_store.record_run_started(manifest)
                recall_query = f"{scored.paper.title} {scored.paper.abstract}"
                recall_limit = int(memory_config.get("recall_limit", 8))
                for agent_name in agent_skills:
                    memories = memory_store.retrieve(
                        agent=agent_name,
                        paper_slug=scored.paper.slug,
                        query=recall_query,
                        limit=recall_limit,
                    )
                    recalled[agent_name] = memories
                    for memory in memories:
                        manifest.record_memory_read(
                            {
                                "agent": agent_name,
                                "memory_id": memory.memory_id,
                                "content_hash": memory.content_hash,
                                "kind": memory.kind,
                                "scope": memory.scope,
                                "scope_key": memory.scope_key,
                            }
                        )
            ctx = RunContext(
                run_id=manifest.run_id,
                run_dir=store.run_dir,
                config=agents_config,
                manifest=manifest,
                llm=build_llm_client(agents_config, manifest),
                memory=memory_store,
                recalled_memories=recalled,
            )

        triage = scout.triage(scored, ctx)
        if triage is not None and not triage.payload.get("passes_gate", True):
            # Gated papers still write their manifest: the triage decision is
            # part of the trial record, not something to discard silently.
            if manifest is not None and store is not None:
                manifest.save(store.run_dir)
                if memory_store is not None:
                    memory_store.record_manifest(manifest, status="gated")
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
            report_markdown = report.to_markdown()
            store.write_text("report.md", report_markdown)
            manifest.save(store.run_dir)
            if memory_store is not None:
                memory_store.record_manifest(manifest)

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
        markdown = report.to_markdown()
        metadata = report_metadata(markdown)
        if path.exists():
            markdown = merge_preserved_feedback(
                markdown,
                path.read_text(encoding="utf-8"),
                run_id=metadata.get("run_id", ""),
                paper_slug=metadata.get("paper_slug", slug),
            )
        path.write_text(markdown, encoding="utf-8")
        source = (strategy_sources or {}).get(slug)
        if source:
            (report_dir / f"{slug}_strategy.py").write_text(source, encoding="utf-8")


def _run_feedback_command(args: argparse.Namespace) -> int:
    store = SQLiteMemoryStore(args.db)
    if args.feedback_command == "ingest":
        results = []
        for report in args.reports:
            record, created = ingest_report_feedback(
                report,
                store,
                category=args.category,
                scope=args.scope,
                scope_key=args.scope_key,
                target_agent=args.agent,
            )
            results.append({**asdict(record), "created": created})
        print(json.dumps(results, indent=2, sort_keys=True))
        return 0
    if args.feedback_command == "list":
        print(
            json.dumps(
                [asdict(item) for item in store.list_feedback(status=args.status)],
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.feedback_command == "approve":
        memory = store.approve_feedback(
            args.feedback_id,
            reviewer=args.reviewer,
            importance=args.importance,
        )
        print(json.dumps(asdict(memory), indent=2, sort_keys=True))
        return 0
    if args.feedback_command == "reject":
        store.reject_feedback(args.feedback_id, reviewer=args.reviewer)
        print(json.dumps({"feedback_id": args.feedback_id, "status": "rejected"}))
        return 0
    raise ValueError(f"unknown feedback command: {args.feedback_command}")


def _run_memory_command(args: argparse.Namespace) -> int:
    store = SQLiteMemoryStore(args.db)
    if args.memory_command == "inspect":
        print(json.dumps(store.inspect(), indent=2, sort_keys=True))
        return 0
    if args.memory_command == "remember":
        memory = store.remember(
            args.content,
            kind=args.kind,
            scope=args.scope,
            scope_key=args.scope_key,
            status=args.status,
            importance=args.importance,
            tags=args.tag,
            source_type="operator",
        )
        print(json.dumps(asdict(memory), indent=2, sort_keys=True))
        return 0
    if args.memory_command == "approve":
        memory = store.set_memory_status(args.memory_id, "approved")
        print(json.dumps(asdict(memory), indent=2, sort_keys=True))
        return 0
    if args.memory_command == "recall":
        memories = store.retrieve(
            agent=args.agent,
            paper_slug=args.paper_slug,
            query=args.query,
            limit=args.limit,
        )
        print(json.dumps([asdict(item) for item in memories], indent=2, sort_keys=True))
        return 0
    if args.memory_command == "consolidate":
        result = store.consolidate_month(args.month)
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return 0
    if args.memory_command == "archive":
        result = store.archive_older_than(
            args.older_than_days,
            archive_dir=args.archive_dir,
        )
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return 0
    raise ValueError(f"unknown memory command: {args.memory_command}")


if __name__ == "__main__":
    raise SystemExit(main())
