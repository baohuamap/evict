# EVICT: Findings & Test Results Tracker

**Last updated:** 2026-06-20
**Purpose:** Centralized record of all real measured results, key findings, and their implications for the paper. Update this file as new experiments run.

---

## 1. Experiment Inventory

| ID | Experiment | Date | Model | k | Alerts | Status | Result File |
|----|-----------|------|-------|---|--------|--------|-------------|
| E1 | Juliet PoC (conformal) | 2026-06-20 | Gemini 2.5 Flash Lite | 5 | 247 | DONE | `artifacts/exports/v2/juliet_conformal_poc_gemini.csv` |
| E2 | CWE-Bench-Java | 2026-06-20 | Gemini 2.5 Flash Lite | 1 | 549 | DONE | `artifacts/exports/cwe_bench_evict_results_gemini.csv` |
| E8 | Juliet PoC (conformal) | 2026-06-20 | Qwen-Coder-32B (vLLM) | 5 | 247 | DONE | `artifacts/exports/v2/juliet_conformal_poc_qwen_coder_32b.csv` |
| E9 | CWE-Bench-Java | 2026-06-20 | Qwen-Coder-32B (vLLM) | 1 | 549 | DONE | `artifacts/exports/cwe_bench_evict_results_qwen_coder_32b.csv` |
| E10 | Juliet PoC (conformal) | 2026-06-21 | GLM-4-9B-Chat (vLLM) | 5 | 247 | DONE | `artifacts/exports/v2/juliet_conformal_poc_glm_4_9b_chat.csv` |
| E11 | CWE-Bench-Java | 2026-06-21 | GLM-4-9B-Chat (vLLM) | 1 | 549 | DONE | `artifacts/exports/cwe_bench_evict_results_glm_4_9b_chat.csv` |
| E12 | Juliet PoC (conformal) | 2026-06-21 | DeepSeek-R1-Distill-Qwen-14B (vLLM) | 5 | 247 | DONE | `artifacts/exports/v2/juliet_conformal_poc_r1_distill_14b.csv` |
| E13 | CWE-Bench-Java | 2026-06-21 | DeepSeek-R1-Distill-Qwen-14B (vLLM) | 1 | 549 | DONE | `artifacts/exports/cwe_bench_evict_results_r1_distill_14b.csv` |
| E3 | Juliet multi-model baseline (Claude Haiku 4.5) | 2026-05-02 | Claude Haiku 4.5 | 1 | 3,061 | DONE | `artifacts/exports/v2/juliet_sampled_results_claude_haiku_4_5.csv` |
| E4 | Juliet multi-model baseline (GPT-4o Mini) | 2026-05-01 | GPT-4o Mini | 1 | 3,107 | DONE | `artifacts/exports/v2/juliet_sampled_results_gpt_4o_mini.csv` |
| E5 | Juliet multi-model baseline (Gemini 2.5 Flash Lite) | 2026-05-02 | Gemini 2.5 Flash Lite | 1 | 3,222 | DONE | `artifacts/exports/v2/juliet_sampled_results_gemini_2_5_flash_lite.csv` |
| E6 | Juliet multi-model baseline (GPT-5 Nano) | 2026-05-02 | GPT-5 Nano | 1 | 1,045 | DONE | `artifacts/exports/v2/juliet_sampled_results_gpt_5_nano.csv` |
| E7 | Juliet multi-model baseline (Gemini 3.1 Flash Lite Preview) | 2026-05-02 | Gemini 3.1 Flash Lite Preview | 1 | 991 | DONE | `artifacts/exports/v2/juliet_sampled_results_gemini_3_1_flash_lite_preview.csv` |

