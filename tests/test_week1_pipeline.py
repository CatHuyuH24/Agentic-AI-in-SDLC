from pathlib import Path

from loader import load_dataset
from retriever import retrieve


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_dataset.json"


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


def test_pipeline_is_deterministic_for_same_input():
    first = [retrieve(record) for record in load_dataset(DATASET_PATH)]
    second = [retrieve(record) for record in load_dataset(DATASET_PATH)]

    assert first == second
