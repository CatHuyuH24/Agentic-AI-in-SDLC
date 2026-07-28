from pathlib import Path
from loader import load_dataset
from retriever import retrieve
from evidence_extractor import extract_evidence


DATASET_PATH = Path(__file__).resolve().parents[1] / "src" / "data" / "sample_dataset.json"


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


def test_extract_evidence_comprehensive_cases(capsys):
    entries = [
        {
            "news_id": "pos-1",
            "title": "Earnings beat",
            "text": "Company posted strong earnings and beat expectations.",
            "cleaned_text": "company posted strong earnings and beat expectations",
        },
        {
            "news_id": "neg-1",
            "title": "Lawsuit risk",
            "text": "Management warned of weak guidance and lawsuit risk.",
            "cleaned_text": "management warned of weak guidance and lawsuit risk",
        },
        {
            "news_id": "hold-1",
            "title": "Stable quarter",
            "text": "The company announced regular operations without surprises.",
            "cleaned_text": "the company announced regular operations without surprises",
        },
        {
            "news_id": "pos-2",
            "title": "New product launch",
            "text": "The highly anticipated product launch was successful.",
            "cleaned_text": "the highly anticipated product launch was successful",
        },
        {
            "news_id": "neg-2",
            "title": "Supply chain disruption",
            "text": "A major drop in supply chain led to a fall in production.",
            "cleaned_text": "a major drop in supply chain led to a fall in production",
        },
    ]
    
    evidence = extract_evidence(entries)
    
    print("\nEvidence Extraction Output:")
    for item in evidence:
        print(f"ID: {item['news_id']} | Direction: {item['direction']} | Score: {item['score']} | Evidence: {item['evidence_text']}")
        
    assert any(item["direction"] == "UP" and item["news_id"] == "pos-1" for item in evidence)
    assert any(item["direction"] == "DOWN" and item["news_id"] == "neg-1" for item in evidence)
    assert any(item["direction"] == "HOLD" and item["news_id"] == "hold-1" for item in evidence)
    assert any(item["direction"] == "UP" and item["news_id"] == "pos-2" for item in evidence)
    assert any(item["direction"] == "DOWN" and item["news_id"] == "neg-2" for item in evidence)
    assert all("evidence_text" in item for item in evidence)
