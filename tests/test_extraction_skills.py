"""QB-07/QB-08 acceptance: golden-paper MethodSpec and ReproductionTarget.

The expected values asserted here are the hand-labeled golden fixtures from
the roadmap: written against tests/fixtures/golden_paper.json before the
extractors, they are the ground truth both extraction paths must reproduce.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from quantbench_crew.agents.reader import QuantReaderAgent
from quantbench_crew.llm import DEFAULT_MODEL, RecordedStubClient, request_fingerprint
from quantbench_crew.skills.reader.method_spec import (
    MethodSpecExtractionSkill,
    SYSTEM_PROMPT as SPEC_SYSTEM,
    build_method_spec_prompt,
    method_spec_from_payload,
)
from quantbench_crew.skills.reader.target_table import (
    SYSTEM_PROMPT as TARGET_SYSTEM,
    TargetTableExtractionSkill,
    build_target_table_prompt,
    reproduction_target_from_payload,
)
from quantbench_crew.tools.arxiv_tool import load_local_papers

GOLDEN = load_local_papers(Path(__file__).parent / "fixtures" / "golden_paper.json")[0]

# Hand-labeled golden MethodSpec (the LLM-path ground truth).
GOLDEN_SPEC_ANSWER = {
    "universe": "NYSE and AMEX common stocks",
    "frequency": "monthly",
    "signal_definition": "rank stocks on cumulative returns over months t-6 to t-1",
    "portfolio_construction": "decile long-short, equal-weighted, winners minus losers",
    "rebalance_frequency": "monthly",
    "holding_period": "6 months, overlapping",
    "sample_start": "1965-01-01",
    "sample_end": "1989-12-31",
    "evaluation_protocol": "full-sample average of overlapping portfolio returns",
    "hyperparameters": {"formation_months": 6, "holding_months": 6},
    "data_requirements": ["CRSP monthly returns or Kenneth French momentum portfolios"],
    "confidence": 0.85,
}

# Hand-labeled golden ReproductionTarget.
GOLDEN_TARGET_ANSWER = {
    "table_reference": "Table 1",
    "claims": [
        {
            "metric": "monthly_return",
            "value": 0.0095,
            "unit": "monthly",
            "context": "equal-weighted winner-minus-loser decile, 6x6 strategy",
            "tolerance": 0.15,
            "source": "Table 1",
        }
    ],
    "notes": ["gross of transaction costs"],
}


def _golden_analysis():
    return QuantReaderAgent().analyze(GOLDEN)


def _stub_for(prompt: str, system: str, answer: dict) -> RecordedStubClient:
    fingerprint = request_fingerprint(DEFAULT_MODEL, prompt, system)
    return RecordedStubClient(
        {
            fingerprint: {
                "text": json.dumps(answer),
                "model": DEFAULT_MODEL,
                "input_tokens": 800,
                "output_tokens": 300,
            }
        }
    )


# --- QB-07: MethodSpec extraction -------------------------------------------


def test_llm_path_yields_golden_method_spec(make_ctx) -> None:
    analysis = _golden_analysis()
    llm = _stub_for(build_method_spec_prompt(analysis), SPEC_SYSTEM, GOLDEN_SPEC_ANSWER)
    ctx = make_ctx(llm=llm)

    result = MethodSpecExtractionSkill().run(ctx, analysis=analysis)

    assert result.status == "ok"
    assert result.payload["source"] == "llm"
    assert result.payload["confidence"] == pytest.approx(0.85)

    spec = method_spec_from_payload(analysis.paper, result.payload)
    assert spec is not None
    assert spec.universe == "NYSE and AMEX common stocks"
    assert spec.frequency == "monthly"
    assert "t-6" in spec.signal_definition
    assert "decile" in spec.portfolio_construction
    assert spec.sample_start == date(1965, 1, 1)
    assert spec.sample_end == date(1989, 12, 31)
    assert spec.extraction_confidence == pytest.approx(0.85)
    assert any(link.reference.startswith("llm:") for link in spec.evidence)
    assert ctx.manifest.skill_results[0].skill == "method_spec_extraction"


def test_metadata_fallback_recovers_golden_structure(make_ctx) -> None:
    analysis = _golden_analysis()

    result = MethodSpecExtractionSkill().run(make_ctx(), analysis=analysis)

    assert result.payload["source"] == "metadata_fallback"
    data = result.payload["method_spec"]
    assert data["frequency"] == "monthly"
    assert "nyse" in data["universe"].lower()
    assert "decile" in data["portfolio_construction"]
    assert data["sample_start"] == "1965-01-01"
    assert data["sample_end"] == "1989-12-31"
    assert data["hyperparameters"]["formation_months"] == 6
    assert data["hyperparameters"]["holding_months"] == 6
    assert data["confidence"] == pytest.approx(0.2)
    assert any("no LLM configured" in note for note in result.notes)


def test_schema_invalid_llm_output_falls_back_with_reason(make_ctx) -> None:
    analysis = _golden_analysis()
    bad_answer = {**GOLDEN_SPEC_ANSWER, "frequency": "fortnightly"}  # enum violation
    llm = _stub_for(build_method_spec_prompt(analysis), SPEC_SYSTEM, bad_answer)

    result = MethodSpecExtractionSkill().run(make_ctx(llm=llm), analysis=analysis)

    assert result.payload["source"] == "metadata_fallback"
    assert any("schema validation" in note for note in result.notes)


def test_llm_error_falls_back_with_reason(make_ctx) -> None:
    analysis = _golden_analysis()
    # Stub with no fixtures raises LookupError on any completion.
    result = MethodSpecExtractionSkill().run(
        make_ctx(llm=RecordedStubClient({})), analysis=analysis
    )

    assert result.payload["source"] == "metadata_fallback"
    assert any("LLM extraction failed" in note for note in result.notes)


# --- QB-08: target-table extraction ------------------------------------------


def test_llm_path_yields_golden_reproduction_target(make_ctx) -> None:
    analysis = _golden_analysis()
    llm = _stub_for(
        build_target_table_prompt(analysis.paper), TARGET_SYSTEM, GOLDEN_TARGET_ANSWER
    )

    result = TargetTableExtractionSkill().run(make_ctx(llm=llm), analysis=analysis)

    assert result.status == "ok"
    assert result.payload["source"] == "llm"
    target = reproduction_target_from_payload(analysis.paper, result.payload)
    assert target is not None
    assert target.table_reference == "Table 1"
    claim = target.claims[0]
    assert claim.metric == "monthly_return"
    assert claim.value == pytest.approx(0.0095)
    assert claim.tolerance == pytest.approx(0.15)
    assert claim.source == "Table 1"


def test_abstract_fallback_finds_golden_claim(make_ctx) -> None:
    analysis = _golden_analysis()

    result = TargetTableExtractionSkill().run(make_ctx(), analysis=analysis)

    assert result.status == "ok"
    assert result.payload["source"] == "abstract_fallback"
    target = reproduction_target_from_payload(analysis.paper, result.payload)
    assert target is not None
    claim = target.claims[0]
    assert claim.metric == "monthly_return"
    assert claim.value == pytest.approx(0.0095)
    assert claim.tolerance == pytest.approx(0.2)  # configured default
    assert claim.source == "abstract"


def test_paper_without_numbers_is_skipped_loudly(make_ctx) -> None:
    from quantbench_crew.models import Paper
    from quantbench_crew.agents.reader import QuantReaderAgent

    paper = Paper(title="A Qualitative Survey", abstract="We discuss markets broadly.")
    analysis = QuantReaderAgent().analyze(paper)

    result = TargetTableExtractionSkill().run(make_ctx(), analysis=analysis)

    assert result.status == "skipped"
    assert any("unfalsifiable" in note for note in result.notes)
    assert reproduction_target_from_payload(paper, result.payload) is None
