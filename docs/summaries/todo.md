# EVICT TODO

**Last updated:** 2026-06-20

## Completed (2026-06-20 session)
- [x] Map codebase (.planning/codebase/ — 7 docs)
- [x] Fix CodeQL query path bug (generate_sarifs.sh, run_full_cwe_bench.sh)
- [x] Fix CodeQL version mismatch (config.py 1.8.1 → 0.8.3)
- [x] Generate 549 CodeQL alerts across 45 CWE-Bench-Java projects
- [x] Implement real conformal calibration (fit_threshold, 5-fold CV, alpha=0.1)
- [x] Implement real symbolic escalation (Z3 SMT, 15 sanitizer patterns, JPF stub)
- [x] Implement real path-constraint extraction (if/while/for guards)
- [x] Write conformal PoC benchmark script (benchmark_juliet_conformal.py)
- [x] Run real Juliet PoC (247 alerts, k=5, Gemini 2.5 Flash Lite)
- [x] Run real CWE-Bench-Java benchmark (549 alerts, k=1)
- [x] Add 8 new tests (10 total, all pass)
- [x] Reconcile paper Table 2 with real numbers
- [x] Reconcile EXECUTIVE_SUMMARY.md with real numbers
- [x] Gitignore .env (security)
- [x] Document findings in FINDINGS_AND_RESULTS.md

## Next Steps (paper updates)
- [ ] Regenerate figures (calibration_plot.pdf, risk_coverage_curve.pdf) from real PoC data
- [ ] Update scripts/generate_figures.py to read from juliet_conformal_poc_gemini.csv
- [ ] Rebuild main.pdf with updated Table 2 and figures
- [ ] Update methodology section to acknowledge vote-share limitation
- [ ] Update discussion section with real CWE-Bench-Java results
- [ ] Update evaluation plan to reflect what was actually done (45/201 projects)

## Next Steps (experiments, budget-dependent)
- [ ] Run PoC with Claude Haiku 4.5 (best precision in Table 1, 59.9%)
- [ ] Run CWE-Bench-Java with k=5 (2,745 LLM calls, ~$0.50)
- [ ] Implement token log-probability confidence (if API supports it)
- [ ] Set up JPF_HOME and test real Java path feasibility
- [ ] Investigate Evidence-Free ≈ Evidence-Conditioned (no precision gain)
- [ ] Improve ground-truth matching for CWE-Bench-Java (only 17/549 TP matched)

## Next Steps (code quality)
- [ ] Fix black/isort on pre-existing files (__init__.py, pipeline.py, verifier.py)
- [ ] Add CI config (.github/workflows) for automated testing
- [ ] Add integration test for full pipeline end-to-end
