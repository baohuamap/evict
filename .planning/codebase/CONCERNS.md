# Codebase Concerns

**Analysis Date:** 2026-06-20
**Last updated:** 2026-06-20 (post-fix session)

This document audits the EVICT research codebase (NeurIPS 2026 paper + Python triage
pipeline). The most severe findings were **research-integrity gaps**: the paper's headline
preliminary results (Table 2: 91.2% precision, ECE 0.08, "23 LLM errors corrected") were
**not reproducible from the committed code**, which contained stubs and hardcoded numbers.
Real measured results (Table 1) are ~42-60% precision with ECE 0.36-0.55.

Findings are ordered by severity. Each was verified by reading the actual file.

---

## Resolution Status (2026-06-20 update)

| # | Concern | Severity | Status | Resolution |
|---|---------|----------|--------|------------|
| Tech Debt 1 | Symbolic escalation stub | CRITICAL | **RESOLVED** | Z3 SMT solving implemented (SAT/UNSAT/UNKNOWN), 15 sanitizer patterns, JPF integration. 0 corrections on real PoC (Z3 returns UNKNOWN for Java string conditions). See `escalator.py` |
| Tech Debt 2 | Conformal calibration never wired | CRITICAL | **RESOLVED** | `fit_threshold` implemented (NumPy compat fix), wired into `benchmark_juliet_conformal.py` with 5-fold CV. Real q_hat=0.2, but vote-share is degenerate (85% unanimous). See `calibrator.py` |
| Tech Debt 3 | num_samples=1 contradicts k=5 | HIGH | **RESOLVED** | PoC benchmark uses k=5 (`--live` mode). CWE-Bench uses k=1 for budget. Both supported via `--num_samples` flag |
| Tech Debt 4 | Paper figures hardcoded | HIGH | **PARTIALLY RESOLVED** | Table 2 numbers updated in `preliminary_results.tex`. Figures (`calibration_plot.pdf`, `risk_coverage_curve.pdf`) are still STALE — need regeneration from real PoC data |
| Tech Debt 5 | Path-constraint extraction stub | HIGH | **RESOLVED** | Real if/while/for guard extraction implemented (regex-based). See `extractor.py:_extract_path_constraints` |
| Bugs 1 | CodeQL query path invalid | CRITICAL | **RESOLVED** | Fixed: bootstrapped `java-security-alerts.qls` suite + `--search-path`. 549 alerts generated across 45 projects. See `generate_sarifs.sh` |
| Bugs 2 | CodeQL version mismatch | HIGH | **RESOLVED** | `config.py` updated from `1.8.1` to `0.8.3` (matches distro) |
| Bugs 3 | 156 Docker images missing | HIGH | **ACCEPTED** | Scoped eval to 45 available projects. Building 156 locally is future work |
| Security 1 | API key handling | LOW | **RESOLVED** | `.env` added to `.gitignore` (was not gitignored). Keys never committed |
| Security 2 | Large untracked artifacts | MEDIUM | **PARTIALLY RESOLVED** | `artifacts/codeql_results/` gitignored (37MB regenerable). `data.tar.gz`/`data.zip` (4.7GB) still untracked |
| Results 1 | Real results far below paper | CRITICAL | **RESOLVED** | Paper Table 2 reconciled with real numbers. See `docs/summaries/FINDINGS_AND_RESULTS.md` |
| Results 2 | CWE-Bench pipeline blocked | HIGH | **RESOLVED** | Full pipeline working: SARIF gen → benchmark. 549 alerts triaged. 3.3% precision, 93.3% recall |
| Fragility 1 | CWE-Bench orchestration | MEDIUM | **RESOLVED** | Scripts fixed and tested end-to-end |
| Fragility 2 | Escalator/Calibrator interaction | MEDIUM | **RESOLVED** | 10 unit tests cover all interaction paths |
| Scale 1 | Juliet scale vs "1,000 samples" | MEDIUM | **RESOLVED** | Paper updated to "247 samples" (real count) |
| Scale 2 | Docker registry dependency | LOW | **ACCEPTED** | Documented limitation |
| Env 1 | Python 3.14 vs >=3.9 | MEDIUM | **ACCEPTED** | Works on 3.14; NumPy compat handled in `fit_threshold` |
| Env 2 | IRIS v2 vendored snapshot | LOW | **ACCEPTED** | No action needed |
| Missing 1 | Calibration driver | HIGH | **RESOLVED** | `benchmark_juliet_conformal.py` implements full driver |
| Missing 2 | Real symbolic verification | HIGH | **PARTIALLY RESOLVED** | Z3 implemented; JPF is stub (needs `JPF_HOME`). Z3 returns UNKNOWN for Java string conditions |

