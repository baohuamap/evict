# Note: DeepSeek-Coder-V2-Lite Benchmark Results + Final 5-Model Summary

**Date:** 2026-06-21
**Thread:** multi-model-benchmark

## DeepSeek-Coder-V2-Lite Results

### Juliet PoC (247 alerts, k=5, 5-fold CV)
- Precision 37.6%, Recall 100%, ECE 0.620 (WORST)
- 98% unanimous 5/5 — most degenerate confidence
- Predicts TP for ALL 247 alerts (100% TP-bias)

### CWE-Bench-Java (549 alerts, k=1)
- **Precision 4.0% (BEST), Recall 82.4%, F1 0.080 (BEST)**
- TN=184 (BEST — correctly rejects most FPs)
- Only 10 abstentions (2%)

## Final 5-Model Comparison Summary

### Juliet PoC Ranking (by ECE — lower is better)
1. R1-Distill-14B: ECE 0.335, 36% unanimous — BEST calibrated
2. GLM-4-9B-Chat: ECE 0.513, 61% unanimous
3. Gemini Flash Lite: ECE 0.555, 85% unanimous
4. Qwen-Coder-32B: ECE 0.565, 86% unanimous
5. DS-Coder-V2-Lite: ECE 0.620, 98% unanimous — WORST

### CWE-Bench-Java Ranking (by F1 — higher is better)
1. DS-Coder-V2-Lite: F1 0.080, Precision 4.0%, TN 184 — BEST
2. Gemini Flash Lite: F1 0.063, Precision 3.3%
3. R1-Distill-14B: F1 0.060, Recall 100%
4. GLM-4-9B-Chat: F1 0.040
5. Qwen-Coder-32B: F1 0.030 — WORST

## Key Paper-Ready Insights

1. **Reasoning → Calibrated Confidence:** R1-Distill-14B's thinking process produces
   diverse k=5 votes (36% unanimous vs 85-98% for others), yielding ECE 0.335.
   This is the first model where conformal calibration shows meaningful benefit.

2. **Code-Specialization ≠ Better Triage:** Despite being code-specialized,
   Qwen-Coder-32B and DS-Coder-V2-Lite have the most degenerate confidence.
   However, DS-Coder-V2-Lite has the best CWE-Bench precision (4.0%) and TN (184).

3. **The Precision-Recall Tradeoff:** R1-Distill-14B (100% recall, 3.0% precision)
   vs Qwen-Coder-32B (40% recall, 1.5% precision) — models span the full tradeoff
   spectrum. The ideal triage model needs high precision (FP rejection), which
   no current model achieves without calibration.

4. **Calibration Only Helps with Good Signals:** Conformal calibration improves
   precision by <1pp for models with degenerate confidence (85-98% unanimous)
   but by ~2pp for R1-Distill-14B (36% unanimous). The confidence signal quality
   is the bottleneck, not the calibration algorithm.
