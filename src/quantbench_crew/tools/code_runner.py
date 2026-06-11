"""Controlled local execution of untrusted candidate code.

This module is the single home for static gating and sandboxed execution of
LLM-generated strategies (QB-10). Defense layers, mapped to the threat model
for generated trading code:

==========================  ===================================================
Threat                      Mitigation
==========================  ===================================================
Network exfiltration /      Import allowlist (no socket/urllib/http/requests);
data poisoning              scrubbed environment; ``-s -P`` interpreter flags.
Shell / process escape      os, sys, subprocess, multiprocessing not in the
                            allowlist; RLIMIT_NPROC blocks fork bombs.
Resource exhaustion         RLIMIT_CPU + wall-clock timeout kill loops;
                            RLIMIT_AS (best effort; unreliable on macOS) and
                            RLIMIT_FSIZE cap memory and file writes.
Filesystem access           ``open`` and friends are banned calls; cwd is a
                            throwaway temp dir; FSIZE caps what slips through.
Dynamic-eval evasion        eval/exec/compile/__import__/getattr-style calls
                            and dunder attribute access are AST violations.
Nondeterminism              PYTHONHASHSEED pinned; candidates must pass the
                            determinism template test regardless.
==========================  ===================================================

Known limitations, on purpose and on record: AST gating is defense-in-depth,
not a security boundary — sufficiently creative attribute laundering can in
principle evade static checks, which is why execution always happens in a
separate isolated process with rlimits, never in the host interpreter, and
why the import allowlist (not the ban list) is the primary control. Treat
candidate output as data, never re-execute it host-side.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ALLOWED_IMPORTS = frozenset(
    {
        "__future__",
        "bisect",
        "collections",
        "dataclasses",
        "datetime",
        "functools",
        "heapq",
        "itertools",
        "json",
        "math",
        "operator",
        "random",
        "statistics",
        "typing",
    }
)

# Opt-in numerical tier (QB-30) for *generated ML strategies only*. This
# widens the attack surface — numpy/pandas can touch the filesystem (e.g.
# numpy.fromfile, pandas.read_csv) — so it is never the default. The isolated
# subprocess, scrubbed environment, RLIMIT_FSIZE/CPU/AS caps, and the absence
# of os/sys/subprocess/socket from the allowlist remain the actual boundary;
# the import allowlist is defense-in-depth, not the boundary. Reviewed via
# /ecc:security-review. Keep this set pinned and minimal.
NUMERIC_ALLOWED_IMPORTS = DEFAULT_ALLOWED_IMPORTS | frozenset(
    {"numpy", "pandas", "sklearn", "scipy"}
)

BANNED_CALLS = frozenset(
    {
        "breakpoint",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "globals",
        "input",
        "locals",
        "memoryview",
        "open",
        "setattr",
        "vars",
        "__import__",
    }
)

BANNED_NAMES = frozenset({"__builtins__", "__import__", "__loader__", "__spec__"})


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class SandboxResult:
    """Outcome of one sandboxed execution attempt."""

    status: str          # "ok" | "blocked" | "timeout" | "error"
    returncode: int | None
    stdout: str
    stderr: str
    violations: tuple[str, ...] = ()


def run_command(command: list[str], timeout: int = 60) -> CommandResult:
    """Run a local command without invoking a shell."""

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CommandResult(
        command=tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def check_code(
    source: str, allowed_imports: frozenset[str] | set[str] = DEFAULT_ALLOWED_IMPORTS
) -> list[str]:
    """Static AST gate: return violations; empty list means admissible."""

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"syntax error: {exc.msg} (line {exc.lineno})"]

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in allowed_imports:
                    violations.append(f"import of {alias.name!r} not in allowlist")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level or root not in allowed_imports:
                violations.append(f"import from {node.module!r} not in allowlist")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in BANNED_CALLS:
                violations.append(f"banned call {func.id!r}")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            violations.append(f"dunder attribute access {node.attr!r}")
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            violations.append(f"banned name {node.id!r}")
    return violations


def _apply_rlimits(cpu_seconds: int, memory_bytes: int) -> None:
    # Runs in the forked child before exec. Each limit is best-effort: some
    # platforms (notably macOS for RLIMIT_AS) accept but do not enforce.
    import resource

    for limit, value in (
        (resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1)),
        (resource.RLIMIT_AS, (memory_bytes, memory_bytes)),
        (resource.RLIMIT_FSIZE, (10_000_000, 10_000_000)),
        (resource.RLIMIT_NPROC, (128, 128)),
    ):
        try:
            resource.setrlimit(limit, value)
        except (ValueError, OSError):
            pass


def run_sandboxed(
    source: str,
    *,
    timeout: float = 15.0,
    cpu_seconds: int = 10,
    memory_bytes: int = 512_000_000,
    allowed_imports: frozenset[str] | set[str] = DEFAULT_ALLOWED_IMPORTS,
) -> SandboxResult:
    """Statically gate, then execute ``source`` in an isolated subprocess."""

    violations = check_code(source, allowed_imports)
    if violations:
        return SandboxResult(
            status="blocked",
            returncode=None,
            stdout="",
            stderr="",
            violations=tuple(violations),
        )

    with tempfile.TemporaryDirectory(prefix="qb-sandbox-") as workdir:
        script = Path(workdir) / "candidate.py"
        script.write_text(source, encoding="utf-8")
        try:
            # -s (no user site) -P (no script dir on sys.path) -B (no .pyc).
            # Deliberately not -I: isolated mode implies -E, which would
            # discard the pinned PYTHONHASHSEED. The env dict below is the
            # entire child environment, so nothing else leaks in anyway.
            completed = subprocess.run(
                [sys.executable, "-s", "-P", "-B", script.name],
                cwd=workdir,
                env={"PYTHONHASHSEED": "0", "PATH": "/usr/bin:/bin"},
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=lambda: _apply_rlimits(cpu_seconds, memory_bytes),
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(
                status="timeout",
                returncode=None,
                stdout=_decode(exc.stdout),
                stderr=_decode(exc.stderr),
            )

    return SandboxResult(
        status="ok" if completed.returncode == 0 else "error",
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _decode(stream: object) -> str:
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", errors="replace")
    return str(stream)
