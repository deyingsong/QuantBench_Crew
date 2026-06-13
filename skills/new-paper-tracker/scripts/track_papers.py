#!/usr/bin/env python3
"""Run QuantBench Scout's date-window paper tracker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quantbench_crew.main import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(["track", *sys.argv[1:]]))
