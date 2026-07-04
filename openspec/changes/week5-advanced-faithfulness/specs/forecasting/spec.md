# Specification: Advanced Faithfulness Diagnostics (Week 5)

## Summary

This specification extends the existing faithfulness evaluation flow with two additional diagnostics that make the evidence analysis more complete and more actionable for users:

1. Counterevidence coverage
2. Market consistency

These diagnostics are derived from the existing evidence list and price features so they stay explainable and do not require changes to the underlying forecasting backends.

## Functional Requirements

### FR-1: Counterevidence Coverage

The system shall compute a counterevidence coverage score for each forecast based on the evidence extracted from valid news.

- The metric shall be a float in the range $[0.0, 1.0]$.
- A value of $1.0$ indicates that the evidence includes both supporting and opposing directional evidence for the forecast.
- A value of $0.0$ indicates that no opposing evidence was detected.
- The metric shall be derived from the evidence list produced by the existing extractor.

### FR-2: Market Regime Classification

The system shall classify each record into one of three regime buckets:

- bull
- bear
- sideways

The classification shall be based on the available price and volume features:

- positive price return and positive volume change -> bull
- negative price return and negative volume change -> bear
- otherwise -> sideways

### FR-3: Market Consistency

The system shall compute a market consistency score that measures how well the evidence direction aligns with the detected market regime.

- If the evidence direction is UP and the regime is bull, the score shall be $1.0$.
- If the evidence direction is DOWN and the regime is bear, the score shall be $1.0$.
- If the evidence direction is HOLD or the evidence is neutral, the score shall default to $1.0$ for sideways and $0.5$ otherwise.
- The score shall always be between $0.0$ and $1.0$.

### FR-4: Extended Faithfulness Payload

The evaluate_faithfulness() function shall include the new values in its return object:

- counterevidence_coverage
- market_consistency
- market_regime

The existing fields shall remain unchanged.

### FR-5: Dashboard Exposure

The dashboard shall render the advanced metrics in a compact panel so an analyst can quickly inspect the evidence context of a forecast.

### FR-6: Batch Output Exposure

The CLI batch pipeline shall include the advanced metrics in the generated JSON and CSV outputs.

## Acceptance Criteria

- Given a list of evidence containing both UP and DOWN items for an UP forecast, the counterevidence coverage metric returns a positive value greater than zero.
- Given a price feature set with positive momentum and growth, the system classifies the record as bull.
- Given a price feature set with near-zero movements, the system classifies the record as sideways.
- Given a forecast evaluation result, the return object contains the new advanced metrics.
- Given a selected record in the dashboard, the advanced metrics panel is visible without breaking the existing layout.

## Non-Functional Requirements

- The implementation shall remain deterministic.
- The implementation shall not require any new external libraries.
- The implementation shall preserve compatibility with the existing test suite.
