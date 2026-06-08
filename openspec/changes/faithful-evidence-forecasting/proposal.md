## Why

This Week 1 change establishes the minimum runnable prototype for faithful evidence forecasting: a small dataset, a canonical input schema, a loader that normalizes records, and a temporal retriever that rejects future-dated news. The goal is to produce a prototype that can be executed locally and tested with `pytest` before any later evidence or dashboard work is added.

## What Changes

- Create the Week 1 OpenSpec package for the faithful evidence forecasting prototype.
- Define the canonical schema and the loader/retriever contract required for the first runnable pipeline.
- Prepare a curated sample dataset of at least 30 records with valid and invalid future-news cases.
- Define the Week 1 implementation tasks, validation rules, and human review gate needed for immediate execution.

## Scope (Week 1 Only)

### In Scope

- A small prototype pipeline for AAPL, TSLA, and NVDA.
- A curated dataset with `ticker`, `forecast_time`, `news_time`, `news_text`, `price_5d_return`, `volume_change_pct`, and `label`.
- A loader that converts raw records into the canonical JSON schema.
- A temporal retriever that returns `valid_news` and `invalid_future_news`.
- Local tests that verify schema validation, temporal safety, and warning behavior.

### Out of Scope

- Evidence extraction beyond the loader/retriever contract.
- Forecasting labels, confidence models, or dashboard visuals.
- Real-time news ingestion, GPU work, or production trading logic.

## User Personas

- Research and Spec Reviewer: needs a clear, defensible Week 1 prototype and explicit temporal safety rules.
- Data and Integration Operator: needs a deterministic loader and retriever that can be run and tested locally.
- QA Reviewer: needs reliable test cases and warning outputs for malformed or future-dated records.

## Rules and Review Gates

- The loader SHALL normalize and validate the canonical schema before downstream logic runs.
- The retriever SHALL accept only `news_time < forecast_time` and SHALL classify `news_time >= forecast_time` as invalid future news.
- Any malformed or missing record SHALL be warned about and skipped rather than crashing the run.
- The Week 1 prototype SHALL be verified with local `pytest` and a short human review note before sign-off.

## Dependencies and Assumptions

- The dataset and loader output are the stable contract for later evidence and forecasting modules.
- The repository structure under `data/`, `src/`, `tests/`, and `outputs/` is expected to exist before implementation begins.

## Canonical Data Structures

### Input model (raw record -> canonical JSON)

```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00:00",
  "news": [
    {
      "news_id": "0001",
      "news_time": "2025-03-11 08:30:00",
      "title": "Apple reports weak iPhone sales in China",
      "text": "Apple reports weak iPhone sales in China after softer demand."
    }
  ],
  "price_features": {
    "price_5d_return": -0.02,
    "volume_change_pct": 0.15
  },
  "label": "DOWN"
}
```

### Output model (loader + retriever contract)

```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00:00",
  "valid_news": [
    {
      "news_id": "0001",
      "news_time": "2025-03-11 08:30:00",
      "title": "Apple reports weak iPhone sales in China",
      "text": "Apple reports weak iPhone sales in China after softer demand.",
      "cleaned_text": "apple reports weak iphone sales in china after softer demand"
    }
  ],
  "invalid_future_news": [],
  "warnings": []
}
```

The Week 1 implementation SHALL use these structures as the main contract for data loading, temporal filtering, and local testing.

## Capabilities

### New Capabilities

- `forecasting`: end-to-end prototype support for evidence-based stock movement forecasting, temporal validity checks, and faithfulness analysis.

### Modified Capabilities

- None

## Impact

- Planning artifacts under `openspec/changes/faithful-evidence-forecasting/`
- Future implementation under `src/`, `tests/`, and `data/`
- Alignment with the rubric in `docs/ChuDe1.pdf` and the project execution plan in `docs/project_plan.md`
