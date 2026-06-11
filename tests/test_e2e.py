"""QB-16: golden-paper end-to-end reproduction and the synthetic-noise gate.

Run with ``pytest -m e2e``. Both tests run the full pipeline through
``run_workflow`` with every skill enabled and the LLM provider set to
``none``, so the path is deterministic and offline (metadata/abstract
fallbacks, no network, no recorded fixtures required).
"""

import json
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from quantbench_crew.config import load_config
from quantbench_crew.main import run_workflow

pytestmark = pytest.mark.e2e

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = str(FIXTURES / "golden_paper.json")


def _config(tmp_path: Path, dataset: str, params: dict) -> str:
    config = load_config("configs/agents.yaml")
    agents = config["agents"]
    agents["quant_scout"]["skills"]["reproducibility_triage"]["enabled"] = True
    for name in ("pdf_acquisition", "method_spec_extraction", "target_table_extraction"):
        agents["quant_reader"]["skills"][name]["enabled"] = True
    agents["quant_coder"]["skills"]["code_generation"]["enabled"] = True
    agents["quant_bench"]["skills"]["dataset_registry"]["enabled"] = True
    agents["quant_bench"]["skills"]["dataset_registry"]["dataset"] = dataset
    agents["quant_bench"]["skills"]["dataset_registry"]["params"] = params
    agents["quant_bench"]["skills"]["walk_forward"]["enabled"] = True
    agents["quant_reviewer"]["skills"]["rubric_verdict"]["enabled"] = True
    path = tmp_path / f"agents-{dataset}.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return str(path)


def _args(tmp_path: Path, config_path: str, runs_subdir: str) -> Namespace:
    return Namespace(
        source="local",
        query="momentum",
        max_papers=1,
        paper_json=GOLDEN,
        agents_config=config_path,
        benchmark_config="configs/benchmarks.yaml",
        report_dir=str(tmp_path / "reports"),
        write_reports=False,
        runs_dir=str(tmp_path / runs_subdir),
    )


def _manifest(runs_dir: Path) -> dict:
    return json.loads(next(runs_dir.glob("*/manifest.json")).read_text(encoding="utf-8"))


# Planted spread is ~1.4737 * strength; calibrate so the long-short earns the
# paper's ~0.95%/month headline and the reproduction genuinely succeeds.
CALIBRATED = {"strength": 0.0095 / 1.4737, "noise": 0.0008, "n_periods": 240, "seed": 0}


def test_golden_paper_reproduces_end_to_end(tmp_path: Path) -> None:
    config_path = _config(tmp_path, "planted_momentum", CALIBRATED)
    reports = run_workflow(_args(tmp_path, config_path, "runs"))

    assert len(reports) == 1
    report = reports[0]

    # A real, evidence-cited verdict — never the placeholder "promising".
    assert report.verdict == "promising"
    assert report.rubric
    assert all(score.evidence for score in report.rubric if score.score > 0)

    # The headline claim was extracted and reproduced within tolerance.
    comparison = report.benchmark_result.comparisons[0]
    assert comparison.claim.value == pytest.approx(0.0095)
    assert comparison.within_tolerance

    # Beats the random-matched-turnover significance floor.
    walk_forward = next(
        entry for entry in _manifest(tmp_path / "runs")["skill_results"]
        if entry["skill"] == "walk_forward"
    )
    assert walk_forward["payload"]["beats_random_null"] is True


def test_golden_run_is_deterministic(tmp_path: Path) -> None:
    config_path = _config(tmp_path, "planted_momentum", CALIBRATED)
    run_workflow(_args(tmp_path, config_path, "runs-a"))
    run_workflow(_args(tmp_path, config_path, "runs-b"))

    first = _manifest(tmp_path / "runs-a")
    second = _manifest(tmp_path / "runs-b")
    assert first["run_id"] != second["run_id"]
    assert first["content_hash"] == second["content_hash"]


def test_noise_world_gate_does_not_reproduce(tmp_path: Path) -> None:
    """Across seeds, pure noise must not be flagged as a reproduction."""

    seeds = range(10)
    false_positives = 0
    for seed in seeds:
        config_path = _config(tmp_path, "pure_noise", {"seed": seed})
        reports = run_workflow(_args(tmp_path, config_path, f"runs-noise-{seed}"))
        report = reports[0]

        # No reproduction may be claimed on noise.
        assert not report.benchmark_result.comparisons[0].within_tolerance
        assert report.verdict != "promising"
        if report.verdict == "promising":
            false_positives += 1

    # False-discovery rate stays at/under the 1-in-10 gate threshold.
    assert false_positives <= 1
