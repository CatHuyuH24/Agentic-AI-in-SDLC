"""Faithfulness metric calculations for the Week 3 prototype.

Three core metrics are computed here:

1. Temporal Validity  — ratio of valid news items to total news items.
2. Evidence Support   — fraction of evidence items whose direction matches
                         the model prediction.
3. Confidence Drop    — reduction in model confidence after cited sentiment
                         keywords are masked with a neutral placeholder.

All functions are pure / deterministic so that they can be unit-tested
without mocking.  The confidence-drop path uses the same
``forecast_from_news`` function that Week 2 already provides; no new
model infrastructure is required.
"""

from __future__ import annotations

import copy
from typing import Any

from evidence_extractor import NEGATIVE_TERMS, POSITIVE_TERMS, extract_evidence
from forecast_model import forecast_from_news, run_forecast

# Placeholder token used when masking sentiment keywords.
_NEUTRAL_TOKEN = "note"


# ---------------------------------------------------------------------------
# Temporal Validity
# ---------------------------------------------------------------------------

def calculate_temporal_validity(valid_count: int, invalid_count: int) -> float:
    """Return the ratio of valid news items to total news items.

    A value of 1.0 means all news is pre-forecast (no leakage detected).
    A value of 0.0 means every item was future-dated.

    Args:
        valid_count:   Number of items in ``valid_news``.
        invalid_count: Number of items in ``invalid_future_news``.

    Returns:
        Float in [0.0, 1.0], or 1.0 when no news is present at all.
    """
    total = valid_count + invalid_count
    if total == 0:
        return 1.0
    return round(valid_count / total, 4)


# ---------------------------------------------------------------------------
# Evidence Support
# ---------------------------------------------------------------------------

def calculate_evidence_support(evidence: list[dict[str, Any]], prediction: str) -> float:
    """Return the fraction of evidence items that support the prediction.

    An evidence item *supports* the prediction when its ``direction`` field
    matches the predicted market direction (UP / DOWN / HOLD).

    Args:
        evidence:   List of evidence dicts produced by ``extract_evidence``.
        prediction: One of ``"UP"``, ``"DOWN"``, or ``"HOLD"``.

    Returns:
        Float in [0.0, 1.0], or 0.0 when the evidence list is empty.
    """
    if not evidence:
        return 0.0
    supporting = sum(1 for item in evidence if item.get("direction") == prediction)
    return round(supporting / len(evidence), 4)


# ---------------------------------------------------------------------------
# Confidence Drop  (counterfactual perturbation)
# ---------------------------------------------------------------------------

def _mask_sentiment_terms(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a deep-copied news list with all sentiment keywords replaced.

    Both ``text`` and ``cleaned_text`` fields are masked so that the
    evidence extractor and forecast model see only neutral language.
    The original list is never mutated.
    """
    perturbed = copy.deepcopy(news_items)
    all_terms = set(POSITIVE_TERMS) | set(NEGATIVE_TERMS)

    for item in perturbed:
        for field in ("text", "cleaned_text", "title"):
            raw = item.get(field)
            if not isinstance(raw, str):
                continue
            tokens = raw.split()
            masked = [
                _NEUTRAL_TOKEN if token.lower().rstrip(".,;:!?") in all_terms else token
                for token in tokens
            ]
            item[field] = " ".join(masked)

    return perturbed


def calculate_confidence_drop(
    valid_news: list[dict[str, Any]],
    price_features: dict[str, Any],
) -> dict[str, Any]:
    """Compute Confidence Drop by re-running the forecast on perturbed news.

    Perturbation strategy (from the design spec):
      - Copy the valid news array.
      - Replace every sentiment keyword (positive *and* negative) from the
        extractor's lexicon with the neutral placeholder ``"note"``.
      - Run ``forecast_from_news`` on the masked copy.
      - Measure the drop in confidence.

    The metric follows the formula agreed in ``spec.md``::

        if original_prediction == perturbed_prediction:
            confidence_drop = original_confidence - perturbed_confidence
        else:
            confidence_drop = original_confidence   # prediction flipped

    Args:
        valid_news:     Accepted news items from the temporal retriever.
        price_features: Price feature dict (``price_5d_return``,
                        ``volume_change_pct``).

    Returns:
        Dict with keys:
            ``original_prediction`` / ``original_confidence``,
            ``perturbed_prediction`` / ``perturbed_confidence``,
            ``confidence_drop``  (rounded to 4 dp),
            ``is_faithful``      (bool: drop > 0.10 or prediction changed).
    """
    # --- Original forecast ---
    original = forecast_from_news(valid_news, price_features)
    orig_pred = original["prediction"]
    orig_conf = original["confidence"]

    # --- Perturbed forecast ---
    perturbed_news = _mask_sentiment_terms(valid_news)
    perturbed = forecast_from_news(perturbed_news, price_features)
    pert_pred = perturbed["prediction"]
    pert_conf = perturbed["confidence"]

    # --- Metric ---
    if orig_pred == pert_pred:
        drop = orig_conf - pert_conf
    else:
        drop = orig_conf  # prediction itself changed → maximum faithfulness signal

    drop = round(drop, 4)
    is_faithful = drop > 0.10 or orig_pred != pert_pred

    return {
        "original_prediction": orig_pred,
        "original_confidence": orig_conf,
        "perturbed_prediction": pert_pred,
        "perturbed_confidence": pert_conf,
        "confidence_drop": drop,
        "is_faithful": is_faithful,
    }


# ---------------------------------------------------------------------------
# Convenience: full faithfulness block for a single retrieval result
# ---------------------------------------------------------------------------

def evaluate_faithfulness(
    retrieval_result: dict[str, Any],
    price_features: dict[str, Any],
    model: str = "rule",
) -> dict[str, Any]:
    """Compute all three faithfulness metrics for one retrieval result.

    This is the single entry point used by ``main.py`` and tests.  It
    does NOT modify ``retrieval_result`` in place.

    Args:
        retrieval_result: Output of ``retriever.retrieve()``, containing
                          ``valid_news`` and ``invalid_future_news``.
        price_features:   Price feature dict from the raw record.
        model:            Model backend to use for the primary forecast
                          (``"rule"`` or ``"finbert"``).  The counterfactual
                          confidence-drop calculation always uses rule-based
                          for determinism and explainability.

    Returns:
        Dict with keys ``temporal_validity``, ``evidence_support``,
        ``confidence_drop``, and the full ``confidence_drop_detail``
        sub-dict from :func:`calculate_confidence_drop`.
    """
    valid_news = retrieval_result.get("valid_news", [])
    invalid_news = retrieval_result.get("invalid_future_news", [])

    temporal_validity = calculate_temporal_validity(len(valid_news), len(invalid_news))

    # Run the forecast on the valid news using the selected backend.
    forecast = run_forecast(valid_news, price_features, model=model)
    evidence = forecast.get("evidence", [])
    prediction = forecast.get("prediction", "HOLD")

    evidence_support = calculate_evidence_support(evidence, prediction)

    # Confidence drop always uses rule-based (deterministic, explainable).
    drop_detail = calculate_confidence_drop(valid_news, price_features)

    return {
        "temporal_validity": temporal_validity,
        "evidence_support": evidence_support,
        "confidence_drop": drop_detail["confidence_drop"],
        "confidence_drop_detail": drop_detail,
        "forecast": forecast,
    }
