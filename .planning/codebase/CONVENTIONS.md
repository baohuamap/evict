# Coding Conventions

**Analysis Date:** 2026-06-20

## Project Shape

This is a hybrid research workspace: a Python pipeline package (`evict_pipeline/`) plus
standalone benchmark/reporting scripts (`scripts/`) plus a LaTeX paper. The conventions
below apply to the Python code; bash scripts in `scripts/` follow a separate shell
convention set documented at the end.

The canonical convention reference committed in the repo is `GEMINI.md` (sections
"Development Conventions" and "Coding Standards"). Follow it; this document elaborates
on what is actually observed in the code.

## Naming Patterns

**Files:**
- `snake_case.py` for all Python modules: `evict_pipeline/src/evict_pipeline/extractor.py`,
  `evict_pipeline/src/evict_pipeline/verifier.py`, `scripts/benchmark_juliet_sampling.py`.
- Test files use the `test_*.py` prefix: `evict_pipeline/tests/test_pipeline.py`,
  `tests/test_extractor_codeql.py`.
- Bash scripts use `lower_snake_case.sh` or `lower_hyphen.sh`: `scripts/generate_sarifs.sh`,
  `scripts/run_full_cwe_bench.sh`, `scripts/setup_cwe_bench.sh`.
- Class-per-file: each pipeline stage is its own module (`extractor.py`, `verifier.py`,
  `calibrator.py`, `escalator.py`, `pipeline.py`, `models.py`).

**Classes:**
- `PascalCase` for all classes: `Extractor`, `Verifier`, `Calibrator`, `Escalator`,
  `EvictPipeline` (`evict_pipeline/src/evict_pipeline/pipeline.py:8`).
- Pydantic model classes are `PascalCase` nouns: `Alert`, `EvidencePack`, `Decision`
  (`evict_pipeline/src/evict_pipeline/models.py:10`).
- Enums are `PascalCase` with `UPPER_SNAKE` members: `Label(str, Enum)` with
  `TP`, `FP`, `ABSTAIN` (`evict_pipeline/src/evict_pipeline/models.py:5`).

**Functions / methods:**
- `snake_case` for public methods: `extract_from_sarif`, `populate_evidence`,
  `get_decision`, `calibrate`, `escalate`, `run_on_sarif`.
- Leading underscore for private helpers: `_extract_cwe_id`,
  `_get_code_context`, `_extract_path_constraints` (`evict_pipeline/src/evict_pipeline/extractor.py`),
  `_build_prompt`, `_sample_llm` (`evict_pipeline/src/evict_pipeline/verifier.py`),
  `_solve_smt`, `_run_jpf`, `_run_klee` (`evict_pipeline/src/evict_pipeline/escalator.py`).
- Top-level script entry points are `snake_case` verbs: `run_sampling_benchmark`,
  `run_benchmark`, `run_poc`, `analyze_results`, `generate_csv`, `generate_table`
  (`scripts/`).

**Variables:**
- `snake_case` for locals and module attributes: `sarif_data`, `flow_path`,
  `project_root`, `processed_fingerprints`, `safe_model_name`.
- Module-level constants are `UPPER_SNAKE`: `ROOT_DIR`, `FIGURES_DIR`
  (`scripts/generate_figures.py:7`).

**Environment variables:**
- `UPPER_SNAKE` throughout: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`,
  `LOCAL_LLM_URL`, `LOCAL_MODEL_NAME`, `JAVA_HOME`.
- Read via `os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") ...`
  with a gemini fallback (`scripts/benchmark_juliet_sampling.py:25`).

**Types:**
- Type aliases are not introduced; types are imported from `typing` and used inline.

## Code Style

**Formatting:**
- 4-space indentation throughout the `evict_pipeline` package and `scripts/`.
- Line length is not strictly enforced; long `print`/f-string lines and prompt
  literals in `verifier._build_prompt` run well past 100 chars.
- Black `>=23.0.0`, isort `>=5.12.0`, mypy `>=1.0.0` are declared as dev extras in
  `evict_pipeline/pyproject.toml:22-28`. Installed versions (venv): black 26.3.1,
  isort 8.0.1, mypy 1.20.2.
- **No formatter/linter config files exist** — no `.black`, `pyproject` `[tool.black]`
  section, `[tool.isort]` section, `mypy.ini`, `.mypy.ini`, `setup.cfg`, `tox.ini`,
  `.flake8`, or `.pre-commit-config.yaml`. Tooling is declared but unconfigured; run
  black/isort/mypy with defaults. GEMINI.md mandates "strict typing with Mypy" — treat
  that as the project's stated intent even though no config enforces it.

