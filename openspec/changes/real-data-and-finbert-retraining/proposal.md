## Why

The current system runs entirely on 38 simulated records in `data/sample_dataset.json`. This blocks two rubric point sources: C1 (real data ≥ 300 rows, ≥ 3 tickers) and C2 (GPU/advanced model with measurable improvement over rule-based). The FinBERT checkpoint (`models/finbert_fusion.pt`) was trained on this same simulated data, causing it to produce outputs identical to the rule-based model — eliminating any academic value from the GPU training claim. Both gaps must be closed before the July 14 deadline to reach the target score of 9.75+.

## What Changes

- **New**: `scripts/fetch_real_data.py` — automated pipeline to download daily OHLCV price data via `yfinance` and load a verified financial news dataset (FinancialPhraseBank or Kaggle FNSPID) for AAPL, TSLA, NVDA; produces `data/financial_corpus.csv` with ≥ 300 labeled rows.
- **New**: `notebooks/week6_finbert_retraining.ipynb` — Colab-ready retraining notebook that fine-tunes FinBERT on the real corpus, evaluates it against the rule-based baseline, and exports updated model weights.
- **Replace**: `models/finbert_fusion.pt` — overwritten with a checkpoint trained on real financial data.
- **Modify**: `outputs/week4_comparison.csv` — re-generated using the real dataset and new checkpoint to show accurate rule-based vs. FinBERT comparison.
- **Modify**: `data/` — `financial_corpus.csv` replaces the role of `sample_dataset.json` as the primary dataset; existing sample file is retained for unit tests.

## Capabilities

### New Capabilities

- `real-data-ingestion`: Fetches real equity prices (yfinance) and financial news headlines, applies temporal labeling (UP/DOWN/HOLD via next-day return threshold), and outputs a unified `financial_corpus.csv` schema compatible with the existing loader/retriever pipeline.
- `finbert-real-training`: Fine-tunes the FinBERT fusion classifier on the real corpus inside Google Colab (T4 GPU), produces a new checkpoint, and generates a quantitative comparison table demonstrating accuracy improvement over the rule-based baseline.

### Modified Capabilities

- `forecasting`: The `run_forecast()` dispatcher and `forecast_model.py` are updated to load the retrained checkpoint and run against the real dataset by default when `financial_corpus.csv` is present.

## Impact

- **Data**: `data/financial_corpus.csv` (new, ≥ 300 rows); `data/sample_dataset.json` (retained for unit tests only)
- **Models**: `models/finbert_fusion.pt` and `models/label_encoder.pkl` replaced with real-data-trained artifacts
- **Code**: `src/forecast_model.py` (minor schema alignment); `src/loader.py` (add CSV loader branch); `scripts/fetch_real_data.py` (new)
- **Notebooks**: `notebooks/week6_finbert_retraining.ipynb` (new)
- **Outputs**: `outputs/week4_comparison.csv` regenerated; `outputs/faithfulness_results.csv` regenerated on real corpus
- **Dependencies**: `yfinance`, `pandas`, `datasets` (HuggingFace) or Kaggle CLI for news data
- **Rubric impact**: Closes C1 (+1.0 pt) and C2 (+1.0 pt) bonus points
