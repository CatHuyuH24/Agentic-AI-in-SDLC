# Task Checklist: FinBERT Fusion Model — Week 4

## 1. Environment & Repository Setup

- [x] 1.1 Create `models/` directory with `.gitkeep`; add `models/*.pt` and `models/*.pkl` to `.gitignore`
- [x] 1.2 Create `requirements-gpu.txt` listing `torch`, `transformers`, `scikit-learn`, `accelerate` with pinned versions
- [x] 1.3 Create `notebooks/` directory structure and verify Colab can mount the project drive

## 2. FinBERT Fusion Model — Colab Training

- [x] 2.1 Copy `data/financial_corpus.csv` to Google Drive and mount in Colab session
- [x] 2.2 Implement `FinBERTDataset` PyTorch Dataset class: tokenize headlines (max_length=128) and concatenate price feature tensors
- [x] 2.3 Implement `FinBertFusionClassifier` nn.Module: frozen FinBERT backbone + fusion linear layer (770→128, ReLU) + output layer (128→3)
- [x] 2.4 Write training loop: Adam optimizer (lr=2e-4), CrossEntropyLoss, 5 epochs, batch size 16; print per-epoch val accuracy + loss
- [x] 2.5 Print final confusion matrix and comparison table (rule-based vs FinBERT accuracy on validation set)
- [x] 2.6 Export `models/finbert_fusion.pt` (state dict) and `models/label_encoder.pkl` from Colab; download and place in local `models/` directory
- [x] 2.7 Save the completed notebook as `notebooks/week4_finbert_training.ipynb`

## 3. Model Integration — `src/forecast_model.py`

- [x] 3.1 Implement `FinBERTFusionModel` class that mirrors the Colab architecture and can load state dict via `models/finbert_fusion.pt`
- [x] 3.2 Implement `forecast_from_news_finbert(news_items, price_features)` function: tokenize news, run model, map softmax output to `{prediction, confidence, evidence_count, evidence}`; evidence list sourced from existing lexicon extractor
- [x] 3.3 Implement `run_forecast(news_items, price_features, model="rule")` dispatcher that routes to either `forecast_from_news()` or `forecast_from_news_finbert()` based on the `model` parameter and `USE_FINBERT` env var
- [x] 3.4 Implement graceful fallback: if `models/finbert_fusion.pt` is absent and FinBERT is requested, log a warning and return rule-based result instead

## 4. Dashboard Enhancement — `src/dashboard.py`

- [x] 4.1 Add model selector radio button ("Rule-Based" / "FinBERT") to the sidebar
- [x] 4.2 Route forecast calls through `run_forecast(..., model=<selected>)` based on sidebar selection
- [x] 4.3 Add a "Model Comparison" section that shows a two-column table: rule-based prediction/confidence vs FinBERT prediction/confidence for the current record (visible only when checkpoint is present)
- [x] 4.4 Display an info banner ("FinBERT checkpoint not found; showing rule-based results only") when `models/finbert_fusion.pt` is absent

## 5. Batch Pipeline Runner — `src/main.py`

- [x] 5.1 Add `--model` CLI argument accepting `rule`, `finbert`, or `both`
- [x] 5.2 When `--model both` is used, run both model backends for each record and collect dual results
- [x] 5.3 Write `outputs/week4_comparison.csv` with columns: `record_index`, `ticker`, `rule_prediction`, `rule_confidence`, `finbert_prediction`, `finbert_confidence`, `label`, `rule_correct`, `finbert_correct`

## 6. Test Suite — `tests/test_week4_finbert.py`

- [x] 6.1 Write unit test: `forecast_from_news_finbert()` returns a dict with exactly the expected keys when checkpoint is present (use a tiny random-weight model for CI)
- [x] 6.2 Write unit test: graceful fallback — patch `models/finbert_fusion.pt` path to a non-existent file and assert rule-based result is returned without exception
- [x] 6.3 Write unit test: `run_forecast()` dispatcher routes correctly based on `model="rule"` and `model="finbert"` parameters
- [x] 6.4 Write unit test: `USE_FINBERT=1` env var activates FinBERT backend via `run_forecast()` when `model` parameter is not explicitly set
- [x] 6.5 Run `python -m pytest tests/test_week4_finbert.py -v` and confirm all tests pass

## 7. Verification & Human Sign-Off

- [x] 7.1 Run `python -m pytest tests/ -v` and confirm all previously passing tests still pass (no regressions)
- [x] 7.2 Run `python src/main.py --model both` and verify `outputs/week4_comparison.csv` is generated with correct schema
- [x] 7.3 Launch Streamlit dashboard and manually verify: model toggle works, comparison panel appears/hides correctly, KPI values update on model switch
- [x] 7.4 Append sign-off entries to the quality gates ledger:
  ```
  [TASK-4.0] [2026-06-13] [FinBERT Fusion — forecast_model.py] Approved by Member A → Checkpoint loaded, fallback verified, schema compatible.
  [TASK-4.1] [2026-06-13] [Dashboard Model Toggle] Approved by Member B → Toggle functional, comparison panel renders correctly.
  [TASK-4.2] [2026-06-13] [Week 4 Test Suite] Approved by Member B → 46/46 tests pass, no regressions.
  ```
