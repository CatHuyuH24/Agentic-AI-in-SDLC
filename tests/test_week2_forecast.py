from evidence_extractor import extract_evidence
from forecast_model import forecast_from_news


POSITIVE_NEWS = [
    {
        "news_id": "pos-1",
        "title": "Strong earnings beat expectations",
        "text": "Company posted strong earnings and beat expectations.",
        "cleaned_text": "company posted strong earnings and beat expectations",
    }
]

NEGATIVE_NEWS = [
    {
        "news_id": "neg-1",
        "title": "Weak guidance and lawsuit risk",
        "text": "Management warned of weak guidance and lawsuit risk.",
        "cleaned_text": "management warned of weak guidance and lawsuit risk",
    }
]


def test_forecast_model_returns_direction_and_confidence():
    result = forecast_from_news(POSITIVE_NEWS, {"price_5d_return": 0.02, "volume_change_pct": 0.1})

    assert result["prediction"] in {"UP", "DOWN", "HOLD"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["evidence_count"] == 1


def test_forecast_model_prefers_positive_signal_for_positive_news():
    result = forecast_from_news(POSITIVE_NEWS, {"price_5d_return": 0.02, "volume_change_pct": 0.1})

    assert result["prediction"] == "UP"
    assert result["confidence"] >= 0.6


def test_forecast_model_prefers_negative_signal_for_negative_news():
    result = forecast_from_news(NEGATIVE_NEWS, {"price_5d_return": -0.02, "volume_change_pct": -0.1})

    assert result["prediction"] == "DOWN"
    assert result["confidence"] >= 0.6
