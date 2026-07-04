# Proposal: Week 5 Advanced Faithfulness Expansion

## Status

Implemented and verified in the local repository as of 2026-07-04.

## Why

The current system already demonstrates a working end-to-end forecasting pipeline with temporal filtering, evidence extraction, rule-based forecasting, and counterfactual confidence-drop analysis. Week 5 extends that foundation toward the advanced rubric targets by making faithfulness analysis more explicit and more actionable for analysts.

The focus is not to replace the existing deterministic pipeline, but to strengthen it in three ways:

- add richer evidence diagnostics such as counterevidence coverage,
- add market consistency analysis that connects evidence polarity with observed price regime,
- and expand the dashboard and batch runner so these insights are visible and comparable in a single workflow.

This keeps the implementation aligned with the project plan and the course requirements while staying compatible with the existing Week 1–4 interfaces.

## What Changes

- Add advanced faithfulness metrics for counterevidence coverage and market consistency to the evaluation layer.
- Extend the batch pipeline outputs so the dashboard and reporting artifacts can inspect richer faithfulness diagnostics.
- Upgrade the Streamlit dashboard to show a compact advanced metrics panel and a more interpretable evidence summary.
- Create a week-based OpenSpec package for the work so it is ready for implementation and future extension.

## Capabilities

### New Capabilities

- Advanced evidence diagnostics: quantify whether a forecast contains both supporting and opposing evidence.
- Market regime analysis: classify each record as bull, bear, or sideways and measure the consistency between evidence direction and market movement.
- Richer reporting: batch outputs and dashboard views can surface the additional metrics for each record.

### Modified Capabilities

- Faithfulness evaluation remains backward-compatible, but now returns the additional advanced measures alongside the existing Week 3 outputs.
- The dashboard and CLI remain compatible with the existing rule-based and FinBERT backends.

## Impact

| Area                                          | Change                                                           |
| --------------------------------------------- | ---------------------------------------------------------------- |
| src/faithfulness_metrics.py                   | Add counterevidence coverage and market consistency metrics      |
| src/dashboard.py                              | Add advanced faithfulness summary cards and evidence diagnostics |
| src/main.py                                   | Write richer CSV/JSON outputs for week 5 analysis                |
| tests/                                        | Add regression tests for the new metrics                         |
| openspec/changes/week5-advanced-faithfulness/ | New week-based OpenSpec package                                  |
