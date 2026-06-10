"""Template tests: the reference passes; defective candidates fail by name."""

from quantbench_crew.skills.coder.code_generation import reference_source
from quantbench_crew.skills.coder.templates import (
    compose_test_script,
    parse_template_result,
)
from quantbench_crew.tools.code_runner import run_sandboxed

LOOKAHEAD_CHEATER = '''
class Cheater:
    def __init__(self, params=None):
        self.params = params or {}

    def fit(self, data, train_end):
        pass

    def weights(self, data, as_of):
        last = data.dates()[-1]  # peeks at the final date, wherever it is
        result = {}
        for asset in data.assets():
            value = data.value(last, asset, "return", 0.0)
            result[asset] = 1.0 if value > 0 else -1.0
        return result


def build_strategy(params=None):
    return Cheater(params)
'''

NONDETERMINISTIC = '''
import random


class Noisy:
    def __init__(self, params=None):
        self.params = params or {}

    def fit(self, data, train_end):
        pass

    def weights(self, data, as_of):
        return {asset: random.random() for asset in data.assets()}


def build_strategy(params=None):
    return Noisy(params)
'''

BROKEN = '''
def build_strategy(params=None):
    raise RuntimeError("cannot build")
'''


def _run(candidate: str) -> dict:
    result = run_sandboxed(compose_test_script(candidate, None))
    assert result.status == "ok", result.stderr
    outcome = parse_template_result(result.stdout)
    assert outcome is not None
    return outcome


def test_reference_momentum_passes_all_template_tests() -> None:
    outcome = _run(reference_source())

    assert outcome["passed"] == outcome["total"] == 3
    assert outcome["failures"] == []


def test_lookahead_cheater_fails_only_no_lookahead() -> None:
    outcome = _run(LOOKAHEAD_CHEATER)

    assert outcome["passed"] == 2
    categories = {failure.split(":")[0] for failure in outcome["failures"]}
    assert categories == {"no_lookahead"}


def test_nondeterministic_candidate_fails_determinism() -> None:
    outcome = _run(NONDETERMINISTIC)

    categories = {failure.split(":")[0] for failure in outcome["failures"]}
    assert "determinism" in categories
    assert outcome["passed"] < 3


def test_broken_candidate_scores_zero() -> None:
    outcome = _run(BROKEN)

    assert outcome["passed"] == 0
    assert any("shape" in failure for failure in outcome["failures"])
