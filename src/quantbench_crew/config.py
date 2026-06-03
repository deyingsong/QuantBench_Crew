"""Configuration helpers for QuantBench Crew."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML or JSON configuration file."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    text = config_path.read_text(encoding="utf-8")
    if config_path.suffix.lower() == ".json":
        return json.loads(text)

    if config_path.suffix.lower() in {".yaml", ".yml"}:
        loaded = yaml.safe_load(text)
        return loaded or {}

    raise ValueError(f"Unsupported config type: {config_path.suffix}")


def project_root() -> Path:
    """Return the repository root when running from an editable checkout."""

    return Path(__file__).resolve().parents[2]
