# Architecture Overview — Faithful Evidence-Centric Financial News Forecasting

> **Scope:** Single authoritative document describing the complete system architecture, component interactions, communication patterns, fault isolation, technical decisions, limitations, and future direction.

---

## 1. System Goal

This system answers the central research question:

> *When a model predicts stock movement from news, does the cited evidence actually drive the prediction — or is it post-hoc rationalization?*

It combines **real-world data ingestion**, **temporal integrity enforcement**, **rule-based and neural forecast models**, and a **faithfulness evaluation suite** into a single end-to-end pipeline. The architecture was shaped by three hard constraints:

1. No future data may ever reach a forecast model (strict temporal gate).
2. Every prediction must be explainable via extractable lexicon evidence.
3. The system must quantify *how much* the cited evidence actually drives the prediction.

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     REAL-WORLD DATA SOURCES                     │
│   Yahoo Finance (yfinance)          Alpha Vantage News API       │
│   AAPL, TSLA, NVDA prices           NEWS_SENTIMENT endpoint      │
│   2023-01-01 → 2025-12-31           time_from / time_to params   │
└───────────────┬────────────────────────────┬────────────────────┘
                │                            │
                ▼                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                scripts/fetch_real_data.py                        │
│  download_prices() → label by next_day_return (±0.5% threshold) │
│  load_news()       → parse Alpha Vantage JSON feed               │
│  align_news_to_prices() → temporal join: news_time < forecast   │
│  save_corpus()     → data/financial_corpus.csv                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │  data/financial_corpus.csv
                                │  (350+ rows: ticker, forecast_time,
                                │   news_time, text, price_features, label)
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    src/loader.py                                  │
│  load_corpus_csv()  → groups by (ticker, forecast_time, label)  │
│  load_dataset()     → parses data/sample_dataset.json           │
│  Each record → schema_adapter.normalize_record()                │
└───────────────────────────────┬──────────────────────────────────┘
                                │  List[Dict] — normalized records
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                  src/schema_adapter.py                            │
│  normalize_record() — validates required fields, parses          │
│  timestamps (YYYY-MM-DD HH:MM:SS), cleans text (lowercase,       │
│  regex strip), attaches _forecast_dt for retriever               │
└───────────────────────────────┬──────────────────────────────────┘
                                │  Validated record dict
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                   src/retriever.py — TemporalRetriever            │
│  for each news_item:                                             │
│    if news_time < forecast_time  → valid_news[]      ✓          │
│    if news_time ≥ forecast_time  → invalid_future_news[] 🚨     │
│  7-day look-back window applied at align step (fetch_real_data)  │
└───────────┬───────────────────────────┬──────────────────────────┘
            │ valid_news                │ invalid_future_news
            ▼                           ▼ (captured, not discarded)
