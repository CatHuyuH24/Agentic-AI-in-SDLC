## Why

The Week 1 baseline is now in place: the repository already contains a runnable loader, a temporal retriever, deterministic warning handling, a curated sample dataset, and local `pytest` coverage. The verified state is stable enough to reuse as the contract foundation for Week 2, where the next work is evidence extraction, simple rule-based forecasting, and confidence-based faithfulness checks.

## What Changes

- Preserve the validated Week 1 contract for data loading, temporal safety, warnings, and deterministic output.
- Extend the OpenSpec package to describe the next Week 2 work: evidence extraction from `valid_news`, rule-based sentiment scoring, and a baseline forecast path.
- Keep the implementation limited to the prototype stage so it remains runnable, testable, and traceable for the academic project.
- Continue the human review gate so the Week 2 work is verified before it is considered complete.

## Scope (Week 1 Baseline + Week 2 Extension)

### In Scope

- The existing Week 1 pipeline for AAPL, TSLA, and NVDA: canonical schema, loader, retriever, warning handling, and deterministic output.
- Reuse of the current sample dataset and the `valid_news` / `invalid_future_news` contract as the stable foundation for later modules.
- Week 2 evidence extraction and simple lexicon-based scoring over the accepted news items.
- Week 2 rule-based forecasting and confidence baseline using `price_features` plus extracted evidence.
- Local verification with `pytest` and human review notes before sign-off.

### Out of Scope

- Real-time news ingestion, GPU training, or production trading logic.
- Full dashboard polish or a finished forecasting system beyond the prototype stage.
- Any step that breaks the Week 1 temporal safety guarantee or the current warning contract.

## Current Verified State

- The current prototype is runnable and deterministic.
- Local `pytest` currently reports 3 passing tests for the Week 1 path.
- The existing loader/retriever contract is the correct base for the Week 2 evidence and forecasting modules.

## User Personas

- Research and Spec Reviewer: needs a defensible prototype, explicit temporal safety, and a clear Week 2 extension plan.
- Data and Integration Operator: needs stable ingestion, normalized schema output, and predictable warnings.
- QA Reviewer: needs reliable tests for temporal leakage, malformed records, and deterministic output throughout the next phase.

## Rules and Review Gates

- The Week 1 contract SHALL remain the stable input/output foundation for Week 2.
- The retriever SHALL continue to accept only `news_time < forecast_time` and SHALL classify `news_time >= forecast_time` as invalid future news.
- Any malformed or missing field SHALL still be warned about and handled safely.
- Week 2 modules SHALL build on the accepted `valid_news` set rather than reintroducing future-dated evidence.

## Dependencies and Assumptions

- The existing sample dataset and loader/retriever output are the base contract for upcoming evidence and forecasting modules.
- The repository structure under `data/`, `src/`, `tests/`, and `outputs/` remains the implementation boundary for this change.
- The Week 2 work SHALL be documented incrementally without discarding the Week 1 validation path.

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

The Week 1 implementation SHALL remain the stable contract for data loading, temporal filtering, and local tests, while Week 2 adds evidence extraction and forecasting on top of this base.

## Capabilities

### New Capabilities

- `forecasting`: end-to-end prototype support for evidence-based stock movement forecasting, temporal validity checks, and faithfulness analysis.
- `evidence_pipeline`: reusable evidence extraction and confidence baseline capabilities built on the Week 1 contract.

### Modified Capabilities

- The existing loader/retriever path is extended rather than replaced, preserving deterministic behavior and warning-based validation.

## Impact

- Planning artifacts under `openspec/changes/faithful-evidence-forecasting/` remain the source of truth for the next phase.
- Future implementation under `src/`, `tests/`, and `data/` should build on the current Week 1 contract rather than duplicate it.
- Alignment with the rubric in `docs/Do_an_cuoi_ki_Agentic_AI.md` and the project execution plan in `docs/project_plan.md` remains intact for the Week 2 path.
