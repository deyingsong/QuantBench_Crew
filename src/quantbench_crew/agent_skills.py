"""Agent Skills (open SKILL.md standard) for the five pipeline agents.

These are *instruction documents* in the Agent Skills format — YAML
frontmatter (name, description) plus a markdown body that teaches a model how
to do its job. They are intentionally distinct from the runtime plug-ins in
``quantbench_crew.skills`` (Python capabilities with ``run()`` methods).

Two consumption routes share these files:

- **Route 2 (default — prompt injection).** The per-agent LLM router wraps
  each backbone so the agent's skill body is prepended to the system prompt
  of every single-shot call. This is manual progressive disclosure: with one
  skill per agent, "load when relevant" reduces to "always load for that
  agent's calls".
- **Route 1 (harness mode).** When an agent is switched to ``mode: harness``,
  the same composed system prompt rides into the agent-host CLI invocation,
  and any standard-compliant host (Claude Code, Codex CLI, Gemini CLI, ...)
  can additionally discover the files natively from ``skills/``.

A missing skill file simply means no injection for that agent — never an
error — so the dry workflow and partial checkouts keep working.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from quantbench_crew.config import project_root

DEFAULT_SKILLS_DIR = "skills"

# Pipeline agent name -> skill directory (skill names are hyphenated per the
# Agent Skills naming convention).
AGENT_SKILL_DIRS = {
    "quant_scout": "quant-scout",
    "quant_reader": "quant-reader",
    "quant_coder": "quant-coder",
    "quant_bench": "quant-bench",
    "quant_reviewer": "quant-reviewer",
}


@dataclass(frozen=True)
class AgentSkill:
    """One parsed SKILL.md."""

    name: str
    description: str
    body: str
    path: str


def resolve_skills_dir(skills_dir: str | Path = DEFAULT_SKILLS_DIR) -> Path:
    """Resolve the skills directory, falling back to the repo root.

    Relative paths are tried against the current working directory first and
    the repository root second, so the CLI works from anywhere.
    """

    path = Path(skills_dir)
    if path.is_absolute() or path.exists():
        return path
    return project_root() / skills_dir


def parse_skill_markdown(text: str, path: str = "") -> AgentSkill:
    """Parse a SKILL.md: ``---`` YAML frontmatter, then the markdown body."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"SKILL.md missing frontmatter delimiter: {path or '<text>'}")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ValueError(f"SKILL.md frontmatter never closed: {path or '<text>'}") from None

    front = yaml.safe_load("\n".join(lines[1:end])) or {}
    body = "\n".join(lines[end + 1 :]).strip()
    name = str(front.get("name", "")).strip()
    description = str(front.get("description", "")).strip()
    if not name or not description:
        raise ValueError(f"SKILL.md frontmatter needs name and description: {path or '<text>'}")
    return AgentSkill(name=name, description=description, body=body, path=path)


def load_agent_skill(
    agent: str, skills_dir: str | Path = DEFAULT_SKILLS_DIR
) -> AgentSkill | None:
    """Load one agent's skill, or None when the file does not exist."""

    skill_dir = AGENT_SKILL_DIRS.get(agent)
    if skill_dir is None:
        return None
    skill_path = resolve_skills_dir(skills_dir) / skill_dir / "SKILL.md"
    if not skill_path.exists():
        return None
    return parse_skill_markdown(skill_path.read_text(encoding="utf-8"), str(skill_path))


def compose_system(skill: AgentSkill, system: str = "") -> str:
    """Compose the injected system prompt: skill body first, task second.

    The skill body is the stable per-agent prefix (cache-friendly); the
    per-call task instruction follows after a delimiter.
    """

    header = f"# Skill: {skill.name}\n\n{skill.body}"
    if not system:
        return header
    return f"{header}\n\n---\n\n{system}"
