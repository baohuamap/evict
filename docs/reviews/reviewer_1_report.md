# Reviewer 1 Report: Methods & Theory Specialist

## Summary

This paper proposes EVICT (Evidence-conditioned Verifier for Investigating Code Triage), a system for triaging static analysis alerts using large language models (LLMs) with calibrated selective prediction and optional symbolic verification. The core approach involves: (1) constructing structured evidence bundles (EvidencePacks) containing alert metadata, code slices, analyzer-produced flows, and constraints; (2) using LLMs to verify alerts through schema-guided prompting; (3) applying calibrated uncertainty estimation to enable abstention when confidence is low; (4) training contrastive representations to learn false-positive signatures; and (5) conditionally invoking SMT solvers and symbolic execution for uncertain cases. The proposal targets evaluation on NASCAR (1M Java warnings), DZA (differential analysis labels), Juliet/SARD (synthetic test suite), and CWE-Bench-Java (120 validated vulnerabilities), with SARIF as a standardized interchange format.

## Soundness: 2/5

The proposal has significant methodological and theoretical weaknesses that undermine its soundness:

**Lack of Theoretical Foundations:**
- The selective prediction framework is presented informally without rigorous mathematical formulation. There are no formal definitions of risk, coverage, or optimality criteria.
- No theoretical analysis of when abstention is beneficial or how to set thresholds optimally for asymmetric costs.
- The proposal mentions "risk-controlled adjudication" but provides no formal guarantees or bounds.
- Calibration methods (temperature scaling, conformal prediction) are mentioned but not adapted to the specific structure of alert triage—simply applying off-the-shelf techniques may not yield valid guarantees.

**Insufficient Algorithmic Detail:**
- The EvidencePack construction process is described conceptually but lacks algorithmic specification. How exactly are "minimal slices" computed? What defines "minimal"?
- The "schema-guided claim checking" prompt structure is vaguely described. What is the formal schema? How does it constrain the LLM's reasoning?
- "Lightweight SMT + targeted symbolic execution" is mentioned repeatedly but never defined. What makes symbolic execution "targeted"? What constraints are extracted and how?
- The contrastive learning approach mentions "hard-negative mining" but provides no algorithm, loss function, or training procedure details.

**Questionable Technical Claims:**
- The proposal claims conditional symbolic invocation will control costs, but provides no analysis of when the overhead is justified. Without a cost model, this is speculative.
- The claim that contrastive learning will improve cross-project generalization is unsupported. False-positive patterns may be project-specific (coding style, library usage, developer practices), making transfer difficult.
- The proposal assumes that "FP signatures" exist as learnable patterns, but provides no evidence that false positives share consistent structural features across diverse projects and bug types.

**Methodological Concerns:**
- The "progressive prompting" mechanism for requesting additional context could lead to unbounded loops or inconsistent context selection. No termination guarantees or convergence analysis is provided.
- Using differential analysis (DZA) for weak supervision is reasonable, but the proposal doesn't address how to handle label noise systematically. Simply acknowledging it as "noisy" is insufficient.
- The proposal conflates "actionable" (NASCAR) with "true vulnerability" but doesn't provide clear criteria for when to use which label, potentially confusing the learning objective.

**Missing Baselines and Ablations:**
- While the proposal lists baselines, it doesn't specify how to fairly compare systems with different design choices (e.g., how to compare a system with symbolic checks to one without?).
- The ablation plan is reasonable but incomplete—it doesn't ablate the selective prediction component itself (what if we just use a confidence threshold without formal calibration?).

**Theoretical Gaps in Selective Prediction:**
- The proposal mentions conformal prediction for API-only settings but doesn't explain how to construct valid prediction sets for classification tasks where the model outputs text rather than class probabilities.
- Temperature scaling requires access to logits and a calibration set, but the proposal doesn't discuss how to construct representative calibration sets that avoid distribution shift.
- The risk-coverage curves mentioned in evaluation require a formal definition of "risk" (FP risk? FN risk? Weighted?), which is not provided.

## Presentation: 3/5

