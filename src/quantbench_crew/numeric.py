"""Optional numerical-stack availability seam.

The stdlib-only dry workflow is the permanent baseline. numpy / pandas /
scikit-learn live in the optional ``numeric`` dependency group and are used
only by the real-data and ML paths. Code that wants them calls these checks
and falls back (or reports "skipped") when they are absent, so the suite
passes with the group uninstalled.

Detection uses ``importlib.util.find_spec`` rather than importing, so a probe
is cheap and never triggers a heavy import as a side effect.
"""

from __future__ import annotations

from importlib.util import find_spec


def numpy_available() -> bool:
    return find_spec("numpy") is not None


def pandas_available() -> bool:
    return find_spec("pandas") is not None


def sklearn_available() -> bool:
    return find_spec("sklearn") is not None


def numeric_stack_available() -> bool:
    """True only when the full numeric group (numpy+pandas+sklearn) is present."""

    return numpy_available() and pandas_available() and sklearn_available()
