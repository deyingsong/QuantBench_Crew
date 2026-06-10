import json
from argparse import Namespace
from pathlib import Path

from quantbench_crew.main import run_workflow, write_reports


def test_run_workflow_returns_review_reports() -> None:
    args = Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=None,
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir="reports",
        write_reports=False,
    )

    reports = run_workflow(args)

    assert len(reports) == 1
    assert reports[0].paper.title
    assert "research review only" in reports[0].to_markdown()


def test_write_reports_creates_markdown(tmp_path: Path) -> None:
    args = Namespace(
        source="local",
        query="asset pricing",
        max_papers=1,
        paper_json=None,
        agents_config="configs/agents.yaml",
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path),
        write_reports=False,
    )
    reports = run_workflow(args)

    write_reports(reports, tmp_path)

    generated = list(tmp_path.glob("*.md"))
    assert len(generated) == 1
    assert generated[0].read_text(encoding="utf-8").startswith("# ")


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
        report_dir=str(tmp_path),
        write_reports=False,
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
