# Meta-Review (Round 2): Evidence-Conditioned LLM Investigation for Static-Analysis Alert Triage

## Overview

This is a **fresh peer review (Round 2)** of the improved EVICT proposal by three NEW reviewers with different perspectives from the first round: (1) Calibration & Statistical Learning Theory Specialist (R1), (2) Program Analysis & Neuro-Symbolic Systems Specialist (R2), and (3) ML for Software Engineering & Human-AI Collaboration Specialist (R3). The goal is to assess whether the improvements adequately address previous concerns and whether the proposal is now competitive for NeurIPS acceptance.

**Reviewer Scores (Round 2):**
- Reviewer 1 (Calibration & Theory): 7/10 (Accept, but needs revisions)
- Reviewer 2 (Program Analysis & Neuro-Symbolic): 7/10 (Accept, but needs revisions)
- Reviewer 3 (ML-for-SE & Human-AI): 7.5/10 (Accept)

**Meta-Reviewer Recommendation: ACCEPT (Conditional)**

## Executive Summary

The revised EVICT proposal demonstrates **substantial improvement** over the original submission. All three reviewers recognize that the authors have addressed the critical concerns from the first review:

✓ **Theoretical foundations added:** PAC-style framework for selective prediction with formal definitions  
✓ **Preliminary experiment plan:** Concrete, phased approach with feasible timeline  
✓ **Algorithmic specifications:** Clear pseudocode for all key components  
✓ **Presentation vastly improved:** Restructured for NeurIPS format with visual elements  
✓ **Novelty claims sharpened:** Clear distinction from prior work  

**Key Improvement:** The proposal has evolved from a vague research idea (Round 1: 4-5/10) to a rigorous, well-specified research plan (Round 2: 7-7.5/10). This represents a **3-point improvement** in reviewer scores.

**Remaining Limitation:** The proposal is still a **roadmap** rather than completed work. No actual preliminary results are included. However, all three reviewers agree that the plan is concrete and feasible enough to warrant acceptance, with the expectation that preliminary results will be available before camera-ready.

---

## Comparison: Round 1 vs. Round 2

### Round 1 Scores (Original Proposal)
- Reviewer 1 (Methods & Theory): 4/10 (Weak Reject)
- Reviewer 2 (Experiments & Practical): 5/10 (Borderline Reject)
- Reviewer 3 (Clarity & Positioning): 5/10 (Borderline Reject)
- **Average: 4.67/10 (REJECT)**

### Round 2 Scores (Improved Proposal)
- Reviewer 1 (Calibration & Theory): 7/10 (Accept, but needs revisions)
- Reviewer 2 (Program Analysis & Neuro-Symbolic): 7/10 (Accept, but needs revisions)
- Reviewer 3 (ML-for-SE & Human-AI): 7.5/10 (Accept)
- **Average: 7.17/10 (CONDITIONAL ACCEPT)**

### Improvement: +2.5 points (53% increase)

---

## Assessment of Improvements

### 1. Theoretical Foundations (Critical Issue → RESOLVED)

**Round 1 Concern (R1: "Critical Gap"):**
> "No formal definitions of risk, coverage, or optimality criteria... no theoretical guarantees or bounds... For NeurIPS, this is a critical gap."

**Round 2 Assessment (R1: "Major Improvement"):**
> "The addition of formal selective prediction theory is the most significant enhancement... PAC-style framework with formal definitions of risk, coverage, and optimality... promise to prove coverage bounds and risk bounds... This is a strong contribution for NeurIPS."

**Verdict:** ✅ **RESOLVED**
- PAC-style framework with predictor-rejector formulation
- Formal definitions of risk R(h,g) = α·R_FN + β·R_FP + γ·R_abstain
- Promise to prove coverage bounds P(g(x)=1) ≥ 1-δ and risk bounds
- Integration of conformal prediction for distribution-free guarantees
- Reference to foundational work (El-Yaniv, Geifman, Vovk)

**Remaining Gaps (Minor):**
- R1: Disagreement coefficient not defined for alert triage setting
- R1: Distribution shift theory (how bounds degrade under project shift)
- R1: Conformal prediction details for text-outputting LLMs

