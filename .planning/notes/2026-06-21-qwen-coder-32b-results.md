# Note: Qwen-Coder-32B Benchmark Results

**Date:** 2026-06-21
**Thread:** multi-model-benchmark

## What was done
Ran Qwen2.5-Coder-32B-Instruct via vLLM 0.7.3 on H100 80GB (8k context, BF16).
Completed both Juliet PoC (k=5, 247 alerts) and CWE-Bench-Java (k=1, 549 alerts).

## Key Results

### Juliet PoC (247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1)
- Precision: 37.0% (vs Gemini 38.9%)
- Recall: 81.5% (vs Gemini 95.5%)
- ECE: 0.565 (vs Gemini 0.555)
- 85.8% unanimous 5/5 vote-share (degenerate, same as Gemini)

### CWE-Bench-Java (549 alerts, 45 projects, k=1)
- Precision: 1.5% (vs Gemini 3.3%)
- Recall: 40.0% (vs Gemini 93.3%)
- 62% abstention (vs Gemini 13%) — dramatically more conservative
- Higher TN (76 vs 47) — better at rejecting FPs when it does classify

## Key Finding
Qwen-Coder-32B is much more conservative than Gemini on real-world alerts (62%
abstain vs 13%), but this comes from LLM refusals (empty/conflicted JSON), not
from conformal calibration. Both models have degenerate vote-share (85%+ unanimous).
The code-specialized model doesn't produce better security triage than the
general-purpose lite model.

## Files
- `artifacts/exports/v2/juliet_conformal_poc_qwen_coder_32b.csv`
- `artifacts/exports/v2/juliet_conformal_poc_qwen_coder_32b.cache.json`
- `artifacts/exports/cwe_bench_evict_results_qwen_coder_32b.csv`
- `artifacts/exports/cwe_bench_evict_results_qwen_coder_32b.cache.json`
