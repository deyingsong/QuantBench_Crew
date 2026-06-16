"""Configuration helpers for QuantBench Crew."""

from __future__ import annotations

import json
import os
import shutil
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


def load_env_file(path: str | Path = ".env", *, override: bool = False) -> dict[str, str]:
    """Load simple KEY=VALUE entries from a local dotenv file into the process.

    The parser intentionally supports the common subset used by `.env.example`:
    comments, blank lines, optional `export`, inline comments after unquoted
    values, and single/double-quoted values. Existing environment variables win
    unless `override=True`.
    """

    env_path = Path(path)
    if not env_path.exists():
        return {}

    loaded: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            continue
        parsed = _parse_env_value(value)
        loaded[key] = parsed
        if override or key not in os.environ:
            os.environ[key] = parsed
    return loaded


def init_env_file(
    path: str | Path = ".env",
    *,
    template: str | Path = ".env.example",
    force: bool = False,
) -> Path:
    """Create a user-editable dotenv file from the checked-in template."""

    env_path = Path(path)
    template_path = Path(template)
    if env_path.exists() and not force:
        raise FileExistsError(f"{env_path} already exists; pass --force to overwrite it")
    if not template_path.exists():
        raise FileNotFoundError(f"Environment template not found: {template_path}")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, env_path)
    return env_path


def _parse_env_value(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    quote = value[0]
    if quote in {"'", '"'}:
        end = value.find(quote, 1)
        if end != -1:
            return value[1:end]
        return value[1:]
    return value.split("#", 1)[0].strip()


def project_root() -> Path:
    """Return the repository root when running from an editable checkout."""

    return Path(__file__).resolve().parents[2]