**Linting:**
- Mypy is the intended type checker (per `GEMINI.md` "Type Safety" section). No
  `mypy.ini` / `[tool.mypy]` config — run `mypy evict_pipeline/src` with defaults.

**Imports:**
- Use `typing` module forms (`List`, `Dict`, `Any`, `Optional`, `Tuple`) — NOT PEP 585
  lowercase generics — across the package and scripts
  (`evict_pipeline/src/evict_pipeline/models.py:2`,
  `evict_pipeline/src/evict_pipeline/verifier.py:4`).
- Newer Python 3.10+ syntax (`list[str]`, `X | Y`) is avoided even though the venv
  runs Python 3.14; this keeps the `requires-python = ">=3.9"` floor in
  `evict_pipeline/pyproject.toml:10` honest.
- One exception: `evict_pipeline/src/evict_pipeline/escalator.py:39` uses
  `list[str]` in a hint — follow the `typing.List` convention used everywhere else
  for consistency.

## Import Organization

**Order (observe in every module):**
1. Standard library: `json`, `os`, `re`, `csv`, `sys`, `random`, `time`, `pathlib`,
   `enum`, `collections`, `argparse`.
2. Third-party: `pydantic`, `openai`, `numpy`, `z3`, `rich`, `matplotlib`, `seaborn`.
3. Local package: `from .models import ...`, `from evict_pipeline import ...`.

**Lazy / conditional imports:**
- Provider-specific SDKs are imported lazily inside `Verifier.__init__` branches:
  `import anthropic` and `from google import genai` are only loaded when the
  corresponding provider is selected (`evict_pipeline/src/evict_pipeline/verifier.py:27`,
  `:31`, `:180`). Keep this pattern — it avoids hard deps on all three SDKs.
- `import argparse` is deferred to inside `if __name__ == "__main__":` blocks in
  `scripts/benchmark_juliet_sampling.py:128`, `scripts/benchmark_cwe_bench.py:148`,
  `scripts/run_juliet_poc.py:141`. Follow this for CLI scripts so the library
  functions stay importable without argparse overhead.

**Path aliases:**
- No `PYTHONPATH` aliases or `pyproject` `[tool.setuptools.packages.find]` src layout
  exposure beyond `where = ["src"]` (`evict_pipeline/pyproject.toml:30`).
- Standalone scripts that need the package without an installed editable wheel use a
  `sys.path.append` bootstrap:
  ```python
  sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))
  ```
  (`scripts/benchmark_juliet_sampling.py:11`, `scripts/benchmark_cwe_bench.py:10`,
  `scripts/run_juliet_poc.py:10`, `tests/test_extractor_codeql.py:6`).
  Prefer `pip install -e "./evict_pipeline[dev]"` (per `GEMINI.md`) over this hack
  for new code; only use the bootstrap for one-off scripts.

## Type Hinting

**Convention: annotate all function signatures and Pydantic fields.**

- Public methods carry full annotations:
  `def run(self, alert: Alert, project_root: str) -> Decision:`
  (`evict_pipeline/src/evict_pipeline/pipeline.py:17`).
- Private helpers annotated too:
  `def _build_prompt(self, alert: Alert) -> str:`
  (`evict_pipeline/src/evict_pipeline/verifier.py:94`).
- Pydantic fields carry explicit types and `Optional[...]` / `Field(default_factory=...)`
  for mutable defaults (`evict_pipeline/src/evict_pipeline/models.py:14-17`).
- Locals inside functions are generally NOT annotated (relies on inference); follow
  that — don't over-annotate locals.

## Error Handling

**Strategy: fail-soft inside the pipeline, fail-loud at script top level, never crash
a long-running benchmark on a single alert.**

**Patterns:**

1. **Per-sample LLM resilience** — `Verifier._sample_llm` wraps each LLM call in its
   own `try/except Exception`; on failure it appends
   `(Label.ABSTAIN, f"Error calling {self.provider}: {str(e)}")` and continues
   (`evict_pipeline/src/evict_pipeline/verifier.py:200-201`). Any API error becomes
   an ABSTAIN vote rather than crashing the run. Keep this — it is the core
   resilience pattern for the LLM stage.

2. **Missing-evidence early return** — `Verifier.get_decision` returns a synthetic
   `Decision(label=ABSTAIN, confidence=0.0, rationale="Missing evidence pack.")`
   when `alert.evidence_pack` is None
   (`evict_pipeline/src/evict_pipeline/verifier.py:52-59`). Same shape for empty
   response counts (`:69-76`). Follow this "return a Decision, never raise" contract
   for the verifier.