**Impact:** This addresses the most critical weakness from Round 1. The theoretical contribution is now sufficient for NeurIPS.

---

### 2. Preliminary Experiments (Critical Issue → SUBSTANTIALLY IMPROVED)

**Round 1 Concern (All Reviewers: "Most Significant Barrier"):**
> "No preliminary results... entirely prospective without even pilot experiments... For NeurIPS, preliminary results are essential."

**Round 2 Assessment (R2: "Addresses Critical Gap"):**
> "The phased preliminary experiment plan is concrete and feasible... Phase 1: 1000 Juliet samples, Phase 2: 5000 samples + LLM4FPM comparison... This addresses the most critical weakness from the first review."

**Verdict:** ⚠️ **SUBSTANTIALLY IMPROVED, BUT INCOMPLETE**
- Concrete plan with phased approach (Weeks 1-4: 1000 samples, Weeks 5-8: 5000 samples)
- Feasible timeline and realistic expectations (precision 85-95%, ECE <0.1, abstention 10-20%)
- Appropriate baseline (LLM4FPM)
- Clear methodology (evidence-conditioned vs. baseline, calibration analysis)

**Remaining Gap:**
- **No actual results yet** - still a plan, not completed work
- All three reviewers note this limitation but consider the plan strong enough to accept conditionally

**Reviewer Consensus:**
- R1: "Even 100-sample pilot results would strengthen enormously... With preliminary results, it's a clear accept (8/10)"
- R2: "Even 50-100 samples with actual results would strengthen significantly"
- R3: "Even 50-100 sample pilot results would strengthen enormously"

**Impact:** The plan is now concrete and feasible. All reviewers agree it warrants conditional acceptance, with the expectation of preliminary results before camera-ready.

---

### 3. Algorithmic Detail (Critical Issue → RESOLVED)

**Round 1 Concern (R1 & R2: "Insufficient"):**
> "Key components lack precise specifications... vague descriptions... no pseudocode... making it difficult to assess technical soundness or reproducibility."

**Round 2 Assessment (R2: "Well-Specified"):**
> "Algorithms 1-3 provide precise pseudocode that could be implemented... Algorithm 1 (EvidencePack construction) is now well-specified... Clear algorithmic specification."

**Verdict:** ✅ **RESOLVED**
- Algorithm 1: EvidencePack construction (slicing, flow extraction, constraint extraction, SARIF encoding)
- Algorithm 2: Calibrated selective triage (LLM verification, confidence estimation, conditional symbolic invocation)
- Algorithm 3: Contrastive FP learning (InfoNCE loss, hard-negative mining)

**Remaining Gaps (Minor):**
- R2: Constraint extraction details still vague ("extract branch conditions" - how exactly?)
- R2: SMT UNKNOWN handling not specified
- R1: Optimal threshold selection algorithm not fully specified

**Impact:** The algorithmic clarity is now sufficient for implementation and reproducibility. Minor gaps can be addressed in camera-ready.

---

### 4. Presentation (Critical Issue → RESOLVED)

**Round 1 Concern (All Reviewers: "Excessive Length, Missing Visuals"):**
> "~12 pages vs. 9-page NeurIPS limit... missing visual elements... vague terminology... unclear problem formulation."

**Round 2 Assessment (R3: "Vastly Improved"):**
> "The presentation is vastly improved... Clear structure, visual elements added, precise terminology, formal notation, appropriate length for 9-page NeurIPS format."

**Verdict:** ✅ **RESOLVED**
- Structured for 9-page NeurIPS format with supplementary material
- Visual elements: architecture diagram, risk-coverage curves, calibration plots, example EvidencePack
- Precise terminology: "lightweight" (10s timeout, 2GB), "targeted" (depth ≤50, max 100 paths)
- Formal notation used consistently (h, g, R)
- Clear problem formulation with selective prediction as primary objective

**Remaining Gaps (Minor):**
- R2: Example prompts missing (can be in supplementary)
- R3: UI mockups for human-in-the-loop workflow
- R2: Complexity analysis

**Impact:** The presentation is now appropriate for NeurIPS. Minor gaps can be addressed in camera-ready.

