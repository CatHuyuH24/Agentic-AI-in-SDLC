## Why

The core technical implementation for the Faithful Evidence-Centric Financial News Forecasting System (Weeks 1–5) is complete, but the project is missing three mandatory submission deliverables: a 5–8 page `report.pdf`, four static output figure PNGs (`outputs/figures/`), and an up-to-date `README.md`. Without these, A7 is only partially credited and the submission checklist cannot be cleared. Deadline is 2026-07-14.

## What Changes

- **New**: `report.pdf` (5–8 pages) written from existing OpenSpec docs, pipeline outputs, and experiment results — covering problem intro, research gap, Agentic SDLC design, data description, pipeline, metrics, results, case analysis, and limitations.
- **New**: `outputs/figures/` directory with four exported static PNGs: `prediction_distribution.png`, `confidence_drop.png`, `temporal_leakage_warning.png`, `faithfulness_radar.png` — exported from the existing Streamlit/Plotly dashboard.
- **Modified**: `README.md` updated to reflect the current repository state: FinBERT model, Week 5 advanced metrics, real data corpus, Streamlit launch command (`streamlit run src/dashboard.py`), full project structure, and all environment setup steps.

## Capabilities

### New Capabilities

- `report-generation`: Produce a 5–8 page academic PDF report using existing OpenSpec specs, pipeline outputs (`faithfulness_results.csv`, `week4_comparison.csv`), and code-level evidence. Sections: introduction, research gap, SDLC design (Agentic AI usage), data description, technical pipeline, metrics & evaluation, experimental results, case analysis, limitations & future work, appendix (agent trace, prompts).
- `figure-export`: Export four Plotly charts from `src/dashboard.py` as static 1200×800 PNG files to `outputs/figures/`. Charts: prediction distribution bar, confidence drop per ticker, temporal leakage warning timeline, faithfulness radar by metric.

### Modified Capabilities

- (none — only README prose updated, no spec-level behavior changes)

## Impact

- `README.md` — overwrite with current commands and project structure
- `outputs/figures/` — new directory with 4 PNG files
- `report.pdf` — new root-level file (or `docs/report.pdf`)
- `src/dashboard.py` — may need a `--export` CLI flag or a separate `scripts/export_figures.py` helper to generate static PNGs without running the full Streamlit server
