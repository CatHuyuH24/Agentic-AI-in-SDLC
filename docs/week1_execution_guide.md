# Week 1 Execution Guide: Faithful Evidence Forecasting

This guide is the working companion for the first implementation week of the project plan in `docs/project_plan.md`. It is designed for both members of the team and should be used together with the OpenSpec artifacts in `openspec/changes/faithful-evidence-forecasting/`.

## 1. Goal of Week 1

Week 1 is not the full forecasting system. It is the foundation phase that proves the project can:

1. ingest real or curated financial text and price inputs,
2. normalize and validate the data schema,
3. enforce strict temporal safety, and
4. produce a reproducible baseline for future evidence and faithfulness work.

The main success condition for Week 1 is: the system can separate valid pre-forecast news from invalid future-dated news, and the output schema is stable enough for the next implementation phases.

---

## 2. Explicit System Boundaries for Week 1

### In Scope

- A small prototype pipeline for AAPL, TSLA, and NVDA.
- Real or curated market records with price and news fields.
- A strict input schema with `ticker`, `forecast_time`, `news_time`, `news_text`, `price_5d_return`, `volume_change_pct`, and `label`.
- Temporal filtering that rejects any news item published at or after the forecast timestamp.
- A rule-based JSON adapter and initial retriever logic.
- A minimal test suite for temporal leakage and schema correctness.

### Out of Scope

- Full trading automation.
- Production-grade news ingestion pipelines.
- GPU training or FinBERT fine-tuning.
- Advanced faithfulness experiments beyond the baseline confidence-drop concept.
- Dashboard polish or full visual analytics.

---

## 3. User Personas and Expected Outcomes

### Persona A — Research and Spec Reviewer

Needs the system to be explainable, academically defensible, and easy to review.

Expected outcome:

- The spec clearly states what is included and excluded.
- The evidence extraction logic is understandable and reproducible.
- The temporal safety rule is explicit and testable.

### Persona B — Data and Integration Operator

Needs the system to be runnable, testable, and connected to real input data.

Expected outcome:

- The loader and schema adapter work with sample and real data.
- The retriever separates valid and invalid news correctly.
- The output can be used by the dashboard later without major rewrite.

### Persona C — Project Reviewer / Demo Audience

Needs a clear demonstration of the core idea: evidence should be faithful, not just plausible.

Expected outcome:

- The pipeline can show why a news item is accepted or rejected.
- The dashboard can highlight future-dated news warnings.
- The prototype is credible enough to justify the next implementation steps.

---

## 4. Edge Cases to Handle in Week 1

These are the minimum edge cases that must be considered before moving to Week 2:

1. Empty or malformed news text.
2. Missing timestamp fields or invalid date formats.
3. News published exactly at the forecast time (`news_time == forecast_time`).
4. Duplicate news entries with identical IDs or text.
5. Missing price features such as `price_5d_return` or `volume_change_pct`.
6. Labels that are not one of `UP`, `DOWN`, or `HOLD`.
7. Ticker values that are inconsistent or misspelled.
8. Future-dated records that must be flagged rather than silently accepted.

Rules for handling these cases:

- Reject malformed entries early.
- Log warnings rather than crashing the pipeline.
- Keep the accepted sample predictable for tests and demos.

---

## 5. Pre-processing Specifications (inspired by koa-fin/sn2)

The preprocessing stage should be simple, deterministic, and explainable.

### Step A — Text Normalization

- Convert text to lowercase.
- Remove extra whitespace and punctuation noise.
- Normalize currency symbols and market terms where practical.
- Keep the original title for traceability.

### Step B — Entity Preservation

- Preserve company names and major market terms.
- Standardize repeated variants of the same concept when possible.
- Keep a small alias map for common financial expressions such as `iphone_sales`, `tesla_earnings`, `ai_chip`, and similar domain words.

### Step C — Temporal Windowing

- For each forecast instance, treat `forecast_time` as the strict boundary.
- Only keep news where `news_time < forecast_time`.
- Flag any `news_time >= forecast_time` as invalid future news.
- Keep the temporal window explicit in the schema and test outputs.

### Step D — Schema Validation

- Ensure that each record contains the minimum fields required for downstream logic.
- Normalize timestamp strings to a consistent format.
- Convert numeric values to floats where applicable.

---

## 6. Week 1 Deliverables and Acceptance Criteria

### Deliverable 1 — OpenSpec package clarity

- The change package should clearly define MVP scope, risks, and Week 1 outputs.
- The spec should mention the temporal rule and the minimal dataset expectation.

### Deliverable 2 — Sample dataset

- At least 30 curated examples across AAPL, TSLA, and NVDA.
- Include both valid and invalid future-news cases.
- Ensure the dataset is small enough for fast local testing.

### Deliverable 3 — Data loader and schema adapter

- The loader should convert raw records into the common JSON schema.
- The adapter should preserve the original text and the cleaned text for evidence later.

### Deliverable 4 — Temporal retriever

- The retriever must split records into `valid_news` and `invalid_future_news`.
- The temporal rule must be deterministic and testable.

---

## 7. Step-by-Step Working Plan for Both Members

### Member A — Research, Specs, and NLP Direction

1. Review the current OpenSpec change package and confirm the Week 1 scope.
2. Update the spec text to explicitly mention:
   - system boundaries,
   - user personas,
   - edge cases,
   - temporal and preprocessing rules.
3. Prepare a small lexicon and rule list for the next evidence extraction stage.
4. Write or refine the acceptance criteria for the first dataset and retriever tests.
5. Record the human review note after each verification pass.

### Member B — Data, Pipeline, and Validation

1. Build the small sample dataset with valid and invalid examples.
2. Implement the loader and schema adapter for normalized records.
3. Implement the initial temporal retriever.
4. Run the first local tests using `pytest`.
5. Verify that the dashboard and output format can consume the generated JSON safely.

---

## 8. Joint Checklist

Use this checklist at the end of Week 1:

### Scope and requirements

- [ ] The MVP scope is clearly stated.
- [ ] The project boundaries are explicit and not overclaimed.
- [ ] The user personas are documented.
- [ ] The main edge cases are listed.

### Data and schema

- [ ] The dataset contains at least 30 records.
- [ ] The schema includes the required fields.
- [ ] The loader handles malformed or missing input safely.

### Temporal safety

- [ ] `news_time < forecast_time` is the only accepted path.
- [ ] `news_time >= forecast_time` is flagged as invalid future news.
- [ ] The retriever behavior is covered by tests.

### Documentation and traceability

- [ ] The OpenSpec proposal, design, spec, and tasks reflect the Week 1 scope.
- [ ] The human review note is recorded after verification.
- [ ] The team can explain what is ready for Week 2.

---

## 9. Recommended Working Order

1. Clarify scope and acceptance criteria.
2. Build the small sample dataset.
3. Implement the loader and schema adapter.
4. Implement the temporal retriever.
5. Run tests and record the evidence of validation.
6. Only then move to the next week’s model and dashboard work.

This guide should keep the project aligned with the main goal: build a faithful evidence-centric forecasting prototype, not a full financial trading system.
