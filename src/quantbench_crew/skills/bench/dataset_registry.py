"""Dataset registry skill: record dataset provenance in the run manifest.

Loading happens in the registry library; this skill writes the dataset's
provenance (name, version, content hash, seed, shape) as a manifest artifact
and records the generator seed, so every benchmark number is traceable to the
exact data that produced it.
"""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.datasets.registry import LoadedDataset
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult


class DatasetRegistrySkill:
    """Record the provenance of the dataset the bench evaluates on."""

    name = "dataset_registry"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        dataset: LoadedDataset = inputs["dataset"]
        provenance = dataset.provenance()

        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        artifact = f"dataset/{dataset.name}.json"
        store.write_json(artifact, provenance)
        if dataset.seed is not None:
            ctx.manifest.record_seed(f"dataset:{dataset.name}", dataset.seed)

        result = SkillResult(
            skill=self.name,
            status="ok",
            payload=provenance,
            artifacts=(artifact,),
            notes=(
                f"dataset {dataset.name!r} v{dataset.version} "
                f"hash {dataset.content_hash[:12]} "
                f"({provenance['n_dates']} dates x {provenance['n_assets']} assets)",
            ),
        )
        ctx.manifest.record_skill(result)
        return result


@register_skill("quant_bench", "dataset_registry")
def _make_dataset_registry_skill() -> DatasetRegistrySkill:
    return DatasetRegistrySkill()
