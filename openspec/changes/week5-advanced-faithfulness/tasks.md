# Task Checklist: Week 5 Advanced Faithfulness Expansion

## 1. Faithfulness Metrics Extension

- [x] 1.1 Implement counterevidence coverage logic that detects both supporting and opposing evidence for a forecast.
- [x] 1.2 Implement market regime classification from price and volume features.
- [x] 1.3 Implement market consistency scoring that measures alignment between evidence direction and market regime.
- [x] 1.4 Extend evaluate_faithfulness() with the new metrics while preserving existing return fields.

## 2. Dashboard Enhancements

- [x] 2.1 Add an advanced faithfulness summary section to the dashboard.
- [x] 2.2 Render counterevidence coverage, market regime, and market consistency in a compact panel.
- [x] 2.3 Keep the existing layout and warning sections intact.

## 3. CLI / Batch Output Expansion

- [x] 3.1 Extend the JSON and CSV outputs to include the week 5 faithfulness fields.
- [x] 3.2 Ensure the batch runner remains compatible with both single-model and dual-model runs.

## 4. Tests

- [x] 4.1 Add unit tests for counterevidence coverage and market consistency.
- [x] 4.2 Add integration tests for the extended evaluate_faithfulness() contract.
- [x] 4.3 Run pytest and confirm all tests pass.

## 5. Verification

- [x] 5.1 Run the full test suite.
- [x] 5.2 Run the pipeline CLI and verify the outputs are created.
- [x] 5.3 Review the updated OpenSpec artifacts for implementation readiness.
