from __future__ import annotations

from pathlib import Path

from faithfulness_metrics import (
    calculate_counterevidence_coverage,
    calculate_market_consistency,
    evaluate_faithfulness,
)
from loader import load_dataset
from retriever import retrieve


DATASET_PATH = Path(__file__).resolve().parents[1] / "src" / "data" / "sample_dataset.json"


class TestAdvancedFaithfulnessMetrics:
    def test_counterevidence_coverage_detects_mixed_evidence(self):
        evidence = [
            {"direction": "UP", "score": 0.8},
            {"direction": "DOWN", "score": 0.7},
        ]
        result = calculate_counterevidence_coverage(evidence, "UP")
        assert result == 1.0

    def test_counterevidence_coverage_is_zero_without_counterevidence(self):
        evidence = [{"direction": "UP", "score": 0.8}]
        result = calculate_counterevidence_coverage(evidence, "UP")
        assert result == 0.0

    def test_market_consistency_matches_bull_regime(self):
        evidence = [{"direction": "UP", "score": 0.8}]
        result = calculate_market_consistency(evidence, {"price_5d_return": 0.02, "volume_change_pct": 0.05})
        assert result["regime"] == "bull"
        assert result["consistency"] == 1.0

    def test_market_consistency_matches_sideways_regime(self):
        evidence = [{"direction": "HOLD", "score": 0.55}]
        result = calculate_market_consistency(evidence, {"price_5d_return": 0.001, "volume_change_pct": 0.01})
        assert result["regime"] == "sideways"
        assert result["consistency"] == 1.0


class TestEvaluateFaithfulnessExtended:
    def test_evaluate_faithfulness_returns_new_metric_fields(self):
        records = load_dataset(DATASET_PATH)
        sample = records[1]
        retrieval = retrieve(sample)

        result = evaluate_faithfulness(retrieval, sample.get("price_features", {}))

        assert "counterevidence_coverage" in result
        assert "market_consistency" in result
        assert "market_regime" in result
        assert 0.0 <= result["counterevidence_coverage"] <= 1.0
        assert 0.0 <= result["market_consistency"] <= 1.0
