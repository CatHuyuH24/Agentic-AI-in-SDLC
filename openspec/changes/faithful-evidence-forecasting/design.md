## Context

The existing project plan already defines the research goal: build a faithful evidence-centric forecasting prototype, not a full trading system. The design therefore prioritizes a small, explainable pipeline with strict temporal safety, simple rule-based forecasting, and a dashboard that makes evidence and confidence-drop behavior visible.

## Goals / Non-Goals

**Goals:**

- Establish a baseline architecture for data ingestion, temporal filtering, evidence extraction, forecasting, and faithfulness evaluation.
- Keep implementation explainable and reviewable for academic grading.
- Support a Streamlit dashboard and testable acceptance criteria.
- Produce a compact, runnable prototype within the first three implementation weeks.

**Non-Goals:**

- Full production trading automation.
- High-frequency market simulation.
- Advanced GPU model training in the first implementation pass.

## Week 1 Deliverables

- Finalized OpenSpec proposal, design, and spec package for the forecasting capability.
- A sample dataset with at least 30 curated records covering AAPL, TSLA, and NVDA.
- A minimal data loader and schema adapter for price/news input.
- A baseline temporal retriever with valid vs. invalid future-news separation.

## Week 2 Deliverables

- Rule-based evidence extraction using a financial lexicon and cleaned text fragments.
- A basic forecast model producing UP/DOWN/HOLD labels and confidence scores.
- Faithfulness metrics for confidence drop and temporal validity.
- Initial pytest suite for temporal leakage and evidence logic.

## Week 3 Deliverables

- A working Streamlit dashboard showing prediction, evidence, and warning signals.
- End-to-end demo output for one or more sample tickers.
- A short report outline, test log, and risk notes for the final hand-off.

## Detailed Architecture Decisions

1. Data flow: raw price/news input -> normalize and validate -> temporal filter -> evidence extraction -> forecasting -> faithfulness analysis -> dashboard.
2. Temporal safety: `news_time < forecast_time` is the only valid path; `news_time >= forecast_time` is rejected and highlighted as lookahead leakage.
3. Evidence extraction: deterministic lexicon rules over cleaned text, with support score and expected direction for each fragment.
4. Forecasting: start with a simple rule-based model using news sentiment and price feature direction; reserve FinBERT integration for later extension.
5. Faithfulness: compute confidence drop when cited evidence is masked or neutralized, and report the result as evidence necessity vs. post-hoc decoration.
6. Dashboard: Streamlit for fast demonstration, Plotly for simple comparison bars, and tables for evidence and warnings.

## Dataset Strategy

- Start with a small curated dataset of 30–100 examples to validate logic quickly.
- Expand to a real-data path with at least 300 samples across AAPL, TSLA, and NVDA if time permits.
- Use `yfinance` for price history and a verified news source or pre-curated financial dataset for text.
- Generate labels from next-day close-to-close return using the rubric thresholds: UP > +0.5%, DOWN < -0.5%, otherwise HOLD.
- Keep a strict schema with `ticker`, `forecast_time`, `news_time`, `news_text`, `price_5d_return`, `volume_change_pct`, and `label`.

## Testing Strategy

- Unit tests: temporal rule correctness, evidence extraction polarity, confidence-drop calculation.
- Integration tests: one full sample run through data ingestion, retriever, extractor, model, and dashboard rendering.
- Human review: all AI-generated code must be verified with a local run and recorded in the OpenSpec task log.
- Acceptance checks: no future-dated news passes the retriever, evidence fragments are displayed, and predictions remain reproducible for the same input.

## Agentic SDLC Workflow

1. Generate: AI assistant drafts logic, tests, or documentation.
2. Review: human developer validates syntax, logic, and temporal boundaries.
3. Test: run local pytest and sample dashboard checks.
4. Record: append the human review note to the task ledger for traceability.
5. Iterate: fix issues before promotion to the main implementation path.

## GitHub Repository Structure

- `docs/` — rubric brief and project master plan
- `openspec/changes/faithful-evidence-forecasting/` — proposal, design, spec, and tasks
- `data/` — curated sample and real-data corpus
- `src/` — `retriever.py`, `evidence_extractor.py`, `forecast_model.py`, `faithfulness_metrics.py`, `dashboard.py`
- `tests/` — temporal retriever and faithfulness metric tests
- `outputs/` — prediction and visualization outputs

## Risks / Trade-offs

- [Data noise] → Mitigation: normalize text and keep a small curated sample for the MVP.
- [Temporal leakage] → Mitigation: reject any news published at or after the forecast timestamp.
- [Overclaiming faithfulness] → Mitigation: report confidence-drop metrics and explain their limits.
- [Limited compute] → Mitigation: start with rule-based logic and postpone GPU work.
- [Dataset sparsity] → Mitigation: use a small but representative sample and validate label generation carefully.

## Migration Plan

- Implement the core modules in the existing repository structure.
- Verify each module with tests before tying them into the dashboard.
- Keep the design modular so later upgrades can add FinBERT or real-data ingestion without rewriting the pipeline.

## Open Questions

- Which real-data source will be used for the bonus dataset path?
- Which confidence metric will be used for the rule-based baseline and counterfactual comparison?
