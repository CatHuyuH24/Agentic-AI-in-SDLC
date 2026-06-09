"""Temporal retriever for the Week 1 prototype."""

from __future__ import annotations

from typing import Any

from schema_adapter import canonical_output, parse_timestamp


def retrieve(record: dict[str, Any]) -> dict[str, Any]:
    """Separate valid news from invalid future-dated news."""
    output = canonical_output(record)
    output["ticker"] = record.get("ticker", "")
    output["forecast_time"] = record.get("forecast_time", "")

    forecast_dt = parse_timestamp(output["forecast_time"])
    for news_item in record.get("news", []):
        item = dict(news_item)
        news_time_dt = parse_timestamp(item.get("news_time"))

        if forecast_dt is None or news_time_dt is None:
            output["warnings"].append(
                f"Record {record.get('_record_index', '?')}: unable to compare timestamps for {item.get('news_id', 'news item')}."
            )
            continue

        if news_time_dt < forecast_dt:
            item["cleaned_text"] = item.get("cleaned_text", "")
            output["valid_news"].append(item)
        else:
            output["invalid_future_news"].append(
                {
                    "news_id": item.get("news_id"),
                    "news_time": item.get("news_time"),
                    "reason": "news_time >= forecast_time",
                    "title": item.get("title"),
                }
            )
            output["warnings"].append(
                f"Record {record.get('_record_index', '?')}: news item {item.get('news_id', 'unknown')} is not earlier than forecast_time."
            )

    return output
