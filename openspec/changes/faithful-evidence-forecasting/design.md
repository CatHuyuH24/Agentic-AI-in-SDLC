## Context

The existing project plan already defines the research goal: build a faithful evidence-centric forecasting prototype, not a full trading system. The design therefore prioritizes a small, explainable pipeline with strict temporal safety, deterministic schema validation, and a loader/retriever contract that can be verified locally.

## Goals / Non-Goals

**Goals:**

- Establish a minimal Week 1 architecture for data ingestion, temporal filtering, and schema validation.
- Keep the implementation explainable, deterministic, and easy to verify with `pytest`.
- Produce a runnable prototype that can separate valid and invalid news records before any later modeling work.

**Non-Goals:**

- Full forecasting logic, evidence scoring beyond the loader/retriever contract, or dashboard polish.
- Real-time ingestion, GPU support, or production trading behavior.

## System Boundaries for Week 1

### In Scope

- Curated sample dataset for AAPL, TSLA, and NVDA with valid and invalid future-news examples.
- Loader and schema adapter that preserve original and cleaned text fields.
- Temporal retriever that separates `valid_news` from `invalid_future_news`.
- Local tests and human review notes for acceptance.

### Out of Scope

- Full faithfulness experiment design beyond baseline confidence-drop reporting.
- Production pipelines, real-time feeds, or advanced model fine-tuning.

## User Personas

- Research and Spec Reviewer: needs a defensible pipeline and explicit temporal safety.
- Data and Integration Operator: needs stable ingestion, schema normalization, and deterministic filtering.
- Project Reviewer / Demo Audience: needs simple evidence display and warning signals for lookahead leakage.

## Implementation Rules

1. Reject malformed or missing fields early and log warnings instead of crashing.
2. Treat `news_time < forecast_time` as the only accepted path.
3. Keep the accepted sample deterministic and small enough for local testing.
4. Record the human review note after each local verification pass.

## Week 1 Deliverables

- Finalized OpenSpec proposal, design, and spec package for the Week 1 prototype.
- A curated sample dataset with at least 30 records covering AAPL, TSLA, and NVDA.
- A minimal data loader and schema adapter for price/news input.
- A baseline temporal retriever that separates `valid_news` and `invalid_future_news`.
- Local tests for schema validation, future-news rejection, and warning behavior.

## Detailed Architecture Decisions

1. Data flow for Week 1: raw records -> normalize and validate -> temporal filter -> warning/validation report -> testable JSON output.
2. Temporal safety: `news_time < forecast_time` is the only accepted path; `news_time >= forecast_time` is rejected and flagged as future-dated leakage.
3. Schema contract: each record must contain `ticker`, `forecast_time`, `news`, `price_features`, and `label`, where `news` is an array of items with `news_id`, `news_time`, `title`, and `text`.
4. Error handling: malformed records are warned about and skipped so the pipeline remains runnable.
5. Output contract: the loader/retriever should expose structured `valid_news`, `invalid_future_news`, and `warnings` lists for downstream modules.

## Canonical Data Models

### Input data model

- `ticker`: string, required, ticker symbol such as `AAPL`.
- `forecast_time`: string timestamp in a consistent format, required.
- `news`: array of news records, required.
  - `news_id`: string, required for traceability.
  - `news_time`: string timestamp, required.
  - `title`: string, required.
  - `text`: string, required.
- `price_features`: object, required.
  - `price_5d_return`: float, required.
  - `volume_change_pct`: float, required.
- `label`: string, required, one of `UP`, `DOWN`, `HOLD`.

### Output data model

- `ticker`: string.
- `forecast_time`: string.
- `valid_news`: array of accepted news items, each with original fields and `cleaned_text`.
- `invalid_future_news`: array of rejected news items with reason `news_time >= forecast_time`.
- `warnings`: array of validation messages for malformed rows, missing fields, or invalid labels.

### Example JSON contracts

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

```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00:00",
  "valid_news": [],
  "invalid_future_news": [
    {
      "news_id": "0002",
      "news_time": "2025-03-12 15:30:00",
      "reason": "news_time >= forecast_time"
    }
  ],
  "warnings": [
    "Record 0002 rejected because news_time is not earlier than forecast_time."
  ]
}
```

## Dataset Strategy

- Start with a small curated dataset of 30–100 examples to validate logic quickly.
- Expand to a real-data path with at least 300 samples across AAPL, TSLA, and NVDA if time permits.
- Use `yfinance` for price history and a verified news source or pre-curated financial dataset for text.
- Generate labels from next-day close-to-close return using the rubric thresholds: UP > +0.5%, DOWN < -0.5%, otherwise HOLD.
- Keep a strict schema with `ticker`, `forecast_time`, `news_time`, `news_text`, `price_5d_return`, `volume_change_pct`, and `label`.

## Testing Strategy

- Unit tests: schema validation, date parsing, temporal rule correctness, and malformed-record warning behavior.
- Integration tests: one full sample run from raw input file through loader and retriever to the final JSON output.
- Human review: all AI-generated code must be verified with a local run and recorded in the OpenSpec task log.
- Acceptance checks: no future-dated news enters `valid_news`, warnings are produced for malformed records, and the output is reproducible for the same input.

## Agentic SDLC Workflow

1. Generate: AI assistant drafts logic, tests, or documentation.
2. Review: human developer validates syntax, logic, and temporal boundaries.
3. Test: run local `pytest` against the loader and retriever path.
4. Record: append the human review note to the task ledger for traceability.
5. Iterate: fix issues before promotion to the main implementation path.

## GitHub Repository Structure

- `docs/` — rubric brief and project master plan
- `openspec/changes/faithful-evidence-forecasting/` — proposal, design, spec, and tasks
- `data/` — curated sample dataset used for Week 1 validation
- `src/` — `loader.py`, `schema_adapter.py`, and `retriever.py` for the initial runnable pipeline
- `tests/` — temporal retriever and schema tests for Week 1 acceptance
- `outputs/` — generated validation output and warnings log

## Risks / Trade-offs

- [Data noise] → Mitigation: normalize text and keep a small curated sample for the MVP.
- [Temporal leakage] → Mitigation: reject any news published at or after the forecast timestamp.
- [Overclaiming faithfulness] → Mitigation: report confidence-drop metrics and explain their limits.
- [Limited compute] → Mitigation: start with rule-based logic and postpone GPU work.
- [Dataset sparsity] → Mitigation: use a small but representative sample and validate label generation carefully.

## Migration Plan

- Implement the Week 1 modules in the existing repository structure.
- Verify each module with tests before any later evidence or dashboard work is added.
- Keep the design modular so future modules can consume the same loader and retriever contract without rework.

## Open Questions

- Which real-data source will be used for the bonus dataset path?
- Which confidence metric will be used for the rule-based baseline and counterfactual comparison?
