## 1. Week 1 Implementation Tasks

- [x] 1.1 Confirm the Week 1 MVP scope, rubric mapping, dataset target, input schema, and explicit system boundaries for the prototype.
  - Acceptance: a written checklist exists for the Week 1 deliverables and the scope excludes later forecasting/dashboard work.
- [x] 1.2 Create the initial repository structure for `data/`, `src/`, `tests/`, and `outputs/`.
  - Acceptance: the directories exist and are ready for the sample dataset, loader, retriever, and tests.
- [x] 1.3 Build a curated sample dataset of at least 30 records across AAPL, TSLA, and NVDA, including valid and invalid future-news examples.
  - Acceptance: each row contains the required fields and includes at least one case where `news_time >= forecast_time`.
- [x] 1.4 Implement the data loader and schema adapter for the canonical JSON contract.
  - Acceptance: raw records are normalized into the schema below; malformed rows are detected and reported.
  - Required input fields: `ticker`, `forecast_time`, `news[].news_id`, `news[].news_time`, `news[].title`, `news[].text`, `price_features.price_5d_return`, `price_features.volume_change_pct`, and `label`.
  - Required output fields: `ticker`, `forecast_time`, `valid_news`, `invalid_future_news`, and `warnings`.
- [x] 1.5 Implement the temporal retriever so only `news_time < forecast_time` is accepted and `news_time >= forecast_time` is flagged.
  - Acceptance: the output contains `valid_news`, `invalid_future_news`, and warning entries for invalid records, using the JSON contract defined in the design package.
- [x] 1.6 Implement warning-based error handling for empty text, malformed timestamps, missing numeric fields, or invalid labels.
  - Acceptance: invalid records are skipped or flagged without crashing the run.
- [x] 1.7 Add pytest coverage for schema validation, temporal safety, warning behavior, and deterministic output.
  - Acceptance: tests pass locally and explicitly prove that future-dated news is rejected.
- [x] 1.8 Run the local prototype end to end and record the human review note.
  - Acceptance: the sample dataset loads, the retriever runs, and the result is documented for traceability.
  - Human review note: Verified locally with `python src/main.py` and `python -m pytest`; output is written to `outputs/week1_pipeline_output.json` and future-dated items are flagged as invalid.

## 2. Quality Gates

- [x] 2.1 Run local `pytest` for all Week 1 logic before any manual sign-off.
- [x] 2.2 Verify the loader and retriever produce reproducible JSON output for the same sample input.
- [x] 2.3 Confirm the OpenSpec task ledger contains the human review and approval note for traceability.

## 3. Implementation Notes for Apply

- Keep the implementation limited to the Week 1 pipeline: sample dataset, canonical schema, loader, retriever, warnings, and tests.
- Do not introduce evidence extraction, forecasting, or dashboard modules in this change.
- Treat the loader/retriever output as the stable contract for any future Week 2 or Week 3 work.
