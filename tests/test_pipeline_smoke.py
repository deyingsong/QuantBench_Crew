from pathlib import Path

from quantbench_crew.main import build_parser, main


def test_pipeline_runs_and_writes_reports_by_default(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "run",
            "--source", "local",
            "--max-papers", "1",
            "--report-dir", str(tmp_path / "reports"),
            "--runs-dir", str(tmp_path / "runs"),
        ]
    )

    capsys.readouterr()
    assert exit_code == 0
    # --write-reports defaults ON: the review markdown and the generated
    # strategy module both land in the report dir.
    reports = list((tmp_path / "reports").glob("*.md"))
    strategies = list((tmp_path / "reports").glob("*_strategy.py"))
    assert len(reports) == 1
    assert len(strategies) == 1
    assert "def build_strategy" in strategies[0].read_text(encoding="utf-8")


def test_no_write_reports_disables_output(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "run",
            "--source", "local",
            "--max-papers", "1",
            "--no-write-reports",
            "--report-dir", str(tmp_path / "reports"),
            "--runs-dir", str(tmp_path / "runs"),
        ]
    )

    capsys.readouterr()
    assert exit_code == 0
    assert not (tmp_path / "reports").exists()


def test_write_reports_flag_defaults_true() -> None:
    args = build_parser().parse_args(["run"])
    assert args.write_reports is True

    args = build_parser().parse_args(["run", "--no-write-reports"])
    assert args.write_reports is False
