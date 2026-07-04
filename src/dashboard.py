"""Streamlit dashboard for visualizing stock movement forecasts and explanation faithfulness.

Week 4 additions:
- Model selector sidebar toggle (Rule-Based / FinBERT)
- Model Comparison panel (side-by-side rule vs FinBERT results)
- Info banner when FinBERT checkpoint is absent
"""

import os
import sys
from pathlib import Path

# Add the directory containing this script to python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from loader import load_dataset
from retriever import retrieve
from faithfulness_metrics import evaluate_faithfulness
from forecast_model import (
    forecast_from_news,
    forecast_from_news_finbert,
    run_forecast,
    _checkpoint_available,
)

_FINBERT_AVAILABLE = _checkpoint_available()


def _pred_emoji(pred: str) -> str:
    return {"UP": "🟢 UP", "DOWN": "🔴 DOWN"}.get(pred, "⚪ HOLD")


def main() -> None:
    # Set page configuration for wide layout and custom styling
    st.set_page_config(
        page_title="Stock Movement Forecast & Faithfulness",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Premium design custom CSS
    st.markdown("""
    <style>
        /* Metric styling */
        div[data-testid="stMetricValue"] {
            font-size: 28px;
            font-weight: 700;
        }
        /* Section dividers */
        .section-header {
            font-family: 'Inter', sans-serif;
            font-size: 22px;
            font-weight: 600;
            color: #1E293B;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        /* Accent alert container */
        .alert-container {
            background-color: #FEF2F2;
            border-left: 4px solid #EF4444;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
        }
        /* Comparison table styling */
        .compare-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 16px;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📈 Stock movement forecasting & explanation faithfulness dashboard")
    st.markdown("This interactive tool visualizes predictions, data warnings, extracted evidence, and mathematically rigorous faithfulness metrics for rule-based stock movement forecasting.")

    # Load dataset
    try:
        records = load_dataset()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    # Tickers list
    tickers = sorted(list(set(r.get("ticker", "") for r in records if r.get("ticker"))))

    # ── Sidebar controls ────────────────────────────────────────────────────
    st.sidebar.header("Controls")
    selected_ticker = st.sidebar.selectbox("Filter Ticker", ["All"] + tickers)

    # Week 4: Model selector
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Model Selection")
    model_options = ["Rule-Based", "FinBERT"]
    selected_model_label = st.sidebar.radio(
        "Forecast Model",
        model_options,
        index=0,
        help="FinBERT requires the trained checkpoint in models/finbert_fusion.pt",
    )
    selected_model = "rule" if selected_model_label == "Rule-Based" else "finbert"

    if not _FINBERT_AVAILABLE:
        st.sidebar.info("ℹ️ FinBERT checkpoint not found. FinBERT selections fall back to Rule-Based automatically.")

    # Filter records by ticker
    if selected_ticker == "All":
        filtered_records = records
    else:
        filtered_records = [r for r in records if r.get("ticker") == selected_ticker]

    if not filtered_records:
        st.sidebar.warning("No records found for selection.")
        st.stop()

    # Record selector
    record_options = [
        f"Index {r['_record_index']}: {r['ticker']} @ {r['forecast_time']}"
        for r in filtered_records
    ]
    selected_option = st.sidebar.selectbox("Select Forecast Record", record_options)
    selected_idx = record_options.index(selected_option)
    record = filtered_records[selected_idx]

    # ── Run Pipeline on the selected record ─────────────────────────────────
    retrieval = retrieve(record)
    price_features = record.get("price_features", {})

    # Use the selected model via dispatcher
    faith_result = evaluate_faithfulness(retrieval, price_features, model=selected_model)
    forecast = faith_result["forecast"]
    detail = faith_result["confidence_drop_detail"]

    # ── Week 4: FinBERT checkpoint banner ───────────────────────────────────
    if not _FINBERT_AVAILABLE:
        st.info(
            "ℹ️ **FinBERT checkpoint not found** — showing rule-based results only. "
            "Train the model via `notebooks/week4_finbert_training.ipynb` and place "
            "`models/finbert_fusion.pt` in the project root to enable FinBERT inference."
        )

    # ── KPI Columns ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Prediction Context & KPIs</div>', unsafe_allow_html=True)
    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        st.markdown(f"**Asset Ticker:** `{record.get('ticker')}`")
    with col_meta2:
        st.markdown(f"**Forecast Timestamp:** `{record.get('forecast_time')}`")
    with col_meta3:
        st.markdown(f"**Ground Truth Label:** `{record.get('label', 'N/A')}`")

    col1, col2, col3, col4, col5 = st.columns(5)

    pred = forecast["prediction"]
    with col1:
        st.metric("Forecast Direction", _pred_emoji(pred))
    with col2:
        st.metric("Prediction Confidence", f"{forecast['confidence']:.2%}")
    with col3:
        st.metric("Temporal Validity", f"{faith_result['temporal_validity']:.2%}")
    with col4:
        st.metric("Evidence Support", f"{faith_result['evidence_support']:.2%}")
    with col5:
        st.metric("Confidence Drop", f"{faith_result['confidence_drop']:.2%}")

    # Faithfulness banner
    is_faithful = detail["is_faithful"]
    if is_faithful:
        st.success("✅ **Faithful explanation**: The forecast prediction is supported by cited evidence, and removing evidence terms significantly drops confidence (or changes the direction prediction).")
    else:
        st.warning("⚠️ **Unfaithful explanation**: Removing evidence sentiment terms does not trigger a significant drop in confidence, meaning the prediction may be driven by price momentum rather than the news, or the news lacks influential tone.")

    # Temporal Leakage / Alerts Banner
    invalid_news = retrieval.get("invalid_future_news", [])
    if invalid_news:
        st.error(f"🚨 **Lookahead Temporal Leakage Detected!** ({len(invalid_news)} future-dated news items filtered)")
        leakage_df = pd.DataFrame([
            {
                "News ID": item.get("news_id"),
                "Title": item.get("title"),
                "Timestamp": item.get("news_time"),
                "Filtering Reason": item.get("reason")
            } for item in invalid_news
        ])
        st.dataframe(leakage_df, use_container_width=True)

    # ── Evidence Table ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">News Evidence Breakdown</div>', unsafe_allow_html=True)
    evidence_items = forecast.get("evidence", [])
    if evidence_items:
        evidence_data = []
        for item in evidence_items:
            evidence_data.append({
                "News ID": item.get("news_id"),
                "Title": item.get("title"),
                "Polarity": item.get("direction"),
                "Support Score": item.get("score"),
                "Positive Terms": ", ".join(item.get("evidence_terms", {}).get("positive", [])),
                "Negative Terms": ", ".join(item.get("evidence_terms", {}).get("negative", [])),
                "Rationale": item.get("rationale")
            })
        df_evidence = pd.DataFrame(evidence_data)
        st.dataframe(df_evidence, use_container_width=True)
    else:
        st.info("No valid news items were extracted as directional evidence.")

    # ── Week 4: Model Comparison Panel ──────────────────────────────────────
    st.markdown('<div class="section-header">🤖 Model Comparison: Rule-Based vs FinBERT</div>', unsafe_allow_html=True)

    if _FINBERT_AVAILABLE:
        valid_news = retrieval.get("valid_news", [])
        rb_result  = forecast_from_news(valid_news, price_features)
        fb_result  = forecast_from_news_finbert(valid_news, price_features)

        cmp_col1, cmp_col2 = st.columns(2)
        with cmp_col1:
            st.markdown("**Rule-Based Model**")
            rb_pred = rb_result["prediction"]
            st.metric("Prediction", _pred_emoji(rb_pred))
            st.metric("Confidence", f"{rb_result['confidence']:.2%}")

        with cmp_col2:
            st.markdown("**FinBERT Fusion Model**")
            fb_pred = fb_result["prediction"]
            st.metric("Prediction", _pred_emoji(fb_pred))
            st.metric("Confidence", f"{fb_result['confidence']:.2%}")

        # Agreement indicator
        if rb_pred == fb_pred:
            st.success(f"✅ Both models agree: **{rb_pred}**")
        else:
            st.warning(f"⚡ Models disagree — Rule-Based: **{rb_pred}** | FinBERT: **{fb_pred}**")

        # Comparison bar chart
        fig_cmp = go.Figure(data=[
            go.Bar(name="Rule-Based", x=["Rule-Based", "FinBERT"], y=[rb_result["confidence"], fb_result["confidence"]],
                   marker_color=["#6366F1", "#EC4899"], text=[f"{rb_result['confidence']:.2%}", f"{fb_result['confidence']:.2%}"],
                   textposition="auto")
        ])
        fig_cmp.update_layout(
            title="Confidence Comparison: Rule-Based vs FinBERT",
            yaxis_title="Confidence Score",
            yaxis_range=[0, 1.05],
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig_cmp, use_container_width=True)
    else:
        st.info(
            "ℹ️ **FinBERT checkpoint not found** — comparison panel unavailable. "
            "Run `notebooks/week4_finbert_training.ipynb` on Google Colab (T4) "
            "and place `models/finbert_fusion.pt` in the project root to enable this panel."
        )

    # ── Plotly counterfactual visualization ─────────────────────────────────
    st.markdown('<div class="section-header">Counterfactual Masking: Original vs. Perturbed Confidence</div>', unsafe_allow_html=True)
    col_chart, col_explain = st.columns([2, 1])

    with col_chart:
        orig_conf = detail["original_confidence"]
        pert_conf = detail["perturbed_confidence"]
        orig_pred = detail["original_prediction"]
        pert_pred = detail["perturbed_prediction"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Original Forecast", "Perturbed (Masked) Forecast"],
            y=[orig_conf, pert_conf],
            text=[f"{orig_pred} ({orig_conf:.2%})", f"{pert_pred} ({pert_conf:.2%})"],
            textposition="auto",
            marker_color=["#0EA5E9", "#F43F5E"],
            width=0.4
        ))
        fig.update_layout(
            title="Comparison of Model Confidence Scores",
            yaxis_title="Confidence Score",
            yaxis_range=[0, 1.05],
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_explain:
        st.markdown("### How confidence drop is computed")
        st.markdown(
            "Confidence Drop measures the **necessity** of the news sentiment for the forecast. "
            "We mask all positive and negative terms from the sentiment lexicon inside the news articles with a neutral word (`note`), "
            "and then re-run the forecast model."
        )
        st.markdown(f"**Original Prediction:** `{orig_pred}` (Confidence: `{orig_conf:.2%}`)")
        st.markdown(f"**Perturbed Prediction:** `{pert_pred}` (Confidence: `{pert_conf:.2%}`)")
        st.markdown(f"**Confidence Drop:** `{detail['confidence_drop']:.2%}`")
        st.markdown(f"**Prediction Changed?** `{'Yes' if orig_pred != pert_pred else 'No'}`")

    # Warnings logs
    warnings = retrieval.get("warnings", []) + record.get("warnings", [])
    if warnings:
        st.markdown('<div class="section-header">Data Quality & Validation Warnings</div>', unsafe_allow_html=True)
        for warn in set(warnings):
            st.warning(warn)


if __name__ == "__main__":
    main()
