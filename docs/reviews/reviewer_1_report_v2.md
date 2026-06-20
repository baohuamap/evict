# Reviewer 1 Report (Fresh Review - Round 2): Calibration & Statistical Learning Theory Specialist

## Summary

This revised EVICT proposal presents a comprehensive improvement roadmap addressing previous peer review concerns. The authors propose a system for static analysis alert triage using evidence-conditioned LLMs with calibrated selective prediction and conditional symbolic verification. The revision includes: (1) a detailed theoretical framework for selective prediction with PAC-style bounds, (2) concrete preliminary experiment plans on Juliet, (3) precise algorithmic specifications, (4) enhanced evaluation protocols, and (5) restructured presentation. This is a **substantial improvement** over the original submission, demonstrating the authors' responsiveness to feedback and commitment to scientific rigor.

## Soundness: 4/5

The revised proposal significantly strengthens the technical soundness:

**Theoretical Foundations (Major Improvement):**

The addition of formal selective prediction theory is the most significant enhancement:

- **PAC-style framework:** The proposal now includes formal definitions of risk, coverage, and optimality for the predictor-rejector framework. The formulation R(h,g) = α·R_FN + β·R_FP + γ·R_abstain with explicit cost parameters is rigorous and appropriate.

- **Theoretical guarantees:** The promise to prove coverage bounds (P(g(x)=1) ≥ 1-δ) and risk bounds (R(h,g) ≤ ε with high probability) addresses Reviewer 1's critical concern. The reference to El-Yaniv & Wiener (2010) and Geifman & El-Yaniv (2017) shows awareness of foundational work.

- **Conformal prediction integration:** The proposal to use conformal prediction for distribution-free guarantees is well-motivated. The split-conformal approach with calibration set is standard and appropriate. However, the proposal should clarify how to construct prediction sets for classification tasks where LLMs output text rather than probability distributions.

- **Cost-sensitive learning:** The extension to asymmetric costs (false negatives in security contexts are more expensive than false positives) is practically important and theoretically sound.

**Remaining Theoretical Gaps:**

1. **Disagreement coefficient:** The proposal mentions proving fast rejection rates under disagreement coefficient bounds but doesn't define the disagreement coefficient for the alert triage setting. This needs clarification.

2. **Distribution shift:** While the proposal acknowledges distribution shift (cross-project, cross-tool), the theoretical guarantees assume i.i.d. data. How do the bounds degrade under distribution shift? This is critical for real-world applicability.

3. **Calibration validity:** The proposal states that conformal prediction provides "distribution-free" guarantees, but this requires the exchangeability assumption. With project-level clustering and distribution shift, is this assumption valid? The proposal should discuss this explicitly.

4. **Optimal threshold selection:** The proposal mentions deriving optimal rejection thresholds but doesn't specify the optimization objective or algorithm. Is it minimizing expected cost? Maximizing utility? This needs formalization.

**Algorithmic Detail (Significant Improvement):**

The proposal now includes:

- **Algorithm 1 (EvidencePack Construction):** Clear pseudocode with specific steps (statement-level slicing, flow extraction, constraint extraction). Good.

- **Algorithm 2 (Calibrated Selective Triage):** Structured workflow with LLM verification, confidence estimation, and conditional symbolic invocation. The decision logic is now explicit.

- **Algorithm 3 (Contrastive FP Learning):** InfoNCE loss with hard-negative mining strategy. Standard and appropriate.

However, some details remain vague:

- **Constraint extraction (Line 8 of Algorithm 1):** "Extract branch conditions" - how exactly? Via symbolic execution? Static analysis? What if extraction fails?

- **Confidence estimation (Line 5 of Algorithm 2):** "Estimate confidence" - using what method? Logit-based? Ensemble-based? The proposal mentions multiple methods but doesn't specify which to use when.

- **Conditional invocation (Line 7 of Algorithm 2):** "If uncertain" - what's the threshold? How is it set? The proposal should specify the decision rule.

