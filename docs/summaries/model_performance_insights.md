# Model Performance Insights

**Last updated:** 2026-06-20

EVICT framework on Juliet Benchmark and CWE-Bench-Java for static analysis alert triage.

## Juliet Multi-Model Baseline (Table 1, k=1, real data)

| Model | Alerts | Coverage | Precision | Recall | ECE |
| --- | --- | --- | --- | --- | --- |
| Claude Haiku 4.5 | 3,061 | 97.5% | 59.9% | 36.8% | 0.358 |
| Gemini 3.1 Flash Lite Preview | 991 | 56.0% | 48.0% | 37.4% | 0.465 |
| Gemini 2.5 Flash Lite | 3,222 | 84.3% | 46.3% | 66.6% | 0.488 |
| GPT-5 Nano | 1,045 | 98.0% | 44.9% | 78.1% | 0.538 |
| GPT-4o Mini | 3,107 | 98.8% | 42.2% | 90.8% | 0.547 |

## Juliet Conformal PoC (Table 2, k=5, 5-fold CV, alpha=0.1, Gemini 2.5 Flash Lite)

| Method | Precision | Recall | F1 | Coverage | ECE | R_sel |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence-Free | 38.9 ± 3.3% | 96.8 ± 2.6% | 55.4 ± 3.5% | 100% | 0.555 ± 0.031 | 0.584 ± 0.044 |
| EVICT (No Symb.) | 38.6 ± 3.0% | 97.8 ± 2.7% | 55.3 ± 3.1% | 97.6% | 0.559 ± 0.030 | 0.586 ± 0.035 |
| EVICT (Full) | 38.7 ± 3.4% | 95.5 ± 2.3% | 55.1 ± 3.8% | 100% | 0.555 ± 0.025 | 0.584 ± 0.038 |

## CWE-Bench-Java (k=1, 45 projects, Gemini 2.5 Flash Lite)

| Metric | Value |
| --- | --- |
| Total alerts | 549 |
| Precision | 3.3% |
| Recall | 93.3% |
| F1 | 0.063 |
| TP / FP / TN / FN / ABSTAIN | 14 / 414 / 47 / 1 / 73 |

## Key Insights

### Vote-Share Confidence is Degenerate
- **85% of pass@5 decisions get unanimous 5/5 votes** (confidence = 1.0)
- Conformal q_hat collapses to 0.2, abstaining only 2.4% of alerts
- Calibration cannot discriminate correct from incorrect predictions
- **Implication:** Need richer confidence signals (token logprobs, semantic consistency)

### Lite LLMs are TP-Biased
- Gemini 2.5 Flash Lite predicts TP for 93.5% of Juliet alerts, 78.0% of CWE-Bench alerts
- High recall (93-97%) but low precision (3-39%)
- **Implication:** The LLM defaults to "vulnerable" — opposite of desired triage behavior

### Claude Haiku 4.5 is the Best Lite Model
- Highest precision (59.9%) and best calibration (ECE 0.358)
- Most conservative (97.5% coverage, 36.8% recall) — closest to desired FP-rejection profile
- **Implication:** Try the conformal PoC with Claude Haiku 4.5 for better results

### Evidence-Free ≈ Evidence-Conditioned
- No precision difference between Evidence-Free and Evidence-Cond. configs
- **Implication:** EvidencePack may not provide useful signal, or prompt needs restructuring

### Z3 SMT Returns UNKNOWN for Java String Conditions
- 0 symbolic corrections (vs paper's previous claim of 23)
- Z3 integer-proxy can't model `!data.isEmpty()`, `data.contains("'")`
- **Implication:** Need JPF (Java path feasibility) or Z3 string-theory encoding
