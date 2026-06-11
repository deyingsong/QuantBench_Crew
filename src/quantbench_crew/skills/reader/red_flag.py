"""Quant-pitfalls red-flag scan.

Detects the recurring ways a backtest flatters itself: results quoted before
transaction costs, in-sample parameter tuning, survivorship-prone samples,
microcap-driven returns, samples too short to mean anything, and explicit
data-snooping language. Each detection emits a `RedFlag` with the quote that
triggered it, so the reviewer's red-team checklist (QB-28) is built on
evidence rather than vibes.

The checklist is seeded from the practitioner corpus in
`Source_data/transcript/` — chiefly Lopez de Prado, "Dangers of Backtest
Overfitting" and "Ten Financial Applications of Machine Learning" — which
catalog exactly these failure modes. Deterministic and offline; the scan
sharpens when full text is available (QB-19) but runs on the abstract alone.
"""

from __future__ import annotations

import re
from typing import Any

from quantbench_crew.models import EvidenceLink, PaperAnalysis, RedFlag
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult

_NO_COST = re.compile(
    r"before transaction costs|gross of (?:transaction )?costs|"
    r"ignoring transaction costs|no transaction costs|"
    r"without (?:accounting for )?transaction costs",
    re.IGNORECASE,
)
_COST_HANDLED = re.compile(
    r"net of (?:transaction )?costs|after transaction costs|"
    r"transaction costs (?:are )?(?:included|incorporated|accounted)",
    re.IGNORECASE,
)
_IN_SAMPLE = re.compile(
    r"in-sample|optimized parameters|optimal parameters|best-performing|"
    r"tuned to|we (?:choose|select|pick)[^.]{0,40}maximiz",
    re.IGNORECASE,
)
_SURVIVOR = re.compile(
    r"current(?:ly)?[^.]{0,25}(?:listed|constituents)|surviving firms|survivorship",
    re.IGNORECASE,
)
_SURVIVOR_OK = re.compile(r"survivorship[- ]bias[- ]free|delisting", re.IGNORECASE)
_MICROCAP = re.compile(
    r"micro-?cap|small-?cap|smallest decile|penny stocks|illiquid stocks",
    re.IGNORECASE,
)
_SNOOP = re.compile(
    r"we tried|various specifications|after experimentation|we experimented|"
    r"data[- ]mining|data[- ]snoop",
    re.IGNORECASE,
)
_YEAR_RANGE = re.compile(
    r"\b(19\d{2}|20\d{2})\s*(?:to|through|until|–|—|-)\s*(19\d{2}|20\d{2})\b"
)
SHORT_SAMPLE_YEARS = 5


class RedFlagScanSkill:
    """Scan a paper for quant-research pitfalls and emit RedFlag records."""

    name = "red_flag_scan"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        text = inputs.get("full_text") or analysis.paper.abstract
        flags = scan_red_flags(text)

        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={"red_flags": [_flag_dict(flag) for flag in flags]},
            notes=(
                f"{len(flags)} red flag(s): "
                + (", ".join(sorted(flag.kind for flag in flags)) or "none"),
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def scan_red_flags(text: str) -> tuple[RedFlag, ...]:
    """Return all detected pitfalls in ``text`` (abstract or full text)."""

    flags: list[RedFlag] = []

    if _NO_COST.search(text) and not _COST_HANDLED.search(text):
        flags.append(_flag("no_transaction_costs", "warning",
                           "results quoted before/without transaction costs", _NO_COST, text))
    if _IN_SAMPLE.search(text):
        flags.append(_flag("in_sample_tuning", "warning",
                           "parameters appear tuned in-sample", _IN_SAMPLE, text))
    if _SURVIVOR.search(text) and not _SURVIVOR_OK.search(text):
        flags.append(_flag("survivorship_prone", "warning",
                           "sample may be survivorship-prone (no delisting handling mentioned)",
                           _SURVIVOR, text))
    if _MICROCAP.search(text):
        flags.append(_flag("microcap_driven", "warning",
                           "returns may be microcap/illiquidity driven", _MICROCAP, text))
    if _SNOOP.search(text):
        flags.append(_flag("data_snooping", "critical",
                           "language suggests data snooping / multiple specifications",
                           _SNOOP, text))

    span = _sample_span_years(text)
    if span is not None and span < SHORT_SAMPLE_YEARS:
        match = _YEAR_RANGE.search(text)
        flags.append(
            RedFlag(
                kind="short_sample",
                severity="warning",
                rationale=f"sample spans only {span} years (< {SHORT_SAMPLE_YEARS})",
                evidence=(EvidenceLink(kind="paper_quote", reference="abstract",
                                       detail=_snippet(text, match.start(), match.end()) if match else ""),),
            )
        )
    return tuple(flags)


def red_flags_from_payload(payload: dict[str, Any]) -> tuple[RedFlag, ...]:
    """Rebuild typed RedFlags from a skill payload."""

    return tuple(
        RedFlag(
            kind=item["kind"],
            severity=item["severity"],
            rationale=item["rationale"],
            evidence=tuple(
                EvidenceLink(kind=e["kind"], reference=e["reference"], detail=e.get("detail", ""))
                for e in item.get("evidence", [])
            ),
        )
        for item in payload.get("red_flags", [])
    )


def _flag(kind: str, severity: str, rationale: str, pattern: re.Pattern[str], text: str) -> RedFlag:
    match = pattern.search(text)
    detail = _snippet(text, match.start(), match.end()) if match else ""
    return RedFlag(
        kind=kind,
        severity=severity,
        rationale=rationale,
        evidence=(EvidenceLink(kind="paper_quote", reference="abstract", detail=detail),),
    )


def _sample_span_years(text: str) -> int | None:
    match = _YEAR_RANGE.search(text)
    if not match:
        return None
    return int(match.group(2)) - int(match.group(1))


def _snippet(text: str, start: int, end: int, radius: int = 60) -> str:
    return " ".join(text[max(0, start - radius): min(len(text), end + radius)].split())


def _flag_dict(flag: RedFlag) -> dict[str, Any]:
    return {
        "kind": flag.kind,
        "severity": flag.severity,
        "rationale": flag.rationale,
        "evidence": [
            {"kind": e.kind, "reference": e.reference, "detail": e.detail} for e in flag.evidence
        ],
    }


@register_skill("quant_reader", "red_flag_scan")
def _make_red_flag_skill() -> RedFlagScanSkill:
    return RedFlagScanSkill()
