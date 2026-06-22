# Model Performance Insights

**Last updated:** 2026-06-22
**Total models benchmarked:** 6 (4 on H100 via vLLM + 2 via hosted APIs)
**Total experiments:** 17 (E1-E17)

## Juliet Conformal PoC (247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1)

| Model | Type | Precision | Recall | ECE | Unanimous | Calib. Benefit |
| --- | --- | --- | --- | --- | --- | --- |
| **Claude Haiku 4.5** | Frontier lite | **47.4%** | 34.5% | 0.373 | 90% | +1.7pp |
| **R1-Distill-14B** | 14B reasoning | 40.0% | 71.9% | **0.335** | **36%** | +1.1pp |
| Gemini 2.5 Flash Lite | Lite instruct | 38.9% | 95.5% | 0.555 | 85% | <1pp |
| GLM-4-9B-Chat | 9B instruct | 38.0% | 95.9% | 0.513 | 61% | +1.1pp |
| DS-Coder-V2-Lite | 16B code MoE | 37.6% | **100%** | 0.620 | 98% | <1pp |
| Qwen-Coder-32B | 32B code | 37.0% | 81.5% | 0.565 | 86% | <1pp |

## CWE-Bench-Java (549 alerts, 45 projects, k=1)

| Model | Precision | Recall | F1 | TN | ABSTAIN |
| --- | --- | --- | --- | --- | --- |
| **DS-Coder-V2-Lite** | **4.0%** | 82.4% | **0.080** | **184** | 10 (2%) |
| Gemini Flash Lite | 3.3% | 93.3% | 0.063 | 47 | 73 (13%) |
| R1-Distill-14B | 3.0% | **100%** | 0.060 | 32 | 77 (14%) |
| GLM-4-9B-Chat | 1.9% | 62.5% | 0.040 | 97 | 185 (34%) |
| Qwen-Coder-32B | 1.5% | 40.0% | 0.030 | 76 | 340 (62%) |

## R1-Distill-14B CWE-Bench k=5 Sample (100 alerts)

| Metric | Value |
| --- | --- |
| Unanimous | **46%** (confirms reasoning → diverse confidence on real-world alerts) |
| Confidence | {0.4: 1, 0.6: 24, 0.8: 29, 1.0: 46} |
| Precision | 3.4% |
| Recall | 100% |
| ABSTAIN | 10% |

## Frontier Model Projections (estimated, ±5pp uncertainty)

| Model | Est. Precision | Est. ECE | Est. Unanimous | Calib. Benefit |
| --- | --- | --- | --- | --- |
| Claude Opus 4 | 60-70% | 0.25-0.35 | 80-95% | Marginal |
| GPT-4.5 | 60-70% | 0.20-0.35 | 30-50% | Moderate |
| Claude Sonnet 4 | 55-65% | 0.20-0.30 | 30-50% | Moderate |
| Gemini 3 Pro | 55-65% | 0.25-0.40 | 40-60% | Marginal |
| GLM-5 | 50-60% | 0.25-0.40 | 30-50% | Moderate (if reasoning) |

## Key Insights

### Training Objective > Model Size for Confidence Quality
- R1-Distill-14B (14B): 36% unanimous → ECE 0.335 (BEST)
- Qwen-Coder-32B (32B): 86% unanimous → ECE 0.565
- GLM-4-9B (9B): 61% unanimous → ECE 0.513 (better than 32B!)
- Training objective (reasoning vs instruct vs code) matters more than scale

### Two Paths to Good ECE
1. **Diverse confidence** (R1: 36% unanimous → ECE 0.335) — reasoning creates disagreement
2. **High base precision** (Claude: 90% unanimous but 47.4% precision → ECE 0.373)
- Ideal: frontier reasoning model (both paths combined)

### Code-Specialization Paradox
- Code models have WORST confidence quality (86-98% unanimous)
- But BEST FP rejection on real-world alerts (DS-Coder-V2-Lite TN=184)
- Code specialization improves semantic understanding but degrades UQ

### Confidence Hierarchy
```
Reasoning (R1-Distill):     36% unanimous → ECE 0.335 → calibration works
Frontier-lite (Claude):     90% unanimous → ECE 0.373 → high precision compensates
Instruct (GLM):             61% unanimous → ECE 0.513 → barely helps
Lite (Gemini):              85% unanimous → ECE 0.555 → ineffective
Code 32B (Qwen):            86% unanimous → ECE 0.565 → ineffective
Code MoE (DS-Coder-V2):     98% unanimous → ECE 0.620 → broken
```
