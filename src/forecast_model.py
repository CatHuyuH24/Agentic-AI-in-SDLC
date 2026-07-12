"""Forecast module for Week 2 (rule-based) and Week 4 (FinBERT fusion).

Public API
----------
forecast_from_news(news_items, price_features)
    Rule-based net-sentiment predictor.  Always available, no GPU needed.

forecast_from_news_finbert(news_items, price_features)
    FinBERT-based predictor.  Falls back to rule-based if the checkpoint
    (models/finbert_fusion.pt) is absent so callers never crash.

run_forecast(news_items, price_features, model="rule")
    Unified dispatcher.  Routes to the appropriate backend based on:
      1. The explicit ``model`` parameter ("rule" | "finbert")  — highest priority.
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
_MAX_LEN      = 128
_LABEL_NAMES  = ["DOWN", "HOLD", "UP"]   # fixed class order


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
    external model dependencies.
    """
    evidence = extract_evidence(news_items)

    up_score   = sum(item["score"] for item in evidence if item["direction"] == "UP")
    down_score = sum(item["score"] for item in evidence if item["direction"] == "DOWN")

    try:
        price_return = float(price_features.get("price_5d_return", 0.0) or 0.0)
    except (TypeError, ValueError):
        price_return = 0.0
    try:
        volume_change = float(price_features.get("volume_change_pct", 0.0) or 0.0)
    except (TypeError, ValueError):
        volume_change = 0.0

    if up_score > down_score:
        prediction      = "UP"
        signal_strength = up_score - down_score
        confidence      = 0.55 + min(0.30, signal_strength * 0.25)
        if price_return > 0:
            confidence += 0.05
        if volume_change > 0:
            confidence += 0.03
    elif down_score > up_score:
        prediction      = "DOWN"
        signal_strength = down_score - up_score
        confidence      = 0.55 + min(0.30, signal_strength * 0.25)
        if price_return < 0:
            confidence += 0.05
        if volume_change < 0:
            confidence += 0.03
    else:
        prediction = "HOLD"
        confidence = 0.50 + min(0.15, (up_score + down_score) * 0.10)

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
    """Return (torch, nn, AutoModel, AutoTokenizer) or None if unavailable."""
    try:
        import torch
        import torch.nn as nn
        from transformers import AutoModel, AutoTokenizer
        return torch, nn, AutoModel, AutoTokenizer
    except ImportError:
        return None


class FinBERTFusionModel:
    """Wrapper that lazy-loads the FinBERT checkpoint on first call.

    Mirrors the architecture in notebooks/week4_finbert_training.ipynb:
        CLS (768) || price_features (2)  →  Linear(770,128)  →  ReLU  →  Linear(128,3)
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
                # use_safetensors=True bypasses torch.load (CVE-2025-32434),
                # allowing this to work on torch < 2.6.
                self.bert    = AutoModel.from_pretrained(
                    _FINBERT_BASE, use_safetensors=True
                )
                for p in self.bert.parameters():
                    p.requires_grad = False
                hidden       = self.bert.config.hidden_size
                self.fusion_layer = _nn.Linear(hidden + 2, 128)
                self.relu    = _nn.ReLU()
                self.dropout = _nn.Dropout(0.2)
                self.output_layer = _nn.Linear(128, 3)

            def forward(self, input_ids, attention_mask, price_features):
                cls_vec = self.bert(
                    input_ids=input_ids, attention_mask=attention_mask
                ).last_hidden_state[:, 0, :]
                fused  = _torch_ref.cat([cls_vec, price_features], dim=1)
                x      = self.dropout(self.relu(self.fusion_layer(fused)))
                return self.output_layer(x)

        self._net_cls = _Net

    @classmethod
    def get_instance(cls) -> "FinBERTFusionModel":
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
            state = torch.load(
                _CHECKPOINT, map_location=self._device, weights_only=True
            )
            self._net.load_state_dict(state)
            self._net.eval()

        price_tensor = torch.tensor(
            [[price_5d, vol_chg]], dtype=torch.float32, device=self._device
        )
        with torch.no_grad():
            logits = self._net(
                enc["input_ids"].to(self._device),
                enc["attention_mask"].to(self._device),
                price_tensor,
            )
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()

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
    """FinBERT-based forecast.  Falls back to rule-based if checkpoint absent.

    The evidence list is always populated by the lexicon extractor so that
    the faithfulness evaluator has explainable attribution regardless of
    which model backend is active.
    """
    # Evidence is always rule-based (explainable)
    evidence = extract_evidence(news_items)

    if not _checkpoint_available():
        logger.warning(
            "FinBERT checkpoint not found at %s — falling back to rule-based model.",
            _CHECKPOINT,
        )
        return forecast_from_news(news_items, price_features)

    try:
        fm = FinBERTFusionModel.get_instance()
    except ImportError as exc:
        logger.warning("FinBERT import failed (%s) — falling back to rule-based.", exc)
        return forecast_from_news(news_items, price_features)

    headlines = [
        str(item.get("cleaned_text") or item.get("text") or item.get("title") or "")
        for item in news_items
    ]
    try:
        price_5d  = float(price_features.get("price_5d_return",  0.0) or 0.0)
        vol_chg   = float(price_features.get("volume_change_pct", 0.0) or 0.0)
    except (TypeError, ValueError):
        price_5d  = 0.0
        vol_chg   = 0.0

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

    Priority:
      1. Explicit ``model`` parameter ("rule" | "finbert").
      2. ``USE_FINBERT=1`` environment variable.
      3. Default: rule-based.
    """
    if model is None:
        model = "finbert" if os.environ.get("USE_FINBERT", "").strip() == "1" else "rule"

    if model == "finbert":
        return forecast_from_news_finbert(news_items, price_features)
    return forecast_from_news(news_items, price_features)
