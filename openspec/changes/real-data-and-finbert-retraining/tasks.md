# Task Checklist: Real Data Acquisition & FinBERT Retraining

## 1. Environment & Dependencies

- [x] 1.1 Add `yfinance`, `datasets` (HuggingFace), and `kaggle` (optional) to `requirements-gpu.txt` and a new `requirements.txt` or `requirements-dev.txt` if not already present.
- [x] 1.2 Verify `yfinance` can download AAPL, TSLA, NVDA OHLCV data by running a quick smoke test: `python -c "import yfinance as yf; print(yf.download('AAPL', period='5d'))"`.
- [x] 1.3 Verify HuggingFace `datasets` library is available: `python -c "from datasets import load_dataset; print('ok')"`.

## 2. Real Data Ingestion Script

- [x] 2.1 Create `scripts/fetch_real_data.py` with a `download_prices(tickers, start, end)` function that uses `yfinance.download()` and computes `price_5d_return`, `volume_change_pct`, and `label` (UP/DOWN/HOLD) per the ±0.005 threshold.
- [x] 2.2 Implement `load_news(tickers)` in the same script that loads FinancialPhraseBank via `load_dataset("financial_phrasebank", "sentences_allagree")` and filters to rows containing at least one ticker keyword (AAPL/Apple, TSLA/Tesla, NVDA/NVIDIA).
- [x] 2.3 Implement `map_polarity(polarity_label)` that maps `positive → UP`, `negative → DOWN`, `neutral → HOLD`.
- [x] 2.4 Implement `join_price_and_news(price_df, news_df)` that joins on trading date key, assigns `forecast_time` = market open (09:00) of the matched date, and `news_time` = publish time (default to previous day close if unknown).
- [x] 2.5 Implement `save_corpus(df, path)` that writes to `data/financial_corpus.csv` with exactly these columns: `ticker`, `forecast_time`, `news_time`, `news_title`, `cleaned_text`, `price_5d_return`, `volume_change_pct`, `label`.
- [x] 2.6 Run `python scripts/fetch_real_data.py` and verify `data/financial_corpus.csv` contains ≥ 300 rows covering all 3 tickers (≥ 80 each). Print summary stats to stdout.

## 3. Loader Extension

- [x] 3.1 Add `load_corpus_csv(path: str) -> List[Dict]` to `src/loader.py` that reads `financial_corpus.csv` and returns records in the same dict schema as `load_sample_dataset()` (keys: `ticker`, `forecast_time`, `news_data`, `price_features`, `ground_truth`).
- [x] 3.2 Update `src/main.py` to prefer `data/financial_corpus.csv` when present: if file exists, call `load_corpus_csv()`; otherwise fall back to `load_sample_dataset()` with a logged warning.
- [x] 3.3 Verify all existing pytest tests still pass after the loader change: `python -m pytest tests/ -v`.

## 4. Colab Retraining Notebook

- [x] 4.1 Create `notebooks/week6_finbert_retraining.ipynb` with cells: (a) install deps, (b) load & split `financial_corpus.csv` 80/20 stratified by ticker+label, (c) tokenize headlines with `AutoTokenizer("ProsusAI/finbert")`, (d) build `FinBERTDataset`, (e) instantiate `FinBertFusionClassifier` (frozen backbone), (f) train 5 epochs with Adam lr=2e-4, CrossEntropyLoss.
- [x] 4.2 Add evaluation cell: compute accuracy, precision, recall, F1 on validation set for both FinBERT and rule-based baseline; print comparison table.
- [x] 4.3 Add export cell: `torch.save(model.state_dict(), "models/finbert_fusion.pt")` and `pickle.dump(label_encoder, open("models/label_encoder.pkl", "wb"))`.
- [x] 4.4 Run the notebook end-to-end in Colab T4; confirm all cells complete without exception.
- [x] 4.5 Download updated `models/finbert_fusion.pt` and `models/label_encoder.pkl` from Colab and place in local `models/` directory.

## 5. Integration Verification

- [x] 5.1 Run `python src/main.py --model both` with `financial_corpus.csv` present and confirm `outputs/week4_comparison.csv` is regenerated with real-data predictions.
- [x] 5.2 Confirm FinBERT and rule-based columns in `week4_comparison.csv` show distinct prediction distributions (not identical outputs as before).
- [x] 5.3 Run the full pytest suite: `python -m pytest tests/ -v` and confirm all previously passing tests still pass.
- [x] 5.4 Launch Streamlit dashboard (`streamlit run src/dashboard.py`) and manually verify: (a) dataset loads from `financial_corpus.csv`, (b) model toggle works, (c) faithfulness metrics display correctly.

## 6. Human Sign-Off & Quality Gate

- [x] 6.1 Inspect `data/financial_corpus.csv`: confirm ≥ 300 rows, no null `label` values, no temporal leakage (`news_time < forecast_time` for all rows).
- [x] 6.2 Review the comparison table in the notebook output and confirm FinBERT achieves at least marginally higher accuracy than rule-based on the validation set.
- [x] 6.3 Append sign-off entries to the quality gates ledger:
  ```
  [TASK-C1.0] [2026-07-04] [Real Data Ingestion — fetch_real_data.py] Approved by Member B → financial_corpus.csv ≥ 300 rows, 3 tickers, no leakage.
  [TASK-C2.0] [2026-07-04] [FinBERT Retraining — week6_finbert_retraining.ipynb] Approved by Member A → checkpoint trained, FinBERT > rule-based accuracy on val set.
  [TASK-C2.1] [2026-07-04] [Integration — main.py + dashboard] Approved by Member B → comparison CSV updated, dashboard functional.
  ```
