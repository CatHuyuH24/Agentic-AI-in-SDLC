# Proposal: FinBERT Fusion Model — Week 4

## Why

Weeks 1–3 established a fully deterministic, rule-based pipeline that demonstrates the core faithfulness framework. However, the rule-based forecast model relies on simple lexicon lookups that cannot capture nuanced financial language—sarcasm, negation, or contextually ambiguous terms. Week 4 introduces a **FinBERT-based deep learning model** fine-tuned on financial sentiment, fused with price trend features, to produce richer, more accurate predictions that remain explainable via the existing faithfulness metrics engine.

This aligns directly with the project rubric's **C2 bonus point** (GPU / advanced model) and sets the foundation for comparing rule-based and neural forecasting faithfulness side by side.

---

## What Changes

- **New Colab Training Notebook** (`notebooks/week4_finbert_training.ipynb`): Trains a `FinBertFusionClassifier` on the `data/financial_corpus.csv` dataset using Google Colab T4 GPU. Exports serialized weights to `models/finbert_fusion.pt` and a label encoder to `models/label_encoder.pkl`.
- **Model Checkpoint Integration** (`src/forecast_model.py`): Adds a `FinBERTFusionModel` class and a `forecast_from_news_finbert()` inference function that loads the serialized checkpoint and produces `{prediction, confidence, evidence}` outputs compatible with the current schema.
- **Model Switch Flag** (`src/forecast_model.py`): Adds a `USE_FINBERT` environment variable / function parameter so the dashboard and `main.py` can toggle between rule-based and FinBERT inference at runtime without breaking any downstream metric calculations.
- **Dashboard Enhancement** (`src/dashboard.py`): Adds a sidebar toggle ("Model: Rule-Based / FinBERT") and a comparison section showing side-by-side predictions from both models when FinBERT weights are available.
- **Updated Pipeline Runner** (`src/main.py`): Accepts a `--model` CLI flag (`rule` or `finbert`) so batch evaluation can be run on both model tiers and results compared in `outputs/`.
- **New Tests** (`tests/test_week4_finbert.py`): Unit tests covering weight loading, inference schema compatibility, and graceful fallback when the checkpoint is absent.
- **Updated OpenSpec Artifacts**: `design.md`, `specs/finbert-model/spec.md`, and `tasks.md` for this change.

---

## Capabilities

### New Capabilities

- `finbert-model`: FinBERT-based sequence classification fused with price features. Produces the same `{prediction, confidence, evidence}` output schema as the rule-based model. Enables the faithfulness evaluator and dashboard to operate unchanged regardless of which model backend is active.

### Modified Capabilities

- `forecasting`: The existing rule-based forecasting capability is extended with a runtime switch to select the FinBERT model. The output schema and faithfulness interface remain identical; only the confidence values and prediction distributions change.

---

## Impact

| Area | Change |
|---|---|
| `src/forecast_model.py` | Add `FinBERTFusionModel`, `forecast_from_news_finbert()`, model-switch logic |
| `src/dashboard.py` | Add model selector toggle, side-by-side comparison panel |
| `src/main.py` | Add `--model` CLI argument, dual-model batch evaluation |
| `notebooks/` | New `week4_finbert_training.ipynb` (Colab, T4 GPU) |
| `models/` | New directory: `finbert_fusion.pt`, `label_encoder.pkl` |
| `tests/` | New `test_week4_finbert.py` (unit + integration) |
| **Dependencies** | `torch`, `transformers`, `scikit-learn` (all already available in Colab; optional local install) |
| **Breaking changes** | None — all downstream consumers (faithfulness evaluator, dashboard) use the same output schema |
