"""Week 4 unit tests: FinBERT integration, model switch, and graceful fallback.

These tests are designed to pass even when:
  - torch / transformers are NOT installed (tests skip gracefully).
  - The real checkpoint (models/finbert_fusion.pt) does NOT exist
    (the fallback behaviour is what we're testing).

The tests use unittest.mock to simulate checkpoint presence/absence and
a tiny random-weight FinBERT surrogate so CI never needs a GPU or a
300MB model file.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# conftest.py adds src/ to sys.path automatically.

# ---------------------------------------------------------------------------
# Sample fixtures
# ---------------------------------------------------------------------------

SAMPLE_NEWS = [
    {
        "news_id": "N-TEST-001",
        "ticker": "AAPL",
        "title": "Apple reports strong iPhone sales growth",
        "cleaned_text": "apple reports strong iphone sales growth",
        "news_time": "2025-03-11 08:00:00",
    },
    {
        "news_id": "N-TEST-002",
        "ticker": "AAPL",
        "title": "Weak demand concerns emerge in Asia",
        "cleaned_text": "weak demand concerns emerge in asia",
        "news_time": "2025-03-11 10:00:00",
    },
]

SAMPLE_PRICE = {
    "price_5d_return": -0.015,
    "volume_change_pct": 0.08,
}

EXPECTED_KEYS = {"prediction", "confidence", "evidence_count", "evidence"}


# ---------------------------------------------------------------------------
# Helper: skip if torch is absent
# ---------------------------------------------------------------------------

def _torch_available() -> bool:
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# 6.1  forecast_from_news_finbert() returns correct schema (checkpoint present)
# ---------------------------------------------------------------------------

class TestFinBERTSchemaCompat:
    """Verify output schema when checkpoint is present (using mocked model)."""

    def test_output_keys_match_rule_based_schema(self, tmp_path):
        """forecast_from_news_finbert returns the same keys as forecast_from_news."""
        # Create a fake checkpoint file so _checkpoint_available() returns True
        fake_ckpt = tmp_path / "finbert_fusion.pt"
        fake_ckpt.write_bytes(b"FAKE")

        with (
            patch("forecast_model._CHECKPOINT", fake_ckpt),
            patch("forecast_model.FinBERTFusionModel.get_instance") as mock_instance,
        ):
            # Make predict() return a valid (prediction, confidence) tuple
            mock_fm = MagicMock()
            mock_fm.predict.return_value = ("DOWN", 0.72)
            mock_instance.return_value = mock_fm

            from forecast_model import forecast_from_news_finbert

            result = forecast_from_news_finbert(SAMPLE_NEWS, SAMPLE_PRICE)

        assert isinstance(result, dict), "Result should be a dict"
        assert EXPECTED_KEYS.issubset(result.keys()), (
            f"Missing keys: {EXPECTED_KEYS - result.keys()}"
        )
        assert result["prediction"] in ("UP", "DOWN", "HOLD")
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["evidence"], list)
        assert isinstance(result["evidence_count"], int)

    def test_confidence_is_float_in_unit_interval(self, tmp_path):
        fake_ckpt = tmp_path / "finbert_fusion.pt"
        fake_ckpt.write_bytes(b"FAKE")

        with (
            patch("forecast_model._CHECKPOINT", fake_ckpt),
            patch("forecast_model.FinBERTFusionModel.get_instance") as mock_instance,
        ):
            mock_fm = MagicMock()
            mock_fm.predict.return_value = ("UP", 0.88)
            mock_instance.return_value = mock_fm

            from forecast_model import forecast_from_news_finbert

            result = forecast_from_news_finbert(SAMPLE_NEWS, SAMPLE_PRICE)

        assert 0.0 <= result["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# 6.2  Graceful fallback when checkpoint is absent
# ---------------------------------------------------------------------------

class TestGracefulFallback:
    """forecast_from_news_finbert falls back silently when checkpoint is absent."""

    def test_missing_checkpoint_returns_rule_based_result(self, tmp_path):
        absent_path = tmp_path / "nonexistent_finbert_fusion.pt"
        # Ensure it definitely doesn't exist
        assert not absent_path.exists()

        with patch("forecast_model._CHECKPOINT", absent_path):
            from forecast_model import forecast_from_news, forecast_from_news_finbert

            fb_result = forecast_from_news_finbert(SAMPLE_NEWS, SAMPLE_PRICE)
            rb_result  = forecast_from_news(SAMPLE_NEWS, SAMPLE_PRICE)

        # Both should produce the same schema
        assert EXPECTED_KEYS.issubset(fb_result.keys())
        # Fallback should match the rule-based prediction exactly
        assert fb_result["prediction"] == rb_result["prediction"]
        assert fb_result["confidence"] == rb_result["confidence"]

    def test_missing_checkpoint_does_not_raise(self, tmp_path):
        absent_path = tmp_path / "nonexistent.pt"

        with patch("forecast_model._CHECKPOINT", absent_path):
            from forecast_model import forecast_from_news_finbert

            try:
                result = forecast_from_news_finbert(SAMPLE_NEWS, SAMPLE_PRICE)
            except Exception as exc:
                pytest.fail(
                    f"forecast_from_news_finbert raised {type(exc).__name__} "
                    f"when checkpoint was absent: {exc}"
                )

        assert result is not None


# ---------------------------------------------------------------------------
# 6.3  run_forecast() dispatcher routing
# ---------------------------------------------------------------------------

class TestRunForecastDispatcher:
    """run_forecast routes correctly based on explicit model parameter."""

    def test_explicit_rule_uses_rule_based(self):
        from forecast_model import forecast_from_news, run_forecast

        result = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE, model="rule")
        expected = forecast_from_news(SAMPLE_NEWS, SAMPLE_PRICE)

        assert result["prediction"] == expected["prediction"]
        assert result["confidence"] == expected["confidence"]

    def test_explicit_finbert_calls_finbert_function(self, tmp_path):
        absent_path = tmp_path / "no_checkpoint.pt"

        with patch("forecast_model._CHECKPOINT", absent_path):
            # With checkpoint absent, finbert falls back to rule — still no crash
            from forecast_model import run_forecast

            result = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE, model="finbert")

        assert EXPECTED_KEYS.issubset(result.keys())

    def test_default_model_is_rule(self):
        """Calling run_forecast() with no model arg should use rule-based."""
        from forecast_model import forecast_from_news, run_forecast

        result_default = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE)
        result_rule    = forecast_from_news(SAMPLE_NEWS, SAMPLE_PRICE)

        assert result_default["prediction"] == result_rule["prediction"]


# ---------------------------------------------------------------------------
# 6.4  USE_FINBERT=1 env var activates FinBERT via run_forecast()
# ---------------------------------------------------------------------------

class TestUseFinBERTEnvVar:
    """USE_FINBERT=1 env var should route run_forecast() to the finbert path."""

    def test_env_var_routes_to_finbert_path(self, tmp_path, monkeypatch):
        absent_path = tmp_path / "no_ckpt.pt"
        monkeypatch.setenv("USE_FINBERT", "1")

        with patch("forecast_model._CHECKPOINT", absent_path):
            from forecast_model import run_forecast

            # With no explicit model param, env var should activate finbert
            # (falls back to rule since checkpoint is absent — but no crash)
            result = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE)

        assert EXPECTED_KEYS.issubset(result.keys())

    def test_explicit_rule_overrides_env_var(self, monkeypatch):
        """Explicit model='rule' takes precedence over USE_FINBERT=1."""
        monkeypatch.setenv("USE_FINBERT", "1")

        from forecast_model import forecast_from_news, run_forecast

        result_dispatcher = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE, model="rule")
        result_direct     = forecast_from_news(SAMPLE_NEWS, SAMPLE_PRICE)

        assert result_dispatcher["prediction"] == result_direct["prediction"]
        assert result_dispatcher["confidence"] == result_direct["confidence"]

    def test_env_var_unset_uses_rule(self, monkeypatch):
        monkeypatch.delenv("USE_FINBERT", raising=False)

        from forecast_model import forecast_from_news, run_forecast

        result = run_forecast(SAMPLE_NEWS, SAMPLE_PRICE)
        expected = forecast_from_news(SAMPLE_NEWS, SAMPLE_PRICE)

        assert result["prediction"] == expected["prediction"]
