"""End-to-end pipeline entry point.

Week 1: raw records -> loader -> retriever -> deterministic JSON output.
Week 2: + evidence extractor -> rule-based forecast model.
Week 3: + faithfulness metrics (temporal validity, evidence support,
         confidence drop via counterfactual perturbation).

Running this script produces two output files under ``outputs/``:
    week3_pipeline_output.json  — full combined result per record.
    faithfulness_results.csv    — compact CSV summary for review.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from loader import DEFAULT_DATASET, load_dataset
from retriever import retrieve
from faithfulness_metrics import evaluate_faithfulness


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
        },
    }


def main() -> None:
    dataset_path = DEFAULT_DATASET
    raw_records = load_dataset(dataset_path)

    combined_results = []
    for raw in raw_records:
        retrieval = retrieve(raw)
        price_features = raw.get("price_features", {})
        faith_result = evaluate_faithfulness(retrieval, price_features)

        combined = _build_combined_record(
            raw,
            retrieval,
            {"faithfulness": faith_result},
        )
        combined_results.append(combined)

    _OUTPUTS_DIR.mkdir(exist_ok=True)

    # --- Full JSON output ---
    json_path = _OUTPUTS_DIR / "week3_pipeline_output.json"
    json_path.write_text(json.dumps(combined_results, indent=2), encoding="utf-8")

    # --- Compact CSV for quick review ---
    csv_path = _OUTPUTS_DIR / "faithfulness_results.csv"
    csv_fields = [
        "ticker", "forecast_time", "label", "prediction", "confidence",
        "temporal_validity", "evidence_support", "confidence_drop", "is_faithful",
        "valid_news_count", "invalid_future_news_count",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for rec in combined_results:
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
                "valid_news_count": rec["valid_news_count"],
                "invalid_future_news_count": rec["invalid_future_news_count"],
            }
            writer.writerow(row)

    print(f"Processed {len(combined_results)} records.")
    print(f"  JSON  -> {json_path}")
    print(f"  CSV   -> {csv_path}")

    # --- Quick faithfulness summary ---
    faithful_count = sum(1 for r in combined_results if r["faithfulness"]["is_faithful"])
    print(
        f"  Faithful predictions: {faithful_count}/{len(combined_results)} "
        f"({100 * faithful_count // max(len(combined_results), 1)}%)"
    )


if __name__ == "__main__":
    main()
