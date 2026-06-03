"""Small text extraction helpers for initial paper metadata analysis."""

from __future__ import annotations

import re
from collections.abc import Iterable


def sentence_summary(text: str, fallback: str) -> str:
    """Return the first readable sentence from text."""

    cleaned = " ".join(text.split())
    if not cleaned:
        return fallback
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return sentences[0].strip() or fallback


def keyword_extract(text: str, candidates: Iterable[str]) -> tuple[str, ...]:
    """Extract candidate keywords that appear in text."""

    lowered = text.lower()
    return tuple(candidate for candidate in candidates if candidate.lower() in lowered)