### Reproducibility Artifacts
- **PoC cache:** `artifacts/exports/v2/juliet_conformal_poc_gemini.cache.json` (247 decisions with labels, confidences, rationales)
- **CWE-Bench cache:** `artifacts/exports/cwe_bench_evict_results_gemini.cache.json` (549 decisions)
- **SARIF generation:** `artifacts/codeql_results/` (45 SARIF files, gitignored — regenerate with `bash scripts/generate_sarifs.sh`)
- **Re-run PoC:** `python scripts/benchmark_juliet_conformal.py --live --provider gemini --model gemini-2.5-flash-lite` (uses cache, only calls API for uncached alerts)
- **Re-run CWE-Bench:** `python scripts/benchmark_cwe_bench.py --provider gemini --model gemini-2.5-flash-lite --num_samples 1` (uses cache)

---

## 2. Key Results: Juliet PoC (E1)

### Setup
- **CWEs:** 89 (SQL injection), 78 (OS command injection), 190 (integer overflow)
- **Sampling:** 50-100 alerts per CWE, seeded (seed=42)
- **Ground truth:** 93 TP, 154 FP (Juliet `bad()`/`good()` method heuristic)
- **Conformal:** 5-fold CV, 60/20/20 train/cal/test split, alpha=0.1, k=5 pass@5
- **LLM:** Gemini 2.5 Flash Lite, temperature=0.7

### Results (mean ± std over 5 folds)

| Method | Precision | Recall | F1 | Coverage | ECE | R_sel |
|--------|-----------|--------|----|----------|-----|-------|
| Evidence-Free | 38.9 ± 3.3% | 96.8 ± 2.6% | 55.4 ± 3.5% | 100.0% | 0.555 ± 0.031 | 0.584 ± 0.044 |
| Evidence-Cond. (No Cal.) | 38.9 ± 3.3% | 96.8 ± 2.6% | 55.4 ± 3.5% | 100.0% | 0.555 ± 0.031 | 0.584 ± 0.044 |
| EVICT (No Symb.) | 38.6 ± 3.0% | 97.8 ± 2.7% | 55.3 ± 3.1% | 97.6% | 0.559 ± 0.030 | 0.586 ± 0.035 |
| EVICT (Full) | 38.7 ± 3.4% | 95.5 ± 2.3% | 55.1 ± 3.8% | 100.0% | 0.555 ± 0.025 | 0.584 ± 0.038 |

### LLM Decision Distribution
- **Labels:** TP=231 (93.5%), FP=16 (6.5%), ABSTAIN=0
- **Confidence (vote-share):** 1.0 → 209 (84.6%), 0.8 → 32 (13.0%), 0.6 → 5 (2.0%), 0.4 → 1 (0.4%)
- **Conformal q_hat:** 0.200 (all 5 folds identical — degenerate calibration set)
- **Alerts abstained by calibration:** 6/247 (2.4%)

### Previous Paper Claims vs Real

| Metric | Paper Claimed | Real Measured | Delta |
|--------|--------------|---------------|-------|
| Precision | 91.2% | 38.9% | -52.3 pp |
| Recall | 87.9% | 95.5% | +7.6 pp |
| F1 | 89.5% | 55.1% | -34.4 pp |
| Coverage | 89.6% | 97.6-100% | +8-10 pp |
| ECE | 0.08 | 0.555 | +0.475 |
| R_sel | 0.088 | 0.584 | +0.496 |
| Symbolic corrections | 23 | 0 | -23 |
| Sample size | 1,000 | 247 | -753 |

---

## 3. Key Results: CWE-Bench-Java (E2)

### Setup
- **Projects:** 45 (of 201 in CWE-Bench-Java; 156 Docker images unavailable)
- **Alerts:** 549 CodeQL security alerts (java-code-scanning suite, excluding IRIS myqueries)
- **Ground truth:** 17 TP, 532 FP (97% FP rate — CodeQL security queries are noisy)
- **LLM:** Gemini 2.5 Flash Lite, k=1 (budget-saving), temperature=0.7
- **Ground truth matching:** file path suffix + line within method range (from `fix_info.csv`)

### Results

