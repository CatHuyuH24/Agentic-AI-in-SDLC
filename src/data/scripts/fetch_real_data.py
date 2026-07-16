# scripts/fetch_real_data.py
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import urllib3
import yfinance as yf
from requests.adapters import HTTPAdapter

# Disable SSL verification globally for requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_original_send = HTTPAdapter.send
def _new_send(self, request, **kwargs):
    kwargs['verify'] = False
    return _original_send(self, request, **kwargs)
HTTPAdapter.send = _new_send # type: ignore

# Disable SSL verification globally for curl_cffi
try:
    import curl_cffi.requests as curl_requests
    _original_curl_request = curl_requests.Session.request
    def _new_curl_request(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_curl_request(self, *args, **kwargs)
    curl_requests.Session.request = _new_curl_request
except Exception:
    pass



ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _load_dotenv() -> None:
    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get_alpha_vantage_api_key() -> str:
    _load_dotenv()
    return os.getenv("ALPHA_VANTAGE_API", "")


def _to_market_open(timestamp: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(timestamp).floor("D") + pd.Timedelta(hours=9)


def _safe_text(value: str | None) -> str:
    return (value or "").strip()


def _parse_av_timestamp(value: str) -> pd.Timestamp | None:
    if not value:
        return None

    try:
        return pd.Timestamp(datetime.strptime(value, "%Y%m%dT%H%M%S"))
    except ValueError:
        return None


def download_prices(tickers, start, end):
    print(f"Downloading prices for {tickers} from {start} to {end}...")
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        group_by="ticker",
        auto_adjust=False,
        threads=False,
    )

    records = []
    ticker_list = list(tickers)

    for ticker in ticker_list:
        if len(ticker_list) == 1:
            ticker_df = raw.copy() # type: ignore
        else:
            ticker_df = raw[ticker].copy() if ticker in raw.columns else raw.xs(ticker, axis=1, level=0).copy() # type: ignore

        ticker_df = ticker_df.dropna()
        ticker_df["price_5d_return"] = ticker_df["Close"].pct_change(periods=5)
        ticker_df["volume_change_pct"] = ticker_df["Volume"].pct_change(periods=1)
        ticker_df["next_day_return"] = ticker_df["Close"].pct_change(periods=1).shift(-1)

        for date, row in ticker_df.iterrows():
            if pd.isna(row["next_day_return"]) or pd.isna(row["price_5d_return"]):
                continue

            ret = float(row["next_day_return"])
            if ret > 0.005:
                label = "UP"
            elif ret < -0.005:
                label = "DOWN"
            else:
                label = "HOLD"

            records.append(
                {
                    "ticker": ticker,
                    "trading_date": pd.Timestamp(date).strftime("%Y-%m-%d"), # type: ignore
                    "price_5d_return": float(row["price_5d_return"]),
                    "volume_change_pct": float(row["volume_change_pct"]) if not pd.isna(row["volume_change_pct"]) else 0.0,
                    "label": label,
                }
            )

    return pd.DataFrame(records)


def load_news(tickers, start: str = "2023-01-01", end: str = "2025-12-31"):
    import time
    api_key = _get_alpha_vantage_api_key()
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API is missing. Add it to the project .env file before rerunning the script.")

    print("Loading Alpha Vantage NEWS_SENTIMENT data...")
    records = []

    # Convert start and end from YYYY-MM-DD to YYYYMMDDTHHMM
    try:
        start_formatted = pd.to_datetime(start).strftime("%Y%m%dT%H%M")
    except Exception:
        start_formatted = start

    try:
        end_formatted = pd.to_datetime(end).strftime("%Y%m%dT%H%M")
    except Exception:
        end_formatted = end

    for idx, ticker in enumerate(tickers):
        if idx > 0:
            print("Sleeping 2.0 seconds to avoid Alpha Vantage rate limits...")
            time.sleep(2.0)
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "time_from": start_formatted,
            "time_to": end_formatted,
            "limit": 1000,
            "sort": "EARLIEST",
            "apikey": api_key,
        }
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        if payload.get("Note"):
            print(payload["Note"])

        feed_key = "feed" if "feed" in payload else "Feed"
        if feed_key not in payload:
            raise ValueError(f"Alpha Vantage did not return a Feed payload for {ticker}: {payload}")

        for article in payload.get(feed_key, []):
            news_time = _parse_av_timestamp(article.get("time_published"))
            if news_time is None:
                continue

            title = _safe_text(article.get("title"))
            summary = _safe_text(article.get("summary"))
            text = summary or title
            cleaned_text = title + " " + summary if title and summary else title or summary

            sentiment_label = article.get("overall_sentiment_label", "")
            if "bullish" in sentiment_label.lower():
                mapped_label = "UP"
            elif "bearish" in sentiment_label.lower():
                mapped_label = "DOWN"
            else:
                mapped_label = "HOLD"

            records.append(
                {
                    "ticker": ticker,
                    "news_time": news_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "title": title,
                    "text": text,
                    "cleaned_text": cleaned_text.lower(),
                    "sentiment_label": mapped_label,
                    "sentiment_score": article.get("overall_sentiment_score"),
                }
            )

    if not records:
        raise ValueError("No Alpha Vantage news records were returned for the requested ticker set.")

    return pd.DataFrame(records)