3. **File-read fallback** — `Extractor._get_code_context` catches `Exception` and
   returns a `// Error reading source file: {e}` comment string instead of raising
   (`evict_pipeline/src/evict_pipeline/extractor.py:137`). Also returns
   `// Could not read source file: {path}` when no file matches (`:126`). The
   pipeline keeps going with a sentinel slice.

4. **SMT solver fallback** — `Escalator._solve_smt` catches `Exception` and returns
   `"UNKNOWN"`, which the caller maps to continued abstention
   (`evict_pipeline/src/evict_pipeline/escalator.py:54-55`). Note the actual Z3
   `parse_smt2_string` call is commented out (`:48-52`) and the method currently
   always returns `"UNKNOWN"` — this is a stub, not a real implementation.

5. **Per-alert try/except in benchmarks** — every benchmark loop wraps the per-alert
   pipeline call in `try/except Exception`, prints `Error processing alert
   {alert_id}: {e}`, and continues to the next alert
   (`scripts/benchmark_juliet_sampling.py:122-123`,
   `scripts/benchmark_cwe_bench.py:119-120`, `scripts/run_juliet_poc.py:135-136`).
   This is mandatory for long runs — never let one alert kill a 15k-alert sweep.

6. **Top-level script guard** — `evict_pipeline/evaluate.py` wraps the whole
   pipeline execution in `try/except Exception` and prints a red rich-console error
   then `return`s (`evict_pipeline/evaluate.py:45-63`). This is the only place a
   caught exception terminates the run.

7. **No custom exception classes** — the codebase uses bare `Exception` catches and
   `ValueError` (`evict_pipeline/src/evict_pipeline/verifier.py:48` for unsupported
   provider). Do not introduce custom exception hierarchies unless a phase explicitly
   calls for them; the project style is to map errors into `Label.ABSTAIN` or a
   sentinel string.

## Logging

**Framework:** `print()` for scripts and benchmarks; `rich.console.Console` for the
interactive CLI `evict_pipeline/evaluate.py`. The stdlib `logging` module is **not**
used anywhere.

**Patterns:**
- Progress lines: `print(f"[{i+1}/{len(selected_alerts)}] Triage {alert.alert_id}...")`
  (`scripts/run_juliet_poc.py:111`).
- Section banners: `print("--- Processing {cwe_id} ---")`
  (`scripts/benchmark_juliet_sampling.py:79`), `print("=== [Phase 1] ... ===")`
  in bash.
- Summary blocks: `print("\n--- Benchmark Summary ---")` followed by metric lines
  (`scripts/benchmark_cwe_bench.py:140-145`).
- Rich tables for CLI: `evict_pipeline/evaluate.py:66-86` builds a `Table` with
  colored columns (`style="cyan"`, `style="magenta"`) and uses
  `console.print(f"[red]Error...[/red]")` for errors.
- Error logs are also written to per-provider log files at the repo root
  (`out_deepseek.log`, `out_gpt-4o-mini.log`, `error_deepseek.log`, etc.) by the
  benchmark runners via shell redirection, not via Python logging.

**When to log:** Print a start banner, per-item progress, per-item errors (continue),
and a final summary. Match this cadence in new scripts.

## Comments

**When to comment:**
- Use `#` line comments to mark pipeline steps and intent:
  `# Step 2: EvidencePack construction` (`evict_pipeline/src/evict_pipeline/pipeline.py:30`),
  `# Step 3: LLM reasoning: guide prompting with evidence` (`:33`).
- Use `#` for fallback/resumability notes: `# Fallback search if file is not found`
  (`evict_pipeline/src/evict_pipeline/extractor.py:114`), `# Resumability: Skip if
  the SARIF for this project already exists` (`scripts/generate_sarifs.sh:40`).
- Use `#` for known stubs/placeholders: `# Placeholder for heuristic extraction`
  (`evict_pipeline/src/evict_pipeline/extractor.py:97`), `# Placeholder for actual
  parsing` (`evict_pipeline/src/evict_pipeline/escalator.py:50`). Always mark
  unfinished work this way.
- Use `#` to note non-obvious model-version routing logic
  (`evict_pipeline/src/evict_pipeline/verifier.py:35-44`).

**JSDoc/TSDoc:** Not applicable (Python). Use triple-quote docstrings instead — see
"Docstrings" below.

