"""Forecast module for Week 2 (rule-based) and Week 4 (FinBERT fusion).

This module serves as the Forecast Model layer in the pipeline, sitting
between the Evidence Extractor and the Faithfulness Evaluator. It provides
TWO model backends:
  1. A deterministic rule-based model that is always available.
  2. A FinBERT fusion model that requires PyTorch and a 418MB checkpoint.

Public API
----------
forecast_from_news(news_items, price_features)
    Rule-based net-sentiment predictor. Always available, no GPU needed.

forecast_from_news_finbert(news_items, price_features)
    FinBERT-based predictor. Falls back to rule-based if the checkpoint
    (models/finbert_fusion.pt) is absent so callers never crash.

run_forecast(news_items, price_features, model="rule")
    Unified dispatcher. Routes to the appropriate backend based on:
      1. The explicit ``model`` parameter ("rule" | "finbert") — highest priority.
      2. The ``USE_FINBERT`` environment variable when ``model`` is not given.
    Falls back to rule-based silently if the FinBERT checkpoint is missing.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from evidence_extractor import extract_evidence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT    = Path(__file__).resolve().parent.parent
_MODELS_DIR   = _REPO_ROOT / "models"
_CHECKPOINT   = _MODELS_DIR / "finbert_fusion.pt"
_LABEL_ENC    = _MODELS_DIR / "label_encoder.pkl"

_FINBERT_BASE = "ProsusAI/finbert"
# Tokenization truncation limit. 128 tokens covers ~2-3 news headlines.
# Longer sequences would slow inference without meaningful accuracy gains.
_MAX_LEN      = 128
# Fixed class order; MUST match the order used by the training label encoder.
_LABEL_NAMES  = ["DOWN", "HOLD", "UP"]


# ===========================================================================
# Rule-Based Model (Week 2 — always available)
# ===========================================================================

def forecast_from_news(
    news_items: list[dict[str, Any]],
    price_features: dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic direction and confidence for the provided evidence set.

    The model uses the Week 2 evidence extractor and simple historical price cues
    from the existing schema so it remains explainable and runnable without any
    external model dependencies. It computes a net-sentiment score (up vs down)
    and boosts confidence slightly using historical price returns and volume trends.
    """
    evidence = extract_evidence(news_items)

    # Calculate aggregate sentiment scores by summing individual evidence scores for each direction
    up_score   = sum(item["score"] for item in evidence if item["direction"] == "UP")
    down_score = sum(item["score"] for item in evidence if item["direction"] == "DOWN")

    # Safely extract price features, defaulting to 0.0 to prevent crashes on bad data
    try:
        price_return = float(price_features.get("price_5d_return", 0.0) or 0.0)
    except (TypeError, ValueError):
        price_return = 0.0
    try:
        volume_change = float(price_features.get("volume_change_pct", 0.0) or 0.0)
    except (TypeError, ValueError):
        volume_change = 0.0

    # Determine direction based on whether UP or DOWN evidence is stronger
    if up_score > down_score:
        prediction      = "UP"
        signal_strength = up_score - down_score
        # Base confidence starts at 0.55, boosted by signal strength (gap between scores, capped at 0.30)
        confidence      = 0.55 + min(0.30, signal_strength * 0.25)
        # Apply minor boosts if historical market context aligns with the sentiment
        if price_return > 0:
            confidence += 0.05
        if volume_change > 0:
            confidence += 0.03
    elif down_score > up_score:
        prediction      = "DOWN"
        signal_strength = down_score - up_score
        # Symmetrical logic for DOWN predictions
        confidence      = 0.55 + min(0.30, signal_strength * 0.25)
        if price_return < 0:
            confidence += 0.05
        if volume_change < 0:
            confidence += 0.03
    else:
        # Fallback to HOLD if evidence is perfectly tied or completely absent
        prediction = "HOLD"
        # Confidence relies purely on total evidence volume in this tied state
        confidence = 0.50 + min(0.15, (up_score + down_score) * 0.10)

    # Clamp confidence to a reasonable probability range [0.50, 0.95]
    confidence = round(min(0.95, max(0.50, confidence)), 2)

    return {
        "prediction":    prediction,
        "confidence":    confidence,
        "evidence_count": len(evidence),
        "evidence":      evidence,
    }