┌──────────────────────────────────────────────────────────────────┐
│              src/evidence_extractor.py                            │
│  extract_evidence(valid_news)                                    │
│  POSITIVE_TERMS lexicon (15 terms): surge, beat, growth ...     │
│  NEGATIVE_TERMS lexicon (15 terms): weak, miss, decline ...     │
│  For each news item:                                             │
│    tokenize cleaned_text → match lexicon → count hits            │
│    if pos_hits > neg_hits → direction=UP, score=f(hits)          │
│    if neg_hits > pos_hits → direction=DOWN                       │
│    else                   → direction=HOLD                       │
└───────────────────────────────┬──────────────────────────────────┘
                                │  evidence[] — per-news polarity
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│               src/forecast_model.py — Dual Dispatcher            │
│                                                                  │
│  ┌─────────────────────────────┐  ┌────────────────────────────┐ │
│  │   Rule-Based Model          │  │  FinBERT Fusion Model       │ │
│  │  forecast_from_news()       │  │  forecast_from_news_finbert │ │
│  │                             │  │                             │ │
│  │  net = Σ(up_scores)         │  │  ProsusAI/finbert CLS(768) │ │
│  │      - Σ(down_scores)       │  │  || price_features(2)       │ │
│  │  + price_5d_return boost    │  │  → Linear(770→128)→ReLU    │ │
│  │  + volume_change boost      │  │  → Linear(128→3) → softmax │ │
│  │  → UP / DOWN / HOLD         │  │  → UP / DOWN / HOLD         │ │
│  │  confidence ∈ [0.50, 0.95] │  │  confidence = max(softmax)  │ │
│  └─────────────────────────────┘  └────────────────────────────┘ │
│                                                                  │
│  run_forecast(model="rule"|"finbert")  — unified dispatcher      │
│  Graceful fallback: if checkpoint missing → rule-based           │
└───────────────────────────────┬──────────────────────────────────┘
                                │  {prediction, confidence, evidence[]}
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│            src/faithfulness_metrics.py — FaithfulnessEvaluator   │
│                                                                  │
│  Metric 1: temporal_validity                                     │
│    = valid_count / (valid_count + invalid_count)                 │
│    1.0 = no leakage; 0.0 = all future news                       │
│                                                                  │
│  Metric 2: evidence_support                                      │
│    = count(evidence[i].direction == prediction) / len(evidence)  │
│                                                                  │
│  Metric 3: confidence_drop (counterfactual perturbation)         │
│    perturbed_news = mask all sentiment keywords → "note"         │
│    re-run forecast → get perturbed_confidence                    │
│    if prediction unchanged: drop = orig_conf - pert_conf         │
│    if prediction flipped:   drop = orig_conf (max signal)        │
│    is_faithful = drop > 0.10 OR prediction changed               │
│                                                                  │
│  Metric 4: counterevidence_coverage                              │
│    = 1.0 if evidence contains both supporting + opposing items   │
│    = 0.0 if all evidence points in one direction                 │
│                                                                  │
│  Metric 5: market_consistency + market_regime                    │
│    regime = "bull" | "bear" | "sideways" (from price/volume)    │
│    consistency = 1.0 if evidence aligns with regime, else 0.5   │
└───────────────────────────────┬──────────────────────────────────┘
                                │  faithfulness report dict
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                        src/main.py                               │
│  Orchestrates full batch pipeline:                               │
│  load → retrieve → extract → forecast → evaluate → write CSV/JSON│
│                                                                  │
│  Outputs:                                                        │
│    outputs/faithfulness_results.csv  (compact, per-record)       │
│    outputs/pipeline_output.json      (full nested record)        │
│    outputs/comparison.csv            (rule vs FinBERT side-by-side)│
└───────────────────────────────┬──────────────────────────────────┘
                                │  CSV / JSON artifacts
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│     src/dashboard.py — Streamlit + Plotly Interactive UI         │
│  Record explorer: ticker filter → record selector → full report  │
│  KPI cards: prediction, confidence, temporal_validity,           │
│             evidence_support, confidence_drop                    │
│  Counterfactual chart: original vs perturbed confidence bar      │
│  Model comparison: Rule-Based vs FinBERT side-by-side            │
│  Corpus analytics: prediction distribution, confidence drop,     │
│    temporal leakage warning, faithfulness radar (Plotly)         │
└──────────────────────────────────────────────────────────────────┘

scripts/export_figures.py — Headless PNG export (matplotlib)
  Reads outputs/faithfulness_results.csv → exports 4 PNG figures
  to outputs/figures/ for reports and documentation
