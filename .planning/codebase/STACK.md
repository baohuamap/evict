# Technology Stack

**Analysis Date:** 2026-06-20

## Languages

**Primary:**
- Python 3.14.6 (runtime in `venv/`) — EVICT pipeline, benchmark scripts, analysis tooling. `evict_pipeline/pyproject.toml` declares `requires-python = ">=3.9"` so the package is source-compatible with 3.9+, but the committed virtualenv pins 3.14.
- LaTeX — NeurIPS 2026 manuscript (`main.tex`, `sections/*.tex`, `algorithm_env.tex`, `neurips_2026.sty`).
- Bash — setup and SARIF-generation automation (`scripts/*.sh`).

**Secondary:**
- Java (JDK 8 / 11 / 17) — Juliet benchmark target language and CodeQL/SpotBugs analysis subject. Juliet modules pin toolchain `JavaLanguageVersion.of(8)` in `data/juliet_java/build.gradle.kts`.
- Kotlin DSL (Gradle) — Juliet build scripts (`data/juliet_java/settings.gradle.kts`, `build.gradle.kts`).
- CodeQL QL — security queries run against Java projects (`data/iris-v2/codeql/java/`, invoked as `codeql database analyze ... java/ql/src/Security/`).
- Python (3.10, conda) — IRIS v2 subproject runtime, isolated in `data/iris-v2/environment.yml`.

## Runtime

**Environment:**
- Python 3.14.6 in committed virtualenv at `venv/` (interpreter `venv/bin/python3.14`).
- IRIS v2 expects a separate conda env `iris` (Python 3.10, PyTorch 2.5) per `data/iris-v2/environment.yml` — not installed in the repo venv.
- Java JRE/JDK required for PMD, SpotBugs, and Gradle builds. `scripts/setup_juliet_spotbugs.sh` and `scripts/generate_full_juliet_sarif.sh` hard-code `JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home` (macOS Homebrew path).
- Docker required for CWE-Bench-Java CodeQL database builds (`scripts/generate_sarifs.sh`, `scripts/run_full_cwe_bench.sh`, `data/iris-v2/Dockerfile`).

**Package Manager:**
- pip 26.0 (in `venv/`), setuptools `>=61.0` build backend declared in `evict_pipeline/pyproject.toml`.
- Lockfile: missing (no `requirements.txt`, no `pip-tools` lock, no `poetry.lock`). Dependencies float at `>=` floors.
- Conda for IRIS v2 (`data/iris-v2/environment.yml`).
- Gradle 6.8.2 / 7.6.4 / 8.9 and Maven 3.2.1 / 3.5.0 / 3.9.8 provisioned inside the IRIS Docker image (`data/iris-v2/Dockerfile`).

## Frameworks

**Core:**
- Pydantic 2.13.3 — data models for `Alert`, `EvidencePack`, `Decision`, `Label` in `evict_pipeline/src/evict_pipeline/models.py`.
- OpenAI SDK 2.32.0 — LLM verifier client (`evict_pipeline/src/evict_pipeline/verifier.py`).
- Google GenAI 1.73.1 — Gemini verifier client (`verifier.py`).
- Anthropic SDK 0.97.0 — Claude verifier client (`verifier.py`). Note: not declared in `pyproject.toml` dependencies; installed ad hoc in `venv/`.
- Z3 Solver 4.16.0.0 (`z3-solver`) — SMT backend for the symbolic escalator (`evict_pipeline/src/evict_pipeline/escalator.py`).

**Testing:**
- pytest 9.0.3 — unit tests in `evict_pipeline/tests/test_pipeline.py` and `tests/test_extractor_codeql.py`.

**Build/Dev:**
- black 26.3.1, isort 8.0.1, mypy 1.20.2 — dev extras from `pyproject.toml` `[project.optional-dependencies] dev`.
- setuptools `>=61.0` — PEP 621 build backend.
- Docker 7.1.0 (Python SDK) — used by `data/iris-v2/scripts/docker_utils.py` for containerized CodeQL builds; installed in `venv/` but not declared in `pyproject.toml`.
- LaTeX toolchain — `pdflatex` / `latexmk` (NeurIPS 2026 style file `neurips_2026.sty`, last revised Jan 2026). `main.fdb_latexmk` and `main.fls` indicate `latexmk` was the build driver.

## Key Dependencies

**Critical (declared in `evict_pipeline/pyproject.toml`):**
- `pydantic>=2.0.0` (installed 2.13.3) — all pipeline data structures.
- `openai>=1.0.0` (installed 2.32.0) — GPT-4o / GPT-4o-mini / GPT-5-nano / o1 calls.
- `google-genai>=0.1.0` (installed 1.73.1) — Gemini 2.5 Flash Lite / 3.1 Flash Lite calls.
- `z3-solver>=4.12.0` (installed 4.16.0.0) — SMT solving in `escalator.py`.
- `numpy>=1.24.0` (installed 2.4.4) — conformal quantile computation in `calibrator.py` (`np.quantile`, `np.ceil`).
- `pandas>=2.0.0` (installed 3.0.2) — used by IRIS v2 (`data/iris-v2/src/iris.py`); not directly imported by EVICT core.
- `scikit-learn>=1.2.0` (installed 1.8.0) — declared but no direct import in EVICT core; available for calibration experiments.
- `rich>=13.0.0` (installed 15.0.0) — terminal tables/console in `evict_pipeline/evaluate.py`.