**Strengths:**
- The proposal is well-structured with clear sections and a logical flow from motivation to method to evaluation.
- The literature survey is comprehensive and positions the work relative to recent systems (BugLens, LLM4PFA, LLM4FPM, AdaTaint).
- The use of concrete examples (Tencent study's cost metrics) helps ground the practical motivation.
- The inclusion of a Gantt chart and resource estimates shows planning effort.

**Weaknesses:**
- **Excessive length and verbosity:** The proposal reads more like a position paper or grant proposal than a research paper. For NeurIPS, it would need substantial condensation (likely 9-12 pages including references).
- **Inconsistent technical depth:** Some sections are quite detailed (dataset descriptions) while others are vague (algorithmic details, theoretical foundations).
- **Missing formal notation:** The problem formulation section mentions (C_i, Y_i) but never uses this notation consistently. A formal problem statement with mathematical definitions would greatly improve clarity.
- **Vague terminology:** Terms like "lightweight," "targeted," "minimal," and "progressive" are used without precise definitions.
- **No figures or diagrams for the method:** The flowchart is helpful but high-level. Detailed architectural diagrams, algorithm pseudocode, and example EvidencePacks would aid understanding.
- **Citation format issues:** The proposal uses URLs and informal references rather than proper academic citations. Many cited works are preprints or unpublished.

**Clarity Issues:**
- The distinction between the three formulations (binary classification, ranking, selective prediction) is unclear—which one is EVICT actually optimizing?
- The relationship between contrastive learning and the main LLM verifier is unclear. Are they separate models? Is the contrastive head used for uncertainty estimation?
- The conditional invocation logic for symbolic checks is described in prose but would benefit from a formal algorithm or decision tree.

## Contribution: 2.5/5

**Claimed Contributions:**
1. Risk-controlled adjudication via selective prediction
2. False-positive signature learning via contrastive learning
3. Verifier with symbolic hooks and abstention
4. Standardized evidence interchange via SARIF

**Assessment of Contributions:**

**Contribution 1 (Selective Prediction): Moderate-High Novelty**
- This is the strongest contribution. Calibrated abstention is not systematically applied in existing LLM-based static analysis work.
- However, the contribution is weakened by lack of theoretical development. Without formal guarantees or optimality analysis, it's primarily an engineering contribution.
- The practical value is clear (enabling human-in-the-loop with risk control), but the scientific advance is limited without theory.

**Contribution 2 (Contrastive Learning): Low-Moderate Novelty**
- Contrastive learning is a standard technique; applying it to code alert triage is a reasonable idea but not particularly novel.
- The proposal doesn't explain why contrastive learning is better than existing supervised approaches (e.g., the Transformer-based FP classifier that already shows cross-bug-type generalization [Kharkar et al. 2022]).
- The claim that FP "signatures" are learnable across projects is speculative without evidence.

**Contribution 3 (Neuro-Symbolic Integration): Low Novelty**
- Recent work (AdaTaint, WARP, Laurel, LLMDFA) already demonstrates neuro-symbolic integration for program analysis.
- The "conditional invocation" aspect is a practical contribution but not a fundamental advance.
- Without algorithmic detail on what "lightweight" and "targeted" mean, it's hard to assess the technical contribution.

**Contribution 4 (SARIF Standardization): Low Scientific Novelty**
- This is primarily an engineering contribution. Using a standard format is good practice but not a research contribution.
- SARIF adoption requires tooling effort but doesn't advance scientific understanding.

**Overall Contribution Assessment:**
The proposal's main scientific contribution is formalizing alert triage as selective prediction. However, this contribution is underdeveloped—without theoretical analysis, formal guarantees, or clear algorithmic innovations, it risks being viewed as incremental application of existing techniques (conformal prediction, temperature scaling) to a new domain.

The other contributions (contrastive learning, neuro-symbolic integration, SARIF) are incremental improvements over existing work rather than fundamental advances.

**Comparison to Recent Baselines:**
A critical weakness is that very recent work (2024-2025) already achieves very high precision:
- LLM4FPM: F1 99% on Juliet, >85% FP elimination
- LLM4PFA: 72-96% FP filtering
- Tencent study: 94-98% FP elimination

The proposal doesn't explain why EVICT will outperform these strong baselines. If EVICT achieves similar performance, the incremental value is limited. If it achieves worse performance, the abstention mechanism becomes a way to "opt out" of hard cases rather than a genuine improvement.

## Strengths

1. **Important Problem:** Static analysis false positive reduction is a significant practical problem with clear industrial demand (Tencent study shows 10-20 minutes per alarm manually).

2. **Comprehensive Literature Review:** The proposal demonstrates strong awareness of recent work and positions EVICT relative to multiple strong baselines (BugLens, LLM4PFA, LLM4FPM, AdaTaint).

3. **Selective Prediction Focus:** Treating alert triage as selective prediction with calibrated abstention addresses a genuine gap in the literature. This is the proposal's strongest contribution.

4. **Rigorous Evaluation Plan:** The proposal emphasizes leakage-resistant protocols, cross-project evaluation, and multiple complementary datasets, addressing known evaluation issues in the field.

5. **Multi-faceted Approach:** Combining evidence extraction, LLM reasoning, calibration, and symbolic verification could yield emergent benefits beyond individual components.

6. **Practical Grounding:** The inclusion of cost-benefit metrics (minutes saved, dollars per alert) and industrial evidence (Tencent) shows practical awareness.

7. **Reproducibility Focus:** Emphasis on SARIF standardization, public datasets, and shared evaluation protocols could improve reproducibility in the field.

## Weaknesses

1. **Lack of Theoretical Foundations:** No formal analysis of selective prediction, no optimality guarantees, no theoretical characterization of when abstention helps. This is critical for a NeurIPS submission.

2. **Insufficient Algorithmic Detail:** Key components (EvidencePack construction, schema-guided prompting, conditional symbolic invocation, contrastive learning) lack precise algorithmic specifications.

3. **Unclear Advantage Over Strong Baselines:** Recent work already achieves 94-99% precision. The proposal doesn't explain why EVICT will outperform or what performance level would constitute success.

4. **Questionable Assumptions:**
   - That FP "signatures" are learnable across diverse projects
   - That symbolic checks can be made "lightweight" enough for practical use
   - That LLM calibration techniques will transfer effectively to code analysis

5. **Incomplete Problem Formulation:** The proposal mentions three formulations (classification, ranking, selective prediction) but doesn't clearly specify which EVICT optimizes or how they relate.

6. **Missing Cost Model:** Conditional symbolic invocation requires a cost model to decide when overhead is justified, but none is provided.

7. **Label Quality Issues Not Addressed:** All proposed datasets have label quality issues (Juliet has 864 FPs per FuzzSlice; DZA uses "very likely" labels; NASCAR conflates "actionable" with "bug"). The proposal acknowledges this but doesn't propose solutions.

8. **Scalability Concerns:** Training contrastive models on million-scale datasets, invoking LLMs for every alert, and running symbolic checks—even conditionally—may not scale. No complexity analysis is provided.

9. **Limited Scope:** The approach is specific to static analysis alert triage. It's unclear if insights generalize to other program analysis tasks or software engineering problems.

10. **Implementation Complexity:** Integrating LLMs, SMT solvers, symbolic execution, calibration, and multiple analyzers via SARIF is highly complex. The 6-month timeline may be optimistic.

## Suggestions

1. **Develop Theoretical Foundations for Selective Prediction:**
   - Formalize the risk-coverage tradeoff with mathematical definitions
   - Prove theoretical guarantees for calibrated abstention (e.g., coverage bounds, risk bounds)
   - Characterize when abstention is optimal given asymmetric costs
   - This would substantially strengthen the contribution for NeurIPS

2. **Provide Detailed Algorithms:**
   - Algorithm for EvidencePack construction (slicing, flow extraction, constraint extraction)
   - Formal schema for claim-checking prompts
   - Algorithm for conditional symbolic invocation (when to invoke, how to scope checks)
   - Contrastive learning procedure (loss function, hard-negative mining strategy, training details)

3. **Clarify the Problem Formulation:**
   - Choose one primary formulation (likely selective prediction) and formalize it mathematically
   - Define risk, coverage, and optimality criteria precisely
   - Explain how classification and ranking relate to the selective prediction objective

4. **Develop a Cost Model:**
   - Formal model of verification costs (LLM inference time/cost, symbolic execution overhead, developer triage time)
   - Analysis of when symbolic checks are cost-effective
   - Algorithm for optimal threshold selection given cost constraints

5. **Address Label Quality Systematically:**
   - Propose noise-robust learning methods for DZA's weak supervision
   - Use FuzzSlice-style validation to audit benchmark labels
   - Consider active learning or human-in-the-loop labeling for high-quality validation sets

6. **Strengthen the Contrastive Learning Contribution:**
   - Provide theoretical or empirical analysis of when contrastive learning helps
   - Compare to simpler alternatives (supervised classification, metric learning)
   - Demonstrate that FP signatures are indeed learnable across projects with ablation studies

7. **Clarify the Neuro-Symbolic Integration:**
   - Define "lightweight" and "targeted" precisely
   - Provide concrete examples of constraints extracted and symbolic checks performed
   - Analyze the tradeoff between verification cost and error reduction

8. **Add Formal Notation and Definitions:**
   - Use consistent mathematical notation throughout
   - Define all key concepts formally (EvidencePack, risk, coverage, calibration error)
   - Provide complexity analysis where relevant

9. **Provide Empirical Evidence of Superiority:**
   - Preliminary experiments showing EVICT outperforms LLM4FPM, LLM4PFA, BugLens on same datasets
   - Demonstrate that integration yields benefits beyond individual components
   - Show that selective prediction reduces costs while maintaining safety

10. **Simplify and Focus:**
    - Consider removing less novel components (SARIF standardization, contrastive learning) to focus on selective prediction
    - Reduce scope to make the 6-month timeline more realistic
    - Prioritize theoretical development over comprehensive evaluation

## Questions

1. **Theoretical Foundations:** Can you provide formal definitions of risk and coverage for alert triage? What theoretical guarantees can you prove about your selective prediction approach?

2. **Problem Formulation:** Is EVICT optimizing for classification accuracy, ranking quality, or risk-coverage tradeoffs? How do these objectives relate?

3. **Calibration Validity:** How do you ensure that conformal prediction or temperature scaling provides valid guarantees when applied to LLM-based alert triage? What assumptions are required?

4. **Contrastive Learning:** What evidence suggests that false-positive signatures are consistent enough across projects to be learned? Have you conducted preliminary experiments?

5. **Symbolic Verification:** What specific constraints are extracted? How is symbolic execution scoped ("targeted")? What makes the approach "lightweight"?

6. **Conditional Invocation:** What algorithm decides when to invoke symbolic checks? How do you balance verification cost against error reduction?

7. **Baseline Comparison:** Given that recent work achieves 94-99% precision, what performance level would demonstrate EVICT's value? How much improvement is needed to justify the added complexity?

8. **Label Noise:** How do you handle label noise in DZA (explicitly described as "very likely" labels)? Do you use noise-robust learning methods?

9. **Scalability:** What is the computational complexity of your approach? Can it scale to millions of warnings (NASCAR) with reasonable runtime and cost?

10. **Generalization:** The proposal focuses on Java warnings (NASCAR, CWE-Bench-Java). How well do you expect the approach to generalize to C/C++, Python, or other languages?

11. **Failure Modes:** When does EVICT fail? What types of alerts or bugs does it struggle with? How does abstention rate vary across bug types?

12. **Cost-Benefit Analysis:** How do you quantify the tradeoff between automated triage savings and the cost of errors (missed bugs, false dismissals)? What cost model do you use?

## Rating: 4/10 (Weak Reject)

**Justification:**

This proposal addresses an important practical problem (static analysis false positive reduction) and makes a valuable contribution by introducing calibrated selective prediction to LLM-based alert triage. However, it suffers from significant weaknesses that make it unsuitable for NeurIPS in its current form:

1. **Insufficient theoretical depth:** The selective prediction framework lacks formal foundations, theoretical guarantees, or optimality analysis. For a NeurIPS submission, this is a critical gap.

2. **Limited novelty in most components:** Evidence-based LLM verification, neuro-symbolic integration, and contrastive learning are all established techniques. Only selective prediction represents genuine novelty, but it's underdeveloped.

3. **Unclear advantage over strong recent baselines:** Recent work (LLM4FPM, LLM4PFA, Tencent study) already achieves 94-99% precision. The proposal doesn't explain why EVICT will outperform or provide preliminary evidence of superiority.

4. **Lack of algorithmic detail:** Key components are described conceptually but lack precise specifications, making it difficult to assess technical soundness or reproducibility.

The proposal would benefit from substantial revision focusing on: (1) developing theoretical foundations for selective prediction with formal guarantees; (2) providing detailed algorithms and complexity analysis; (3) demonstrating empirical superiority over strong baselines; and (4) simplifying the scope to focus on the most novel contributions.

**Alternative venues:** This work might be better suited for ICSE, FSE, or ASE, where systems contributions and practical impact are more valued than theoretical depth.

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have strong expertise in machine learning theory, program analysis, and calibrated uncertainty estimation. I am familiar with recent work in LLM-based code analysis and selective prediction frameworks. My main uncertainty is whether the authors have preliminary results or theoretical insights not included in this proposal that would substantially strengthen the contribution. However, based on the submitted material, my assessment stands.