```

---

## 3. Component Inventory

| Component | Primary File | Role | Stateful? |
|-----------|-------------|------|-----------|
| **Data Fetcher** | `scripts/fetch_real_data.py` | Live yfinance + Alpha Vantage ingestion, temporal alignment | No (offline script) |
| **Data Loader** | `src/loader.py` | CSV/JSON → normalized Python dicts | No |
| **Schema Adapter** | `src/schema_adapter.py` | Field validation, timestamp parsing, text cleaning | No |
| **Temporal Retriever** | `src/retriever.py` | Strict `news_time < forecast_time` gate | No |
| **Evidence Extractor** | `src/evidence_extractor.py` | Lexicon-based polarity + direction scoring | No |
| **Rule-Based Model** | `src/forecast_model.py` | Net sentiment score → UP/DOWN/HOLD | No |
| **FinBERT Fusion Model** | `src/forecast_model.py` | BERT CLS + price features → softmax | Yes (lazy singleton) |
| **Faithfulness Evaluator** | `src/faithfulness_metrics.py` | 5 faithfulness metrics via counterfactual | No |
| **Pipeline Orchestrator** | `src/main.py` | Batch end-to-end runner, output writer | No |
| **Dashboard** | `src/dashboard.py` | Interactive Streamlit exploration | Session-stateful |
| **Figure Exporter** | `scripts/export_figures.py` | Headless matplotlib PNG export | No |

---

## 4. Communication Flow — Data Path Step by Step

### 4.1 Offline Data Ingestion (one-time)

```
scripts/fetch_real_data.py
  │
  ├─ download_prices(["AAPL","TSLA","NVDA"], "2023-01-01", "2025-12-31")
  │     → yfinance.download() → raw OHLCV DataFrame
  │     → compute price_5d_return = pct_change(5)
  │     → compute volume_change_pct = pct_change(1)
  │     → compute next_day_return = Close.pct_change(1).shift(-1)
  │     → label: next_day_return > 0.005 → UP | < -0.005 → DOWN | else → HOLD
  │
  ├─ load_news(tickers, start="2023-01-01", end="2025-12-31")
  │     → Alpha Vantage NEWS_SENTIMENT API (time_from=YYYYMMDDTHHMM format)
  │     → for each article: parse time_published, title, summary, sentiment_label
  │     → map: Bullish→UP, Bearish→DOWN, else→HOLD
  │     → rate-limit: 2s sleep between tickers
  │
  └─ align_news_to_prices(price_df, news_df)
        → for each trading_date: forecast_time = date + 09:00 AM
        → prior_news = news where:
            news_time < forecast_time  (strict past)
          AND news_time >= forecast_time - 7 days  (7-day window)
        → takes latest matching news item per day
        → saves to data/financial_corpus.csv
```

### 4.2 Batch Pipeline (python src/main.py)

```
main.py
  │
  ├─ loader.load_corpus_csv("data/financial_corpus.csv")
  │     → groups by (ticker, forecast_time, price_5d_return, volume_change_pct, label)
  │     → each group → list of news dicts
  │     → each record → schema_adapter.normalize_record()
  │
  ├─ for each record:
  │     retriever.retrieve(record)
  │       → parse timestamps
  │       → for each news_item:
  │           news_time_dt < forecast_dt?
  │             YES → valid_news[]
  │             NO  → invalid_future_news[] + warning
  │
  │     faithfulness_metrics.evaluate_faithfulness(retrieval, price_features, model)
  │       → calculate_temporal_validity(len(valid_news), len(invalid_news))
  │       → forecast_model.run_forecast(valid_news, price_features, model)
  │           → evidence_extractor.extract_evidence(valid_news)
  │           → compute prediction + confidence
  │       → calculate_evidence_support(evidence, prediction)
  │       → calculate_counterevidence_coverage(evidence, prediction)
  │       → calculate_market_consistency(evidence, price_features)
  │       → calculate_confidence_drop(valid_news, price_features, model)
  │           → run_forecast(valid_news, ...)         → original
  │           → _mask_sentiment_terms(valid_news)     → neutral copy
  │           → run_forecast(perturbed_news, ...)     → perturbed
  │           → drop = orig_conf - pert_conf (or orig_conf if flipped)
  │           → is_faithful = drop > 0.10 OR prediction_changed
  │
  └─ write outputs/faithfulness_results.csv + pipeline_output.json
```

### 4.3 Interactive Dashboard (streamlit run src/dashboard.py)

```
dashboard.py
  │
  ├─ loads data/financial_corpus.csv → same path as main.py
  ├─ sidebar: select ticker, model (Rule/FinBERT), record index
  ├─ on selection:
  │     retriever.retrieve(record) → valid_news, invalid_future_news
  │     faithfulness_metrics.evaluate_faithfulness(retrieval, price_features, model)
  │     if FinBERT available: compare rule vs FinBERT side-by-side
  │
  └─ renders KPI metrics, evidence table, counterfactual chart,
     temporal leakage warning, and corpus-level Plotly figures
     (reads outputs/faithfulness_results.csv for corpus charts)
