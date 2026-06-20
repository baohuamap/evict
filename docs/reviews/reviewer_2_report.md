# Reviewer 2 Report: Experiments & Practical Impact Specialist

## Summary

This proposal presents EVICT (Evidence-conditioned Verifier for Investigating Code Triage), a system designed to reduce false positives in static analysis using LLMs with calibrated uncertainty and conditional symbolic verification. The approach constructs structured evidence bundles (alert metadata, code slices, flows, constraints), applies LLM-based verification with schema-guided prompting, uses calibrated uncertainty to enable abstention, trains contrastive representations for false-positive patterns, and conditionally invokes SMT/symbolic execution. The evaluation plan includes NASCAR (1M Java warnings), DZA (differential labels), Juliet/SARD (synthetic), and CWE-Bench-Java (120 validated vulnerabilities), with emphasis on leakage-resistant protocols and cross-project generalization.

## Soundness: 2.5/5

From an experimental and practical perspective, the proposal has several soundness concerns:

**Experimental Design Issues:**

1. **Dataset Selection and Quality:**
   - The proposal acknowledges label quality issues across all datasets but doesn't provide concrete solutions. Juliet has documented label errors (864 FPs per FuzzSlice), DZA uses "very likely" labels, and NASCAR conflates "actionable" with "true bug."
   - No strategy for validating or correcting labels beyond "acknowledging" the problem
   - The proposal mentions using commit-differential labeling (DZA-style) as "scalable but noisy" weak supervision, but doesn't describe how to handle this noise systematically
   - Different datasets use different labeling schemes (actionable vs. true-positive vs. fixed), making it difficult to train a unified model

2. **Baseline Comparisons:**
   - The proposal lists strong baselines (BugLens, LLM4FPM, LLM4PFA) but doesn't specify how to implement them fairly for comparison
   - Many baselines are recent preprints without public implementations, making reproduction difficult
   - No discussion of how to control for confounding factors (different LLM versions, prompt engineering, context extraction strategies)
   - The "heuristic filters" baseline is vague—what specific heuristics?

3. **Evaluation Metrics:**
   - The proposal lists many metrics (precision, recall, F1, FPR, AUC, ECE, Brier, NDCG@k, risk-coverage) but doesn't specify which are primary
   - No discussion of how to handle class imbalance (if FP rate is very high, precision@k may be more meaningful than overall precision)
   - Calibration metrics (ECE, Brier) require careful bin selection and may not be comparable across different model families
   - "Minutes saved per 1k alerts" is mentioned but not operationalized—how will this be measured?

4. **Cross-Project Evaluation:**
   - The proposal emphasizes cross-project generalization but doesn't specify the train/test split strategy
   - Project-level holdout is mentioned, but with only 120 samples in CWE-Bench-Java, statistical power will be very limited
   - No discussion of how to handle severe distribution shift (different codebases, analyzers, CWE types)

5. **Ablation Studies:**
   - The ablation plan is reasonable but incomplete:
     - No ablation of the selective prediction component itself (calibrated abstention vs. simple confidence threshold)
     - No ablation of the contrastive learning component (is it better than supervised classification?)
     - No ablation of SARIF standardization (does it actually help or just add complexity?)
   - The symbolic hook ablation (no hooks vs. SMT-only vs. symex-only vs. conditional) is good, but needs cost-benefit analysis

**Practical Feasibility Concerns:**

6. **Scalability:**
   - NASCAR has 1M warnings. Even at 1 second per warning (optimistic), that's 278 hours of inference time
   - LLM API costs could be substantial (Tencent study reports "fractions of a dollar" per alarm, but 1M warnings × $0.10 = $100K)
   - Training contrastive models on million-scale datasets requires significant compute
   - No discussion of how to batch or cache results for efficiency

