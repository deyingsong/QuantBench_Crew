"""Code generation behind the ERA seams (QB-11).

``generate_fn`` emits candidate Strategy modules; ``execute_fn`` scores each
candidate in the sandbox as template tests passed (0..3) plus a structure
score (0..1). The Flat UCB search explores from the deterministic reference
template, so the worst case for the golden paper is the hand-written
momentum strategy itself — which passes every template test.

Generation adapters: ``complete`` (single-shot emission through the QB-02
LLM seam) is implemented; ``agent`` (headless Claude Code / Agent SDK with an
inner generate-test-fix loop, the roadmap's eventual default) is reserved in
config and rejected loudly until it lands. With no LLM configured the skill
runs fallback-only and says so.

Spend discipline: every generation call checks the per-paper cost cap
(``llm.cost_cap_usd``) against the manifest's accumulated LLM spend before
calling out; once exceeded, the search coasts on existing candidates. Every
candidate's score lands in the manifest — discarded trials included, because
uncounted trials are how selection bias creeps in.
"""

from __future__ import annotations

import inspect
import json
import re
from typing import Any

from quantbench_crew.agents import era
from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.benchmarks import reference_momentum
from quantbench_crew.models import MethodSpec, PaperAnalysis
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.llm import llm_for_agent
from quantbench_crew.skills.coder.agent_adapter import resolve_agent_backend
from quantbench_crew.skills.coder.templates import (
    compose_test_script,
    parse_template_result,
    template_params,
    template_test_count,
)
from quantbench_crew.tools.code_runner import check_code, run_sandboxed

PROMPT_NAME = "code_generation"
SYSTEM_PROMPT = (
    "You write small, correct, deterministic Python trading-strategy modules "
    "that satisfy an exact interface. Output only code."
)
DEFAULT_ITERATIONS = 3
DEFAULT_COST_CAP_USD = 2.0
MAX_CANDIDATE_CHARS = 20_000

_CODE_BLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def reference_source() -> str:
    """The reference momentum module's source, the fallback candidate."""

    return inspect.getsource(reference_momentum)


def build_generation_prompt(
    spec: MethodSpec | None, analysis: PaperAnalysis, feedback: str = ""
) -> str:
    template = load_prompt(PROMPT_NAME)
    if spec is not None:
        spec_fields = {
            "universe": spec.universe,
            "frequency": spec.frequency,
            "signal_definition": spec.signal_definition,
            "portfolio_construction": spec.portfolio_construction,
            "rebalance_frequency": spec.rebalance_frequency,
            "holding_period": spec.holding_period,
            "hyperparameters": spec.hyperparameters,
        }
    else:
        spec_fields = {
            "proposed_method": analysis.proposed_method,
            "metrics": list(analysis.metrics),
        }
    return template.format(
        spec_json=json.dumps(spec_fields, sort_keys=True, indent=2),
        feedback=feedback,
    )


def extract_module_source(text: str) -> str:
    """Pull the module source out of an LLM completion."""

    match = _CODE_BLOCK.search(text)
    if match:
        return match.group(1).strip() + "\n"
    if "def build_strategy" in text:
        return text.strip() + "\n"
    return ""


def structure_score(source: str) -> float:
    """Cheap structural prior in [0, 1], independent of test outcomes."""

    import ast

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0.0

    score = 0.0
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    if "build_strategy" in function_names:
        score += 0.4
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = {
                item.name for item in node.body if isinstance(item, ast.FunctionDef)
            }
            if {"fit", "weights"} <= methods:
                score += 0.3
                break
    if "up_to" in source or "history" in source:
        score += 0.2
    if len(source) <= MAX_CANDIDATE_CHARS:
        score += 0.1
    return score