```

---

## 5. Component Interaction Matrix

| Caller | Callee | Data Passed | Return |
|--------|--------|-------------|--------|
| `main.py` | `loader.load_corpus_csv` | file path | `List[Dict]` records |
| `loader.py` | `schema_adapter.normalize_record` | raw dict + index | validated dict |
| `main.py` | `retriever.retrieve` | normalized record | `{valid_news, invalid_future_news, warnings}` |
| `main.py` | `faithfulness_metrics.evaluate_faithfulness` | retrieval + price_features + model | faithfulness report |
| `faithfulness_metrics` | `forecast_model.run_forecast` | valid_news + price_features | `{prediction, confidence, evidence[]}` |
| `forecast_model` | `evidence_extractor.extract_evidence` | news items | `evidence[]` |
| `faithfulness_metrics` | `faithfulness_metrics._mask_sentiment_terms` | news items | perturbed copy |
| `faithfulness_metrics` | `forecast_model.run_forecast` | perturbed news | perturbed forecast |
| `dashboard.py` | All above | record from sidebar | live faithfulness report |
| `export_figures.py` | `outputs/faithfulness_results.csv` | file read | 4 PNG files |

---

## 6. Fault Isolation & Failure Impact Analysis

### 6.1 Data Fetcher (`fetch_real_data.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| yfinance network error | No price data; script aborts | SSL bypass + retry logic; fallback to existing CSV |
| Alpha Vantage API key missing | RuntimeError: aborts cleanly | `.env` check at startup; clear error message |
| Alpha Vantage rate limit (25 req/day) | Partial news fetch | `time.sleep(2.0)` between tickers; warning printed |
| `time_from`/`time_to` format wrong | API returns error payload | `strftime("%Y%m%dT%H%M")` format enforced in code |

**Downstream impact:** If data fetcher fails, the pipeline falls back to `data/sample_dataset.json` (30 synthetic records). All other components are unaffected.

### 6.2 Schema Adapter (`schema_adapter.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| Missing `forecast_time` | Warning appended; record included with empty field | `warnings[]` list collects non-fatal issues |
| Invalid timestamp format | `_forecast_dt = None`; retriever skips that record | Temporal retriever adds skip warning |
| Empty news array | Warning; retrieve returns empty `valid_news` | Pipeline produces HOLD prediction with 0.5 confidence |

### 6.3 Temporal Retriever (`retriever.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| `_forecast_dt = None` | Cannot compare timestamps; all news skipped | Warning logged per news item; `valid_news = []` |
| All news is future-dated | `temporal_validity = 0.0`; `valid_news = []` | Faithfulness report flags `temporal_validity = 0.0`; dashboard shows leakage alert |
| News timestamps malformed | Item skipped | Per-item warning logged |

**Downstream impact:** If `valid_news = []`, the evidence extractor returns `[]`, the forecast defaults to HOLD at 0.5 confidence, and all faithfulness metrics collapse to 0.0. This is by design — the system clearly signals missing data rather than silently predicting.

### 6.4 Evidence Extractor (`evidence_extractor.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| No lexicon hits in any news | All evidence → HOLD, score = 0.55 | Graceful default; confidence drop will be ~0.0 |
| Lexicon misses domain-specific terms | Under-extraction of true sentiment | Acknowledged limitation; lexicon is manually curated |

**Downstream impact:** Low evidence coverage means confidence_drop ≈ 0.0, which correctly labels predictions as "potentially unfaithful" (driven by price features, not news sentiment).

### 6.5 Forecast Model (`forecast_model.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| `models/finbert_fusion.pt` missing | Warning emitted; falls back to rule-based | `_checkpoint_available()` checked before load |
| `torch`/`transformers` not installed | `ImportError` caught; falls back to rule-based | `_try_import_torch()` returns None cleanly |
| CUDA OOM | Exception caught; falls back to rule-based | `try/except` in `predict()` |
| FinBERT inference slow on CPU | High latency (~30s per record) | Warning in README; GPU recommended |

**Downstream impact:** Rule-based fallback is always available. The faithfulness evaluator continues working because it uses the lexicon evidence regardless of which model backend ran.