---

### 5. Novelty Claims (Major Issue → RESOLVED)

**Round 1 Concern (All Reviewers: "Overstated"):**
> "Evidence-conditioned verification is presented as novel, but multiple recent systems already use this approach... should more clearly distinguish EVICT's contributions."

**Round 2 Assessment (R3: "Much Clearer"):**
> "The proposal now clearly distinguishes EVICT from recent systems... vs. LLM4FPM: EVICT adds selective prediction... vs. LLM4PFA: EVICT adds formal guarantees... This is much clearer than the original proposal."

**Verdict:** ✅ **RESOLVED**
- Clear distinction from LLM4FPM, LLM4PFA, BugLens, AdaTaint
- Honest acknowledgment of what's not novel (evidence-based reasoning is established)
- Focus on selective prediction as primary contribution
- Explicit comparison table

**Impact:** The novelty narrative is now honest and clear. Reviewers understand what is novel (selective prediction framework) and what is incremental (contrastive learning, symbolic verification).

---

### 6. Label Quality (Major Issue → ACKNOWLEDGED BUT NOT FULLY RESOLVED)

**Round 1 Concern (All Reviewers: "Not Addressed"):**
> "All datasets have known problems... proposal only acknowledges without proposing solutions... Juliet: 864 FPs, DZA: 'very likely' labels, NASCAR: conflates actionable with bug."

**Round 2 Assessment (R2: "Acknowledges but Doesn't Propose Solutions"):**
> "Acknowledges label issues but doesn't propose concrete solutions... 'Treat DZA as weak supervision' - but what noise-robust methods?"

**Verdict:** ⚠️ **ACKNOWLEDGED BUT INCOMPLETE**
- Proposal acknowledges label quality issues explicitly
- Mentions "weak supervision" for DZA
- Emphasizes leakage-resistant protocols (deduplication, project splits)
- But: no concrete noise-robust learning methods specified

**Reviewer Suggestions:**
- R1: "Use noise-robust methods (e.g., confident learning, noise adaptation layer)"
- R2: "Specify techniques (confident learning, noise adaptation)"
- R3: "Validate labels on subset using fuzzing or manual auditing"

**Impact:** This is a remaining weakness but not critical. Reviewers accept that label noise is inherent in the domain. The proposal should add noise-robust methods in camera-ready.

---

### 7. Neuro-Symbolic Integration (Moderate Issue → SUBSTANTIALLY IMPROVED)

**Round 1 Concern (R1: "Vague"):**
> "'Lightweight SMT + targeted symbolic execution' is mentioned repeatedly but never defined... no algorithmic detail."

**Round 2 Assessment (R2: "Well-Designed"):**
> "The conditional symbolic verification is now explicit... Clear decision logic, appropriate tool choices (Z3, KLEE/JPF), auditable certificates... Well-designed neuro-symbolic integration."

**Verdict:** ✅ **SUBSTANTIALLY IMPROVED**
- Clear decision rule: invoke when `confidence < θ_uncertain` OR `severity == HIGH` AND `predicted_label == FP`
- Specific tools: Z3 (SMT), KLEE/JPF (symbolic execution)
- Concrete limits: 10s timeout, 2GB memory, depth ≤50, max 100 paths
- Auditable certificates with counterexamples

**Remaining Gaps (Minor):**
- R2: Tool mismatch - KLEE is for C/C++, but focus is Java (should specify JPF)
- R2: SMT UNKNOWN handling not specified
- R1: No complexity analysis or average-case overhead estimates

**Impact:** The neuro-symbolic integration is now well-specified. The tool mismatch is a technical error that should be corrected, but doesn't undermine the approach.

---

## Summary of Reviewer Assessments (Round 2)

### Reviewer 1 (Calibration & Statistical Learning Theory Specialist)

**Overall Assessment:** "Substantial improvement... addresses all critical concerns"

**Soundness:** 4/5 (up from 2/5 in Round 1)
- Theoretical foundations: Major improvement with PAC-style framework
- Algorithmic detail: Significant improvement with clear pseudocode
- Preliminary experiments: Addresses critical gap with concrete plan
- Remaining gaps: Conformal prediction details, distribution shift theory, disagreement coefficient

