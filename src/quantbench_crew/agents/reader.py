"""QuantReader agent backed by PaperQA2 when document files are available."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from quantbench_crew.models import Paper, PaperAnalysis
from quantbench_crew.tools.paper_parser import keyword_extract, sentence_summary


class PaperQAReaderClient(Protocol):
    """Interface for PaperQA2-powered document analysis."""

    def analyze(self, paper: Paper) -> str | None:
        """Return a structured answer for a paper, or None if unavailable."""


class PaperQA2Client:
    """Small adapter around PaperQA2's Docs API."""

    def __init__(self, settings: Any | None = None) -> None:
        try:
            from paperqa import Docs, Settings
        except ImportError as exc:
            raise RuntimeError("PaperQA2 is not installed. Install with `pip install paper-qa>=5`.") from exc

        self._docs_cls = Docs
        self._settings = settings if settings is not None else Settings(temperature=0)

    @classmethod
    def create_if_available(cls) -> "PaperQA2Client | None":
        try:
            return cls()
        except RuntimeError:
            return None

    def analyze(self, paper: Paper) -> str | None:
        paths = document_paths_for_paper(paper)
        if not paths:
            return None

        docs = self._docs_cls()
        for path in paths:
            docs.add(str(path))

        session = docs.query(_paperqa_question(paper), settings=self._settings)
        return _answer_text(session)


class QuantReaderAgent:
    """Extract structured method notes from a paper record using PaperQA2."""

    def __init__(
        self,
        paperqa_client: PaperQAReaderClient | None = None,
        use_paperqa: bool = True,
    ) -> None:
        self.paperqa_client = paperqa_client
        if self.paperqa_client is None and use_paperqa:
            self.paperqa_client = PaperQA2Client.create_if_available()

    def analyze(self, paper: Paper) -> PaperAnalysis:
        paperqa_answer = (
            self.paperqa_client.analyze(paper) if self.paperqa_client is not None else None
        )
        if paperqa_answer:
            return _analysis_from_paperqa_answer(paper, paperqa_answer)

        return _metadata_analysis(paper)


def document_paths_for_paper(paper: Paper) -> tuple[Path, ...]:
    """Return local document paths that PaperQA2 can index for this paper."""

    path_keys = (
        "path",
        "file",
        "file_path",
        "paper_path",
        "pdf_path",
        "document_path",
        "document_paths",
    )
    values: list[object] = []
    for key in path_keys:
        if key in paper.raw:
            values.append(paper.raw[key])

    if paper.url and paper.url.startswith("file://"):
        values.append(paper.url.removeprefix("file://"))

    paths: list[Path] = []
    for value in values:
        for item in _as_sequence(value):
            path = Path(str(item)).expanduser()
            if path.exists() and path.is_file():
                paths.append(path)
    return tuple(dict.fromkeys(paths))


def _paperqa_question(paper: Paper) -> str:
    return (
        "Analyze this quantitative finance research paper for a reproducible "
        "benchmarking workflow. Return concise JSON with these keys: "
        "research_question, proposed_method, assumptions, datasets, metrics, "
        "limitations. The assumptions, datasets, metrics, and limitations values "
        "must be arrays of short strings. Use citations in values when helpful. "
        f"Paper title: {paper.title}"
    )


def _analysis_from_paperqa_answer(paper: Paper, answer: str) -> PaperAnalysis:
    payload = _extract_json_object(answer)
    if not payload:
        fallback = _metadata_analysis(paper)
        return PaperAnalysis(
            paper=paper,
            research_question=sentence_summary(answer, fallback.research_question),
            proposed_method=sentence_summary(answer, fallback.proposed_method),
            assumptions=fallback.assumptions,
            datasets=fallback.datasets,
            metrics=fallback.metrics,
            limitations=(
                "PaperQA2 answer was not valid JSON; metadata extraction filled structured fields.",
                *fallback.limitations,
            ),
        )

    fallback = _metadata_analysis(paper)
    return PaperAnalysis(
        paper=paper,
        research_question=_string_value(payload.get("research_question"), fallback.research_question),
        proposed_method=_string_value(payload.get("proposed_method"), fallback.proposed_method),
        assumptions=_string_tuple(payload.get("assumptions")) or fallback.assumptions,
        datasets=_string_tuple(payload.get("datasets")) or fallback.datasets,
        metrics=_string_tuple(payload.get("metrics")) or fallback.metrics,
        limitations=_string_tuple(payload.get("limitations"))
        or ("PaperQA2 extraction did not identify limitations.",),
    )


def _metadata_analysis(paper: Paper) -> PaperAnalysis:
    text = f"{paper.title}. {paper.abstract}"
    datasets = keyword_extract(
        text,
        candidates=("crsp", "compustat", "wrds", "optionmetrics", "intraday", "returns"),
    )
    metrics = keyword_extract(
        text,
        candidates=("sharpe", "accuracy", "rmse", "drawdown", "turnover", "return"),
    )
    assumptions = keyword_extract(
        text,
        candidates=("stationary", "linear", "transaction costs", "liquidity", "no arbitrage"),
    )

    return PaperAnalysis(
        paper=paper,
        research_question=sentence_summary(
            paper.abstract,
            fallback="Identify whether the paper proposes a testable quantitative finance method.",
        ),
        proposed_method=_method_hint(text),
        assumptions=assumptions or ("Requires human review of modeling assumptions.",),
        datasets=datasets or ("Dataset not identified from metadata.",),
        metrics=metrics or ("Evaluation metrics not identified from metadata.",),
        limitations=("Metadata-only extraction; PaperQA2 document analysis was not available.",),
    )


def _method_hint(text: str) -> str:
    lowered = text.lower()
    if "machine learning" in lowered or "neural" in lowered:
        return "Machine learning method requiring model specification and validation protocol review."
    if "portfolio" in lowered:
        return "Portfolio construction or allocation method requiring benchmark comparison."
    if "risk" in lowered:
        return "Risk modeling method requiring stress and robustness evaluation."
    if "forecast" in lowered or "predict" in lowered:
        return "Forecasting method requiring out-of-sample evaluation."
    return "Method details require full-text extraction before implementation."


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()

    candidates = [stripped]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and start < end:
        candidates.append(stripped[start : end + 1])

    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def _answer_text(session: Any) -> str:
    for attribute in ("formatted_answer", "answer"):
        value = getattr(session, attribute, None)
        if value:
            return str(value)
    return str(session)


def _string_value(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _as_sequence(value: object) -> tuple[object, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value,)
