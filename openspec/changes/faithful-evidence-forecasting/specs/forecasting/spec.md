# OpenSpec: Stock Forecasting & Faithfulness Specification

This document defines the functional requirements and acceptance criteria for the stock movement forecasting system.

---

## 1. Baseline Requirements (Week 1 & 2 - Verified)

### Requirement: Deterministic Ingestion & Schema Validation (Week 1)
The system SHALL normalize raw stock price and news records into a canonical schema. It SHALL reject malformed records early with warning messages while allowing the rest of the pipeline to continue.
*   **Canonical Input fields**: `ticker`, `forecast_time`, `news` (array of `news_id`, `news_time`, `title`, `text`), `price_features` (`price_5d_return`, `volume_change_pct`), `label`.
*   **Canonical Output fields**: `ticker`, `forecast_time`, `valid_news`, `invalid_future_news`, `warnings`.

#### Scenario: Malformed fields are warned and handled safely
*   **GIVEN** a raw dataset containing both valid and malformed stock/news records
*   **WHEN** the loader processes an input record containing missing fields, malformed timestamps, or invalid labels
*   **THEN** the loader SHALL log a warning and continue processing other valid data points
*   **AND** the output SHALL maintain the canonical format.

### Requirement: Temporal Filtering to Prevent Lookahead Leakage (Week 1)
The system SHALL filter news to ensure that only items published strictly before the forecast time are used in predictions. All future items must be flagged.

#### Scenario: Future news items are filtered out
*   **GIVEN** a forecast record with forecast_time `2026-06-03 09:00:00`
*   **WHEN** retriever processes news item A at `2026-06-02 16:30:00` and news item B at `2026-06-03 09:05:00`
*   **THEN** item A SHALL be placed in `valid_news`
*   **AND** item B SHALL be placed in `invalid_future_news` with a leakage warning.

### Requirement: Lexicon Evidence Extraction & Rule-Based Forecast Engine (Week 2)
The system SHALL extract evidence from the `valid_news` using a deterministic financial sentiment lexicon and execute a rule-based forecast prediction (UP/DOWN/HOLD) with confidence scores.

#### Scenario: Rule-based forecasting on valid news
*   **GIVEN** valid news items and price features
*   **WHEN** the valid news contains sentiment keywords (e.g., "surge", "weak")
*   **THEN** the evidence extractor SHALL output directional scores (UP/DOWN/HOLD)
*   **AND** the model SHALL combine these with price features to yield a forecast prediction and confidence score (between 0.50 and 0.95).

---

## 2. Faithfulness & Visualization Requirements (Week 3 - Verified)

### Requirement: Base Faithfulness Metrics Calculation
The system SHALL evaluate the faithfulness of its explanations by calculating three metrics:
1.  **Temporal Validity**: Ratio of valid news items to total news items.
    $$\text{Temporal Validity} = \frac{|\text{valid\_news}|}{|\text{valid\_news}| + |\text{invalid\_future\_news}|}$$
2.  **Evidence Support**: Average score of evidence items matching the predicted market direction.
3.  **Confidence Drop**: The reduction in prediction confidence when the cited evidence is masked or removed from the model's input text (counterfactual perturbation).

#### Scenario: Confidence Drop calculation on evidence removal
*   **GIVEN** a forecast prediction is made on full input texts with confidence $C_{\text{orig}}$ (e.g., $0.80$)
*   **WHEN** the cited evidence text is removed/perturbed to a neutral state by masking sentiment keywords with "note"
*   **THEN** the system SHALL re-calculate the model confidence $C_{\text{pert}}$ on the perturbed input
*   **AND** the confidence drop metric SHALL be calculated as:
    $$\text{Confidence Drop} = \begin{cases} C_{\text{orig}} - C_{\text{pert}} & \text{if perturbed prediction matches original} \\ C_{\text{orig}} & \text{if prediction changes} \end{cases}$$

### Requirement: Streamlit Visualization Dashboard MVP
The system SHALL provide an interactive Streamlit-based dashboard to display predictions, warnings, and evidence faithfulness.

#### Scenario: Interactive analysis on the dashboard
*   **GIVEN** a financial analyst launches the Streamlit dashboard
*   **WHEN** the analyst selects a specific ticker (AAPL, TSLA, NVDA) and forecast record index
*   **THEN** the dashboard SHALL display:
    *   **Selected Ticker and Time**: Details of the current prediction context.
    *   **Prediction and Confidence**: The forecast direction (UP/DOWN/HOLD) and associated confidence score.
    *   **Evidence Table**: A table containing news titles, publication timestamps, polarities, and support scores.
    *   **Temporal Leakage Panel**: A clear alert panel listing all filtered `invalid_future_news` and data validation warnings.
    *   **Faithfulness Metrics**: Numerical display of Temporal Validity, Evidence Support, and Confidence Drop.
    *   **Confidence Drop Plot**: An interactive Plotly bar chart showing the comparison between original confidence and perturbed confidence (representing necessity of evidence).