class CodeGenerationSkill:
    """Emit and score Strategy candidates for the analyzed paper."""

    name = "code_generation"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        spec = analysis.method_spec
        settings = skill_settings(ctx.config, "quant_coder", self.name)
        iterations = int(settings.get("iterations", DEFAULT_ITERATIONS))
        adapter = str(settings.get("adapter", "complete"))
        if adapter not in ("complete", "agent"):
            raise ValueError(
                f"unknown generation adapter {adapter!r}; expected 'complete' or 'agent'"
            )
        llm_config = ctx.config.get("llm") or {}
        cost_cap = float(llm_config.get("cost_cap_usd", DEFAULT_COST_CAP_USD))

        notes: list[str] = []
        if spec is None:
            notes.append("no MethodSpec on analysis; generating from analysis fields")

        # Resolve the source generator. The agent adapter swaps the generator
        # for a headless Claude backend; the ERA search and sandbox oracle are
        # unchanged. An unavailable agent backend falls back to single-shot
        # through the coder's own LLM backbone.
        coder_llm = llm_for_agent(ctx.llm, "quant_coder")
        agent_backend = None
        if adapter == "agent":
            agent_backend = inputs.get("agent_backend") or resolve_agent_backend(settings)
            if not agent_backend.available():
                notes.append(
                    f"agent backend {agent_backend.name!r} unavailable; "
                    "falling back to single-shot complete"
                )
                agent_backend = None
                adapter = "complete"

        def generate_source(prompt: str, feedback: str) -> str | None:
            system_prompt = ctx.augment_system_prompt("quant_coder", SYSTEM_PROMPT)
            if agent_backend is not None:
                return agent_backend.generate(prompt, system_prompt, feedback)
            if coder_llm is not None:
                return coder_llm.complete(prompt, system=system_prompt).text
            return None

        evaluations: dict[str, dict[str, Any]] = {}

        def execute_fn(problem: era.Problem, solution: era.Solution) -> float:
            del problem
            info = evaluations.get(solution.program)
            if info is None:
                info = self._evaluate(solution.program, spec)
                evaluations[solution.program] = info
            return float(info["score"])

        initial = era.Solution(reference_source())
        initial_score = execute_fn(era.Problem(""), initial)

        best_solution, best_score = initial, initial_score
        gen_iterations = 0
        can_generate = agent_backend is not None or coder_llm is not None
        if not can_generate:
            notes.append(
                "no LLM configured for quant_coder and no agent backend; "
                "deterministic fallback candidate only"
            )
        elif iterations > 0:
            problem = era.Problem(
                description=json.dumps(
                    {"paper": analysis.paper.title, "spec": spec is not None,
                     "adapter": "agent" if agent_backend else "complete"},
                    sort_keys=True,
                )
            )

            def generate_fn(
                problem: era.Problem,
                parent_solution: era.Solution,
                parent_score: float,
            ) -> era.Solution:
                nonlocal gen_iterations
                # The complete path's spend is tracked in the manifest; the
                # agent path is bounded by the iteration budget (capturing
                # headless-claude cost into the manifest is a follow-up).
                spent = sum(
                    float(call.get("cost_usd", 0.0)) for call in ctx.manifest.llm_calls
                )
                if agent_backend is None and spent >= cost_cap:
                    if not any("cost cap" in note for note in notes):
                        notes.append(
                            f"per-paper cost cap reached (${spent:.4f} >= "
                            f"${cost_cap:.2f}); generation stopped"
                        )
                    return parent_solution

                parent_info = evaluations.get(parent_solution.program, {})
                feedback = ""
                failures = parent_info.get("failures") or []
                if failures:
                    feedback = (
                        "The previous candidate scored "
                        f"{parent_score:.2f} and failed these checks:\n- "
                        + "\n- ".join(str(item) for item in failures)
                        + "\nFix every failure."
                    )
                prompt = build_generation_prompt(spec, analysis, feedback)
                try:
                    text = generate_source(prompt, feedback)
                except Exception as exc:  # boundary: keep searching from parent
                    notes.append(f"generation call failed: {exc!r}")
                    return parent_solution
                gen_iterations += 1
                source = extract_module_source(text or "")
                if not source:
                    notes.append("generation produced no usable module source")
                    return parent_solution
                return era.Solution(source)

            best_solution, best_score = era.search(
                problem=problem,
                initial_solution=initial,
                initial_score=initial_score,
                generate_fn=generate_fn,
                execute_fn=execute_fn,
                num_iterations=iterations,
                c_puct=1.0,
            )

        best_info = evaluations[best_solution.program]
        passed_all = best_info["tests_passed"] == best_info["tests_total"]
        used_fallback = best_solution.program == initial.program

        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        code_path = "generated/strategy.py"
        store.write_text(code_path, best_solution.program)
        store.write_text(
            "generated/template_tests.py",
            compose_test_script(best_solution.program, spec),
        )
        store.write_json(
            "generated/candidates.json",
            [
                {
                    "score": info["score"],
                    "tests_passed": info["tests_passed"],
                    "tests_total": info["tests_total"],
                    "failures": info["failures"],
                    "sandbox_status": info["sandbox_status"],
                }
                for info in evaluations.values()
            ],
        )

        result = SkillResult(
            skill=self.name,
            status="ok" if passed_all else "failed",
            payload={
                "code_path": code_path,
                "entry_point": "build_strategy",
                "score": best_score,
                "tests_passed": best_info["tests_passed"],
                "tests_total": best_info["tests_total"],
                "failures": best_info["failures"],
                "params": template_params(spec),
                "source": "fallback" if used_fallback else ("agent" if agent_backend else "llm"),
                "candidates_evaluated": len(evaluations),
                "llm_iterations": gen_iterations,
            },
            artifacts=(code_path, "generated/template_tests.py", "generated/candidates.json"),
            notes=tuple(notes),
        )
        ctx.manifest.record_skill(result)
        return result

    def _evaluate(self, source: str, spec: MethodSpec | None) -> dict[str, Any]:
        """Score one candidate: template tests passed + structure prior."""

        total = template_test_count(spec)
        violations = check_code(source)
        if violations:
            return {
                "score": 0.0,
                "tests_passed": 0,
                "tests_total": total,
                "failures": [f"static: {violation}" for violation in violations],
                "sandbox_status": "blocked",
            }

        sandbox = run_sandboxed(compose_test_script(source, spec))
        outcome = parse_template_result(sandbox.stdout) if sandbox.status == "ok" else None
        if outcome is None:
            failure = f"sandbox: {sandbox.status}"
            if sandbox.stderr.strip():
                failure += f" ({sandbox.stderr.strip().splitlines()[-1]})"
            return {
                "score": 0.0,
                "tests_passed": 0,
                "tests_total": total,
                "failures": [failure],
                "sandbox_status": sandbox.status,
            }

        return {
            "score": float(outcome["passed"]) + structure_score(source),
            "tests_passed": int(outcome["passed"]),
            "tests_total": int(outcome["total"]),
            "failures": list(outcome.get("failures", [])),
            "sandbox_status": sandbox.status,
        }


@register_skill("quant_coder", "code_generation")
def _make_code_generation_skill() -> CodeGenerationSkill:
    return CodeGenerationSkill()
