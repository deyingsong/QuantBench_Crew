import json
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from quantbench_crew.config import load_config
from quantbench_crew.main import run_workflow

FIXTURES = Path(__file__).parent / "fixtures"


def test_run_workflow_returns_review_reports(tmp_path: Path) -> None:
    # The shipped config enables code_generation, so a runs dir is required.
    args = Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=None,
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path / "reports"),
        write_reports=False,
        runs_dir=str(tmp_path / "runs"),
    )

    reports = run_workflow(args)

    assert len(reports) == 1
    assert reports[0].paper.title
    assert "research review only" in reports[0].to_markdown()


def test_write_reports_creates_markdown_and_strategy(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    args = Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=None,
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(report_dir),
        write_reports=True,
        runs_dir=str(tmp_path / "runs"),
    )
    reports = run_workflow(args)

    generated = list(report_dir.glob("*.md"))
    assert len(generated) == 1
    assert generated[0].read_text(encoding="utf-8").startswith("# ")
    strategies = list(report_dir.glob("*_strategy.py"))
    assert len(strategies) == 1
    assert "def build_strategy" in strategies[0].read_text(encoding="utf-8")
    assert reports  # workflow returned the same papers it wrote


def test_run_workflow_reads_local_json_source(tmp_path: Path) -> None:
    paper_json = tmp_path / "papers.json"
    paper_json.write_text(
        """
        [
          {
            "title": "Portfolio Forecasting with Transaction Costs",
            "abstract": "A forecasting method for portfolio returns with turnover controls.",
            "authors": ["Researcher D"],
            "keywords": ["portfolio", "forecasting"]
          }
        ]
        """,
        encoding="utf-8",
    )
    args = Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=str(paper_json),
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path / "reports"),
        write_reports=False,
        runs_dir=str(tmp_path / "runs"),
    )

    reports = run_workflow(args)

    assert reports[0].paper.authors == ("Researcher D",)
    assert reports[0].paper.title == "Portfolio Forecasting with Transaction Costs"


def _run_args(tmp_path: Path, runs_subdir: str) -> Namespace:
    return Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=None,
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path / "reports"),
        write_reports=False,
        runs_dir=str(tmp_path / runs_subdir),
    )


def _load_manifests(runs_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(runs_dir.glob("*/manifest.json"))
    ]


def test_run_workflow_writes_manifest_per_paper_run(tmp_path: Path) -> None:
    run_workflow(_run_args(tmp_path, "runs"))

    manifests = _load_manifests(tmp_path / "runs")
    assert len(manifests) == 1
    manifest = manifests[0]
    assert manifest["paper_slug"]
    assert manifest["config_hash"]
    assert "report.md" in manifest["artifacts"]
    run_dir = next((tmp_path / "runs").glob("*"))
    assert (run_dir / "report.md").exists()


def test_rerun_with_identical_inputs_has_identical_content_hash(tmp_path: Path) -> None:
    run_workflow(_run_args(tmp_path, "runs-a"))
    run_workflow(_run_args(tmp_path, "runs-b"))

    first = _load_manifests(tmp_path / "runs-a")[0]
    second = _load_manifests(tmp_path / "runs-b")[0]
    assert first["run_id"] != second["run_id"]
    assert first["content_hash"] == second["content_hash"]


def _skills_enabled_config(tmp_path: Path) -> str:
    """Shipped config with the Workstream B and C skills toggled on."""

    config = load_config("configs/agents.yaml")
    # Pin offline: the shipped default is a live OpenAI backbone, which
    # must never place network calls from tests even when keys are exported.
    config["llm"]["provider"] = "none"
    agents = config["agents"]
    for agent in agents.values():
        for skill in (agent.get("skills") or {}).values():
            if isinstance(skill, dict) and "enabled" in skill:
                skill["enabled"] = False
    agents["quant_scout"]["skills"]["reproducibility_triage"]["enabled"] = True
    agents["quant_scout"]["skills"]["charter_relevance"]["enabled"] = True
    for name in (
        "pdf_acquisition",
        "method_spec_extraction",
        "target_table_extraction",
        "red_flag_scan",
    ):
        agents["quant_reader"]["skills"][name]["enabled"] = True
    agents["quant_coder"]["skills"]["code_generation"]["enabled"] = True
    agents["quant_coder"]["skills"]["metric_synthesis"]["enabled"] = True
    agents["quant_bench"]["skills"]["dataset_registry"]["enabled"] = True
    agents["quant_bench"]["skills"]["walk_forward"]["enabled"] = True
    agents["quant_reviewer"]["skills"]["rubric_verdict"]["enabled"] = True
    path = tmp_path / "agents-skills.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return str(path)


