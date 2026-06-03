"""Controlled local command runner for future reproducibility checks."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


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