**Presentation:** 4.5/5 (up from 3/5)
- Clear structure, visual elements, precise terminology, formal notation
- Minor gaps: Example prompts, complexity analysis

**Contribution:** 4/5 (up from 2.5/5)
- Selective prediction: High novelty, strong theoretical contribution
- Contrastive learning: Moderate novelty
- Neuro-symbolic integration: Moderate novelty
- Evaluation protocols: Moderate-high practical value

**Rating:** 7/10 (Accept, but needs revisions)
- **Conditions:** Must include preliminary results (100-1000 samples) before camera-ready; must clarify conformal prediction; should discuss distribution shift

**Confidence:** 4/5

---

### Reviewer 2 (Program Analysis & Neuro-Symbolic Systems Specialist)

**Overall Assessment:** "Substantial improvement... technical approach is sound"

**Soundness:** 4/5 (up from 2.5/5)
- Evidence extraction: Well-specified with SARIF standardization
- Neuro-symbolic integration: Clear decision logic, appropriate tools
- Practical considerations: Lightweight verification, cost-benefit analysis
- Remaining gaps: Tool mismatch (KLEE vs. JPF), constraint extraction details, SMT UNKNOWN handling

**Presentation:** 4/5 (up from 3.5/5)
- Clear structure, algorithmic clarity, visual elements
- Minor gaps: Tool mismatch not addressed upfront, constraint extraction details, example prompts

**Contribution:** 4/5 (up from 3/5)
- Evidence-conditioned verification with selective prediction: High value
- Conditional neuro-symbolic verification: Moderate-high value
- SARIF cross-tool evaluation: High practical value
- Contrastive learning: Moderate value (depends on validation)

**Rating:** 7/10 (Accept, but needs revisions)
- **Conditions:** Must fix tool mismatch (specify JPF for Java); should include preliminary results (50-100 samples); must detail constraint extraction

**Confidence:** 4/5

---

### Reviewer 3 (ML for Software Engineering & Human-AI Collaboration Specialist)

**Overall Assessment:** "Major improvement... approach is sound and valuable"

**Soundness:** 4.5/5 (up from 3/5)
- Human-in-the-loop design: Major improvement with explicit collaboration model
- Practical feasibility: Significant improvement with deployment considerations
- Realistic evaluation: Multiple datasets reflecting real SE tasks
- Remaining gaps: User studies missing, developer feedback mechanism not specified

**Presentation:** 4.5/5 (up from 2.5/5)
- Vastly improved: clear structure, visual elements, precise terminology
- Minor gaps: UI mockups, developer feedback mechanism, longitudinal evaluation plan

**Contribution:** 4/5 (up from 3/5)
- Human-in-the-loop with calibrated abstention: High value (strongest contribution)
- Evidence-based LLM reasoning: Moderate value
- Cross-tool evaluation with SARIF: High practical value
- Rigorous evaluation protocols: High value for community

**Rating:** 7.5/10 (Accept)
- **Conditions:** Should include preliminary results (50-100 samples) before camera-ready; should add user study plans; must specify developer feedback mechanism

**Confidence:** 4/5

---

## Areas of Agreement (Round 2)

All three reviewers agree on:

**Strengths:**
1. **Substantial improvement** over Round 1 - all critical concerns addressed
2. **Theoretical foundations** now rigorous with PAC-style framework
3. **Algorithmic specifications** clear and implementable
4. **Presentation vastly improved** - appropriate for NeurIPS
5. **Novelty claims sharpened** - clear distinction from prior work
6. **Preliminary experiment plan** concrete and feasible
7. **Practical value** high - addresses real industrial problem
8. **Responsive to feedback** - authors took first review seriously

**Remaining Concerns:**
1. **No actual preliminary results yet** - still a roadmap, not completed work
2. **Minor technical gaps** - conformal prediction details, constraint extraction, SMT UNKNOWN handling, tool mismatch
3. **Label quality** - acknowledged but no concrete noise-robust methods
4. **User studies missing** - important for human-in-the-loop work

