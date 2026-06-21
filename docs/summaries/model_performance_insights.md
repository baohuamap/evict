# Model Performance Insights

**Last updated:** 2026-06-21
**Total models benchmarked:** 5 (3 on H100 via vLLM + 2 via hosted APIs)

EVICT framework on Juliet Benchmark and CWE-Bench-Java for static analysis alert triage.

## Juliet Conformal PoC (247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1)

| Model | Params | Precision | Recall | F1 | Coverage | ECE | Unanimous |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **R1-Distill-14B** | 14B | **40.0%** | 71.9% | 51.2% | 98.4% | **0.335** | **36%** |
| Gemini 2.5 Flash Lite | ~? | 38.9% | 95.5% | 55.1% | 100% | 0.555 | 85% |
| GLM-4-9B-Chat | 9B | 38.0% | 95.9% | 54.3% | 100% | 0.513 | 61% |
| DS-Coder-V2-Lite | 16B MoE | 37.6% | **100%** | 54.5% | 100% | 0.620 | 98% |
| Qwen-Coder-32B | 32B | 37.0% | 81.5% | 50.7% | 100% | 0.565 | 86% |

## CWE-Bench-Java (549 alerts, 45 projects, k=1)

| Model | Precision | Recall | F1 | TP | FP | TN | FN | ABSTAIN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **DS-Coder-V2-Lite** | **4.0%** | 82.4% | **0.080** | 14 | 338 | **184** | 3 | 10 (2%) |
| Gemini Flash Lite | 3.3% | 93.3% | 0.063 | 14 | 414 | 47 | 1 | 73 (13%) |
| R1-Distill-14B | 3.0% | **100%** | 0.060 | 13 | 427 | 32 | **0** | 77 (14%) |
| GLM-4-9B-Chat | 1.9% | 62.5% | 0.040 | 5 | 259 | 97 | 3 | 185 (34%) |
| Qwen-Coder-32B | 1.5% | 40.0% | 0.030 | 2 | 128 | 76 | 3 | 340 (62%) |

## Juliet Multi-Model Baseline (Table 1, k=1, existing hosted API data)

| Model | Alerts | Coverage | Precision | Recall | ECE |
| --- | --- | --- | --- | --- | --- |
| Claude Haiku 4.5 | 3,061 | 97.5% | 59.9% | 36.8% | 0.358 |
| Gemini 3.1 Flash Lite Preview | 991 | 56.0% | 48.0% | 37.4% | 0.465 |
| Gemini 2.5 Flash Lite | 3,222 | 84.3% | 46.3% | 66.6% | 0.488 |
| GPT-5 Nano | 1,045 | 98.0% | 44.9% | 78.1% | 0.538 |
| GPT-4o Mini | 3,107 | 98.8% | 42.2% | 90.8% | 0.547 |

## Key Insights

### Reasoning Models Produce Calibrated Confidence
- R1-Distill-14B: 36% unanimous → ECE 0.335 (BEST)
- Standard models: 61-98% unanimous → ECE 0.513-0.620
- The "thinking" process causes k=5 samples to disagree when uncertain

### Code-Specialization Helps FP Rejection but Not Confidence
- DS-Coder-V2-Lite: Best CWE-Bench precision (4.0%) and TN (184)
- But worst confidence degeneracy (98% unanimous, ECE 0.620)
- Code models are better at recognizing safe code but overconfident in their judgments

### The Confidence-Quality Hierarchy
```
Reasoning (R1-Distill):    36% unanimous → ECE 0.335 → calibration works
Small inst-tuned (GLM):    61% unanimous → ECE 0.513 → barely helps
Lite commercial (Gemini):  85% unanimous → ECE 0.555 → ineffective
Code 32B (Qwen):           86% unanimous → ECE 0.565 → ineffective
Code MoE (DS-Coder-V2):    98% unanimous → ECE 0.620 → broken
```

### Model Size ≠ Confidence Quality
- GLM-4-9B (9B) has better ECE (0.513) than Qwen-Coder-32B (0.565)
- R1-Distill-14B (14B) has better ECE than all 32B+ models
- Training objective (reasoning vs instruction-tuned) matters more than scale
