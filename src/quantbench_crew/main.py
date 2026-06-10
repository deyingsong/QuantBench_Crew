"""Command-line entry point for QuantBench Crew."""

from __future__ import annotations

import argparse
import sys
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
from quantbench_crew.tools.arxiv_tool import load_local_papers, search_arxiv


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    normalized_argv = _with_default_command(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(normalized_argv)

    if args.command == "run":
        reports = run_workflow(args)
        for report in reports:
            print(report.to_markdown())
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
    run.add_argument("--source", choices=("local", "arxiv"), default="local")
    run.add_argument("--query", default="quantitative finance")
    run.add_argument("--max-papers", type=int, default=2)
    run.add_argument("--paper-json", help="Path to a local JSON list of paper records.")
    run.add_argument("--agents-config", default="configs/agents.yaml")
    run.add_argument("--benchmark-config", default="configs/benchmarks.yaml")
    run.add_argument("--report-dir", default="reports")
    run.add_argument("--write-reports", action="store_true")
    run.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory for run manifests; each paper run writes <runs-dir>/<run_id>/manifest.json.",
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

    papers = (
        search_arxiv(args.query, max_results=args.max_papers)
        if args.source == "arxiv"
        else load_local_papers(args.paper_json)
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

    scout = QuantScoutAgent(keywords=scout_keywords, skills=agent_skills["quant_scout"])
    reader = QuantReaderAgent(skills=agent_skills["quant_reader"])
    coder = QuantCoderAgent(skills=agent_skills["quant_coder"])
    bench = QuantBenchAgent(skills=agent_skills["quant_bench"])
    reviewer = QuantReviewerAgent(skills=agent_skills["quant_reviewer"])

    # Volatile inputs (timestamps, run ids) stay out of this hash so reruns
    # on identical inputs produce identical manifest content hashes.
    run_config = {"agents": agents_config, "benchmarks": benchmark_config}

    reports: list[ReviewReport] = []
    for scored in scout.rank(papers, max_papers=args.max_papers):
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

        analysis = reader.analyze(scored.paper, ctx=ctx)
        implementation_plan = coder.plan(analysis)
        benchmark_result = bench.evaluate(implementation_plan)
        report = reviewer.review(analysis, implementation_plan, benchmark_result)
        reports.append(report)

        if manifest is not None and store is not None:
            store.write_text("report.md", report.to_markdown())
            manifest.save(store.run_dir)

    if args.write_reports:
        write_reports(reports, Path(args.report_dir))

    return reports


def write_reports(reports: list[ReviewReport], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    for report in reports:
        path = report_dir / f"{report.paper.slug}.md"
        path.write_text(report.to_markdown(), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