**Consensus on Recommendation:**
- All three reviewers recommend **ACCEPT** (with conditions)
- All agree that preliminary results would strengthen the work (would raise scores to 8/10)
- All agree that the plan is concrete enough to warrant conditional acceptance

---

## Areas of Disagreement (Round 2)

The reviewers have minor differences in emphasis:

**Reviewer 1 (Theory)** is most concerned about:
- Conformal prediction details for text-outputting LLMs
- Distribution shift theory (how bounds degrade)
- Disagreement coefficient definition
- Gives 7/10 (conditional accept)

**Reviewer 2 (Program Analysis)** emphasizes:
- Tool mismatch (KLEE for C/C++ vs. Java focus)
- Constraint extraction details
- SMT UNKNOWN handling
- Gives 7/10 (conditional accept)

**Reviewer 3 (ML-for-SE)** focuses on:
- User studies and developer feedback
- Human-in-the-loop workflow details
- Longitudinal evaluation
- Gives 7.5/10 (accept) - **most positive**

**Interpretation:** R3 (ML-for-SE specialist) is most enthusiastic because the human-in-the-loop design and practical deployment considerations are particularly strong from that perspective. R1 and R2 are slightly more cautious due to remaining technical gaps, but all agree the work is acceptable.

---

## Detailed Decision Rationale

### Why ACCEPT (Conditional)?

**1. Substantial Improvement Over Round 1**

The proposal has improved from 4.67/10 (REJECT) to 7.17/10 (CONDITIONAL ACCEPT), a **53% increase**. This demonstrates:
- Authors' responsiveness to feedback
- Serious commitment to addressing concerns
- Ability to execute rigorous research

**2. Critical Concerns Resolved**

All critical issues from Round 1 are now addressed:
- ✅ Theoretical foundations: PAC-style framework added
- ✅ Algorithmic detail: Clear pseudocode provided
- ✅ Presentation: Restructured for NeurIPS format
- ✅ Novelty claims: Clearly distinguished from prior work
- ⚠️ Preliminary experiments: Concrete plan (but no results yet)

**3. Strong Theoretical Contribution**

R1: "Formalizing alert triage as selective prediction with PAC-style bounds is novel and rigorous... This is a strong contribution for NeurIPS."

The theoretical development is now sufficient for NeurIPS. While some details remain (disagreement coefficient, distribution shift), the core framework is solid.

**4. Feasible and Well-Designed Plan**

All reviewers agree the preliminary experiment plan is:
- Concrete (specific datasets, sample sizes, metrics)
- Feasible (8-week timeline is realistic)
- Well-designed (phased approach, appropriate baselines)
- Likely to succeed (expectations are reasonable given recent work)

**5. High Practical Value**

R3: "High potential for industrial adoption with clear ROI... addresses critical trust and reliability concerns."

The problem is important (10-20 min/alarm wasted), the solution is practical (SARIF standardization, cost-benefit analysis), and the impact is clear.

**6. Precedent for Conditional Acceptance**

NeurIPS has precedent for conditional acceptance of strong proposals with preliminary experiment plans, especially when:
- The plan is concrete and feasible
- The authors have demonstrated ability to execute (via quality of revision)
- The contribution is strong (theoretical + practical)
- Preliminary results can be available before camera-ready

### Conditions for Acceptance

**MUST (Required for camera-ready):**

1. **Include preliminary results** (at least 100-1000 Juliet samples)
   - Precision, recall, F1, calibration (ECE), abstention rate
   - Comparison to baseline (evidence-conditioned vs. simple prompting)
   - Demonstrate feasibility and show promise

2. **Fix tool mismatch**
   - Specify Java PathFinder or Symbolic PathFinder for Java
   - Or include C/C++ evaluation with KLEE
   - Correct this technical error

3. **Clarify conformal prediction for text-outputting LLMs**
   - Provide explicit algorithm for constructing prediction sets
   - Define conformity score
   - Discuss exchangeability assumption with project-level clustering

**SHOULD (Strongly recommended for camera-ready):**

4. **Detail constraint extraction**
   - Specify method (symbolic execution? static analysis? AST traversal?)
   - Provide examples
   - Discuss handling of complex Java features

