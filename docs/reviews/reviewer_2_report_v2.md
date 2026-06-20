# Reviewer 2 Report (Fresh Review - Round 2): Program Analysis & Neuro-Symbolic Systems Specialist

## Summary

This revised EVICT proposal presents a comprehensive improvement roadmap for static analysis alert triage using evidence-conditioned LLMs with calibrated selective prediction and conditional symbolic verification. As a program analysis and neuro-symbolic systems specialist, I focus on: (1) the soundness of evidence extraction and representation, (2) the feasibility and effectiveness of symbolic verification integration, (3) the practical deployment considerations, and (4) the evaluation on realistic program analysis benchmarks. The revision shows **significant improvement** in technical depth, particularly in algorithmic specifications and neuro-symbolic integration strategy.

## Soundness: 4/5

From a program analysis and neuro-symbolic perspective, the proposal demonstrates strong technical soundness with some areas needing clarification:

**Evidence Extraction and Representation (Significant Improvement):**

The EvidencePack construction (Algorithm 1) is now well-specified:

- **Statement-level slicing:** Lines 4-5 specify backward slicing from sink with forward slicing from source. This is standard and appropriate for taint-style analysis.

- **Flow extraction:** Line 6 extracts the analyzer's reported path (call chain, taint edges). Good - leverages analyzer's existing work.

- **Constraint extraction:** Line 8 extracts branch conditions along the path. This is where details matter:
  - How are constraints extracted? Via symbolic execution? Static analysis? AST traversal?
  - What if constraints contain complex expressions (function calls, pointer dereferences)?
  - How are constraints normalized across different analyzers (SpotBugs vs. Infer vs. CodeQL)?

- **SARIF encoding:** Lines 9-10 package everything in SARIF format. Excellent for cross-tool compatibility.

**Strengths:**
- Clear algorithmic specification
- Leverages analyzer's existing evidence (flow traces)
- SARIF standardization enables cross-tool evaluation
- Handles missing evidence via progressive prompting (bounded multi-turn)

**Concerns:**
- Constraint extraction details are still vague. For complex Java code (generics, lambdas, reflection), constraint extraction is non-trivial.
- No discussion of how to handle analyzer-specific representations (e.g., CodeQL's data-flow paths vs. SpotBugs' bug patterns)
- Missing evidence handling: what if the analyzer doesn't provide flow traces? The proposal says "progressive prompting" but doesn't specify fallback strategies.

**Neuro-Symbolic Integration (Major Improvement):**

The conditional symbolic verification (Algorithm 2, Lines 7-9) is now explicit:

