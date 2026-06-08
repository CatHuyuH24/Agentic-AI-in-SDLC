## ADDED Requirements

### Requirement: Data ingestion and schema validation are deterministic

The system SHALL normalize raw price/news records into the canonical Week 1 schema and SHALL reject malformed records early without crashing the pipeline.

The canonical input model SHALL contain:

- `ticker` (string)
- `forecast_time` (timestamp string)
- `news` (array of records with `news_id`, `news_time`, `title`, `text`)
- `price_features` (object with `price_5d_return` and `volume_change_pct`)
- `label` (one of `UP`, `DOWN`, `HOLD`)

The canonical output model SHALL contain:

- `ticker`
- `forecast_time`
- `valid_news`
- `invalid_future_news`
- `warnings`

#### Scenario: Invalid input is handled safely

- **WHEN** a record is missing `ticker`, `forecast_time`, `news_time`, `news_text`, `price_5d_return`, or `volume_change_pct`
- **THEN** the loader SHALL mark the record invalid and log a warning
- **AND** the pipeline SHALL continue with the remaining valid records
- **AND** the output SHALL preserve the canonical `valid_news`, `invalid_future_news`, and `warnings` structure for downstream testing

### Requirement: Temporal filtering prevents future leakage

The system SHALL retain only news items whose publication time is strictly earlier than the forecast time, and SHALL classify all other items as invalid future news.

#### Scenario: Valid and invalid news are separated

- **WHEN** the forecast time is 2026-06-03 09:00:00 and a news item is published at 2026-06-02 16:30:00
- **THEN** the item SHALL be included in `valid_news`
- **AND WHEN** another item is published at 2026-06-03 09:05:00
- **THEN** that item SHALL be classified as `invalid_future_news`

### Requirement: The Week 1 pipeline is runnable and testable

The system SHALL expose a minimal end-to-end path that can be executed locally with the sample dataset and verified through `pytest`.

#### Scenario: Local execution produces stable output

- **WHEN** the sample dataset is loaded and the retriever runs
- **THEN** the system SHALL produce a deterministic result set and a warning summary
- **AND** the output SHALL be suitable for later evidence or forecasting modules

### Requirement: Review and reproducibility are part of the delivery path

The system SHALL support human review, reproducible local tests, and traceable acceptance notes before the prototype is considered complete.

#### Scenario: Verification is recorded for sign-off

- **WHEN** the prototype is validated locally with `pytest`
- **THEN** the result SHALL be documented in the OpenSpec task ledger for traceability and approval
