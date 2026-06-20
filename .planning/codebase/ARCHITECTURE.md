<!-- refreshed: 2026-06-20 -->
# Architecture

**Analysis Date:** 2026-06-20

## System Overview

EVICT is a 4-stage triage pipeline for static-analysis alerts. A single SARIF alert is
walked through `Extractor → Verifier → Calibrator → Escalator`, producing a `Decision`
(`TP` / `FP` / `ABSTAIN`) with a calibrated confidence and stage tag. The pipeline is
orchestrated by `EvictPipeline`; benchmark/CLI entry points wire concrete stage
instances and stream results to CSV.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                       Entry Points (CLI / Scripts)                       │
│  `evict_pipeline/evaluate.py`  `scripts/run_juliet_poc.py`               │
│  `scripts/benchmark_juliet_sampling.py`  `scripts/benchmark_cwe_bench.py`│
│  `scripts/run_full_cwe_bench.sh` (3-step shell orchestrator)             │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │ construct stages + loop alerts
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  Orchestrator: `EvictPipeline.run()`                     │
│                  `evict_pipeline/src/evict_pipeline/pipeline.py`         │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
   ┌───────────────┬───────────────┼───────────────┬────────────────┐
   ▼               ▼               ▼               ▼                ▼
┌────────┐  ┌──────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐
│Extract │  │ Verify   │  │ Calibrate  │  │ Escalate   │  │  Models      │
│SARIF→  │  │ LLM pass@│  │ conformal  │  │ Z3/JPF/KLEE│  │ Alert/Decision│
│Evidence│  │ 5 vote   │  │ threshold  │  │ (stubs)    │  │ EvidencePack │
│`extrac │  │ `verifier│  │ `calibrator│  │ `escalator │  │ `models.py`  │
│tor.py` │  │ .py`     │  │ .py`       │  │ .py`       │  │              │
└────────┘  └──────────┘  └────────────┘  └────────────┘  └──────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  I/O & External: SARIF files, LLM providers (OpenAI/Gemini/Anthropic),   │
│  Z3 solver, source files under `data/`, CSV results in `artifacts/exports`│
└──────────────────────────────────────────────────────────────────────────┘
```

A parallel, decoupled subsystem — `data/iris-v2/` (the IRIS baseline, vendored) and
`data/cwe-bench-java/` (benchmark dataset) — feed SARIF into EVICT but are not
imported by the pipeline package.

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `EvictPipeline` | Orchestrates the 4 stages over a single `Alert` or a whole SARIF file | `evict_pipeline/src/evict_pipeline/pipeline.py` |
| `Extractor` | Parses SARIF into `Alert` objects; populates `EvidencePack` (flow path, code slice, path constraints) | `evict_pipeline/src/evict_pipeline/extractor.py` |
| `Verifier` | Builds schema-guided prompt, samples the LLM `pass@5`, aggregates by majority vote-share into a `Decision` | `evict_pipeline/src/evict_pipeline/verifier.py` |
| `Calibrator` | Applies split-conformal threshold on `1 - confidence`; abstains when score exceeds threshold | `evict_pipeline/src/evict_pipeline/calibrator.py` |
| `Escalator` | Symbolic fallback on abstention: Z3 SMT (stub), JPF/KLEE (stubs) | `evict_pipeline/src/evict_pipeline/escalator.py` |
| `models` | Pydantic data contracts: `Label`, `EvidencePack`, `Alert`, `Decision` | `evict_pipeline/src/evict_pipeline/models.py` |
| `evaluate.py` | CLI runner with `rich` table output, computes coverage | `evict_pipeline/evaluate.py` |
| `benchmark_juliet_sampling.py` | Juliet benchmark: per-CWE SARIF, samples 50–100 alerts, resumable CSV | `scripts/benchmark_juliet_sampling.py` |
| `benchmark_cwe_bench.py` | CWE-Bench-Java benchmark: matches alerts to `fix_info.csv` ground truth, computes precision/recall/F1 | `scripts/benchmark_cwe_bench.py` |
| `run_juliet_poc.py` | Quick PoC runner over a single SARIF; resumable via alert fingerprints | `scripts/run_juliet_poc.py` |
| `run_full_cwe_bench.sh` | Shell orchestrator: build CodeQL DBs → analyze → run EVICT benchmark | `scripts/run_full_cwe_bench.sh` |
| `analyze_juliet_performance.py` | Post-hoc Juliet metrics (precision/recall/coverage/ECE) + per-CWE breakdown; derives ground truth from `bad`/`good` method names | `scripts/analyze_juliet_performance.py` |
| `IRIS` baseline | State-of-the-art comparison baseline (vendored, `SAPipeline` class) | `data/iris-v2/src/iris.py` |

## Pattern Overview

**Overall:** Pipes-and-filters pipeline with constructor-injected stages (a lightweight
strategy/composition pattern). Each stage is a plain class with a single primary
method; `EvictPipeline` is a thin orchestrator with no domain logic of its own.

**Key Characteristics:**
- Stages are stateless except for config held in `__init__` (e.g. `Verifier.api_key`, `Calibrator.threshold`). No stage caches results.
- Data flows through Pydantic models (`Alert` → `Decision`), mutated in place (`populate_evidence` writes `alert.evidence_pack`; `calibrate` mutates the passed `Decision`).
- Benchmark scripts do **not** call `EvictPipeline.run()`; they inline the same 4-step loop to control `num_samples`, per-alert `try/except`, and CSV streaming. `pipeline.py:run_on_sarif` exists as the library entry but is unused by benchmarks.
- Provider selection is environment-driven (detect `OPENAI_API_KEY` → `GEMINI_API_KEY` → `ANTHROPIC_API_KEY`) and replicated in every entry-point script.

## Layers

**Entry / Runner Layer:**
- Purpose: parse CLI args/env, wire stages, iterate alerts, write CSV.
- Location: `scripts/*.py`, `evict_pipeline/evaluate.py`, `scripts/*.sh`.
- Contains: argparse setup, env-var detection, resumability (fingerprint/CSV append), CSV schema.
- Depends on: `evict_pipeline` package (added to `sys.path` manually).
- Used by: developers running benchmarks.

**Orchestration Layer:**
- Purpose: define the 4-step sequence and the abstain→escalate branch.
- Location: `evict_pipeline/src/evict_pipeline/pipeline.py` (`EvictPipeline.run`, `run_on_sarif`).
- Contains: 59 lines total; the canonical 6-step EVICT workflow comment.
- Depends on: `Extractor`, `Verifier`, `Calibrator`, `Escalator`.
- Used by: `evaluate.py` (via direct step-by-step loop), library consumers.

**Stage Layer (domain logic):**
- Purpose: one stage = one class = one primary method.
- Location: `evict_pipeline/src/evict_pipeline/{extractor,verifier,calibrator,escalator}.py`.
- Contains: SARIF parsing, prompt construction, LLM sampling, conformal threshold, symbolic stubs.
- Depends on: `models.py`, `openai`/`google.genai`/`anthropic` SDKs, `z3`, `numpy`.
- Used by: orchestrator and benchmark scripts (directly).

**Model Layer (data contracts):**
- Purpose: typed payloads that cross stage boundaries.
- Location: `evict_pipeline/src/evict_pipeline/models.py`.
- Contains: `Label` enum (`TP`/`FP`/`ABSTAIN`), `EvidencePack`, `Alert`, `Decision`.
- Depends on: `pydantic`.
- Used by: every stage and every entry point.

**I/O / External Layer:**
- Purpose: read SARIF + source files; call LLM providers; write CSV; shell out to CodeQL/SpotBugs/PMD.
- Location: filesystem under `data/`, CSV under `artifacts/exports/`, LLM SDKs, `bin/spotbugs-*`, `bin/pmd-bin-*`, `data/iris-v2/codeql/`.
- Contains: SARIF JSON, Juliet/CWE-Bench-Java sources, vendored analyzers.
- Depends on: nothing in the package.
- Used by: Extractor (source read), Verifier (LLM calls), shell scripts (analyzer invocation).

## Data Flow

### Primary Request Path (single alert triage)

1. **SARIF load** — entry script reads JSON from a `.sarif` file (`scripts/benchmark_juliet_sampling.py:81-86`, `scripts/benchmark_cwe_bench.py:89-90`, `evict_pipeline/evaluate.py:47-49`).
2. **Extract alerts** — `Extractor.extract_from_sarif(sarif_data)` walks `runs[].results[]`, pulls `ruleId`/message/location, builds `Alert` with `raw_sarif` retained (`extractor.py:10-40`).
3. **Populate evidence** — `Extractor.populate_evidence(alert, project_root)` reads `codeFlows[0].threadFlows[0].locations` for `flow_path`, reads the source file (with `data/juliet_java` fallback rglob), builds `EvidencePack` (`extractor.py:49-90`). `path_constraints` is always `[]` (stub at `extractor.py:92-99`).
4. **LLM verify** — `Verifier.get_decision(alert, num_samples=5)` builds a schema-guided prompt with CWE-specific hints (23/78/89), samples the LLM N times, majority vote → `Label`, confidence = vote-share (`verifier.py:50-92`). Per-sample errors degrade to `ABSTAIN` (`verifier.py:200-201`).
5. **Calibrate** — `Calibrator.calibrate(decision)` computes `nonconformity = 1 - confidence`; if it exceeds `threshold` the label becomes `ABSTAIN` and stage becomes `"Calibrated"` (`calibrator.py:11-26`).
6. **Escalate (conditional)** — if label is `ABSTAIN`, `Escalator.escalate(alert, decision)` attempts Z3 on `path_constraints`. Because `path_constraints` is always empty and `_solve_smt` is a stub returning `"UNKNOWN"`, the escalator in practice only appends a rationale line and sets `stage="Symbolic"` (`escalator.py:11-37`, `escalator.py:39-55`).
7. **Output** — entry script writes a CSV row (schema varies per script) and flushes; aggregate metrics computed at end (`benchmark_cwe_bench.py:122-145`) or by `analyze_juliet_performance.py`.

### Library Path (`EvictPipeline.run`)

`pipeline.py:17-46` encodes steps 3–7 verbatim. `run_on_sarif` (lines 48–59) additionally does steps 1–2. This path is used by `evaluate.py` conceptually but `evaluate.py` actually inlines the loop to pass `num_samples` and to wrap each alert in `try/except`.

### Juliet Benchmark Flow

1. `scripts/generate_full_juliet_sarif.sh` builds each Juliet CWE module with Gradle and runs SpotBugs → `data/juliet_sarifs/cwe<NN>.sarif` (one per CWE).
2. `scripts/benchmark_juliet_sampling.py` globs `data/juliet_sarifs/*.sarif`, randomly samples 50–100 alerts per CWE (`benchmark_juliet_sampling.py:93-100`), runs the primary path with `num_samples=1` (fast PoC), appends to `artifacts/exports/v2/juliet_sampled_results_<model>.csv`.
3. `scripts/analyze_juliet_performance.py` post-processes the CSV: derives ground truth by parsing Juliet source for `bad`/`good` method names and matching the alert line (`analyze_juliet_performance.py:7-73`), computes precision/recall/coverage/ECE and a per-CWE breakdown, writes `*_summary.md`.

### CWE-Bench-Java Flow

1. `scripts/run_full_cwe_bench.sh` (or `scripts/generate_sarifs.sh`) calls `data/iris-v2/scripts/build_codeql_dbs.py --use-container` to build CodeQL DBs in Docker, then `codeql database analyze` per DB → `artifacts/codeql_results/<slug>.sarif`.
2. `scripts/benchmark_cwe_bench.py` loads ground truth from `data/cwe-bench-java/data/fix_info.csv` keyed by project slug (`benchmark_cwe_bench.py:18-36`), matches an alert as TP if same file suffix and line within `[method_start, method_end]` (`benchmark_cwe_bench.py:38-48`), runs the primary path, and computes precision/recall/F1 inline (`benchmark_cwe_bench.py:130-145`).

### IRIS Baseline Flow (vendored, not invoked by EVICT)

`data/iris-v2/src/iris.py` `SAPipeline` class: collects external APIs + function params via CodeQL, asks an LLM to classify them as sources/sinks/propagators, builds a CWE-specific CodeQL query, runs it, then asks the LLM to filter FPs. Used only as a comparison baseline; EVICT consumes IRIS's CWE-specific hints (hardcoded in `verifier.py:99-103`) but does not import IRIS code.

**State Management:**
- No persistent state in the pipeline. The only mutable state is per-alert: `populate_evidence` writes `alert.evidence_pack`; `calibrate`/`escalate` mutate the `Decision` in place.
- Cross-run state lives in CSV files (`artifacts/exports/`); resumability is achieved by reading already-processed CWEs (sampling benchmark) or alert fingerprints (`run_juliet_poc.py:18-20, 60-87`).
- `Calibrator.threshold` is instance state, defaulted to `0.5` in `evaluate.py` and `0.4` in all benchmark scripts — never fitted at runtime.

## Key Abstractions

**`Alert`:**
- Purpose: a single static-analyzer finding, the unit of work.
- Examples: `evict_pipeline/src/evict_pipeline/models.py:23-32`; constructed in `extractor.py:30-38`.
- Pattern: Pydantic `BaseModel`; carries `raw_sarif` dict so downstream stages can re-read SARIF fields without re-parsing.

**`EvidencePack`:**
- Purpose: structured evidence extracted from analyzer output + source code; the LLM prompt's primary input.
- Examples: `models.py:10-21`; populated in `extractor.py:82-90`.
- Pattern: Pydantic model with completeness flags (`flow_partial`, `constraints_missing`) that the prompt surfaces to the LLM.

**`Decision`:**
- Purpose: the pipeline's output; carries label, confidence, rationale, `stage` (`"LLM"`/`"Calibrated"`/`"Symbolic"`), `is_escalated`, and freeform `metadata` (vote distribution, provider, model).
- Examples: `models.py:34-42`; produced in `verifier.py:85-92`, mutated in `calibrator.py` and `escalator.py`.
- Pattern: mutable-by-reference accumulator — each stage tags `stage` and appends to `rationale`.

**`Label`:**
- Purpose: the triage outcome vocabulary.
- Examples: `models.py:5-8`.
- Pattern: `str, Enum` so `Label.TP == "TP"` and serializes directly into CSVs.

**Stage classes:**
- Purpose: pluggable 4-stage implementations.
- Examples: `Extractor`, `Verifier`, `Calibrator`, `Escalator`.
- Pattern: constructor takes config (API key, threshold, timeout); one primary method (`extract_from_sarif`/`populate_evidence`, `get_decision`, `calibrate`, `escalate`). No interface/ABC — duck-typed by `EvictPipeline`'s constructor.

## Entry Points

**`EvictPipeline` (library API):**
- Location: `evict_pipeline/src/evict_pipeline/pipeline.py:8-59`; re-exported from `evict_pipeline/src/evict_pipeline/__init__.py`.
- Triggers: imported by `evict_pipeline/evaluate.py` and all benchmark scripts.
- Responsibilities: hold the 4 stages; `run(alert, project_root)` and `run_on_sarif(sarif_file, project_root)`.

**`evict_pipeline/evaluate.py` (CLI):**
- Location: `evict_pipeline/evaluate.py:10-101`.
- Triggers: `python evict_pipeline/evaluate.py <sarif> --provider ... --model ... --num-samples ...`.
- Responsibilities: argparse, env-var API key lookup, run the 4-step loop per alert, render a `rich` table + coverage summary.

**`scripts/run_juliet_poc.py`:**
- Location: `scripts/run_juliet_poc.py:22-138`.
- Triggers: `python scripts/run_juliet_poc.py --sarif data/juliet_alerts_pmd.sarif --output ...`.
- Responsibilities: quick Juliet PoC; supports local LLM via `LOCAL_LLM_URL`/`LOCAL_MODEL_NAME`; resumable via `alert_id@file:line` fingerprints; rate-limits remote LLMs with `time.sleep(4)`.

**`scripts/benchmark_juliet_sampling.py`:**
- Location: `scripts/benchmark_juliet_sampling.py:19-137`.
- Triggers: `python scripts/benchmark_juliet_sampling.py --sarif_dir data/juliet_sarifs --output_dir artifacts/exports/v2 --model ...`.
- Responsibilities: per-CWE SARIF glob, random 50–100 sample, resumable per-CWE skip, CSV append, `num_samples=1` for speed.

**`scripts/benchmark_cwe_bench.py`:**
- Location: `scripts/benchmark_cwe_bench.py:50-159`.
- Triggers: `python scripts/benchmark_cwe_bench.py --sarif_dir artifacts/codeql_results --gt_path data/cwe-bench-java/data/fix_info.csv --output ...`.
- Responsibilities: load ground truth, match alerts to TP/FP, run EVICT, compute precision/recall/F1 inline.

**`scripts/run_full_cwe_bench.sh`:**
- Location: `scripts/run_full_cwe_bench.sh`.
- Triggers: `bash scripts/run_full_cwe_bench.sh` (requires Docker + CodeQL CLI).
- Responsibilities: 3-step orchestrator — `build_codeql_dbs.py` → `codeql database analyze` loop → `benchmark_cwe_bench.py`. Resumable via "skip if SARIF exists".

## Architectural Constraints

- **Threading:** Single-threaded. LLM calls are sequential `for _ in range(num_samples)` (`verifier.py:162`); IRIS uses `thread_map` but EVICT does not. `time.sleep(4)` rate-limits remote calls in `run_juliet_poc.py:134`.
- **Global state:** None at module scope in the pipeline package. Stage instances are per-run. `Verifier` holds an open SDK client (`self.client`). The `z3` import at the top of `escalator.py:2` means importing `evict_pipeline` requires `z3-solver` installed even when escalation is never exercised.
- **Circular imports:** None. `pipeline.py` imports the four stages; stages import only `models`. `__init__.py` re-exports everything.
- **sys.path injection:** Every script under `scripts/` and `tests/` does `sys.path.append(.../evict_pipeline/src)` rather than relying on `pip install -e .` (`benchmark_juliet_sampling.py:10-11`, `benchmark_cwe_bench.py:9-10`, `run_juliet_poc.py:9-10`, `tests/test_extractor_codeql.py:5-6`). The pipeline is installed editable per the README, but scripts are defensive.
- **Stub correctness:** `Escalator._solve_smt` returns `"UNKNOWN"` unconditionally with the real Z3 calls commented out (`escalator.py:39-55`); `_run_jpf`/`_run_klee` return `"UNKNOWN"` (`escalator.py:57-63`). `Extractor._extract_path_constraints` returns `[]` unconditionally (`extractor.py:92-99`), so `EvidencePack.path_constraints` is always empty and `constraints_missing` is always `True`.
- **Hardcoded calibration:** `Calibrator.fit_threshold` exists and computes q-hat correctly (`calibrator.py:28-38`) but is never invoked by any entry point. All callers hardcode `Calibrator(threshold=0.4)` (benchmarks) or `Calibrator(threshold=0.5)` (`evaluate.py:39`). Conformal calibration is therefore inactive in practice.
- **Provider auto-detection precedence:** `OPENAI_API_KEY` wins over `GEMINI_API_KEY` wins over `ANTHROPIC_API_KEY`; default fallback is `"gemini"` (`benchmark_juliet_sampling.py:25-33`, `benchmark_cwe_bench.py:56-64`, `run_juliet_poc.py:31-46`).
- **Java toolchain:** Juliet SARIF generation requires `JAVA_HOME` pointed at OpenJDK 17 and Gradle/SpotBugs/PMD under `bin/` (`generate_full_juliet_sarif.sh:5-9`). CWE-Bench-Java requires Docker for `build_codeql_dbs.py`.

## Anti-Patterns

### Stub stages presented as functional

**What happens:** `Escalator._solve_smt` is a stub that always returns `"UNKNOWN"` (`escalator.py:39-55`); `_run_jpf`/`_run_klee` are stubs (`escalator.py:57-63`); `Extractor._extract_path_constraints` always returns `[]` (`extractor.py:92-99`). The `escalator.py:2` `from z3 import ...` import still forces a hard dependency on `z3-solver`.
**Why it's wrong:** The README, `evict_pipeline/README.md`, and `implementation.md` describe symbolic escalation via Z3/JPF/KLEE as a live feature. In practice escalation only appends a rationale line and relabels `stage="Symbolic"`; it never changes a label. Callers reading the docs will mis-architect integrations.
**Do this instead:** Either (a) gate the `z3` import behind a lazy import inside `_solve_smt` and document the stubs as "not yet implemented" in `escalator.py` docstrings, or (b) implement `_solve_smt` to actually call `solver.from_string(smt_str); solver.check()` and surface a clear error when `path_constraints` is empty. Until then, `Escalator.escalate` should early-return the unchanged decision when `path_constraints` is empty (it already does at `escalator.py:13-14`, but the symbolic "UNKNOWN" branch at lines 29-31 still mutates `stage`).

### Conformal calibration bypassed by hardcoded threshold

**What happens:** `Calibrator.fit_threshold` computes q-hat from calibration scores (`calibrator.py:28-38`) but no entry point calls it. Benchmarks hardcode `Calibrator(threshold=0.4)` (`benchmark_juliet_sampling.py:40`, `benchmark_cwe_bench.py:72`, `run_juliet_poc.py:53`); `evaluate.py` uses `0.5` (`evaluate.py:39`). The "conformal" behavior is a fixed confidence cutoff.
**Why it's wrong:** The paper's headline calibration contribution (split-conformal q-hat) is not exercised by the evaluation harness, so reported ECE/coverage numbers reflect a hand-tuned threshold, not a statistically calibrated one.
**Do this instead:** Add a `--calibration-scores` flag (or a calibration SARIF) to the benchmark scripts and call `calibrator.fit_threshold(scores, alpha=0.1)` once before the alert loop. Wire `alpha` through the CLI. Keep the hardcoded value only as a default when no calibration set is supplied.

### Duplicated orchestration across entry points

**What happens:** `evaluate.py`, `run_juliet_poc.py`, `benchmark_juliet_sampling.py`, and `benchmark_cwe_bench.py` each re-implement the 4-step loop (populate → get_decision → calibrate → escalate-on-abstain) instead of calling `EvictPipeline.run`. The same provider-auto-detection block is copy-pasted into each script.
**Why it's wrong:** Logic drift: `evaluate.py` passes `num_samples=5` default while the benchmarks pass `num_samples=1` for speed, but nothing in `pipeline.py` exposes `num_samples`. Any change to the abstain/escalate branch must be replicated in 4 places.
**Do this instead:** Extend `EvictPipeline.run` to accept `num_samples` and a per-alert `on_decision` callback (for CSV streaming + error isolation), then have the scripts call `run`/`run_on_sarif`. Extract provider auto-detection into `evict_pipeline/verifier.py` as a `Verifier.from_env()` classmethod.

### `evaluate.py` README snippet is wrong

**What happens:** `evict_pipeline/README.md:18-20` shows `EvictPipeline()` with no args and `pipeline.run("alert.sarif")`, but `EvictPipeline.__init__` requires four stage instances (`pipeline.py:11`) and `run` takes an `Alert` + `project_root` (`pipeline.py:17`).
**Why it's wrong:** Users following the README will hit `TypeError`.
**Do this instead:** Update the snippet to construct the four stages (or add a `EvictPipeline.from_env()` factory) and show `run_on_sarif(sarif_file, project_root)`.

## Error Handling

**Strategy:** Defensive per-alert isolation. Each alert is wrapped in `try/except` at the entry-point level; failures are logged to stdout and skipped, never re-raised. The pipeline continues with the next alert.

**Patterns:**
- **LLM errors degrade to ABSTAIN:** `Verifier._sample_llm` catches all exceptions per sample and appends `(Label.ABSTAIN, "Error calling ...")` (`verifier.py:200-201`); missing JSON also yields `ABSTAIN` (`verifier.py:198-199`).
- **Missing evidence → ABSTAIN:** `Verifier.get_decision` returns an `ABSTAIN` `Decision` when `alert.evidence_pack` is `None` (`verifier.py:52-59`) or when no valid responses were collected (`verifier.py:69-76`).
- **Source-file read failures:** `Extractor._get_code_context` returns a `// Error reading source file: ...` comment string rather than raising (`extractor.py:137-138`); missing files return `// Could not read source file: ...` (`extractor.py:126`).
- **Z3 errors:** `Escalator._solve_smt` catches `Exception` and returns `"UNKNOWN"` (`escalator.py:54-55`).
- **SARIF parse errors:** Benchmark scripts wrap `json.load` in `try/except` and `continue` to the next file (`benchmark_juliet_sampling.py:82-86`).
- **No retry/backoff:** a failed LLM call is a lost sample; with `num_samples=1` (benchmarks) a single failure forces ABSTAIN + escalation.
- **No structured logging:** all diagnostics are `print(...)`. Log files at the repo root (`out.log`, `out_gpt-4o-mini.log`, `error.log`, `sarif_generation.log`) are ad-hoc captures, not framework output.

## Cross-Cutting Concerns

**Logging:** `print()` to stdout everywhere. No `logging` module usage in the pipeline package. `data/iris-v2/src/logger.py` provides IRIS's `Logger` class but EVICT does not adopt it. Stray `.log` files at the repo root (`out.log`, `error_deepseek.log`, `poc_progress.log`, `sarif_generation.log`, etc.) are unstructured captures from past runs.

**Validation:** Pydantic validates `Alert`/`Decision`/`EvidencePack` field types on construction. No JSON-schema validation of LLM output beyond a regex `\{.*\}` extraction (`verifier.py:191`) and `Label.__members__` membership check (`verifier.py:195`). CWE IDs are extracted heuristically from `ruleId` (`extractor.py:42-47`) and fall back to `"Unknown"`.

**Authentication:** None in the pipeline itself. LLM provider auth is via env vars (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`) read at the entry-point level and passed into `Verifier`. CodeQL DB building in Docker uses `data/iris-v2/dep_configs.json` for JDK/Maven/Gradle paths (no secrets). No API tokens are persisted in the repo.

**Configuration:** No config files for the pipeline; all knobs are CLI flags or env vars. IRIS uses `data/iris-v2/src/config.py` (hardcoded paths) and `dep_configs.json`. EVICT's `Calibrator.threshold`, `Verifier.temperature`, `Escalator.timeout_ms` are constructor args with defaults.

**Resumability:** Two incompatible schemes — `run_juliet_poc.py` fingerprints alerts as `alert_id@file:line` (`run_juliet_poc.py:18-20`); `benchmark_juliet_sampling.py` skips whole CWEs by reading the output CSV's `CWE` column (`benchmark_juliet_sampling.py:57-63`); `run_full_cwe_bench.sh` skips projects whose SARIF already exists (`run_full_cwe_bench.sh:38-41`).

---

*Architecture analysis: 2026-06-20*
