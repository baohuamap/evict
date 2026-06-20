# Codebase Structure

**Analysis Date:** 2026-06-20

## Directory Layout

```
FP_SA/                          # repo root (paper + pipeline + datasets)
├── evict_pipeline/             # Python package: the EVICT pipeline (src layout)
│   ├── src/evict_pipeline/     # importable package source
│   ├── tests/                  # pytest unit tests for the pipeline
│   ├── demo_data/              # tiny SARIF + .java fixtures for quick demos
│   ├── evaluate.py             # CLI runner (rich table output)
│   ├── pyproject.toml          # package metadata + deps (pydantic, openai, z3, ...)
│   └── README.md               # package readme (note: usage snippet is stale)
├── scripts/                    # automation: benchmarks, SARIF generation, analysis
├── data/                       # datasets + vendored baselines (gitignored bulk)
│   ├── juliet_java/            # Juliet C/C++→Java test cases (per-CWE Gradle modules)
│   ├── juliet_sarifs/          # per-CWE SpotBugs SARIF outputs (cwe<NN>.sarif)
│   ├── cwe-bench-java/         # real-world Java benchmark (ground truth CSVs)
│   ├── iris-v2/                # vendored IRIS baseline + CodeQL DB builder
│   ├── literature_exports/     # literature-review CSVs (paper asset)
│   ├── juliet_alerts_pmd.sarif # PMD-generated Juliet SARIF (PoC input)
│   └── juliet_alerts_spotbugs.sarif
├── artifacts/                  # generated outputs
│   ├── exports/                # EVICT result CSVs + summaries + v2/ subdir
│   ├── codeql_results/         # CWE-Bench SARIFs from CodeQL
│   ├── runtime_screenshots/    # run screenshots
│   └── source_images/          # source diagram images
├── sections/                   # LaTeX paper sections
├── figures/                    # paper figures (PDF/PNG)
├── docs/                       # research notes, reviews, summaries (paper asset)
├── reviews/                    # reviewer reports (paper asset)
├── tests/                      # repo-level tests (CodeQL extractor test)
├── bin/                        # vendored analyzers: spotbugs-4.8.4, pmd-bin-7.1.0
├── main.tex                    # paper entry; sections/ included from here
├── references.bib              # paper bibliography
├── neurips_2026.sty            # NeurIPS style file
├── implementation.md           # implementation notes referenced by paper
├── README.md                   # project readme (quickstart)
├── WORKSPACE_ORGANIZATION.md   # one-page layout note
├── GEMINI.md                   # AI-assistant context note
└── venv/                       # project virtualenv (gitignored)
```

## Directory Purposes

**`evict_pipeline/src/evict_pipeline/`:**
- Purpose: the importable `evict_pipeline` Python package — the 4-stage triage engine.
- Contains: 6 modules (`__init__.py`, `models.py`, `extractor.py`, `verifier.py`, `calibrator.py`, `escalator.py`, `pipeline.py`).
- Key files: `pipeline.py` (orchestrator), `models.py` (Pydantic contracts), `verifier.py` (LLM + pass@5, largest at 202 lines).

**`evict_pipeline/tests/`:**
- Purpose: pytest unit tests for the pipeline.
- Contains: `test_pipeline.py` (TP path + abstain→escalate path, uses `MagicMock` for `Verifier`/`Escalator`).
- Key files: `test_pipeline.py:8-20` (`mock_pipeline` fixture).

**`evict_pipeline/demo_data/`:**
- Purpose: tiny fixtures for quick smoke runs.
- Contains: `juliet_alerts.sarif`, `JulietCWE22.java`, `JulietCWE78.java`, `JulietCWE89.java`.

**`scripts/`:**
- Purpose: all automation — SARIF generation, benchmark runners, metric analysis, paper-table generation.
- Contains: 4 Python benchmark/runner scripts, 5 shell scripts, 2 paper-CSV/table generators, 1 todo helper.
- Key files: `benchmark_juliet_sampling.py`, `benchmark_cwe_bench.py`, `run_juliet_poc.py`, `run_full_cwe_bench.sh`, `analyze_juliet_performance.py`, `generate_figures.py`.