**Docstrings:**
- Every class has a one-line triple-quote docstring: `"""LLM-based verification
  stage of the EVICT pipeline."""` (`evict_pipeline/src/evict_pipeline/verifier.py:10`).
- Public methods get triple-quote docstrings describing behavior:
  `"""Runs the verifier and aggregates results using vote-share."""`
  (`evict_pipeline/src/evict_pipeline/verifier.py:51`).
- Pydantic models carry class docstrings: `"""Structured evidence extracted from
  analyzer output and code."""` (`evict_pipeline/src/evict_pipeline/models.py:11`).
- Multi-line docstrings document the workflow steps inside `EvictPipeline.run`
  (`evict_pipeline/src/evict_pipeline/pipeline.py:18-26`).
- No Args/Returns/Raises sections are used — keep docstrings prose-style and short.

## Function Design

**Size:** Functions run 5-40 lines. The longest is `Verifier._build_prompt`
(~60 lines, mostly a big f-string) — acceptable because it is a single prompt
template. `analyze_juliet_performance.analyze_results` (~130 lines) is the outlier;
new analysis functions should be split by metric group.

**Parameters:**
- Keyword-friendly: `Verifier.__init__(self, api_key, model_name=None, provider="openai",
  base_url=None, temperature=None)` (`evict_pipeline/src/evict_pipeline/verifier.py:12`).
- `Optional[...]` with `None` defaults for anything not required.
- Boolean flags use plain defaults: `flow_partial: bool = False`
  (`evict_pipeline/src/evict_pipeline/models.py:20`).

**Return values:**
- Pipeline stages return Pydantic models (`Alert`, `Decision`) or `List[...]` of them,
  never dicts. Follow this — the Pydantic model IS the contract.
- Sentinels for failures: `Label.ABSTAIN` decisions, `"UNKNOWN"` strings from the
  escalator, `// Error reading source file: ...` strings from the extractor. Document
  the sentinel in the docstring when you add one.
- Calibrator mutates and returns the same `Decision` instance
  (`evict_pipeline/src/evict_pipeline/calibrator.py:11-26`); escalator does the same
  (`escalator.py:11-37`). Mutation-in-place is accepted for `Decision` — do not copy.

## Module Design

**Exports:**
- `evict_pipeline/src/evict_pipeline/__init__.py` re-exports the full public surface
  with an explicit `__all__` list (`Label`, `Alert`, `EvidencePack`, `Decision`,
  `Extractor`, `Verifier`, `Calibrator`, `Escalator`, `EvictPipeline`). Consumers
  should `from evict_pipeline import X` — not `from evict_pipeline.verifier import X`.
- New public classes/models go in their own module under
  `evict_pipeline/src/evict_pipeline/` AND get added to `__init__.py`'s `__all__`.

**Barrel files:** Only `__init__.py` is used as a barrel. No `models/__init__.py`
or similar aggregation.

**Pydantic-first data modeling:** All structured data crossing module boundaries is
a Pydantic `BaseModel` (`evict_pipeline/src/evict_pipeline/models.py`). This is
mandated by `GEMINI.md` ("Data Modeling"). New structured types go here as Pydantic
v2 models, not dataclasses or TypedDict.

**Stage-per-module pattern:** One class per pipeline stage in its own file, wired
together in `EvictPipeline.__init__` via dependency injection
(`evict_pipeline/src/evict_pipeline/pipeline.py:11-15`). New stages follow this:
new file, new class, inject into `EvictPipeline`.

## Configuration & Environment

**Environment:**
- `requires-python = ">=3.9"` in `evict_pipeline/pyproject.toml:10`.
- The committed venvs (`venv/` and `evict_pipeline/venv/`) both run Python 3.14.6 —
  a discrepancy from the declared floor. Code must still avoid 3.10+ syntax (see
  "Imports") so the package remains installable on 3.9.
- API keys are read from env at runtime; no `.env` loader is used. Scripts print
  `Error: No API key found.` and `return` when none is set
  (`scripts/benchmark_juliet_sampling.py:35-37`).

**Build:**
- `evict_pipeline/pyproject.toml` is the only Python build config (setuptools backend,
  src layout). No `setup.py`, no `setup.cfg`, no `requirements.txt`.
- Install with `pip install -e "./evict_pipeline[dev]"` (`GEMINI.md`).

## Shell Script Conventions (`scripts/*.sh`)

