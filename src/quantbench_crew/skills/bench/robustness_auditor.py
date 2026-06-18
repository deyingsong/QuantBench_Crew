"""Stress strategies and preserve an auditable experiment ledger."""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore, stable_hash
from quantbench_crew.datasets.registry import LoadedDataset
from quantbench_crew.models import RobustnessAudit
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.bench.strategy_evaluator import experiment_result_from_dict
from quantbench_crew.skills.bench.walk_forward import WalkForwardSkill


class RobustnessAuditorSkill:
    """Run cost stresses and audit robustness evidence and provenance."""

    name = "robustness_auditor"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        dataset: LoadedDataset = inputs["dataset"]
        spec = inputs.get("spec")
        target = inputs.get("target")
        primary = dict(inputs.get("primary_payload") or {})
        strategy_evaluation = dict(inputs.get("strategy_evaluation") or {})
        settings = skill_settings(ctx.config, "quant_bench", self.name)
        walk_settings = skill_settings(ctx.config, "quant_bench", "walk_forward")
        experiments: list[dict[str, Any]] = []
        evaluator = WalkForwardSkill()

        base_cost = float(walk_settings.get("cost_bps", 10.0))
        scenarios = list(settings.get("cost_bps_scenarios") or [base_cost, base_cost * 2.5])
        for index, cost in enumerate(dict.fromkeys(float(value) for value in scenarios)):
            if primary and cost == base_cost:
                payload = primary
            else:
                payload, _ = evaluator.evaluate(
                    ctx,
                    dataset,
                    spec=spec,
                    target=target,
                    settings={**walk_settings, "cost_bps": cost},
                )
            experiments.append(
                {
                    "name": f"cost_stress:{cost:g}bps",
                    "dataset": dataset.name,
                    "expect_edge": True,
                    "passed": bool(payload.get("beats_random_null", False)),
                    "configuration": {
                        "dataset": dataset.provenance(),
                        "walk_forward": dict(
                            payload.get("configuration")
                            or {**walk_settings, "cost_bps": cost}
                        ),
                    },
                    "metrics": dict(payload.get("metrics") or {}),
                    "baselines": dict(payload.get("baselines") or {}),
                    "n_trials": int(payload.get("n_trials", 0)),
                }
            )

        passed_checks: list[str] = []
        failed_checks: list[str] = []
        unavailable_checks: list[str] = []

        _record_check(
            "multi_dataset_expectations",
            strategy_evaluation.get("passed_all"),
            passed_checks,
            failed_checks,
            unavailable_checks,
        )
        robustness = primary.get("robustness") or {}
        _record_check(
            "subsample_sign_stability",
            robustness.get("sign_stable"),
            passed_checks,
            failed_checks,
            unavailable_checks,
        )
        spread = (robustness.get("parameter_sensitivity") or {}).get("spread")
        _record_check(
            "parameter_sensitivity",
            None
            if spread is None
            else float(spread) <= float(settings.get("max_parameter_sharpe_spread", 1.5)),
            passed_checks,
            failed_checks,
            unavailable_checks,
        )
        deflated = primary.get("deflated_sharpe") or {}
        p_value = deflated.get("p_value")
        _record_check(
            "deflated_sharpe_significance",
            None
            if p_value is None
            else float(p_value) <= float(settings.get("max_deflated_sharpe_p_value", 0.1)),
            passed_checks,
            failed_checks,
            unavailable_checks,
        )
        _record_check(
            "conservative_cost_stress",
            all(experiment["passed"] for experiment in experiments) if experiments else None,
            passed_checks,
            failed_checks,
            unavailable_checks,
        )
        _record_check(
            "trial_count_disclosed",
            int(primary.get("n_trials", 0)) > 0 if primary else None,
            passed_checks,
            failed_checks,
            unavailable_checks,
        )

        strategy_experiments = list(strategy_evaluation.get("experiments") or [])
        all_experiments = [*strategy_experiments, *experiments]
        audit_policy = {
            "cost_bps_scenarios": scenarios,
            "max_parameter_sharpe_spread": float(
                settings.get("max_parameter_sharpe_spread", 1.5)
            ),
            "max_deflated_sharpe_p_value": float(
                settings.get("max_deflated_sharpe_p_value", 0.1)
            ),
        }
        configuration_hash = stable_hash(
            {
                "experiments": [item["configuration"] for item in all_experiments],
                "audit_policy": audit_policy,
            }
        )
        results_hash = stable_hash(
            {
                "experiments": [
                    {
                        "name": item["name"],
                        "passed": item["passed"],
                        "metrics": item["metrics"],
                        "baselines": item["baselines"],
                        "n_trials": int(item.get("n_trials", 0)),
                    }
                    for item in all_experiments
                ],
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "unavailable_checks": unavailable_checks,
            }
        )
        recorded_experiments = len(all_experiments)
        disclosed_local_trials = sum(
            int(item.get("n_trials", 0))
            for item in all_experiments
        )
        robust = not failed_checks and not unavailable_checks and bool(passed_checks)
        audit = {
            "experiments": all_experiments,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "unavailable_checks": unavailable_checks,
            "configuration_hash": configuration_hash,
            "results_hash": results_hash,
            "robust": robust,
            "recorded_experiments": recorded_experiments,
            "disclosed_local_trials": disclosed_local_trials,
            "audit_policy": audit_policy,
        }
        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        artifact = "benchmark/robustness_audit.json"
        store.write_json(artifact, audit)
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={"robustness_audit": audit},
            artifacts=(artifact,),
            notes=(
                f"robustness verdict={'pass' if robust else 'fail'}; "
                f"{len(passed_checks)} passed, {len(failed_checks)} failed, "
                f"{len(unavailable_checks)} unavailable",
                f"configuration hash {configuration_hash[:12]}; results hash {results_hash[:12]}",
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def robustness_audit_from_payload(payload: dict[str, Any]) -> RobustnessAudit | None:
    """Build a typed robustness audit from the skill payload."""

    data = payload.get("robustness_audit")
    if not data:
        return None
    return RobustnessAudit(
        experiments=tuple(
            experiment_result_from_dict(item) for item in data.get("experiments", [])
        ),
        passed_checks=tuple(str(item) for item in data.get("passed_checks", [])),
        failed_checks=tuple(str(item) for item in data.get("failed_checks", [])),
        unavailable_checks=tuple(str(item) for item in data.get("unavailable_checks", [])),
        configuration_hash=str(data.get("configuration_hash", "")),
        results_hash=str(data.get("results_hash", "")),
        robust=bool(data.get("robust", False)),
        recorded_experiments=int(data.get("recorded_experiments", 0)),
        disclosed_local_trials=int(data.get("disclosed_local_trials", 0)),
        notes=("Audit retains failed and unavailable checks.",),
    )


def _record_check(
    name: str,
    passed: Any,
    passed_checks: list[str],
    failed_checks: list[str],
    unavailable_checks: list[str],
) -> None:
    if passed is None:
        unavailable_checks.append(name)
    elif bool(passed):
        passed_checks.append(name)
    else:
        failed_checks.append(name)


@register_skill("quant_bench", "robustness_auditor")
def _make_robustness_auditor_skill() -> RobustnessAuditorSkill:
    return RobustnessAuditorSkill()
