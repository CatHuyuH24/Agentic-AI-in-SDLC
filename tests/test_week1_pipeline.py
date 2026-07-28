from pathlib import Path

from loader import load_dataset
from retriever import retrieve


DATASET_PATH = Path(__file__).resolve().parents[1] / "src" / "data" / "sample_dataset.json"


def test_loader_normalizes_dataset_and_reports_warnings():
    records = load_dataset(DATASET_PATH)

    assert len(records) >= 30
    assert all("ticker" in record for record in records)
    assert any(record["warnings"] for record in records)


def test_retriever_separates_future_news_from_valid_news():
    records = load_dataset(DATASET_PATH)

    sample = records[0]
    result = retrieve(sample)

    assert "valid_news" in result
    assert "invalid_future_news" in result
    assert "warnings" in result
    assert isinstance(result["valid_news"], list)
    assert isinstance(result["invalid_future_news"], list)

    all_results = [retrieve(record) for record in records]
    assert any(item["invalid_future_news"] for item in all_results)
    assert any("not earlier than forecast_time" in warning for item in all_results for warning in item["warnings"])


def test_temporal_retriever_detects_valid_and_future_news():
    record = {
        "_record_index": "test-1",
        "ticker": "AAPL",
        "forecast_time": "2024-05-10 12:00:00",
        "news": [
            {
                "news_id": "news-1",
                "news_time": "2024-05-09 10:00:00",
                "title": "Valid News",
                "text": "This is a valid news",
                "cleaned_text": "this is a valid news",
            },
            {
                "news_id": "news-2",
                "news_time": "2024-05-10 13:00:00",
                "title": "Future News",
                "text": "This is a future news",
                "cleaned_text": "this is a future news",
            },
            {
                "news_id": "news-3",
                "news_time": "2024-05-10 12:00:00",
                "title": "Exact Time News",
                "text": "This is an exact time news",
                "cleaned_text": "this is an exact time news",
            },
            {
                "news_id": "news-4",
                "news_time": "invalid_date",
                "title": "Invalid Date News",
                "text": "This is an invalid date news",
                "cleaned_text": "this is an invalid date news",
            }
        ]
    }
    
    result = retrieve(record)
    
    assert len(result["valid_news"]) == 1
    assert result["valid_news"][0]["news_id"] == "news-1"
    
    assert len(result["invalid_future_news"]) == 2
    invalid_ids = [n["news_id"] for n in result["invalid_future_news"]]
    assert "news-2" in invalid_ids
    assert "news-3" in invalid_ids
    
    assert len(result["warnings"]) == 3



def test_pipeline_is_deterministic_for_same_input():
    first = [retrieve(record) for record in load_dataset(DATASET_PATH)]
    second = [retrieve(record) for record in load_dataset(DATASET_PATH)]

    assert first == second