- **Decision rule:** Invoke symbolic checks when `confidence < θ_uncertain` OR `severity == HIGH` AND `predicted_label == FP`
  - This is sensible: verify uncertain cases and high-stakes dismissals
  - The severity-based triggering addresses safety concerns (don't auto-dismiss critical security bugs)

- **SMT feasibility check:** Extract path constraints, encode as SMT formula, invoke Z3 with 10s timeout
  - Standard approach, similar to LLM4PFA
  - Timeout is reasonable for practical deployment
  - But: what if Z3 returns UNKNOWN (neither SAT nor UNSAT)? The proposal should specify handling

- **Symbolic execution:** KLEE with depth ≤50, max 100 paths
  - These are very conservative limits - will likely miss deep bugs
  - But reasonable for "lightweight" verification to validate LLM decisions
  - Question: KLEE is for C/C++, but the focus is Java. Will you use Java PathFinder instead?

- **Certificate generation:** Lines 10-11 produce auditable SAT/UNSAT results with counterexamples
  - Excellent for trust and explainability
  - Counterexamples (concrete inputs triggering the bug) are valuable for developers

**Strengths:**
- Clear decision logic for when to invoke symbolic checks
- Appropriate tool choices (Z3, KLEE/JPF)
- Auditable certificates with counterexamples
- Safety-conscious (verify high-severity dismissals)

**Concerns:**
- **Tool mismatch:** KLEE is for C/C++, but NASCAR and CWE-Bench-Java are Java. The proposal should specify Java PathFinder or Symbolic PathFinder for Java.
- **UNKNOWN handling:** SMT solvers often return UNKNOWN (timeout, undecidable theory). How does this affect the decision?
- **Constraint extraction quality:** Symbolic verification is only as good as the extracted constraints. If constraints are incomplete or incorrect, verification may give false confidence.
- **Scalability:** Even with conservative limits (depth 50, 100 paths), symbolic execution can be slow. The proposal should provide expected overhead (e.g., "symbolic checks add X seconds per alert on average").

**LLM Verification (Well-Specified):**

Algorithm 2, Lines 3-5 specify the LLM verification:

- **Schema-guided prompting:** The schema (Section 3.2.3) is now detailed:
  1. Restate analyzer claim
  2. List necessary preconditions for the bug
  3. Check each precondition against evidence
  4. Output TP/FP/ABSTAIN with confidence and rationale

- **Confidence estimation:** Multiple methods mentioned:
  - Logit-based (if accessible): entropy, margin
  - Ensemble-based (if API-only): self-consistency, vote entropy
  - Conformal prediction wrapper

**Strengths:**
- Structured reasoning reduces hallucination
- Multiple confidence estimation methods for different LLM access levels
- Explicit rationale with evidence references

**Concerns:**
- **Prompt engineering:** The schema is described but no actual prompts are provided. Prompt wording can dramatically affect results.
- **Hallucination risk:** Even with structured prompts, LLMs can hallucinate preconditions or misinterpret evidence. The symbolic verification mitigates this, but only for uncertain cases.
- **Non-determinism:** LLM outputs vary across runs. The proposal mentions "deterministic seeds where possible" but API-only models don't support this. How is reproducibility ensured?

**Contrastive Learning for FP Signatures (Improved but Questions Remain):**

Algorithm 3 specifies contrastive learning with InfoNCE loss and hard-negative mining:

- **Positive pairs:** Same alert, same label (TP or FP)
- **Hard negatives:** Same rule, similar slice, different label
- **Loss:** InfoNCE with temperature τ=0.1

**Strengths:**
- Standard contrastive learning approach
- Hard-negative mining is appropriate for learning discriminative features
- Explicit training procedure

**Concerns:**
- **Assumption validity:** The approach assumes FP patterns are consistent across projects. Is this true? False positives may arise from project-specific coding styles, library usage, or domain-specific patterns.
- **Negative mining strategy:** "Similar slice" - how is similarity measured? Edit distance? Embedding similarity? This affects what the model learns.
- **Evaluation:** The proposal should include experiments showing that learned representations transfer across projects. Without this, the value of contrastive learning is unclear.

**Preliminary Experiments (Addresses Critical Gap):**

The phased preliminary experiment plan is concrete and feasible:

- **Phase 1 (Weeks 1-4):** 1000 Juliet samples, evidence-conditioned vs. baseline, preliminary calibration
  - Feasible and appropriate for proof-of-concept
  - Juliet is controlled and well-understood
  - Expected precision 85-95% is reasonable given recent work

- **Phase 2 (Weeks 5-8):** 5000 Juliet samples, contrastive learning, compare to LLM4FPM
  - Good choice of baseline (LLM4FPM is strong recent work)
  - 5000 samples sufficient for training contrastive models
  - Expected ECE <0.1 is achievable with proper calibration

**Strengths:**
- Concrete, feasible plan
- Phased approach reduces risk
- Appropriate baseline comparison

**Concerns:**
- **Still no actual results:** The proposal is a plan, not completed work. For NeurIPS, even 100-sample pilot results would be much more convincing.
- **Juliet limitations:** Juliet is synthetic and may not reflect real-world FP patterns. Phase 2 should include at least one real-world dataset (e.g., DZA or NASCAR subset).
- **Baseline implementation:** The proposal says "implement LLM4FPM using same LLM and prompts" but LLM4FPM uses eCPG-based slicing. Will you reimplement their slicing or use your own? This affects fairness of comparison.

## Presentation: 4/5

The presentation is much improved:

**Strengths:**

1. **Clear structure:** Part 1 (improvements), Part 2 (theory), Part 3 (methodology), Part 4 (evaluation), Part 5 (roadmap). Easy to navigate.

2. **Algorithmic clarity:** Algorithms 1-3 provide precise pseudocode that could be implemented.

3. **Visual elements:** Architecture diagram, risk-coverage curves, calibration plots, example EvidencePack. These are helpful.

4. **Precise definitions:** "Lightweight" (10s timeout, 2GB memory), "targeted" (depth ≤50, max 100 paths). No more vague terminology.

5. **SARIF examples:** The EvidencePack example (Figure 4) shows concrete SARIF encoding. This clarifies the data representation.

**Weaknesses:**

1. **Tool mismatch not addressed in main text:** KLEE is for C/C++, but the focus is Java. This should be clarified upfront (e.g., "KLEE for C/C++, JPF for Java").

2. **Constraint extraction details:** Algorithm 1, Line 8 says "extract branch conditions" but doesn't specify how. For a program analysis audience, this is a critical detail.

3. **Example prompts missing:** The schema is described, but actual prompts would help assess whether the structured reasoning is effective.

4. **Complexity analysis:** No formal time/space complexity for algorithms. For scalability assessment, this is important.

5. **Failure mode analysis:** The proposal mentions "when EVICT fails" (concurrency, algorithmic bugs, severe shift) but doesn't provide systematic analysis or mitigation strategies.

## Contribution: 4/5

From a program analysis and neuro-symbolic perspective:

**Contribution 1: Evidence-Conditioned Verification with Selective Prediction (High Value)**

- **Novelty:** Combining evidence-based LLM reasoning with formal selective prediction is new
- **Impact:** Enables safe automation of alert triage with theoretical guarantees
- **Practical value:** High - addresses major pain point in industrial static analysis

**Assessment:** Strong contribution. The integration of program analysis evidence (slices, flows, constraints) with calibrated ML decision-making is valuable.

**Contribution 2: Conditional Neuro-Symbolic Verification (Moderate-High Value)**

- **Novelty:** Conditional invocation based on uncertainty and severity is less explored
- **Impact:** Reduces verification overhead while maintaining safety
- **Practical value:** High - makes symbolic verification practical for large-scale triage

**Assessment:** The decision logic (verify uncertain and high-severity cases) is sensible and novel. However, the symbolic verification itself (SMT + symex) is standard. The contribution is in the integration and conditional invocation strategy.

**Contribution 3: SARIF-Based Cross-Tool Evaluation (High Practical Value)**

- **Novelty:** Low - SARIF is an existing standard
- **Impact:** High for reproducibility and cross-tool comparison
- **Practical value:** Very high - enables systematic evaluation across analyzers

**Assessment:** This is primarily an engineering contribution, but it's valuable for the community. Cross-tool evaluation is rare in this area.

**Contribution 4: Contrastive Learning for FP Signatures (Moderate Value)**

- **Novelty:** Moderate - contrastive learning is standard, application to FP patterns is new
- **Impact:** Depends on whether FP patterns actually transfer across projects (unvalidated)
- **Practical value:** Moderate - if patterns transfer, this could improve cross-project generalization

**Assessment:** The value depends on empirical validation. The proposal should include experiments showing that learned representations transfer.

**Comparison to Recent Work:**

The proposal now clearly distinguishes EVICT:

- **vs. LLM4FPM:** EVICT adds selective prediction, symbolic verification, and cross-tool evaluation
- **vs. LLM4PFA:** EVICT adds formal guarantees, conditional invocation, and SARIF standardization
- **vs. AdaTaint:** EVICT adds selective prediction, contrastive learning, and comprehensive evaluation
- **vs. BugLens:** EVICT adds quantitative risk control, symbolic verification, and cross-tool support

This is clear and honest.

## Strengths

1. **Addresses Critical Program Analysis Challenges:**
   - Evidence extraction from diverse analyzers via SARIF
   - Handling missing or incomplete evidence
   - Cross-tool evaluation and generalization

2. **Well-Designed Neuro-Symbolic Integration:**
   - Clear decision logic for conditional symbolic verification
   - Appropriate tool choices (Z3, KLEE/JPF)
   - Auditable certificates with counterexamples
   - Safety-conscious (verify high-severity dismissals)

3. **Practical Deployment Considerations:**
   - Lightweight verification (10s timeout, conservative limits)
   - Cost-benefit analysis (verification overhead vs. error reduction)
   - Industrial grounding (Tencent study, ROI metrics)

4. **Rigorous Evaluation Design:**
   - Multiple complementary datasets (synthetic, differential, validated)
   - Leakage-resistant protocols (function-level dedup, project splits)
   - Cross-tool evaluation (SpotBugs, Infer, CodeQL)
   - Comprehensive ablations

5. **Clear Algorithmic Specifications:**
   - Algorithm 1 (EvidencePack construction)
   - Algorithm 2 (Calibrated selective triage)
   - Algorithm 3 (Contrastive FP learning)

6. **Concrete Preliminary Experiment Plan:**
   - Phased approach (1000 → 5000 Juliet samples)
   - Feasible timeline (8 weeks)
   - Appropriate baselines (LLM4FPM)

7. **SARIF Standardization:**
   - Enables cross-tool comparison
   - Facilitates reproducibility
   - Practical value for community

8. **Honest About Limitations:**
   - Discusses failure modes (concurrency, algorithmic bugs, severe shift)
   - Acknowledges label quality issues
   - Recognizes symbolic verification limitations

9. **Responsive to Feedback:**
   - Addresses all major concerns from first review
   - Substantial improvement in technical depth

10. **Strong Practical Motivation:**
    - Clear industrial demand (10-20 min/alarm)
    - Concrete cost-benefit analysis
    - ROI metrics and deployment considerations

## Weaknesses

1. **Still No Actual Results:**
   - The proposal is a detailed plan, not completed work
   - Even 100-sample pilot results would strengthen significantly
   - For NeurIPS, preliminary results are expected

2. **Tool Mismatch:**
   - KLEE is for C/C++, but focus is Java (NASCAR, CWE-Bench-Java)
   - Should specify Java PathFinder or Symbolic PathFinder
   - This is a technical error that should be corrected

3. **Constraint Extraction Details:**
   - Algorithm 1, Line 8 is vague: "extract branch conditions"
   - How exactly? Via symbolic execution? Static analysis? AST traversal?
   - For complex Java (generics, lambdas, reflection), this is non-trivial
   - Missing detail for a program analysis audience

4. **SMT UNKNOWN Handling:**
   - Z3 often returns UNKNOWN (timeout, undecidable theory)
   - How does this affect the decision? Treat as uncertain? Abstain?
   - The proposal should specify this

5. **Contrastive Learning Validation:**
   - Assumes FP patterns transfer across projects (untested)
   - No preliminary analysis of pattern consistency
   - Should include experiments showing transferability

6. **Baseline Implementation Details:**
   - "Implement LLM4FPM using same LLM" - but LLM4FPM uses eCPG-based slicing
   - Will you reimplement their slicing or use your own?
   - This affects fairness of comparison

7. **Juliet-Only Preliminary Experiments:**
   - Phase 1 and 2 use only Juliet (synthetic)
   - Should include at least one real-world dataset (DZA or NASCAR subset)
   - Juliet may not reflect real-world FP patterns

8. **Scalability Analysis:**
   - No formal complexity analysis
   - No expected overhead for symbolic verification
   - "Lightweight" is defined (10s timeout) but average case is not reported

9. **Prompt Engineering:**
   - Schema is described but no actual prompts provided
   - Prompt wording can dramatically affect results
   - Should include example prompts (appendix or supplementary)

10. **Failure Mode Analysis:**
    - Mentions failure modes (concurrency, algorithmic bugs) but no systematic analysis
    - No mitigation strategies beyond "abstain when uncertain"
    - Should characterize failure patterns more precisely

11. **Cross-Language Generalization:**
    - Focus on Java (NASCAR, CWE-Bench-Java)
    - C/C++ evaluation mentioned but not detailed
    - Should include at least one C/C++ dataset (e.g., Linux kernel from BugLens)

12. **Label Quality Solutions:**
    - Acknowledges label issues but doesn't propose concrete solutions
    - "Treat DZA as weak supervision" - but what noise-robust methods?
    - Should specify techniques (confident learning, noise adaptation)

## Suggestions

1. **Conduct Minimal Preliminary Experiments:**
   - Even 50-100 Juliet samples with actual results would strengthen enormously
   - Show precision, calibration (ECE), abstention rate
   - Include in the proposal as proof-of-concept

2. **Fix Tool Mismatch:**
   - Specify Java PathFinder or Symbolic PathFinder for Java
   - Or include C/C++ evaluation with KLEE
   - This is a technical error that undermines credibility

3. **Detail Constraint Extraction:**
   - Specify method: symbolic execution? Static analysis? AST traversal?
   - Discuss handling of complex Java features (generics, lambdas, reflection)
   - Provide example: given code snippet, show extracted constraints

4. **Specify SMT UNKNOWN Handling:**
   - Add to Algorithm 2: if Z3 returns UNKNOWN, treat as uncertain → abstain
   - Discuss impact on abstention rate
   - Report expected UNKNOWN rate based on prior work

5. **Validate Contrastive Learning:**
   - Preliminary analysis of FP pattern consistency across projects
   - Experiments showing learned representations transfer
   - Compare to supervised baseline (same architecture, no contrastive pre-training)

6. **Clarify Baseline Implementation:**
   - Specify whether you reimplement LLM4FPM's eCPG slicing or use your own
   - If using your own, acknowledge that comparison is not apples-to-apples
   - Consider implementing multiple baselines for robustness

7. **Add Real-World Dataset to Preliminary Experiments:**
   - Phase 1.5 (Weeks 4-6): 500 DZA samples or 1000 NASCAR samples
   - Show that approach works on real-world data, not just synthetic
   - Compare FP patterns: Juliet vs. real-world

8. **Provide Complexity Analysis:**
   - Formal time/space complexity for Algorithms 1-3
   - Expected overhead for symbolic verification (average case, worst case)
   - Scalability experiments: runtime vs. number of warnings

9. **Include Example Prompts:**
   - Provide actual prompts in appendix or supplementary material
   - Show how schema is instantiated for concrete examples
   - Include LLM responses to illustrate structured reasoning

10. **Systematic Failure Mode Analysis:**
    - Categorize bugs by type (concurrency, algorithmic, resource, taint)
    - Report expected performance by category
    - Identify mitigation strategies for each failure mode

11. **Add C/C++ Evaluation:**
    - Include Linux kernel warnings from BugLens study
    - Compare Java vs. C/C++ performance
    - Analyze language-specific challenges

12. **Specify Noise-Robust Learning:**
    - For DZA weak supervision, use confident learning or noise adaptation
    - Report experiments with varying label noise levels
    - Validate labels on subset using fuzzing or manual auditing

## Questions

1. **Preliminary Results:** Do you have any preliminary results, even on 10-50 samples? This would greatly strengthen the proposal.

2. **Tool Selection:** For Java, will you use Java PathFinder or Symbolic PathFinder instead of KLEE? Please clarify.

3. **Constraint Extraction:** How exactly do you extract branch conditions (Algorithm 1, Line 8)? Via symbolic execution? Static analysis? AST traversal?

4. **SMT UNKNOWN:** How do you handle Z3 returning UNKNOWN? Treat as uncertain? Abstain? What's the expected UNKNOWN rate?

5. **Contrastive Learning:** Do you have evidence that FP patterns are consistent across projects? Have you analyzed pattern transferability?

6. **Baseline Implementation:** Will you reimplement LLM4FPM's eCPG slicing or use your own? How does this affect comparison fairness?

7. **Real-World Evaluation:** Will Phase 1 or 2 include real-world data (DZA, NASCAR), or only Juliet? Juliet is synthetic and may not reflect real patterns.

8. **Scalability:** What is the expected overhead for symbolic verification? Average seconds per alert? What fraction of alerts trigger symbolic checks?

9. **Prompt Examples:** Can you provide example prompts showing how the schema is instantiated? This would help assess effectiveness.

10. **Failure Modes:** Can you provide systematic analysis of when EVICT fails? Performance by bug category? Mitigation strategies?

11. **Cross-Language:** Will you evaluate on C/C++ (e.g., Linux kernel)? How do you expect performance to differ from Java?

12. **Label Noise:** What noise-robust learning methods will you use for DZA's weak supervision? How will you validate labels?

13. **Reproducibility:** How do you ensure reproducibility with non-deterministic LLMs? Multiple runs with variance reporting? Fixed seeds (if available)?

14. **Analyzer Coverage:** Which analyzers will you evaluate (SpotBugs, Infer, CodeQL)? How do you handle analyzer-specific representations?

15. **Deployment:** What would be required to deploy EVICT in a real industrial setting? Integration challenges? Maintenance overhead?

## Rating: 7/10 (Accept, but needs revisions)

**Justification:**

This revised proposal shows **substantial improvement** over the original submission. From a program analysis and neuro-symbolic perspective, the technical approach is sound:

✓ **Evidence extraction:** Well-specified with SARIF standardization  
✓ **Neuro-symbolic integration:** Clear decision logic, appropriate tools, auditable certificates  
✓ **Practical considerations:** Lightweight verification, cost-benefit analysis, industrial grounding  
✓ **Evaluation design:** Rigorous protocols, cross-tool evaluation, comprehensive ablations  
✓ **Algorithmic clarity:** Precise pseudocode for all key components  

**Remaining concerns:**

- **No actual results:** Still a roadmap, not completed work. Even minimal pilot results would strengthen significantly.
- **Tool mismatch:** KLEE for C/C++, but focus is Java. Needs correction.
- **Constraint extraction:** Details are vague for a program analysis audience.
- **Contrastive learning:** Assumption that FP patterns transfer is untested.

**Why Accept:**

1. **Addresses important problem:** Static analysis false positives are a major practical issue.

2. **Novel integration:** Combining evidence-based reasoning, selective prediction, and conditional symbolic verification is new.

3. **Practical value:** High potential for industrial deployment with clear ROI.

4. **Rigorous methodology:** Leakage-resistant protocols, cross-tool evaluation, comprehensive ablations.

5. **Feasible plan:** The preliminary experiment plan is concrete and achievable.

**Conditions for acceptance:**

1. **Must fix tool mismatch:** Specify JPF for Java or include C/C++ evaluation with KLEE.

2. **Should include preliminary results:** At least 50-100 samples with actual numbers before camera-ready.

3. **Must detail constraint extraction:** Specify method and provide examples.

**Alternative:** If preliminary results are not available, consider **conditional accept** pending results or **poster track**.

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have strong expertise in program analysis, static analysis tools, and neuro-symbolic systems. I am familiar with the tools mentioned (Z3, KLEE, JPF, SpotBugs, CodeQL) and can assess technical soundness. My main uncertainty is whether the authors can execute the preliminary experiments successfully and whether FP patterns actually transfer across projects. However, based on the quality of the revision and the feasibility of the plan, I believe this work has strong potential for NeurIPS acceptance.