# ===========================================================================
# FinBERT Fusion Model (Week 4 — requires torch + transformers)
# ===========================================================================

def _try_import_torch():
    """Return (torch, nn, AutoModel, AutoTokenizer) or None if unavailable.
    
    This allows safely running the pipeline in environments without PyTorch installed,
    falling back to the rule-based approach.
    """
    try:
        import torch
        import torch.nn as nn
        from transformers import AutoModel, AutoTokenizer
        return torch, nn, AutoModel, AutoTokenizer
    except ImportError:
        return None


class FinBERTFusionModel:
    """Wrapper that lazy-loads the FinBERT checkpoint on first call.

    Uses a Singleton pattern (_instance) to avoid re-loading the 418MB model
    on every record in a batch loop.

    Mirrors the architecture in notebooks/week4_finbert_training.ipynb:
        CLS (768) || price_features (2)  →  Linear(770,128)  →  ReLU  →  Dropout(0.2)  →  Linear(128,3)
    """

    _instance: "FinBERTFusionModel | None" = None

    def __init__(self) -> None:
        libs = _try_import_torch()
        if libs is None:
            raise ImportError(
                "torch and transformers are required for FinBERT inference. "
                "Install via: pip install -r requirements-gpu.txt"
            )
        self._torch, nn, AutoModel, self._tokenizer_cls = libs
        import torch.nn as _nn
        from transformers import AutoTokenizer

        # Setup device for CPU/GPU inference automatically
        self._device = self._torch.device(
            "cuda" if self._torch.cuda.is_available() else "cpu"
        )
        self._tokenizer = AutoTokenizer.from_pretrained(_FINBERT_BASE)

        # Capture torch at this scope so the nested _Net class can use it
        import torch as _torch_ref

        # Build model architecture
        class _Net(_nn.Module):
            def __init__(self):
                super().__init__()
                # use_safetensors=False is required because the checkpoint was saved 
                # as a .pt file (PyTorch), not the newer .safetensors format.
                self.bert    = AutoModel.from_pretrained(
                    _FINBERT_BASE, use_safetensors=False
                )
                for p in self.bert.parameters():
                    p.requires_grad = False
                hidden       = self.bert.config.hidden_size
                # Fusion layer taking BERT's CLS output (768) + 2 numerical price features
                self.fusion_layer = _nn.Linear(hidden + 2, 128)
                self.relu    = _nn.ReLU()
                self.dropout = _nn.Dropout(0.2)
                self.output_layer = _nn.Linear(128, 3)

            def forward(self, input_ids, attention_mask, price_features):
                # Extract CLS vector representing the entire sentence sequence
                cls_vec = self.bert(
                    input_ids=input_ids, attention_mask=attention_mask
                ).last_hidden_state[:, 0, :]
                # Concatenate the text features (CLS) with structured numeric features
                fused  = _torch_ref.cat([cls_vec, price_features], dim=1)
                x      = self.dropout(self.relu(self.fusion_layer(fused)))
                return self.output_layer(x)

        self._net_cls = _Net

    @classmethod
    def get_instance(cls) -> "FinBERTFusionModel":
        # Singleton access to ensure model weights are loaded into memory exactly once
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(
        self,
        headlines: list[str],
        price_5d: float,
        vol_chg: float,
    ) -> tuple[str, float]:
        """Return (prediction_label, confidence) for a list of headlines."""
        torch = self._torch

        # Concatenate all headlines into one passage for simplicity
        text = " ".join(headlines) if headlines else "no news"
        # Tokenize and truncate to _MAX_LEN to maintain low latency
        enc  = self._tokenizer(
            text,
            max_length=_MAX_LEN,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Lazy load net + checkpoint
        if not hasattr(self, "_net"):
            self._net = self._net_cls().to(self._device)
            # weights_only=True avoids the torch.load CVE-2025-32434 warning;
            # our checkpoint only contains a state_dict (tensors), so this is safe.
            # map_location=self._device ensures it loads correctly on CPU even if trained on GPU.
            state = torch.load(
                _CHECKPOINT, map_location=self._device, weights_only=True
            )
            self._net.load_state_dict(state)
            self._net.eval()

        # Prepare the structured features tensor
        price_tensor = torch.tensor(
            [[price_5d, vol_chg]], dtype=torch.float32, device=self._device
        )
        with torch.no_grad():
            logits = self._net(
                enc["input_ids"].to(self._device),
                enc["attention_mask"].to(self._device),
                price_tensor,
            )
            # Convert raw logits to probabilities over [DOWN, HOLD, UP]
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()

        # Find the max probability class
        idx        = int(max(range(len(probs)), key=lambda i: probs[i]))
        prediction = _LABEL_NAMES[idx]
        confidence = round(probs[idx], 4)
        return prediction, confidence


def _checkpoint_available() -> bool:
    return _CHECKPOINT.exists()


def forecast_from_news_finbert(
    news_items: list[dict[str, Any]],
    price_features: dict[str, Any],
) -> dict[str, Any]:
    """FinBERT-based forecast. Falls back to rule-based if checkpoint absent.

    The evidence list is always populated by the lexicon extractor so that
    the faithfulness evaluator has explainable attribution regardless of
    which model backend is active. FinBERT attention weights are not exposed, 
    so rule-based evidence is required for counterfactual masking.
    """
    # Evidence is always rule-based (explainable) to support faithfulness evaluation
    evidence = extract_evidence(news_items)

    # Graceful fallback: If the 418MB checkpoint was not downloaded, fall back to rules
    if not _checkpoint_available():
        logger.warning(
            "FinBERT checkpoint not found at %s — falling back to rule-based model.",
            _CHECKPOINT,
        )
        return forecast_from_news(news_items, price_features)

    # Graceful fallback: If PyTorch is unavailable
    try:
        fm = FinBERTFusionModel.get_instance()
    except ImportError as exc:
        logger.warning("FinBERT import failed (%s) — falling back to rule-based.", exc)
        return forecast_from_news(news_items, price_features)

    # Extract text fields from news items, joining possible keys where text might reside
    headlines = [
        str(item.get("cleaned_text") or item.get("text") or item.get("title") or "")
        for item in news_items
    ]
    # Safely parse numeric features for the fusion layer
    try:
        price_5d  = float(price_features.get("price_5d_return",  0.0) or 0.0)
        vol_chg   = float(price_features.get("volume_change_pct", 0.0) or 0.0)
    except (TypeError, ValueError):
        price_5d  = 0.0
        vol_chg   = 0.0

    # Execute inference
    try:
        prediction, confidence = fm.predict(headlines, price_5d, vol_chg)
    except Exception as exc:  # noqa: BLE001
        logger.warning("FinBERT inference failed (%s) — falling back to rule-based.", exc)
        return forecast_from_news(news_items, price_features)

    return {
        "prediction":    prediction,
        "confidence":    confidence,
        "evidence_count": len(evidence),
        "evidence":      evidence,   # always lexicon-based for explainability
    }


# ===========================================================================
# Unified Dispatcher
# ===========================================================================

def run_forecast(
    news_items: list[dict[str, Any]],
    price_features: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    """Route to rule-based or FinBERT backend.
    
    This is the unified entry point called by faithfulness_metrics and other layers.

    Priority:
      1. Explicit ``model`` parameter ("rule" | "finbert").
      2. ``USE_FINBERT=1`` environment variable (enables headless overrides).
      3. Default: rule-based.
    """
    # Check env var if no explicit parameter was provided
    if model is None:
        model = "finbert" if os.environ.get("USE_FINBERT", "").strip() == "1" else "rule"

    if model == "finbert":
        return forecast_from_news_finbert(news_items, price_features)
    return forecast_from_news(news_items, price_features)
