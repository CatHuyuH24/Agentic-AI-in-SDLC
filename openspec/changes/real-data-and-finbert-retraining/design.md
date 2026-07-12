## Context

The project currently runs exclusively on 38 simulated records in `data/sample_dataset.json`. The FinBERT fusion model in `models/finbert_fusion.pt` was trained on this synthetic corpus, so its predictions are indistinguishable from the rule-based baseline — `week4_comparison.csv` confirms identical outputs across all records. Two rubric bonus points (C1 + C2, +2.0 total) require a real dataset (≥ 300 rows, ≥ 3 tickers) and a GPU model demonstrably better than rule-based. The existing source modules (`loader.py`, `schema_adapter.py`, `forecast_model.py`) are designed with clean interfaces that can accommodate a CSV-based real corpus with minimal changes.

## Goals / Non-Goals

**Goals:**
- Produce `data/financial_corpus.csv` with ≥ 300 rows across AAPL, TSLA, NVDA using real price and news data.
- Retrain `FinBertFusionClassifier` on the real corpus and replace `models/finbert_fusion.pt`.
- Demonstrate measurable accuracy improvement of FinBERT vs. rule-based on a held-out validation split.
- Keep existing unit tests and `sample_dataset.json` intact (used by all current pytest fixtures).
- The new data pipeline and notebook must run end-to-end without manual intervention.

**Non-Goals:**
- Real-time data streaming or live market API integration.
- Deployment to any hosted environment.
- Rewriting or restructuring existing source modules beyond minimal schema alignment.
- Achieving a specific accuracy threshold (improvement over baseline is sufficient for C2).

## Decisions

### D1 — News Data Source: FinancialPhraseBank + Kaggle FNSPID

**Decision:** Use FinancialPhraseBank (Malo et al., via HuggingFace `datasets`) as the primary news source, supplemented by Kaggle FNSPID financial news headlines if additional volume is needed.

**Rationale:** FinancialPhraseBank is a verified, pre-labeled financial sentiment dataset compatible with the HuggingFace `datasets` library — no scraping or API key required. It provides polarity labels (positive/negative/neutral) that map directly to the UP/DOWN/HOLD schema. FNSPID adds volume when ticker-specific coverage is thin.

**Alternatives considered:**
- *Yahoo Finance news scraper*: Fragile, violates ToS, rate-limited.
- *Reuters/Bloomberg*: Requires paid API access.
- *Alpha Vantage news*: Free tier limits 25 calls/day — insufficient for 300+ records.

---

### D2 — Price Data: yfinance

**Decision:** Use the `yfinance` Python library to download daily OHLCV data for AAPL, TSLA, NVDA covering a 2-year window (2023-01-01 to 2024-12-31).

**Rationale:** `yfinance` is stable, free, well-documented, and already listed in project dependencies. Next-day return labeling (`ΔP > 0.005 → UP`, `< -0.005 → DOWN`, else `HOLD`) is deterministic from close prices.

**Alternatives considered:**
- *Stooq / Alpha Vantage*: Additional dependency with lower reliability.
- *Kaggle price datasets*: Manual download required; breaks reproducibility.

---

### D3 — Data Join Strategy: Date-Key Matching

**Decision:** Join news headlines to price dates using trading date as the key. A news headline published on date `D` is matched to the price record for date `D`; its label is derived from `close[D+1] / close[D] - 1`.

**Rationale:** Keeps temporal integrity — no future price information enters the news record. Matches the existing schema's `forecast_time` / `news_time` contract.

**Sequence diagram:**

```
yfinance API          FinancialPhraseBank
     |                        |
     | OHLCV(AAPL,TSLA,NVDA) | headlines + polarity
     v                        v
  price_df              news_df
     |                        |
     +--------JOIN(date)------+
                 |
           raw_corpus_df
                 |
         label_engine (ΔP rule)
                 |
       financial_corpus.csv (≥300 rows)
                 |
       loader.py (existing, unchanged)
```

---

### D4 — Retraining Approach: Colab Notebook, Frozen Backbone

**Decision:** Retrain using the same `FinBertFusionClassifier` architecture (frozen FinBERT backbone + fusion linear layer), 5 epochs, Adam lr=2e-4, in `notebooks/week6_finbert_retraining.ipynb`.

**Rationale:** Reusing the existing architecture avoids any breaking changes to `forecast_model.py`'s `FinBERTFusionModel` loader. Only the weights change. Frozen backbone keeps training time under 15 minutes on Colab T4.

**Alternatives considered:**
- *Full fine-tuning (unfrozen)*: Risk of overfitting on 300 rows; longer training time.
- *Switching to a different model (e.g., RoBERTa)*: Would require updating `forecast_model.py` loader significantly.

---

### D5 — Loader Extension: CSV Branch in `loader.py`

**Decision:** Add a `load_corpus_csv(path)` function to `src/loader.py` that reads `financial_corpus.csv` and converts rows into the existing internal dict schema. The `sample_dataset.json` loader path is preserved.

**Rationale:** Minimal-change principle. All existing pytest fixtures continue to use `sample_dataset.json`. The new CSV path is activated by `src/main.py` when `data/financial_corpus.csv` is present.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| FinancialPhraseBank sentences don't map 1:1 to tickers (AAPL/TSLA/NVDA) | Filter by ticker keyword presence in headline; accept general financial news if ticker-specific volume < 100 |
| yfinance rate limits on consecutive requests | Add `time.sleep(1)` between ticker requests; use `yfinance.download()` batch call |
| FinBERT still underperforms rule-based after retraining on 300 rows | 300 rows is minimal; document in report as a limitation. Even marginal improvement (+1-2%) satisfies C2 rubric. |
| Colab session expires mid-training | Checkpoint saved every epoch; notebook includes resume logic |
| `financial_corpus.csv` schema drift vs. existing `schema_adapter.py` | `fetch_real_data.py` outputs columns matching the adapter's expected keys exactly |

## Open Questions

- **Q1**: Should `financial_corpus.csv` use only ticker-specific headlines, or include general market/sector headlines for AAPL/TSLA/NVDA context? → Prefer ticker-specific first; pad with sector headlines if volume < 100/ticker.
- **Q2**: Train/validation split ratio? → 80/20 stratified by ticker and label, matching class distribution.