### 6.6 Faithfulness Evaluator (`faithfulness_metrics.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| `valid_news = []` | All metrics = 0.0 / 1.0 (vacuous) | Documented behavior; temporal_validity = 1.0 (no leakage = clean) |
| Counterfactual masking removes all text | Perturbed forecast defaults to HOLD | This is a valid signal: prediction was entirely evidence-driven |

### 6.7 Dashboard (`dashboard.py`)

| Failure Mode | Impact | Mitigation |
|---|---|---|
| `outputs/faithfulness_results.csv` missing | Corpus charts not shown; per-record view still works | `st.info()` message guides user |
| Streamlit crash | Web UI unavailable | CSV output remains; inspection via pandas/Excel |

**Key principle:** The dashboard is read-only and cosmetically independent. A dashboard failure never affects data integrity.

---

## 7. Architectural Decisions & Rationale

### 7.1 Why Strict Temporal Gate (not 7-day window in retriever)?

The 7-day window is enforced at **data creation time** (`align_news_to_prices`), not at retrieval time. The retriever enforces the **hard causal constraint**: `news_time < forecast_time`. This two-layer design ensures:

- The CSV corpus already contains only causally valid news-price pairs.
- The retriever acts as a **second-pass integrity check** that catches any edge cases where a news item somehow got through with a future timestamp.
- This makes the system safe even if the CSV is manually edited or extended.

### 7.2 Why Rule-Based Evidence, Even for FinBERT?

The `forecast_from_news_finbert()` function always computes lexicon evidence (from `extract_evidence()`), even when FinBERT produces the prediction. This is because:

- Faithfulness metrics require **explainable, token-level evidence** to perform counterfactual masking.
- FinBERT's internal attention weights are not exposed in this architecture.
- The lexicon provides a consistent, human-interpretable attribution layer regardless of model backend.

### 7.3 Why a Singleton for FinBERT?

`FinBERTFusionModel.get_instance()` uses the singleton pattern to avoid re-loading the 418MB checkpoint on every record. The model loads once on first call and is reused across the batch.

### 7.4 Why OpenSpec / Spec-Driven Development?

