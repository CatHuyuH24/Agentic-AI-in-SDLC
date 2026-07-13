"""Lightweight evidence extraction for Week 2 prototype."""

from __future__ import annotations

import re
from typing import Any


POSITIVE_TERMS = (
    "surge", "beat", "strong", "growth", "rally", "profit", "launch", "upgrade",
    "expansion", "momentum", "record", "better", "increase", "gain", "outperform"
)

NEGATIVE_TERMS = (
    "weak", "miss", "drop", "decline", "slower", "lawsuit", "downgrade", "loss",
    "risk", "delay", "fall", "underperform", "pressure", "cut", "concern"
)

_LEXICON_TERMS = set(POSITIVE_TERMS) | set(NEGATIVE_TERMS)


def _normalize_token(token: str) -> str | None:
    """Map a token to its canonical lexicon form when possible."""
    candidate = token.strip().lower()
    if not candidate:
        return None

    if candidate in _LEXICON_TERMS:
        return candidate

    if candidate.endswith("ies") and candidate[:-3] + "y" in _LEXICON_TERMS:
        return candidate[:-3] + "y"

    if candidate.endswith("es") and candidate[:-2] in _LEXICON_TERMS:
        return candidate[:-2]

    if candidate.endswith("s") and candidate[:-1] in _LEXICON_TERMS:
        return candidate[:-1]

    return None


def extract_evidence(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create simple evidence candidates from accepted news items.

    The extractor uses a deterministic lexicon over the cleaned text and/or title
    so that Week 2 modules can build on the verified Week 1 contract without
    introducing additional stochastic behavior.
    """
    evidence: list[dict[str, Any]] = []

    for item in news_items:
        text = str(item.get("cleaned_text") or item.get("text") or item.get("title") or "")
        tokens = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text.lower())

        positive_hits: list[str] = []
        negative_hits: list[str] = []
        for tok in tokens:
            normalized = _normalize_token(tok)
            if normalized is None:
                continue
            if normalized in POSITIVE_TERMS:
                positive_hits.append(normalized)
            elif normalized in NEGATIVE_TERMS:
                negative_hits.append(normalized)

        positive_hits = sorted(set(positive_hits))
        negative_hits = sorted(set(negative_hits))

        if not positive_hits and not negative_hits:
            direction = "HOLD"
            score = 0.55
            rationale = "No strong lexicon signal detected"
        else:
            if len(positive_hits) > len(negative_hits):
                direction = "UP"
            elif len(negative_hits) > len(positive_hits):
                direction = "DOWN"
            else:
                direction = "HOLD"

            score = 0.55 + 0.08 * max(len(positive_hits), len(negative_hits))
            score += 0.02 * abs(len(positive_hits) - len(negative_hits))
            score = round(min(0.95, score), 2)
            rationale = "positive terms" if direction == "UP" else "negative terms" if direction == "DOWN" else "mixed terms"

        evidence.append(
            {
                "news_id": item.get("news_id", "unknown"),
                "ticker": item.get("ticker") or item.get("symbol"),
                "title": item.get("title", ""),
                "direction": direction,
                "score": score,
                "evidence_terms": {
                    "positive": positive_hits,
                    "negative": negative_hits,
                },
                "rationale": rationale,
            }
        )

    return evidence
