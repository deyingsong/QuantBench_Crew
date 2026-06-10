"""Skill plumbing: the Skill protocol, SkillResult, and per-run context.

A skill is a named, per-agent capability with a typed result and an
availability check. Skills must keep a deterministic offline fallback so the
dry workflow always runs (see docs/skills-design.md, Guiding Principles).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from quantbench_crew.artifacts import RunManifest
    from quantbench_crew.llm import LLMClient


@dataclass(frozen=True)
class SkillResult:
    """Outcome of one skill invocation, recorded in the run manifest."""

    skill: str
    status: str                    # "ok" | "skipped" | "failed"
    payload: dict[str, Any] = field(default_factory=dict)
    artifacts: tuple[str, ...] = ()   # paths relative to the run directory
    notes: tuple[str, ...] = ()


@runtime_checkable
class Skill(Protocol):
    """A pluggable agent capability with an offline-checkable contract."""

    name: str

    def available(self) -> bool:
        """Return True when required dependencies and credentials exist."""
        ...

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        """Execute the skill and record artifacts in the run manifest."""
        ...


@dataclass
class RunContext:
    """Shared per-run state passed to every skill."""

    run_id: str
    run_dir: Path
    config: dict[str, Any]
    manifest: RunManifest
    llm: LLMClient | None = None


def skill_settings(config: Mapping[str, Any], agent: str, name: str) -> dict[str, Any]:
    """Return one skill's config entry from agents.yaml, minus ``enabled``.

    Skills read their tunables (thresholds, cache dirs, tolerances) from the
    run config at execution time, so toggling and tuning stay in one file.
    """

    agents = config.get("agents") or {}
    skills = (agents.get(agent) or {}).get("skills") or {}
    entry = skills.get(name) or {}
    return {key: value for key, value in entry.items() if key != "enabled"}
