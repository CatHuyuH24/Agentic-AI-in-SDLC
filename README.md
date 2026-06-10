# Agentic AI in SDLC

## Stock Trend Forecasting with Evidence-Based Verification

This project builds a small, runnable prototype for forecasting stock direction from financial news while keeping evidence and temporal safety visible. The current codebase already includes the Week 1 baseline and the first Week 2 evidence/forecasting extension.

### Project Goal and Project Plan

Build a faithful evidence-centric forecasting prototype that:

- filters out future-dated news,
- keeps a deterministic loader/retriever contract,
- extracts simple evidence signals from valid news,
- produces a basic rule-based forecast direction and confidence.
- The detailed project description is in the file [ChuDe1.pdf](/docs/ChuDe1.pdf) (`.md` version is the file [Do_an_cuoi_ki_Agentic_AI.md](/docs/Do_an_cuoi_ki_Agentic_AI.md))
- The detailed project plan can be found in the file [project_plan.md](/docs/project_plan.md)

### Project structure

- `data/` — curated sample dataset used for local validation.
- `src/` — loader, retriever, evidence extractor, and simple forecast model.
- `tests/` — pytest coverage for the Week 1 baseline and Week 2 extension.
- `outputs/` — generated validation outputs and reproducibility reports.
- `openspec/changes/faithful-evidence-forecasting/` — OpenSpec proposal, design, spec, and task ledger for the current change.
- `docs/` — project plan and assignment references.
- `scripts/` — local verification helper for repeated validation.

### Getting started

1. Clone the repository.
2. Install Python dependencies and run the tests with `python -m pytest`.
3. Run the prototype with `python src/main.py`.
4. Run the verification helper with `python scripts/verify_week1.py`.

### Current project status

- Week 1 baseline is implemented and verified: loader, temporal retriever, warnings, deterministic output, and tests.
- Week 2 extension is now in progress: simple evidence extraction and a rule-based forecast model are implemented and covered by tests.
- The system is currently functional, runnable, and testable.

### Suggested workflow for the next iteration

1. Review the current loader/retriever contract and keep it unchanged.
2. Add or refine evidence extraction rules for stronger signal quality.
3. Extend the forecast model with more explainable confidence logic.
4. Re-run `python -m pytest` and confirm the pipeline remains deterministic.
5. Update the OpenSpec notes only when the implementation milestone changes.
