import json
from pathlib import Path

from quantbench_crew.main import build_parser, track_new_papers


def test_track_local_papers_updates_ranked_queue(tmp_path: Path) -> None:
    papers_path = tmp_path / "papers.json"
    papers_path.write_text(
        json.dumps(
            [
                {
                    "title": "Useful momentum paper",
                    "abstract": (
                        "Out-of-sample momentum returns with public data, baseline, "
                        "robustness, turnover, and transaction costs."
                    ),
                    "online_date": "2026-06-02",
                },
                {
                    "title": "Old paper",
                    "abstract": "portfolio returns",
                    "online_date": "2026-05-01",
                },
                {"title": "Unknown date", "abstract": "portfolio returns"},
            ]
        )
    )
    queue_path = tmp_path / "queue.json"
    args = build_parser().parse_args(
        [
            "track",
            "--source",
            "local",
            "--paper-json",
            str(papers_path),
            "--start-date",
            "2026-05-31",
            "--end-date",
            "2026-06-10",
            "--queue-path",
            str(queue_path),
        ]
    )

    summary = track_new_papers(args)

    assert summary["in_window"] == 1
    assert summary["outside_window"] == 1
    assert summary["missing_exact_online_date"] == 1
    assert summary["source_failures"] == []
    assert summary["queue"]["added"] == 1
    assert queue_path.exists()
