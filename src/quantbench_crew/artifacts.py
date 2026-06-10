"""Run manifests, artifact store, and hashing helpers.

The manifest is the reproducibility claim for one paper run: it records every
skill invocation, LLM call, seed, and artifact hash. Recording *all* trials —
not just the winning candidate — is load-bearing: selection bias makes
backtest overfitting trivial when discarded experiments go uncounted
(Lopez de Prado, "Dangers of Backtest Overfitting"), so downstream
multiple-testing corrections need the full trial count from the manifest.

Determinism contract: rerunning the pipeline on identical inputs must produce
an identical ``content_hash``. The hash therefore excludes the volatile
fields (``run_id``, ``started_at``) and everything else must be serialized
canonically (sorted keys, no timestamps).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from quantbench_crew.skills.base import SkillResult

MANIFEST_FILENAME = "manifest.json"

# Excluded from content_hash: they differ across reruns by construction.
_VOLATILE_FIELDS = ("run_id", "started_at")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (set, frozenset)):
        return sorted(str(item) for item in value)
    raise TypeError(f"Not canonically serializable: {type(value)!r}")


def canonical_json(obj: Any) -> str:
    """Serialize deterministically: sorted keys, compact separators."""

    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), default=_json_default
    )


def stable_hash(obj: Any) -> str:
    """SHA-256 of the canonical JSON serialization of ``obj``."""

    return sha256_text(canonical_json(obj))


def new_run_id(paper_slug: str, now: datetime | None = None) -> str:
    """Timestamped, human-sortable run id; uniqueness from microseconds."""

    moment = now or datetime.now(timezone.utc)
    return f"{moment:%Y%m%dT%H%M%S%f}-{paper_slug[:40]}"


@dataclass
class RunManifest:
    """Reproducibility record for one paper run.

    Deliberately mutable: it accumulates results as the run progresses, then
    is serialized once to ``runs/<run_id>/manifest.json``.
    """

    run_id: str
    paper_slug: str
    started_at: datetime
    config_hash: str
    skill_results: list[SkillResult] = field(default_factory=list)
    llm_calls: list[dict[str, Any]] = field(default_factory=list)
    seeds: dict[str, int] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)  # rel path -> sha256

    def record_skill(self, result: SkillResult) -> None:
        self.skill_results.append(result)

    def record_llm_call(self, entry: dict[str, Any]) -> None:
        self.llm_calls.append(dict(entry))

    def record_seed(self, name: str, value: int) -> None:
        self.seeds[name] = int(value)

    def record_artifact(self, rel_path: str, digest: str) -> None:
        self.artifacts[rel_path] = digest

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "paper_slug": self.paper_slug,
            "started_at": self.started_at.isoformat(),
            "config_hash": self.config_hash,
            "seeds": dict(sorted(self.seeds.items())),
            "artifacts": dict(sorted(self.artifacts.items())),
            "skill_results": [asdict(result) for result in self.skill_results],
            "llm_calls": list(self.llm_calls),
        }

    def content_hash(self) -> str:
        """Hash of the run content, excluding volatile identity fields."""

        payload = self.to_dict()
        for volatile in _VOLATILE_FIELDS:
            payload.pop(volatile, None)
        return stable_hash(payload)

    def save(self, run_dir: Path) -> Path:
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = self.to_dict()
        payload["content_hash"] = self.content_hash()
        path = run_dir / MANIFEST_FILENAME
        path.write_text(
            json.dumps(payload, sort_keys=True, indent=2, default=_json_default) + "\n",
            encoding="utf-8",
        )
        return path


class ArtifactStore:
    """Writes run artifacts under the run directory, hashing each into the manifest."""

    def __init__(self, run_dir: Path, manifest: RunManifest) -> None:
        self.run_dir = run_dir
        self.manifest = manifest
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def _target(self, rel_path: str) -> Path:
        pure = PurePosixPath(rel_path)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"Artifact path must stay inside the run directory: {rel_path}")
        target = self.run_dir / pure
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_text(self, rel_path: str, text: str) -> Path:
        target = self._target(rel_path)
        target.write_text(text, encoding="utf-8")
        self.manifest.record_artifact(rel_path, sha256_text(text))
        return target

    def write_json(self, rel_path: str, obj: Any) -> Path:
        text = json.dumps(obj, sort_keys=True, indent=2, default=_json_default) + "\n"
        return self.write_text(rel_path, text)


def start_run(
    runs_root: Path,
    paper_slug: str,
    config: dict[str, Any],
    run_id: str | None = None,
    started_at: datetime | None = None,
) -> tuple[RunManifest, ArtifactStore]:
    """Create the manifest and artifact store for one paper run."""

    moment = started_at or datetime.now(timezone.utc)
    manifest = RunManifest(
        run_id=run_id or new_run_id(paper_slug, moment),
        paper_slug=paper_slug,
        started_at=moment,
        config_hash=stable_hash(config),
    )
    store = ArtifactStore(runs_root / manifest.run_id, manifest)
    return manifest, store
