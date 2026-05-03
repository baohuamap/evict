# GEMINI.md

## Project Overview
**EVICT (Evidence-Conditioned Investigation with Calibrated Triage)** is a research project aimed at improving the triage of static analysis alerts. The core innovation is a framework that combines LLM-based reasoning, evidence extraction from static analyzers, confidence calibration via conformal prediction, and symbolic execution for escalation.

The project is structured as a hybrid research workspace containing both the academic manuscript (targeting NeurIPS 2026) and a functional Python implementation of the EVICT pipeline.

### Main Technologies
- **Paper:** LaTeX (NeurIPS style), BibTeX.
- **Pipeline:** Python 3.9+, Pydantic (data models), OpenAI/Google GenAI (LLM backend), Z3 Solver (symbolic execution), NumPy/Pandas (data analysis), Matplotlib/Seaborn (visualization).
- **Development Tools:** Pytest, Black, Isort, Mypy.

---

## Directory Structure
- `main.tex`, `sections/`, `figures/`: LaTeX source and assets for the research paper.
- `evict_pipeline/`: The Python package implementing the EVICT framework.
    - `src/evict_pipeline/`: Core logic (Extractor, Verifier, Calibrator, Escalator).
    - `tests/`: Unit and integration tests using Pytest.
- `data/`: Literature reviews, CSV exports, and experimental results (e.g., Juliet benchmark data).
- `docs/`: Extensive research notes, reviewer reports, and executive summaries.
- `scripts/`: Utility scripts for figure generation and task automation.
- `artifacts/`: Build byproducts, exported deliverables, and runtime screenshots.

---

## Building and Running

### Software Pipeline
1.  **Installation:**
    ```bash
    pip install -e "./evict_pipeline[dev]"
    ```
2.  **Running Tests:**
    ```bash
    pytest evict_pipeline/tests
    ```
3.  **Basic Usage:**
    ```python
    from evict_pipeline import EvictPipeline
    pipeline = EvictPipeline()
    result = pipeline.run("path/to/alert.sarif")
    ```

### Research Paper
- **Compile PDF:** Run `pdflatex main.tex` or use a LaTeX build tool like `latexmk`.
- **Generate Figures:**
    ```bash
    python scripts/generate_figures.py
    ```

---

## Development Conventions

### Coding Standards
- **Data Modeling:** Use Pydantic models (defined in `evict_pipeline/src/evict_pipeline/models.py`) for all structured data like Alerts and EvidencePacks.
- **Mocking:** Tests should use `unittest.mock` to simulate LLM and SMT solver responses to avoid API costs and environment dependencies during CI.
- **Type Safety:** Maintain strict typing with Mypy.

### Manuscript Editing
- **Sectional Writing:** The paper is split into modular files in `sections/`. Edits to the main narrative should be made in the corresponding `.tex` file (e.g., `sections/methodology.tex`).
- **Citations:** Update `references.bib` for new literature.
- **Terminology:** Adhere to the terms defined in the executive summary: "Evidence-Conditioned", "Selective Prediction", "Conformal Prediction", and "Symbolic Escalation".

---

## Key Files
- `main.tex`: Root LaTeX file.
- `evict_pipeline/src/evict_pipeline/pipeline.py`: Main entry point for the triage logic.
- `docs/summaries/EXECUTIVE_SUMMARY.md`: High-level status and research goals.
- `WORKSPACE_ORGANIZATION.md`: Detailed map of the directory structure.
