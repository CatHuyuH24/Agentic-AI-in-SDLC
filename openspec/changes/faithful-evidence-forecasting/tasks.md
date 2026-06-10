## 1. Current Week 1 Baseline Status

- [x] 1.1 Confirm the Week 1 MVP scope, rubric mapping, dataset target, input schema, and explicit system boundaries for the prototype.
- [x] 1.2 Create the initial repository structure for `data/`, `src/`, `tests/`, and `outputs/`.
- [x] 1.3 Build a curated sample dataset of at least 30 records across AAPL, TSLA, and NVDA, including valid and invalid future-news examples.
- [x] 1.4 Implement the data loader and schema adapter for the canonical JSON contract.
- [x] 1.5 Implement the temporal retriever so only `news_time < forecast_time` is accepted and `news_time >= forecast_time` is flagged.
- [x] 1.6 Implement warning-based error handling for empty text, malformed timestamps, missing numeric fields, or invalid labels.
- [x] 1.7 Add pytest coverage for schema validation, temporal safety, warning behavior, and deterministic output.
- [x] 1.8 Run the local prototype end to end and record the human review note.
  - Verified baseline: local `python -m pytest` currently passes 3 tests, and the loader/retriever path remains deterministic for repeated runs.

## 2. Week 2 Implementation Tasks

- [x] 2.1 Reuse the verified Week 1 contract as the stable input/output foundation for evidence extraction and forecasting.
  - Acceptance: the Week 2 modules consume `valid_news`, `invalid_future_news`, and warnings without redefining the baseline schema.
- [x] 2.2 Implement a simple evidence extraction layer over `valid_news` and `cleaned_text`.
  - Acceptance: accepted news items are converted into evidence candidates that can be scored by a later rule-based module.
- [x] 2.3 Implement a rule-based forecasting baseline using evidence signals and `price_features`.
  - Acceptance: the prototype returns a simple direction/confidence output that remains explainable and deterministic.
- [x] 2.4 Extend tests to cover evidence extraction, confidence baseline behavior, and preserved temporal safety.
  - Acceptance: tests validate the new Week 2 path without weakening current temporal leakage protections.
- [x] 2.5 Run the local validation path again and update the human review note for the next milestone.
  - Acceptance: the updated pipeline remains runnable, reproducible, and traceable in the OpenSpec ledger.
  - Verified after the Week 2 forecasting addition: `python -m pytest` now passes 8 tests and the pipeline remains deterministic.

## 3. Quality Gates

- [x] 3.1 Run local `pytest` for the Week 1 logic before any manual sign-off.
- [x] 3.2 Verify the loader and retriever produce reproducible JSON output for the same sample input.
- [x] 3.3 Confirm the OpenSpec task ledger contains the human review and approval note for traceability.
- [x] 3.4 Re-run the validation path after the Week 2 evidence extraction extension is added.

## 4. Implementation Notes for Apply

- Keep the Week 1 baseline intact and reusable for Week 2 work.
- Extend the prototype in small steps: evidence extraction first, then a simple rule-based forecast layer.
- Do not remove the temporal safety, warning, or reproducibility guarantees already established in Week 1.
- Treat the current loader/retriever contract as the stable foundation for the next implementation phase.
