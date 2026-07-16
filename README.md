# Faithful Evidence-Centric Financial News Forecasting

> **Course:** Công nghệ mới (New Technologies)
> **Team:** 2 members | **Deadline:** 2026-07-14

A production-quality prototype that forecasts stock movement (UP / DOWN / HOLD) from financial news and then _verifies_ whether the cited evidence actually drove the prediction—distinguishing faithful explanations from post-hoc rationalization.

## Overview

The system combines:

- **Temporal Retriever** — strict news filter that prevents lookahead bias (future news → rejected)
- **Rule-Based Evidence Extractor** — lexicon-driven keyword matching to identify directional signals
- **Dual Forecast Model** — Rule-Based (net sentiment) + FinBERT Fusion (ProsusAI/finbert fine-tuned on 350 real records)
- **Faithfulness Evaluator** — counterfactual perturbation (confidence drop), counterevidence coverage, market regime classification, and market consistency scoring
- **Streamlit Interactive Dashboard** — live record exploration, model comparison, and corpus-level Plotly analytics

## Architecture

```
Financial News + Price Data (CSV / real-time)
              │
              ▼
   [loader.py + schema_adapter.py]
   Normalize records → unified JSON schema
              │
              ▼
   [retriever.py]  TemporalRetriever
   news_time < forecast_time  → valid_news ✓
   news_time ≥ forecast_time  → invalid_future_news 🚨
              │
              ▼
   [evidence_extractor.py]  RuleBasedEvidenceExtractor
   Lexicon matching → polarity + support_score
              │
              ▼
   [forecast_model.py]  Dual-Model Dispatcher
   ├── Rule-Based:  Net Sentiment Score → UP / DOWN / HOLD
   └── FinBERT:     BERT-CLS + price_features → softmax (UP/DOWN/HOLD)
              │
              ▼
   [faithfulness_metrics.py]  FaithfulnessEvaluator
   ├── Evidence Support & Temporal Validity
   ├── Confidence Drop  (counterfactual perturbation)
   ├── Counterevidence Coverage
   └── Market Regime + Market Consistency
              │
              ▼
   [dashboard.py]  Streamlit + Plotly
   Interactive record explorer + corpus-level analytics
```

## Requirements

- **Python:** 3.10 or higher
- **GPU (optional):** CUDA-compatible GPU for FinBERT inference acceleration
- **FinBERT checkpoint:** `models/finbert_fusion.pt` (~418 MB) — placed at project root after training on Google Colab T4

### Dependency files

| File                   | Purpose                                             |
| ---------------------- | --------------------------------------------------- |
| `requirements.txt`     | CPU-only: core pipeline, Streamlit, Plotly, kaleido |
| `requirements-gpu.txt` | GPU: adds CUDA-enabled PyTorch + transformers       |

## Setup

**First, go to https://www.alphavantage.co/support/#api-key to claim your API then put it in `.env` file next to `.env.example`**

### Fetch data

Run the script to fetch price and news data. Update the date in the script if needed (currently from "1/1/2023" to "31/12/2025").

```bash
python data/scripts/fetch_real_data.py
```

### CPU (recommended for quick start)

```bash
git clone <repo-url>
cd <project-dir>
pip install -r requirements.txt
```

### GPU (for FinBERT inference)

```bash
pip install -r requirements-gpu.txt
```

### Create FinBERT checkpoint

Run `notebooks\week6_finbert_retraining.ipynb` to train FinBERT model
Output: `models/finbert_fusion.pt`

## Running

### Full pipeline (batch evaluation over all records)

```bash
# Both
python src/main.py

# FinBERT mode
python src/main.py --model finbert

# Rule mode
python src/main.py --model rule
```

Outputs: `outputs/faithfulness_results.csv`, `outputs/comparison.csv`

### Interactive dashboard

```bash
streamlit run src/dashboard.py
```

Opens at `http://localhost:8501`. Select ticker and record from the sidebar.

### Export output figures (4 PNG files → `outputs/figures/`)

```bash
python scripts/export_figures.py
```

Requires `outputs/faithfulness_results.csv` (run `main.py` first). Needs `kaleido==0.2.1`.

