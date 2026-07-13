from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fetch_real_data as fr


def test_align_news_to_prices_matches_previous_news_by_timestamp():
    price_df = pd.DataFrame(
        [
            {
                "ticker": "AAPL",
                "trading_date": "2024-01-03",
                "price_5d_return": 0.02,
                "volume_change_pct": 0.01,
                "label": "UP",
            },
            {
                "ticker": "AAPL",
                "trading_date": "2024-01-04",
                "price_5d_return": -0.01,
                "volume_change_pct": -0.02,
                "label": "DOWN",
            },
        ]
    )

    news_df = pd.DataFrame(
        [
            {
                "ticker": "AAPL",
                "news_time": "2024-01-02 16:30:00",
                "title": "Apple rises on earnings",
                "text": "Apple rises on earnings",
                "cleaned_text": "apple rises on earnings",
            },
            {
                "ticker": "AAPL",
                "news_time": "2024-01-03 08:00:00",
                "title": "Apple warns on demand",
                "text": "Apple warns on demand",
                "cleaned_text": "apple warns on demand",
            },
            {
                "ticker": "AAPL",
                "news_time": "2024-01-04 15:00:00",
                "title": "Apple after-hours move",
                "text": "Apple after-hours move",
                "cleaned_text": "apple after-hours move",
            },
        ]
    )

    aligned_df = fr.align_news_to_prices(price_df, news_df)

    assert len(aligned_df) == len(price_df)
    assert all(pd.Timestamp(row["news_time"]) < pd.Timestamp(row["forecast_time"]) for _, row in aligned_df.iterrows())
    assert aligned_df.iloc[0]["news_time"] == "2024-01-03 08:00:00"
    assert aligned_df.iloc[1]["news_time"] == "2024-01-03 08:00:00"
