"""Compare paper claims with reproduced results and diagnose evidence gaps."""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.models import (
    BenchmarkResult,
    Claim,
    ClaimResultFinding,
    ClaimsVsResultsAnalysis,
    EvidenceLink,
    ImplementationPlan,
    PaperAnalysis,
)
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult


class ClaimsVsResultsAnalyzerSkill:
    """Produce a conservative, evidence-linked claim comparison ledger."""

    name = "claims_vs_results_analyzer"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        plan: ImplementationPlan = inputs["implementation_plan"]
        benchmark: BenchmarkResult = inputs["benchmark_result"]

        findings = _claim_findings(analysis, benchmark)
        implementation_issues = _implementation_issues(analysis, plan, benchmark)
        reproducibility_issues = _reproducibility_issues(analysis, benchmark, findings)
        counts = {
            "reproduced": sum(item.status == "reproduced" for item in findings),
            "failed": sum(item.status == "not_reproduced" for item in findings),
            "unevaluated": sum(item.status == "not_evaluated" for item in findings),
        }
        evidence = _analysis_evidence(findings, benchmark)
        payload = {
            "findings": [_finding_dict(item) for item in findings],
            "implementation_issues": list(implementation_issues),
            "reproducibility_issues": list(reproducibility_issues),
            "reproduced_count": counts["reproduced"],
            "failed_count": counts["failed"],
            "unevaluated_count": counts["unevaluated"],
            "evidence": [_evidence_dict(link) for link in evidence],
        }
        artifact = "review/claims_vs_results.json"
        ArtifactStore(ctx.run_dir, ctx.manifest).write_json(artifact, payload)
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload=payload,
            artifacts=(artifact,),
            notes=(
                f"{counts['reproduced']} reproduced, {counts['failed']} failed, "
                f"{counts['unevaluated']} not evaluated",
                "A failed reproduction diagnoses a gap; it does not by itself falsify the paper.",
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def claims_analysis_from_payload(payload: dict[str, Any]) -> ClaimsVsResultsAnalysis:
    """Build a typed claims analysis from a JSON-shaped skill payload."""

    return ClaimsVsResultsAnalysis(
        findings=tuple(_finding_from_dict(item) for item in payload.get("findings", [])),
        implementation_issues=tuple(
            str(item) for item in payload.get("implementation_issues", [])
        ),
        reproducibility_issues=tuple(
            str(item) for item in payload.get("reproducibility_issues", [])
        ),
        reproduced_count=int(payload.get("reproduced_count", 0)),
        failed_count=int(payload.get("failed_count", 0)),
        unevaluated_count=int(payload.get("unevaluated_count", 0)),
        evidence=tuple(_evidence_from_dict(item) for item in payload.get("evidence", [])),
    )


def _claim_findings(
    analysis: PaperAnalysis, benchmark: BenchmarkResult
) -> tuple[ClaimResultFinding, ...]:
    findings: list[ClaimResultFinding] = []
    seen: set[tuple[str, float, str]] = set()

    for comparison in benchmark.comparisons:
        claim = comparison.claim
        seen.add(_claim_key(claim))
        status = "reproduced" if comparison.within_tolerance else "not_reproduced"
        findings.append(
            ClaimResultFinding(
                metric=claim.metric,
                claimed_value=claim.value,
                achieved_value=comparison.achieved,
                tolerance=claim.tolerance,
                status=status,
                gap=comparison.achieved - claim.value,
                note=comparison.note or _comparison_note(status),
                evidence=_claim_evidence(claim, include_benchmark=True),
            )
        )

    target = analysis.reproduction_target
    for claim in target.claims if target is not None else ():
        if _claim_key(claim) in seen:
            continue
        findings.append(
            ClaimResultFinding(
                metric=claim.metric,
                claimed_value=claim.value,
                achieved_value=None,
                tolerance=claim.tolerance,
                status="not_evaluated",
                note="The paper claim was extracted, but Bench produced no comparable metric.",
                evidence=_claim_evidence(claim, include_benchmark=False),
            )
        )
    return tuple(findings)


def _implementation_issues(
    analysis: PaperAnalysis, plan: ImplementationPlan, benchmark: BenchmarkResult
) -> tuple[str, ...]:
    issues: list[str] = []
    if analysis.method_spec is None:
        issues.append("No implementable method specification was extracted.")
    elif analysis.method_spec.extraction_confidence < 0.5:
        issues.append(
            "The method specification has low extraction confidence "
            f"({analysis.method_spec.extraction_confidence:.2f})."
        )
    issues.extend(f"Implementation open question: {item}" for item in plan.open_questions)
    if not analysis.datasets:
        issues.append("The paper analysis names no dataset.")
    if not analysis.metrics:
        issues.append("The paper analysis names no evaluation metric.")
    evaluation = benchmark.strategy_evaluation
    if evaluation is not None:
        issues.extend(
            f"Experiment {item.name!r} contradicted its declared expectation."
            for item in evaluation.experiments
            if not item.passed
        )
    return _dedupe(issues)


def _reproducibility_issues(
    analysis: PaperAnalysis,
    benchmark: BenchmarkResult,
    findings: tuple[ClaimResultFinding, ...],
) -> tuple[str, ...]:
    issues: list[str] = []
    if analysis.reproduction_target is None:
        issues.append("No quantitative reproduction target was extracted.")
    issues.extend(
        f"Claim {item.metric!r} was not evaluated."
        for item in findings
        if item.status == "not_evaluated"
    )
    audit = benchmark.robustness_audit
    if audit is None:
        issues.append("No auditable robustness ledger is attached.")
    else:
        issues.extend(f"Robustness check failed: {item}." for item in audit.failed_checks)
        issues.extend(
            f"Robustness check unavailable: {item}." for item in audit.unavailable_checks
        )
    issues.extend(f"Reported limitation: {item}" for item in analysis.limitations)
    if analysis.critique is not None:
        issues.extend(
            f"Author-stated limitation: {item}"
            for item in analysis.critique.author_stated_limitations
        )
        issues.extend(
            f"Reader-inferred validity threat: {item}"
            for item in analysis.critique.reader_inferred_threats
        )
        issues.extend(
            f"Unanswered reproducibility question: {item}"
            for item in analysis.critique.unanswered_questions
        )
    issues.extend(
        f"Red flag [{flag.severity}] {flag.kind}: {flag.rationale}"
        for flag in analysis.red_flags
    )
    return _dedupe(issues)


def _claim_key(claim: Claim) -> tuple[str, float, str]:
    return claim.metric, claim.value, claim.context


def _claim_evidence(claim: Claim, *, include_benchmark: bool) -> tuple[EvidenceLink, ...]:
    links: list[EvidenceLink] = []
    if claim.source:
        links.append(
            EvidenceLink(
                kind="paper_quote",
                reference=claim.source,
                detail=f"claimed {claim.metric}={claim.value:g}",
            )
        )
    if include_benchmark:
        links.append(
            EvidenceLink(
                kind="metric",
                reference="benchmark/walk_forward.json",
                detail=f"comparison for {claim.metric}",
            )
        )
    return tuple(links)


def _comparison_note(status: str) -> str:
    return (
        "Achieved value is within the paper claim's declared tolerance."
        if status == "reproduced"
        else "Achieved value is outside the paper claim's declared tolerance."
    )


def _analysis_evidence(
    findings: tuple[ClaimResultFinding, ...], benchmark: BenchmarkResult
) -> tuple[EvidenceLink, ...]:
    links = [link for finding in findings for link in finding.evidence]
    if benchmark.strategy_evaluation is not None:
        links.append(
            EvidenceLink(
                kind="artifact",
                reference="benchmark/strategy_evaluation.json",
                detail="declared multi-dataset expectations",
            )
        )
    if benchmark.robustness_audit is not None:
        links.append(
            EvidenceLink(
                kind="artifact",
                reference="benchmark/robustness_audit.json",
                detail="failed, passed, and unavailable robustness checks",
            )
        )
    return _dedupe_links(links)


def _finding_dict(finding: ClaimResultFinding) -> dict[str, Any]:
    return {
        "metric": finding.metric,
        "claimed_value": finding.claimed_value,
        "achieved_value": finding.achieved_value,
        "tolerance": finding.tolerance,
        "status": finding.status,
        "gap": finding.gap,
        "note": finding.note,
        "evidence": [_evidence_dict(link) for link in finding.evidence],
    }


def _finding_from_dict(data: dict[str, Any]) -> ClaimResultFinding:
    return ClaimResultFinding(
        metric=str(data.get("metric", "")),
        claimed_value=_optional_float(data.get("claimed_value")),
        achieved_value=_optional_float(data.get("achieved_value")),
        tolerance=_optional_float(data.get("tolerance")),
        status=str(data.get("status", "not_evaluated")),
        gap=_optional_float(data.get("gap")),
        note=str(data.get("note", "")),
        evidence=tuple(_evidence_from_dict(item) for item in data.get("evidence", [])),
    )


def _evidence_dict(link: EvidenceLink) -> dict[str, str]:
    return {"kind": link.kind, "reference": link.reference, "detail": link.detail}


def _evidence_from_dict(data: dict[str, Any]) -> EvidenceLink:
    return EvidenceLink(
        kind=str(data.get("kind", "")),
        reference=str(data.get("reference", "")),
        detail=str(data.get("detail", "")),
    )


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in items if item))


def _dedupe_links(links: Any) -> tuple[EvidenceLink, ...]:
    return tuple(
        {
            (link.kind, link.reference, link.detail): link
            for link in links
        }.values()
    )


@register_skill("quant_reviewer", "claims_vs_results_analyzer")
def _make_claims_vs_results_analyzer_skill() -> ClaimsVsResultsAnalyzerSkill:
    return ClaimsVsResultsAnalyzerSkill()