7. **Reproducibility:**
   - LLMs are non-deterministic, especially via API. How will results be stabilized?
   - Different LLM versions (GPT-4 vs. GPT-4-turbo vs. GPT-4o) may give different results
   - Temperature scaling requires a held-out calibration set—how is this split from training/test to avoid leakage?
   - The proposal mentions "deterministic seeds where possible" but API-only models don't support this

8. **Implementation Complexity:**
   - Integrating multiple components (LLM inference, SMT solvers, symbolic execution, SARIF parsing, multiple analyzers) is highly complex
   - The 6-month timeline includes 4 weeks for "EvidencePack construction + baseline prompts" but this may be underestimated given the need to support multiple analyzers and convert to SARIF
   - No discussion of software engineering practices (testing, version control, containerization) to ensure reproducibility

**Missing Experimental Details:**

9. **LLM Selection:**
   - The proposal says "model family is unspecified" but this is a critical design choice
   - GPT-4 vs. Claude vs. Llama 3 vs. CodeLlama vs. specialized code models—which will be used?
   - Will multiple models be compared? If so, how?
   - For fine-tuning (LoRA), what base model, what rank, what learning rate?

10. **Prompt Engineering:**
    - The proposal mentions "schema-constrained verifier prompt" but doesn't provide examples
    - Prompt engineering can dramatically affect results—how will prompts be designed and validated?
    - Will prompts be tuned on a development set? If so, how to avoid overfitting?
    - How many few-shot examples? How are they selected?

11. **Symbolic Verification Details:**
    - What SMT solver (Z3, CVC5, Yices)? What timeout?
    - What symbolic execution engine (KLEE, Angr, Manticore)? What depth/path limits?
    - How are constraints extracted from code? This is non-trivial and error-prone
    - What happens when symbolic checks timeout or fail?

12. **Statistical Testing:**
    - The proposal mentions "paired bootstrap CIs over projects" and "McNemar tests" but doesn't specify significance levels, multiple testing correction, or power analysis
    - With only a few projects in CWE-Bench-Java, statistical power may be insufficient
    - Clustering within projects/files is mentioned but not formalized

## Presentation: 3.5/5

**Strengths:**
- Well-organized with clear section structure
- Comprehensive literature review with concrete references
- Good use of tables (dataset comparison, resource estimates)
- Gantt chart provides clear timeline
- Acknowledges limitations and challenges explicitly

**Weaknesses:**
- **Excessive length:** This reads like a grant proposal or position paper, not a research paper. For NeurIPS (9 pages + references), substantial condensation would be needed
- **Inconsistent detail level:** Dataset descriptions are very detailed, but experimental protocols are vague
- **Missing figures:** No architectural diagrams, no example EvidencePacks, no result visualizations
- **No preliminary results:** The proposal would be much stronger with even small-scale pilot experiments
- **Vague terminology:** "Lightweight," "targeted," "minimal," "progressive" are used without precise definitions
- **Citation format:** Many informal URLs rather than proper citations; several unpublished preprints

**Clarity Issues:**
- The relationship between the three formulations (classification, ranking, selective prediction) is unclear
- How contrastive learning integrates with the main pipeline is not explained
- The conditional invocation logic for symbolic checks needs a flowchart or algorithm
- Cost-benefit tradeoffs are mentioned repeatedly but never quantified

## Contribution: 3/5

**From an Experimental/Practical Perspective:**

**Contribution 1: Risk-Controlled Adjudication (Moderate-High Value)**
- Calibrated abstention is practically valuable—allows safe automation with human oversight
- However, the contribution depends on whether calibration actually works in practice
- No preliminary experiments demonstrating that LLM confidence scores are well-calibrated for alert triage
- Industrial adoption would benefit, but scientific contribution is limited without rigorous evaluation

**Contribution 2: False-Positive Signature Learning (Moderate Value)**
- Contrastive learning is a reasonable approach, but unclear if it's better than simpler alternatives
- The assumption that FP patterns transfer across projects is untested
- Would need strong empirical evidence (cross-project transfer experiments) to validate this contribution

