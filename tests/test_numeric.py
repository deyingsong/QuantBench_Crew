"""QB-23 acceptance: numeric-stack availability seam (env-independent)."""

from importlib.util import find_spec

from quantbench_crew import numeric


def test_helpers_match_find_spec() -> None:
    assert numeric.numpy_available() == (find_spec("numpy") is not None)
    assert numeric.pandas_available() == (find_spec("pandas") is not None)
    assert numeric.sklearn_available() == (find_spec("sklearn") is not None)


def test_stack_is_conjunction_of_parts() -> None:
    assert numeric.numeric_stack_available() == (
        numeric.numpy_available()
        and numeric.pandas_available()
        and numeric.sklearn_available()
    )


def test_helpers_return_bool() -> None:
    for fn in (
        numeric.numpy_available,
        numeric.pandas_available,
        numeric.sklearn_available,
        numeric.numeric_stack_available,
    ):
        assert isinstance(fn(), bool)
