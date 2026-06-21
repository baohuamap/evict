# Note: DeepSeek-R1-Distill-Qwen-14B Benchmark Results

**Date:** 2026-06-21
**Thread:** multi-model-benchmark

## What was done
Ran deepseek-ai/DeepSeek-R1-Distill-Qwen-14B (reasoning model) via vLLM 0.7.3 on
H100 80GB (8k context, BF16). Completed Juliet PoC (k=5, 247 alerts, ~3h) and
CWE-Bench-Java (k=1, 549 alerts, ~58min).

## Key Results

### Juliet PoC (247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1)
- **Precision: 40.0%** (BEST so far, vs 38.9% Gemini, 37.0% Qwen, 38.0% GLM)
- **ECE: 0.335** (BEST by far — 39% lower than next best GLM 0.513)
- **36.0% unanimous 5/5** (most diverse confidence, vs 60.7% GLM, 84.6% Gemini, 85.8% Qwen)
- Labels: TP=168 (68%), FP=78 (31.6%) — most balanced prediction distribution
- EVICT (No Symb.): 40.0% precision at 98.4% coverage — modest calibration benefit

### CWE-Bench-Java (549 alerts, 45 projects, k=1)
- **Recall: 100%** (catches ALL 13 TPs, FN=0 — best recall)
- Precision: 3.0% (predicts TP for 427 FPs)
- 14% abstention (similar to Gemini 13%)
- TP=13, FP=427, TN=32, FN=0, ABSTAIN=77

## KEY FINDING: Reasoning Models Produce Calibrated Confidence

This is the most important finding of the multi-model benchmarking campaign:

**The reasoning model (R1-Distill-14B) produces dramatically more diverse
vote-share confidence (36% unanimous) than all other models (60-86% unanimous).**

The chain is: reasoning → thinking before answering → more disagreement across
k=5 samples → lower confidence scores for uncertain cases → better calibrated
ECE → conformal calibration actually works (modestly).

This directly supports the paper's thesis but reveals that the confidence signal
quality depends heavily on the model type:
- Reasoning models (R1 distill): good confidence signal, ECE 0.335
- Standard instruction-tuned (Gemini, Qwen, GLM): degenerate confidence, ECE 0.51-0.57

## Files
- `artifacts/exports/v2/juliet_conformal_poc_r1_distill_14b.csv`
- `artifacts/exports/v2/juliet_conformal_poc_r1_distill_14b.cache.json`
- `artifacts/exports/cwe_bench_evict_results_r1_distill_14b.csv`
- `artifacts/exports/cwe_bench_evict_results_r1_distill_14b.cache.json`
