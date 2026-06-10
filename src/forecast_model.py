"""Simple rule-based forecast model for Week 2 prototype."""

from __future__ import annotations

from typing import Any

from evidence_extractor import extract_evidence


def forecast_from_news(news_items: list[dict[str, Any]], price_features: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic direction and confidence for the provided evidence set.

    The model uses the Week 2 evidence extractor and simple historical price cues
    from the existing schema so it remains explainable and runnable without any
    external model dependencies.
    """
    evidence = extract_evidence(news_items)

    up_score = sum(item["score"] for item in evidence if item["direction"] == "UP")
    down_score = sum(item["score"] for item in evidence if item["direction"] == "DOWN")
    hold_score = sum(item["score"] for item in evidence if item["direction"] == "HOLD")

    price_return = float(price_features.get("price_5d_return", 0.0) or 0.0)
    volume_change = float(price_features.get("volume_change_pct", 0.0) or 0.0)

    if up_score > down_score and up_score >= hold_score:
        prediction = "UP"
        signal_strength = up_score - down_score
        confidence = 0.55 + min(0.30, signal_strength * 0.25)
        if price_return > 0:
            confidence += 0.05
        if volume_change > 0:
            confidence += 0.03
    elif down_score > up_score and down_score >= hold_score:
        prediction = "DOWN"
        signal_strength = down_score - up_score
        confidence = 0.55 + min(0.30, signal_strength * 0.25)
        if price_return < 0:
            confidence += 0.05
        if volume_change < 0:
            confidence += 0.03
    else:
        prediction = "HOLD"
        confidence = 0.50 + min(0.15, (up_score + down_score) * 0.10)

    confidence = round(min(0.95, max(0.50, confidence)), 2)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "evidence_count": len(evidence),
        "evidence": evidence,
    }
