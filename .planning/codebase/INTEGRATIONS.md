# External Integrations

**Analysis Date:** 2026-06-20

## APIs & External Services

**LLM Providers (EVICT pipeline — `evict_pipeline/src/evict_pipeline/verifier.py`):**
- **OpenAI** — GPT-4o, GPT-4o-mini, GPT-5-nano, o1 family.
  - SDK/Client: `openai` 2.32.0 (`openai.OpenAI(api_key=..., base_url=...)`).
  - Auth: `OPENAI_API_KEY` env var (or `LOCAL_LLM_URL` + dummy key for local servers).
  - Default model: `gpt-4o-mini` (`verifier.py:19`).
  - Restricted models (names containing `nano` or starting with `o1`) are force-pinned to `temperature=1.0` (`verifier.py:23-24`).
- **Google Gemini** — Gemini 2.5 Flash Lite, 3.1 Flash Lite / Preview.
  - SDK/Client: `google-genai` 1.73.1 (`genai.Client(api_key=..., http_options={"api_version": version})`).
  - Auth: `GEMINI_API_KEY` env var.
  - Default model: `gemini-2.5-flash-lite` (`verifier.py:33`).
  - API version routing logic at `verifier.py:39-44`: `v1beta` for preview/experimental/2.5 models, `v1` for stable 1.5/2.0/3.x.
- **Anthropic Claude** — Claude 3.5 Sonnet, Claude Haiku 4.5.
  - SDK/Client: `anthropic` 0.97.0 (`anthropic.Anthropic(api_key=...)`), lazy-imported inside the `elif self.provider == "anthropic":` branch (`verifier.py:27-29`).
  - Auth: `ANTHROPIC_API_KEY` env var.
  - Default model: `claude-3-5-sonnet-20241022` (`verifier.py:28`).
  - Calls use `client.messages.create(..., max_tokens=1024, temperature=...)` (`verifier.py:172-177`).

**Local LLM Servers (optional, OpenAI-compatible):**
- **Ollama / vLLM / DeepSeek 7B** — routed through the OpenAI SDK by setting `LOCAL_LLM_URL` and `LOCAL_MODEL_NAME`. See `scripts/run_juliet_poc.py:29-46`. When `LOCAL_LLM_URL` is set, `api_key` falls back to the literal `"local-key"` if no real key is present.

