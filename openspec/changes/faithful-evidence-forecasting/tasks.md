# Task Checklist & Quality Gates

## 1. Week 1 Baseline Status (Completed)

- [x] 1.1 Establish canonical data schema, setup repository structure, and create a curated sample dataset (AAPL, TSLA, NVDA) with valid and future-news items.
- [x] 1.2 Implement data loader and schema adapter with warning-based exception handling.
- [x] 1.3 Implement temporal retriever filtering out future news (`news_time >= forecast_time`).
- [x] 1.4 Add pytest coverage for loader, retriever, and warning generation.
- [x] 1.5 Execute local verification run and sign off on Week 1 baseline.

---

## 2. Week 2 Baseline Status (Completed)

- [x] 2.1 Integrate Week 2 modules with the validated Week 1 temporal retrieval outputs.
- [x] 2.2 Implement financial lexicon keyword evidence extractor over cleaned news texts.
- [x] 2.3 Implement rule-based forecast engine combining sentiment signals with 5-day returns.
- [x] 2.4 Add unit tests verifying evidence parsing and directional forecast accuracy (8 tests passing).
- [x] 2.5 Complete manual inspection and record sign-off.

---

## 3. Week 3 Implementation Tasks (Completed)

- [x] 3.1 Implement programmatic faithfulness metrics in `src/faithfulness_metrics.py`.
  - **Acceptance**: Computes Temporal Validity, Evidence Support, and Confidence Drop (using text-masking counterfactual perturbation).
  - **Status**: Completed. Metrics calculation engine is pure and deterministic.
- [x] 3.2 Scaffold and build the Streamlit visualization dashboard in `src/dashboard.py`.
  - **Acceptance**: UI has dropdown selection for stocks, displays forecast direction/confidence, shows evidence tables, displays leakage warnings, and plots original vs. perturbed confidence bar charts.
  - **Status**: Completed. Built an interactive multi-column Streamlit UI with modular layout rendering.
- [x] 3.3 Create unit test suite in `tests/test_week3_metrics.py` and `tests/test_week3_dashboard.py`.
  - **Acceptance**: Asserts correctness of confidence drop math under news masking scenarios, and checks import reliability of the dashboard.
  - **Status**: Completed. 27 unit tests under `test_week3_metrics.py` plus a dashboard import smoke test in `test_week3_dashboard.py`.
- [x] 3.4 Integrate frontend with the pipeline backend.
  - **Acceptance**: Streamlit dashboard successfully imports and runs inference using the forecast model and metrics engine.
  - **Status**: Completed. Dashboard dynamically imports loader, retriever, and faithfulness modules, running inference on selected records.
- [x] 3.5 Run local end-to-end check and append human review notes to the ledger.
  - **Acceptance**: `pytest` passes all tests, and pipeline writes `outputs/week3_pipeline_output.json` and `outputs/faithfulness_results.csv`.
  - **Status**: Completed. All 36 tests pass, end-to-end script executed cleanly and produced output summaries.

---

## 4. Quality Gates

- [x] 4.1 Run local unit tests for Week 1 & 2 logic.
- [x] 4.2 Validate output JSON structures for ingestion and retrieval layers.
- [x] 4.3 Ensure `pytest` checks for faithfulness metrics calculations are 100% successful.
  - **Result**: `36 passed in 2.64s` (8 baseline + 27 metrics + 1 dashboard smoke test).
- [x] 4.4 Verify Streamlit UI compiles and imports without python exceptions.
  - **Result**: Import smoke test passes successfully and `py_compile` checks output clean bytecode.
- [x] 4.5 Document human verification notes in the project ledger below.

---

## 5. Human Sign-Off & Verification Ledger

- `[TASK-1.0] [2026-06-05] [Ingestion & Retriever] Approved by Member B -> Week 1 Quality Gate Passed.`
- `[TASK-2.0] [2026-06-10] [Lexicon Extractor & Forecast Model] Approved by Member A -> Week 2 Quality Gate Passed.`
- `[TASK-3.1] [2026-06-11] [Faithfulness Evaluator - faithfulness_metrics.py] Approved by Member A -> 35/35 tests passing, end-to-end pipeline writes JSON + CSV outputs.`
- `[TASK-3.3] [2026-06-11] [Week 3 Test Suite - test_week3_metrics.py] Approved by Member A -> Quality Gate 4.3 Passed.`
- `[TASK-3.5] [2026-06-11] [End-to-end pipeline run] Approved by Member A -> 38 records processed, 12/38 faithful, no exceptions.`
- `[TASK-3.2] [2026-06-11] [Streamlit Dashboard MVP - dashboard.py] Approved by Member A -> Interactive controls, alerts, Plotly charts, and layouts fully built.`
- `[TASK-3.4] [2026-06-11] [Frontend-Backend Integration] Approved by Member A -> Smoke tests passing, module is importable, pipeline executes dynamically.`
