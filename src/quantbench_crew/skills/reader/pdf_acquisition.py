"""PDF acquisition: resolve a paper's arXiv URL to a cached local file.

Caching under ``data/raw/`` keeps reruns deterministic and offline once a
PDF has been fetched. When no PDF can be obtained the skill reports
"skipped" and the reader continues on its metadata path — acquisition
failure must never block the dry workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quantbench_crew.artifacts import sha256_file
from quantbench_crew.models import Paper
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.tools.arxiv_tool import DEFAULT_PDF_CACHE_DIR, cache_pdf


class PdfAcquisitionSkill:
    """Download and cache the paper PDF so PaperQA2 can engage."""

    name = "pdf_acquisition"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        paper: Paper = inputs["paper"]
        settings = skill_settings(ctx.config, "quant_reader", self.name)
        cache_dir = Path(settings.get("cache_dir", DEFAULT_PDF_CACHE_DIR))

        path = cache_pdf(paper, cache_dir=cache_dir)
        if path is None:
            result = SkillResult(
                skill=self.name,
                status="skipped",
                payload={"pdf_path": None},
                notes=(
                    "no PDF cached or downloadable (missing URL, offline, or "
                    "non-PDF response); reader continues on metadata",
                ),
            )
        else:
            result = SkillResult(
                skill=self.name,
                status="ok",
                payload={"pdf_path": str(path), "sha256": sha256_file(path)},
                notes=(f"PDF available at {path}",),
            )
        ctx.manifest.record_skill(result)
        return result


@register_skill("quant_reader", "pdf_acquisition")
def _make_pdf_acquisition_skill() -> PdfAcquisitionSkill:
    return PdfAcquisitionSkill()
