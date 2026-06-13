## ADDED Requirements

### Requirement: FinBERT Fusion Model Inference

The system SHALL provide a `FinBERTFusionModel` that accepts tokenized news headlines and numeric price features as input and returns a directional prediction (UP/DOWN/HOLD) with a softmax confidence score.

The model architecture SHALL:
- Use `ProsusAI/finbert` as the frozen text encoder backbone (768-dimensional CLS embedding).
- Concatenate the CLS embedding with a 2-dimensional price feature vector (`price_5d_return`, `volume_change_pct`).
- Pass the fused vector through a linear layer (`770 → 128`) with ReLU activation, then an output layer (`128 → 3`).
- Apply softmax to produce class probabilities for {UP, DOWN, HOLD}.

#### Scenario: Valid inference with checkpoint present

- **WHEN** `models/finbert_fusion.pt` exists and `forecast_from_news_finbert(news_items, price_features)` is called with at least one valid news item
- **THEN** the function SHALL return a dict with keys `prediction` (str), `confidence` (float in [0, 1]), `evidence_count` (int), and `evidence` (list)

#### Scenario: Graceful fallback when checkpoint is absent

- **WHEN** `models/finbert_fusion.pt` does not exist and `forecast_from_news_finbert()` is called
- **THEN** the system SHALL log a warning and transparently return the rule-based forecast result without raising an exception

#### Scenario: Output schema compatibility

- **WHEN** `forecast_from_news_finbert()` returns a result
- **THEN** the result dict MUST contain exactly the same top-level keys as `forecast_from_news()` so the faithfulness evaluator and dashboard can call either function interchangeably

---

### Requirement: Model Selection Switch

The system SHALL support runtime selection between the rule-based model and the FinBERT model via:
1. An environment variable `USE_FINBERT=1`.
2. An explicit `model` parameter passed to the forecast function (`"rule"` or `"finbert"`).
3. A sidebar toggle in the Streamlit dashboard.

The explicit parameter SHALL take precedence over the environment variable.

#### Scenario: Environment variable activates FinBERT globally

- **WHEN** `USE_FINBERT=1` is set in the environment and no explicit `model` parameter is passed
- **THEN** all calls to the unified `run_forecast()` dispatcher SHALL route to `forecast_from_news_finbert()`

#### Scenario: Explicit parameter overrides environment variable

- **WHEN** `run_forecast(news, price, model="rule")` is called regardless of `USE_FINBERT`
- **THEN** the rule-based model SHALL be used

#### Scenario: Dashboard toggle switches model at runtime

- **WHEN** the user selects "FinBERT" from the sidebar model toggle in the dashboard
- **THEN** all subsequent forecast calls for that session SHALL use the FinBERT model, and the KPI cards SHALL update to reflect the new predictions

---

### Requirement: Colab Training Notebook

The system SHALL include a reproducible Jupyter notebook (`notebooks/week4_finbert_training.ipynb`) that trains the FinBERT fusion model on Colab (T4 GPU) and exports a compatible checkpoint.

The notebook SHALL:
- Load `data/financial_corpus.csv` and split it 80/20 (train/val) with a fixed random seed.
- Tokenize all headline strings using `AutoTokenizer.from_pretrained("ProsusAI/finbert")` with `max_length=128`.
- Train for 5 epochs with Adam (`lr=2e-4`) and CrossEntropyLoss.
- Print validation accuracy and a confusion matrix after each epoch.
- Save the model state dict to `models/finbert_fusion.pt` and a label encoder to `models/label_encoder.pkl`.

#### Scenario: Notebook produces a valid checkpoint

- **WHEN** the notebook is run end-to-end on a Colab T4 instance
- **THEN** `models/finbert_fusion.pt` SHALL be a valid PyTorch state dict loadable by `FinBERTFusionModel.load_state_dict()`

#### Scenario: Notebook reports training metrics

- **WHEN** training completes
- **THEN** the notebook SHALL display final validation accuracy, a confusion matrix, and a comparison table of rule-based vs FinBERT accuracy on the validation set

---

### Requirement: Dashboard Model Comparison Panel

The Streamlit dashboard SHALL display a side-by-side comparison section when both model backends produce results for the same record.

#### Scenario: Side-by-side comparison is displayed

- **WHEN** FinBERT weights are available and the user selects a forecast record
- **THEN** the dashboard SHALL render a table showing rule-based prediction/confidence alongside FinBERT prediction/confidence for the selected record

#### Scenario: Comparison panel is hidden when checkpoint is absent

- **WHEN** `models/finbert_fusion.pt` does not exist
- **THEN** the dashboard SHALL display a dismissible info banner ("FinBERT checkpoint not found; showing rule-based results only") instead of the comparison panel

---

### Requirement: Batch Comparison Output

The system SHALL support generating a CSV file comparing both models across the full corpus via `python src/main.py --model both`.

#### Scenario: Batch run produces comparison CSV

- **WHEN** `python src/main.py --model both` is executed and `financial_corpus.csv` is present
- **THEN** `outputs/week4_comparison.csv` SHALL be written containing columns: `record_index`, `ticker`, `rule_prediction`, `rule_confidence`, `finbert_prediction`, `finbert_confidence`, `label`, `rule_correct`, `finbert_correct`

---

## MODIFIED Requirements

### Requirement: Forecasting model produces explainable predictions

The forecast module (`src/forecast_model.py`) SHALL expose a unified dispatcher function `run_forecast(news_items, price_features, model="rule")` that routes to either the rule-based or FinBERT backend and returns a dict with keys `prediction`, `confidence`, `evidence_count`, and `evidence`. The evidence list SHALL always be populated from the lexicon-based extractor regardless of which model backend is active, ensuring the faithfulness evaluator has explainable evidence terms to work with.

#### Scenario: Rule-based backend produces evidence terms

- **WHEN** `run_forecast(..., model="rule")` is called
- **THEN** the returned `evidence` list SHALL contain items with `direction`, `score`, `evidence_terms`, and `rationale` fields populated by the lexicon extractor

#### Scenario: FinBERT backend still provides lexicon evidence terms

- **WHEN** `run_forecast(..., model="finbert")` is called
- **THEN** the returned `evidence` list SHALL be identical in structure to the rule-based output — FinBERT only changes `prediction` and `confidence`, not the evidence attribution
