"""Week 1 dataset loader and schema adapter entry point."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schema_adapter import canonical_output, normalize_record


DEFAULT_DATASET = Path(__file__).resolve().parent.parent / "data" / "sample_dataset.json"


def load_dataset(path: str | Path = DEFAULT_DATASET) -> list[dict[str, Any]]:
    """Load and normalize raw records from a JSON file."""
    dataset_path = Path(path)
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))

    if not isinstance(payload, list):
        raise ValueError("Dataset must be a JSON array of records.")

    normalized = []
    for index, record in enumerate(payload, start=1):
        if not isinstance(record, dict):
            normalized.append(
                {
                    "ticker": "",
                    "forecast_time": "",
                    "news": [],
                    "price_features": {"price_5d_return": None, "volume_change_pct": None},
                    "label": "",
                    "warnings": [f"Record {index}: entry must be an object."],
                    "_record_index": index,
                }
            )
            continue

        normalized_record = normalize_record(record, index)
        normalized.append(
            {
                "ticker": normalized_record["ticker"],
                "forecast_time": normalized_record["forecast_time"],
                "news": normalized_record["news"],
                "price_features": normalized_record["price_features"],
                "label": normalized_record["label"],
                "warnings": normalized_record["warnings"],
                "_record_index": index,
                "_forecast_dt": normalized_record.get("_forecast_dt"),
            }
        )

    return normalized


def load_record(path: str | Path = DEFAULT_DATASET, index: int = 0) -> dict[str, Any]:
    """Load a single record by positional index from the dataset."""
    records = load_dataset(path)
    return records[index]

def load_corpus_csv(path: str | Path) -> list[dict[str, Any]]:
    import pandas as pd
    import math
    df = pd.read_csv(path)
    
    # We group by forecast_time and ticker to collect all news
    records = []
    index = 1
    
    # Actually, the python structure for retriever expects list of dicts.
    grouped = df.groupby(['ticker', 'forecast_time', 'price_5d_return', 'volume_change_pct', 'label'])
    
    for name, group in grouped:
        ticker, forecast_time, price_5d_return, volume_change_pct, label = name
        
        news_data = []
        for _, n_row in group.iterrows():
            title = n_row.get("news_title") or n_row.get("title") or ""
            text = n_row.get("cleaned_text") or n_row.get("text") or title or ""
            news_data.append({
                "news_id": f"N-{ticker}-{index}-{len(news_data)}",
                "news_time": n_row['news_time'],
                "title": title,
                "text": text,
                "cleaned_text": text,
            })
            
        record = {
            "ticker": ticker,
            "forecast_time": forecast_time,
            "news": news_data,
            "price_features": {
                "price_5d_return": float(price_5d_return),
                "volume_change_pct": float(volume_change_pct)
            },
            "label": label
        }
        
        # We need to normalize it using existing schema
        normalized_record = normalize_record(record, index)
        records.append({
            "ticker": normalized_record["ticker"],
            "forecast_time": normalized_record["forecast_time"],
            "news": normalized_record["news"],
            "price_features": normalized_record["price_features"],
            "label": normalized_record["label"],
            "warnings": normalized_record["warnings"],
            "_record_index": index,
            "_forecast_dt": normalized_record.get("_forecast_dt"),
        })
        index += 1
        
    return records