**Contribution 3: Conditional Symbolic Verification (Moderate Value)**
- Practically useful to control costs, but the decision logic is underspecified
- Would need cost-benefit analysis showing when symbolic checks are worth the overhead
- Runtime and cost metrics are essential but not included in the evaluation plan

**Contribution 4: Standardized Evaluation (High Practical Value, Low Scientific Value)**
- SARIF-based standardization would improve reproducibility and cross-tool comparison
- Multiple complementary datasets (synthetic, differential, manually validated) provide good coverage
- Leakage-resistant protocols address known issues
- However, this is primarily an engineering contribution, not a scientific advance

**Overall Assessment:**
The practical value is clear—if EVICT works as described, it could significantly reduce developer triage burden. However, the scientific contribution is limited without:
1. Preliminary experiments demonstrating feasibility
2. Strong empirical evidence of superiority over recent baselines
3. Rigorous cost-benefit analysis
4. Careful ablation studies showing each component's value

## Strengths

1. **Addresses Critical Practical Problem:** Static analysis false positives waste significant developer time (10-20 minutes per alarm per Tencent study). This is a high-impact problem.

2. **Comprehensive Dataset Strategy:** Combining NASCAR (large scale), DZA (realistic), Juliet (controlled), and CWE-Bench-Java (high-stakes) provides complementary evaluation signals.

3. **Strong Awareness of Evaluation Issues:** The proposal explicitly addresses label quality, data leakage, cross-project generalization, and calibration—issues often ignored in this area.

4. **Rigorous Baseline Comparison Plan:** Including static analyzer alone, heuristic filters, classic ML, recent LLM systems, and neuro-symbolic approaches provides comprehensive comparison.

5. **Cost-Benefit Focus:** Emphasis on minutes saved, dollar costs, and ROI metrics shows practical grounding beyond just accuracy metrics.