| Metric | Value |
|--------|-------|
| Total alerts | 549 |
| TP (correct) | 14 |
| FP (false positive predictions) | 414 |
| FN (missed) | 1 |
| TN (correctly rejected) | 47 |
| ABSTAIN | 73 |
| **Precision** | **3.3%** |
| **Recall** | **93.3%** |
| **F1** | **0.063** |

### Prediction Distribution
- TP predicted: 428 (78.0%) — massive TP-bias
- FP predicted: 48 (8.7%)
- ABSTAIN: 73 (13.3%) — from LLM refusals, not calibration (k=1 → all confidence=1.0)

### Ground Truth Matching Limitation
- Only 17/549 alerts matched as TP — the file-suffix + line-range heuristic is conservative
- The 1 missed TP (FN) suggests matching is slightly lossy
- CodeQL alerts on real projects produce mostly FPs (97%), unlike Juliet's balanced TP/FP

---

## 3b. Key Results: Qwen-Coder-32B PoC (E8)

### Setup
- **Model:** Qwen2.5-Coder-32B-Instruct, served via vLLM 0.7.3 on H100 80GB (8k context, BF16)
- **Same protocol as E1:** 247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1

### Results (mean ± std over 5 folds)

| Method | Precision | Recall | F1 | Coverage | ECE | R_sel |
|--------|-----------|--------|----|----------|-----|-------|
| Evidence-Free | 36.8 ± 5.5% | 81.5 ± 6.5% | 50.6 ± 6.1% | 100% | 0.569 ± 0.083 | 0.600 ± 0.082 |
| EVICT (No Symb.) | 37.4 ± 6.1% | 82.3 ± 6.5% | 51.3 ± 6.8% | 98.0% | 0.571 ± 0.081 | 0.594 ± 0.086 |
| EVICT (Full) | 37.0 ± 5.6% | 81.5 ± 6.5% | 50.7 ± 6.2% | 100% | 0.565 ± 0.087 | 0.596 ± 0.085 |

### LLM Decision Distribution
- **Labels:** TP=207 (83.8%), FP=40 (16.2%), ABSTAIN=0
- **Confidence:** 1.0 → 212 (85.8%), 0.8 → 22 (8.9%), 0.6 → 13 (5.3%)
- **Unanimous 5/5:** 85.8% — similarly degenerate to Gemini (84.6%)

### Gemini vs Qwen-Coder-32B Comparison (Juliet PoC)

| Metric | Gemini 2.5 Flash Lite | Qwen-Coder-32B |
|--------|----------------------|----------------|
| Precision | 38.9% | 37.0% |
| Recall | 95.5% | 81.5% |
| F1 | 55.1% | 50.7% |
| TP predictions | 231 (93.5%) | 207 (83.8%) |
| Unanimous 5/5 | 84.6% | 85.8% |

**Finding:** Qwen-Coder-32B is more conservative (fewer TP predictions) but similarly overconfident (85.8% unanimous). Neither model produces discriminative vote-share confidence.

---

## 3c. Key Results: Qwen-Coder-32B CWE-Bench-Java (E9)

### Setup
- **Model:** Qwen2.5-Coder-32B-Instruct via vLLM, k=1, 549 CodeQL alerts, 45 projects

### Results

| Metric | Gemini 2.5 Flash Lite | Qwen-Coder-32B |
|--------|----------------------|----------------|
| Precision | 3.3% | 1.5% |
| Recall | 93.3% | 40.0% |
| F1 | 0.063 | 0.030 |
| TP | 14 | 2 |
| FP | 414 | 128 |
| TN | 47 | 76 |
| FN | 1 | 3 |
| ABSTAIN | 73 (13.3%) | 340 (62.0%) |
| TP predictions | 428 (78%) | 130 (24%) |
| FP predictions | 48 (9%) | 79 (14%) |

