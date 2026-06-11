# OpenSpec Proposal: Stock Forecasting & Faithfulness

## Why

The baseline pipeline from Weeks 1 and 2 is fully in place (ingestion, temporal safety filtering, lexicons, rule-based forecasting). 
To make the system transparent and reliable, Week 3 implements **Explanation Faithfulness** metrics (measuring if predictions are genuinely driven by the evidence cited) and an **Interactive Streamlit Visualization Dashboard MVP** to easily analyze predictions, warnings, news evidence, and faithfulness metrics.

---

## What Changes

- Preserved the validated ingestion, temporal retriever, and lexicon forecasting components.
- Added a faithfulness evaluation engine (`src/faithfulness_metrics.py`) computing:
  - **Temporal Validity**: ratio of valid pre-forecast news to total news.
  - **Evidence Support**: match score between evidence polarity and prediction direction.
  - **Confidence Drop**: impact on confidence when sentiment words are perturbed.
- Added an interactive Streamlit UI dashboard (`src/dashboard.py`) integrating the data loader, temporal retriever, forecast model, and faithfulness metrics.
- Added unit and integration tests under `tests/` verifying the correctness of metrics, perturbation logic, and the dashboard.
- Maintained a deterministic, local-run, non-LLM implementation.

---

## Scope (Week 1, 2, and 3 - Verified)

### In Scope
- **Data Ingestion & Cleaning**: Normalizing stock data and news feeds safely.
- **Lookahead Filtering**: Isolating post-forecast news strictly to block leakage.
- **Lexicon Forecasting**: Sentiment extraction and rule-based prediction.
- **Faithfulness Metrics**: Mathematical formulations for temporal safety, support alignment, and counterfactual perturbation.
- **Streamlit Dashboard MVP**: A single-page interactive UI for ticker filtering, record selection, KPI cards, evidence tables, lookahead alerts, and a Plotly bar chart comparison of original vs perturbed confidence scores.
- **Test Coverage**: 36 unit/smoke tests verifying the whole system end-to-end.

### Out of Scope
- Production databases, live web scraping.
- Deep Learning (FinBERT) model training (deferred to Week 4).
- Production trading execution.

---

## Current Verified State

- Ingestion, retriever, lexicon, model, faithfulness metrics, and dashboard are fully functional.
- Local `pytest` suite runs and passes 36/36 tests successfully.
- Main entry point `python src/main.py` processes all 38 dataset records cleanly, outputting `outputs/week3_pipeline_output.json` (canonical JSON structure) and `outputs/faithfulness_results.csv` (CSV summary).
- The dashboard starts cleanly and allows selecting tickers and records dynamically.

---

## User Personas

- **Financial Analyst / Spec Reviewer**: Needs a transparent view of why the model predicted a direction and wants to verify if the cited evidence actually influenced the model's confidence.
- **Data & QA Engineer**: Needs to ensure future-dated news is rejected, warnings are raised for bad records, and metrics are calculated mathematically.

---

## Rules and Review Gates

- **Rule 1**: The temporal safety rule (`news_time < forecast_time`) remains the absolute firewall.
- **Rule 2**: Evidence and metrics calculations must use the outputs from retriever/model.
- **Rule 3**: All new metric calculation and dashboard integration must pass local tests.

---

## Canonical Data Structures

### Input model (canonical JSON)
```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00:00",
  "news": [
    {
      "news_id": "0001",
      "news_time": "2025-03-11 08:30:00",
      "title": "Apple reports weak iPhone sales in China",
      "text": "Apple reports weak iPhone sales in China after softer demand."
    }
  ],
  "price_features": {
    "price_5d_return": -0.02,
    "volume_change_pct": 0.15
  },
  "label": "DOWN"
}
```

### Output model (with Week 3 Faithfulness Metrics)
```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00:00",
  "prediction": "DOWN",
  "confidence": 0.72,
  "evidence": [
    {
      "news_id": "0001",
      "title": "Apple reports weak iPhone sales in China",
      "direction": "DOWN",
      "score": 0.73,
      "evidence_terms": {
        "positive": [],
        "negative": ["weak"]
      },
      "rationale": "negative terms"
    }
  ],
  "warnings": [],
  "faithfulness": {
    "temporal_validity": 1.0,
    "evidence_support": 1.0,
    "confidence_drop": 0.22,
    "is_faithful": true
  }
}
```

---

## Capabilities

### Completed Capabilities
- `faithfulness_evaluation`: Programmatic calculation of Evidence Support, Temporal Validity, and Confidence Drop (via masking).
- `dashboard`: Streamlit UI allowing interactive selection of assets, prediction display, leakage warnings, and Plotly visualization.
- `forecasting`: Updated output JSON to include the nested `faithfulness` metric results.