**`data/juliet_java/`:**
- Purpose: NIST Juliet test suite ported to Java, split into per-CWE Gradle modules (`juliet-cwe<NN>`) plus `juliet-support` (utility classes).
- Contains: ~120 CWE modules, each with `src/main/java/juliet/testcases/CWE<NN>_*/` and a Gradle `build/`. `settings.gradle.kts` enumerates modules via `myInclude("cwe<NN>")`.
- Key files: `settings.gradle.kts` (consumed by `scripts/generate_full_juliet_sarif.sh:22`); `juliet-support/src/main/java/juliet/utils/` (auxiliary classes needed on the SpotBgs auxclasspath).

**`data/juliet_sarifs/`:**
- Purpose: SpotBugs SARIF output per CWE — the input to `benchmark_juliet_sampling.py`.
- Contains: ~110 files named `cwe<NN>.sarif` (e.g. `cwe89.sarif`, `cwe78.sarif`).
- Key files: one SARIF per CWE; stem is the CWE identifier used by the sampling benchmark.

**`data/cwe-bench-java/`:**
- Purpose: real-world Java vulnerability benchmark with ground truth.
- Contains: `data/fix_info.csv` (file + method_start/method_end per project_slug), `data/build_info.csv` (build config), `data/project_info.csv` (CVE→project mapping); `advisory/`, `package-names/`, `patches/`, `baselines/`, `scripts/`, `java-env/`.
- Key files: `data/fix_info.csv` (consumed by `benchmark_cwe_bench.py:18-36`), `README.md`.

**`data/iris-v2/`:**
- Purpose: vendored IRIS baseline (state-of-the-art comparison) + CodeQL database builder. Independent architecture; not imported by `evict_pipeline`.
- Contains: `src/iris.py` (1399-line `SAPipeline` class), `src/modules/` (`codeql_query_runner.py`, `contextual_analysis_pipeline.py`, `evaluation_pipeline.py`), `src/models/` (15 LLM wrappers: `gpt.py`, `gemini.py`, `llama.py`, `deepseek.py`, `mistral.py`, `qwen.py`, `ollama.py`, etc.), `src/queries/` and `src/cwe-queries/` (`.ql` CodeQL queries), `scripts/build_codeql_dbs.py` (Docker-based DB builder), `codeql/` (patched CodeQL CLI), `visualizer/` (JS/HTML results browser), `docs/` (mdBook docs), `iclr-2025-results/`, `Dockerfile`, `environment.yml`, `book.toml`.
- Key files: `src/iris.py:58` (`class SAPipeline`), `scripts/build_codeql_dbs.py` (called by `run_full_cwe_bench.sh:26`), `src/config.py` (hardcoded paths).

**`artifacts/exports/`:**
- Purpose: EVICT triage result CSVs + per-run summaries + cross-model comparison tables.
- Contains: per-model `juliet_evict_results_<model>.csv` (+ `_summary.md`), `juliet_sampled_results.csv`, `performance_comparison.{csv,md}`, and a `v2/` subdir holding the latest sampled runs (`juliet_sampled_results_<model>.csv` for `claude_haiku_4_5`, `gemini_2_5_flash_lite`, `gemini_3_1_flash_lite*`, `gpt_4o_mini`, `gpt_5_nano`, ...). Also holds the paper draft PDF/DOCX and `evict_paper_writing_prompt.md`.
- Key files: `v2/juliet_sampled_results_*_summary.md` (consumed by `generate_paper_csv.py`/`generate_paper_table.py` via glob `artifacts/exports/*_summary.md`).

**`artifacts/codeql_results/`:**
- Purpose: SARIF output from `codeql database analyze` for CWE-Bench-Java projects.
- Contains: one `<slug>.sarif` per project; produced by `scripts/generate_sarifs.sh` / `run_full_cwe_bench.sh:32-48`.

**`sections/`:**
- Purpose: LaTeX paper sections included by `main.tex`.
- Contains: `introduction.tex`, `background.tex`, `theory.tex`, `methodology.tex`, `evaluation_plan.tex`, `preliminary_results.tex`, `discussion.tex`, `broader_impact.tex`, `appendix.tex`.

**`figures/`:**
- Purpose: paper figures.
- Contains: `calibration_plot.pdf`, `risk_coverage_curve.pdf` (generated by `scripts/generate_figures.py`), `evict_framework_architecture.png`, `evict_workflow_example.png`.

**`docs/`, `reviews/`:**
- Purpose: paper-adjacent research assets (literature notes, reviewer reports, summaries). Not coupled to the pipeline.

**`tests/` (repo-level):**
- Purpose: integration test for the SARIF extractor against a real CodeQL sample.
- Contains: `test_extractor_codeql.py` + `sample_codeql.sarif` fixture.