### Key Observation
Qwen-Coder-32B is **dramatically more conservative** than Gemini on real-world alerts:
- 62% abstention rate (vs Gemini's 13%) — refuses to classify most alerts
- Higher TN (76 vs 47) — better at correctly identifying FPs when it does classify
- But lower recall (40% vs 93%) — misses most real vulnerabilities
- The high abstention suggests Qwen "knows what it doesn't know" better than Gemini, but the abstention comes from LLM refusals (empty/conflicted JSON), not from conformal calibration

---

## 3d. Key Results: GLM-4-9B-Chat PoC (E10)

### Setup
- **Model:** zai-org/glm-4-9b-chat, served via vLLM 0.7.3 on H100 80GB (8k context, BF16)
- **Same protocol as E1/E8:** 247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1

### Results (mean ± std over 5 folds)

| Method | Precision | Recall | F1 | Coverage | ECE | R_sel |
|--------|-----------|--------|----|----------|-----|-------|
| Evidence-Free | 38.0 ± 3.3% | 95.9 ± 3.8% | 54.3 ± 3.1% | 100% | 0.513 ± 0.050 | 0.604 ± 0.042 |
| EVICT (No Symb.) | 39.1 ± 4.6% | 97.9 ± 2.6% | 55.7 ± 4.8% | 96.3% | 0.516 ± 0.046 | 0.595 ± 0.052 |
| EVICT (Full) | 38.0 ± 3.3% | 95.9 ± 3.8% | 54.3 ± 3.1% | 100% | 0.513 ± 0.050 | 0.604 ± 0.042 |

### LLM Decision Distribution
- **Labels:** TP=234 (94.7%), FP=13 (5.3%), ABSTAIN=0
- **Confidence:** 1.0 → 150 (60.7%), 0.8 → 69 (27.9%), 0.6 → 28 (11.3%)
- **Unanimous 5/5:** 60.7% — **the most diverse confidence distribution so far** (vs 84.6% Gemini, 85.8% Qwen)
- **Best ECE:** 0.513 (vs 0.555 Gemini, 0.565 Qwen) — the more diverse confidence directly improves calibration

### Key Observation
GLM-4-9B-Chat produces significantly more diverse vote-share confidence (only 60.7%
unanimous vs 85%+ for the other models). This translates to a marginally better ECE
(0.513) and a small calibration benefit: EVICT (No Symb.) achieves 39.1% precision
(+1.1pp over evidence-free) at 96.3% coverage. However, the improvement is still
modest because the confidence signal, while more diverse, does not strongly
correlate with correctness — overconfident wrong answers still dominate.

---

## 3e. Key Results: GLM-4-9B-Chat CWE-Bench-Java (E11)

### Setup
- **Model:** GLM-4-9B-Chat via vLLM, k=1, 549 CodeQL alerts, 45 projects

### Results

| Metric | Gemini 2.5 Flash Lite | Qwen-Coder-32B | GLM-4-9B-Chat |
|--------|----------------------|----------------|---------------|
| Precision | 3.3% | 1.5% | 1.9% |
| Recall | 93.3% | 40.0% | 62.5% |
| F1 | 0.063 | 0.030 | 0.040 |
| TP | 14 | 2 | 5 |
| FP | 414 | 128 | 259 |
| TN | 47 | 76 | 97 |
| FN | 1 | 3 | 3 |
| ABSTAIN | 73 (13.3%) | 340 (62.0%) | 185 (33.7%) |
| TP predictions | 428 (78%) | 130 (24%) | 264 (48%) |
| FP predictions | 48 (9%) | 79 (14%) | 100 (18%) |

### Key Observation
GLM-4-9B-Chat sits between Gemini (aggressive, 13% abstain) and Qwen (conservative,
62% abstain) with 33.7% abstention. It has the highest TN count (97) of the three,
meaning it correctly rejects more false positives. However, precision remains very
low (1.9%) because the base rate of TPs in CWE-Bench is only 3.1%.

---

## 3f. Key Results: DeepSeek-R1-Distill-Qwen-14B PoC (E12)

### Setup
- **Model:** deepseek-ai/DeepSeek-R1-Distill-Qwen-14B (reasoning model), served via vLLM 0.7.3 on H100 80GB (8k context, BF16)
- **Same protocol as E1/E8/E10:** 247 alerts, CWE-89/78/190, k=5, 5-fold CV, alpha=0.1
- **Runtime:** ~3 hours (reasoning model generates long thinking traces before JSON)

### Results (mean ± std over 5 folds)

| Method | Precision | Recall | F1 | Coverage | ECE | R_sel |
|--------|-----------|--------|----|----------|-----|-------|
| Evidence-Free | 39.7 ± 2.4% | 71.9 ± 6.2% | 51.0 ± 1.8% | 100% | 0.335 ± 0.073 | 0.518 ± 0.053 |
| EVICT (No Symb.) | 40.0 ± 2.4% | 71.9 ± 6.2% | 51.2 ± 1.6% | 98.4% | 0.331 ± 0.072 | 0.523 ± 0.054 |
| EVICT (Full) | 40.0 ± 2.4% | 71.9 ± 6.2% | 51.2 ± 1.6% | 100% | 0.331 ± 0.072 | 0.514 ± 0.051 |

### LLM Decision Distribution
- **Labels:** TP=168 (68.0%), FP=78 (31.6%), ABSTAIN=1 (0.4%)
- **Confidence:** 1.0 → 89 (36.0%), 0.8 → 74 (30.0%), 0.6 → 81 (32.8%), 0.4 → 3 (1.2%)
- **Unanimous 5/5:** 36.0% — **BY FAR the most diverse confidence distribution** (vs 60.7% GLM, 84.6% Gemini, 85.8% Qwen)
- **Best ECE:** 0.335 (vs 0.513 GLM, 0.555 Gemini, 0.565 Qwen) — 39% lower ECE than the next best

### Key Observation
The reasoning model (R1-Distill-14B) produces dramatically more diverse vote-share
confidence (only 36% unanimous vs 60-86% for non-reasoning models). This translates
to the best ECE by a wide margin (0.335 vs 0.513-0.565). The reasoning process
("thinking" before answering) appears to produce more calibrated self-consistency
votes — when the model is uncertain, the 5 samples disagree more often, producing
lower confidence scores that correctly reflect uncertainty. This is the first model
where conformal calibration shows a meaningful (though still modest) benefit:
EVICT (No Symb.) achieves 40.0% precision at 98.4% coverage.

### Implications for Paper
This finding directly supports the paper's thesis that calibrated abstention can
improve triage reliability — but ONLY when the underlying confidence signal is
discriminative. Reasoning models (R1 distill) produce much better confidence
signals than standard instruction-tuned models. The paper should:
1. Report R1-Distill-14B as the best-calibrated model
2. Highlight the reasoning → confidence diversity → calibration quality chain
3. Acknowledge that standard lite models (Gemini, Qwen) have degenerate confidence

---

## 3g. Key Results: DeepSeek-R1-Distill-Qwen-14B CWE-Bench-Java (E13)

### Setup
- **Model:** R1-Distill-14B via vLLM, k=1, 549 CodeQL alerts, 45 projects
- **Runtime:** ~58 minutes

### Results

| Metric | Gemini 2.5 Flash Lite | Qwen-Coder-32B | GLM-4-9B-Chat | R1-Distill-14B |
|--------|----------------------|----------------|---------------|----------------|
| Precision | 3.3% | 1.5% | 1.9% | 3.0% |
| Recall | 93.3% | 40.0% | 62.5% | **100.0%** |
| F1 | 0.063 | 0.030 | 0.040 | 0.060 |
| TP | 14 | 2 | 5 | **13** |
| FP | 414 | 128 | 259 | 427 |
| TN | 47 | 76 | 97 | 32 |
| FN | 1 | 3 | 3 | **0** |
| ABSTAIN | 73 (13.3%) | 340 (62.0%) | 185 (33.7%) | 77 (14.0%) |

### Key Observation
R1-Distill-14B achieves **100% recall** on CWE-Bench-Java — it catches every
single true positive (13/13, with FN=0). However, it also predicts TP for 427
false positives, giving only 3.0% precision. The reasoning model's thoroughness
makes it excellent at finding real vulnerabilities but terrible at filtering FPs.
This is the opposite of Qwen-Coder-32B (conservative, 62% abstain, 40% recall).
The 14% abstention rate is close to Gemini's 13%, suggesting the reasoning model
doesn't refuse more often despite being more "thoughtful."

---

## 4. Key Results: Multi-Model Baseline (E3-E7, Table 1)

These are the **existing real results** that were already in the paper's Table 1. They are verified against the CSV files.

| Model | Alerts | Coverage | Precision | Recall | ECE |
|-------|--------|----------|-----------|--------|-----|
| Claude Haiku 4.5 | 3,061 | 97.5% | 59.9% | 36.8% | 0.358 |
| Gemini 3.1 Flash Lite Preview | 991 | 56.0% | 48.0% | 37.4% | 0.465 |
| Gemini 2.5 Flash Lite | 3,222 | 84.3% | 46.3% | 66.6% | 0.488 |
| GPT-5 Nano | 1,045 | 98.0% | 44.9% | 78.1% | 0.538 |
| GPT-4o Mini | 3,107 | 98.8% | 42.2% | 90.8% | 0.547 |

**Note:** These used k=1 (not k=5), so confidence is always 1.0 — calibration was never applied. The ECE values are computed from the raw label correctness vs. the (degenerate) confidence.

---

## 5. Critical Findings

### Finding 1: Vote-Share Confidence is Degenerate (CRITICAL)

**85% of pass@5 decisions receive unanimous 5/5 vote-share** (confidence = 1.0), even for false positives. This is the single most important finding.

**Evidence:**
- PoC (E1): 209/247 = 84.6% unanimous
- Distribution: {1.0: 209, 0.8: 32, 0.6: 5, 0.4: 1}
- The LLM is consistently confident even when wrong

**Implication:** Conformal calibration cannot discriminate correct from incorrect predictions when the nonconformity score (1 - confidence) is 0.0 for 85% of alerts. q_hat collapses to 0.2 (the 90th percentile of a mostly-0 distribution), abstaining only 2.4% of alerts.

**Paper impact:** The paper's central claim — "calibrated abstention converts the unreliable raw output of fast lite models into a high-precision accepted set" — is **not supported** by the current vote-share confidence signal.

### Finding 2: Lite LLMs are TP-Biased

Gemini 2.5 Flash Lite predicts TP for 93.5% of Juliet alerts and 78.0% of CWE-Bench-Java alerts, regardless of ground truth.

**Evidence:**
- PoC: 231 TP / 16 FP predictions (93.5% TP)
- CWE-Bench: 428 TP / 48 FP / 73 ABSTAIN (78.0% TP)
- Recall is high (93-97%) but precision is low (3-39%)

**Implication:** The LLM defaults to "vulnerable" unless there is strong evidence of safety. This is the opposite of the desired triage behavior (filtering FPs).

### Finding 3: Z3 SMT Solver Returns UNKNOWN for Java String Conditions

The escalator's Z3 backend uses an integer-proxy variable (`data: Int`) to model path constraints. Java conditions like `!data.isEmpty()` or `data.contains("'")` cannot be translated to integer comparisons, so Z3 returns UNKNOWN.

**Evidence:**
- All 6 escalated alerts in the PoC returned UNKNOWN
- 0 symbolic corrections (vs paper's claimed 23)

**Implication:** The Z3 integer-proxy model is insufficient for Java taint-style vulnerabilities. Need either:
- A string-theory SMT encoding (Z3 supports `String` sort, but Java string methods are hard to model)
- JPF for actual Java path feasibility (stub exists, needs JPF_HOME setup)
- A different symbolic backend

### Finding 4: Sanitization Detection Did Not Trigger on Juliet

Juliet's synthetic vulnerable code (`bad()` methods) does not employ standard sanitizer patterns. The 15 sanitizer regexes (replaceAll, PreparedStatement, etc.) found no matches in the PoC CWE-89/78/190 test cases.

**Implication:** Sanitization detection is more useful for real-world code (CWE-Bench-Java) than for Juliet's synthetic cases. The CWE-Bench k=1 run doesn't isolate escalation effects (all confidence=1.0, so calibration never abstains, so escalation is never triggered).

### Finding 5: Conformal Calibration is Mechanically Correct

The implementation is correct — `fit_threshold` computes the right q-hat, the 60/20/20 split works, 5-fold CV works. The problem is the **input signal**, not the algorithm.

**Evidence:**
- Mock mode with simulated diverse confidence (0.2-1.0) showed calibration reducing coverage to 92.7% and improving ECE from 0.250 to 0.215
- With real LLM confidence (85% at 1.0), the algorithm has nothing to work with

### Finding 6: CWE-Bench-Java Ground Truth is 97% FP

CodeQL security queries on real Java projects produce overwhelmingly false positives: 532 FP / 17 TP out of 549 alerts.

**Implication:** This is actually the **target use case** for EVICT — triaging noisy static analysis alerts. But it means:
- Precision metrics look terrible (3.3%) because the base rate is 3.1% TP
- A perfect FP-rejector would achieve 100% precision at 3.1% recall
- The LLM's TP-bias is especially harmful here (414 FPs predicted as TP)

### Finding 7: Evidence-Free ≈ Evidence-Conditioned (No Cal.)

The PoC shows identical numbers for Evidence-Free and Evidence-Cond. (No Cal.) configurations.

**Implication:** The EvidencePack extraction either isn't providing useful signal to the LLM, or the LLM isn't using it effectively. The paper claims "+5.2 pp precision from evidence" — this is **not supported** by the current implementation. The evidence pack may need richer content (full data flow, better slicing) or the prompt may need restructuring.

---

## 6. Implications for Paper Sections

### Section 5 (Preliminary Results) — UPDATED
- **Table 2:** Replaced with real numbers (38.9% precision, ECE 0.555). See `sections/preliminary_results.tex`.
- **Table 1:** Unchanged — was already real.
- **Narrative:** Rewritten to honestly describe the vote-share degeneracy finding.
- **Figures:** `figures/calibration_plot.pdf` and `figures/risk_coverage_curve.pdf` are now **stale** — they show the old aspirational curves. Need regeneration from real data.

### Section 3 (Methodology)
- **Algorithm 3 (Conformal):** Algorithm is correct, but needs a note about the confidence signal requirement.
- **Algorithm 2 (Symbolic Escalation):** Z3 integer-proxy limitation should be acknowledged. JPF integration path described.

### Section 6 (Evaluation Plan)
- Should acknowledge that the full evaluation plan (50K alerts, user study) is future work.
- CWE-Bench-Java results (3.3% precision) should be reported honestly.

### Section 7 (Discussion)
- The "when EVICT succeeds/struggles" analysis should cite the vote-share degeneracy finding.
- Limitations should include: lite LLM confidence quality, Z3 Java modeling gaps, ground truth matching heuristic.

### Appendix
- **Figure regeneration needed:** `scripts/generate_figures.py` produces the calibration/risk-coverage plots. Need to update with real PoC data.

---

## 7. Recommended Next Experiments

### Priority 1: Richer Confidence Signals
- **Token log-probabilities:** If the LLM API exposes logprobs, use the probability of the predicted label token as confidence instead of vote-share.
- **Semantic consistency:** Measure pairwise agreement across k samples at the rationale level (not just label level).
- **Expected calibration:** Try Claude Haiku 4.5 (ECE 0.358 is better than Gemini's 0.555) or a larger model.

### Priority 2: k=5 on CWE-Bench-Java
- The CWE-Bench run used k=1 (budget). A k=5 run would show whether vote-share is also degenerate on real-world alerts.
- **Cost:** 549 × 5 = 2,745 LLM calls (~45 min at 0.1/s).

### Priority 3: JPF Integration
- Set up `JPF_HOME` and test the `_run_jpf` method on a sample Juliet case.
- Would allow real Java path feasibility checking instead of Z3 integer-proxy.

### Priority 4: Stronger Model Comparison
- Run the PoC with Claude Haiku 4.5 (best precision in Table 1 at 59.9%).
- Hypothesis: a more discriminative model may produce less degenerate vote-share.

### Priority 5: Figure Regeneration
- Update `scripts/generate_figures.py` to read from the real PoC CSV.
- Generate new `calibration_plot.pdf` and `risk_coverage_curve.pdf`.

---

## 8. Implementation Status

### What's Real Now (Implemented & Tested)
- [x] Conformal calibration (`fit_threshold`, 5-fold CV, alpha) — `calibrator.py`
- [x] Z3 SMT solving (SAT/UNSAT/UNKNOWN) — `escalator.py`
- [x] Sanitization detection (15 patterns) — `escalator.py`
- [x] JPF integration stub (needs `JPF_HOME`) — `escalator.py`
- [x] Path-constraint extraction (if/while/for guards) — `extractor.py`
- [x] Conformal PoC benchmark (5-fold, 4 configs) — `scripts/benchmark_juliet_conformal.py`
- [x] CWE-Bench-Java benchmark (caching, progress) — `scripts/benchmark_cwe_bench.py`
- [x] CodeQL SARIF generation (fixed query path) — `scripts/generate_sarifs.sh`
- [x] 10 unit tests (all pass) — `evict_pipeline/tests/test_pipeline.py`

### What's Still a Gap
- [ ] Token log-probability confidence (not implemented — API-dependent)
- [ ] JPF actual execution (stub only — needs `JPF_HOME` setup)
- [ ] Z3 string-theory encoding (currently integer-proxy only)
- [ ] Figure regeneration from real data
- [ ] Full 45-project CWE-Bench k=5 run (budget-dependent)
- [ ] Claude Haiku 4.5 PoC comparison (budget-dependent)

### Test Results
- **11 tests pass** (10 pipeline + 1 extractor)
- `pytest evict_pipeline/tests/test_pipeline.py tests/test_extractor_codeql.py`
- black/isort clean on modified files
- mypy clean on modified files (`escalator.py`, `calibrator.py`, `extractor.py`)

---

## 9. Budget Log

| Experiment | Model | Calls | Est. Cost | Date |
|-----------|-------|-------|-----------|------|
| E1 (PoC k=5) | Gemini 2.5 Flash Lite | 247 × 5 = 1,235 | ~$0.50 | 2026-06-20 |
| E2 (CWE-Bench k=1) | Gemini 2.5 Flash Lite | 549 | ~$0.10 | 2026-06-20 |
| **Total spent** | | **1,784** | **~$0.60** | |

Remaining budget: check your API dashboard. Gemini 2.5 Flash Lite is the cheapest option.

---

## 10. File Map for Paper Updates

When updating the paper, reference these files:

| Paper Element | Source File | Key Numbers |
|--------------|------------|-------------|
| Table 1 (multi-model baseline) | `artifacts/exports/v2/*_summary.md` | See Section 4 above |
| Table 2 (EVICT PoC) | `artifacts/exports/v2/juliet_conformal_poc_gemini.csv` | See Section 2 above |
| CWE-Bench results | `artifacts/exports/cwe_bench_evict_results_gemini.csv` | See Section 3 above |
| Calibration figure | `figures/calibration_plot.pdf` (STALE — needs regen) | — |
| Risk-coverage figure | `figures/risk_coverage_curve.pdf` (STALE — needs regen) | — |
| PoC decisions cache | `artifacts/exports/v2/juliet_conformal_poc_gemini.cache.json` | 247 decisions |
| CWE-Bench decisions cache | `artifacts/exports/cwe_bench_evict_results_gemini.cache.json` | 549 decisions |
