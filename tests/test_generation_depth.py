"""QB-29/30/31: spec invariants, numeric sandbox, agent adapter."""

from pathlib import Path

import pytest

from quantbench_crew.datasets import synthetic
from quantbench_crew.models import MethodSpec, Paper
from quantbench_crew.numeric import numpy_available
from quantbench_crew.skills.coder.agent_adapter import (
    HeadlessClaudeBackend,
    StubAgentBackend,
)
from quantbench_crew.skills.coder.code_generation import (
    CodeGenerationSkill,
    reference_source,
)
from quantbench_crew.skills.coder.templates import (
    compose_test_script,
    parse_template_result,
    spec_invariants,
    template_test_count,
)
from quantbench_crew.tools.code_runner import (
    NUMERIC_ALLOWED_IMPORTS,
    check_code,
    run_sandboxed,
)

LONG_ONLY_CHEATER = '''
class S:
    def __init__(self, params=None):
        self.params = params or {}
    def fit(self, data, train_end):
        pass
    def weights(self, data, as_of):
        view = data.up_to(as_of)
        # long-only: violates the zero-net invariant for a long-short spec
        return {a: 1.0 / len(view.assets()) for a in view.assets()}
def build_strategy(params=None):
    return S(params)
'''


def _spec(construction: str) -> MethodSpec:
    return MethodSpec(
        paper=Paper(title="x", abstract=""),
        universe="US stocks",
        frequency="monthly",
        signal_definition="past returns",
        portfolio_construction=construction,
        rebalance_frequency="monthly",
        holding_period="1 month",
        hyperparameters={"formation_months": 6},
    )


# --- QB-29: spec-derived invariants -----------------------------------------

def test_long_short_spec_adds_zero_net_invariant() -> None:
    spec = _spec("equal-weighted winner-minus-loser decile portfolio")
    kinds = {inv["kind"] for inv in spec_invariants(spec)}
    assert "zero_net" in kinds
    assert "uniform_magnitude" in kinds
    assert template_test_count(spec) == 3 + len(spec_invariants(spec))


def test_reference_passes_all_invariants_but_cheater_fails_zero_net() -> None:
    spec = _spec("equal-weighted long-short decile portfolio")

    ref = parse_template_result(run_sandboxed(compose_test_script(reference_source(), spec)).stdout)
    assert ref["passed"] == ref["total"]  # reference satisfies every invariant

    cheat = parse_template_result(run_sandboxed(compose_test_script(LONG_ONLY_CHEATER, spec)).stdout)
    categories = {f.split(":")[0] for f in cheat["failures"]}
    assert "zero_net" in categories  # long-only book fails the long-short invariant
    assert cheat["passed"] < cheat["total"]


# --- QB-30: vetted numerical sandbox ----------------------------------------

def test_numeric_allowlist_permits_numpy_but_blocks_os() -> None:
    assert check_code("import numpy as np", NUMERIC_ALLOWED_IMPORTS) == []
    assert check_code("import pandas", NUMERIC_ALLOWED_IMPORTS) == []
    assert check_code("import os", NUMERIC_ALLOWED_IMPORTS)  # still blocked
    assert check_code("import socket", NUMERIC_ALLOWED_IMPORTS)  # network still blocked


def test_default_allowlist_still_blocks_numpy() -> None:
    # Numeric tier is opt-in; the default stdlib sandbox must still reject it.
    assert check_code("import numpy")  # non-empty violations


@pytest.mark.skipif(not numpy_available(), reason="numpy not installed")
def test_numeric_sandbox_executes_numpy() -> None:
    source = "import numpy as np\nprint(int(np.array([1, 2, 3]).sum()))"
    result = run_sandboxed(source, allowed_imports=NUMERIC_ALLOWED_IMPORTS)
    assert result.status == "ok"
    assert result.stdout.strip() == "6"


def test_numeric_sandbox_still_blocks_forbidden_import() -> None:
    result = run_sandboxed("import os\nprint(os.getcwd())", allowed_imports=NUMERIC_ALLOWED_IMPORTS)
    assert result.status == "blocked"


# --- QB-31: agent adapter ----------------------------------------------------

def _golden_analysis():
    from quantbench_crew.agents.reader import QuantReaderAgent
    from quantbench_crew.tools.arxiv_tool import load_local_papers

    paper = load_local_papers(Path(__file__).parent / "fixtures" / "golden_paper.json")[0]
    return QuantReaderAgent().analyze(paper)


def _agent_config(iterations: int = 1) -> dict:
    return {
        "llm": {"cost_cap_usd": 2.0},
        "agents": {
            "quant_coder": {
                "skills": {
                    "code_generation": {
                        "enabled": True,
                        "iterations": iterations,
                        "adapter": "agent",
                    }
                }
            }
        },
    }


def test_agent_backend_produces_passing_candidate(make_ctx) -> None:
    analysis = _golden_analysis()
    candidate = reference_source() + "\n# agent-generated variant\n"
    backend = StubAgentBackend(f"```python\n{candidate}```")
    ctx = make_ctx(config=_agent_config(iterations=1))

    result = CodeGenerationSkill().run(
        ctx, analysis=analysis, plan=None, agent_backend=backend
    )

    # The agent backend was driven through the generate-test-fix loop and its
    # candidate passed every template/invariant check. (It ties the equally
    # good reference, which the search keeps as the simpler winner — so the
    # winning *source* may be the reference; what matters is the agent ran and
    # produced a passing candidate within budget.)
    assert result.status == "ok"
    assert backend.calls >= 1
    assert result.payload["llm_iterations"] == 1
    assert result.payload["candidates_evaluated"] == 2
    assert result.payload["tests_passed"] == result.payload["tests_total"]


def test_unavailable_agent_backend_falls_back(make_ctx) -> None:
    backend = StubAgentBackend("unused", available=False)
    ctx = make_ctx(config=_agent_config(iterations=1))  # ctx.llm is None

    result = CodeGenerationSkill().run(
        ctx, analysis=_golden_analysis(), plan=None, agent_backend=backend
    )

    assert result.status == "ok"  # deterministic reference fallback still passes
    assert result.payload["source"] == "fallback"
    assert any("unavailable" in note for note in result.notes)
    assert backend.calls == 0


def test_headless_backend_unavailable_without_cli(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert HeadlessClaudeBackend().available() is False
