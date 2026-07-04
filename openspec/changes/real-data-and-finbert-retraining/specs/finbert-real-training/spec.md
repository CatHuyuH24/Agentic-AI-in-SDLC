## ADDED Requirements

### Requirement: FinBERT retraining on real corpus
The system SHALL provide a reproducible Colab notebook (`notebooks/week6_finbert_retraining.ipynb`) that fine-tunes `FinBertFusionClassifier` on `data/financial_corpus.csv` for 5 epochs using Adam (lr=2e-4), exports updated weights to `models/finbert_fusion.pt`, and prints per-epoch validation accuracy.

#### Scenario: Notebook runs end-to-end without error
- **WHEN** `notebooks/week6_finbert_retraining.ipynb` is executed top-to-bottom in Colab T4
- **THEN** all cells complete without exceptions and `models/finbert_fusion.pt` is written

#### Scenario: Training uses only training split
- **GIVEN** a 80/20 stratified train/val split of `financial_corpus.csv`
- **WHEN** the training loop runs
- **THEN** validation data is never used to update model weights

---

### Requirement: Quantitative comparison against rule-based baseline
The system SHALL compute and display a comparison table showing rule-based accuracy vs. FinBERT accuracy on the held-out validation set, stored in `outputs/week4_comparison.csv` using the real corpus.

#### Scenario: FinBERT accuracy reported
- **WHEN** the notebook evaluation cell runs
- **THEN** it prints FinBERT validation accuracy, precision, recall, and F1 per class

#### Scenario: Rule-based baseline comparison shown
- **WHEN** the comparison table is generated
- **THEN** both rule-based and FinBERT predictions are evaluated on the same validation records and reported side-by-side

#### Scenario: Comparison CSV regenerated
- **WHEN** `python src/main.py --model both` is run with `financial_corpus.csv` present
- **THEN** `outputs/week4_comparison.csv` is overwritten with columns `record_index`, `ticker`, `rule_prediction`, `rule_confidence`, `finbert_prediction`, `finbert_confidence`, `label`, `rule_correct`, `finbert_correct`

---

### Requirement: Retrained checkpoint backward-compatible with forecast_model.py
The new `models/finbert_fusion.pt` SHALL be loadable by the existing `FinBERTFusionModel` class in `src/forecast_model.py` without any architecture changes.

#### Scenario: Checkpoint loads without error
- **WHEN** `FinBERTFusionModel.load()` is called with the new checkpoint path
- **THEN** the model loads successfully and `run_forecast(..., model="finbert")` returns a valid prediction dict

#### Scenario: Graceful fallback preserved
- **WHEN** `models/finbert_fusion.pt` is absent
- **THEN** `run_forecast()` falls back to rule-based and logs a warning, with no exception raised

---

## MODIFIED Requirements

### Requirement: Forecast dispatcher uses real corpus by default
The `run_forecast()` dispatcher in `src/forecast_model.py` SHALL prefer `data/financial_corpus.csv` over `data/sample_dataset.json` when the CSV file is present, while remaining backward-compatible with the JSON format for unit tests.

#### Scenario: CSV corpus used when present
- **GIVEN** `data/financial_corpus.csv` exists
- **WHEN** `src/main.py` is executed without `--data` flag
- **THEN** records are loaded from `financial_corpus.csv`

#### Scenario: JSON corpus used as fallback
- **GIVEN** `data/financial_corpus.csv` does not exist
- **WHEN** `src/main.py` is executed
- **THEN** records are loaded from `data/sample_dataset.json` and a warning is logged
