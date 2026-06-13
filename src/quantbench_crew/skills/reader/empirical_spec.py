"""Parse datasets, variables, splits, baselines, and evaluation metrics."""

from __future__ import annotations

from typing import Any

from quantbench_crew.models import EmpiricalSpecification, Paper, PaperAnalysis
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult
from quantbench_crew.skills.reader.structured_components import (
    EVIDENCE_SCHEMA,
    evidence_items,
    evidence_links,
    run_component_extraction,
    sentences_matching,
    source_text,
    string_tuple,
    substantive_strings,
)

PROMPT_NAME = "empirical_spec_parser"
SYSTEM_PROMPT = (
    "You parse research papers into exact empirical data and evaluation "
    "specifications. Answer with one JSON object and never invent missing design details."
)
EMPIRICAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "datasets",
        "features",
        "labels",
        "preprocessing",
        "splits",
        "baselines",
        "metrics",
        "confidence",
        "evidence",
    ],
    "properties": {
        "datasets": {"type": "array", "items": {"type": "string"}},
        "features": {"type": "array", "items": {"type": "string"}},
        "labels": {"type": "array", "items": {"type": "string"}},
        "preprocessing": {"type": "array", "items": {"type": "string"}},
        "splits": {"type": "array", "items": {"type": "string"}},
        "baselines": {"type": "array", "items": {"type": "string"}},
        "metrics": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
        "evidence": EVIDENCE_SCHEMA,
    },
}


class EmpiricalSpecParserSkill:
    """Extract the paper's empirical data-and-evaluation contract."""

    name = "empirical_spec_parser"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        return run_component_extraction(
            ctx,
            analysis=inputs["analysis"],
            full_text=str(inputs.get("full_text") or ""),
            skill_name=self.name,
            payload_key="empirical_spec",
            prompt_name=PROMPT_NAME,
            system_prompt=SYSTEM_PROMPT,
            schema=EMPIRICAL_SCHEMA,
            fallback=_fallback,
        )


def empirical_spec_from_payload(
    paper: Paper, payload: dict[str, Any]
) -> EmpiricalSpecification | None:
    """Build a typed empirical specification from the skill payload."""

    data = payload.get("empirical_spec")
    if not data:
        return None
    return EmpiricalSpecification(
        datasets=string_tuple(data.get("datasets")),
        features=string_tuple(data.get("features")),
        labels=string_tuple(data.get("labels")),
        preprocessing=string_tuple(data.get("preprocessing")),
        splits=string_tuple(data.get("splits")),
        baselines=string_tuple(data.get("baselines")),
        metrics=string_tuple(data.get("metrics")),
        confidence=float(data.get("confidence", 0.0)),
        evidence=evidence_links(data.get("evidence", [])),
    )


def _fallback(analysis: PaperAnalysis, full_text: str) -> dict[str, Any]:
    text = source_text(analysis, full_text)
    datasets = substantive_strings(analysis.datasets)
    metrics = substantive_strings(analysis.metrics)
    features = sentences_matching(
        text, ("feature", "predictor", "covariate", "input", "characteristic", "signal")
    )
    labels = sentences_matching(
        text, ("label", "target", "outcome", "predict", "forecast", "dependent variable")
    )
    preprocessing = sentences_matching(
        text, ("normalize", "standardize", "winsor", "impute", "preprocess", "filter")
    )
    splits = sentences_matching(
        text,
        (
            "out-of-sample",
            "out of sample",
            "train",
            "validation",
            "test set",
            "cross-validation",
            "walk-forward",
        ),
    )
    baselines = sentences_matching(text, ("baseline", "benchmark", "compared with", "versus"))
    evidence = []
    evidence.extend(
        evidence_items(
            "datasets", [item for item in datasets if item.casefold() in text.casefold()]
        )
    )
    evidence.extend(
        evidence_items(
            "metrics", [item for item in metrics if item.casefold() in text.casefold()]
        )
    )
    for field, values in (
        ("features", features),
        ("labels", labels),
        ("preprocessing", preprocessing),
        ("splits", splits),
        ("baselines", baselines),
    ):
        evidence.extend(evidence_items(field, values))
    return {
        "datasets": datasets,
        "features": features,
        "labels": labels,
        "preprocessing": preprocessing,
        "splits": splits,
        "baselines": baselines,
        "metrics": metrics,
        "confidence": 0.35 if full_text else 0.2,
        "evidence": evidence,
    }


@register_skill("quant_reader", "empirical_spec_parser")
def _make_empirical_spec_parser_skill() -> EmpiricalSpecParserSkill:
    return EmpiricalSpecParserSkill()
