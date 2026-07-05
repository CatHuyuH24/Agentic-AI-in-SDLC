## 1. Setup & Dependencies

- [x] 1.1 Add `kaleido` to `requirements.txt` (needed for Plotly static PNG export via `fig.write_image()`)
- [x] 1.2 Verify `pandoc` is available on the host machine (`pandoc --version`); if not, install `fpdf2` as fallback (`pip install fpdf2`)
- [x] 1.3 Create `outputs/figures/` directory (if it doesn't exist)
- [x] 1.4 Create `scripts/` directory (if it doesn't exist)

## 2. Figure Export

- [x] 2.1 Audit `src/dashboard.py` and identify the four Plotly figure-building blocks: prediction distribution bar chart, confidence drop bar chart, temporal leakage warning chart, faithfulness radar chart
- [x] 2.2 Refactor each of the four chart blocks in `dashboard.py` into standalone helper functions (e.g., `build_prediction_distribution_fig()`, `build_confidence_drop_fig()`, `build_temporal_leakage_fig()`, `build_faithfulness_radar_fig()`) that accept data and return `go.Figure` objects — keep dashboard rendering unchanged
- [x] 2.3 Create `scripts/export_figures.py` that: loads `outputs/faithfulness_results.csv`, calls each helper function from `dashboard.py`, and writes the result with `fig.write_image("outputs/figures/<name>.png", width=1200, height=800)`
- [x] 2.4 Run `python scripts/export_figures.py` and verify all 4 PNGs appear in `outputs/figures/` with correct filenames: `prediction_distribution.png`, `confidence_drop.png`, `temporal_leakage_warning.png`, `faithfulness_radar.png`

## 3. Report Writing

- [x] 3.1 Create `docs/report.md` with all required sections (see spec): Introduction, Research Gap, Agentic SDLC Design, Data Description, Technical Pipeline, Metrics & Evaluation, Experimental Results, Case Analysis, Limitations, Appendix
- [x] 3.2 Write **Section 1 — Introduction**: state the central research question (does cited evidence truly drive forecasts?), motivation, and project scope
- [x] 3.3 Write **Section 2 — Research Gap**: distinguish prediction accuracy from explanation faithfulness; cite industry examples of post-hoc rationalization risk
- [x] 3.4 Write **Section 3 — Agentic SDLC Design**: describe the OpenSpec workflow, list the three changes (`faithful-evidence-forecasting`, `finbert-fusion-model`, `week5-advanced-faithfulness`), explain human quality-gate process from `project_plan.md` §2.2, include a table of SDLC phases vs. AI agent usage
- [x] 3.5 Write **Section 4 — Data Description**: describe `data/financial_corpus.csv` (350 rows, 3 tickers: AAPL, TSLA, NVDA), labeling logic (Δ>0.005→UP, Δ<-0.005→DOWN), temporal leakage test split, source provenance
- [x] 3.6 Write **Section 5 — Technical Pipeline**: describe each module (`retriever.py`, `evidence_extractor.py`, `forecast_model.py`, `faithfulness_metrics.py`, `schema_adapter.py`, `loader.py`) with a brief ASCII pipeline diagram; reference design.md for architecture
- [x] 3.7 Write **Section 6 — Metrics & Evaluation**: define Evidence Support, Temporal Validity, Confidence Drop, Counterevidence Coverage, Market Consistency, Regime Analysis; include formula for Confidence Drop
- [x] 3.8 Write **Section 7 — Experimental Results**: include a comparison table (Rule-based vs FinBERT accuracy/avg-confidence-drop) from `outputs/week4_comparison.csv`; embed references to the 4 exported figure PNGs; write 2–3 sentence narrative per figure
- [x] 3.9 Write **Section 8 — Case Analysis**: pick 2 concrete records from `outputs/faithfulness_results.csv` — one FAITHFUL and one POST_HOC_DECORATION — and walk through evidence, confidence values, and conclusion
- [x] 3.10 Write **Section 9 — Limitations & Future Work**: address 3–4 real limitations (lexicon coverage, dataset size, FinBERT fine-tuning on small corpus, no live news feed) and suggest improvements
- [x] 3.11 Write **Appendix**: include one representative agent trace entry (from project_plan.md §2.2 quality gate format), one prompt example used (from project_plan.md §6), and a sample test case for temporal leakage
- [x] 3.12 Convert `docs/report.md` to `report.pdf` using `pandoc docs/report.md -o report.pdf --pdf-engine=xelatex -V geometry:margin=2.5cm -V fontsize=11pt` (or equivalent `fpdf2` script if pandoc unavailable); verify page count is 5–8 pages

## 4. README Update

- [x] 4.1 Rewrite `README.md` **Project Overview** section: update title, one-paragraph description mentioning FinBERT, real data (AAPL/TSLA/NVDA, 350 rows), and faithfulness evaluation
- [x] 4.2 Add **Architecture** section to README with ASCII pipeline diagram: `News + Price Data → Temporal Retriever → Evidence Extractor → Forecast Model (Rule / FinBERT) → Faithfulness Evaluator → Dashboard`
- [x] 4.3 Add/update **Requirements** section: list Python 3.10+, `requirements.txt` (CPU) and `requirements-gpu.txt` (GPU); mention `kaleido` for figure export
- [x] 4.4 Add **Setup** section with two sub-paths: CPU (`pip install -r requirements.txt`) and GPU (`pip install -r requirements-gpu.txt`); note FinBERT checkpoint at `models/finbert_fusion.pt`
- [x] 4.5 Add **Running** section with exact commands: `python src/main.py` (full pipeline), `streamlit run src/dashboard.py` (interactive dashboard), `python scripts/export_figures.py` (generate PNGs), `pytest tests/` (run tests)
- [x] 4.6 Update **Project Structure** section to reflect current repo: include `src/loader.py`, `src/schema_adapter.py`, `data/financial_corpus.csv`, `outputs/figures/`, `scripts/export_figures.py`, `models/finbert_fusion.pt`, all `openspec/changes/` entries
- [x] 4.7 Review final README for accuracy: confirm all commands work when executed from repo root, confirm all file paths in the structure section exist in the repo