### Run all tests

```bash
pytest tests/
```

46+ tests across temporal retriever, evidence extractor, faithfulness metrics, and model dispatcher.

## Project Structure

```
Agentic-AI-in-SDLC/
│
├── README.md                          ← This file
├── report.pdf                         ← 5–8 page academic report
├── requirements.txt                   ← CPU dependencies
├── requirements-gpu.txt               ← GPU dependencies (PyTorch + transformers)
│
├── data/
│   └── financial_corpus.csv           ← Real corpus: 350 rows, AAPL/TSLA/NVDA
│
├── src/
│   ├── __init__.py
│   ├── loader.py                      ← CSV loader + corpus normalization
│   ├── schema_adapter.py              ← Raw row → unified JSON schema
│   ├── retriever.py                   ← TemporalRetriever (strict news filter)
│   ├── evidence_extractor.py          ← RuleBasedEvidenceExtractor (lexicon)
│   ├── forecast_model.py              ← Rule-Based + FinBERT Fusion dispatcher
│   ├── faithfulness_metrics.py        ← Counterfactual + advanced metrics
│   ├── main.py                        ← Batch pipeline entrypoint
│   └── dashboard.py                   ← Streamlit app + Plotly figure helpers
│
├── tests/
│   ├── test_temporal_retriever.py     ← Temporal leakage unit tests
│   ├── test_metrics.py                ← Faithfulness metric unit tests
│   └── ...                            ← Additional test modules
│
├── scripts/
│   ├── export_figures.py              ← Headless PNG export (kaleido 0.2.1)
│   └── verify_week1.py                ← Week 1 verification helper
│
├── models/
│   └── finbert_fusion.pt              ← FinBERT checkpoint (~418 MB, Git LFS)
│
├── outputs/
│   ├── faithfulness_results.csv       ← Batch faithfulness evaluation results
│   ├── week4_comparison.csv           ← Rule-Based vs FinBERT comparison (350 rows)
│   ├── week3_pipeline_output.json     ← Week 3 full pipeline JSON output
│   └── figures/
│       ├── prediction_distribution.png
│       ├── confidence_drop.png
│       ├── temporal_leakage_warning.png
│       └── faithfulness_radar.png
│
├── docs/
│   ├── report.md                      ← Report source (Markdown)
│   ├── project_plan.md                ← Full 6-week project plan
│   └── Do_an_cuoi_ki_Agentic_AI.md   ← Assignment specification (Vietnamese)
│
└── openspec/
    ├── config.yaml
    └── changes/
        ├── faithful-evidence-forecasting/   ← Change 1: Core pipeline
        │   ├── proposal.md
        │   ├── design.md
        │   ├── tasks.md
        │   └── specs/
        ├── finbert-fusion-model/            ← Change 2: FinBERT + GPU
        │   ├── proposal.md
        │   ├── design.md
        │   ├── tasks.md
        │   └── specs/
        ├── week5-advanced-faithfulness/     ← Change 3: Week 5 advanced metrics
        │   ├── proposal.md
        │   ├── design.md
        │   ├── tasks.md
        │   └── specs/
        └── final-deliverables/             ← Change 4: Report, figures, README
            ├── proposal.md
            ├── design.md
            ├── tasks.md
            └── specs/
```

## Results Summary

| Model                             | Accuracy | Avg Confidence Drop        | Device |
| --------------------------------- | -------- | -------------------------- | ------ |
| Rule-Based (Net Sentiment)        | ~16%     | 0.00 (lexicon-sparse data) | CPU    |
| FinBERT Fusion (ProsusAI/finbert) | ~44%     | N/A (batch eval)           | GPU T4 |

**Faithful predictions:** ~33% of evaluated records had a confidence drop > 0.10 (evidence was causally necessary).

## OpenSpec & Agentic SDLC

This project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec/) for spec-driven development. Every implementation change is documented with `proposal.md` → `design.md` → `spec.md` → `tasks.md`. AI agents (Antigravity/Gemini) contributed at every SDLC phase; human quality gates prevented unreviewed code from being merged.

See `openspec/changes/` for full documentation of all four development changes.