### New Concerns Discovered During Fix Session

| # | New Concern | Severity | Status |
|---|------------|----------|--------|
| New 1 | Vote-share confidence is degenerate (85% unanimous 5/5) | **CRITICAL** | Documented in `FINDINGS_AND_RESULTS.md`. Motivates richer confidence signals (token logprobs) |
| New 2 | Z3 integer-proxy can't model Java string conditions | HIGH | Documented. Motivates JPF or Z3 string-theory encoding |
| New 3 | Evidence-Free ≈ Evidence-Conditioned (no precision gain) | HIGH | Documented. EvidencePack may not provide useful signal to LLM |
| New 4 | Lite LLMs are TP-biased (78-94% TP predictions) | HIGH | Documented. Opposite of desired triage behavior |
| New 5 | CWE-Bench ground truth is 97% FP | MEDIUM | Documented. This is the target use case but makes precision look terrible |
| New 6 | Figures are stale (show old aspirational curves) | MEDIUM | Need regeneration from real PoC data |

---

## Original Findings (pre-fix, preserved for reference)

---

## Tech Debt

### 1. Symbolic Escalation Is a Stub — And Doubly Dead (CRITICAL, research-integrity)

- Issue: The symbolic escalation stage — central to the paper's "neuro-symbolic" claim and
  the "23 LLM errors corrected" figure in `sections/preliminary_results.tex:69` — is
  entirely unimplemented. It is broken at TWO layers, so even fixing one layer leaves it dead.
- Files:
  - `evict_pipeline/src/evict_pipeline/escalator.py:39-55` — `_solve_smt()` always returns
    `"UNKNOWN"` (line 53). The real Z3 call `solver.check()` is **commented out** at lines
    48-52 (`# solver.from_string(smt_str)`, `# result = solver.check()`,
    `# return str(result).upper()`, `return "UNKNOWN" # Placeholder`).
  - `evict_pipeline/src/evict_pipeline/escalator.py:57-63` — `_run_jpf()` and `_run_klee()`
    are stubs returning `"UNKNOWN"`.
  - `evict_pipeline/src/evict_pipeline/extractor.py:92-99` — `_extract_path_constraints()`
    is a stub that **always returns `[]`** (line 99, `# Placeholder for heuristic extraction`).
- Impact: `escalator.escalate()` (`escalator.py:13`) guards on
  `if not alert.evidence_pack.path_constraints: return decision`. Because constraints are
  always empty, the escalator **early-returns before ever calling `_solve_smt()`**. So even
  if `_solve_smt()` were implemented, it would never run. The symbolic stage can correct
  **zero** decisions. The paper's claim of "17 FP→TP + 6 TP→FP corrections" is impossible
  from this code. `implementation.md:24-28` and `sections/methodology.tex` describe JPF/KLEE
  routing and SMT solving that does not exist.
