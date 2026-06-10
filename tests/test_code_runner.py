"""QB-10 acceptance: static gating and sandboxed execution."""

from quantbench_crew.tools.code_runner import check_code, run_sandboxed


def test_check_code_flags_forbidden_imports() -> None:
    assert any("'os'" in v for v in check_code("import os"))
    assert any("subprocess" in v for v in check_code("from subprocess import run"))
    assert check_code("import socket")  # network is not in the allowlist


def test_check_code_flags_banned_calls_and_dunders() -> None:
    assert any("eval" in v for v in check_code("eval('1')"))
    assert any("open" in v for v in check_code("open('x')"))
    assert any("getattr" in v for v in check_code("getattr(int, 'x')"))
    assert any("dunder" in v for v in check_code("x = ().__class__"))
    assert any("__builtins__" in v for v in check_code("y = __builtins__"))


def test_check_code_accepts_clean_strategy_code() -> None:
    source = (
        "import math\n"
        "class S:\n"
        "    def __init__(self, params=None):\n"
        "        self.params = params or {}\n"
        "    def fit(self, data, train_end):\n"
        "        pass\n"
        "    def weights(self, data, as_of):\n"
        "        return {a: 1.0 for a in data.assets()}\n"
        "def build_strategy(params=None):\n"
        "    return S(params)\n"
    )
    assert check_code(source) == []


def test_check_code_reports_syntax_errors() -> None:
    assert any("syntax error" in v for v in check_code("def broken(:"))


def test_sandbox_runs_clean_script_and_captures_stdout() -> None:
    result = run_sandboxed("print('hello sandbox')")

    assert result.status == "ok"
    assert result.returncode == 0
    assert "hello sandbox" in result.stdout


def test_sandbox_blocks_forbidden_import_before_execution() -> None:
    result = run_sandboxed("import os\nprint(os.getcwd())")

    assert result.status == "blocked"
    assert result.returncode is None
    assert result.violations


def test_sandbox_kills_infinite_loop() -> None:
    result = run_sandboxed("while True:\n    pass", timeout=3.0, cpu_seconds=1)

    assert result.status in ("timeout", "error")
    assert result.returncode != 0


def test_sandbox_captures_errors_with_traceback() -> None:
    result = run_sandboxed("raise ValueError('boom')")

    assert result.status == "error"
    assert "boom" in result.stderr


def test_sandbox_hash_seed_is_pinned_across_runs() -> None:
    script = "print(hash('quantbench'))"

    first = run_sandboxed(script)
    second = run_sandboxed(script)

    assert first.status == second.status == "ok"
    assert first.stdout == second.stdout
