"""Agent interfaces for the QuantBench Crew workflow."""

from quantbench_crew.agents.bench import QuantBenchAgent
from quantbench_crew.agents.coder import QuantCoderAgent
from quantbench_crew.agents.reader import QuantReaderAgent
from quantbench_crew.agents.reviewer import QuantReviewerAgent
from quantbench_crew.agents.scout import QuantScoutAgent

__all__ = [
    "QuantBenchAgent",
    "QuantCoderAgent",
    "QuantReaderAgent",
    "QuantReviewerAgent",
    "QuantScoutAgent",
]
