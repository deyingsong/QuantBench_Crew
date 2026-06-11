"""QB-20 acceptance: a multi-result abstract yields multiple distinct claims."""

from quantbench_crew.models import Paper, PaperAnalysis
from quantbench_crew.skills.reader.target_table import (
    TargetTableExtractionSkill,
    reproduction_target_from_payload,
)

MULTI = (
    "The long-short strategy earns 0.95% per month with an annualized Sharpe "
    "ratio of 1.2 and a t-statistic of 3.5. The monthly alpha of 0.4% is "
    "significant, and the information ratio of 0.8 is robust out of sample."
)


def _analysis(abstract: str) -> PaperAnalysis:
    paper = Paper(title="Multi-claim paper", abstract=abstract)
    return PaperAnalysis(
        paper=paper,
        research_question="q",
        proposed_method="m",
        assumptions=(),
        datasets=(),
        metrics=(),
        limitations=(),
    )


def test_enumerates_all_falsifiable_claims(make_ctx) -> None:
    ctx = make_ctx()  # no LLM => deterministic abstract fallback
    result = TargetTableExtractionSkill().run(ctx, analysis=_analysis(MULTI))

    claims = {c["metric"]: c for c in result.payload["target"]["claims"]}
    assert set(claims) == {
        "monthly_return",
        "sharpe",
        "t_statistic",
        "alpha",
        "information_ratio",
    }
    assert claims["monthly_return"]["value"] == 0.0095
    assert claims["sharpe"]["value"] == 1.2
    assert claims["t_statistic"]["value"] == 3.5
    assert claims["alpha"]["value"] == 0.004
    assert claims["information_ratio"]["value"] == 0.8
    # Every claim carries value, tolerance, and source.
    for claim in claims.values():
        assert claim["tolerance"] > 0 and claim["source"]


def test_target_built_with_multiple_claims(make_ctx) -> None:
    ctx = make_ctx()
    result = TargetTableExtractionSkill().run(ctx, analysis=_analysis(MULTI))
    target = reproduction_target_from_payload(_analysis(MULTI).paper, result.payload)

    assert target is not None
    assert len(target.claims) == 5


def test_duplicate_claims_are_deduped(make_ctx) -> None:
    ctx = make_ctx()
    abstract = "Sharpe ratio of 1.2 ... a Sharpe ratio of 1.2 again."
    result = TargetTableExtractionSkill().run(ctx, analysis=_analysis(abstract))

    sharpes = [c for c in result.payload["target"]["claims"] if c["metric"] == "sharpe"]
    assert len(sharpes) == 1


def test_no_claims_reports_skipped(make_ctx) -> None:
    ctx = make_ctx()
    result = TargetTableExtractionSkill().run(
        ctx, analysis=_analysis("A qualitative study with no numbers.")
    )
    assert result.status == "skipped"