**Preliminary Experiments (Addresses Critical Gap):**

The proposal now includes a concrete plan for preliminary experiments:

- **Phase 1 (Weeks 1-4):** Juliet subset (1000 samples), evidence-conditioned prompting vs. baseline, preliminary calibration analysis. This is feasible and appropriate.

- **Phase 2 (Weeks 5-8):** Expand to 5000 samples, implement contrastive learning, compare to LLM4FPM. Good choice of baseline.

- **Expected outcomes:** Precision 85-95%, calibration ECE <0.1, abstention rate 10-20%. These are reasonable expectations given recent work.

This addresses the most critical weakness from the first review. However, the proposal is still a **roadmap** rather than completed work. For NeurIPS, I would strongly prefer to see actual preliminary results, not just a plan.

**Experimental Design (Enhanced):**

- **Leakage-resistant protocols:** Function-level deduplication, project-based splits, time-based splits. Excellent attention to ICSE'22 concerns.

- **Baseline implementations:** Clear specification of how to implement LLM4FPM, LLM4PFA for fair comparison. Good.

- **Statistical testing:** Paired bootstrap, McNemar tests, Bonferroni correction. Appropriate.

- **Ablation studies:** Comprehensive ablations for evidence components, calibration methods, symbolic hooks, contrastive learning. This will provide strong evidence for each component's contribution.

**Concerns:**

1. **Still no actual results:** The proposal is an improvement roadmap, not a completed study. For NeurIPS, preliminary results (even on 100 samples) would be much more convincing than a detailed plan.

2. **Conformal prediction applicability:** For API-only LLMs that output text, constructing prediction sets is non-trivial. The proposal should provide more detail on how to apply conformal prediction in this setting.

3. **Symbolic verification scalability:** The proposal claims "lightweight" and "targeted" symbolic execution but doesn't provide complexity analysis or timeout strategies. What if symbolic checks don't terminate?

4. **Cross-project generalization:** The theoretical bounds assume i.i.d. data, but cross-project evaluation involves distribution shift. How do the guarantees transfer?

## Presentation: 4.5/5

The presentation is vastly improved:

**Strengths:**

1. **Clear structure:** Part 1 (improvements), Part 2 (theoretical foundations), Part 3 (methodology), Part 4 (evaluation), Part 5 (roadmap). Logical and easy to follow.

2. **Visual elements added:** The proposal now includes:
   - System architecture diagram (Figure 1) - shows component interactions clearly
   - Risk-coverage curves (Figure 2) - illustrates selective prediction tradeoffs
   - Calibration plots (Figure 3) - demonstrates expected calibration quality
   - Example EvidencePack (Figure 4) - concrete illustration of data structure

3. **Precise terminology:** Terms like "lightweight" and "targeted" are now defined:
   - "Lightweight SMT": Z3 with 10-second timeout, memory limit 2GB
   - "Targeted symbolic execution": KLEE with path depth ≤50, maximum 100 paths
   
4. **Formal notation:** Consistent use of mathematical notation throughout (h for predictor, g for rejector, R for risk).

5. **Clear problem formulation:** The three formulations (classification, ranking, selective prediction) are now explained, with selective prediction identified as the primary objective.

6. **Condensed length:** The proposal is now structured for 9-page NeurIPS format with supplementary material clearly delineated.

**Minor Weaknesses:**

1. **Example prompts:** While the schema is described, actual example prompts would be helpful (could be in supplementary material).

2. **Result tables:** The proposal includes expected result patterns but not actual results. Placeholder tables could show what the final paper would include.

3. **Complexity analysis:** While algorithms are provided, computational complexity (time and space) is not formally analyzed.

## Contribution: 4/5

The contribution assessment is significantly strengthened:

**Contribution 1: Theoretical Framework for Selective Prediction in Alert Triage (High Novelty)**

This is now the clear primary contribution:

