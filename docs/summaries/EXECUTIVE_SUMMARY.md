# EVICT: Preliminary Results - Executive Summary

## Status: IMPLEMENTED WITH HONEST FINDINGS

**Version:** 4.0 - Real Results
**Date:** June 20, 2026

---

## What Was Implemented

1. **Real conformal calibration** - Split-conformal q-hat threshold fitting (Calibrator.fit_threshold), 5-fold CV with 60/20/20 train/cal/test split, alpha=0.1
2. **Real symbolic escalation** - Z3 SMT solving of path constraints (SAT->TP, UNSAT->FP), 15 Java sanitizer patterns, JPF integration
3. **Real path-constraint extraction** - if/while/for guard extraction from code slices
4. **CWE-Bench-Java dataset** - Fixed CodeQL query path bug, generated 549 alerts across 45 projects
5. **Real benchmarks** - Both Juliet PoC (k=5) and CWE-Bench-Java (k=1) with Gemini 2.5 Flash Lite

---

## Key Results (Real Measured)

### Juliet PoC (247 alerts, CWE-89/78/190, 5-fold CV, k=5, alpha=0.1)

| Method | Precision | Recall | Coverage | ECE | R_sel |
|--------|-----------|--------|----------|-----|-------|
| Evidence-Free | 38.9% | 96.8% | 100% | 0.555 | 0.584 |
| EVICT (Full) | 38.7% | 95.5% | 100% | 0.555 | 0.584 |

### CWE-Bench-Java (549 alerts, 45 projects, k=1)

| Metric | Value |
|--------|-------|
| Precision | 3.3% |
| Recall | 93.3% |
| F1 | 0.06 |

---

## Critical Finding: Vote-Share Confidence is Degenerate

**85% of decisions receive unanimous 5/5 vote-share (confidence = 1.0)**, even for false positives. This makes the nonconformity score degenerate (mostly 0.0), so:
- q_hat = 0.200 (conformal threshold)
- Only 2.4% of alerts (6/247) are abstained
- Conformal calibration provides negligible selective prediction benefit

**The calibration deficit of raw lite models (ECE > 0.35) is NOT recoverable by conformal prediction alone** when the confidence signal is degenerate.

---

## What Was Previously Claimed vs Reality

| Metric | Previous Claim | Real Measured | Gap |
|--------|---------------|---------------|-----|
| Precision | 91.2% | 38.9% | -52.3 pp |
| ECE | 0.08 | 0.555 | +0.475 |
| Coverage | 89.6% | 97.6% | +8.0 pp |
| Symbolic corrections | 23 | 0 | -23 |

The previous Table 2 numbers were aspirational, not measured. The real implementation reveals that vote-share confidence from lite LLMs is not a sufficiently discriminative signal for conformal selective prediction.

---

## Path Forward

To achieve production-grade precision:
1. **Richer confidence signals** - token-level log-probabilities, semantic consistency, chain-of-thought self-evaluation
2. **Stronger LLMs** - Claude Haiku 4.5 showed 59.9% precision (vs 38.9% for Gemini Flash Lite)
3. **Full symbolic backends** - JPF for Java path feasibility (Z3 integer-proxy returns UNKNOWN for string conditions)
4. **Better ground-truth matching** - CWE-Bench-Java matching found only 17 TP out of 549 alerts

---

## Table 1 (Multi-Model Baseline) IS Real

The multi-model zero-shot baseline study (Table 1) uses real data from existing CSVs:
- Claude Haiku 4.5: 59.9% precision, ECE 0.358
- GPT-4o Mini: 42.2% precision, ECE 0.547
- Gemini 2.5 Flash Lite: 46.8% precision, ECE 0.483

These numbers are verified against the CSV files in artifacts/exports/v2/.
