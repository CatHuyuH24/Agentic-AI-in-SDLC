"""Canonical schema normalization helpers for the Week 1 prototype."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


REQUIRED_NEWS_FIELDS = ("news_id", "news_time", "title", "text")
VALID_LABELS = {"UP", "DOWN", "HOLD"}
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_timestamp(value: Any) -> datetime | None:
    """Parse a canonical timestamp string into a datetime value."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip(), TIMESTAMP_FORMAT)
    except ValueError:
        return None


def cleaned_text(value: str) -> str:
    """Return deterministic cleaned text for downstream use."""
    text = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return text


def normalize_record(raw_record: dict[str, Any], record_index: int) -> dict[str, Any]:
    """
    Normalize one raw record into the Week 1 canonical contract.
    <br/> Ensure the record have required fields, valid labels, correct timestamp format
    """
    warnings: list[str] = []
    ticker = raw_record.get("ticker")
    forecast_time = raw_record.get("forecast_time")
    label = raw_record.get("label")

    if not isinstance(ticker, str) or not ticker.strip():
        warnings.append(f"Record {record_index}: ticker is required.")
    if not isinstance(forecast_time, str) or not forecast_time.strip():
        warnings.append(f"Record {record_index}: forecast_time is required.")
    if not isinstance(raw_record.get("news"), list) or not raw_record["news"]:
        warnings.append(f"Record {record_index}: news must be a non-empty array.")
    if not isinstance(raw_record.get("price_features"), dict):
        warnings.append(f"Record {record_index}: price_features object is required.")

    price_features = raw_record.get("price_features") or {}
    price_5d_return = price_features.get("price_5d_return")
    volume_change_pct = price_features.get("volume_change_pct")

    if not isinstance(price_5d_return, (int, float)):
        warnings.append(f"Record {record_index}: price_5d_return must be numeric.")
    if not isinstance(volume_change_pct, (int, float)):
        warnings.append(f"Record {record_index}: volume_change_pct must be numeric.")

    if label not in VALID_LABELS:
        warnings.append(f"Record {record_index}: label must be one of UP, DOWN, HOLD.")

    forecast_dt = parse_timestamp(forecast_time)
    if forecast_dt is None and isinstance(forecast_time, str) and forecast_time.strip():
        warnings.append(f"Record {record_index}: forecast_time is invalid; expected YYYY-MM-DD HH:MM:SS.")

    normalized_news = []
    for item in raw_record.get("news", []):
        if not isinstance(item, dict):
            warnings.append(f"Record {record_index}: news entry must be an object.")
            continue

        news_id = item.get("news_id")
        news_time = item.get("news_time")
        title = item.get("title")
        text = item.get("text")

        missing_fields = [field for field in REQUIRED_NEWS_FIELDS if not item.get(field)]
        if missing_fields:
            warnings.append(
                f"Record {record_index}: missing news fields {', '.join(missing_fields)}."
            )

        news_time_dt = parse_timestamp(news_time)
        if news_time_dt is None and isinstance(news_time, str) and news_time.strip():
            warnings.append(
                f"Record {record_index}: news_time for {news_id or 'item'} is invalid."
            )

        if isinstance(text, str) and not text.strip():
            warnings.append(f"Record {record_index}: news text for {news_id or 'item'} is empty.")

        normalized_news.append(
            {
                "news_id": news_id,
                "news_time": news_time,
                "title": title,
                "text": text,
                "cleaned_text": cleaned_text(text) if isinstance(text, str) else "",
            }
        )

    return {
        "ticker": ticker if isinstance(ticker, str) else "",
        "forecast_time": forecast_time if isinstance(forecast_time, str) else "",
        "news": normalized_news,
        "price_features": {
            "price_5d_return": price_5d_return,
            "volume_change_pct": volume_change_pct,
        },
        "label": label,
        "warnings": warnings,
        "_record_index": record_index,
        "_forecast_dt": forecast_dt,
    }


def canonical_output(record: dict[str, Any]) -> dict[str, Any]:
    """Build the loader/retriever output contract for a record."""
    return {
        "ticker": record.get("ticker", ""),
        "forecast_time": record.get("forecast_time", ""),
        "valid_news": [],
        "invalid_future_news": [],
        "warnings": list(record.get("warnings", [])),
    }
