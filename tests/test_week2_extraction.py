from loader import load_dataset
from retriever import retrieve
from evidence_extractor import extract_evidence


DATASET_PATH = "data/sample_dataset.json"


def test_extract_evidence_uses_only_valid_news_items():
    records = load_dataset(DATASET_PATH)
    sample = records[1]

    filtered = retrieve(sample)
    evidence = extract_evidence(filtered["valid_news"])

    assert evidence
    assert all(item["direction"] in {"UP", "DOWN", "HOLD"} for item in evidence)
    assert all("score" in item for item in evidence)
    assert all(item["news_id"] for item in evidence)


def test_extract_evidence_detects_positive_and_negative_tones():
    entries = [
        {
            "news_id": "pos-1",
            "title": "Strong earnings beat expectations",
            "text": "Company posted strong earnings and beat expectations.",
            "cleaned_text": "company posted strong earnings and beat expectations",
        },
        {
            "news_id": "neg-1",
            "title": "Weak guidance and lawsuit risk",
            "text": "Management warned of weak guidance and lawsuit risk.",
            "cleaned_text": "management warned of weak guidance and lawsuit risk",
        },
    ]

    evidence = extract_evidence(entries)

    assert any(item["direction"] == "UP" and item["news_id"] == "pos-1" for item in evidence)
    assert any(item["direction"] == "DOWN" and item["news_id"] == "neg-1" for item in evidence)
