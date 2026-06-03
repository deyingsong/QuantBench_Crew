from pathlib import Path

from quantbench_crew.config import load_config


def test_load_yaml_config() -> None:
    config = load_config(Path("configs/agents.yaml"))

    assert "agents" in config
    assert "quant_scout" in config["agents"]
