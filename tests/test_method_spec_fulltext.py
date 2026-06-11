"""QB-19 acceptance: full-text extraction matches labels and lifts confidence."""

import json
from pathlib import Path

import pytest

from quantbench_crew.agents.reader import QuantReaderAgent
from quantbench_crew.llm import DEFAULT_MODEL, RecordedStubClient, request_fingerprint
from quantbench_crew.skills.reader.method_spec import (
    SYSTEM_PROMPT,
    MethodSpecExtractionSkill,
    build_method_spec_prompt,
    field_match_rate,
)
from quantbench_crew.tools.arxiv_tool import load_local_papers

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN_PAPER = load_local_papers(FIXTURES / "golden_paper.json")[0]
GOLDEN_SPEC = json.loads((FIXTURES / "method_spec_golden.json").read_text())

FULL_TEXT = (
    "Section 3. We rank all NYSE and AMEX common stocks each month on their "
    "past 6-month returns and form an equal-weighted winner-minus-loser decile "
    "portfolio, rebalanced monthly and held for 6 overlapping months. The "
    "sample runs from January 1965 to December 1989."
)


def _analysis():
    return QuantReaderAgent().analyze(GOLDEN_PAPER)  # metadata analysis, no ctx


def _fulltext_fixture(analysis):
    spec = dict(GOLDEN_SPEC)
    spec["confidence"] = 0.5  # model's own modest estimate; floored to 0.7
    prompt = build_method_spec_prompt(analysis, FULL_TEXT)
    return {
        request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT): {
            "text": json.dumps(spec),
            "model": DEFAULT_MODEL,
            "input_tokens": 3000,
            "output_tokens": 300,
        }
    }


def test_fulltext_extraction_matches_label_and_floors_confidence(make_ctx) -> None:
    analysis = _analysis()
    ctx = make_ctx()
    ctx.llm = RecordedStubClient(_fulltext_fixture(analysis))

    result = MethodSpecExtractionSkill().run(ctx, analysis=analysis, full_text=FULL_TEXT)

    assert result.payload["source"] == "llm_fulltext"
    assert result.payload["confidence"] >= 0.7
    assert field_match_rate(result.payload["method_spec"], GOLDEN_SPEC) >= 0.8


def test_metadata_fallback_has_lower_confidence(make_ctx) -> None:
    # No LLM => deterministic metadata fallback, which is honestly unsure.
    ctx = make_ctx()
    result = MethodSpecExtractionSkill().run(ctx, analysis=_analysis(), full_text="")

    assert result.payload["source"] == "metadata_fallback"
    assert result.payload["confidence"] == pytest.approx(0.2)
    assert result.payload["confidence"] < 0.7


def test_field_match_rate_partial_and_full() -> None:
    assert field_match_rate(GOLDEN_SPEC, GOLDEN_SPEC) == pytest.approx(1.0)
    wrong = dict(GOLDEN_SPEC, frequency="daily", universe="crypto")
    assert field_match_rate(wrong, GOLDEN_SPEC) == pytest.approx(4 / 6)


def test_full_text_prompt_extends_abstract_only_prompt() -> None:
    analysis = _analysis()
    base = build_method_spec_prompt(analysis)
    extended = build_method_spec_prompt(analysis, FULL_TEXT)
    # Abstract-only prompt is unchanged (fixtures stay valid); full text appends.
    assert extended.startswith(base)
    assert "Full-text excerpts" in extended