def _skills_args(tmp_path: Path, paper_json: str | None) -> Namespace:
    return Namespace(
        source="local",
        query="momentum",
        max_papers=1,
        paper_json=paper_json,
        agents_config=_skills_enabled_config(tmp_path),
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path / "reports"),
        write_reports=False,
        runs_dir=str(tmp_path / "runs"),
    )


def test_golden_paper_flows_through_enabled_skills(tmp_path: Path) -> None:
    args = _skills_args(tmp_path, str(FIXTURES / "golden_paper.json"))

    reports = run_workflow(args)

    assert len(reports) == 1
    analysis = reports[0].analysis
    assert analysis.method_spec is not None
    assert analysis.method_spec.frequency == "monthly"
    assert analysis.reproduction_target is not None
    assert analysis.reproduction_target.claims[0].value == pytest.approx(0.0095)
    # Charter relevance attached; red-flag scan caught the gross-of-cost claim.
    assert analysis.relevance is not None
    assert analysis.relevance.method == "charter_overlap"
    assert "no_transaction_costs" in {flag.kind for flag in analysis.red_flags}

    manifest = _load_manifests(tmp_path / "runs")[0]
    recorded = {entry["skill"] for entry in manifest["skill_results"]}
    assert recorded == {
        "charter_relevance",
        "reproducibility_triage",
        "pdf_acquisition",
        "method_spec_extraction",
        "target_table_extraction",
        "red_flag_scan",
        "code_generation",
        "metric_synthesis",
        "dataset_registry",
        "walk_forward",
        "rubric_verdict",
    }
    # The golden paper's claim (monthly_return) is covered by the built-in
    # suite, so metric synthesis correctly records a no-op.
    synthesis = next(
        entry for entry in manifest["skill_results"]
        if entry["skill"] == "metric_synthesis"
    )
    assert synthesis["status"] == "skipped"
    assert synthesis["payload"]["missing"] == []
    triage = next(
        entry for entry in manifest["skill_results"]
        if entry["skill"] == "reproducibility_triage"
    )
    assert triage["payload"]["passes_gate"] is True
    codegen = next(
        entry for entry in manifest["skill_results"]
        if entry["skill"] == "code_generation"
    )
    assert codegen["status"] == "ok"
    assert codegen["payload"]["tests_passed"] == codegen["payload"]["tests_total"] >= 3
    assert "generated/strategy.py" in manifest["artifacts"]

    # Bench: the planted-momentum world beats the random null and the golden
    # claim is compared against the achieved metric.
    walk_forward = next(
        entry for entry in manifest["skill_results"] if entry["skill"] == "walk_forward"
    )
    assert walk_forward["payload"]["beats_random_null"] is True
    assert walk_forward["payload"]["comparisons"][0]["metric"] == "monthly_return"
    assert "benchmark/walk_forward.json" in manifest["artifacts"]
    benchmark = reports[0].benchmark_result
    assert benchmark.dataset == "planted_momentum"
    assert len(benchmark.comparisons) == 1

    # Reviewer: a real, evidence-cited rubric — not the placeholder verdict.
    report = reports[0]
    assert report.verdict != "scaffold-only"
    assert {score.dimension for score in report.rubric} == {
        "reproducibility",
        "robustness",
        "net_of_cost_viability",
        "novelty_vs_baselines",
        "data_accessibility",
    }
    assert all(score.evidence for score in report.rubric if score.score > 0)
    assert "## Rubric" in report.to_markdown()


def test_low_feasibility_paper_is_gated_but_audited(tmp_path: Path) -> None:
    paper_json = tmp_path / "proprietary.json"
    paper_json.write_text(
        json.dumps(
            [
                {
                    "title": "Alpha from Internal Order Flow",
                    "abstract": "We use proprietary internal data from an order-level feed.",
                    "keywords": ["microstructure"],
                }
            ]
        ),
        encoding="utf-8",
    )
    args = _skills_args(tmp_path, str(paper_json))

    reports = run_workflow(args)

    assert reports == []
    manifest = _load_manifests(tmp_path / "runs")[0]
    triage = manifest["skill_results"][0]
    assert triage["payload"]["passes_gate"] is False
    # Gated runs keep their manifest but never produce a report artifact.
    assert "report.md" not in manifest["artifacts"]


def test_enabled_skills_require_runs_dir(tmp_path: Path) -> None:
    args = _skills_args(tmp_path, str(FIXTURES / "golden_paper.json"))
    args.runs_dir = None

    with pytest.raises(ValueError, match="runs-dir"):
        run_workflow(args)