**LLM Providers (IRIS v2 baseline — `data/iris-v2/src/models/`):**
- **OpenAI** (`gpt.py`, `openaimodels.py`) — `OPENAI_API_KEY`.
- **Google Gemini** (`gemini.py`) — uses the legacy `google.generativeai` SDK and `GOOGLE_API_KEY` (note: different var name than EVICT's `GEMINI_API_KEY`).
- **Ollama** (`ollama.py`) — `OLLAMA_HOST`, model map `qwen2.5-coder:latest`, `qwen2.5:32b`, `llama3.2:latest`, `deepseek-r1:32b`, `deepseek-r1:latest`.
- **Hugging Face local models** (`llm.py`, `codellama.py`, `codet5.py`, `llama.py`, `mistral.py`, `qwen.py`, `starcoder.py`, `wizarcoder.py`, `deepseek.py`, `codegen.py`, `google.py`) — via `transformers` + `torch`, optional vLLM backend (`vllm.LLM(tensor_parallel_size=8, ...)`). Sets `PYTORCH_CUDA_ALLOC_CONF` env in each module.
- Together AI (`*-tai` prefix in `llm.py:39`).

**Static Analyzers (invoked as external CLI binaries, not APIs):**
- **PMD 7.1.0** — `bin/pmd-bin-7.1.0/bin/pmd check -d <src> -R category/java/security.xml -f sarif -r <out>`. Installed by `scripts/setup_juliet_pmd.sh` from `github.com/pmd/pmd/releases`.
- **SpotBugs 4.8.4** — `bin/spotbugs-4.8.4/bin/spotbugs -textui -sarif -output <out> -effort:max -low -auxclasspath <support> <classes>`. Installed by `scripts/setup_juliet_spotbugs.sh`. Requires pre-compiled `.class` files (Gradle `:cweXXX:classes` task).
- **CodeQL v2.23.2** — `codeql database create` then `codeql database analyze <db> java/ql/src/Security/ --format=sarif-latest --output=<out>`. Bundled in `data/iris-v2/codeql/` (also available system-wide at `/opt/homebrew/bin/codeql`).

**Symbolic Execution / SMT (invoked in-process or as stubs):**
- **Z3** — `z3-solver` 4.16.0.0, imported in `evict_pipeline/src/evict_pipeline/escalator.py:2` (`from z3 import Solver, parse_smt2_string, sat, unsat, unknown`). Solver timeout configurable via `Escalator(timeout_ms=5000)`. The actual `solver.check()` call is currently commented out (`escalator.py:50-53`) — `_solve_smt` returns `"UNKNOWN"` as a placeholder.
- **Java PathFinder (JPF)** — referenced as a stub `Escalator._run_jpf` (`escalator.py:57-59`); not yet wired. The implementation plan (`implementation.md`) commits to JPF over KLEE for Java targets.
- **KLEE** — referenced as a stub `Escalator._run_klee` (`escalator.py:61-63`); intended for C/C++ targets, deferred.

## Data Storage

**Databases:**
- None. No SQL/NoSQL database is used anywhere in the EVICT pipeline or IRIS v2 orchestration.

**File Storage:**
- **Local filesystem only.**
- Raw analyzer output: SARIF JSON files in `data/` (`juliet_alerts_pmd.sarif`, `juliet_alerts_spotbugs.sarif`) and per-CWE files in `data/juliet_sarifs/` (112 files).
- CodeQL results: `artifacts/codeql_results/*.sarif`.
- Triage results: CSV files in `artifacts/exports/` and `artifacts/exports/v2/` (e.g., `juliet_sampled_results_claude_haiku_4_5.csv`, `juliet_evict_results_gpt_4o_mini.csv`).
- Ground truth: `data/cwe-bench-java/data/fix_info.csv` (file + method range), `data/iris-v2/data/fix_info.csv`, `data/iris-v2/data/build_info.csv`, `data/iris-v2/data/project_info.csv`.
- Juliet source: `data/juliet_java/juliet-cwe<NNN>/src/main/java/...` (~120 CWE modules).
- CWE-Bench-Java source: `data/iris-v2/data/project-sources/` (fetched by IRIS `fetch_one.py`).
- CodeQL databases: `data/iris-v2/data/codeql-dbs/*-docker/`.

**Caching:**
- None (no Redis, no on-disk LLM response cache). Resumability is achieved via fingerprinting alerts in the output CSVs (`scripts/run_juliet_poc.py:18-20, 60-74`) — already-triaged alerts are skipped on re-run.

## Authentication & Identity

**Auth Provider:**
- None for the EVICT pipeline itself. All auth is API-key based to external LLM providers, passed via environment variables.
- IRIS v2 Docker image (`data/iris-v2/Dockerfile`) does not bake in any credentials; API keys are expected at runtime.

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, no Rollbar, no structured error tracking).

**Logs:**
- Ad hoc log files in the repo root: `error.log`, `error_deepseek.log`, `error_gpt-4o-mini.log`, `out.log`, `out_deepseek.log`, `out_gpt-4o-mini.log`, `poc_error.log`, `poc_progress.log`, `sarif_generation.log`. These are unstructured stdout/stderr captures, not managed logging.
- `rich.console.Console` is used for terminal output in `evict_pipeline/evaluate.py`.
- IRIS v2 has its own `src/logger.py` and `src/utils/mylogger.py`.
- No `logging` framework configuration in EVICT core — `verifier.py` and `escalator.py` swallow exceptions and append error strings into the `Decision.rationale` field.

## CI/CD & Deployment

**Hosting:**
- None. This is a local research workspace; results are produced as CSVs/PDFs on disk.

**CI Pipeline:**
- None detected. No `.github/workflows/`, no `tox.ini`, no `Makefile` test target, no CI config in `.gitlab-ci.yml` or `azure-pipelines.yml`. Tests are run manually via `pytest evict_pipeline/tests`.

## Environment Configuration

**Required env vars (by integration):**

