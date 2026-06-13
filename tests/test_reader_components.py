import json

from quantbench_crew.agents.reader import QuantReaderAgent
from quantbench_crew.llm import DEFAULT_MODEL, RecordedStubClient, request_fingerprint
from quantbench_crew.models import Paper
from quantbench_crew.skills import default_registry
from quantbench_crew.skills.reader.question_identifier import (
    PROMPT_NAME,
    SYSTEM_PROMPT,
    QuestionIdentifierSkill,
)
from quantbench_crew.skills.reader.structured_components import build_component_prompt


def _paper() -> Paper:
    return Paper(
        title="Nonlinear Return Forecasts",
        abstract=(
            "Previous studies use linear models, but they fail to capture nonlinear signals. "
            "This important problem motivates a neural network algorithm using CRSP monthly "
            "returns and firm characteristics to predict next-month returns. We propose the "
            "network as a reusable forecasting method. We compare against a linear baseline "
            "using an out-of-sample test and Sharpe ratio. The approach may not generalize "
            "beyond US stocks. Future research could extend the sample."
        ),
    )


def _reader_skills():
    return {
        name: default_registry.create("quant_reader", name)
        for name in (
            "question_identifier",
            "methodology_extractor",
            "empirical_spec_parser",
            "criticizer",
        )
    }


def test_reader_attaches_all_four_deterministic_assessments(make_ctx) -> None:
    analysis = QuantReaderAgent(use_paperqa=False, skills=_reader_skills()).analyze(
        _paper(), make_ctx()
    )

    assert analysis.question_assessment is not None
    assert analysis.question_assessment.existing_method_gap
    assert analysis.question_assessment.claimed_contribution
    assert analysis.methodology_assessment is not None
    assert analysis.methodology_assessment.algorithms
    assert analysis.methodology_assessment.baselines
    assert analysis.empirical_spec is not None
    assert analysis.empirical_spec.features
    assert analysis.empirical_spec.labels
    assert analysis.empirical_spec.splits
    assert analysis.critique is not None
    assert any("generalize" in item for item in analysis.critique.author_stated_limitations)
    assert not analysis.critique.reader_inferred_threats
    assert analysis.critique.future_directions
    assert all(link.detail for link in analysis.question_assessment.evidence)


def test_question_identifier_keeps_only_verified_llm_evidence(make_ctx) -> None:
    base = QuantReaderAgent(use_paperqa=False).analyze(_paper())
    prompt = build_component_prompt(PROMPT_NAME, base)
    answer = {
        "question": "Can neural networks improve return forecasts?",
        "field_state": ["Previous studies use linear models."],
        "importance": ["Better forecasts could improve allocation."],
        "existing_method_gap": ["Linear models fail to capture nonlinear signals."],
        "claimed_contribution": ["A reusable neural network forecasting method."],
        "confidence": 0.9,
        "evidence": [
            {
                "field": "field_state",
                "quote": "Previous studies use linear models",
            },
            {"field": "importance", "quote": "This quote was fabricated"},
        ],
    }
    fingerprint = request_fingerprint(DEFAULT_MODEL, prompt, SYSTEM_PROMPT)
    llm = RecordedStubClient(
        {
            fingerprint: {
                "text": json.dumps(answer),
                "model": DEFAULT_MODEL,
                "input_tokens": 100,
                "output_tokens": 100,
            }
        }
    )

    result = QuestionIdentifierSkill().run(make_ctx(llm=llm), analysis=base)
    evidence = result.payload["question_assessment"]["evidence"]

    assert result.payload["source"] == "llm"
    assert len(evidence) == 1
    assert evidence[0]["detail"] == "Previous studies use linear models"
