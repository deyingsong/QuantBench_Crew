"""Skill registry and config wiring.

Skills are declared per agent in ``configs/agents.yaml`` under an optional
``skills:`` mapping and toggled with ``enabled``. Agents resolve their skills
through the registry; with every skill disabled the registry resolves to an
empty mapping and pipeline behavior is unchanged.

Resolution walks an explicit fallback chain: when a skill's implementation is
unavailable (missing credentials or optional dependencies), the registry
falls back to the registered fallback skill. An enabled skill whose entire
chain is unavailable raises, because a silent skip would hide a
misconfiguration — the design contract is that every chain terminates in a
deterministic offline implementation.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from quantbench_crew.skills.base import RunContext, Skill, SkillResult, skill_settings

__all__ = [
    "AGENT_NAMES",
    "RunContext",
    "Skill",
    "SkillRegistry",
    "SkillResult",
    "SkillSpec",
    "default_registry",
    "register_skill",
    "resolve_skills",
    "skill_settings",
]

AGENT_NAMES = (
    "quant_scout",
    "quant_reader",
    "quant_coder",
    "quant_bench",
    "quant_reviewer",
)


@dataclass(frozen=True)
class SkillSpec:
    """Registration record for one skill implementation."""

    agent: str
    name: str
    factory: Callable[[], Skill]
    fallback: str | None = None   # name of the same-agent fallback skill


class SkillRegistry:
    """Maps (agent, skill name) to skill factories with fallback chains."""

    def __init__(self) -> None:
        self._specs: dict[tuple[str, str], SkillSpec] = {}

    def register(
        self,
        agent: str,
        name: str,
        factory: Callable[[], Skill] | None = None,
        *,
        fallback: str | None = None,
    ) -> Callable[..., Any]:
        """Register a skill factory; usable directly or as a decorator."""

        if factory is None:
            def decorator(fn: Callable[[], Skill]) -> Callable[[], Skill]:
                self.register(agent, name, fn, fallback=fallback)
                return fn

            return decorator

        key = (agent, name)
        if key in self._specs:
            raise ValueError(f"Skill already registered: {agent}/{name}")
        self._specs[key] = SkillSpec(agent=agent, name=name, factory=factory, fallback=fallback)
        return factory

    def names(self, agent: str) -> tuple[str, ...]:
        return tuple(sorted(name for (owner, name) in self._specs if owner == agent))

    def spec(self, agent: str, name: str) -> SkillSpec:
        try:
            return self._specs[(agent, name)]
        except KeyError:
            registered = ", ".join(self.names(agent)) or "none"
            raise KeyError(
                f"Unknown skill {agent}/{name}; registered for {agent}: {registered}"
            ) from None

    def create(self, agent: str, name: str) -> Skill:
        """Instantiate the named skill without availability resolution."""

        return self.spec(agent, name).factory()

    def resolve(self, agent: str, config: Mapping[str, Any]) -> dict[str, Skill]:
        """Return enabled, available skills for one agent from the config.

        ``config`` is the full agents.yaml mapping. Disabled entries are
        inert even when unregistered, so configs may declare future skills
        ahead of their implementation. Enabled entries must be registered
        and must resolve to an available implementation via the fallback
        chain.
        """

        agent_config = (config.get("agents") or {}).get(agent) or {}
        skills_config = agent_config.get("skills") or {}

        resolved: dict[str, Skill] = {}
        for name, entry in skills_config.items():
            enabled = bool((entry or {}).get("enabled", False))
            if not enabled:
                continue
            resolved[name] = self._resolve_chain(agent, name)
        return resolved

    def _resolve_chain(self, agent: str, name: str) -> Skill:
        chain: list[str] = []
        current: str | None = name
        while current is not None:
            if current in chain:
                raise LookupError(
                    f"Skill fallback cycle for {agent}/{name}: {' -> '.join([*chain, current])}"
                )
            chain.append(current)
            spec = self.spec(agent, current)
            skill = spec.factory()
            if skill.available():
                return skill
            current = spec.fallback
        raise LookupError(
            f"No available implementation for {agent}/{name} "
            f"(tried: {' -> '.join(chain)}); every skill chain must end in a "
            "deterministic offline fallback"
        )


default_registry = SkillRegistry()


def register_skill(
    agent: str, name: str, *, fallback: str | None = None
) -> Callable[..., Any]:
    """Decorator registering a skill factory on the default registry."""

    return default_registry.register(agent, name, fallback=fallback)


def resolve_skills(agent: str, config: Mapping[str, Any]) -> dict[str, Skill]:
    """Resolve one agent's enabled skills from the default registry."""

    return default_registry.resolve(agent, config)


# Import skill implementations so their @register_skill decorators run when
# the package is imported. These must stay below the registry definitions.
from quantbench_crew.skills.bench import dataset_registry as _bench_dataset_registry  # noqa: E402,F401
from quantbench_crew.skills.bench import robustness_auditor as _bench_robustness_auditor  # noqa: E402,F401
from quantbench_crew.skills.bench import strategy_evaluator as _bench_strategy_evaluator  # noqa: E402,F401
from quantbench_crew.skills.bench import walk_forward as _bench_walk_forward  # noqa: E402,F401
from quantbench_crew.skills.coder import code_generation as _coder_code_generation  # noqa: E402,F401
from quantbench_crew.skills.coder import metric_synthesis as _coder_metric_synthesis  # noqa: E402,F401
from quantbench_crew.skills.reader import criticizer as _reader_criticizer  # noqa: E402,F401
from quantbench_crew.skills.reader import empirical_spec as _reader_empirical_spec  # noqa: E402,F401
from quantbench_crew.skills.reader import method_spec as _reader_method_spec  # noqa: E402,F401
from quantbench_crew.skills.reader import methodology_extractor as _reader_methodology  # noqa: E402,F401
from quantbench_crew.skills.reader import pdf_acquisition as _reader_pdf_acquisition  # noqa: E402,F401
from quantbench_crew.skills.reader import question_identifier as _reader_question  # noqa: E402,F401
from quantbench_crew.skills.reader import red_flag as _reader_red_flag  # noqa: E402,F401
from quantbench_crew.skills.reader import target_table as _reader_target_table  # noqa: E402,F401
from quantbench_crew.skills.reviewer import rubric as _reviewer_rubric  # noqa: E402,F401
from quantbench_crew.skills.scout import charter_relevance as _scout_charter_relevance  # noqa: E402,F401
from quantbench_crew.skills.scout import relevance_scorer as _scout_relevance_scorer  # noqa: E402,F401
from quantbench_crew.skills.scout import triage as _scout_triage  # noqa: E402,F401
