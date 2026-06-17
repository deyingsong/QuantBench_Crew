import json
from pathlib import Path

from quantbench_crew.feedback import FEEDBACK_START, ensure_feedback_section
from quantbench_crew.main import build_parser, main


def test_init_command_creates_env_file(tmp_path: Path, capsys) -> None:
    template = tmp_path / ".env.example"
    target = tmp_path / ".env"
    template.write_text("OPENAI_API_KEY=\n", encoding="utf-8")

    exit_code = main(
        [
            "init",
            "--template",
            str(template),
            "--env-file",
            str(target),
        ]
    )

    assert exit_code == 0
    assert target.read_text(encoding="utf-8") == "OPENAI_API_KEY=\n"
    assert "Created" in capsys.readouterr().out


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


def test_memory_cli_remember_and_recall(tmp_path: Path, capsys) -> None:
    database = tmp_path / "memory.sqlite3"

    assert main(
        [
            "memory",
            "remember",
            "Use point-in-time data.",
            "--db",
            str(database),
            "--kind",
            "procedural",
        ]
    ) == 0
    proposed = json.loads(capsys.readouterr().out)
    assert proposed["status"] == "proposed"
    assert main(
        [
            "memory",
            "approve",
            proposed["memory_id"],
            "--db",
            str(database),
        ]
    ) == 0
    capsys.readouterr()
    assert main(
        [
            "memory",
            "recall",
            "--db",
            str(database),
            "--agent",
            "quant_reader",
        ]
    ) == 0

    recalled = json.loads(capsys.readouterr().out)
    assert recalled[0]["content"] == "Use point-in-time data."


def test_feedback_cli_ingest_and_approve(tmp_path: Path, capsys) -> None:
    database = tmp_path / "memory.sqlite3"
    report_path = tmp_path / "paper.md"
    report_path.write_text(
        ensure_feedback_section("# Paper\n", paper_slug="paper").replace(
            FEEDBACK_START + "\n",
            FEEDBACK_START + "\nQuant_reader should verify sample dates.\n",
        ),
        encoding="utf-8",
    )

    assert main(
        ["feedback", "ingest", str(report_path), "--db", str(database)]
    ) == 0
    ingested = json.loads(capsys.readouterr().out)
    feedback_id = ingested[0]["feedback_id"]
    assert ingested[0]["status"] == "proposed"

    assert main(
        [
            "feedback",
            "approve",
            feedback_id,
            "--db",
            str(database),
            "--reviewer",
            "expert",
        ]
    ) == 0
    approved = json.loads(capsys.readouterr().out)
    assert approved["status"] == "approved"