- **Formalization:** First work to formalize alert triage as selective prediction with PAC-style bounds
- **Cost-sensitive extension:** Explicit modeling of asymmetric costs (FN > FP in security contexts)
- **Practical algorithms:** Concrete algorithms for optimal threshold selection and risk-controlled abstention
- **Novel application:** While selective prediction theory exists, application to code analysis with distribution shift is new

**Assessment:** This is a strong contribution for NeurIPS. The theoretical development is rigorous and the application is novel.

**Contribution 2: Contrastive Learning for FP Signatures (Moderate Novelty)**

The proposal now provides:

- **Formal objective:** InfoNCE loss with hard-negative mining
- **Cross-project transfer:** Explicit evaluation of transfer learning across projects
- **Ablation:** Comparison to supervised baselines

**Assessment:** The contribution is clearer but still incremental. Contrastive learning is standard; the novelty is in the application and the demonstration of cross-project transfer.

**Contribution 3: Conditional Neuro-Symbolic Verification (Moderate Novelty)**

The proposal now specifies:

- **Decision rule:** Invoke symbolic checks when uncertainty > threshold
- **Cost-benefit analysis:** Formal model of verification cost vs. error reduction
- **Certificates:** Auditable SAT/UNSAT results

**Assessment:** The conditional invocation strategy is useful but not groundbreaking. The value is in the integration with selective prediction.

**Contribution 4: Rigorous Evaluation Protocols (Moderate-High Practical Value)**

- **Leakage-resistant protocols:** Address ICSE'22 concerns about data leakage
- **Multiple datasets:** Complementary evaluation signals from synthetic, differential, and manually validated data
- **SARIF standardization:** Enables cross-tool comparison

**Assessment:** High practical value for the community but limited scientific novelty.

**Overall Contribution:**

The proposal now has one strong theoretical contribution (selective prediction framework) and several moderate contributions (contrastive learning, conditional symbolic verification, evaluation protocols). This is appropriate for NeurIPS, especially if preliminary results demonstrate practical value.

**Comparison to Prior Work:**

The proposal now clearly distinguishes EVICT from recent systems:

- **vs. LLM4FPM:** EVICT adds calibrated abstention and theoretical guarantees
- **vs. LLM4PFA:** EVICT adds formal selective prediction framework and cost-sensitive learning
- **vs. BugLens:** EVICT adds quantitative risk control and cross-project transfer learning
- **vs. AdaTaint:** EVICT adds selective prediction and systematic evaluation protocols

This is much clearer than the original proposal.

## Strengths

1. **Addresses All Critical Concerns:** The revision directly addresses every major weakness identified in the first review (preliminary experiments, theoretical foundations, algorithmic detail, presentation).

2. **Strong Theoretical Development:** The PAC-style framework for selective prediction with cost-sensitive learning is rigorous and novel in this application domain.

3. **Concrete Preliminary Experiment Plan:** The phased approach (Juliet subset → full Juliet → cross-project) is feasible and will provide strong evidence.

4. **Precise Algorithmic Specifications:** Algorithms 1-3 provide clear pseudocode that could be implemented directly.

5. **Comprehensive Evaluation Design:** Leakage-resistant protocols, multiple baselines, extensive ablations, and statistical rigor.

6. **Excellent Presentation:** Clear structure, visual elements, formal notation, and precise terminology.

7. **Honest About Limitations:** The proposal explicitly discusses when EVICT is expected to fail (concurrency bugs, algorithmic issues, severe distribution shift).

8. **Reproducibility Focus:** Detailed experimental protocols, public datasets, code release plan, and ML reproducibility checklist.

9. **Practical Grounding:** Cost-benefit analysis, industrial deployment considerations, and concrete ROI metrics.

10. **Responsive to Feedback:** The authors clearly took the previous reviews seriously and made substantial improvements.

## Weaknesses

1. **Still a Roadmap, Not Completed Work:** The proposal is a detailed plan for experiments, not actual results. For NeurIPS, completed preliminary experiments would be much stronger.

