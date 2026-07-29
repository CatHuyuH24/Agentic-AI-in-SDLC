"""Lightweight evidence extraction for Week 2 prototype.

This module sits between the Temporal Retriever and the Forecast Model in the pipeline.
It receives temporally valid news items (where news_time < forecast_time) and processes
them to extract deterministic polarity signals. The extracted evidence is output as a list 
of per-news annotations, which are subsequently used by:
1. The Forecast Model, to compute a net sentiment score.
2. The Faithfulness Evaluator, to measure evidence support and perform counterfactual 
   perturbations (e.g., masking sentiment terms).

The extraction relies on a small, strict lexicon (15 positive and 15 negative terms) to 
ensure determinism and explainability in the prototype. Expanding this lexicon is a known 
future work item.
"""

from __future__ import annotations

import re
from typing import Any


# Define a strict, minimal lexicon for explainable and deterministic sentiment extraction.
# A small lexicon ensures we have predictable baseline behavior for the prototype.
POSITIVE_TERMS = (
    "surge", "beat", "strong", "growth", "rally", "profit", "launch", "upgrade",
    "expansion", "momentum", "record", "better", "increase", "gain", "outperform"
)

NEGATIVE_TERMS = (
    "weak", "miss", "drop", "decline", "slower", "lawsuit", "downgrade", "loss",
    "risk", "delay", "fall", "underperform", "pressure", "cut", "concern"
)

# Combine both lists to create a fast lookup set for membership testing during normalization.
_LEXICON_TERMS = set(POSITIVE_TERMS) | set(NEGATIVE_TERMS)


def _normalize_token(token: str) -> str | None:
    """Map a token to its canonical lexicon form when possible.
    
    This function handles simple plural and conjugation variations (e.g., 'runs' -> 'run', 
    'surges' -> 'surge') so that the 15-term lexicon has broader reach without needing 
    to explicitly list every word form.
    """
    candidate = token.strip().lower()
    if not candidate:
        return None

    # Exact match check first
    if candidate in _LEXICON_TERMS:
        return candidate

    # Handle standard English pluralization rules mapped to root words in the lexicon
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

    This function expects only `valid_news` items that have already passed the 
    strict temporal gate (i.e., news_time < forecast_time).
    """
    evidence: list[dict[str, Any]] = []

    # Process each temporally validated news item to extract polarity features
    for item in news_items:
        # Prioritize 'cleaned_text', fallback to 'text', then 'title' for extraction
        text = str(item.get("cleaned_text") or item.get("text") or item.get("title") or "")
        
        # Simple word tokenization, preserving intra-word apostrophes (e.g., "company's")
        tokens = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text.lower())

        positive_hits: list[str] = []
        negative_hits: list[str] = []
        
        # Scan through all tokens to find matches in our positive and negative lexicons
        for tok in tokens:
            normalized = _normalize_token(tok)
            if normalized is None:
                continue
            if normalized in POSITIVE_TERMS:
                positive_hits.append(normalized)
            elif normalized in NEGATIVE_TERMS:
                negative_hits.append(normalized)

        # Deduplicate hits via set() to prevent double-counting the same term 
        # appearing multiple times in a single article, avoiding skewed scores
        positive_hits = sorted(set(positive_hits))
        negative_hits = sorted(set(negative_hits))

        # Determine direction and base score based on presence and volume of hits
        if not positive_hits and not negative_hits:
            direction = "HOLD"
            score = 0.55
            rationale = "No strong lexicon signal detected"
        else:
            # Determine overall polarity direction via simple majority voting of unique hits
            if len(positive_hits) > len(negative_hits):
                direction = "UP"
            elif len(negative_hits) > len(positive_hits):
                direction = "DOWN"
            else:
                direction = "HOLD"

            # Confidence score calculation: 
            # - Base 0.55
            # - +0.08 per unique lexicon hit (rewards total evidence volume)
            # - +0.02 per hit differential (rewards polarity strength/consensus)
            score = 0.55 + 0.08 * max(len(positive_hits), len(negative_hits))
            score += 0.02 * abs(len(positive_hits) - len(negative_hits))
            
            # Cap the score at 0.95 to prevent overconfidence from such a tiny lexicon
            score = round(min(0.95, score), 2)
            
            rationale = "positive terms" if direction == "UP" else "negative terms" if direction == "DOWN" else "mixed terms"

        # Append the structured evidence annotation for downstream models
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
                "evidence_text": item.get("text", item.get("title", "")),
                "rationale": rationale,
            }
        )

    return evidence