| Env var | Used by | Purpose | File |
|---|---|---|---|
| `OPENAI_API_KEY` | EVICT Verifier, IRIS gpt.py | OpenAI auth | `evict_pipeline/src/evict_pipeline/verifier.py:20`, `scripts/benchmark_*.py`, `data/iris-v2/src/models/gpt.py:23` |
| `GEMINI_API_KEY` | EVICT Verifier | Google GenAI auth (new SDK) | `scripts/benchmark_*.py`, `evict_pipeline/evaluate.py:30` |
| `GOOGLE_API_KEY` | IRIS gemini.py | Google Generative AI auth (legacy SDK) | `data/iris-v2/src/models/gemini.py:25` |
| `ANTHROPIC_API_KEY` | EVICT Verifier | Anthropic Claude auth | `scripts/benchmark_juliet_sampling.py:30`, `scripts/benchmark_cwe_bench.py:61` |
| `LOCAL_LLM_URL` | run_juliet_poc.py | OpenAI-compatible local server base URL | `scripts/run_juliet_poc.py:29` |
| `LOCAL_MODEL_NAME` | run_juliet_poc.py | Override model id for local LLM | `scripts/run_juliet_poc.py:30, 152` |
| `OLLAMA_HOST` | IRIS ollama.py | Ollama server host | `data/iris-v2/src/models/ollama.py:29` |
| `DOCKER_HOST` | IRIS docker_utils.py | Remote Docker daemon URL | `data/iris-v2/scripts/docker_utils.py:13` |
| `JAVA_HOME` | setup_juliet_spotbugs.sh, generate_full_juliet_sarif.sh, IRIS build_codeql_dbs.py | JDK location | `scripts/setup_juliet_spotbugs.sh:24`, `data/iris-v2/scripts/build_codeql_dbs.py:62` |
| `PYTORCH_CUDA_ALLOC_CONF` | IRIS local model modules | CUDA memory allocator tuning | `data/iris-v2/src/models/{codellama,codet5,codegen,deepseek,llama,mistral,qwen,starcoder,google}.py` |

**Secrets location:**
- Out-of-band (user's shell environment). No `.env` file committed; `.gitignore` does not explicitly exclude `.env` but none is present. The forbidden-files audit confirmed no secret files exist in the working tree.

## Webhooks & Callbacks

**Incoming:**
- None. EVICT is a batch CLI tool — it reads SARIF from disk and writes CSV to disk. No HTTP server, no webhook receiver.

**Outgoing:**
- None beyond the LLM API calls described above. No Slack/Teams/email notifications, no result-posting webhooks.

## Inter-Submodule Integration

**EVICT ↔ IRIS v2 (`data/iris-v2/`):**
- EVICT shells out to IRIS v2 scripts to build CodeQL databases: `scripts/generate_sarifs.sh:27` invokes `python3 scripts/build_codeql_dbs.py --use-container --db-path "$DB_DIR"` from inside `data/iris-v2/`.
- EVICT consumes the SARIF output that IRIS/CodeQL produces; no Python-level import of `iris.py` from EVICT core.
- IRIS v2 is treated as a vendored tool, not a versioned dependency. `setup_cwe_bench.sh` clones it from `github.com/iris-sast/iris.git --branch v2`.

**EVICT ↔ CWE-Bench-Java (`data/cwe-bench-java/`):**
- EVICT reads `data/cwe-bench-java/data/fix_info.csv` as ground truth (`scripts/benchmark_cwe_bench.py:152` default `--gt_path`).
- CWE-Bench-Java provides per-project build metadata (`build_info.csv`, `project_info.csv`) consumed by IRIS's `build_codeql_dbs.py`.

**EVICT ↔ Juliet (`data/juliet_java/`):**
- EVICT's `Extractor._get_code_context` (`evict_pipeline/src/evict_pipeline/extractor.py:118-121`) falls back to `rglob` under `data/juliet_java/` to locate source files by basename when the SARIF path is not found directly.
- Ground truth for Juliet is computed at analysis time by `scripts/analyze_juliet_performance.py:47-73` — it parses each Java file to find `bad()` / `good()` method boundaries and labels alerts inside `bad*` methods as TP and `good*` methods as FP.

---

*Integration audit: 2026-06-20*
