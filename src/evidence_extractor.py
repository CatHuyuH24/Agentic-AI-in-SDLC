"""Lightweight evidence extraction for Week 2 prototype."""

from __future__ import annotations

from typing import Any


POSITIVE_TERMS = (
    "surge", "beat", "strong", "growth", "rally", "profit", "launch", "upgrade",
    "expansion", "momentum", "record", "better", "increase", "gain", "outperform"
)

NEGATIVE_TERMS = (
    "weak", "miss", "drop", "decline", "slower", "lawsuit", "downgrade", "loss",
    "risk", "delay", "fall", "underperform", "pressure", "cut", "concern"
)


def extract_evidence(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create simple evidence candidates from accepted news items.

    The extractor uses a deterministic lexicon over the cleaned text and/or title
    so that Week 2 modules can build on the verified Week 1 contract without
    introducing additional stochastic behavior.
    """
    evidence: list[dict[str, Any]] = []

    for item in news_items:
        text = str(item.get("cleaned_text") or item.get("text") or item.get("title") or "").lower()
        positive_hits = [term for term in POSITIVE_TERMS if term in text]
        negative_hits = [term for term in NEGATIVE_TERMS if term in text]

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
