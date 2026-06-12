"""QB-11 acceptance: golden paper yields a passing candidate within budget."""

import json
from pathlib import Path

import pytest

from quantbench_crew.agents.reader import QuantReaderAgent
from quantbench_crew.llm import (
    DEFAULT_MODEL,
    ManifestLoggingClient,
    RecordedStubClient,
    request_fingerprint,
)
from quantbench_crew.skills.coder.code_generation import (
    CodeGenerationSkill,
    SYSTEM_PROMPT,
    build_generation_prompt,
    extract_module_source,
    reference_source,
    structure_score,
)
from quantbench_crew.tools.arxiv_tool import load_local_papers

GOLDEN = load_local_papers(Path(__file__).parent / "fixtures" / "golden_paper.json")[0]


def _golden_analysis():
    return QuantReaderAgent().analyze(GOLDEN)


def _codegen_config(iterations: int = 1, cost_cap: float = 2.0) -> dict:
    return {
        "llm": {"cost_cap_usd": cost_cap},
        "agents": {
            "quant_coder": {
                "skills": {
                    "code_generation": {"enabled": True, "iterations": iterations}
                }
            }
        },
    }


def test_fallback_candidate_passes_all_template_tests(make_ctx) -> None:
    analysis = _golden_analysis()
    ctx = make_ctx(config=_codegen_config())

    result = CodeGenerationSkill().run(ctx, analysis=analysis, plan=None)

    assert result.status == "ok"
    payload = result.payload
    # Templates (3) plus the golden spec's construction invariants (QB-29).
    assert payload["tests_passed"] == payload["tests_total"] >= 3
    assert payload["source"] == "fallback"
    assert payload["entry_point"] == "build_strategy"
    assert (ctx.run_dir / "generated" / "strategy.py").exists()
    assert "generated/strategy.py" in ctx.manifest.artifacts
    assert any("no LLM configured for quant_coder" in note for note in result.notes)


def test_llm_candidates_are_generated_and_scored(make_ctx) -> None:
    analysis = _golden_analysis()
    # A valid alternative candidate: the reference module plus a comment, so
    # the program text differs but every template test still passes.
    candidate = reference_source() + "\n# generated variant\n"
    prompt = build_generation_prompt(analysis.method_spec, analysis, "")
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT): {
            "text": f"```python\n{candidate}```",
            "model": DEFAULT_MODEL,
            "input_tokens": 1200,
            "output_tokens": 900,
        }
    }
    ctx = make_ctx(config=_codegen_config(iterations=1))
    ctx.llm = ManifestLoggingClient(RecordedStubClient(fixtures), ctx.manifest)

    result = CodeGenerationSkill().run(ctx, analysis=analysis, plan=None)

    assert result.status == "ok"
    assert result.payload["llm_iterations"] == 1
    assert result.payload["candidates_evaluated"] == 2
    assert result.payload["tests_passed"] == 3
    # The generation call went through the seam and was cost-logged.
    assert len(ctx.manifest.llm_calls) == 1
    assert ctx.manifest.llm_calls[0]["cost_usd"] > 0


def test_cost_cap_stops_generation_before_any_llm_call(make_ctx) -> None:
    analysis = _golden_analysis()
    ctx = make_ctx(config=_codegen_config(iterations=2, cost_cap=0.5))
    ctx.manifest.record_llm_call({"model": DEFAULT_MODEL, "cost_usd": 1.0})
    # Empty stub raises LookupError on any completion: proves no call happens.
    ctx.llm = RecordedStubClient({})

    result = CodeGenerationSkill().run(ctx, analysis=analysis, plan=None)

    assert result.status == "ok"  # fallback still wins
    assert result.payload["llm_iterations"] == 0
    assert any("cost cap" in note for note in result.notes)


def test_unusable_llm_output_keeps_fallback(make_ctx) -> None:
    analysis = _golden_analysis()
    prompt = build_generation_prompt(analysis.method_spec, analysis, "")
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT): {
            "text": "I am unable to write code today.",
            "model": DEFAULT_MODEL,
            "input_tokens": 10,
            "output_tokens": 10,
        }
    }
    ctx = make_ctx(config=_codegen_config(iterations=1))
    ctx.llm = RecordedStubClient(fixtures)

    result = CodeGenerationSkill().run(ctx, analysis=analysis, plan=None)

    assert result.status == "ok"
    assert result.payload["source"] == "fallback"
    assert any("no usable module source" in note for note in result.notes)


def test_unknown_adapter_is_rejected_loudly(make_ctx) -> None:
    config = _codegen_config()
    config["agents"]["quant_coder"]["skills"]["code_generation"]["adapter"] = "bogus"
    ctx = make_ctx(config=config)

    with pytest.raises(ValueError, match="unknown generation adapter"):
        CodeGenerationSkill().run(ctx, analysis=_golden_analysis(), plan=None)


def test_extract_module_source_handles_fences_and_raw() -> None:
    fenced = "```python\ndef build_strategy(params=None):\n    return 1\n```"
    raw = "def build_strategy(params=None):\n    return 1"

    assert "def build_strategy" in extract_module_source(fenced)
    assert "def build_strategy" in extract_module_source(raw)
    assert extract_module_source("no code at all") == ""


def test_structure_score_rewards_contract_shape() -> None:
    assert structure_score(reference_source()) == pytest.approx(1.0)
    assert structure_score("def build_strategy(p=None):\n    return None\n") < 0.7
    assert structure_score("def broken(:") == 0.0