**Installed but NOT declared in `pyproject.toml` (implicit dependencies):**
- `anthropic` 0.97.0 — Claude support in `verifier.py` line 27 (`import anthropic`).
- `docker` 7.1.0 — required by `data/iris-v2/scripts/docker_utils.py`.
- `scipy` 1.17.1, `joblib` 1.5.3, `threadpoolctl` 3.6.3 — transitive via scikit-learn.
- `matplotlib` / `seaborn` — used by `scripts/generate_figures.py` but NOT installed in `venv/` (script will fail without manual `pip install matplotlib seaborn`).

**Infrastructure (IRIS v2 conda env, `data/iris-v2/environment.yml`):**
- `pytorch=2.5`, `transformers`, `accelerate` — local Hugging Face model serving (CodeLlama, CodeT5, Llama, Mistral, Qwen, StarCoder, WizardCoder, DeepSeek).
- `google-generativeai` — legacy Gemini SDK (IRIS uses `google.generativeai`, EVICT uses the newer `google-genai`).
- `tqdm`, `requests` — IRIS orchestration.

## Configuration

**Environment:**
- No `.env` file committed. `.gitignore` excludes only `__pycache__`, `.DS_Store`, and LaTeX build artifacts — secrets must be supplied out-of-band.
- LLM provider selected at runtime by which `*_API_KEY` env var is set; precedence: `OPENAI_API_KEY` → `GEMINI_API_KEY` → `ANTHROPIC_API_KEY` (see `scripts/benchmark_juliet_sampling.py:25-33`, `scripts/benchmark_cwe_bench.py:56-64`).
- `LOCAL_LLM_URL` + `LOCAL_MODEL_NAME` route the OpenAI client at a local endpoint (Ollama / vLLM / DeepSeek 7B) — see `scripts/run_juliet_poc.py:29-46`.
- `DOCKER_HOST` consumed by `data/iris-v2/scripts/docker_utils.py:13` for remote Docker daemons.
- `OLLAMA_HOST` consumed by `data/iris-v2/src/models/ollama.py:29`.
- `GOOGLE_API_KEY` is the legacy var name in IRIS (`data/iris-v2/src/models/gemini.py:25`); EVICT uses `GEMINI_API_KEY`.

**Build:**
- `evict_pipeline/pyproject.toml` — PEP 621 project metadata, setuptools build backend, `src/` layout.
- `data/iris-v2/Dockerfile` — Ubuntu 22.04 base, installs OpenJDK 8/11/17, Maven 3.2.1/3.5.0/3.9.8, Gradle 6.8.2/7.6.4/8.9, Miniconda, CodeQL v2.23.2 (`github/codeql-cli-binaries/releases/download/v2.23.2/codeql.zip`).
- `data/iris-v2/dep_configs.json` + `dep_configs.linux_x64.json` — map JDK/Maven/Gradle versions to install paths.
- `data/iris-v2/environment.yml` — conda env spec for IRIS v2.
- `data/juliet_java/build.gradle.kts` + `settings.gradle.kts` — Gradle Kotlin DSL multi-module build for ~120 CWE modules.
- `neurips_2026.sty` + `main.tex` — LaTeX paper build (`latexmk -pdf main.tex`).

## Platform Requirements

**Development:**
- macOS (Homebrew paths in `scripts/setup_juliet_spotbugs.sh:24`) or Linux (IRIS Docker image is `ubuntu:22.04`).
- Python 3.9+ (3.14 in the committed venv).
- Java JDK 8 for Juliet compilation, JDK 17 for SpotBugs runner.
- Docker Desktop / daemon for CWE-Bench-Java builds.
- CodeQL CLI on `PATH` (`which codeql` resolves to `/opt/homebrew/bin/codeql` on this machine; IRIS ships its own at `data/iris-v2/codeql/codeql`).
- LaTeX distribution with `pdflatex`, `bibtex`, `latexmk`, and `tikz` for paper builds.

**Production:**
- No production deployment target. This is a research artifact: the "deliverables" are (a) the LaTeX PDF (`main.pdf`) and (b) CSV result exports in `artifacts/exports/` and `artifacts/exports/v2/`.
- Benchmarks are run ad hoc from a developer workstation against LLM APIs; `scripts/run_full_cwe_bench.sh` estimates 20–60 hours for the full CWE-Bench-Java sweep.

---

*Stack analysis: 2026-06-20*