2. **Conformal Prediction Details:** The application of conformal prediction to text-outputting LLMs needs more detail. How are prediction sets constructed? How is the conformity score computed?

3. **Distribution Shift Theory:** The theoretical guarantees assume i.i.d. data, but cross-project evaluation involves distribution shift. The proposal should discuss how bounds degrade under shift.

4. **Symbolic Verification Scalability:** While "lightweight" and "targeted" are now defined, there's no complexity analysis or guarantee that checks terminate in reasonable time.

5. **Disagreement Coefficient:** Mentioned but not defined for the alert triage setting. This is important for proving fast rejection rates.

6. **Optimal Threshold Selection:** The optimization objective and algorithm are not fully specified. Is it expected cost minimization? Constrained optimization?

7. **Contrastive Learning Justification:** While the method is now clear, the justification for why contrastive learning should help is still somewhat weak. Are FP patterns really consistent across projects?

8. **Label Noise Handling:** The proposal acknowledges label quality issues but doesn't provide concrete noise-robust learning methods beyond "treat DZA as weak supervision."

9. **Generalization Beyond Java:** The focus is on Java (NASCAR, CWE-Bench-Java). Cross-language generalization is mentioned but not evaluated.

10. **Timeline Optimism:** The 6-month timeline is ambitious. Completing preliminary experiments, full evaluation, ablations, and paper writing in 6 months is challenging.

## Suggestions

1. **Conduct Minimal Preliminary Experiments Before Submission:**
   - Even 100 Juliet samples with evidence-conditioned prompting vs. baseline would strengthen the proposal enormously
   - Show that the approach is feasible and promising
   - Include actual numbers (precision, calibration, abstention rate) rather than just expected ranges

2. **Clarify Conformal Prediction for Text-Outputting LLMs:**
   - Provide explicit algorithm for constructing prediction sets
   - Define the conformity score (e.g., based on self-consistency, ensemble disagreement)
   - Discuss how to convert prediction sets to binary accept/reject decisions

3. **Extend Theory to Distribution Shift:**
   - Discuss how theoretical bounds degrade under covariate shift
   - Consider domain adaptation theory or transfer learning bounds
   - Provide conditions under which guarantees transfer across projects

4. **Add Complexity Analysis:**
   - Formal time and space complexity for each algorithm
   - Analysis of symbolic verification overhead (expected case, worst case)
   - Discussion of scalability to millions of warnings

5. **Define Disagreement Coefficient:**
   - Provide formal definition for alert triage setting
   - Discuss whether fast rejection rates (O(1/m)) are achievable
   - Connect to practical convergence rates

6. **Specify Optimal Threshold Selection:**
   - Formalize the optimization objective (expected cost minimization? Utility maximization?)
   - Provide algorithm for threshold selection (grid search? cross-validation? Neyman-Pearson?)
   - Discuss how to handle multiple CWE types with different cost profiles

7. **Strengthen Contrastive Learning Justification:**
   - Provide preliminary analysis of FP pattern consistency across projects
   - Discuss what makes a "signature" transferable
   - Compare to simpler alternatives (supervised classification, metric learning)

8. **Implement Noise-Robust Learning:**
   - For DZA's weak supervision, use noise-robust methods (e.g., confident learning, noise adaptation layer)
   - Report experiments with varying label noise levels
   - Validate labels on a subset using fuzzing or manual auditing

9. **Add Cross-Language Evaluation:**
   - Include at least one C/C++ dataset (e.g., Linux kernel warnings from BugLens)
   - Analyze language-specific challenges
   - Discuss when language-specific fine-tuning is needed

10. **Provide Realistic Timeline:**
    - Consider 9-12 months for full evaluation and paper writing
    - Alternatively, focus on preliminary results for this submission and plan full evaluation for a journal extension

## Questions

1. **Preliminary Results:** Do you have any preliminary results yet, even on a small scale (10-100 samples)? This would greatly strengthen the proposal.