**`bin/`:**
- Purpose: vendored static analyzers used by the Juliet SARIF generation scripts.
- Contains: `spotbugs-4.8.4/`, `pmd-bin-7.1.0/`.

**`venv/`, `evict_pipeline/venv/`:**
- Purpose: Python virtualenvs (project-root and package-local). Gitignored; not committed.

## Key File Locations

**Entry Points:**
- `evict_pipeline/src/evict_pipeline/pipeline.py`: `EvictPipeline` class — the canonical 4-stage orchestrator.
- `evict_pipeline/evaluate.py`: CLI runner with `rich` table output.
- `scripts/run_juliet_poc.py`: Juliet PoC runner (resumable, supports local LLM).
- `scripts/benchmark_juliet_sampling.py`: Juliet sampled benchmark (50–100/CWE).
- `scripts/benchmark_cwe_bench.py`: CWE-Bench-Java benchmark with ground-truth matching.
- `scripts/run_full_cwe_bench.sh`: 3-step shell orchestrator (build → analyze → triage).
- `scripts/generate_sarifs.sh`: build CodeQL DBs + analyze (CWE-Bench path).
- `scripts/generate_full_juliet_sarif.sh`: SpotBugs over all Juliet CWE modules.
- `evict_pipeline/src/evict_pipeline/__init__.py`: public API re-exports (`Label`, `Alert`, `EvidencePack`, `Decision`, `Extractor`, `Verifier`, `Calibrator`, `Escalator`, `EvictPipeline`).

**Configuration:**
- `evict_pipeline/pyproject.toml`: package metadata, deps (`pydantic>=2`, `openai>=1`, `google-genai>=0.1`, `z3-solver>=4.12`, `numpy`, `pandas`, `scikit-learn`, `rich`), dev extras (`pytest`, `black`, `isort`, `mypy`), `setuptools` src-layout discovery.
- `data/iris-v2/src/config.py`: IRIS hardcoded paths (`CODEQL_DIR`, `CODEQL_DB_PATH`, `BUILD_INFO`, `DATA_DIR`, ...).
- `data/iris-v2/dep_configs.json` / `dep_configs.linux_x64.json`: JDK/Maven/Gradle version paths for Docker builds.
- `data/iris-v2/environment.yml`: IRIS conda env.
- `data/iris-v2/Dockerfile`: IRIS container build.
- `.gitignore` (repo root): excludes `venv/`, build artifacts.
- No `.env`/settings file for the EVICT pipeline — config is env vars + CLI flags.

**Core Logic:**
- `evict_pipeline/src/evict_pipeline/models.py`: `Label`, `EvidencePack`, `Alert`, `Decision`.
- `evict_pipeline/src/evict_pipeline/extractor.py`: SARIF → `Alert`, `populate_evidence` → `EvidencePack`.
- `evict_pipeline/src/evict_pipeline/verifier.py`: LLM prompt + pass@5 vote-share.
- `evict_pipeline/src/evict_pipeline/calibrator.py`: conformal threshold + `fit_threshold` (unused).
- `evict_pipeline/src/evict_pipeline/escalator.py`: Z3/JPF/KLEE stubs.
- `scripts/analyze_juliet_performance.py`: Juliet ground-truth derivation + metrics (precision/recall/coverage/ECE).

**Testing:**
- `evict_pipeline/tests/test_pipeline.py`: pipeline unit tests (mocked stages).
- `tests/test_extractor_codeql.py`: extractor integration test against `tests/sample_codeql.sarif`.
- `evict_pipeline/demo_data/`: demo fixtures (SARIF + Java sources).

**Paper Artifacts (decoupled from pipeline):**
- `main.tex`, `sections/*.tex`, `references.bib`, `neurips_2026.sty`, `algorithm_env.tex`.
- `figures/*`, `artifacts/exports/*_summary.md`, `artifacts/exports/performance_comparison*.{csv,md}`.
- `implementation.md`, `README.md`, `WORKSPACE_ORGANIZATION.md`, `GEMINI.md`.
- `docs/research_notes/`, `docs/reviews/`, `docs/summaries/`, `reviews/`.
- `data/literature_exports/` (literature-review CSVs).

## Naming Conventions

**Files (pipeline package):**
- Lowercase single-word module names matching the class: `extractor.py`→`Extractor`, `verifier.py`→`Verifier`, `calibrator.py`→`Calibrator`, `escalator.py`→`Escalator`, `pipeline.py`→`EvictPipeline`, `models.py` (plural for the data-contract module).

