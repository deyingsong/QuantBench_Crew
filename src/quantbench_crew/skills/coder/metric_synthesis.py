"""Metric synthesis: code paper-claimed metrics the suite doesn't know (QB-44).

The reader extracts claims by the *paper's* metric names; the bench computes
a fixed suite. When a claim's metric maps to nothing in that suite, this
coder skill generates a ``compute_metric(returns, periods_per_year)`` module
for it through the coder's LLM backbone, gates it through the sandbox AST
check, and validates it by executing it in the sandbox on a fixed test
series (the result must be a finite float). Validated modules are stored as
run artifacts; the bench's walk-forward skill then executes them — again in
the sandbox, never host-side — on the candidate's out-of-sample net returns
and merges the values into the achieved metrics under the claim's normalized
name, so claim comparison covers them with no alias configuration.

Offline-safe: with no LLM for the coder the skill records which metrics are
missing and skips, and those claims stay honestly "no achieved metric
mapped". Spend is bounded by the shared per-paper cost cap and a
``max_metrics`` setting.
"""

from __future__ import annotations

import json
from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.benchmarks.claims import normalize_metric_name, unmapped_claims
from quantbench_crew.benchmarks.protocols import WALK_FORWARD_METRIC_KEYS
from quantbench_crew.llm import llm_for_agent
from quantbench_crew.models import Claim, PaperAnalysis
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.coder.code_generation import extract_module_source
from quantbench_crew.tools.code_runner import check_code, run_sandboxed

PROMPT_NAME = "metric_synthesis"
SYSTEM_PROMPT = (
    "You implement standard quantitative-finance performance metrics as "
    "small, deterministic Python functions. Output only code."
)
DEFAULT_MAX_METRICS = 3
DEFAULT_COST_CAP_USD = 2.0

# Fixed validation vector: mixed signs, a zero, enough points for tails.
VALIDATION_RETURNS = (0.01, -0.02, 0.03, 0.0, -0.01, 0.02, 0.015, -0.005)
VALIDATION_PPY = 12.0


def build_metric_prompt(claim: Claim) -> str:
    template = load_prompt(PROMPT_NAME)
    return template.format(
        metric_name=claim.metric,
        unit=claim.unit or "not stated",
        context=claim.context or "not stated",
    )


def compose_metric_script(source: str, returns: list[float], ppy: float) -> str:
    """One sandbox-runnable script: metric module + JSON-printing harness."""

    harness = (
        "\n\n# === metric evaluation harness (generated) ===\n"
        "import json as _json\n"
        f"_returns = _json.loads('{json.dumps(list(returns))}')\n"
        f"_value = compute_metric(_returns, {float(ppy)})\n"
        'print(_json.dumps({"value": float(_value)}))\n'
    )
    return source.rstrip() + harness


def run_metric(
    source: str, returns: list[float], ppy: float
) -> tuple[float | None, str]:
    """Execute a metric module in the sandbox; return (value, error)."""

    violations = check_code(source)
    if violations:
        return None, f"static violations: {'; '.join(violations[:3])}"
    sandbox = run_sandboxed(compose_metric_script(source, returns, ppy))
    if sandbox.status != "ok":
        tail = sandbox.stderr.strip().splitlines()[-1:] or [sandbox.status]
        return None, f"sandbox {sandbox.status}: {tail[0]}"
    for line in reversed(sandbox.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = float(json.loads(line)["value"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
            if value != value or value in (float("inf"), float("-inf")):
                return None, "metric returned a non-finite value"
            return value, ""
    return None, "no value emitted"


class MetricSynthesisSkill:
    """Generate, gate, and validate metric modules for unmapped claims."""

    name = "metric_synthesis"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        settings = skill_settings(ctx.config, "quant_coder", self.name)
        max_metrics = int(settings.get("max_metrics", DEFAULT_MAX_METRICS))
        llm_config = ctx.config.get("llm") or {}
        cost_cap = float(llm_config.get("cost_cap_usd", DEFAULT_COST_CAP_USD))

        known = {key: 0.0 for key in WALK_FORWARD_METRIC_KEYS}
        missing = unmapped_claims(analysis.reproduction_target, known)
        notes: list[str] = []

        if not missing:
            result = SkillResult(
                skill=self.name,
                status="skipped",
                payload={"missing": [], "synthesized": {}},
                notes=("every claimed metric is covered by the built-in suite",),
            )
            ctx.manifest.record_skill(result)
            return result

        missing = missing[:max_metrics]
        missing_names = [normalize_metric_name(claim.metric) for claim in missing]
        client = llm_for_agent(ctx.llm, "quant_coder")
        synthesized: dict[str, dict[str, Any]] = {}

        if client is None:
            notes.append(
                "no LLM configured for quant_coder; unmapped metrics left "
                "unsynthesized: " + ", ".join(missing_names)
            )
        else:
            store = ArtifactStore(ctx.run_dir, ctx.manifest)
            for claim, metric_name in zip(missing, missing_names):
                spent = sum(
                    float(call.get("cost_usd", 0.0)) for call in ctx.manifest.llm_calls
                )
                if spent >= cost_cap:
                    notes.append(
                        f"per-paper cost cap reached (${spent:.4f} >= ${cost_cap:.2f}); "
                        f"skipping remaining metrics"
                    )
                    break
                try:
                    response = client.complete(
                        build_metric_prompt(claim),
                        system=ctx.augment_system_prompt("quant_coder", SYSTEM_PROMPT),
                    )
                except Exception as exc:  # boundary: record and move on
                    notes.append(f"{metric_name}: generation failed: {exc!r}")
                    continue
                source = extract_module_source(response.text)
                if not source or "def compute_metric" not in source:
                    notes.append(f"{metric_name}: completion had no compute_metric module")
                    continue
                value, error = run_metric(source, list(VALIDATION_RETURNS), VALIDATION_PPY)
                if value is None:
                    notes.append(f"{metric_name}: validation failed ({error})")
                    continue
                rel_path = f"generated/metrics/{metric_name}.py"
                store.write_text(rel_path, source)
                synthesized[metric_name] = {
                    "path": rel_path,
                    "validated": True,
                    "validation_value": value,
                    "claim_metric": claim.metric,
                }
                notes.append(f"{metric_name}: synthesized and validated ({value:.6f})")

        result = SkillResult(
            skill=self.name,
            status="ok" if synthesized else "skipped",
            payload={"missing": missing_names, "synthesized": synthesized},
            artifacts=tuple(entry["path"] for entry in synthesized.values()),
            notes=tuple(notes),
        )
        ctx.manifest.record_skill(result)
        return result


@register_skill("quant_coder", "metric_synthesis")
def _make_metric_synthesis_skill() -> MetricSynthesisSkill:
    return MetricSynthesisSkill()
