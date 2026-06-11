"""QB-12 acceptance: synthetic worlds, registry hashing, French parsing."""

from pathlib import Path

import pytest

from quantbench_crew.datasets import french, synthetic
from quantbench_crew.datasets.registry import LoadedDataset, load_dataset, panel_hash

FRENCH_FIXTURE = Path(__file__).parent / "fixtures" / "french_momentum_monthly.csv"


def test_planted_momentum_is_deterministic_and_monthly() -> None:
    first = synthetic.planted_momentum(seed=3)
    second = synthetic.planted_momentum(seed=3)

    assert first.records() == second.records()
    assert len(first.assets()) == synthetic.DEFAULT_N_ASSETS
    months = {d.month for d in first.dates()}
    assert months <= set(range(1, 13)) and len(first.dates()) == synthetic.DEFAULT_N_PERIODS


def test_planted_momentum_has_persistent_cross_sectional_spread() -> None:
    panel = synthetic.planted_momentum(seed=0, strength=0.01, noise=0.0)
    assets = panel.assets()

    # With zero noise the per-asset mean return is exactly its drift, ordered.
    means = {
        asset: sum(panel.history(asset, "return", end=panel.dates()[-1], periods=999))
        for asset in assets
    }
    ordered = [means[a] for a in assets]
    assert ordered == sorted(ordered)  # drift increases with asset index
    assert means[assets[-1]] > 0 > means[assets[0]]


def test_pure_noise_is_zero_mean_and_seed_varies() -> None:
    panel = synthetic.pure_noise(seed=1, n_periods=240)
    dates = panel.dates()
    pooled = [
        panel.value(d, asset, "return")
        for d in dates
        for asset in panel.assets()
    ]
    assert abs(sum(pooled) / len(pooled)) < 0.002  # ~zero mean

    other = synthetic.pure_noise(seed=2, n_periods=240)
    assert panel.records() != other.records()


def test_load_dataset_returns_hashed_provenance() -> None:
    loaded = load_dataset("planted_momentum", {"seed": 7})

    assert isinstance(loaded, LoadedDataset)
    assert loaded.frequency == "monthly"
    assert loaded.seed == 7
    assert loaded.content_hash == panel_hash(loaded.panel)
    provenance = loaded.provenance()
    assert provenance["name"] == "planted_momentum"
    assert provenance["n_assets"] == synthetic.DEFAULT_N_ASSETS
    assert "panel" not in provenance  # provenance is JSON-safe, no payload


def test_dataset_hash_is_stable_and_content_sensitive() -> None:
    a = load_dataset("planted_momentum", {"seed": 1})
    b = load_dataset("planted_momentum", {"seed": 1})
    c = load_dataset("planted_momentum", {"seed": 2})

    assert a.content_hash == b.content_hash
    assert a.content_hash != c.content_hash


def test_unknown_dataset_raises() -> None:
    with pytest.raises(ValueError, match="unknown dataset"):
        load_dataset("nonexistent")


def test_french_loader_parses_fixture_to_decimals() -> None:
    panel = french.load_french_momentum(FRENCH_FIXTURE)

    assert set(panel.assets()) == {"Lo PRIOR", "Hi PRIOR"}
    first_date = panel.dates()[0]
    assert panel.value(first_date, "Hi PRIOR", "return") == pytest.approx(0.023)
    assert panel.value(first_date, "Lo PRIOR", "return") == pytest.approx(0.008)


def test_french_loader_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError, match="French momentum fixture"):
        french.load_french_momentum("data/raw/does_not_exist.csv")