- Fix approach:
  1. Implement `_extract_path_constraints()` in `extractor.py` using real AST traversal
     (JDT for Java, Clang AST for C/C++) to populate `EvidencePack.path_constraints`.
  2. Uncomment and validate the Z3 path in `escalator.py:_solve_smt()` (parse SMT-LIB2,
     call `solver.check()`, map `sat`/`unsat`/`unknown`).
  3. Implement `_run_jpf()` / `_run_klee()` subprocess invocations (or remove the paper's
     claims about them).
  4. Re-run the PoC and report whatever escalation actually corrects — do not claim 23.

### 2. Conformal Calibration Never Wired (CRITICAL, research-integrity)

- Issue: `Calibrator.fit_threshold()` (the split-conformal q-hat computation) is defined but
  **never called anywhere in the codebase**. Both benchmark scripts hardcode the threshold
  and use no train/calibration/test split and no cross-validation.
- Files:
  - `evict_pipeline/src/evict_pipeline/calibrator.py:28-38` — `fit_threshold()` computes the
    conformal q-hat. A `grep` for `fit_threshold` across the whole repo returns exactly one
    match: the definition itself. It has zero call sites.
  - `scripts/benchmark_juliet_sampling.py:40` — `calibrator = Calibrator(threshold=0.4)`.
  - `scripts/benchmark_cwe_bench.py:72` — `calibrator = Calibrator(threshold=0.4)`.
  - `scripts/run_juliet_poc.py` — same hardcoded pattern.
- Impact: The paper (`sections/preliminary_results.tex:39`) claims "5-fold cross-validation
  with a 60/20/20 train-calibration-test split and target miscoverage rate α = 0.1" and
  reports ECE 0.08 / 91.2% precision (Table 2, `tab:preliminary`). None of this is
  reproducible: there is no calibration set, no q-hat fitting, no fold logic. The threshold
  0.4 is a magic constant, not a learned conformal quantile.
- Fix approach: Add a calibration driver that (a) splits Juliet into train/cal/test,
  (b) runs the verifier on the cal set to collect nonconformity scores
  (`1 - confidence`), (c) calls `fit_threshold(scores, alpha=0.1)`, (d) evaluates on the
  test set, (e) repeats across 5 folds and reports mean ± std. Only then cite Table 2.

### 3. num_samples=1 Contradicts the Paper's k=5 Self-Consistency Claim (HIGH)

- Issue: The Juliet benchmark scripts sample the LLM once per alert, not 5 times, making the
  vote-share confidence signal degenerate and the calibrator threshold a no-op.
- Files:
  - `scripts/benchmark_juliet_sampling.py:106` — `verifier.get_decision(alert, num_samples=1)
    # Fast PoC`.
  - `scripts/run_juliet_poc.py:114` — `verifier.get_decision(alert, num_samples=1)`.
  - `evict_pipeline/src/evict_pipeline/verifier.py:50` — default is `num_samples=5`, and
    confidence = `count / num_samples` (line 79).
  - `scripts/benchmark_cwe_bench.py:102` — uses the default `get_decision(alert)` (k=5),
    inconsistent with the Juliet script.
- Impact: With `num_samples=1`, confidence is always 1.0 (for any single non-error
  response). In `calibrator.calibrate()` (`calibrator.py:15-19`), nonconformity =
  `1 - 1.0 = 0.0`, which is never `> 0.4`, so the calibrator **never abstains on low
  confidence** — it only passes through. This means the abstain→escalate branch
  (`benchmark_juliet_sampling.py:108`) is triggered solely by LLM-native ABSTAIN outputs,
  never by the conformal threshold. The paper (`sections/preliminary_results.tex:8`,
  `implementation.md:78-84`) explicitly claims "k=5 self-consistency samples" and
  "pass@5" — contradicted by the actual runner.
- Fix approach: Set `num_samples=5` (or a configurable `--k`) in all benchmark scripts and
  re-run. Without this, the confidence/ECE numbers in the real CSVs are not even measuring
  what the paper describes.

### 4. Paper Figures Hardcoded from Aspirational Table 2 Numbers (HIGH, research-integrity)

