#!/usr/bin/env python3
"""Score local paper metadata with Scout's deterministic relevance rubric."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quantbench_crew.agents.scout import QuantScoutAgent  # noqa: E402
from quantbench_crew.config import load_config  # noqa: E402
from quantbench_crew.skills.scout.charter_relevance import load_charter  # noqa: E402
from quantbench_crew.skills.scout.relevance_scorer import RelevanceScorerSkill  # noqa: E402
from quantbench_crew.tools.arxiv_tool import load_local_papers  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-json", required=True)
    parser.add_argument("--agents-config", default=str(ROOT / "configs/agents.yaml"))
    parser.add_argument("--max-papers", type=int, default=50)
    args = parser.parse_args()

    config = load_config(args.agents_config)
    scout = QuantScoutAgent(
        keywords=(),
        skills={"relevance_scorer": RelevanceScorerSkill()},
        charter=load_charter(config),
        relevance_boost=1.0,
    )
    ranked = scout.rank(load_local_papers(args.paper_json), max_papers=args.max_papers)
    output = [
        {
            "rank": index,
            "title": scored.paper.title,
            "score": scored.score,
            "reasons": list(scored.reasons),
            "assessment": asdict(scored.relevance) if scored.relevance else None,
        }
        for index, scored in enumerate(ranked, start=1)
    ]
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
