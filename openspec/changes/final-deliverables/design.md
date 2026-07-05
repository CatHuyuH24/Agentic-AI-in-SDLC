## Context

The Faithful Evidence-Centric Financial News Forecasting System has completed all core technical implementation (Weeks 1–5). The pipeline is functional: real data (350 rows, 3 tickers), FinBERT fusion model checkpoint (`models/finbert_fusion.pt`), advanced faithfulness metrics, and a Streamlit dashboard. What remains are three submission artifacts needed to close A7 and the overall submission checklist.

Current gaps:
- No `report.pdf` exists at root level
- `outputs/figures/` directory does not exist; rubric requires 4 static PNGs
- `README.md` still describes Week 1 state; missing FinBERT and Streamlit launch instructions

## Goals / Non-Goals

**Goals:**
- Generate a properly structured 5–8 page academic report in PDF format, sourcing all content from existing artifacts (OpenSpec docs, `faithfulness_results.csv`, `week4_comparison.csv`, pipeline code)
- Export 4 Plotly charts from `dashboard.py` as static 1200×800 PNG files to `outputs/figures/`
- Rewrite `README.md` to accurately describe the current project state: setup, environment, commands, structure

**Non-Goals:**
- Writing new code beyond what's needed to export figures (e.g., no new models or metrics)
- Creating `outputs/run_log.json` (B4 — excluded per user instruction)
- Recording the demo video
- Modifying any existing `src/` modules beyond adding an optional figure-export helper

## Decisions

### Decision 1: Report toolchain — Python `fpdf2` / `reportlab` or Markdown-to-PDF

**Chosen**: Write report as a structured Markdown file (`docs/report.md`) and convert to PDF using `pandoc` (system-available) or `md-to-pdf` via Node. Alternatively produce directly with Python `fpdf2`.

**Rationale**: Content already exists in Markdown (OpenSpec docs). `pandoc` produces clean academic PDF with minimal setup. If unavailable, `fpdf2` gives full Python control.

**Alternative considered**: LaTeX — too heavyweight for a 5–8 page student report with no complex math beyond displayed formulas.

### Decision 2: Figure export — standalone script vs. Streamlit button

**Chosen**: Create `scripts/export_figures.py` — a standalone Python script that imports `dashboard.py`'s Plotly figure-building functions and calls `fig.write_image(path)` via `kaleido`.

**Rationale**: Running `streamlit run` just to export figures is unnecessary. A headless script is reproducible and can run in CI. `kaleido` is the standard Plotly static export backend.

**Alternative considered**: Adding an "Export PNGs" button inside the dashboard — less reproducible for grader, requires manual interaction.

### Decision 3: README structure

**Chosen**: Single `README.md` with sections: Project Overview, Architecture Diagram (ASCII), Requirements, Setup (CPU + GPU paths), Running (pipeline + dashboard + export figures), Project Structure, and Results Summary table.

**Rationale**: Matches the rubric expectation of "setup blueprints and local execution guides." ASCII diagram avoids image dependency.

## Risks / Trade-offs

- **`kaleido` not installed** → Mitigation: add `kaleido` to `requirements.txt`; fallback to `plotly.io.write_html` + browser screenshot if needed.
- **`pandoc` not on PATH** → Mitigation: document alternative `fpdf2`-based script in tasks; `fpdf2` is pip-installable.
- **Dashboard imports are heavy (torch, transformers)** → Mitigation: `export_figures.py` imports only the figure-building helper functions, not the full Streamlit app bootstrap; may need to refactor `dashboard.py` to expose a `build_figures()` function.
- **Report page count** → Rubric says 5–8 pages; with proper formatting (11pt, 1.15 spacing, figures) this is achievable from existing content without padding.
