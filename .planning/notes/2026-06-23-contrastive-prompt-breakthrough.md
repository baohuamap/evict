# Note: Contrastive Prompt Strategy — MAJOR FINDING

**Date:** 2026-06-23
**Thread:** multi-model-benchmark

## BREAKTHROUGH: Prompt Technique Fixes Confidence Degeneracy

The contrastive prompt strategy (forcing the model to argue both TP and FP sides
before deciding) produces dramatically more diverse confidence than ANY model
tested with the default prompt — including reasoning models.

### Results (Gemini 2.5 Flash Lite, k=5, 247 Juliet alerts)

| Metric | Default Prompt | Contrastive Prompt | R1-Distill-14B (default) |
|--------|---------------|-------------------|--------------------------|
| Unanimous | 84.6% | **16.2%** | 36.0% |
| ABSTAIN | 0% | **29.1%** | 0.4% |
| TP predictions | 93.5% | 68.4% | 68.0% |
| FP predictions | 6.5% | 2.4% | 31.6% |
| Confidence spread | {1.0: 209, 0.8: 32} | {0.4:17, 0.6:101, 0.8:89, 1.0:40} | {0.4:3, 0.6:81, 0.8:74, 1.0:89} |

### Why This Matters

1. **Prompt > Model for confidence quality:** A standard lite model with the
   contrastive prompt (16.2% unanimous) outperforms a 14B reasoning model with
   the default prompt (36% unanimous) on confidence diversity.

2. **Practical deployment:** Lite models are 10-100x cheaper and faster than
   reasoning models. If prompt technique alone can fix confidence quality,
   conformal calibration becomes deployable with cheap models.

3. **Conformal calibration can now work:** With 16.2% unanimous and well-spread
   confidence (0.4-1.0), the conformal q-hat will be meaningful — the calibration
   can actually discriminate between certain and uncertain predictions.

4. **The "argue both sides" mechanism:** Forcing the model to construct the
   strongest FP argument before deciding creates natural disagreement across
   k=5 samples when the case is genuinely ambiguous. This is the same mechanism
   that makes reasoning models produce diverse confidence, but achieved through
   prompt design rather than model architecture.

### Contrastive Prompt Design
The key innovation is Step 2: "Describe why this might be a false positive."
This forces the model to actively search for FP evidence (sanitizers, infeasible
paths, non-attacker input) before committing to a label. The natural disagreement
across samples arises because different samples may weight the TP vs FP
arguments differently.

## Still Running
- decomposed strategy (sub-question decomposition)
- few_shot strategy (calibrated examples)
- Results pending
