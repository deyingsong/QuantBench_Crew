"""QB-33/34/35: the system's own regression suite over the eval set."""

from dataclasses import replace
from pathlib import Path

import pytest

from quantbench_crew.datasets.eval_set import build_eval_set
from quantbench_crew.eval import (
    case_available,
    format_report,
    run_eval_case,
    run_eval_suite,
)
from quantbench_crew.models import Claim, ReproductionTarget


def _case(slug: str):
    return next(c for c in build_eval_set() if c.slug == slug)


# --- QB-33 acceptance: a reproduce case and a does-not-reproduce case --------

def test_reproduce_case_earns_promising(tmp_path: Path) -> None:
    result = run_eval_case(_case("momentum_planted"), tmp_path)

    assert result.achieved_verdict == "promising"
    assert result.matches_expected


def test_negative_control_does_not_reproduce(tmp_path: Path) -> None:
    # The pure-noise negative control must never be called a reproduction.
    result = run_eval_case(_case("noise_control"), tmp_path)

    assert result.achieved_verdict != "promising"
    assert result.matches_expected


# --- QB-35: a deliberately broken target turns a green case red --------------

def test_broken_target_flips_reproduce_case_red(tmp_path: Path) -> None:
    case = _case("momentum_planted")
    # Mutate the hand-labeled target to an unreachable claim: the strategy can
    # no longer reproduce it, so the case that *should* pass now fails.
    broken = replace(
        case,
        targets=ReproductionTarget(
            paper=case.paper,
            claims=(Claim(metric="monthly_return", value=0.10, tolerance=0.05),),
        ),
    )
    result = run_eval_case(broken, tmp_path)

    assert result.achieved_verdict != "promising"
    assert result.matches_expected is False  # expected reproduces, but it didn't


def test_synthetic_cases_are_always_available() -> None:
    synthetic = [c for c in build_eval_set() if c.data_tier == "synthetic"]
    assert synthetic and all(case_available(c) for c in synthetic)


def test_format_report_renders_pass_fail(tmp_path: Path) -> None:
    results = [run_eval_case(_case("momentum_planted"), tmp_path)]
    report = format_report(results)
    assert "momentum_planted" in report
    assert "PASS" in report


# --- QB-35: the full regression gate (slow; CRSP cases run when present) -----

@pytest.mark.eval
def test_full_eval_suite_matches_expectations(tmp_path: Path) -> None:
    cases = build_eval_set()
    results = run_eval_suite(cases, tmp_path)

    assert results  # at least the synthetic cases ran
    failures = [r for r in results if not r.matches_expected]
    assert not failures, format_report(results)
    # The negative control must be present and correctly judged.
    assert any(r.case.slug == "noise_control" and r.matches_expected for r in results)