2. **Conformal Prediction:** How exactly do you apply conformal prediction when the LLM outputs text (TP/FP/ABSTAIN) rather than probabilities? What is the conformity score?

3. **Distribution Shift:** How do your theoretical guarantees (coverage, risk bounds) degrade under cross-project distribution shift? Can you provide formal analysis?

4. **Exchangeability:** Conformal prediction requires exchangeability. With project-level clustering, is this assumption valid? How do you handle it?

5. **Disagreement Coefficient:** Can you define the disagreement coefficient for alert triage and discuss whether fast rejection rates are achievable?

6. **Optimal Thresholds:** What is the formal optimization objective for threshold selection? How do you handle multiple CWE types with different cost profiles?

7. **Symbolic Verification:** What happens when symbolic checks timeout or fail? How does this affect the theoretical guarantees?

8. **Contrastive Learning:** Do you have evidence that FP patterns are consistent across projects? Have you analyzed signature transferability?

9. **Label Noise:** Beyond treating DZA as weak supervision, what noise-robust learning methods will you use? How will you validate labels?

10. **Scalability:** What is the computational complexity of your approach? Can it scale to 1M NASCAR warnings in reasonable time?

11. **Generalization:** Will you evaluate on C/C++ in addition to Java? How do you expect performance to differ across languages?

12. **Timeline:** Is 6 months realistic for completing all proposed work? What is the contingency plan if experiments take longer than expected?

## Rating: 7/10 (Accept, but needs revisions)

**Justification:**

This revised proposal represents a **substantial improvement** over the original submission. The authors have addressed all critical concerns raised in the first review:

✓ **Theoretical foundations:** PAC-style framework with formal definitions and promised proofs  
✓ **Preliminary experiments:** Concrete plan with phased approach and reasonable expectations  
✓ **Algorithmic detail:** Clear pseudocode for all key components  
✓ **Presentation:** Restructured for 9-page format with visual elements and precise terminology  
✓ **Novelty claims:** Clearly distinguished from prior work with honest acknowledgment  

**Remaining concerns:**

- **Still a roadmap:** No actual preliminary results yet. Even minimal experiments (100 samples) would strengthen significantly.
- **Theory gaps:** Conformal prediction details, distribution shift analysis, disagreement coefficient need clarification.
- **Scalability:** Complexity analysis and symbolic verification overhead need formal treatment.

**Why Accept:**

1. **Strong theoretical contribution:** Formalizing alert triage as selective prediction with PAC-style bounds is novel and rigorous.

2. **Feasible plan:** The preliminary experiment plan is concrete and achievable. The authors could execute it before camera-ready.

3. **Addresses important problem:** Static analysis false positives are a significant practical issue with clear demand.

4. **Rigorous methodology:** Leakage-resistant protocols, comprehensive ablations, and statistical rigor.

5. **Excellent presentation:** Clear, well-structured, and appropriate for NeurIPS.

**Conditions for acceptance:**

1. **Must include preliminary results:** At least 100-1000 Juliet samples with actual numbers (precision, calibration, abstention rate) before camera-ready.

2. **Must clarify conformal prediction:** Explicit algorithm for text-outputting LLMs.

3. **Should discuss distribution shift:** How theoretical guarantees transfer across projects.

**Alternative:** If preliminary results are not available, consider **poster/workshop** track or **conditional accept** pending results.

**Confidence in recommendation:** This is a borderline case. With preliminary results, it's a clear accept (8/10). Without results, it's a conditional accept (6/10). I'm giving 7/10 assuming results will be available before camera-ready.

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have strong expertise in selective prediction theory, calibration, and statistical learning. I am familiar with the foundational work (El-Yaniv, Geifman, conformal prediction) and can assess the theoretical rigor. My main uncertainty is whether the authors can execute the preliminary experiments in time and whether the results will be as promising as expected. However, based on the quality of the revision and the feasibility of the plan, I believe this work has strong potential for NeurIPS acceptance.