def map_polarity(polarity_label):
    if polarity_label == 1:
        return "UP"
    elif polarity_label == 0:
        return "DOWN"
    return "HOLD"


def align_news_to_prices(price_df, news_df):
    print("Aligning Alpha Vantage news to price forecast timestamps...")
    aligned_records = []

    if price_df.empty or news_df.empty:
        return pd.DataFrame(aligned_records)

    price_df = price_df.copy()
    price_df["trading_date"] = pd.to_datetime(price_df["trading_date"])
    price_df["forecast_time"] = price_df["trading_date"].apply(_to_market_open)

    news_df = news_df.copy()
    news_df["news_time"] = pd.to_datetime(news_df["news_time"], errors="coerce")
    news_df = news_df.dropna(subset=["news_time"]).sort_values("news_time")

    for ticker in sorted(price_df["ticker"].unique()):
        price_subset = price_df[price_df["ticker"] == ticker].sort_values("forecast_time")
        news_subset = news_df[news_df["ticker"] == ticker].sort_values("news_time")

        if news_subset.empty:
            continue

        for _, p_row in price_subset.iterrows():
            forecast_time = p_row["forecast_time"]
            prior_news = news_subset[
                (news_subset["news_time"] < forecast_time) & 
                (news_subset["news_time"] >= forecast_time - pd.Timedelta(days=7))
            ]
            if prior_news.empty:
                continue

            latest_news = prior_news.iloc[-1]
            aligned_records.append(
                {
                    "ticker": ticker,
                    "forecast_time": forecast_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "news_time": latest_news["news_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "news_title": latest_news["title"],
                    "title": latest_news["title"],
                    "text": latest_news["text"],
                    "cleaned_text": latest_news["cleaned_text"],
                    "price_5d_return": p_row["price_5d_return"],
                    "volume_change_pct": p_row["volume_change_pct"],
                    "label": p_row["label"],
                }
            )

    return pd.DataFrame(aligned_records)


def join_price_and_news(price_df, news_df):
    return align_news_to_prices(price_df, news_df)


def save_corpus(df, path):
    print(f"Saving corpus to {path}...")
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path_obj, index=False)
    print(f"Total rows: {len(df)}")
    print(df["ticker"].value_counts())


if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "NVDA"]
    price_df = download_prices(tickers, "2023-01-01", "2025-12-31")
    news_df = load_news(tickers)
    final_df = join_price_and_news(price_df, news_df)
    save_corpus(final_df, ROOT_DIR / "../data" / "financial_corpus.csv")
