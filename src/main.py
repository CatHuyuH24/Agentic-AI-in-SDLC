"""End-to-end pipeline entry point.

Week 1: raw records -> loader -> retriever -> deterministic JSON output.
Week 2: + evidence extractor -> rule-based forecast model.
Week 3: + faithfulness metrics (temporal validity, evidence support,
         confidence drop via counterfactual perturbation).
Week 4: + FinBERT fusion model support via --model flag.

Usage
-----
    python src/main.py                       # rule-based (default)
    python src/main.py --model rule          # explicit rule-based
    python src/main.py --model finbert       # FinBERT (requires checkpoint)
    python src/main.py --model both          # run both, write comparison CSV

Output files (under outputs/):
    week3_pipeline_output.json   — full combined result per record (active model)
    faithfulness_results.csv     — compact CSV summary (active model)
    week4_comparison.csv         — side-by-side comparison (--model both only)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Add the directory containing this script to python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from loader import DEFAULT_DATASET, load_dataset
from retriever import retrieve
from faithfulness_metrics import evaluate_faithfulness
from forecast_model import forecast_from_news, forecast_from_news_finbert


_OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


def _build_combined_record(
    raw: dict,
    retrieval: dict,
    faithfulness: dict,
) -> dict:
    """Merge retriever output + faithfulness block into the canonical schema."""
    forecast = faithfulness["faithfulness"]["forecast"]
    return {
        "ticker": retrieval["ticker"],
        "forecast_time": retrieval["forecast_time"],
        "label": raw.get("label"),
        "prediction": forecast["prediction"],
        "confidence": forecast["confidence"],
        "evidence_count": forecast["evidence_count"],
        "evidence": forecast["evidence"],
        "valid_news_count": len(retrieval["valid_news"]),
        "invalid_future_news_count": len(retrieval["invalid_future_news"]),
        "invalid_future_news": retrieval["invalid_future_news"],
        "warnings": retrieval["warnings"],
        "faithfulness": {
            "temporal_validity": faithfulness["faithfulness"]["temporal_validity"],
            "evidence_support": faithfulness["faithfulness"]["evidence_support"],
            "confidence_drop": faithfulness["faithfulness"]["confidence_drop"],
            "is_faithful": faithfulness["faithfulness"]["confidence_drop_detail"]["is_faithful"],
            "counterevidence_coverage": faithfulness["faithfulness"].get("counterevidence_coverage", 0.0),
            "market_consistency": faithfulness["faithfulness"].get("market_consistency", 0.0),
            "market_regime": faithfulness["faithfulness"].get("market_regime", "sideways"),
        },
    }


def _run_single_model(raw_records: list[dict], model: str) -> list[dict]:
    """Run the full pipeline for a single model backend."""
    results = []
    for raw in raw_records:
        retrieval = retrieve(raw)
        price_features = raw.get("price_features", {})
        faith_result = evaluate_faithfulness(retrieval, price_features, model=model)

        combined = _build_combined_record(
            raw,
            retrieval,
            {"faithfulness": faith_result},
        )
        results.append(combined)
    return results


def _write_single_model_outputs(results: list[dict], label: str) -> None:
    """Write JSON + CSV outputs for a single-model run."""
    _OUTPUTS_DIR.mkdir(exist_ok=True)

    json_path = _OUTPUTS_DIR / "week3_pipeline_output.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    csv_path = _OUTPUTS_DIR / "faithfulness_results.csv"
    csv_fields = [
        "ticker", "forecast_time", "label", "prediction", "confidence",
        "temporal_validity", "evidence_support", "confidence_drop", "is_faithful",
        "counterevidence_coverage", "market_consistency", "market_regime",
        "valid_news_count", "invalid_future_news_count",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for rec in results:
            row = {
                "ticker": rec["ticker"],
                "forecast_time": rec["forecast_time"],
                "label": rec["label"],
                "prediction": rec["prediction"],
                "confidence": rec["confidence"],
                "temporal_validity": rec["faithfulness"]["temporal_validity"],
                "evidence_support": rec["faithfulness"]["evidence_support"],
                "confidence_drop": rec["faithfulness"]["confidence_drop"],
                "is_faithful": rec["faithfulness"]["is_faithful"],
                "counterevidence_coverage": rec["faithfulness"].get("counterevidence_coverage", 0.0),
                "market_consistency": rec["faithfulness"].get("market_consistency", 0.0),
                "market_regime": rec["faithfulness"].get("market_regime", "sideways"),
                "valid_news_count": rec["valid_news_count"],
                "invalid_future_news_count": rec["invalid_future_news_count"],
            }
            writer.writerow(row)

    print(f"[{label}] Processed {len(results)} records.")
    print(f"  JSON  -> {json_path}")
    print(f"  CSV   -> {csv_path}")

    faithful_count = sum(1 for r in results if r["faithfulness"]["is_faithful"])
    print(
        f"  Faithful predictions: {faithful_count}/{len(results)} "
        f"({100 * faithful_count // max(len(results), 1)}%)"
    )


def _run_both_models(raw_records: list[dict]) -> None:
    """Run rule-based and FinBERT side-by-side; write comparison CSV."""
    _OUTPUTS_DIR.mkdir(exist_ok=True)

    comparison_rows = []
    for idx, raw in enumerate(raw_records):
        retrieval = retrieve(raw)
        price_features = raw.get("price_features", {})
        valid_news = retrieval.get("valid_news", [])
        true_label = str(raw.get("label", "")).upper()

        # Rule-based
        rb = forecast_from_news(valid_news, price_features)
        # FinBERT (graceful fallback built-in)
        fb = forecast_from_news_finbert(valid_news, price_features)

        rb_pred = rb["prediction"]
        fb_pred = fb["prediction"]
        comparison_rows.append({
            "record_index": raw.get("_record_index", idx),
            "ticker": retrieval.get("ticker", ""),
            "rule_prediction": rb_pred,
            "rule_confidence": round(rb["confidence"], 4),
            "finbert_prediction": fb_pred,
            "finbert_confidence": round(fb["confidence"], 4),
            "label": true_label,
            "rule_correct": int(rb_pred == true_label),
            "finbert_correct": int(fb_pred == true_label),
        })

    csv_path = _OUTPUTS_DIR / "week4_comparison.csv"
    fields = [
        "record_index", "ticker",
        "rule_prediction", "rule_confidence",
        "finbert_prediction", "finbert_confidence",
        "label", "rule_correct", "finbert_correct",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(comparison_rows)

    n = len(comparison_rows)
    rb_acc  = sum(r["rule_correct"]    for r in comparison_rows) / max(n, 1)
    fb_acc  = sum(r["finbert_correct"] for r in comparison_rows) / max(n, 1)
    print(f"[both] Processed {n} records.")
    print(f"  Rule-Based accuracy : {rb_acc:.2%}")
    print(f"  FinBERT accuracy    : {fb_acc:.2%}")
    print(f"  Comparison CSV      -> {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Faithful Evidence-Centric Forecasting Pipeline"
    )
    parser.add_argument(
        "--model",
        choices=["rule", "finbert", "both"],
        default="both",
        help="Model backend to use (default: rule). 'both' generates week4_comparison.csv.",
    )
    args = parser.parse_args()

    csv_path = Path("data/financial_corpus.csv")
    if csv_path.exists():
        from loader import load_corpus_csv
        print(f"Loading data from {csv_path}...")
        raw_records = load_corpus_csv(csv_path)
    else:
        print("Warning: data/financial_corpus.csv not found, falling back to sample_dataset.json")
        raw_records = load_dataset(DEFAULT_DATASET)

    if args.model == "both":
        # Generate the single-model outputs for the finbert model to update faithfulness_results.csv
        results = _run_single_model(raw_records, model="finbert")
        _write_single_model_outputs(results, label="finbert")
        _run_both_models(raw_records)
    else:
        results = _run_single_model(raw_records, model=args.model)
        _write_single_model_outputs(results, label=args.model)


if __name__ == "__main__":
    main()