- Issue: The two figures cited as evidence in `sections/preliminary_results.tex:75,82`
  (`figures/calibration_plot.pdf`, `figures/risk_coverage_curve.pdf`) are generated from
  **hardcoded numpy arrays**, not from any benchmark CSV.
- Files:
  - `scripts/generate_figures.py:22-25` — `accuracy_free` and `accuracy_evict` are literal
    arrays.
  - `scripts/generate_figures.py:32-34` — labels hardcode `ECE=0.15` and `ECE=0.08`.
  - `scripts/generate_figures.py:54-56` — `risk_free = 0.165`, `risk_evidence = 0.113`,
    `risk_evict = 0.088 + ...` are constants matching Table 2's `R_sel` column exactly.
- Impact: The figures visually assert calibration (ECE 0.08) and risk-coverage behavior
  that the real runs do not exhibit (real ECE is 0.36-0.55). The figure PDFs are dated
  Apr 9 (`ls figures/`), while the benchmark CSVs are dated Apr 30 - May 2 — the figures
  predate the data. This is fabricated evidence.
- Fix approach: Regenerate both figures from `artifacts/exports/v2/*_summary.md` (real
  per-CWE precision/ECE) or from real per-alert CSVs binned by confidence. Remove the
  hardcoded arrays.

### 5. Path-Constraint Extraction Stub (HIGH)

- Issue: The evidence extractor's path-constraint step is a stub, which both disables
  symbolic escalation (see #1) and means `EvidencePack.path_constraints` is always empty
  in real runs.
- Files: `evict_pipeline/src/evict_pipeline/extractor.py:92-99`. The docstring says "In a
  full implementation, this would use AST traversal (JDT/Clang)" — but `implementation.md:12`
  and the paper claim AST-based constraint extraction as a delivered feature.
- Impact: `EvidencePack.constraints_missing` is always `True` (`extractor.py:89`), so the
  LLM prompt (`verifier.py:117`) always shows "No explicit path constraints extracted",
  weakening the evidence-conditioning the paper relies on. The whole "path constraints"
  column of the methodology is absent in practice.
- Fix approach: Implement real constraint extraction (at minimum, a heuristic that scans
  `if`/guard conditions along `flow_path`), or downgrade the paper's claims to "flow traces
  only" until implemented.

---

## Known Bugs

### 1. CodeQL Query Path Invalid — Zero SARIFs Generated for CWE-Bench-Java (CRITICAL)

- Symptoms: `codeql database analyze` fails with "A fatal error occurred: java/ql/src/Security/
  is not a .ql file, .qls file, a directory, or a query pack specification." No SARIFs are
  produced.
- Files:
  - `scripts/generate_sarifs.sh:51-54` — passes `java/ql/src/Security/` as the query spec.
  - `scripts/run_full_cwe_bench.sh:44-47` — same invalid path.
- Trigger: Running either shell script end-to-end.
- Workaround / correct pattern: IRIS's own runner uses the proper path scheme at
  `data/iris-v2/src/codeql_vul.py:108`:
  `f"{CODEQL_DIR}/qlpacks/codeql/java-queries/{CODEQL_QUERY_VERSION}/{exp}Security/CWE/CWE-{self.cwe_id}/"`.
  The EVICT scripts should adopt this per-CWE directory form (and resolve `CODEQL_DIR`
  to the vendored qlpacks), not the bare `java/ql/src/Security/` shorthand.
- Verification: `ls artifacts/codeql_results/` returns **0 files** — confirms no SARIFs
  were ever generated, so `benchmark_cwe_bench.py` (which defaults `--sarif_dir` to
  `artifacts/codeql_results`) has nothing to triage.

### 2. CodeQL Query Version Mismatch (HIGH)

- Symptoms: Even with the query path fixed, IRIS would fail with path-not-found because the
  configured query version does not exist locally.
- Files:
  - `data/iris-v2/src/config.py:38` — `CODEQL_QUERY_VERSION = "1.8.1"`.
  - `data/iris-v2/codeql/qlpacks/codeql/java-queries/` — contains only `0.8.3` (verified
    via `ls`). No `1.8.1` directory exists.
- Impact: `codeql_vul.py:108` interpolates `{CODEQL_QUERY_VERSION}` into the query path, so
  it would resolve to `.../java-queries/1.8.3/Security/...` which does not exist.
- Workaround: Either set `CODEQL_QUERY_VERSION = "0.8.3"` in `config.py`, or download the
  `1.8.1` query pack into the qlpacks directory.

### 3. 156/201 CWE-Bench-Java Docker Images Missing (404) (HIGH)

- Symptoms: The SARIF-generation build summary reports `Successfully processed: 45, Failed:
  156`. Most `irissast/cwe-bench-java-containers-v2:<slug>` images return 404 / "manifest
  unknown". Every CVE-2025-* project fails (e.g. `netty_CVE-2025-25193_*`,
  `s3proxy_CVE-2025-24961_*`, `keycloak_CVE-2025-*`, etc.).
