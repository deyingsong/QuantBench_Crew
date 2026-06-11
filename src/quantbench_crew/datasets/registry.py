"""Versioned, point-in-time dataset access with content hashing.

Every dataset the bench evaluates on resolves through ``load_dataset``, which
returns a ``LoadedDataset`` carrying a content hash and version. The hash is
recorded in the run manifest so a benchmark number is always traceable to the
exact data that produced it — and so a silently changed dataset can never
masquerade as a reproduced result.

Point-in-time discipline is the panel's job (``PanelData.up_to``); the
registry's job is provenance.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from quantbench_crew.artifacts import stable_hash
from quantbench_crew.benchmarks.contract import PanelData
from quantbench_crew.datasets import french, synthetic

REGISTRY_VERSION = "1"


@dataclass(frozen=True)
class LoadedDataset:
    """A resolved dataset plus the provenance recorded in the manifest."""

    name: str
    frequency: str
    panel: PanelData
    content_hash: str
    version: str = REGISTRY_VERSION
    seed: int | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def provenance(self) -> dict[str, Any]:
        """JSON-serializable record for the manifest (no panel payload)."""

        return {
            "name": self.name,
            "frequency": self.frequency,
            "version": self.version,
            "content_hash": self.content_hash,
            "seed": self.seed,
            "params": dict(sorted(self.params.items())),
            "n_dates": len(self.panel.dates()),
            "n_assets": len(self.panel.assets()),
        }


def panel_hash(panel: PanelData) -> str:
    """Deterministic content hash over the panel's (date, asset, fields)."""

    serializable = [
        [d.isoformat(), asset, [list(item) for item in fields]]
        for d, asset, fields in panel.records()
    ]
    return stable_hash(serializable)


def load_dataset(name: str, params: Mapping[str, Any] | None = None) -> LoadedDataset:
    """Resolve a dataset by name with optional generator params."""

    params = dict(params or {})
    if name == "planted_momentum":
        seed = int(params.get("seed", 0))
        panel = synthetic.planted_momentum(
            n_assets=int(params.get("n_assets", synthetic.DEFAULT_N_ASSETS)),
            n_periods=int(params.get("n_periods", synthetic.DEFAULT_N_PERIODS)),
            seed=seed,
            strength=float(params.get("strength", 0.010)),
            noise=float(params.get("noise", 0.001)),
        )
        return _build(name, "monthly", panel, seed, params)

    if name == "pure_noise":
        seed = int(params.get("seed", 0))
        panel = synthetic.pure_noise(
            n_assets=int(params.get("n_assets", synthetic.DEFAULT_N_ASSETS)),
            n_periods=int(params.get("n_periods", synthetic.DEFAULT_N_PERIODS)),
            seed=seed,
            noise=float(params.get("noise", 0.02)),
        )
        return _build(name, "monthly", panel, seed, params)

    if name == "french_momentum":
        path = params.get("path", french.DEFAULT_FIXTURE)
        panel = french.load_french_momentum(path)
        return _build(name, "monthly", panel, None, params)

    raise ValueError(
        f"unknown dataset {name!r}; expected planted_momentum, pure_noise, or "
        "french_momentum"
    )


def _build(
    name: str,
    frequency: str,
    panel: PanelData,
    seed: int | None,
    params: Mapping[str, Any],
) -> LoadedDataset:
    return LoadedDataset(
        name=name,
        frequency=frequency,
        panel=panel,
        content_hash=panel_hash(panel),
        seed=seed,
        params=dict(params),
    )
