# Note: GLM-4-9B-Chat Benchmark Results

**Date:** 2026-06-21
**Thread:** multi-model-benchmark

## What was done
Ran zai-org/glm-4-9b-chat via vLLM 0.7.3 on H100 80GB (8k context, BF16).
Completed Juliet PoC (k=5, 247 alerts, 19 min) and CWE-Bench-Java (k=1, 549 alerts, 5 min).

## Key Results

### Juliet PoC (247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1)
- Precision: 38.0% (vs Gemini 38.9%, Qwen 37.0%)
- Recall: 95.9% (vs Gemini 95.5%, Qwen 81.5%)
- ECE: 0.513 (vs Gemini 0.555, Qwen 0.565) — BEST ECE so far
- 60.7% unanimous 5/5 vote-share — most diverse confidence (vs 84.6% Gemini, 85.8% Qwen)
- EVICT (No Symb.) 39.1% precision at 96.3% coverage — small calibration benefit

### CWE-Bench-Java (549 alerts, 45 projects, k=1)
- Precision: 1.9%, Recall: 62.5%, F1: 0.040
- 33.7% abstention (between Gemini 13% and Qwen 62%)
- Highest TN (97) of three models — best at correctly rejecting FPs
- TP=5, FP=259, TN=97, FN=3, ABSTAIN=185

## Key Finding
GLM-4-9B-Chat has the MOST DIVERSE vote-share confidence (60.7% unanimous vs 85%+)
which produces the BEST ECE (0.513). This suggests model size and training approach
matter for confidence calibration — a 9B model produces more calibrated confidence
than 32B code-specialized or lite commercial models. However, the calibration
benefit is still modest because overconfident wrong answers dominate.

## Files
- `artifacts/exports/v2/juliet_conformal_poc_glm_4_9b_chat.csv`
- `artifacts/exports/v2/juliet_conformal_poc_glm_4_9b_chat.cache.json`
- `artifacts/exports/cwe_bench_evict_results_glm_4_9b_chat.csv`
- `artifacts/exports/cwe_bench_evict_results_glm_4_9b_chat.cache.json`