5. **Specify SMT UNKNOWN handling**
   - Add to Algorithm 2: if Z3 returns UNKNOWN, treat as uncertain → abstain
   - Discuss impact on abstention rate

6. **Add noise-robust learning methods**
   - Specify techniques for DZA weak supervision (confident learning, noise adaptation)
   - Validate labels on subset

7. **Specify developer feedback mechanism**
   - Show how feedback is collected and incorporated
   - UI mockup or description

**NICE TO HAVE (Would strengthen but not required):**

8. **Include real-world data in preliminary experiments**
   - 500 DZA samples or 1000 NASCAR samples
   - Show that approach works beyond synthetic Juliet

9. **Add user study plans**
   - Even a small pilot (5-10 developers)
   - Validate human-in-the-loop design

10. **Discuss distribution shift theory**
    - How bounds degrade under cross-project shift
    - Conditions for transferability

### Why Not REJECT?

**Argument for rejection:** "The proposal still has no actual results. For NeurIPS, completed work is expected."

**Counter-argument (Meta-Reviewer's Position):**

1. **Quality of revision demonstrates competence:** The authors have addressed every major concern from Round 1 with rigor and depth. This shows they can execute the plan successfully.

2. **Plan is concrete and feasible:** Unlike Round 1 (vague ideas), Round 2 provides specific algorithms, datasets, timelines, and expected outcomes. Three expert reviewers independently assessed the plan as feasible.

3. **Theoretical contribution is sufficient:** The PAC-style framework for selective prediction is novel and rigorous, even without empirical validation. The theory stands on its own.

4. **Precedent exists:** NeurIPS has accepted papers with strong theoretical contributions and preliminary experiment plans, especially when authors demonstrate competence through revision quality.

5. **Risk is manageable:** The conditions for acceptance (preliminary results before camera-ready) mitigate the risk. If authors cannot deliver, the paper can be withdrawn or moved to poster/workshop.

6. **Practical importance:** The problem is significant, the solution is well-designed, and the potential impact is high. Rejecting this work would delay valuable research.

### Why Not FULL ACCEPT (Without Conditions)?

**Argument for full accept:** "The revision is strong enough. Preliminary results are a minor detail."

**Counter-argument (Meta-Reviewer's Position):**

1. **NeurIPS standard:** Most accepted papers include empirical validation. While theory-only papers exist, they are rare and require exceptional theoretical depth.

2. **Reviewer consensus:** All three reviewers explicitly noted that preliminary results would raise their scores to 8/10. Their conditional acceptance reflects this expectation.

3. **Feasibility validation:** Even a small pilot (100 samples) would validate that the approach works in practice, not just in theory. Without this, there's risk that implementation reveals unforeseen challenges.

4. **Community expectation:** Readers expect to see at least preliminary empirical evidence in ML papers. A theory-only paper on a practical problem (alert triage) would be unusual.

**Conclusion:** Conditional acceptance is the right balance - it recognizes the strong revision while maintaining NeurIPS standards for empirical validation.

---

## Comparison to NeurIPS Standards

### Typical NeurIPS Contributions

Strong NeurIPS papers typically include:
1. **Novel algorithms with theoretical analysis** ✅ EVICT has this (selective prediction framework)
2. **Significant empirical improvements on established benchmarks** ⚠️ EVICT has a plan but no results yet
3. **New problem formulations with broad applicability** ✅ EVICT formalizes alert triage as selective prediction
4. **Theoretical insights that advance understanding** ✅ EVICT provides PAC-style bounds for code analysis

### EVICT's Fit (Round 2)

**Strengths:**
- ✅ Novel theoretical framework (selective prediction for alert triage)
- ✅ Rigorous formalization (PAC-style bounds, cost-sensitive learning)
- ✅ Clear algorithmic specifications
- ✅ Comprehensive evaluation design
- ⚠️ Preliminary experiment plan (but no results yet)

**Comparison to Accepted NeurIPS Papers:**

**Theory-heavy papers (e.g., "On the Foundations of Noise-free Selective Classification"):**
- Strong theoretical contributions with minimal empirics
- EVICT's theory is solid but not as deep as pure theory papers
- Would benefit from empirical validation

**Applied ML papers (e.g., "Learning to Reduce False Positives in Analytic Bug Detectors"):**
- Strong empirical results with moderate theory
- EVICT has strong theory but limited empirics (plan only)
- Needs preliminary results to fit this category

**Hybrid papers (e.g., "Classification with Rejection Based on Cost-sensitive Classification"):**
- Combines theory and empirics
- EVICT aims for this category
- Needs to deliver on empirical plan

**Conclusion:** EVICT is a **hybrid paper** (theory + application) that fits NeurIPS standards, but needs preliminary empirical results to be complete. Conditional acceptance is appropriate.

---

## Recommendations for Camera-Ready

### Critical (Must Address)

1. **Include Preliminary Results:**
   - Minimum: 100-1000 Juliet samples
   - Metrics: Precision, recall, F1, calibration (ECE), abstention rate
   - Comparison: Evidence-conditioned vs. baseline prompting
   - Expected: Precision 85-95%, ECE <0.1, abstention 10-20%
   - Timeline: Can be completed in 4-6 weeks

2. **Fix Tool Mismatch:**
   - Change "KLEE" to "Java PathFinder (JPF)" or "Symbolic PathFinder (SPF)" for Java
   - Or add C/C++ evaluation with KLEE
   - This is a technical error that undermines credibility

3. **Clarify Conformal Prediction:**
   - Algorithm for text-outputting LLMs
   - Conformity score definition
   - Exchangeability assumption discussion

### Important (Should Address)

4. **Detail Constraint Extraction:**
   - Method specification (symbolic execution? static analysis?)
   - Examples for complex Java code
   - Fallback strategies

5. **Specify SMT UNKNOWN Handling:**
   - Add to Algorithm 2
   - Discuss impact on abstention rate

6. **Add Noise-Robust Learning:**
   - Techniques for DZA weak supervision
   - Label validation strategy

7. **Specify Developer Feedback Mechanism:**
   - UI description or mockup
   - Feedback collection and incorporation process

### Recommended (Would Strengthen)

8. **Include Real-World Data:**
   - 500 DZA or 1000 NASCAR samples in preliminary experiments
   - Compare synthetic vs. real-world patterns

9. **Add User Study Plans:**
   - Small pilot with 5-10 developers
   - Validate human-in-the-loop design

10. **Discuss Distribution Shift:**
    - How bounds degrade under cross-project shift
    - Conditions for transferability

### Timeline for Camera-Ready

Assuming conditional acceptance at NeurIPS 2026 (notification in September):

**Weeks 1-4 (September):**
- Conduct preliminary experiments (1000 Juliet samples)
- Implement evidence-conditioned prompting + baseline
- Measure precision, calibration, abstention rate

**Weeks 5-6 (October):**
- Fix tool mismatch (specify JPF)
- Clarify conformal prediction algorithm
- Detail constraint extraction
- Specify SMT UNKNOWN handling

**Weeks 7-8 (October):**
- Add noise-robust learning methods
- Specify developer feedback mechanism
- Polish presentation
- Prepare camera-ready submission

**Week 9 (October):**
- Final review and submission

**Feasibility:** This timeline is tight but achievable. The preliminary experiments are the most time-consuming part (4 weeks), but the plan is concrete and the authors have demonstrated competence through the quality of revision.

---

## Final Decision

**Decision: CONDITIONAL ACCEPT**

**Conditions:**
1. **MUST include preliminary results** (100-1000 Juliet samples) before camera-ready
2. **MUST fix tool mismatch** (specify JPF for Java or add C/C++ evaluation)
3. **MUST clarify conformal prediction** for text-outputting LLMs

**Recommendation:**
- If conditions are met: **ACCEPT** for main conference track
- If conditions are partially met: **ACCEPT** for poster track
- If conditions are not met: **REJECT** (resubmit next cycle)

**Rationale:**

This revised proposal demonstrates **substantial improvement** over the original submission, with all critical concerns from Round 1 addressed. The theoretical foundations are now rigorous (PAC-style framework), the algorithmic specifications are clear (Algorithms 1-3), the presentation is vastly improved (9-page format with visual elements), and the novelty claims are sharpened (clear distinction from prior work).

The main remaining limitation is the lack of actual preliminary results. However, all three reviewers agree that the preliminary experiment plan is concrete, feasible, and well-designed, and that the authors have demonstrated competence through the quality of revision. Given the strong theoretical contribution, the practical importance of the problem, and the feasibility of the plan, **conditional acceptance is appropriate**.

The conditions for acceptance (preliminary results, tool mismatch fix, conformal prediction clarification) are achievable within the camera-ready timeline (8-9 weeks). If the authors deliver on these conditions, the paper will be a strong contribution to NeurIPS.

**Confidence: 4.5/5 (Very High Confidence)**

This decision is based on:
- Three independent expert reviews with consensus (7, 7, 7.5/10)
- Clear evidence of substantial improvement (+2.5 points, 53% increase)
- Strong theoretical contribution (selective prediction framework)
- Feasible preliminary experiment plan
- Precedent for conditional acceptance at NeurIPS

The main uncertainty is whether the authors can execute the preliminary experiments successfully within the camera-ready timeline. However, based on the quality of revision and the feasibility of the plan, I am confident this is achievable.

---

## Message to Authors

Congratulations on the substantial improvement in your proposal! The revision demonstrates strong responsiveness to feedback and scientific rigor. All three reviewers recognize that you have addressed the critical concerns from the first review.

**Your strongest contributions are:**
1. **Theoretical framework:** Formalizing alert triage as selective prediction with PAC-style bounds is novel and valuable
2. **Human-in-the-loop design:** Explicit modeling of calibrated abstention enables safe automation
3. **Practical value:** Addresses a significant industrial problem with clear ROI

**To ensure acceptance, you MUST:**
1. Include preliminary results (100-1000 Juliet samples) showing precision, calibration, and abstention rate
2. Fix the tool mismatch (specify JPF for Java, not KLEE)
3. Clarify how conformal prediction works for text-outputting LLMs

**We strongly recommend:**
- Detailing constraint extraction methodology
- Specifying SMT UNKNOWN handling
- Adding noise-robust learning methods for weak supervision
- Including real-world data (DZA or NASCAR) in preliminary experiments

With these improvements, your paper will be a strong contribution to NeurIPS. We look forward to seeing the completed work.

**Timeline:** You have approximately 8-9 weeks from notification to camera-ready. We recommend:
- Weeks 1-4: Conduct preliminary experiments
- Weeks 5-6: Address technical issues (tool mismatch, conformal prediction, etc.)
- Weeks 7-8: Polish presentation and prepare camera-ready
- Week 9: Final review and submission

Good luck with the revisions!

---

## Comparison to Alternative Venues

If the authors cannot complete preliminary experiments in time, alternative venues include:

**1. ICSE 2027 (International Conference on Software Engineering)**
- Deadline: August 2026
- More time for experiments (6+ months)
- More receptive to systems contributions
- Accepts longer papers (up to 11 pages)
- Strong fit for ML-for-SE work

**2. FSE 2026 (Foundations of Software Engineering)**
- Deadline: March 2026
- Emphasis on practical SE tools
- Values comprehensive evaluation
- Good fit for EVICT's practical focus

**3. ASE 2026 (Automated Software Engineering)**
- Deadline: April 2026
- Focus on automation and tool support
- Receptive to ML-based SE tools
- Good fit for EVICT

**4. NeurIPS 2026 Workshops**
- Multiple relevant workshops (e.g., ML for Systems, AI for Code)
- Lower bar for preliminary work
- Good venue for getting feedback

**5. ArXiv + Journal Extension**
- Post to ArXiv immediately to establish priority
- Extend to journal (e.g., TOSEM, TSE, EMSE) with full evaluation
- Longer timeline allows comprehensive study

**Recommendation:** Given the quality of the revision, I strongly recommend completing the preliminary experiments and submitting to NeurIPS 2026. The work is very close to acceptance, and the preliminary experiments are achievable in 4-6 weeks. If timing is tight, ICSE 2027 is an excellent alternative with more time for comprehensive evaluation.
