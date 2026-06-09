# Agentic AI in SDLC

## Building a Stock Trend Forecasting System from News with Evidence-Based Verification

### Geting Started

1. Clone the repo
2. Set up [OpenSpecs](https://github.com/Fission-AI/OpenSpec) in your environment
3. Run `openspec init` and choose your IDEs
4. Restart the IDE to apply the slash commands

### Week 1 validation

Run the local prototype and its tests with:

- `python -m pytest`
- `python src/main.py`
- `python scripts/verify_week1.py`

The verification script runs the test suite, checks deterministic output across repeated passes, and writes the combined result to `outputs/week1_verification_output.json`.
