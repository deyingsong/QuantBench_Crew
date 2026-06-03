from quantbench_crew.main import main


def test_pipeline_runs(capsys) -> None:
    exit_code = main(["run", "--source", "local", "--max-papers", "1"])

    capsys.readouterr()
    assert exit_code == 0
