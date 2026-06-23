# Rewrite EVICT Paper for ICSE 2027

## ROLE AND MISSION

You are an expert academic writer specializing in software engineering and applied machine learning. Your task is to rewrite the EVICT research paper for submission to **ICSE 2027** (the International Conference on Software Engineering, the flagship venue in the field).

The paper currently exists in a NeurIPS-oriented draft that has since been updated with **real, measured experimental results** (replacing earlier simulated baselines). Your job is to transform it into a polished, novel-academic-tone ICSE submission that leverages the genuine findings, addresses all prior reviewer concerns, and positions the contribution for the SE community.

### Notes from the author
- Be concise and precise.
- Find the "liquid gold" of insight buried in the experiments and make it the headline — don't bury the finding under pipeline description.
- Every number in the final paper must be traceable to a specific study in this prompt or explicitly marked as a projection. Do not invent, smooth, or round numbers beyond what's given. If a number is referenced but not provided here, write `[VERIFY: <what's needed>]` inline rather than fabricating it.

---

## PROJECT OVERVIEW

**EVICT** (Evidence-Conditioned Investigation with Calibrated Triage) is a framework for triaging static-analysis alerts. Static analyzers (SpotBugs, CodeQL, Infer) suffer false-positive rates of 40–90%, with manual triage costing 10–20 minutes per alert. EVICT reframes alert triage as **cost-sensitive selective prediction**: the system accepts an alert as TP or FP only when calibrated evidence supports a reliable decision, and **abstains** (defers to a human) otherwise.

### Four-stage pipeline
1. **Evidence Extractor** — Parses SARIF analyzer output into a structured `EvidencePack` (code slice, data-flow summary, path constraints, metadata). Uses JDT for Java, Clang for C/C++. Preserves evidence incompleteness as explicit flags rather than hiding it.
2. **LLM Verifier** — Applies a fixed four-step schema-guided reasoning prompt (restate claim → enumerate preconditions → check against evidence → emit TP/FP/ABSTAIN with confidence + rationale). Confidence via self-consistency vote share (k_sc=5, temperature 0.7) for API-only models, or logit margins for open-weight models.
3. **Confidence Calibrator** — Split-Conformal Prediction converts raw confidence into prediction sets. Singleton sets → committed TP/FP; empty or multi-label sets → abstention. Provides distribution-free finite-sample coverage guarantees.
4. **Symbolic Escalator** — Invoked selectively on abstained alerts. Z3 SMT for path feasibility, Java PathFinder (JPF) for Java, KLEE for C/C++. SMT `UNKNOWN` and timeouts are strictly treated as continued abstentions (safety preservation).

### Implementation
- Pipeline code: `evict_pipeline/src/evict_pipeline/` (`extractor.py`, `verifier.py`, `calibrator.py`, `escalator.py`, `pipeline.py`, `models.py`)
- Benchmark scripts: `scripts/` (Juliet PoC, CWE-Bench-Java, multi-model conformal, on-prem vLLM serving)
- All results below are from **actual runs** (CSV exports in `artifacts/exports/` and `artifacts/exports/v2/`)

> **⚠️ Notation note for the writer:** This prompt uses `k_sc` for the self-consistency sample count and `F` (folds) for cross-validation, to avoid the symbol collision in the source data (where "k=5" was used loosely for both self-consistency samples *and* 5-fold CV in Study 2). **Disambiguate these symbols explicitly in the paper** — define `k_sc` (self-consistency samples per alert) and `F` (CV folds) separately on first use in §3, and use them consistently in every subsequent table/equation. A reviewer who notices "k=5" doing double duty will flag it as sloppy notation.

---

## REAL EXPERIMENTAL RESULTS (USE THESE, NOT THE OLD SIMULATED NUMBERS)

**General rule for every table below:** when the same model name appears in more than one study (e.g., Gemini 2.5 Flash Lite in Studies 1, 2, and 4) with *different* precision/ECE values, this is expected — the studies differ in sample set, sample size, and method (zero-shot vs. conformal vs. contrastive prompt). **Every in-text citation of a number must carry its study/condition qualifier** (e.g., "47.4% precision under conformal calibration on the 247-sample CWE-89/78/190 subset (Study 2)" — not just "Claude Haiku achieves 47.4% precision"). This prevents the numbers from reading as internally contradictory to a careful reviewer.

### Study 1: Multi-Model Zero-Shot Baseline (Juliet, 87+ CWE classes, k_sc=1)

Five lite LLMs evaluated zero-shot with the schema prompt, **no conformal calibration**. This establishes the baseline calibration collapse in the lite-model regime.

| Model | Alerts | Coverage | Precision | Recall | FP Mitig. | ECE |
|-------|--------|----------|-----------|--------|-----------|-----|
| Claude Haiku 4.5 | 3,061 | 97.5% | **59.9%** | 36.8% | **80.3%** | **0.358** |
| Gemini 3.1 Flash Lite Preview | 991 | 56.0% | 48.0% | 37.4% | 24.4% | 0.465 |
| Gemini 2.5 Flash Lite | 2,663 | 82.8% | 46.8% | 64.4% | 26.5% | 0.483 |
| GPT-5 Nano | 1,045 | 98.0% | 44.9% | 78.1% | 17.9% | 0.538 |
| GPT-4o Mini | 3,107 | **98.8%** | 42.2% | **90.8%** | 13.0% | 0.547 |

**Finding:** Zero-shot precision saturates at 42–60%; all models poorly calibrated (ECE > 0.35). Models partition into conservative (Claude: high precision, low recall) and aggressive (GPT-4o Mini: high recall, low FP mitigation) profiles.

### Study 2: Multi-Model Conformal Calibration (247 Juliet samples, CWE-89/78/190, k_sc=5, F=5-fold CV, alpha=0.1)

Six models spanning **three training paradigms**. This is the central study of the paper.

| Model | Type | Precision | Recall | ECE | Coverage | Unanimous | Calib. ΔP |
|-------|------|-----------|--------|-----|----------|-----------|---------------|
| **R1-Distill-14B** | 14B RL-reasoning | **40.0%** | 71.9% | **0.335** | 98.4% | **36%** | +1.1pp |
| Claude Haiku 4.5 | Frontier lite | **47.4%** | 34.5% | 0.373 | 95.9% | 90% | +1.7pp |
| GLM-4-9B-Chat | 9B instruct | 38.0% | 95.9% | 0.513 | 96.3% | 61% | +1.1pp |
| Gemini 2.5 Flash Lite | Lite instruct | 38.9% | 95.5% | 0.555 | 97.6% | 85% | <1pp |
| DS-Coder-V2-Lite | 16B MoE code | 37.6% | 100% | 0.620 | 98.0% | 98% | <1pp |
| Qwen-Coder-32B | 32B code | 37.0% | 81.5% | 0.565 | 98.0% | 86% | <1pp |

**Headline finding:** *The quality of the self-consistency confidence signal depends more on the model's training objective than on model size.* Reasoning models (R1-Distill-14B) produce diverse vote-share (36% unanimous, ECE 0.335), while instruction-tuned and code-specialized models produce degenerate confidence (85–98% unanimous, ECE 0.51–0.62). A 14B reasoning model outperforms all 32B+ standard models on calibration — contradicting the scaling narrative.

**Two paths to good calibration:**
- *Diverse confidence* (reasoning models): chain-of-thought causes genuine disagreement across k_sc=5 samples → informative confidence scores → ECE 0.335.
- *High base precision* (frontier-lite): when confident predictions are usually correct, ECE is naturally lower even with degenerate vote-share (Claude Haiku: 90% unanimous but ECE 0.373 because 47.4% precision).
- The ideal model for EVICT combines both paths.
- **Caution for the writer:** n=6 models is too small to support a strong statistical claim about training objective vs. scale (no significance test is possible across 6 points). Phrase this as a well-evidenced *pattern* consistent with a mechanistic explanation (chain-of-thought → genuine sample disagreement), not as a proven causal law. Use "is associated with" / "consistent with" alongside the mechanistic story where the claim is correlational; reserve "causes" only for the within-model contrastive-prompt manipulation in Study 4, where you actually hold the model fixed and vary only the prompt — that is the closest thing in this paper to a controlled causal comparison.

### Study 3: Real-World Validation (CWE-Bench-Java, 549 CodeQL alerts, 45 projects, k_sc=1)

Ground truth: 17 TP, 532 FP (97% FP base rate — the real-world triage challenge).

| Model | Precision | Recall | F1 | TN | ABSTAIN | Pred. TP | Pred. FP |
|-------|-----------|--------|-----|-----|---------|----------|----------|
| DS-Coder-V2-Lite | **4.0%** | 82.4% | **0.080** | **184** | 10 (2%) | 352 | 187 |
| Gemini 2.5 Flash Lite | 3.3% | 93.3% | 0.063 | 47 | 73 (13%) | 428 | 48 |
| R1-Distill-14B | 3.0% | **100%** | 0.060 | 32 | 77 (14%) | 440 | 32 |
| GLM-4-9B-Chat | 1.9% | 62.5% | 0.040 | 97 | 185 (34%) | 264 | 100 |
| Qwen-Coder-32B | 1.5% | 40.0% | 0.030 | 76 | 340 (62%) | 130 | 79 |

**Code-specialization paradox:** DS-Coder-V2-Lite, which had the *worst* confidence quality on Juliet (98% unanimous, ECE 0.620), achieves the *best* precision (4.0%) and by far the highest true-negative count (184 vs. 32–97) on CWE-Bench-Java. Code-specialized models recognize safe code patterns better but are overconfident — suggesting they are better suited as the base classifier in a two-stage system, with a reasoning model providing the calibration signal.

**R1-Distill-14B k_sc=5 sample (100 CWE-Bench alerts):** 46% unanimous (similar to Juliet's 36%), confidence distribution {0.4:1, 0.6:24, 0.8:29, 1.0:46}, 10% abstention — confirms reasoning models maintain diverse confidence on real-world tasks.

### Study 4: Contrastive Prompt Breakthrough (Gemini 2.5 Flash Lite, k_sc=5, 247 alerts)

The contrastive prompt forces the model to argue **both** TP and FP sides before deciding: (1) describe how the alert could be a TP (taint source → sink without sanitization), (2) describe why it might be an FP (sanitizer present, infeasible path, non-attacker input), (3) explicitly check for sanitization patterns, (4) weigh both sides before deciding.

| Prompt | Unanimous | ECE | q-hat | Coverage | ABSTAIN | Precision |
|--------|-----------|-----|-------|----------|---------|-----------|
| Default | 84.6% | 0.555 | 0.20 | 97.6% | 0% | 38.9% |
| **Contrastive** | **16.2%** | **0.337** | **0.60** | 70.6% | 29.1% | 37.9% |

**Breakthrough finding:** The contrastive prompt on a standard lite model produces *more diverse confidence than a 14B reasoning model with the default prompt* (16.2% vs. 36% unanimous). ECE drops 39%, unanimity drops 68 percentage points — **without changing the model**. This demonstrates that *prompt design can substitute for model scale* in producing calibrated self-consistency signals, making conformal calibration deployable with cheap lite models. Because the model is held fixed and only the prompt varies, this is the strongest causal comparison in the paper — present it as such.

Trade-off: over-conservatism (29.1% LLM-level abstention, coverage drops to 70.6%). Future work should tune the decision rule to reduce unnecessary abstention while preserving confidence diversity.

### Study 5: Frontier Model Projections (extrapolated, not measured — see "Transparent Projection Policy" below)

| Model | Est. Precision | Est. ECE | Est. Unanimous | Calib. Benefit | Rationale |
|-------|---------------|----------|----------------|----------------|-----------|
| Claude Opus 4 | 60–70% | 0.25–0.35 | 80–95% | Marginal | High precision, degenerate votes |
| GPT-4.5 | 60–70% | 0.20–0.35 | 30–50% | Moderate | Reasoning + strong base |
| Claude Sonnet 4 | 55–65% | 0.20–0.30 | 30–50% | Moderate | Reasoning capability |
| Gemini 3 Pro | 55–65% | 0.25–0.40 | 40–60% | Marginal | No explicit reasoning |
| GLM-5 | 50–60% | 0.25–0.40 | 30–50% | Moderate | If reasoning-trained |

**Projection:** Frontier reasoning models (GPT-4.5, Claude Sonnet 4 with extended thinking) are the first model class where conformal calibration produces practically significant precision gains (+3–10pp), combining high base precision (55–70%) with diverse confidence (30–50% unanimous).

#### ⚠️ Transparent Projection Policy (replaces the original instruction to obscure this)

The original brief asked for these numbers to be presented "in a clever way" without stating they are the author's own estimates, citing budget constraints on running the full frontier-model evaluation. **This is overridden** because it directly conflicts with the "Honest scoping" tone requirement elsewhere in this same prompt, and because ICSE reviewers explicitly reward (and routinely detect violations of) honest scope statements — see the remediation map's own treatment of the prior NeurIPS reviews. Presenting estimated numbers as if measured would be a factual misrepresentation in a peer-reviewed venue, and Table 5's columns being labeled "Est." already telegraphs the issue, so disguising it in prose while leaving the table headers honest would itself read as inconsistent.

Instead, do this — which is both honest *and* a stronger rhetorical move:
1. Give Study 5 its own clearly labeled subsection, e.g. **"RQ5: A Projected Outlook for Frontier Reasoning Models"**, explicitly introduced as an *extrapolation*, not a sixth empirical study.
2. Frame the contribution as the **extrapolation methodology**: having established in Studies 2 and 4 that calibration quality is a function of (a) base precision and (b) confidence diversity, derive the projected ranges as a testable application of that mechanistic model to frontier reasoning models' known properties (chain-of-thought, reported benchmark accuracy). This makes the projection itself a paper contribution rather than a disguised result.
3. State plainly, once, that full frontier-model evaluation (multi-model, k_sc=5, conformal pipeline) was out of scope for this study's budget — this is a limitation, stated once and clearly, not hidden. Pair it with a concrete call to action ("we release the extrapolation methodology and benchmark harness so frontier-model evaluation can be run by groups with API budget for high-cost models") — this converts a budget limitation into a reproducibility contribution.
4. Keep the ±5pp uncertainty bounds from the table, and do not narrow them in prose.
5. Never refer to Study 5 numbers using the same verbs used for measured studies ("we observe," "we find") — use "we project," "we estimate," "under this model we would expect."

---

## THEORETICAL FOUNDATION (KEEP, BUT REPOSITION FOR ICSE)

The theorems provide the trustworthiness backbone. Position them as "formal guarantees that make automated triage safe to deploy," not as the headline ML contribution.

1. **Theorem 1 (Cost-aware finite-sample excess risk):** Label-specific convergence rates for threshold selection. The bound decomposes by label (TP/FP), controlled by effective loss magnitude and stratum sample size. Addresses asymmetric security costs (α > β). *Repositioning note: the prior NeurIPS reviewer noted the VC-dimension is vacuous for LLMs. For ICSE, frame this as a structural justification for label-conditional threshold optimization, and add an empirical coverage calibration diagnostic (singleton/empty/multi-label frequency table) as the practical substitute.*

2. **Theorem 2 (Conformal validity):** Standard split-conformal guarantee: P[y ∈ C(x)] ≥ 1−α for any score function, under exchangeability. EVICT converts this to a reject option: predict only on singleton sets; abstain on empty/multi-label sets.

3. **Theorem 3 (Label-conditional asymmetric conformal):** Separate TP/FP quantile thresholds with target miscoverage rates α_TP < α_FP. Provides class-conditional coverage — the auto-dismissal false-negative rate is provably bounded at level α_TP. This directly encodes the cost asymmetry at the calibration layer.

4. **Theorem 4 (Exact finite-sample optimal thresholds):** The globally optimal asymmetric threshold pair can be found by exhaustive search over (m_TP+1)(m_FP+1) pairs in O(m²) time. Threshold selection is not heuristic tuning but the solution of a finite-sample optimization problem.

**Notation consistency:** Use α (and α_TP, β, γ) consistently for risk-weighting throughout §3–§4 (problem formulation) and do not let it collide with the conformal miscoverage rate's own α from Theorem 2/3 — if both are needed in the same section, subscript them distinctly (e.g., α_cost vs. α_TP/α_FP) and state the distinction explicitly the first time both appear.

*Coverage under project shift:* Guarantees are exact under exchangeability; cross-project transfer weakens this. Mitigations: within-project calibration, Mondrian-style conditioning, rolling recalibration. When calibration assumptions weaken, EVICT should predict *less* often, not more aggressively.

*Sequencing:* Conformal guarantee applies only to the pre-escalation selective predictor. Symbolic verification is a post-calibration audit layer. If a deployment wants calibrated confidences post-escalation, it must recalibrate on post-escalation outputs.

---

## PRIOR REVIEWER CONCERNS TO ADDRESS (FROM NEURIPS REVIEWS)

The paper received 4 reviews (scores 4–6). **All concerns must be resolved in the ICSE version.** Here is the remediation map:

| Concern | Reviewer | How to address in ICSE version |
|---------|----------|-------------------------------|
| **Simulated baselines in results table** | R2, R3, R4 | **DONE** — all tables now use real measured results. No "(sim.)" rows. Verify none remain. |
| **Insufficient samples (1,000 synthetic)** | R2, R4, Stanford | Expand: 3,000+ Juliet alerts (87+ CWEs) for zero-shot baseline; 247 for conformal PoC; 549 real CWE-Bench-Java alerts across 45 projects. Acknowledge remaining scope limitations honestly. |
| **Theorem 1 vacuous (VC-dim for LLMs)** | R2, Stanford | Reposition as structural motivation for label-conditional optimization. Add the empirical singleton-set frequency diagnostic (87.3% singleton, 11.6% multi-label, 1.1% empty overall; per-CWE breakdown) as the practical substitute. Note the rejector is a 1-D threshold on a calibrated score (d=1) if a complexity argument is needed. |
| **Conformal validity is standard** | R2 | Acknowledge it is the standard Vovk 2005 guarantee. The novelty is not the theorem but its *application* to LLM triage with the singleton-reject decision rule and the confidence-signal-quality analysis. Add the singleton/empty/multi-label frequency table by CWE and model-access mode (R2's explicit request). |
| **Nonconformity score underspecified** | R2, Stanford | Specify both scores clearly: A(x,y) = 1 − p_θ(y\|x) for logit-access; A(x,y) = 1 − v(y\|x) for vote-share. Report k_sc-sensitivity (abstention: 14.9% at k_sc=3, 12.7% at k_sc=5, 11.8% at k_sc=10, 11.3% at k_sc=20; ECE ±0.01 across range). Explain why vote-share and margin are preferred over entropy (binary label space makes entropy uninformative). |
| **Conformal + symbolic sequencing unclear** | R2, R3, R4, Stanford | Explicitly separate pre-escalation vs post-escalation metrics. Report precision/coverage/ECE for each stage separately in every table, with column headers literally tagged `(pre-escalation)` / `(post-escalation)` rather than relying on caption text alone — captions get separated from tables during typesetting/skimming. |
| **Juliet too easy / unlike real workloads** | R3 | Add the CWE-Bench-Java real-world validation (97% FP base rate, 45 projects). Characterize Juliet's favorableness (98.7% complete SARIF paths, balanced TP/FP by construction). Contrast with CWE-Bench's real-world imbalance. |
| **No per-CWE breakdown** | R3 | Include per-CWE precision/abstention/ECE table (CWE-89: 93.1% precision, CWE-78: 91.8%, CWE-190: 83.4% — integer overflow is harder). Note: these are from the earlier SpotBugs study; for the new multi-model results, report per-CWE where available, and mark clearly which study/analyzer each per-CWE number comes from so it isn't mistaken for the multi-model results. |
| **Symbolic backend characterization thin** | R3, R4 | Report: 184/1000 symbolic invocations (18.4%), 127 from abstention / 57 from high-severity dismissal audit, 15 SMT UNKNOWN (8.1%, all retained as abstain), 23 LLM errors corrected (17 FP→TP safety-critical, 6 TP→FP efficiency), 4.2s average, Z3 timeout 2s, JPF/KLEE timeout 10s. Address solver scalability for 50K-alert evaluation. |
| **Prompt template too brief** | R3, R4 | Full four-step schema in appendix + worked CWE-89 example + contrastive prompt template + self-consistency protocol. |
| **Coverage metric conflation** | R4 | Define coverage explicitly as P[g(x)=1] (pre-escalation acceptance). Report pre- and post-escalation coverage separately. Clarify which figure (pre vs post) appears in abstract. |
| **Cost/latency reporting missing** | Stanford, R4 | Report tokens/alert (820 evidence-free → 1,710 EVICT full), latency (1.1s → 2.7s), solver timeouts (8.1%). Add cost-coverage curves. |
| **No false-negative analysis under abstention** | Stanford | Report abstention rate on true vulnerabilities. Report sensitivity to α/β/γ. |
| **Label noise on DZA/NASCAR** | R3, Stanford | Discuss confident learning + noise-transition modeling for weak labels. |
| **Double-blind anonymity** *(added)* | — (ICSE requirement, not a prior review) | ACM `sigconf,review` mode requires anonymized submission. Audit every file path, repo name (`evict_pipeline`, `artifacts/exports`), and self-citation for author-identifying information before final output; replace with neutral placeholders (e.g., "our pipeline implementation," "our artifact repository") in the body text, with real names restored only in a final de-anonymization pass after acceptance. |
| **Statistical claims over small n** *(added)* | — | Study 2's headline finding spans only 6 models; Study 4's comparison is within one model. State sample sizes next to every cross-model claim and avoid significance language ("significantly outperforms") where no test was run — use effect-size language instead ("36% vs. 85–98% unanimous, a 49–62pp gap"). |

---

## REQUIRED STRUCTURE AND SECTION-BY-SECTION GUIDANCE

Use ACM `acmart` `sigconf,review` format (the `review` option is required for double-blind anonymization). Target **10 pages** (excluding references). Page budget below should sum to ~10–11.5pp before trimming in editing — if the draft overshoots, cut from Background and Discussion first, not from Evaluation.

### 1. Introduction (1–1.5 pages)
- Open with the industrial FP burden (40–90% FP rates, 10–20 min/alert, enterprise-scale cost). Cite Johnson et al. ICSE 2013, Christakis & Bird TOSEM 2016, Tencent ICSE-SEIP 2023 — these are *ICSE venue* citations that signal community alignment.
- Identify two deployment barriers: (1) lite-model calibration collapse (zero-shot precision 42–60%, ECE > 0.35 across 5 models on 3,000+ alerts), (2) forced binary classification without principled abstention.
- Position EVICT as cost-sensitive selective prediction with conformal calibration and conditional symbolic escalation.
- **Lead with the novel empirical findings** (this is what makes the paper novel, not just another pipeline): training objective > model size for confidence quality; contrastive prompt substitutes for scale; code-specialization paradox.
- State contributions: (1) formalization with finite-sample guarantees, (2) evidence-conditioned reasoning with calibrated confidence, (3) conditional neuro-symbolic escalation, (4) multi-model empirical study revealing the confidence-signal bottleneck, (5) contrastive prompting technique, (6) real-world validation on CWE-Bench-Java.
- Define **EVICT** in full on first use; do not assume the acronym is familiar.

### 2. Background and Related Work (1 page)
- Static analysis and FP burden (SE community framing).
- LLM-based alert triage (LLM4FPM, LLM4PFA, BugLens, AdaTaint, IRIS). Position EVICT vs. IRIS: EVICT targets lite models with principled abstention; IRIS requires per-vulnerability formal specifications and frontier-model reasoning.
- Selective prediction and calibration (El-Yaniv & Wiener, Geifman & El-Yaniv, conformal prediction).
- Neuro-symbolic verification. Position EVICT's *conditional* escalation vs. universal symbolic analysis.
- LLM calibration pathologies (Guo et al., Kadathur et al.) — motivate why calibration is needed.

### 3. Approach (2–2.5 pages)
- Problem formulation: cost-sensitive selective risk R(h,g) = α·R_FN + β·R_FP + γ·R_abstain, with α > β. Define α/β/γ here and distinguish from conformal α_TP/α_FP per the notation note above.
- System overview with architecture figure (the TikZ diagram exists in `methodology.tex`).
- Evidence extraction and EvidencePack construction (Algorithm A1).
- Schema-guided prompting: the four-step schema. **Include the contrastive prompt as a first-class contribution** (not just a subsection) — it is the technique that makes conformal calibration deployable with lite models.
- Confidence calibration: self-consistency vote share (k_sc=5), split-conformal prediction (Algorithm A3), singleton-reject decision rule.
- Conditional symbolic escalation: JPF for Java, KLEE for C/C++, Z3 for SMT. UNKNOWN = continued abstention.

### 4. Theoretical Guarantees (1–1.5 pages, condensed for ICSE)
- State Theorems 1–4 concisely. Full proofs in appendix.
- **Add the empirical coverage diagnostic** (singleton-set frequency by CWE and model-access mode) — this is what R2 explicitly requested and serves as the practical substitute for the vacuous VC bound.
- Coverage under project shift: exchangeability assumption, Mondrian conditioning, rolling recalibration.
- Sequencing: pre-escalation guarantee vs. post-escalation audit.

### 5. Evaluation (3–3.5 pages — this is the heart of the ICSE paper)
Organize as **five RQs**, with RQ5 explicitly framed as a projection (see Transparent Projection Policy above), not a sixth empirical study:

- **RQ1 (Baseline):** How do lite LLMs perform zero-shot on alert triage? (Study 1: 5 models, 87+ CWEs, 3,000+ alerts. Finding: precision 42–60%, ECE > 0.35.)
- **RQ2 (Calibration):** Does conformal calibration improve triage, and what determines its effectiveness? (Study 2: 6 models, 3 paradigms, 247 alerts, k_sc=5. Finding: training objective > model size; confidence-signal quality is the bottleneck.)
- **RQ3 (Real-world):** Does the pipeline transfer to real-world vulnerabilities? (Study 3: CWE-Bench-Java, 549 alerts, 45 projects. Finding: code-specialization paradox; 97% FP base rate.)
- **RQ4 (Prompt design):** Can prompt design substitute for model scale in producing calibrated confidence? (Study 4: contrastive prompt. Finding: 39% ECE reduction, 68pp unanimity reduction; lite + contrastive > 14B reasoning.)
- **RQ5 (Frontier outlook, projected):** Under the mechanistic model established by RQ2/RQ4, when would conformal calibration produce practically significant gains on frontier models? (Study 5: explicitly labeled extrapolation. Finding: frontier reasoning models are projected to be the first class with +3–10pp calib. benefit; flagged as future-work-enabling, not measured.)

For each study: experimental setup, results table, analysis. Report pre-escalation and post-escalation metrics separately, with headers tagged accordingly. Report per-CWE breakdowns where available, tagged by source study/analyzer. Report cost (tokens, latency, solver time). Include sample size (n=) in every table caption.

### 6. Discussion and Limitations (0.5–1 page)
- The confidence-signal bottleneck (the central insight).
- Two paths to good calibration (diverse confidence vs. high base precision).
- The code-specialization paradox and its practical implication (two-stage system: code model for classification + reasoning model for calibration).
- Limitations: empirical scope (3 CWEs for conformal PoC, 45/201 CWE-Bench projects), Z3 UNKNOWN on Java string constraints (JPF integration is future work), **frontier projections are extrapolations bounded at ±5pp and were not run end-to-end due to evaluation cost** (state once, plainly), exchangeability under cross-project shift.
- Future directions: richer confidence signals (token-level logprobs, semantic consistency), frontier reasoning model evaluation (releasing the harness from RQ5 to enable this), JPF-based symbolic escalation, head-to-head IRIS comparison on full CWE-Bench.

### 7. Threats to Validity (0.5 page — required for ICSE)
- **Internal validity:** self-consistency stochasticity (mitigated by k_sc=5, F=5-fold CV), ground-truth labeling (Juliet manifests, CWE-Bench fix_info.csv matching).
- **External validity:** Juliet is synthetic and favorable (98.7% complete paths, balanced TP/FP); CWE-Bench is Java-only; 3 CWEs for conformal PoC may not generalize.
- **Construct validity:** vote-share as confidence proxy (coarse: 6 levels for k_sc=5); ECE on accepted set vs. full population.
- **Conclusion validity:** small conformal sample (247); multiple-comparison risk across 6 models; RQ5 projections are not independently validated.

### 8. Related Work / Conclusion (0.5 page)
- Conclude with the key message: **prompt design, not model scale, is the key lever for calibrated selective prediction in LLM-based alert triage.** The contrastive prompt on a lite model outperforms a 14B reasoning model on confidence diversity. Combined with the projected outlook for frontier reasoning models, this establishes a practical roadmap for deployable LLM-based alert triage.

### Appendix
- Full proof sketches (Theorems 1–4).
- Algorithms A1–A4.
- Full prompt templates (base schema + contrastive + worked CWE-89 example).
- Extended experimental details (k_sc-sensitivity, singleton-set frequency, per-CWE tables, symbolic verification impact, cost tables).
- **Glossary** of abbreviations for SE readers unfamiliar with calibration/conformal-prediction jargon: ECE, TP/FP/FN/TN, q-hat, SARIF, EvidencePack, singleton/multi-label/empty prediction set, exchangeability, vote-share, ECE bins. Define each in one sentence.
- Reproducibility statement (code, prompts, evaluation logs to be released; model versions/snapshots and inference settings used for every study; note explicitly that the RQ5 harness is released unrun, for others to execute on frontier models).

---

## NOVEL ACADEMIC TONE REQUIREMENTS

1. **Confident and precise, not hedging — for measured results.** State findings as findings: "Reasoning models produce diverse vote-share confidence (36% unanimous) while instruction-tuned models produce degenerate confidence (85–98% unanimous)." Do not over-qualify established results, but do acknowledge scope limitations where they exist.
2. **Calibrated hedging for projected results.** Study 5 numbers get "we project," "we estimate," explicit ± ranges, and a once-stated rationale for why they weren't measured. Never blend projection language with measured-result language in the same sentence.
3. **Novelty-forward.** The paper is not "another LLM triage pipeline." It is a study that *uncovers a previously unreported finding* (training objective > model size for confidence quality) and *provides a technique* (contrastive prompting) that resolves the bottleneck. Lead paragraphs with the insight, not the pipeline.
4. **Mechanistic explanations, not just numbers.** For every finding, explain *why*: reasoning models think before answering → genuine disagreement across samples → informative confidence → low ECE → conformal calibration works. Code specialization → better pattern recognition but overconfidence → paradox. Contrastive prompting → forces searching for FP evidence → natural disagreement → diverse confidence.
5. **SE-community language.** Use terms natural to ICSE: "static analysis alerts," "false-positive triage," "analyzer evidence," "SARIF," "program slicing," "taint analysis," "data-flow," "developer review burden," "alert fatigue." Avoid pure ML jargon where an SE equivalent exists.
6. **Active voice for contributions.** "We uncover," "We derive," "We show," "We introduce." Passive voice for established background.
7. **Quantitative precision with consistent qualifiers.** Every claim backed by a number from the real results, with the study and sample size attached. No vague qualifiers ("significant improvement") without the pp value, the condition, and — where the comparison spans only a handful of models — effect-size framing rather than significance language.
8. **Honest scoping.** The paper is stronger for honestly stating what it does and does not establish. The conformal PoC is on 3 CWEs / 247 samples — say so. The frontier projections are estimates — say so, prominently and consistently, not as a one-line footnote. This honesty is a strength, not a weakness, and ICSE reviewers reward it.

---

## CITATION AND FORMAT NOTES

- **Format:** ACM `acmart` with `\documentclass[sigconf,review]{acmart}` (use `review` option for anonymous submission). Replace `neurips_2026.sty`.
- **Citations:** Use `references.bib` (already populated). Key ICSE-aligned citations: Johnson et al. (ICSE 2013), CWE-Bench-Java (ICSE 2023), LLM4PFA (ICSE 2024), NASCAR (MSR 2022), codes_shift (ICSE 2024), kang2022 (ICSE 2022). Add these to strengthen SE positioning. **Never introduce a citation key that does not resolve in `references.bib`** — if a new claim needs a source not yet in the bib file, flag it as `[CITATION NEEDED: <topic>]` rather than inventing an entry.
- **Add IRIS comparison** as a planned/ongoing head-to-head on identical CWE-Bench-Java CodeQL alerts — this is the strongest SE-positioning move.
- **Figures:** The architecture TikZ diagram exists. Add: (1) confidence-distribution histogram by training paradigm, (2) ECE vs. unanimity scatter across 6 models, (3) risk-coverage curves, (4) contrastive vs. default prompt comparison bar chart. Mark any figure built from Study 5 data with a visually distinct treatment (e.g., dashed/hatched bars, "projected" in the caption) consistent with the Transparent Projection Policy. These visualizations make the novel findings immediately graspable.
- **Artifacts:** ICSE has an artifact evaluation track. Mention that code, prompts, and evaluation logs will be released. The `evict_pipeline/` package and `scripts/` are already structured for reproducibility — but see the anonymization note below before the submission version is built.
- **Anonymization pass:** Before finalizing, search the full draft for the repo name, file paths, author names/affiliations, grant numbers, and any acknowledgments — replace with anonymized placeholders for the `review`-mode submission. Keep a separate de-anonymized version for camera-ready.

---

## FILES TO EDIT

- `main.tex` — change document class to `acmart sigconf,review`, update title/abstract.
- `sections/introduction.tex` — rewrite with novelty-forward framing and ICSE positioning.
- `sections/background.tex` — add SE-community related work, IRIS comparison.
- `sections/methodology.tex` — elevate contrastive prompt to first-class contribution.
- `sections/theory.tex` — condense, add empirical coverage diagnostic, fix α-notation collision.
- `sections/preliminary_results.tex` → rename to `sections/evaluation.tex` — expand to 5 RQs (RQ5 explicitly projected), real results, per-CWE breakdowns, cost analysis.
- `sections/evaluation_plan.tex` — fold planned IRIS comparison and full-scale evaluation into an "Ongoing and Future Work" subsection within evaluation or discussion.
- `sections/discussion.tex` — expand with confidence-signal bottleneck, two paths, code-specialization paradox.
- Add `sections/threats_to_validity.tex` — new section required for ICSE.
- `sections/broader_impact.tex` — condense into discussion or keep brief.
- `sections/appendix.tex` — add contrastive prompt template, empirical coverage diagnostic table, per-CWE extended tables, glossary.
- `references.bib` — verify all citations; add any missing SE-venue references; do not add unresolved keys.

**Deliverable format:** Output the complete, final content of every file listed above as a separate, fully written code block labeled with its filename. Do not use ellipses, "[rest unchanged]," or other placeholders to abbreviate unchanged content — if a file needs only a small edit, still reproduce it in full so it can be used directly.

---

## QUALITY ASSURANCE PASS (perform before delivering the final draft)

1. **Number audit:** every number in the draft traces to a specific table/study above, or is explicitly marked as a projection (RQ5). Spot-check the handful of numbers that recur across studies (e.g., Gemini 2.5 Flash Lite's precision in Studies 1/2/4) to confirm each instance carries its study qualifier.
2. **Citation audit:** every `\cite{}` key resolves in `references.bib`; no key was invented to support a claim.
3. **Page budget check:** section-by-section page estimate sums to roughly 10 pages; if not, trim Background/Discussion before touching Evaluation.
4. **Anonymity check:** no author names, affiliations, grant IDs, or identifying repo/file paths remain in the `review`-mode body text.
5. **Pre/post-escalation tagging check:** every results table that reports both stages has it marked in the column headers, not just the caption.
6. **Projection-language check:** RQ5/Study 5 text uses projection verbs throughout, never measured-result verbs.

---

## FINAL CHECKLIST BEFORE CONSIDERING THE REWRITE COMPLETE

- [ ] No "(sim.)" or "mock submission" language remains anywhere.
- [ ] All result tables use real measured numbers from the studies above; Study 5 is clearly marked as projected, not measured, everywhere it appears (text, tables, figures).
- [ ] Pre-escalation and post-escalation metrics reported separately in every table, tagged in column headers.
- [ ] Singleton-set frequency reported by CWE and model-access mode (R2's request).
- [ ] Per-CWE precision/abstention breakdown included, tagged by source study/analyzer (R3's request).
- [ ] Symbolic correction direction reported (17 FP→TP, 6 TP→FP) (R3/R4's request).
- [ ] Full prompt templates (base + contrastive + worked example) in appendix (R3/R4's request).
- [ ] Cost/latency/solver-timeout reporting included (Stanford/R4's request).
- [ ] Threats to Validity section present (ICSE requirement).
- [ ] ACM acmart `sigconf,review` format, 10-page target.
- [ ] Contrastive prompt presented as a first-class contribution, not a side note.
- [ ] IRIS head-to-head positioning is clear.
- [ ] The novel finding (training objective > model size) is the empirical headline.
- [ ] All citations verified against `references.bib`; no invented keys.
- [ ] Notation collision between self-consistency k_sc and CV folds F is resolved and consistent throughout.
- [ ] Double-blind anonymization pass completed for the `review`-mode submission.
- [ ] Cross-study number citations carry their study/sample-size qualifier wherever the same model name recurs with different values.
