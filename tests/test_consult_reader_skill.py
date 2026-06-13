"""Consult-Reader skill: deterministic gap detection + Reader resolution seam."""

import json

from quantbench_crew.agents.coder import QuantCoderAgent
from quantbench_crew.llm import (
    DEFAULT_MODEL,
    RecordedStubClient,
    request_fingerprint,
)
from quantbench_crew.models import MethodSpec, Paper, PaperAnalysis
from quantbench_crew.skills.coder.consult_reader import (
    ConsultReaderSkill,
    SYSTEM_PROMPT,
    build_consult_prompt,
    detect_gaps,
)

PAPER = Paper(title="A Momentum Strategy", abstract="We sort stocks on past returns.")


def _spec(**overrides) -> MethodSpec:
    base = dict(
        paper=PAPER,
        universe="US common stocks, price > $5",
        frequency="monthly",
        signal_definition="past 12-month return, skip last month",
        portfolio_construction="decile long-short, value-weighted",
        rebalance_frequency="monthly",
        holding_period="1 month, non-overlapping",
        extraction_confidence=0.9,
    )
    base.update(overrides)
    return MethodSpec(**base)


def _analysis(spec: MethodSpec | None) -> PaperAnalysis:
    return PaperAnalysis(
        paper=PAPER,
        research_question="Does momentum predict returns?",
        proposed_method="Cross-sectional momentum sort.",
        assumptions=(),
        datasets=("CRSP",),
        metrics=("sharpe",),
        limitations=(),
        method_spec=spec,
    )


def _config(resolve: bool = False, threshold: float = 0.5, cost_cap: float = 2.0) -> dict:
    return {
        "llm": {"cost_cap_usd": cost_cap},
        "agents": {
            "quant_coder": {
                "skills": {
                    "consult_reader": {
                        "enabled": True,
                        "resolve": resolve,
                        "confidence_threshold": threshold,
                    }
                }
            }
        },
    }


# --- pure gap detection ------------------------------------------------------

def test_detect_gaps_flags_empty_and_vague_fields() -> None:
    spec = _spec(universe="", signal_definition="not identified")
    gaps = {g["field"] for g in detect_gaps(_analysis(spec), 0.5)}
    assert "universe" in gaps and "signal_definition" in gaps
    assert "frequency" not in gaps  # complete fields are not gaps


def test_detect_gaps_flags_low_confidence() -> None:
    gaps = {g["field"] for g in detect_gaps(_analysis(_spec(extraction_confidence=0.2)), 0.5)}
    assert "overall" in gaps


def test_detect_gaps_missing_spec_covers_all_required_fields() -> None:
    gaps = {g["field"] for g in detect_gaps(_analysis(None), 0.5)}
    assert {"universe", "frequency", "signal_definition",
            "portfolio_construction", "rebalance_frequency", "holding_period"} <= gaps


def test_complete_spec_has_no_gaps() -> None:
    assert detect_gaps(_analysis(_spec()), 0.5) == []


# --- skill run ---------------------------------------------------------------

def test_complete_spec_skips_consultation(make_ctx) -> None:
    ctx = make_ctx(config=_config())
    result = ConsultReaderSkill().run(ctx, analysis=_analysis(_spec()))

    assert result.status == "skipped"
    assert result.payload["gaps"] == []
    assert not (ctx.run_dir / "generated" / "reader_consultation.json").exists()


def test_gaps_emit_questions_offline_with_default_assumptions(make_ctx) -> None:
    ctx = make_ctx(config=_config(resolve=False))
    spec = _spec(portfolio_construction="")
    result = ConsultReaderSkill().run(ctx, analysis=_analysis(spec))

    assert result.status == "ok"
    assert result.payload["consulted"] == "none"
    assert result.payload["answers"] == {}
    # The unresolved field falls back to a declared neutral default, recorded.
    assert any("portfolio_construction" in a for a in result.payload["assumptions"])
    artifact = ctx.run_dir / "generated" / "reader_consultation.json"
    assert artifact.exists()
    data = json.loads(artifact.read_text())
    assert data["answers"] == {} and data["consulted"] == "none"
    assert any("resolution disabled" in note for note in result.notes)


def test_resolution_routes_questions_to_reader_backbone(make_ctx) -> None:
    spec = _spec(signal_definition="")
    analysis = _analysis(spec)
    gaps = detect_gaps(analysis, 0.5)
    prompt = build_consult_prompt(analysis, gaps)
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT): {
            "text": '{"signal_definition": "12-1 momentum, skip the most recent month"}',
            "model": DEFAULT_MODEL,
            "input_tokens": 80,
            "output_tokens": 30,
        }
    }
    ctx = make_ctx(config=_config(resolve=True))
    ctx.llm = RecordedStubClient(fixtures)  # llm_for_agent returns it for quant_reader

    result = ConsultReaderSkill().run(ctx, analysis=analysis)

    assert result.status == "ok"
    assert result.payload["consulted"] == "quant_reader"
    assert result.payload["resolved"] is True
    assert result.payload["answers"]["signal_definition"].startswith("12-1 momentum")
    # Resolved field is not re-defaulted as an assumption.
    assert not any("signal_definition" in a for a in result.payload["assumptions"])


def test_cost_cap_blocks_reader_call(make_ctx) -> None:
    ctx = make_ctx(config=_config(resolve=True, cost_cap=0.5))
    ctx.manifest.record_llm_call({"model": DEFAULT_MODEL, "cost_usd": 1.0})
    ctx.llm = RecordedStubClient({})  # any call would raise LookupError

    result = ConsultReaderSkill().run(ctx, analysis=_analysis(_spec(universe="")))

    assert result.status == "ok"
    assert result.payload["consulted"] == "none"
    assert any("cost cap" in note for note in result.notes)


# --- agent seam --------------------------------------------------------------

def test_agent_consult_reader_returns_none_when_disabled(make_ctx) -> None:
    # No skills wired -> the agent method is a no-op, leaving the spec as-is.
    agent = QuantCoderAgent(skills={})
    assert agent.consult_reader(_analysis(_spec(universe="")), make_ctx(config={})) is None
