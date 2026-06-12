"""Agent Skills: SKILL.md parsing, route-2 injection, route-1 harness port."""

import sys
from pathlib import Path

import pytest

from quantbench_crew.agent_skills import (
    AGENT_SKILL_DIRS,
    compose_system,
    load_agent_skill,
    parse_skill_markdown,
)
from quantbench_crew.llm import (
    DEFAULT_MODEL,
    HarnessClient,
    PerAgentLLMRouter,
    RecordedStubClient,
    SkillAugmentedClient,
    build_llm_client,
    request_fingerprint,
)
from quantbench_crew.skills.reader.method_spec import (
    SYSTEM_PROMPT as READER_SYSTEM,
    MethodSpecExtractionSkill,
    build_method_spec_prompt,
)
from tests.test_llm_router import _golden_analysis  # reuse the shared fixture


# --- SKILL.md format ---------------------------------------------------------

def test_all_five_agents_have_valid_skills() -> None:
    for agent, skill_dir in AGENT_SKILL_DIRS.items():
        skill = load_agent_skill(agent)
        assert skill is not None, f"missing skills/{skill_dir}/SKILL.md"
        assert skill.name == skill_dir
        assert len(skill.description) <= 1024
        assert skill.body  # non-empty instructions


def test_parse_skill_markdown_frontmatter_and_body() -> None:
    skill = parse_skill_markdown(
        "---\nname: demo-skill\ndescription: What and when.\n---\n\nBody text.\n"
    )
    assert skill.name == "demo-skill"
    assert skill.description == "What and when."
    assert skill.body == "Body text."


def test_parse_skill_markdown_rejects_bad_files() -> None:
    with pytest.raises(ValueError, match="frontmatter"):
        parse_skill_markdown("no frontmatter at all")
    with pytest.raises(ValueError, match="never closed"):
        parse_skill_markdown("---\nname: x\ndescription: y\nbody without close")
    with pytest.raises(ValueError, match="name and description"):
        parse_skill_markdown("---\nname: only-name\n---\nbody")


def test_missing_skill_or_unknown_agent_is_none(tmp_path: Path) -> None:
    assert load_agent_skill("quant_reader", tmp_path) is None  # empty dir
    assert load_agent_skill("not_an_agent") is None


def test_compose_system_orders_skill_first() -> None:
    skill = parse_skill_markdown(
        "---\nname: demo\ndescription: d.\n---\nAlways be careful."
    )
    composed = compose_system(skill, "Answer with JSON only.")
    assert composed.startswith("# Skill: demo")
    assert "Always be careful." in composed
    assert composed.endswith("Answer with JSON only.")
    assert compose_system(skill, "") == "# Skill: demo\n\nAlways be careful."


# --- route 2: injection through the router ----------------------------------

PER_AGENT_STUB = {
    "llm": {
        "provider": "per-agent",
        "agents": {"quant_reader": {"provider": "stub"}},
    }
}


def test_router_injects_reader_skill_into_system_prompt(make_ctx) -> None:
    analysis = _golden_analysis()
    prompt = build_method_spec_prompt(analysis)
    reader_skill = load_agent_skill("quant_reader")
    augmented_system = compose_system(reader_skill, READER_SYSTEM)
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, augmented_system): {
            "text": '{"universe": "US common stocks", "frequency": "monthly",'
            ' "signal_definition": "past 6-month return",'
            ' "portfolio_construction": "decile long-short",'
            ' "rebalance_frequency": "monthly", "holding_period": "6 months",'
            ' "confidence": 0.9}',
            "model": DEFAULT_MODEL,
            "input_tokens": 100,
            "output_tokens": 50,
        }
    }
    ctx = make_ctx()
    # Build through the seam so injection applies, then swap in fixtures.
    router = build_llm_client(PER_AGENT_STUB)
    assert isinstance(router, PerAgentLLMRouter)
    ctx.llm = PerAgentLLMRouter(
        {
            "quant_reader": SkillAugmentedClient(
                RecordedStubClient(fixtures),
                lambda system: compose_system(reader_skill, system),
            )
        }
    )

    result = MethodSpecExtractionSkill().run(ctx, analysis=analysis)

    # The fixture only matches the skill-augmented system prompt, so a
    # successful "llm" extraction proves the injection reached the call.
    assert result.payload["source"] == "llm"


def test_build_llm_client_wraps_with_skill_by_default() -> None:
    router = build_llm_client(PER_AGENT_STUB)
    client = router.for_agent("quant_reader")

    assert isinstance(client, SkillAugmentedClient)
    assert client.name == "recorded-stub"  # name passthrough


def test_skills_dir_empty_disables_injection() -> None:
    config = {
        "llm": {
            "provider": "per-agent",
            "skills_dir": "",
            "agents": {"quant_reader": {"provider": "stub"}},
        }
    }
    client = build_llm_client(config).for_agent("quant_reader")

    assert not isinstance(client, SkillAugmentedClient)


# --- route 1: the harness port ------------------------------------------------

def test_harness_client_echo_round_trip() -> None:
    client = HarnessClient(
        "claude", "test-model", command=["/bin/echo", "{model}::{prompt}"], timeout=10.0
    )
    assert client.available()

    response = client.complete("write code", system="be careful")

    assert response.model == "test-model"
    assert response.text.startswith("test-model::")
    # No {system} slot in the template -> system is prepended to the prompt.
    assert "be careful" in response.text and "write code" in response.text
    assert response.cost_usd == 0.0


def test_harness_client_unavailable_when_cli_missing() -> None:
    client = HarnessClient("claude", "m", command=["definitely-not-a-real-cli", "{prompt}"])
    assert client.available() is False


def test_harness_failure_raises_oserror_for_skill_fallback() -> None:
    failing = HarnessClient(
        "claude", "m", command=[sys.executable, "-c", "import sys; sys.exit(3)"]
    )
    with pytest.raises(OSError, match="exited 3"):
        failing.complete("q")

    silent = HarnessClient("claude", "m", command=[sys.executable, "-c", "pass"])
    with pytest.raises(OSError, match="no output"):
        silent.complete("q")


def test_mode_harness_via_config_builds_harness_client(monkeypatch) -> None:
    config = {
        "llm": {
            "provider": "per-agent",
            "skills_dir": "",
            "agents": {
                "quant_coder": {
                    "provider": "anthropic",
                    "model": "claude-opus-4-8",
                    "mode": "harness",
                    "harness_command": ["/bin/echo", "{prompt}"],
                }
            },
        }
    }
    router = build_llm_client(config)
    client = router.for_agent("quant_coder")

    assert isinstance(client, HarnessClient)
    assert client.name == "harness:anthropic"
    assert client.complete("hello").text == "hello"


def test_mode_harness_missing_cli_falls_back_offline() -> None:
    config = {
        "llm": {
            "provider": "per-agent",
            "agents": {
                "quant_coder": {
                    "provider": "anthropic",
                    "mode": "harness",
                    "harness_command": ["definitely-not-a-real-cli", "{prompt}"],
                }
            },
        }
    }
    router = build_llm_client(config)

    assert router.for_agent("quant_coder") is None
    assert "host CLI not on PATH" in router.reasons["quant_coder"]


def test_unknown_mode_rejected() -> None:
    config = {
        "llm": {
            "provider": "per-agent",
            "agents": {"quant_coder": {"provider": "stub", "mode": "telepathy"}},
        }
    }
    with pytest.raises(ValueError, match="unknown llm mode"):
        build_llm_client(config)
