"""Multi-dataset strategy evaluation against declared expectations."""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.datasets.registry import LoadedDataset, load_dataset
from quantbench_crew.models import (
    ExperimentResult,
    Paper,
    StrategyEvaluation,
)
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.bench.walk_forward import WalkForwardSkill


class StrategyEvaluatorSkill:
    """Evaluate one strategy across declared signal and no-signal datasets."""

    name = "strategy_evaluator"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        primary: LoadedDataset = inputs["dataset"]
        spec = inputs.get("spec")
        target = inputs.get("target")
        primary_payload = dict(inputs.get("primary_payload") or {})
        settings = skill_settings(ctx.config, "quant_bench", self.name)
        walk_settings = skill_settings(ctx.config, "quant_bench", "walk_forward")
        experiments: list[dict[str, Any]] = []

        if primary_payload:
            experiments.append(
                _experiment_payload(
                    name=f"primary:{primary.name}",
                    dataset=primary,
                    expect_edge=bool(settings.get("primary_expect_edge", True)),
                    walk_settings=walk_settings,
                    result=primary_payload,
                )
            )

        evaluator = WalkForwardSkill()
        for index, entry in enumerate(settings.get("datasets") or []):
            if not isinstance(entry, dict) or not entry.get("name"):
                continue
            dataset = load_dataset(str(entry["name"]), entry.get("params") or {})
            if dataset.seed is not None:
                ctx.manifest.record_seed(f"strategy_evaluator:{dataset.name}:{index}", dataset.seed)
            payload, _ = evaluator.evaluate(
                ctx, dataset, spec=spec, target=target, settings=walk_settings
            )
            experiments.append(
                _experiment_payload(
                    name=str(entry.get("experiment") or f"dataset:{dataset.name}:{index}"),
                    dataset=dataset,
                    expect_edge=bool(entry.get("expect_edge", True)),
                    walk_settings=walk_settings,
                    result=payload,
                )
            )

        passed = sum(1 for experiment in experiments if experiment["passed"])
        pass_rate = passed / len(experiments) if experiments else 0.0
        payload = {
            "experiments": experiments,
            "passed_all": bool(experiments) and passed == len(experiments),
            "pass_rate": pass_rate,
            "baseline_names": sorted(
                {
                    name
                    for experiment in experiments
                    for name in experiment["baselines"]
                }
            ),
        }
        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        artifact = "benchmark/strategy_evaluation.json"
        store.write_json(artifact, payload)
        result = SkillResult(
            skill=self.name,
            status="ok" if experiments else "skipped",
            payload={"strategy_evaluation": payload},
            artifacts=(artifact,),
            notes=(
                f"{passed}/{len(experiments)} declared dataset expectations passed",
                "correct rejection of no-signal datasets counts as a pass",
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def strategy_evaluation_from_payload(
    paper: Paper, payload: dict[str, Any]
) -> StrategyEvaluation | None:
    """Build the typed multi-dataset evaluation from a skill payload."""

    data = payload.get("strategy_evaluation")
    if not data:
        return None
    experiments = tuple(
        experiment_result_from_dict(item) for item in data.get("experiments", [])
    )
    return StrategyEvaluation(
        paper=paper,
        experiments=experiments,
        passed_all=bool(data.get("passed_all", False)),
        pass_rate=float(data.get("pass_rate", 0.0)),
        notes=(
            f"{sum(experiment.passed for experiment in experiments)}/"
            f"{len(experiments)} declared expectations passed",
        ),
    )


def _experiment_payload(
    *,
    name: str,
    dataset: LoadedDataset,
    expect_edge: bool,
    walk_settings: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    beats_null = bool(result.get("beats_random_null", False))
    return {
        "name": name,
        "dataset": dataset.name,
        "expect_edge": expect_edge,
        "passed": beats_null == expect_edge,
        "configuration": {
            "dataset": dataset.provenance(),
            "walk_forward": dict(result.get("configuration") or walk_settings),
        },
        "metrics": dict(result.get("metrics") or {}),
        "baselines": dict(result.get("baselines") or {}),
        "beats_random_null": beats_null,
        "n_windows": int(result.get("n_windows", 0)),
        "n_trials": int(result.get("n_trials", 0)),
        "deflated_sharpe": result.get("deflated_sharpe"),
        "robustness": result.get("robustness"),
    }


def experiment_result_from_dict(data: dict[str, Any]) -> ExperimentResult:
    """Build one typed experiment record from a JSON-shaped ledger entry."""

    return ExperimentResult(
        name=str(data.get("name", "")),
        dataset=str(data.get("dataset", "")),
        expect_edge=bool(data.get("expect_edge", False)),
        passed=bool(data.get("passed", False)),
        configuration=dict(data.get("configuration") or {}),
        metrics={key: float(value) for key, value in (data.get("metrics") or {}).items()},
        baselines={
            name: {key: float(value) for key, value in values.items()}
            for name, values in (data.get("baselines") or {}).items()
        },
        notes=(
            "behavior matched declared expectation"
            if data.get("passed")
            else "behavior contradicted declared expectation",
        ),
    )


@register_skill("quant_bench", "strategy_evaluator")
def _make_strategy_evaluator_skill() -> StrategyEvaluatorSkill:
    return StrategyEvaluatorSkill()
