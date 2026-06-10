"""Prompt templates for LLM-backed skills.

Templates are plain text files in this package, loaded by name and formatted
with ``str.format``. Keeping them as files (rather than inline strings) makes
prompt diffs reviewable and keeps the recorded-fixture fingerprints stable.
"""

from __future__ import annotations

from importlib import resources


def load_prompt(name: str) -> str:
    """Return the prompt template ``<name>.txt`` from this package."""

    return (
        resources.files(__package__)
        .joinpath(f"{name}.txt")
        .read_text(encoding="utf-8")
    )
