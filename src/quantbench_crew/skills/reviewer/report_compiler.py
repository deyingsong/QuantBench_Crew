"""Compile a final evidence-linked review through quantitative expert lenses."""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.models import (
    ClaimsVsResultsAnalysis,
    EvidenceLink,
    ReportCompilation,
    ReviewReport,
)
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult


class ReportCompilerSkill:
    """Assemble a comprehensive Markdown review without outrunning evidence."""

    name = "report_compiler"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        report: ReviewReport = inputs["report"]
        claims: ClaimsVsResultsAnalysis | None = inputs.get("claims_analysis")
        compilation = compile_report(report, claims)
        payload = _compilation_dict(compilation)
        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        markdown_artifact = "review/compiled_report.md"
        json_artifact = "review/report_compilation.json"
        store.write_text(markdown_artifact, compilation.markdown)
        store.write_json(json_artifact, payload)
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload=payload,
            artifacts=(markdown_artifact, json_artifact),
            notes=(
                f"compiled {len(compilation.empirical_findings)} empirical findings "
                f"through {len(compilation.expert_lens_findings)} expert lenses",
                "Expert lenses are diagnostic questions, not appeals to authority.",
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def compile_report(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None = None
) -> ReportCompilation:
    """Build the deterministic final report used by the Reviewer agent."""

    claims = claims or report.claims_analysis
    empirical = _empirical_findings(report, claims)
    expert_lenses = _expert_lens_findings(report, claims)
    strengths = _strengths(report, claims)
    weaknesses = _weaknesses(report, claims)
    open_questions = _open_questions(report, claims)
    evidence = _evidence(report, claims)
    executive_summary = _executive_summary(report, claims)
    markdown = _markdown(
        report,
        claims,
        executive_summary,
        empirical,
        expert_lenses,
        strengths,
        weaknesses,
        open_questions,
    )
    return ReportCompilation(
        executive_summary=executive_summary,
        empirical_findings=empirical,
        expert_lens_findings=expert_lenses,
        strengths=strengths,
        weaknesses=weaknesses,
        open_questions=open_questions,
        markdown=markdown,
        evidence=evidence,
    )


def report_compilation_from_payload(payload: dict[str, Any]) -> ReportCompilation:
    """Build a typed report compilation from a JSON-shaped skill payload."""

    return ReportCompilation(
        executive_summary=str(payload.get("executive_summary", "")),
        empirical_findings=tuple(
            str(item) for item in payload.get("empirical_findings", [])
        ),
        expert_lens_findings=tuple(
            str(item) for item in payload.get("expert_lens_findings", [])
        ),
        strengths=tuple(str(item) for item in payload.get("strengths", [])),
        weaknesses=tuple(str(item) for item in payload.get("weaknesses", [])),
        open_questions=tuple(str(item) for item in payload.get("open_questions", [])),
        markdown=str(payload.get("markdown", "")),
        evidence=tuple(
            EvidenceLink(
                kind=str(item.get("kind", "")),
                reference=str(item.get("reference", "")),
                detail=str(item.get("detail", "")),
            )
            for item in payload.get("evidence", [])
        ),
    )


def _executive_summary(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> str:
    claim_summary = (
        f"{claims.reproduced_count} reproduced, {claims.failed_count} failed, and "
        f"{claims.unevaluated_count} not evaluated"
        if claims is not None
        else "no claim-level forensic analysis was run"
    )
    return (
        f"Reviewer verdict: {report.verdict}. Claim comparison found {claim_summary}. "
        "Treat the verdict as a statement about this reproduction attempt and its "
        "recorded evidence, not as a universal judgment on the paper or an investment signal."
    )


def _empirical_findings(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[str, ...]:
    benchmark = report.benchmark_result
    findings = [
        f"Primary dataset {benchmark.dataset!r}: {name}={value:.4f}."
        for name, value in sorted(benchmark.metrics.items())
    ]
    findings.extend(
        f"Baseline {name!r}: "
        + ", ".join(f"{metric}={value:.4f}" for metric, value in sorted(metrics.items()))
        + "."
        for name, metrics in sorted(benchmark.baselines.items())
    )
    if claims is not None:
        findings.extend(
            f"Claim {item.metric!r}: status={item.status}, "
            f"claimed={_number(item.claimed_value)}, achieved={_number(item.achieved_value)}, "
            f"gap={_number(item.gap)}."
            for item in claims.findings
        )
    evaluation = benchmark.strategy_evaluation
    if evaluation is not None:
        findings.append(
            f"Multi-dataset evaluation passed {sum(item.passed for item in evaluation.experiments)}"
            f"/{len(evaluation.experiments)} declared expectations."
        )
    audit = benchmark.robustness_audit
    if audit is not None:
        findings.append(
            f"Robustness audit: robust={audit.robust}; {len(audit.passed_checks)} passed, "
            f"{len(audit.failed_checks)} failed, {len(audit.unavailable_checks)} unavailable."
        )
    return tuple(findings) or ("No empirical findings were available.",)


def _expert_lens_findings(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[str, ...]:
    benchmark = report.benchmark_result
    lenses: list[str] = []
    if benchmark.deflated_sharpe is not None:
        item = benchmark.deflated_sharpe
        lenses.append(
            "Trial honesty (Lopez de Prado / Niederhoffer): "
            f"observed Sharpe {item.observed_sharpe:.2f} deflates to "
            f"{item.deflated_sharpe:.2f} over {item.n_trials} disclosed trials "
            f"(p={item.p_value:.3f})."
        )
    else:
        lenses.append(
            "Trial honesty (Lopez de Prado / Niederhoffer): no deflated-Sharpe "
            "evidence is attached, so selection-bias risk remains unresolved."
        )
    if claims is not None:
        lenses.append(
            "Research process (Simons / Shaw / WorldQuant): "
            f"{claims.reproduced_count}/{len(claims.findings)} extracted claims reproduced; "
            f"{claims.unevaluated_count} remain outside the implemented test."
        )
    capacity = benchmark.capacity
    lenses.append(
        "Implementation reality (Chan / Jane Street): "
        + (
            f"estimated ADV participation is {capacity.adv_participation:.4f} with "
            f"average turnover {capacity.average_turnover:.4f}."
            if capacity is not None
            else "capacity, market impact, and execution evidence are incomplete."
        )
    )
    lenses.append(
        "Simple alternatives and portfolio role (Bogle / Markowitz / Sharpe / Asness): "
        f"the candidate was compared with {len(benchmark.baselines)} recorded baseline(s)"
        + (
            f"; factor-spanning residual Sharpe is {benchmark.spanning.residual_sharpe:.2f}."
            if benchmark.spanning is not None
            else "; no factor-spanning result is attached."
        )
    )
    audit = benchmark.robustness_audit
    lenses.append(
        "Regime, downside, and survival (Dalio / Druckenmiller / Tudor Jones / Thorp): "
        + (
            f"the audit records {len(audit.failed_checks)} failed and "
            f"{len(audit.unavailable_checks)} unavailable robustness checks."
            if audit is not None
            else "there is no auditable stress-test ledger, so survival across adverse "
            "conditions is unknown."
        )
    )
    lenses.append(
        "Incentives and controls (institutional model-risk lens): "
        + (
            f"the experiment ledger records {audit.recorded_experiments} experiments and "
            f"{audit.disclosed_local_trials} local trials with configuration hash "
            f"{audit.configuration_hash[:12]}."
            if audit is not None
            else "controls, experiment provenance, and trial disclosure are incomplete; "
            "a polished narrative cannot substitute for auditability."
        )
    )
    lenses.append(
        "Variant perception and falsification (Ackman / Loeb / Icahn / Robertson): "
        + (
            f"the decisive unresolved question is: {report.open_questions[0]}"
            if report.open_questions
            else "state the observation that would invalidate the claimed edge before "
            "treating it as actionable."
        )
    )
    return tuple(lenses)


def _strengths(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[str, ...]:
    strengths = list(report.strengths)
    if claims is not None and claims.reproduced_count:
        strengths.append(
            f"{claims.reproduced_count} paper claim(s) reproduced within declared tolerance."
        )
    evaluation = report.benchmark_result.strategy_evaluation
    if evaluation is not None and evaluation.passed_all:
        strengths.append("All declared multi-dataset expectations passed.")
    audit = report.benchmark_result.robustness_audit
    if audit is not None and audit.robust:
        strengths.append("The recorded robustness audit passed with no unavailable checks.")
    return _dedupe(strengths)


def _weaknesses(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[str, ...]:
    weaknesses = list(report.weaknesses)
    if claims is not None:
        if claims.failed_count:
            weaknesses.append(
                f"{claims.failed_count} paper claim(s) were outside declared tolerance."
            )
        if claims.unevaluated_count:
            weaknesses.append(
                f"{claims.unevaluated_count} paper claim(s) were not evaluated."
            )
        weaknesses.extend(claims.implementation_issues)
        weaknesses.extend(claims.reproducibility_issues)
    return _dedupe(weaknesses)


def _open_questions(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[str, ...]:
    questions = list(report.open_questions)
    if claims is not None:
        questions.extend(
            f"What evidence or implementation change would resolve: {item}"
            for item in (*claims.implementation_issues, *claims.reproducibility_issues)
        )
    return _dedupe(questions)


def _evidence(
    report: ReviewReport, claims: ClaimsVsResultsAnalysis | None
) -> tuple[EvidenceLink, ...]:
    links = [link for score in report.rubric for link in score.evidence]
    if claims is not None:
        links.extend(claims.evidence)
    return tuple(
        {
            (link.kind, link.reference, link.detail): link
            for link in links
        }.values()
    )


def _markdown(
    report: ReviewReport,
    claims: ClaimsVsResultsAnalysis | None,
    executive_summary: str,
    empirical: tuple[str, ...],
    expert_lenses: tuple[str, ...],
    strengths: tuple[str, ...],
    weaknesses: tuple[str, ...],
    open_questions: tuple[str, ...],
) -> str:
    sections = [
        f"# {report.paper.title}",
        "",
        f"**Source:** {report.paper.source}",
        _paper_link_line(report),
        f"**Verdict:** {report.verdict}",
        "",
        "## Decision Summary",
        executive_summary,
        "",
        "## Paper Thesis And Claimed Contribution",
        _paper_thesis(report),
        "",
        "## Claims Versus Reproduced Results",
        _claims_table(claims),
        "",
        "## Empirical Findings",
        _bullets(empirical),
        "",
        "## Implementation And Reproducibility Issues",
        _bullets(
            ()
            if claims is None
            else (*claims.implementation_issues, *claims.reproducibility_issues)
        ),
        "",
        "## Robustness And Risk",
        _robustness_summary(report),
        "",
        "## Portfolio And Economic Interpretation",
        _portfolio_summary(report),
        "",
        "## Expert Lens Review",
        _bullets(expert_lenses),
        "",
        "## Rubric",
        _rubric_table(report),
        "",
        "## Strengths",
        _bullets(strengths),
        "",
        "## Weaknesses",
        _bullets(weaknesses),
        "",
        "## Open Questions And Decisive Next Tests",
        _bullets(open_questions),
        "",
        "## Verdict And Scope",
        f"The evidence recorded in this run supports a **{report.verdict}** verdict.",
        "",
        "This report supports research review only and is not financial advice.",
        "",
    ]
    return "\n".join(sections)


def _paper_link_line(report: ReviewReport) -> str:
    url = report.paper.url or str(report.paper.raw.get("pdf_url") or "").strip()
    if not url:
        return "**Paper:** Not available from source metadata"
    return f"**Paper:** [Original paper]({url})"


def _paper_thesis(report: ReviewReport) -> str:
    assessment = report.analysis.question_assessment
    contribution = (
        "\n".join(f"- {item}" for item in assessment.claimed_contribution)
        if assessment is not None and assessment.claimed_contribution
        else "- No distinct claimed contribution was extracted."
    )
    return "\n".join(
        [
            f"**Research question:** {report.analysis.research_question}",
            "",
            f"**Proposed method:** {report.analysis.proposed_method}",
            "",
            "**Claimed contribution:**",
            contribution,
        ]
    )


def _claims_table(claims: ClaimsVsResultsAnalysis | None) -> str:
    if claims is None or not claims.findings:
        return "No claim-level comparison was available."
    rows = [
        "| Metric | Claimed | Achieved | Gap | Tolerance | Status | Evidence |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in claims.findings:
        references = "; ".join(link.reference for link in item.evidence) or "none"
        rows.append(
            f"| {_cell(item.metric)} | {_number(item.claimed_value)} | "
            f"{_number(item.achieved_value)} | {_number(item.gap)} | "
            f"{_number(item.tolerance)} | {item.status} | {_cell(references)} |"
        )
    return "\n".join(rows)


def _robustness_summary(report: ReviewReport) -> str:
    audit = report.benchmark_result.robustness_audit
    if audit is not None:
        return "\n".join(
            [
                f"- **Audit verdict:** {'pass' if audit.robust else 'fail'}",
                f"- **Passed checks:** {', '.join(audit.passed_checks) or 'none'}",
                f"- **Failed checks:** {', '.join(audit.failed_checks) or 'none'}",
                f"- **Unavailable checks:** {', '.join(audit.unavailable_checks) or 'none'}",
                f"- **Recorded experiments:** {audit.recorded_experiments}",
                f"- **Disclosed local trials:** {audit.disclosed_local_trials}",
            ]
        )
    if report.robustness is not None:
        return (
            f"- Subsample sign-stable: {report.robustness.sign_stable}\n"
            f"- Subsample Sharpes: {report.robustness.subsample_sharpes}\n"
            f"- Parameter sensitivity: {report.robustness.parameter_sensitivity}"
        )
    return "No robustness evidence was attached."


def _portfolio_summary(report: ReviewReport) -> str:
    benchmark = report.benchmark_result
    lines = [f"- Recorded baselines: {', '.join(sorted(benchmark.baselines)) or 'none'}"]
    if benchmark.spanning is not None:
        lines.extend(
            [
                f"- Factor-spanning alpha: {benchmark.spanning.alpha:.4f}",
                f"- Factor-spanning alpha t-stat: {benchmark.spanning.alpha_tstat:.2f}",
                f"- Residual Sharpe: {benchmark.spanning.residual_sharpe:.2f}",
            ]
        )
    else:
        lines.append("- Factor-spanning evidence: unavailable")
    if benchmark.capacity is not None:
        lines.extend(
            [
                f"- Average turnover: {benchmark.capacity.average_turnover:.4f}",
                f"- ADV participation: {benchmark.capacity.adv_participation:.4f}",
                f"- Capacity estimate: {_number(benchmark.capacity.capacity_usd)}",
            ]
        )
    else:
        lines.append("- Capacity and market-impact evidence: unavailable")
    return "\n".join(lines)


def _rubric_table(report: ReviewReport) -> str:
    if not report.rubric:
        return "No rubric was scored."
    rows = [
        "| Dimension | Score | Rationale | Evidence |",
        "| --- | ---: | --- | --- |",
    ]
    for score in report.rubric:
        references = "; ".join(link.reference for link in score.evidence) or "none"
        rows.append(
            f"| {_cell(score.dimension)} | {score.score}/4 | "
            f"{_cell(score.rationale)} | {_cell(references)} |"
        )
    return "\n".join(rows)


def _compilation_dict(compilation: ReportCompilation) -> dict[str, Any]:
    return {
        "executive_summary": compilation.executive_summary,
        "empirical_findings": list(compilation.empirical_findings),
        "expert_lens_findings": list(compilation.expert_lens_findings),
        "strengths": list(compilation.strengths),
        "weaknesses": list(compilation.weaknesses),
        "open_questions": list(compilation.open_questions),
        "markdown": compilation.markdown,
        "evidence": [
            {"kind": link.kind, "reference": link.reference, "detail": link.detail}
            for link in compilation.evidence
        ],
    }


def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None identified."


def _number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in items if item))


@register_skill("quant_reviewer", "report_compiler")
def _make_report_compiler_skill() -> ReportCompilerSkill:
    return ReportCompilerSkill()
