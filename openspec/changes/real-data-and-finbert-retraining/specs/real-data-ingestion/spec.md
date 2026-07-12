## ADDED Requirements

### Requirement: Automated real price data download
The system SHALL download daily OHLCV price data for AAPL, TSLA, and NVDA using `yfinance` for the period 2023-01-01 to 2024-12-31 and compute next-day return labels (UP/DOWN/HOLD) using the threshold ±0.5%.

#### Scenario: Price data downloaded successfully
- **WHEN** `scripts/fetch_real_data.py` is executed with no arguments
- **THEN** the script downloads OHLCV data for all three tickers and writes intermediate price CSVs without raising exceptions

#### Scenario: Labels assigned correctly
- **GIVEN** a next-day return of +0.008 (> 0.005)
- **WHEN** the labeling function is applied
- **THEN** the record receives label `UP`

#### Scenario: Labels assigned for DOWN
- **GIVEN** a next-day return of -0.007 (< -0.005)
- **WHEN** the labeling function is applied
- **THEN** the record receives label `DOWN`

#### Scenario: Labels assigned for HOLD
- **GIVEN** a next-day return of +0.003 (within ±0.005)
- **WHEN** the labeling function is applied
- **THEN** the record receives label `HOLD`

---

### Requirement: Real news data integration
The system SHALL load financial news headlines from FinancialPhraseBank (via HuggingFace `datasets`) and filter to headlines containing AAPL, TSLA, NVDA tickers or their company name variants.

#### Scenario: News headlines loaded and filtered
- **WHEN** the news ingestion step runs
- **THEN** only headlines containing at least one ticker keyword (e.g., "Apple", "Tesla", "NVIDIA", "AAPL", "TSLA", "NVDA") are retained

#### Scenario: News polarity mapped to direction
- **GIVEN** a headline with FinancialPhraseBank polarity `negative`
- **WHEN** polarity is mapped to expected_direction
- **THEN** `expected_direction` is set to `DOWN`

---

### Requirement: Unified corpus output
The system SHALL produce `data/financial_corpus.csv` with ≥ 300 rows covering all three tickers (≥ 80 rows per ticker), containing columns: `ticker`, `forecast_time`, `news_time`, `news_title`, `cleaned_text`, `price_5d_return`, `volume_change_pct`, `label`.

#### Scenario: Corpus meets minimum size
- **WHEN** `scripts/fetch_real_data.py` completes
- **THEN** `data/financial_corpus.csv` contains ≥ 300 rows

#### Scenario: All tickers represented
- **WHEN** `data/financial_corpus.csv` is loaded
- **THEN** records exist for AAPL, TSLA, and NVDA with ≥ 80 rows each

#### Scenario: No temporal leakage in corpus
- **GIVEN** any row in `financial_corpus.csv`
- **WHEN** `news_time` is compared to `forecast_time`
- **THEN** `news_time` is strictly before `forecast_time`

#### Scenario: Schema compatible with existing loader
- **WHEN** `src/loader.py` calls `load_corpus_csv("data/financial_corpus.csv")`
- **THEN** the returned records conform to the internal dict schema used by `retriever.py` and `evidence_extractor.py` without modification