**Files (scripts):**
- Snake_case action scripts: `benchmark_<dataset>_<mode>.py` (`benchmark_juliet_sampling.py`, `benchmark_cwe_bench.py`), `run_<target>_<mode>.py` (`run_juliet_poc.py`), `analyze_<dataset>_<metric>.py` (`analyze_juliet_performance.py`), `generate_<artifact>.py` (`generate_figures.py`, `generate_paper_csv.py`, `generate_paper_table.py`).
- Shell scripts: `setup_<target>_<tool>.sh` (`setup_juliet_pmd.sh`, `setup_juliet_spotbugs.sh`, `setup_cwe_bench.sh`), `generate_<scope>.sh` (`generate_sarifs.sh`, `generate_full_juliet_sarif.sh`, `generate_mini_benchmark.sh`), `run_full_<dataset>.sh` (`run_full_cwe_bench.sh`).

**Files (data):**
- Juliet SARIFs: `cwe<NN>.sarif` (lowercase CWE number, no padding) — `data/juliet_sarifs/cwe89.sarif`. The stem is the CWE key used by `benchmark_juliet_sampling.py:74`.
- CWE-Bench SARIFs: `<project_slug>.sarif` under `artifacts/codeql_results/`.
- Result CSVs: `juliet_evict_results_<safe_model>.csv` / `juliet_sampled_results_<safe_model>.csv` where `<safe_model>` replaces `/`, `.`, `-` with `_` (`benchmark_juliet_sampling.py:44`, `run_juliet_poc.py:57`). Summaries: `<csv_basename>_summary.md`.

**Directories:**
- Pipeline package uses Python `src/` layout: `evict_pipeline/src/evict_pipeline/`.
- Per-CWE Juliet modules: `juliet-cwe<NN>` (e.g. `juliet-cwe89`); test packages `juliet/testcases/CWE<NN>_<Name>/`.
- IRIS CWE queries: `src/cwe-queries/cwe-<NNN>/` (zero-padded 3 digits); generic queries: `src/queries/*.ql`.

**Classes:** PascalCase (`EvictPipeline`, `Extractor`, `Verifier`, `Calibrator`, `Escalator`, `EvidencePack`, `Alert`, `Decision`, `SAPipeline`).

**Functions/methods:** snake_case (`extract_from_sarif`, `populate_evidence`, `get_decision`, `_build_prompt`, `_sample_llm`, `fit_threshold`, `_solve_smt`, `run_on_sarif`). Private helpers prefixed with `_`.

**Module constants:** UPPERCASE (`PRIMITIVE_TYPES`, `MAX_DOC_LENGTH` in IRIS; `CODEQL`, `THIS_SCRIPT_DIR`).

**CSV columns:** Space-separated header names matching prose: `"Alert ID"`, `"CWE"`, `"EVICT Label"`, `"Ground Truth"`, `"Confidence"`, `"Stage"`, `"Escalated"`, `"Rationale"` (`run_juliet_poc.py:100`, `benchmark_juliet_sampling.py:54`, `benchmark_cwe_bench.py:124`).

## Where to Add New Code

**New pipeline stage (e.g. a Ranker before Verify):**
- Implement the class in `evict_pipeline/src/evict_pipeline/<stage>.py` (single primary method, constructor config, import only `models`).
- Add to `evict_pipeline/src/evict_pipeline/__init__.py` `__all__` and import.
- Wire into `EvictPipeline.__init__` and the `run` sequence in `evict_pipeline/src/evict_pipeline/pipeline.py`.
- Add a mock-based test in `evict_pipeline/tests/test_pipeline.py` mirroring `test_pipeline_tp`.
- Mirror the step in every entry-point script's inline loop (`evaluate.py`, `run_juliet_poc.py`, `benchmark_juliet_sampling.py`, `benchmark_cwe_bench.py`) — or refactor to call `EvictPipeline.run` (see ARCHITECTURE.md "Duplicated orchestration" anti-pattern).

**New LLM provider (e.g. Mistral direct API):**
- Add an `elif self.provider == "mistral":` branch in `Verifier.__init__` (`evict_pipeline/src/evict_pipeline/verifier.py:12-48`) and a matching branch in `_sample_llm` (`verifier.py:159-201`).
- Update provider auto-detection in `scripts/benchmark_juliet_sampling.py:25-33`, `scripts/benchmark_cwe_bench.py:56-64`, `scripts/run_juliet_poc.py:31-46`.
- Add the env var to `README.md:13-15`.

