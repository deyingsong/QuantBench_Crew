"""Metric synthesis: detect unmapped claims, generate, validate, bench-apply."""

import pytest

from quantbench_crew.datasets.registry import load_dataset
from quantbench_crew.llm import DEFAULT_MODEL, RecordedStubClient, request_fingerprint
from quantbench_crew.models import Claim, Paper, PaperAnalysis, ReproductionTarget
from quantbench_crew.skills.bench.walk_forward import WalkForwardSkill
from quantbench_crew.skills.coder.metric_synthesis import (
    SYSTEM_PROMPT,
    MetricSynthesisSkill,
    build_metric_prompt,
    run_metric,
)

OMEGA_MODULE = '''def compute_metric(returns, periods_per_year):
    gains = sum(r for r in returns if r > 0)
    losses = -sum(r for r in returns if r < 0)
    if losses == 0.0:
        return 0.0
    return gains / losses
'''


def _analysis(*claims: Claim) -> PaperAnalysis:
    paper = Paper(title="Omega Paper", abstract="omega")
    return PaperAnalysis(
        paper=paper,
        research_question="q",
        proposed_method="momentum",
        assumptions=(),
        datasets=(),
        metrics=(),
        limitations=(),
        reproduction_target=ReproductionTarget(paper=paper, claims=tuple(claims)),
    )


def _omega_claim() -> Claim:
    return Claim(metric="Omega Ratio", value=2.6, unit="ratio", tolerance=0.5)


def _fixture_client(module: str) -> RecordedStubClient:
    prompt = build_metric_prompt(_omega_claim())
    return RecordedStubClient(
        {
            request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT): {
                "text": f"```python\n{module}```",
                "model": DEFAULT_MODEL,
                "input_tokens": 50,
                "output_tokens": 80,
            }
        }
    )


# --- run_metric (the sandbox runner both skills share) -------------------------

def test_run_metric_executes_valid_module() -> None:
    value, error = run_metric(OMEGA_MODULE, [0.02, -0.01, 0.03], 12.0)
    assert error == ""
    assert value == pytest.approx(0.05 / 0.01)


def test_run_metric_rejects_banned_code_and_failures() -> None:
    value, error = run_metric("import os\ndef compute_metric(r, p):\n    return 1.0\n", [0.01], 12.0)
    assert value is None and "static violations" in error

    value, error = run_metric(
        "def compute_metric(r, p):\n    raise ValueError('boom')\n", [0.01], 12.0
    )
    assert value is None and "sandbox" in error

    value, error = run_metric(
        "def compute_metric(r, p):\n    return float('inf')\n", [0.01], 12.0
    )
    assert value is None and "non-finite" in error


# --- the skill ------------------------------------------------------------------

def test_all_covered_claims_skip(make_ctx) -> None:
    result = MetricSynthesisSkill().run(
        make_ctx(), analysis=_analysis(Claim(metric="sharpe", value=1.0))
    )
    assert result.status == "skipped"
    assert result.payload["missing"] == []


def test_offline_records_missing_and_skips(make_ctx) -> None:
    result = MetricSynthesisSkill().run(make_ctx(), analysis=_analysis(_omega_claim()))

    assert result.status == "skipped"
    assert result.payload["missing"] == ["omega_ratio"]
    assert any("no LLM configured" in note for note in result.notes)


def test_llm_path_synthesizes_and_validates(make_ctx) -> None:
    ctx = make_ctx()
    ctx.llm = _fixture_client(OMEGA_MODULE)

    result = MetricSynthesisSkill().run(ctx, analysis=_analysis(_omega_claim()))

    assert result.status == "ok"
    entry = result.payload["synthesized"]["omega_ratio"]
    assert entry["validated"] is True
    assert (ctx.run_dir / entry["path"]).is_file()
    assert "def compute_metric" in (ctx.run_dir / entry["path"]).read_text(encoding="utf-8")


def test_invalid_generated_code_fails_validation(make_ctx) -> None:
    ctx = make_ctx()
    ctx.llm = _fixture_client("def compute_metric(r, p):\n    return eval('1')\n")

    result = MetricSynthesisSkill().run(ctx, analysis=_analysis(_omega_claim()))

    assert result.status == "skipped"
    assert result.payload["synthesized"] == {}
    assert any("validation failed" in note for note in result.notes)


def test_cost_cap_blocks_generation(make_ctx) -> None:
    ctx = make_ctx(config={"llm": {"cost_cap_usd": 0.5}})
    ctx.manifest.record_llm_call({"cost_usd": 1.0})
    ctx.llm = RecordedStubClient({})  # would raise if a call were placed

    result = MetricSynthesisSkill().run(ctx, analysis=_analysis(_omega_claim()))

    assert result.status == "skipped"
    assert any("cost cap" in note for note in result.notes)


# --- bench applies synthesized metrics to the OOS series ------------------------

def test_walk_forward_merges_synthesized_metric(make_ctx) -> None:
    ctx = make_ctx()
    ctx.llm = _fixture_client(OMEGA_MODULE)
    analysis = _analysis(_omega_claim())
    MetricSynthesisSkill().run(ctx, analysis=analysis)

    # Noise world: mixed-sign OOS returns, so the omega ratio is finite > 0
    # (on the planted world every net return is positive and the module's
    # no-losses guard returns 0.0).
    dataset = load_dataset("pure_noise", {"seed": 0})
    result = WalkForwardSkill().run(
        ctx, dataset=dataset, spec=None, target=analysis.reproduction_target
    )

    metrics = result.payload["metrics"]
    assert "omega_ratio" in metrics and metrics["omega_ratio"] > 0
    assert result.payload["synthesized_metrics"]["omega_ratio"] == metrics["omega_ratio"]
    omega = next(
        c for c in result.payload["comparisons"] if c["metric"] == "Omega Ratio"
    )
    assert "no achieved metric" not in omega["note"]
    assert omega["achieved"] == pytest.approx(metrics["omega_ratio"])
