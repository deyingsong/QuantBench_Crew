"""QB-21 acceptance: planted pitfalls are caught; a clean abstract is not."""

from quantbench_crew.models import Paper, PaperAnalysis
from quantbench_crew.skills.reader.red_flag import RedFlagScanSkill, scan_red_flags


def _kinds(text: str) -> set[str]:
    return {flag.kind for flag in scan_red_flags(text)}


def test_no_transaction_costs_flagged_unless_handled() -> None:
    assert "no_transaction_costs" in _kinds("earns 0.95% per month before transaction costs")
    assert "no_transaction_costs" not in _kinds("earns 0.5% per month net of transaction costs")


def test_in_sample_tuning_flagged() -> None:
    assert "in_sample_tuning" in _kinds("we use the optimal parameters chosen in-sample")


def test_survivorship_flagged_unless_delisting_handled() -> None:
    assert "survivorship_prone" in _kinds("backtested on current S&P 500 constituents")
    assert "survivorship_prone" not in _kinds(
        "current constituents with delisting returns spliced in"
    )


def test_microcap_and_snooping_and_short_sample() -> None:
    assert "microcap_driven" in _kinds("returns are concentrated in microcap stocks")
    assert "data_snooping" in _kinds("we tried various specifications before settling")
    assert "short_sample" in _kinds("over the sample from 2020 to 2023")
    assert "short_sample" not in _kinds("over the sample from 1965 to 2020")


def test_data_snooping_is_critical_severity() -> None:
    flags = scan_red_flags("we experimented with many signals")
    snoop = next(f for f in flags if f.kind == "data_snooping")
    assert snoop.severity == "critical"
    assert snoop.evidence and snoop.evidence[0].kind == "paper_quote"


def test_clean_abstract_has_no_flags() -> None:
    clean = (
        "A survivorship-bias-free study, net of transaction costs, over 1965 to "
        "2020, using value-weighted large-capitalization portfolios."
    )
    assert scan_red_flags(clean) == ()


def test_skill_records_flags_in_manifest(make_ctx) -> None:
    analysis = PaperAnalysis(
        paper=Paper(title="x", abstract="earns 5% per year before transaction costs"),
        research_question="q",
        proposed_method="m",
        assumptions=(),
        datasets=(),
        metrics=(),
        limitations=(),
    )
    ctx = make_ctx()
    result = RedFlagScanSkill().run(ctx, analysis=analysis)

    assert result.payload["red_flags"][0]["kind"] == "no_transaction_costs"
    assert ctx.manifest.skill_results[-1].skill == "red_flag_scan"
