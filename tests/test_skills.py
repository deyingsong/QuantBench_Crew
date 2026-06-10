import pytest

from quantbench_crew.agents import (
    QuantBenchAgent,
    QuantCoderAgent,
    QuantReaderAgent,
    QuantReviewerAgent,
    QuantScoutAgent,
)
from quantbench_crew.skills import SkillRegistry, default_registry
from quantbench_crew.skills.base import Skill, SkillResult


class StubSkill:
    def __init__(self, name: str, available: bool = True) -> None:
        self.name = name
        self._available = available

    def available(self) -> bool:
        return self._available

    def run(self, ctx, **inputs) -> SkillResult:
        return SkillResult(skill=self.name, status="ok", payload=dict(inputs))


def _config(agent: str, skills: dict) -> dict:
    return {"agents": {agent: {"skills": skills}}}


def test_register_and_create() -> None:
    registry = SkillRegistry()
    registry.register("quant_scout", "demo", lambda: StubSkill("demo"))

    skill = registry.create("quant_scout", "demo")

    assert isinstance(skill, Skill)
    assert skill.name == "demo"
    assert registry.names("quant_scout") == ("demo",)


def test_register_as_decorator() -> None:
    registry = SkillRegistry()

    @registry.register("quant_reader", "demo")
    def make_demo() -> StubSkill:
        return StubSkill("demo")

    assert registry.create("quant_reader", "demo").name == "demo"


def test_duplicate_registration_raises() -> None:
    registry = SkillRegistry()
    registry.register("quant_scout", "demo", lambda: StubSkill("demo"))

    with pytest.raises(ValueError, match="already registered"):
        registry.register("quant_scout", "demo", lambda: StubSkill("demo"))


def test_resolve_returns_empty_when_no_skills_configured() -> None:
    registry = SkillRegistry()

    assert registry.resolve("quant_scout", {}) == {}
    assert registry.resolve("quant_scout", {"agents": {"quant_scout": {}}}) == {}


def test_resolve_toggles_on_enabled_flag() -> None:
    registry = SkillRegistry()
    registry.register("quant_scout", "demo", lambda: StubSkill("demo"))

    disabled = registry.resolve(
        "quant_scout", _config("quant_scout", {"demo": {"enabled": False}})
    )
    enabled = registry.resolve(
        "quant_scout", _config("quant_scout", {"demo": {"enabled": True}})
    )

    assert disabled == {}
    assert list(enabled) == ["demo"]
    assert enabled["demo"].name == "demo"


def test_disabled_unknown_skill_is_inert_but_enabled_unknown_raises() -> None:
    registry = SkillRegistry()

    assert (
        registry.resolve(
            "quant_scout", _config("quant_scout", {"future_skill": {"enabled": False}})
        )
        == {}
    )
    with pytest.raises(KeyError, match="Unknown skill"):
        registry.resolve(
            "quant_scout", _config("quant_scout", {"future_skill": {"enabled": True}})
        )


def test_fallback_selection_when_primary_unavailable() -> None:
    registry = SkillRegistry()
    registry.register(
        "quant_scout", "primary", lambda: StubSkill("primary", available=False),
        fallback="backup",
    )
    registry.register("quant_scout", "backup", lambda: StubSkill("backup"))

    resolved = registry.resolve(
        "quant_scout", _config("quant_scout", {"primary": {"enabled": True}})
    )

    assert resolved["primary"].name == "backup"


def test_exhausted_fallback_chain_raises() -> None:
    registry = SkillRegistry()
    registry.register(
        "quant_scout", "primary", lambda: StubSkill("primary", available=False)
    )

    with pytest.raises(LookupError, match="No available implementation"):
        registry.resolve(
            "quant_scout", _config("quant_scout", {"primary": {"enabled": True}})
        )


def test_fallback_cycle_raises() -> None:
    registry = SkillRegistry()
    registry.register(
        "quant_scout", "a", lambda: StubSkill("a", available=False), fallback="b"
    )
    registry.register(
        "quant_scout", "b", lambda: StubSkill("b", available=False), fallback="a"
    )

    with pytest.raises(LookupError, match="cycle"):
        registry.resolve("quant_scout", _config("quant_scout", {"a": {"enabled": True}}))


def test_shipped_config_resolves_no_skills() -> None:
    # Workstream B registers real skills, but the shipped config keeps every
    # entry disabled: default pipeline behavior stays the dry workflow.
    from quantbench_crew.config import load_config

    config = load_config("configs/agents.yaml")
    for agent in (
        "quant_scout",
        "quant_reader",
        "quant_coder",
        "quant_bench",
        "quant_reviewer",
    ):
        assert default_registry.resolve(agent, config) == {}


def test_workstream_b_skills_are_registered() -> None:
    assert "reproducibility_triage" in default_registry.names("quant_scout")
    assert default_registry.names("quant_reader") == (
        "method_spec_extraction",
        "pdf_acquisition",
        "target_table_extraction",
    )


def test_agents_accept_and_store_skills() -> None:
    skills = {"demo": StubSkill("demo")}

    assert QuantScoutAgent(skills=skills).skills["demo"].name == "demo"
    assert QuantReaderAgent(skills=skills).skills["demo"].name == "demo"
    assert QuantCoderAgent(skills=skills).skills["demo"].name == "demo"
    assert QuantBenchAgent(skills=skills).skills["demo"].name == "demo"
    assert QuantReviewerAgent(skills=skills).skills["demo"].name == "demo"


def test_agents_default_to_no_skills() -> None:
    assert QuantScoutAgent().skills == {}
    assert QuantBenchAgent().skills == {}
