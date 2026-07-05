## ADDED Requirements

### Requirement: Report generation
The system SHALL produce a 5–8 page academic report in PDF format covering: problem introduction, research gap (accuracy vs. faithfulness), Agentic SDLC design and AI agent usage, dataset description, technical pipeline, faithfulness metrics, experimental results, case analysis, limitations, and an appendix with agent traces and prompts.
The report SHALL source all factual claims from existing artifacts: `openspec/changes/`, `outputs/faithfulness_results.csv`, `outputs/week4_comparison.csv`, and `src/` module docstrings.

#### Scenario: Report covers all required sections
- **WHEN** the grader opens `report.pdf`
- **THEN** the document SHALL contain at minimum these sections: Introduction, Research Gap, Agentic SDLC Design, Data Description, Pipeline, Metrics & Evaluation, Experimental Results, Case Analysis, Limitations, and Appendix

#### Scenario: Report references real experiment data
- **WHEN** the results section is read
- **THEN** it SHALL include a comparison table of Rule-based vs FinBERT accuracy and average confidence drop sourced from `outputs/week4_comparison.csv`

#### Scenario: Report page count
- **WHEN** the PDF is rendered at A4/Letter size with 11–12pt body font
- **THEN** the document SHALL be between 5 and 8 pages inclusive (excluding appendix if appendix pushes beyond 8)

### Requirement: Figure export
The system SHALL export four Plotly charts from the dashboard as static PNG files to `outputs/figures/`. The required filenames are: `prediction_distribution.png`, `confidence_drop.png`, `temporal_leakage_warning.png`, `faithfulness_radar.png`. Each PNG SHALL be at least 1200px wide and 800px tall.

#### Scenario: All four figures present
- **WHEN** `scripts/export_figures.py` is executed
- **THEN** all four PNG files SHALL be created under `outputs/figures/`

#### Scenario: Figures match dashboard content
- **WHEN** a figure PNG is opened
- **THEN** it SHALL display the same chart visible in the corresponding dashboard panel

#### Scenario: Export script is headless
- **WHEN** `python scripts/export_figures.py` is run from the command line (no browser or Streamlit server)
- **THEN** all four PNG files SHALL be generated without requiring user interaction

### Requirement: README accuracy
The README SHALL accurately describe the current project state. It SHALL include: a project overview, a system architecture overview (ASCII or inline diagram), Python environment setup instructions (CPU and GPU variants), the Streamlit dashboard launch command (`streamlit run src/dashboard.py`), the figure export command (`python scripts/export_figures.py`), the main pipeline run command (`python src/main.py`), the test command (`pytest tests/`), and the full current project directory structure.

#### Scenario: README mentions FinBERT
- **WHEN** the README is read
- **THEN** it SHALL mention the FinBERT fusion model and the model checkpoint at `models/finbert_fusion.pt`

#### Scenario: Dashboard launch command present
- **WHEN** a new user follows the README
- **THEN** they SHALL find the exact command `streamlit run src/dashboard.py` in the Running section

#### Scenario: Project structure is current
- **WHEN** the README structure section is compared to the actual repo
- **THEN** it SHALL include `src/loader.py`, `src/schema_adapter.py`, `data/financial_corpus.csv`, and `outputs/figures/` (all added after Week 1)