- Start every script with `set -e` (`scripts/generate_sarifs.sh:6`,
  `scripts/run_full_cwe_bench.sh:6`, `scripts/setup_cwe_bench.sh:5`,
  `scripts/generate_full_juliet_sarif.sh:2`).
- Capture the repo root once: `PROJECT_ROOT=$(pwd)`
  (`scripts/generate_sarifs.sh:8`, `scripts/run_full_cwe_bench.sh:8`,
  `scripts/generate_mini_benchmark.sh:19`). Derive paths as
  `$PROJECT_ROOT/data/...`, `$PROJECT_ROOT/artifacts/...`.
- Always `mkdir -p` output directories before writing
  (`scripts/generate_sarifs.sh:13`, `scripts/run_full_cwe_bench.sh:13`).
- Activate the venv when Python deps are needed:
  `source "$PROJECT_ROOT/venv/bin/activate"` (`scripts/generate_sarifs.sh:19`,
  `scripts/run_full_cwe_bench.sh:54`).
- Append `|| true` to analyzer commands that exit non-zero on findings
  (SpotBugs/PMD return non-zero when bugs are found):
  `... spotbugs ... || true` (`scripts/setup_juliet_spotbugs.sh:39`,
  `scripts/setup_juliet_pmd.sh:37`, `scripts/generate_full_juliet_sarif.sh:40`).
- Resumability via skip-if-output-exists:
  ```bash
  if [ -f "$output_sarif" ]; then
      echo "Skipping $slug (already analyzed)"
      continue
  fi
  ```
  (`scripts/generate_sarifs.sh:41-44`, `scripts/run_full_cwe_bench.sh:38-41`).
  Always add this guard around the expensive per-project step.
- `cd` into subdirectories and `cd ../..` or `cd "$PROJECT_ROOT"` back rather than
  using `pushd/popd` (`scripts/generate_full_juliet_sarif.sh:16-18`).
- Header comment block naming the script and its phase purpose:
  `# scripts/generate_sarifs.sh` / `# Phase 1: Build CodeQL databases ...`
  (`scripts/generate_sarifs.sh:3-4`).

## Resumability Pattern (cross-language)

Long-running benchmark runs MUST be resumable. The pattern has three parts:

1. **Alert fingerprinting** (Python):
   ```python
   def get_alert_fingerprint(alert_id: str, file_path: str, line: str) -> str:
       return f"{alert_id}@{file_path}:{line}"
   ```
   (`scripts/run_juliet_poc.py:18-20`). Use this exact format for new benchmarks.

2. **Append-mode CSV with header-on-create** (Python):
   ```python
   mode = "a" if os.path.exists(output_path) else "w"
   with open(output_path, mode, newline="") as f:
       writer = csv.DictWriter(f, fieldnames=fieldnames)
       if mode == "w":
           writer.writeheader()
       ...
       writer.writerow({...}); f.flush()
   ```
   (`scripts/benchmark_juliet_sampling.py:67-71`, `scripts/run_juliet_poc.py:103-108`).
   The `f.flush()` after every row is mandatory — it survives a Ctrl-C.

3. **Pre-scan existing output to build a skip set** (Python):
   ```python
   processed_cwes = set()
   if os.path.exists(output_path):
       with open(output_path, "r", newline="") as f:
           for row in csv.DictReader(f):
               processed_cwes.add(row["CWE"])
   ```
   (`scripts/benchmark_juliet_sampling.py:57-62`,
   `scripts/run_juliet_poc.py:61-74`). Skip any item whose fingerprint/CWE is
   already in the set.

New benchmark scripts must implement all three.

## Anti-Patterns to Avoid

- **Don't use PEP 585 lowercase generics** (`list[str]`, `dict[str, Any]`) in new
  package code — the codebase standardizes on `typing.List`/`Dict`/`Any` for 3.9
  compatibility. (One stray `list[str]` exists in `escalator.py:39`; do not
  propagate it.)
- **Don't raise from inside `Verifier.get_decision` or `Escalator.escalate`** —
  they are expected to return a `Decision` always. Map errors to `Label.ABSTAIN`.
- **Don't introduce `logging`** unless a phase explicitly requires structured logs;
  the project uses `print`/`rich` and per-provider redirected log files.
- **Don't add `setup.py`, `requirements.txt`, or a second `pyproject.toml`** — the
  single `evict_pipeline/pyproject.toml` is the source of truth for deps.
- **Don't write to `data/` from pipeline code** — `data/` is input only. Outputs go
  to `artifacts/exports/` (CSV) and `artifacts/codeql_results/` (SARIF).

---

*Convention analysis: 2026-06-20*