The project used [OpenSpec](https://github.com/Fission-AI/OpenSpec/) to enforce a structured SDLC:

- `proposal.md` → problem statement, motivation, scope
- `design.md` → technical design, schema, API contracts
- `spec.md` → precise input/output contracts, acceptance criteria
- `tasks.md` → concrete implementation checklist

This workflow ensured that AI agent contributions (code generation, test writing, documentation) were traceable and passed human quality gates before being accepted into the codebase.

---

## 8. Technical Challenges Solved

| Challenge | Problem Statement | Solution Implemented |
|---|---|---|
| **Temporal Leakage** | Future news contaminates predictions; metrics appear better than reality | Strict `news_time < forecast_time` comparison in `retriever.py`; 7-day lookback window in `align_news_to_prices()`; unit tests in `test_week1_pipeline.py` validate this gate |
| **Alpha Vantage API Format** | API requires `YYYYMMDDTHHMM` format, not `YYYY-MM-DD` | `strftime("%Y%m%dT%H%M")` conversion in `load_news()`; confirmed via prior debugging |
| **SSL Verification in Corporate/University Networks** | `yfinance` and `requests` fail with SSL errors | `HTTPAdapter.send` patched to disable SSL verification; `curl_cffi` also patched if available |
| **FinBERT Checkpoint Security (CVE-2025-32434)** | `torch.load()` without `weights_only=True` is unsafe | `weights_only=True` in `torch.load()`; `use_safetensors=True` for `AutoModel.from_pretrained()` |
| **Rate-Limiting (Alpha Vantage)** | 25 API calls/day on free tier | `time.sleep(2.0)` between tickers; per-ticker error handling |
| **Faithfulness vs. Accuracy** | Standard accuracy metrics don't measure explanation quality | 5 faithfulness metrics implemented: temporal_validity, evidence_support, confidence_drop, counterevidence_coverage, market_consistency |
| **Counterfactual Perturbation** | Must re-run model on masked news without changing other inputs | Deep copy of news items; keyword masking preserves structure; same model backend used for both passes |
| **GPU/CPU Portability** | FinBERT requires GPU but system must work on CPU | `_try_import_torch()` graceful import; `_checkpoint_available()` check; auto-fallback to rule-based model |

---

## 9. Limitations

| Limitation | Severity | Details |
|---|---|---|
| **Lexicon Sparsity** | Medium | Only 30 terms (15 positive + 15 negative). Financial news often uses domain jargon, numeric data, and hedged language not captured by the lexicon. This causes high HOLD rates and low confidence_drop for many records. |
| **Alpha Vantage Rate Limits** | Medium | Free tier: 25 API calls/day. Fetching all 3 tickers for the full date range requires multiple sessions. Real-world deployment would need a premium plan or alternative API. |
| **Dataset Scale** | Medium | ~350 rows across 3 tickers (AAPL, TSLA, NVDA). Statistical conclusions drawn from this corpus have high variance. FinBERT trained on 350 samples is underfitted for production use. |
| **Single News Item per Day** | Medium | `align_news_to_prices()` takes only the **latest** news before each forecast_time, not all news within the 7-day window. This means some relevant articles are silently dropped. |
| **Rule-Based Accuracy (~16%)** | High | The rule-based model has very low accuracy because the lexicon signal is sparse and market movements are noisy. This is expected for a pure rule-based approach. |
| **No True Causal Inference** | High | Confidence drop is a **correlation** metric, not a causal metric. A prediction can be faithful (high drop) while the news merely coincides with price movement, not causes it. |
| **FinBERT Checkpoint Dependency** | Low | The 418MB checkpoint is stored via Git LFS and must be downloaded separately. Without it, the system falls back to rule-based. |
| **No Streaming / Real-Time** | Low | The pipeline is batch-only. Live trading applications would require streaming news ingestion and incremental model updates. |

---

## 10. Future Development Directions

### Near-Term (1–3 months)
- **Expand the lexicon** with domain-specific financial terms (EBITDA, guidance, consensus, beat/miss by X%) using financial glossaries.
- **Include all news per window** instead of just the latest article — aggregate multiple news items per forecast day.
- **Add sufficiency test**: re-run forecast using only cited evidence (not all valid news) to test whether the subset alone is sufficient.

### Mid-Term (3–6 months)
- **Trained evidence extractor**: Replace rule-based lexicon with a fine-tuned NER or FinBERT-NLI classifier for higher-quality evidence extraction.
- **Incremental data pipeline**: Stream live news via Alpaca, Polygon.io, or Bloomberg API; update the corpus daily.
- **Causal inference metrics**: Use difference-in-differences or synthetic control methods to estimate the causal effect of specific news on price.

### Long-Term
- **Docker containerization**: Single `docker compose up` to launch the full pipeline + dashboard.
- **CI/CD**: GitHub Actions workflow to run the full test suite on every commit and automatically export figures.
- **Multi-modal fusion**: Combine news sentiment with technical indicators (RSI, MACD, Bollinger Bands) and macro-economic data (Fed rate decisions, CPI).
- **Production safeguards**: Differential privacy for training data, adversarial robustness testing, model monitoring dashboard.

---

## 11. Technology Stack Summary

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.10+ | Ecosystem dominance for ML/NLP/data science |
| Price Data | `yfinance` | Free, easy, covers AAPL/TSLA/NVDA historically |
| News Data | Alpha Vantage NEWS_SENTIMENT API | Structured JSON with timestamp, sentiment score, ticker |
| NLP Model | ProsusAI/finbert (HuggingFace) | Pre-trained on financial news; 768-dim BERT CLS |
| ML Framework | PyTorch + transformers | Standard for BERT fine-tuning |
| Dashboard | Streamlit + Plotly | Rapid interactive prototyping |
| Figure Export | matplotlib (headless Agg backend) | No browser needed; PNG for reports |
| Data Format | CSV (corpus) + JSON (sample) | Pandas-compatible; human-readable |
| Testing | pytest | Standard Python testing; 46+ tests |
| Spec/SDLC | OpenSpec | Structured proposal→design→spec→tasks workflow |
| Version Control | Git + Git LFS | LFS for 418MB FinBERT checkpoint |

---

*Document authored and maintained by the Agentic AI in SDLC project team. Last updated: 2026-07-13.*
