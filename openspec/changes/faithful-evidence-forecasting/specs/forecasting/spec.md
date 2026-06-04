## ADDED Requirements

### Requirement: Temporal filtering prevents future leakage

The system SHALL retain only news items whose publication time is strictly earlier than the forecast time, and SHALL classify all other items as invalid future news.

#### Scenario: Valid and invalid news are separated

- **WHEN** the forecast time is 2026-06-03 09:00:00 and a news item is published at 2026-06-02 16:30:00
- **THEN** the item SHALL be included in valid_news
- **AND WHEN** another item is published at 2026-06-03 09:05:00
- **THEN** that item SHALL be classified as invalid_future_news

### Requirement: Evidence extraction produces interpretable fragments

The system SHALL extract one or more evidence fragments from news text, each with polarity and expected direction, so that the prediction can be explained.

#### Scenario: Evidence fragment is mapped to a market direction

- **WHEN** the text contains a phrase such as "weak iPhone sales in China"
- **THEN** the extractor SHALL return a fragment with a negative polarity and an expected direction of DOWN

### Requirement: Forecasting produces a direction and confidence score

The system SHALL generate an UP, DOWN, or HOLD prediction along with a confidence score for each forecast instance.

#### Scenario: Rule-based prediction is produced from evidence and market features

- **WHEN** the model receives news evidence and price features
- **THEN** it SHALL return a label and a confidence value that can be displayed in the dashboard

### Requirement: Faithfulness evaluation measures explanation impact

The system SHALL compute faithfulness metrics such as confidence drop and temporal validity to assess whether cited evidence materially affects the prediction.

#### Scenario: Counterfactual masking changes confidence

- **WHEN** cited evidence is masked or replaced with neutral text
- **THEN** the system SHALL recalculate confidence and report the resulting confidence drop
