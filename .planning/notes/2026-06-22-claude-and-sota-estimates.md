# Note: Claude Haiku 4.5 PoC + R1 CWE-Bench k=5 + SOTA Estimates

**Date:** 2026-06-22
**Thread:** multi-model-benchmark

## Claude Haiku 4.5 PoC (E16)
- **Precision 47.4% (BEST of all models), ECE 0.373 (2nd best)**
- **FP-biased**: 71.7% FP predictions (opposite of all other models)
- Recall only 34.5% (very conservative)
- 90.3% unanimous — degenerate vote-share despite frontier quality
- Calibration benefit: +1.7pp precision (marginal, limited by unanimity)

## R1-Distill-14B CWE-Bench k=5 Sample (E17)
- 100 alerts, k=5: **46% unanimous** (similar to Juliet's 36%)
- Confidence: {0.4: 1, 0.6: 24, 0.8: 29, 1.0: 46} — well-spread
- Precision 3.4%, Recall 100%, 10% ABSTAIN
- **Confirms: reasoning models produce diverse confidence on BOTH synthetic and real-world tasks**

## SOTA Frontier Model Estimates
Created comprehensive estimates for Claude Opus 4, Sonnet 4, GPT-4.5, Gemini 3 Pro, GLM-5.
Key prediction: Claude models have degenerate vote-share (90%+ unanimous) but high base precision.
The ideal model for EVICT would be a frontier REASONING model (combines high precision + diverse confidence).

## Two Paths to Good ECE
1. Diverse confidence (R1: 36% unanimous → ECE 0.335) — reasoning creates disagreement
2. High base precision (Claude: 90% unanimous but 47.4% precision → ECE 0.373) — correct confident predictions