**New CWE hint:**
- Add an entry to the `hints` dict in `Verifier._build_prompt` (`evict_pipeline/src/evict_pipeline/verifier.py:99-103`). Key is the numeric CWE as a string.

**New benchmark dataset:**
- Add `scripts/benchmark_<dataset>.py` mirroring `benchmark_cwe_bench.py` (sys.path append, provider auto-detect, ground-truth loader, inline 4-step loop, CSV writer, inline metric computation).
- Place ground truth under `data/<dataset>/data/`.
- Add a `--sarif_dir`/`--gt_path`/`--output` argparse block.

**New metric / post-hoc analysis:**
- Add `scripts/analyze_<dataset>_<metric>.py` mirroring `analyze_juliet_performance.py` (read CSV from `artifacts/exports/`, compute metrics, write `*_summary.md`).
- Wire into `scripts/generate_paper_csv.py` / `generate_paper_table.py` glob if it produces a `*_summary.md`.

**New SARIF generator:**
- Add `scripts/generate_<tool>.sh` mirroring `generate_full_juliet_sarif.sh` (build → run analyzer → write `data/<dataset>_sarifs/*.sarif`).
- Vendor the analyzer under `bin/` if it is a static distribution.

**New test:**
- Pipeline unit test: `evict_pipeline/tests/test_<thing>.py` using `pytest` + `unittest.mock.MagicMock` for external stages.
- Extractor/integration test: `tests/test_<thing>.py` with a fixture SARIF alongside.

**New Pydantic field on a model:**
- Edit `evict_pipeline/src/evict_pipeline/models.py`; Pydantic v2 syntax (`Field(default_factory=...)`, `Optional[...]`).
- Update any place that constructs the model (`extractor.py:30`, `extractor.py:82`, `verifier.py:53`, `verifier.py:70`, `verifier.py:85`) and the CSV writers that read its fields.

**New paper section / figure:**
- Section: add `sections/<name>.tex` and `\input{sections/<name>}` in `main.tex`.
- Figure: drop into `figures/`, regenerate via `scripts/generate_figures.py` if programmatic.

## Special Directories

**`venv/` and `evict_pipeline/venv/`:**
- Purpose: Python virtualenvs.
- Generated: Yes (by `python -m venv`).
- Committed: No (gitignored).

**`data/` (bulk):**
- Purpose: datasets + vendored baselines. Most contents are large and/or gitignored; `data.tar.gz` / `data.zip` (~2.3 GB each) at the repo root are archive snapshots.
- Generated: Partially — Juliet sources are checked out by `setup_juliet_*.sh`; CWE-Bench-Java by `setup_cwe_bench.sh`; SARIFs generated by the `generate_*.sh` scripts; CodeQL DBs by IRIS.
- Committed: Mix — `data/iris-v2/`, `data/cwe-bench-java/`, `data/literature_exports/` are committed; `data/juliet_java/`, `data/juliet_sarifs/`, SARIF files, and CodeQL DBs are generated locally. `.keep` and `.gitignore` guard the dir.

**`artifacts/exports/`:**
- Purpose: benchmark result CSVs + summaries — the bridge from pipeline runs to paper tables.
- Generated: Yes (by benchmark + analysis scripts).
- Committed: Yes (summaries + selected CSVs are committed; very large raw CSVs may be excluded).

**`bin/`:**
- Purpose: vendored static analyzer distributions (SpotBugs 4.8.4, PMD 7.1.0).
- Generated: No (downloaded manually or via `setup_*.sh`).
- Committed: Yes (binary distributions).

**`data/iris-v2/codeql/` and `data/iris-v2/codeql.zip`:**
- Purpose: patched CodeQL CLI required by IRIS (~800 MB zip).
- Generated: No (downloaded from IRIS releases).
- Committed: `codeql/` is committed; `codeql.zip` is a local archive.

**`evict_pipeline/src/evict_pipeline.egg-info/`:**
- Purpose: setuptools editable-install metadata.
- Generated: Yes (by `pip install -e .`).
- Committed: No.

**`__pycache__/` / `.pytest_cache/`:**
- Purpose: Python bytecode + pytest cache.
- Generated: Yes.
- Committed: No.

---

*Structure analysis: 2026-06-20*