- Files:
  - `sarif_generation.log` — final summary: "=== Build Summary === Successfully processed:
    45 Failed: 156" followed by a comma-separated list of 156 failed project slugs.
  - `data/iris-v2/data/build_info.csv` — 213 projects listed (214 lines w/ header); 201
    were attempted.
  - `data/iris-v2/data/Dockerfiles/` — 189 local Dockerfile directories exist (68 of them
    for CVE-2025-* projects), so the missing images **could be built locally**.
- Trigger: `scripts/run_full_cwe_bench.sh` / IRIS `build_codeql_dbs.py --use-container`
  pulling from Docker Hub.
- Workaround: Build the 156 missing images locally from the vendored Dockerfiles instead of
  pulling from the `irissast` registry, or restrict the benchmark to the 45 projects with
  published images and disclose that scope in the paper.

---

## Security Considerations

### 1. API Key Handling (LOW — currently correct)

- Risk: Leaked LLM provider keys.
- Files: `evict_pipeline/src/evict_pipeline/verifier.py:12-46`, `scripts/benchmark_*.py`.
- Current mitigation: Keys are read from env vars (`OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `ANTHROPIC_API_KEY`) and passed into the SDK clients. A source scan for hardcoded keys
  (`sk-...`, `AIza...`, `api_key="..."` literals) found **none**. Logs are gitignored
  (`*.log` in `.gitignore`) and `git ls-files | grep '\.log$'` returns 0 tracked logs. A
  content scan of `out.log`, `out_deepseek.log`, `out_gpt-4o-mini.log`, `sarif_generation.log`
  found no leaked secrets.
- Recommendations: Keep this posture. Add a pre-commit hook that rejects files matching
  `*.env`, `*.pem`, `*secret*` to prevent future regressions. Note `verifier.py:13` stores
  `self.api_key` on the instance — fine as long as instances are not serialized to logs.

### 2. Large Untracked Artifacts Not Gitignored (MEDIUM)

- Risk: `data.tar.gz` (2.1 GB), `data.zip` (2.3 GB), `data/` (5.6 GB), `venv/` (550 MB) sit
  in the working tree untracked but are **not** in `.gitignore`. An accidental
  `git add -A` would attempt to commit gigabytes (and the venv).
- Files: `.gitignore` (10 lines — only covers `.DS_Store`, LaTeX build byproducts, `*.log`,
  `**__pycache__/**`). The repo has only 3 commits and 26 untracked top-level entries.
- Current mitigation: None — these paths are simply not yet staged.
- Recommendations: Append to `.gitignore`: `data.tar.gz`, `data.zip`, `data/`, `venv/`,
  `artifacts/runtime_screenshots/`, `*.pdf` (or keep PDFs intentionally). Verify with
  `git status` after.

---

## Performance Bottlenecks

### 1. Real Results Far Below Paper Claims (CRITICAL, reproducibility)

- Problem: Measured benchmark results are 42-60% precision and ECE 0.36-0.55, vs the paper's
  Table 2 claim of 91.2% precision / ECE 0.08.
- Files (real summaries in `artifacts/exports/v2/`):
  - `juliet_sampled_results_claude_haiku_4_5_summary.md` — Precision 59.92%, ECE 0.3582,
    Accuracy 64.18%.
  - `juliet_sampled_results_gemini_2_5_flash_lite_summary.md` — Precision 46.32%, ECE 0.4880.
  - `juliet_sampled_results_gpt_4o_mini_summary.md` — Precision 42.16%, ECE 0.5472.
  - `juliet_sampled_results_gpt_5_nano_summary.md` — Precision 44.92%, ECE 0.5381.
- Cause: Table 1 (`tab:multimodel`, `sections/preliminary_results.tex:10-29`) **is real**
  and matches the CSVs (e.g. Claude Haiku 4.5: 59.9% / 0.358). Table 2 (`tab:preliminary`,
  lines 44-64) is **aspirational** — it is not produced by any script and is not backed by
  any CSV. `scripts/generate_paper_table.py` and `generate_paper_csv.py` only regurgitate
  the real Table-1 summaries; nothing generates Table 2.
- Improvement path: Either (a) implement calibration + k=5 + escalation and re-run to
  produce a real Table 2, or (b) retract Table 2 and present only the honest multi-model
  baseline. Do not ship 91.2% / 0.08 unsupported.

### 2. CWE-Bench-Java Pipeline Blocked End-to-End (HIGH)

- Problem: The real-world evaluation cannot run because every upstream stage is broken.
- Files: `scripts/run_full_cwe_bench.sh` (orchestrator), `scripts/generate_sarifs.sh`,
  `data/iris-v2/src/config.py`.
- Cause: Compounding failures — (1) 156/201 Docker images 404, (2) CodeQL query path
  invalid, (3) CodeQL version mismatch, (4) `artifacts/codeql_results/` empty. Even the 45
  "successfully processed" databases never got analyzed into SARIFs because of bug #1.
- Improvement path: Fix the CodeQL query path + version first (cheapest), then either build
  the missing Docker images locally or narrow the CVE scope, then re-run.

---

## Fragile Areas

### 1. CWE-Bench-Java Orchestration

- Files: `scripts/run_full_cwe_bench.sh`, `scripts/generate_sarifs.sh`,
  `scripts/setup_cwe_bench.sh`, `data/iris-v2/src/codeql_vul.py`.
- Why fragile: Three independent failure modes (Docker registry, query path, version
  constant) must all be correct for any SARIF to appear. `set -e` in the shell scripts
  means the first fatal CodeQL error aborts the whole loop, yet resumability depends on
  per-project SARIF existence checks that never get created.
- Safe modification: Test each stage in isolation (build one DB → analyze one DB → triage
  one SARIF) before running the full loop. Pin `CODEQL_QUERY_VERSION` to an installed pack.
- Test coverage: None — no integration test exercises the shell pipeline.

### 2. Escalator / Calibrator / Extractor Interaction

- Files: `evict_pipeline/src/evict_pipeline/{escalator,calibrator,extractor}.py`.
- Why fragile: The abstain→escalate control flow (`pipeline.py:40-41`,
  `benchmark_juliet_sampling.py:108`) silently depends on (a) non-empty `path_constraints`
  to even enter `_solve_smt`, and (b) a meaningful confidence `< 1.0` for the calibrator to
  abstain. Both preconditions are currently false (stub constraints, `num_samples=1`), so
  the escalation branch is effectively dead code that nonetheless appears in the paper.
- Safe modification: Before touching any of these three modules, add unit tests asserting
  the data-flow contract (constraints populated → escalator invoked; confidence < threshold
  → abstain). Currently there are none.
- Test coverage: `tests/test_extractor_codeql.py` is the **only** test file and it asserts
  only source/sink/flow_path — it does **not** assert `path_constraints` is non-empty, so
  the stub goes undetected.

---

## Scaling Limits

### 1. Juliet Benchmark Scale vs. Paper's "1,000 samples" Claim

- Current capacity: Real v2 runs triaged 1,045-3,107 alerts per model
  (`artifacts/exports/v2/*_summary.md` "Total Alerts").
- Limit: The paper (`sections/preliminary_results.tex:37`) claims a focused PoC on "1,000
  Juliet samples spanning CWE-89, CWE-78, CWE-190". The real CSVs cover 87+ CWEs, not 3,
  and use `num_samples=1`. The 3-CWE / k=5 / calibrated PoC described in the paper does not
  correspond to any committed output.
- Scaling path: Add a `--cwes 89,78,190 --k 5 --calibrate` mode to
  `benchmark_juliet_sampling.py` and produce a CSV that actually matches the paper's
  described setup.

### 2. Dependency on External Docker Registry

- Current capacity: 45/201 CWE-Bench projects have published images.
- Limit: The benchmark cannot scale beyond those 45 without local image builds; all
  CVE-2025-* entries (68 of the 189 Dockerfiles) are unreachable from the registry.
- Scaling path: Batch-build the 156 missing images from `data/iris-v2/data/Dockerfiles/`
  and push to a private registry, or vendor pre-built image tarballs.

---

## Dependencies at Risk

### 1. Python 3.14 vs. `requires-python >= 3.9` (MEDIUM)

- Risk: The active `venv/` is Python 3.14.6 (`venv/bin/python --version`), but
  `evict_pipeline/pyproject.toml:10` declares `requires-python = ">=3.9"`. Several pinned
  dependencies may lack 3.14 wheels.
- Impact: `z3-solver>=4.12.0` and `google-genai>=0.1.0` are the riskiest on a brand-new
  CPython; a wheel gap would make `pip install -e .` fail or fall back to a source build of
  Z3 (slow, needs C++ toolchain). The committed `tests/__pycache__/test_extractor_codeql.cpython-314-pytest-9.0.3.pyc`
  shows tests were run under 3.14, so it currently works — but this is fragile and untested
  on the declared minimum (3.9).
- Migration plan: Pin the venv to Python 3.11 or 3.12 (mature wheel availability for z3 and
  google-genai) and update `requires-python` to `>=3.11` to match what is actually tested,
  or add a CI matrix across 3.9/3.12/3.14.

### 2. Vendored IRIS v2 Snapshot (LOW)

- Risk: `data/iris-v2/` is a clone of `github.com/iris-sast/iris` branch `v2`
  (`scripts/setup_cwe_bench.sh`). It carries its own `config.py` with a stale
  `CODEQL_QUERY_VERSION` and a qlpacks tree at `0.8.3`.
- Impact: Drift between the vendored snapshot and upstream IRIS; the version mismatch
  (Known Bug #2) stems directly from this.
- Migration plan: Submodule IRIS or record the pinned commit; sync the query version with
  the actually vendored qlpack.

---

## Missing Critical Features

### 1. Calibration Driver

- Problem: No script or module performs the train/calibration/test split, q-hat fitting, or
  k-fold CV that the paper describes. `fit_threshold()` exists in isolation.
- Blocks: Any reproduction of Table 2's ECE 0.08 / 91.2% precision claim.

### 2. Real Symbolic Verification

- Problem: Z3 solving, JPF, and KLEE invocation are all stubs. The "neuro-symbolic
  escalation" contribution is not implemented.
- Blocks: The paper's central novelty claim and the "23 errors corrected" figure.

### 3. Real Path-Constraint Extraction

- Problem: `_extract_path_constraints()` returns `[]`. The evidence pack is missing a
  whole column the paper relies on.
- Blocks: Both symbolic escalation and the evidence-conditioning ablation.

### 4. Real Figure Generation

- Problem: `generate_figures.py` hardcodes the plotted values instead of reading CSVs.
- Blocks: Reproducible figures for the camera-ready.

---

## Test Coverage Gaps

### 1. Calibrator Untested

- What's not tested: `fit_threshold()` q-hat math and the abstain threshold logic in
  `calibrate()`.
- Files: `evict_pipeline/src/evict_pipeline/calibrator.py` (no corresponding test).
- Risk: The conformal correctness theorem (`sections/theory.tex`) is empirically
  unvalidated; a bug in q-hat computation would ship undetected.
- Priority: High — this is the paper's theoretical core.

### 2. Escalator Untested

- What's not tested: `escalate()` dispatch and the `_solve_smt` / `_run_jpf` / `_run_klee`
  returns.
- Files: `evict_pipeline/src/evict_pipeline/escalator.py` (no test).
- Risk: The stub returning `"UNKNOWN"` is silently accepted as "escalation ran".
- Priority: High.

### 3. Verifier Untested

- What's not tested: Prompt construction, multi-sample aggregation, JSON extraction
  (`verifier.py:191` regex), provider routing.
- Files: `evict_pipeline/src/evict_pipeline/verifier.py` (no test).
- Risk: Malformed LLM responses silently become ABSTAIN; vote-share confidence logic is
  unchecked.
- Priority: Medium.

### 4. Path-Constraint Stub Undetected by Existing Test

- What's not tested: `tests/test_extractor_codeql.py:21-31` asserts source/sink/flow_path
  but never asserts `evidence.path_constraints` is non-empty.
- Files: `tests/test_extractor_codeql.py`, `extractor.py:92-99`.
- Risk: The stub at `extractor.py:99` returns `[]` and the test passes, hiding the fact that
  symbolic escalation can never fire.
- Priority: High — add `assert len(evidence.path_constraints) > 0` once the extractor is
  implemented.

### 5. No Integration / Reproducibility Test

- What's not tested: No test runs the full `EvictPipeline.run` (`pipeline.py:17`) on a fixed
  input and asserts a stable decision, so the end-to-end path (extract → verify → calibrate
  → escalate) has no regression guard.
- Files: `evict_pipeline/src/evict_pipeline/pipeline.py`.
- Risk: Any of the stubs could be "fixed" in a way that breaks the orchestration without
  detection.
- Priority: Medium.

---

## Documentation / Integrity Inconsistencies

### 1. EXECUTIVE_SUMMARY.md Overstates Status

- Files: `docs/summaries/EXECUTIVE_SUMMARY.md:3` ("Status: READY FOR NEURIPS 2026
  SUBMISSION ✅"), `:7` ("Expected Score: 8.17/10"), `:18` ("91.2% precision, 87.3%
  coverage, ECE 0.08"), `docs/summaries/COMPLETE_PACKAGE_SUMMARY.md` (same 91.2%/0.08
  claims).
- Impact: These summaries are inconsistent with the measured CSVs and with the stubbed
  implementation. They present aspirational Table 2 numbers as delivered results.
- Recommendation: Mark Table 2 / executive claims as "projected, pending implementation of
  calibration + symbolic escalation" until the code reproduces them.

### 2. implementation.md Describes Unimplemented Features

- Files: `implementation.md:12` ("Uses AST traversal for extracting path constraints"),
  `:21` ("Implements Split-Conformal Prediction (Algorithm 3)"), `:24-28` (JPF/KLEE
  routing), `:55` ("EVICT achieved 91.2% in prelims"), `:78-84` ("pass@5", "k=5").
- Impact: The implementation doc asserts capabilities (AST constraints, conformal fitting,
  symbolic escalation, k=5) that the code does not have.
- Recommendation: Reconcile `implementation.md` with the actual source, or implement the
  features to match.

---

*Concerns audit: 2026-06-20*