6. **Leakage-Resistant Protocols:** Project-level splits, time-based splits, and deduplication address known data leakage problems highlighted in prior work (ICSE'22).

7. **Realistic Timeline:** The 6-month Gantt chart with staged experiments (foundations → ML core → verification → generalization) shows careful planning.

8. **Reproducibility Emphasis:** SARIF standardization, public datasets, prompt templates, and evaluation scripts would improve reproducibility.

## Weaknesses

1. **No Preliminary Results:** The proposal would be much stronger with pilot experiments demonstrating feasibility. Even small-scale results on Juliet would increase confidence.

2. **Label Quality Not Addressed Systematically:** All datasets have label issues, but the proposal only acknowledges this without proposing solutions (e.g., active learning, human validation, noise-robust learning).

3. **Unclear Advantage Over Strong Baselines:** Recent work achieves 94-99% precision. The proposal doesn't specify what performance level would constitute success or how much improvement is needed to justify added complexity.

4. **Missing Cost-Benefit Analysis:** Conditional symbolic invocation requires knowing when overhead is justified, but no cost model is provided. Similarly, abstention rates need to be balanced against manual triage costs.

5. **Insufficient Experimental Detail:**
   - Which LLM(s) will be used?
   - What are the exact prompts?
   - What SMT solver and symbolic execution engine?
   - How are constraints extracted?
   - What are the hyperparameters?

6. **Scalability Concerns Not Addressed:** 1M warnings × seconds per warning = days of compute. API costs could be substantial. No discussion of batching, caching, or optimization strategies.

7. **Reproducibility Challenges:** LLM non-determinism, API version changes, and lack of logit access make reproducibility difficult. The proposal acknowledges this but doesn't propose solutions beyond "log prompts/responses."

8. **Statistical Power Issues:** CWE-Bench-Java has only 120 samples. Cross-project evaluation with so few samples will have limited statistical power. No power analysis is provided.

9. **Incomplete Ablation Plan:** Missing ablations for selective prediction (calibrated vs. threshold), contrastive learning (vs. supervised), and SARIF standardization (vs. direct analyzer output).

10. **Overly Ambitious Scope:** Combining evidence extraction, LLM reasoning, calibration, contrastive learning, symbolic verification, and multi-analyzer support in 6 months may be unrealistic.

11. **Missing Failure Analysis:** No discussion of when EVICT is expected to fail, what bug types are hardest, or how abstention rates vary across categories.

12. **Generalization Concerns:** Focus on Java (NASCAR, CWE-Bench-Java) raises questions about generalization to C/C++, Python, etc. Cross-language evaluation is not included.

## Suggestions

1. **Conduct Preliminary Experiments:**
   - Start with Juliet (controlled, manageable scale) to validate the approach
   - Show that evidence-conditioned prompting outperforms simple prompting
   - Demonstrate that calibration improves reliability
   - Provide proof-of-concept results before full-scale evaluation

2. **Address Label Quality Systematically:**
   - Use FuzzSlice-style validation to audit and correct benchmark labels
   - Implement noise-robust learning for DZA's weak supervision
   - Consider active learning to obtain high-quality labels for a validation set
   - Report inter-annotator agreement for manually labeled samples

3. **Develop Cost-Benefit Analysis:**
   - Create a formal cost model: LLM inference cost, symbolic verification overhead, developer triage time
   - Measure actual runtime and costs for each component
   - Analyze when symbolic checks are cost-effective
   - Report total end-to-end cost per alert and cost savings vs. manual triage

4. **Provide Detailed Experimental Protocols:**
   - Specify exact LLM(s), prompts (include examples in appendix), hyperparameters
   - Describe SMT solver, symbolic execution engine, timeout settings
   - Explain constraint extraction procedure with examples
   - Document all design choices and provide justification

5. **Strengthen Baseline Comparisons:**
   - Implement recent strong baselines (LLM4FPM, LLM4PFA) using the same LLM and context extraction for fair comparison
   - Control for confounding factors (prompt engineering, LLM version)
   - Report variance across multiple runs to account for non-determinism
   - Include human performance as an upper bound

6. **Expand Ablation Studies:**
   - Ablate selective prediction: calibrated abstention vs. simple confidence threshold vs. no abstention
   - Ablate contrastive learning: contrastive vs. supervised classification vs. no fine-tuning
   - Ablate symbolic verification: measure cost vs. error reduction tradeoff
   - Ablate SARIF: does standardization actually help or just add complexity?

7. **Address Scalability:**
   - Implement batching and caching strategies
   - Report runtime and memory usage for each component
   - Analyze computational complexity
   - Provide scalability experiments (e.g., how does runtime scale with warning volume?)

8. **Improve Reproducibility:**
   - Use deterministic sampling where possible
   - Report exact LLM versions and API settings
   - Provide Docker containers with all dependencies
   - Release code, data splits, and prompts publicly
   - Use version control for all experimental artifacts

9. **Conduct Power Analysis:**
   - Calculate statistical power for cross-project evaluation given sample sizes
   - If power is insufficient, consider increasing CWE-Bench-Java or using more projects
   - Report confidence intervals and effect sizes, not just p-values

10. **Include Failure Analysis:**
    - Characterize when EVICT fails (which bug types, code patterns, projects)
    - Analyze abstention patterns (when does the system abstain? Is it calibrated?)
    - Identify limitations and discuss when manual triage is still necessary

11. **Simplify Scope:**
    - Consider focusing on a subset of components (e.g., evidence-conditioned verification + calibration) and leaving others for future work
    - Start with Java only and expand to other languages later
    - Reduce the number of datasets to ensure thorough evaluation of each

12. **Add Cross-Language Evaluation:**
    - Include C/C++ datasets (e.g., Linux kernel warnings) to test generalization
    - Analyze language-specific challenges
    - Report performance separately for each language

## Questions

1. **Preliminary Results:** Do you have any pilot experiments demonstrating that evidence-conditioned prompting works? Even small-scale results would strengthen the proposal.

2. **Baseline Performance:** What precision/recall do strong recent baselines (LLM4FPM, LLM4PFA) achieve on your proposed datasets? How much improvement would demonstrate EVICT's value?

3. **Label Validation:** How will you validate dataset labels? Will you use fuzzing (FuzzSlice-style), manual auditing, or other methods?

4. **LLM Selection:** Which specific LLM(s) will you use? GPT-4? Claude? Open-source models? Will you compare multiple models?

5. **Prompt Design:** Can you provide example prompts for the schema-guided claim checking? How will prompts be designed and validated?

6. **Calibration Validation:** How will you ensure that calibration methods (temperature scaling, conformal prediction) provide valid guarantees? What calibration set will you use?

7. **Cost Analysis:** What are the expected costs per alert for LLM inference, symbolic verification, and manual triage? When is automation cost-effective?

8. **Scalability:** How long will it take to process 1M NASCAR warnings? What are the computational requirements? Can the approach scale to real-world deployment?

9. **Abstention Rate:** What abstention rate do you expect? If 50% of alerts are abstained, is that acceptable? How do you balance automation vs. manual workload?

10. **Symbolic Verification:** How are constraints extracted from code? What happens when extraction fails or symbolic checks timeout?

11. **Contrastive Learning:** Do you have evidence that FP patterns transfer across projects? Have you analyzed FP signature consistency?

12. **Statistical Power:** With only 120 samples in CWE-Bench-Java, how will you ensure sufficient statistical power for cross-project evaluation?

13. **Failure Modes:** What types of alerts or bugs does EVICT struggle with? When does it abstain? How does performance vary across CWE types?

14. **Generalization:** The focus is on Java. How well do you expect the approach to generalize to C/C++, Python, JavaScript, etc.?

15. **Industrial Deployment:** What would be required to deploy EVICT in a real industrial setting? What are the integration challenges?

## Rating: 5/10 (Borderline Reject)

**Justification:**

This proposal addresses an important practical problem with a reasonable approach and comprehensive evaluation plan. The emphasis on calibrated abstention, rigorous evaluation protocols, and cost-benefit analysis is commendable. However, several significant weaknesses prevent me from recommending acceptance:

1. **No preliminary results:** The proposal would be much stronger with even small-scale pilot experiments demonstrating feasibility and showing promise compared to baselines.

2. **Unclear advantage over strong recent baselines:** Recent work achieves 94-99% precision. Without preliminary results or clear analysis of why EVICT will outperform, it's hard to assess the potential impact.

3. **Label quality issues not addressed:** All datasets have known label problems, but the proposal only acknowledges this without proposing systematic solutions.

4. **Missing experimental details:** Critical details (LLM selection, prompts, symbolic verification tools, cost model) are not provided, making it difficult to assess feasibility.

5. **Scalability and cost concerns:** Processing 1M warnings with LLM + symbolic verification could be prohibitively expensive and slow, but no analysis is provided.

The proposal is well-motivated and thoughtfully designed, but it reads more like a research plan than a completed or near-completed work. For NeurIPS, I would expect to see at least preliminary results demonstrating proof-of-concept and showing promise relative to baselines.

**Recommendation:** Conduct pilot experiments on Juliet demonstrating that the approach works, then resubmit with empirical evidence of feasibility and initial results. Alternatively, consider submitting to a venue that accepts research proposals or work-in-progress (e.g., workshop papers, or software engineering venues that value systems contributions).

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have expertise in experimental design, empirical software engineering, and evaluation of ML systems for code analysis. I am familiar with the datasets and baselines mentioned. My main uncertainty is whether the authors have preliminary results or implementation details not included in this proposal that would substantially change the assessment. Based on the submitted material, my rating stands.
