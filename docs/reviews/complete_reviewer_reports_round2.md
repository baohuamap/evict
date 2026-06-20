# Complete Reviewer Reports - Round 2 (Fresh Reviews)

## Meta-Review Summary

**Decision**: **CONDITIONAL ACCEPT**  
**Average Score**: 7.17/10 (up from 4.67/10 in Round 1)  
**Improvement**: +2.5 points (53% increase)

### Reviewer Scores

| Reviewer | Expertise | Score | Recommendation |
|----------|-----------|-------|----------------|
| **Reviewer 1** | Calibration & Statistical Learning Theory | 7/10 | Accept, but needs revisions |
| **Reviewer 2** | Program Analysis & Neuro-Symbolic Systems | 7/10 | Accept, but needs revisions |
| **Reviewer 3** | ML for Software Engineering & Human-AI Collaboration | 7.5/10 | Accept |

### Key Findings

**✅ MAJOR IMPROVEMENTS (All Critical Issues Addressed):**
1. **Theoretical foundations added** - PAC-style framework with formal definitions
2. **Preliminary experiment plan** - Concrete, phased, feasible (8 weeks)
3. **Algorithmic specifications** - Clear pseudocode for all components
4. **Presentation vastly improved** - 9-page format with visual elements
5. **Novelty claims sharpened** - Clear distinction from prior work

**⚠️ REMAINING GAPS (Must Address for Camera-Ready):**
1. **No actual preliminary results yet** - Still a plan, not completed work
2. **Minor technical issues** - Tool mismatch (KLEE→JPF), conformal prediction details
3. **User studies missing** - Important for human-in-the-loop validation

**📊 PROBABILITY OF FINAL ACCEPTANCE:**
- **With conditions met** (preliminary results + fixes): 85-90%
- **Partial conditions** (only fixes, no results): 50-60%
- **Conditions not met**: 10-20%

---

## Reviewer 1: Calibration & Statistical Learning Theory Specialist

### Overall Assessment
> "Substantial improvement... addresses all critical concerns. The addition of formal selective prediction theory is the most significant enhancement."

### Scores
- **Soundness**: 4/5 (up from 2/5)
- **Presentation**: 4.5/5 (up from 3/5)
- **Contribution**: 4/5 (up from 2.5/5)
- **Overall**: 7/10 (Accept, but needs revisions)
- **Confidence**: 4/5

### Key Strengths

1. **Theoretical Foundations (Major Improvement)**
   - PAC-style framework with formal definitions
   - Risk formulation: R(h,g) = α·R_FN + β·R_FP + γ·R_abstain
   - Coverage bounds: P(g(x)=1) ≥ 1-δ
   - Risk bounds: R(h,g) ≤ ε with high probability
   - Conformal prediction integration
   - References to foundational work (El-Yaniv, Geifman, Vovk)

2. **Algorithmic Detail (Significant Improvement)**
   - Algorithm 1: EvidencePack construction
   - Algorithm 2: Calibrated selective triage
   - Algorithm 3: Contrastive FP learning
   - Clear pseudocode, implementable

3. **Preliminary Experiments (Addresses Critical Gap)**
   - Phase 1: 1000 Juliet samples (weeks 1-4)
   - Phase 2: 5000 samples + LLM4FPM comparison (weeks 5-8)
   - Feasible timeline, realistic expectations

### Remaining Concerns

1. **Still No Actual Results** (Critical)
   > "Even 100-sample pilot results would strengthen enormously. With preliminary results, it's a clear accept (8/10)."

2. **Theoretical Gaps** (Minor)
   - Disagreement coefficient not defined for alert triage
   - Distribution shift theory (how bounds degrade)
   - Conformal prediction details for text-outputting LLMs

3. **Algorithmic Details** (Minor)
   - Constraint extraction ("extract branch conditions" - how exactly?)
   - Optimal threshold selection algorithm not fully specified

### Questions from Reviewer 1

1. Do you have any preliminary results yet, even on 10-100 samples?
2. How exactly do you apply conformal prediction when the LLM outputs text (TP/FP/ABSTAIN) rather than probabilities?
3. How do your theoretical guarantees degrade under cross-project distribution shift?
4. Can you define the disagreement coefficient for alert triage?
5. What is the computational complexity of your approach?

### Conditions for Acceptance

**MUST:**
- Include preliminary results (100-1000 samples) before camera-ready
- Clarify conformal prediction for text-outputting LLMs

**SHOULD:**
- Discuss distribution shift theory
- Define disagreement coefficient
- Provide complexity analysis

### Rating Justification
> "This is a borderline case. With preliminary results, it's a clear accept (8/10). Without results, it's a conditional accept (6/10). I'm giving 7/10 assuming results will be available before camera-ready."

---

## Reviewer 2: Program Analysis & Neuro-Symbolic Systems Specialist

### Overall Assessment
> "Substantial improvement... technical approach is sound. The neuro-symbolic integration is well-designed with clear decision logic and appropriate tool choices."

### Scores
- **Soundness**: 4/5 (up from 2.5/5)
- **Presentation**: 4/5 (up from 3.5/5)
- **Contribution**: 4/5 (up from 3/5)
- **Overall**: 7/10 (Accept, but needs revisions)
- **Confidence**: 4/5

### Key Strengths

1. **Evidence Extraction (Well-Specified)**
   - Clear algorithmic specification (Algorithm 1)
   - SARIF standardization enables cross-tool compatibility
   - Leverages analyzer's existing evidence (flow traces)
   - Handles missing evidence via progressive prompting

2. **Neuro-Symbolic Integration (Major Improvement)**
   - Clear decision rule: invoke when uncertain or high-severity
   - Appropriate tools: Z3 (SMT), KLEE/JPF (symbolic execution)
   - Concrete limits: 10s timeout, 2GB memory, depth ≤50, max 100 paths
   - Auditable certificates with counterexamples

3. **Practical Deployment Considerations**
   - Lightweight verification (10s timeout)
   - Cost-benefit analysis
   - SARIF cross-tool evaluation
   - Industrial grounding (Tencent study, ROI metrics)

### Remaining Concerns

1. **Tool Mismatch** (Technical Error - Must Fix)
   > "KLEE is for C/C++, but NASCAR and CWE-Bench-Java are Java. The proposal should specify Java PathFinder or Symbolic PathFinder for Java."

2. **Constraint Extraction Details** (Vague)
   - "Extract branch conditions" - how exactly?
   - Via symbolic execution? Static analysis? AST traversal?
   - For complex Java (generics, lambdas, reflection), this is non-trivial

3. **SMT UNKNOWN Handling** (Not Specified)
   - Z3 often returns UNKNOWN (timeout, undecidable theory)
   - How does this affect the decision? Treat as uncertain? Abstain?

4. **Contrastive Learning Validation** (Untested)
   - Assumes FP patterns transfer across projects (untested)
   - No preliminary analysis of pattern consistency
   - Should include experiments showing transferability

### Questions from Reviewer 2

1. Do you have any preliminary results, even on 50-100 samples?
2. For Java, will you use Java PathFinder instead of KLEE?
3. How exactly do you extract branch conditions (Algorithm 1, Line 8)?
4. How do you handle Z3 returning UNKNOWN?
5. Do you have evidence that FP patterns are consistent across projects?
6. Will Phase 1 or 2 include real-world data (DZA, NASCAR)?

### Conditions for Acceptance

**MUST:**
- Fix tool mismatch (specify JPF for Java or include C/C++ evaluation)

**SHOULD:**
- Include preliminary results (50-100 samples) before camera-ready
- Detail constraint extraction methodology
- Specify SMT UNKNOWN handling

### Rating Justification
> "The technical approach is sound. The main concerns are the tool mismatch (technical error) and lack of actual results. With these addressed, this is a strong contribution."

---

## Reviewer 3: ML for Software Engineering & Human-AI Collaboration Specialist

### Overall Assessment
> "Major improvement... approach is sound and valuable. The human-in-the-loop design with calibrated abstention is the strongest contribution."

### Scores
- **Soundness**: 4.5/5 (up from 3/5)
- **Presentation**: 4.5/5 (up from 2.5/5)
- **Contribution**: 4/5 (up from 3/5)
- **Overall**: 7.5/10 (Accept)
- **Confidence**: 4/5

### Key Strengths

1. **Human-in-the-Loop Design (Major Improvement)**
   - Three-way decision: TP, FP, ABSTAIN
   - Cost-sensitive formulation: R(h,g) = α·R_FN + β·R_FP + γ·R_abstain
   - Calibrated confidence (multiple methods)
   - Safety-conscious (abstain when uncertain)

2. **Practical Feasibility (Significant Improvement)**
   - Lightweight verification (10s timeout, 2GB memory)
   - SARIF standardization (reduces integration effort)
   - Clear cost-benefit analysis (10-20 min/alarm manually → seconds with EVICT)
   - ROI is clear if precision is high

3. **Realistic Evaluation**
   - Multiple datasets: NASCAR (1M warnings), DZA (differential), CWE-Bench-Java (validated), Juliet (synthetic)
   - Reflects real SE tasks (actionability, bug fixes, vulnerabilities)
   - Honest about dataset limitations

4. **Excellent Presentation**
   - Clear structure, visual elements
   - Precise terminology (no vague language)
   - Honest about limitations
   - Appropriate for 9-page NeurIPS format

### Remaining Concerns

1. **User Studies Missing** (Important)
   - No plans for developer studies to validate decisions
   - No evaluation of whether developers trust and use abstention appropriately
   - No assessment of developer satisfaction or workflow impact

2. **Developer Feedback Mechanism Not Specified**
   - Algorithm 2, Line 12 mentions "collect feedback" but doesn't show how
   - How is feedback validated? Incorporated into model updates?
   - What if developers disagree with EVICT's decisions?

3. **Abstention Rate Validation**
   - Expected 10-20% abstention. Is this acceptable to developers?
   - Too high may reduce adoption; too low may miss uncertain cases
   - No user research to validate this range

4. **No Longitudinal Evaluation**
   - How does EVICT perform over time as codebases evolve?
   - Do developers continue to trust it?
   - Does performance degrade (concept drift)?

### Questions from Reviewer 3

1. Do you have any preliminary results, even on 10-50 samples?
2. Do you plan to conduct user studies with developers? When and how?
3. How will developer feedback be collected, validated, and incorporated?
4. Is 10-20% abstention acceptable to developers? Have you validated this?
5. How will you evaluate EVICT over time (3-6 months)?
6. How much engineering effort is required to integrate EVICT?
7. What is human precision/recall on these tasks? How close does EVICT get?

### Conditions for Acceptance

**SHOULD:**
- Include preliminary results (50-100 samples) before camera-ready
- Add user study plans (even small pilot with 5-10 developers)
- Specify developer feedback mechanism

### Rating Justification
> "From an ML-for-SE perspective, the human-in-the-loop design and practical deployment considerations are particularly strong. While preliminary results would strengthen the work, the plan is concrete enough that I believe the authors can execute it successfully."

**Why higher score than other reviewers:**
> "The explicit modeling of human review cost and calibrated abstention addresses critical trust and reliability concerns. This is the strongest contribution for ML-for-SE."

---

## Consensus Across All Reviewers

### Areas of Agreement

**✅ STRENGTHS (All Reviewers Agree):**
1. Substantial improvement over Round 1 (all critical concerns addressed)
2. Theoretical foundations now rigorous (PAC-style framework)
3. Algorithmic specifications clear and implementable
4. Presentation vastly improved (9-page format, visual elements)
5. Novelty claims sharpened (clear distinction from prior work)
6. Preliminary experiment plan concrete and feasible
7. Practical value high (addresses real industrial problem)
8. Responsive to feedback (authors took first review seriously)

**⚠️ REMAINING CONCERNS (All Reviewers Agree):**
1. No actual preliminary results yet (still a roadmap, not completed work)
2. Minor technical gaps (conformal prediction details, constraint extraction, SMT UNKNOWN, tool mismatch)
3. Label quality acknowledged but no concrete noise-robust methods
4. User studies missing (important for human-in-the-loop work)

**📋 CONSENSUS RECOMMENDATION:**
- All three reviewers recommend **ACCEPT** (with conditions)
- All agree preliminary results would strengthen (raise scores to 8/10)
- All agree the plan is concrete enough to warrant conditional acceptance

### Areas of Disagreement (Minor)

**Reviewer 1 (Theory)** most concerned about:
- Conformal prediction details for text-outputting LLMs
- Distribution shift theory (how bounds degrade)
- Disagreement coefficient definition

**Reviewer 2 (Systems)** most concerned about:
- Tool mismatch (KLEE for C/C++ vs. Java focus)
- Constraint extraction details
- SMT UNKNOWN handling

**Reviewer 3 (ML-SE)** most concerned about:
- User studies and developer feedback
- Human-in-the-loop workflow details
- Longitudinal evaluation

**Interpretation:**
R3 is most enthusiastic (7.5/10) because the human-in-the-loop design is particularly strong from an ML-SE perspective. R1 and R2 are slightly more cautious (7/10) due to remaining technical gaps, but all agree the work is acceptable.

---

## Conditions for Final Acceptance

### MUST Address (Required for Camera-Ready)

1. **Include Preliminary Results** ⚠️ CRITICAL
   - Minimum: 100-1000 Juliet samples
   - Metrics: Precision, recall, F1, calibration (ECE), abstention rate
   - Comparison: Evidence-conditioned vs. baseline prompting
   - Expected: Precision 85-95%, ECE <0.1, abstention 10-20%
   - **Timeline**: 4-6 weeks
   - **Impact**: Would raise scores to 8/10

2. **Fix Tool Mismatch** 🔧 TECHNICAL ERROR
   - Change "KLEE" to "Java PathFinder (JPF)" for Java
   - Or add C/C++ evaluation with KLEE
   - **Timeline**: 1 day
   - **Impact**: Corrects credibility issue

3. **Clarify Conformal Prediction** 📐 THEORETICAL GAP
   - Algorithm for text-outputting LLMs
   - Conformity score definition
   - Exchangeability assumption discussion
   - **Timeline**: 1 week
   - **Impact**: Completes theoretical framework

### SHOULD Address (Strongly Recommended)

4. **Detail Constraint Extraction**
   - Method specification (symbolic execution? AST traversal?)
   - Examples for complex Java code
   - Fallback strategies
   - **Timeline**: 1 week

5. **Specify SMT UNKNOWN Handling**
   - Add to Algorithm 2
   - Discuss impact on abstention rate
   - **Timeline**: 1 day

6. **Add Noise-Robust Learning Methods**
   - Techniques for DZA weak supervision (confident learning)
   - Label validation strategy
   - **Timeline**: 1 week

7. **Specify Developer Feedback Mechanism**
   - UI description or mockup
   - Feedback collection and incorporation
   - **Timeline**: 3 days

### NICE TO HAVE (Would Strengthen)

8. **Include Real-World Data**
   - 500 DZA or 1000 NASCAR samples
   - Compare synthetic vs. real patterns
   - **Timeline**: +2 weeks

9. **Add User Study Plans**
   - Small pilot with 5-10 developers
   - Validate human-in-the-loop design
   - **Timeline**: 2 weeks

10. **Discuss Distribution Shift Theory**
    - How bounds degrade under cross-project shift
    - Conditions for transferability
    - **Timeline**: 1 week

---

## Timeline to Camera-Ready (8-9 Weeks)

### Weeks 1-4: Preliminary Experiments ⚠️ CRITICAL
- [ ] Week 1: Setup Juliet dataset (1000 samples)
- [ ] Week 2: Implement evidence-conditioned prompting + baseline
- [ ] Week 3: Run experiments, measure metrics
- [ ] Week 4: Analyze results, create tables/figures

**Deliverable**: Actual preliminary results

### Weeks 5-6: Technical Fixes
- [ ] Week 5: Fix tool mismatch (KLEE→JPF), clarify conformal prediction
- [ ] Week 6: Detail constraint extraction, specify SMT UNKNOWN handling

**Deliverable**: Technical issues resolved

### Weeks 7-8: Enhancements
- [ ] Week 7: Add noise-robust learning, developer feedback mechanism
- [ ] Week 8: Polish presentation, create all figures/tables

**Deliverable**: Camera-ready draft

### Week 9: Final Review
- [ ] Internal review and revision
- [ ] Check all conditions met
- [ ] Submit camera-ready

**Deliverable**: Final submission

---

## Key Takeaways for Authors

### What You Did Right ✅

1. **Responded systematically to every concern** from Round 1
2. **Added rigorous theoretical foundations** (PAC-style framework)
3. **Provided concrete algorithms** (Algorithms 1-3 with pseudocode)
4. **Restructured for conference format** (9 pages with visuals)
5. **Created feasible preliminary experiment plan** (8 weeks, phased)
6. **Sharpened novelty claims** (clear distinction from prior work)
7. **Demonstrated competence** through quality of revision

### What You Need to Do Now 🎯

1. **PRIORITY 1**: Conduct preliminary experiments (100-1000 Juliet samples)
   - This is the #1 thing all reviewers want to see
   - Would raise scores from 7/10 to 8/10
   - Demonstrates feasibility and validates approach

2. **PRIORITY 2**: Fix tool mismatch (KLEE→JPF)
   - Simple technical correction
   - Takes 1 day but critical for credibility

3. **PRIORITY 3**: Clarify conformal prediction algorithm
   - Complete the theoretical framework
   - Addresses R1's main remaining concern

4. **PRIORITY 4**: Add user study plans
   - Important for ML-SE work (R3's main concern)
   - Even small pilot (5-10 developers) would help

### Your Path to Acceptance 🚀

**Current Status**: CONDITIONAL ACCEPT (7.17/10)

**With conditions met**:
- **Probability**: 85-90% acceptance
- **Expected score**: 8-8.5/10
- **Track**: Main conference

**Timeline**: 8-9 weeks to camera-ready is tight but achievable

**Confidence**: All three reviewers believe you can execute this successfully based on the quality of your revision

---

## Comparison: Round 1 vs Round 2

| Metric | Round 1 | Round 2 | Change |
|--------|---------|---------|--------|
| **Average Score** | 4.67/10 | 7.17/10 | +2.5 (+53%) |
| **Decision** | REJECT | CONDITIONAL ACCEPT | ✅ Success |
| **Soundness** | 2.5/5 | 4.17/5 | +1.67 (+67%) |
| **Presentation** | 3/5 | 4.33/5 | +1.33 (+44%) |
| **Contribution** | 2.83/5 | 4/5 | +1.17 (+41%) |
| **Theoretical Foundations** | ❌ Missing | ✅ PAC framework | Major improvement |
| **Preliminary Experiments** | ❌ None | ⚠️ Plan only | Substantial improvement |
| **Algorithmic Detail** | ❌ Vague | ✅ Clear pseudocode | Resolved |
| **Presentation** | ❌ 12 pages, no visuals | ✅ 9 pages, 8 figures | Resolved |
| **Novelty Claims** | ❌ Overstated | ✅ Clear, honest | Resolved |

---

## Final Recommendation from Meta-Reviewer

**Decision**: **CONDITIONAL ACCEPT**

**Rationale**:
> "This revised proposal demonstrates substantial improvement over the original submission, with all critical concerns from Round 1 addressed. The theoretical foundations are now rigorous (PAC-style framework), the algorithmic specifications are clear (Algorithms 1-3), the presentation is vastly improved (9-page format with visual elements), and the novelty claims are sharpened (clear distinction from prior work).

> The main remaining limitation is the lack of actual preliminary results. However, all three reviewers agree that the preliminary experiment plan is concrete, feasible, and well-designed, and that the authors have demonstrated competence through the quality of revision. Given the strong theoretical contribution, the practical importance of the problem, and the feasibility of the plan, conditional acceptance is appropriate."

**Confidence**: 4.5/5 (Very High Confidence)

**Message to Authors**:
> "Congratulations on the substantial improvement! Your strongest contributions are: (1) Theoretical framework for selective prediction in alert triage, (2) Human-in-the-loop design with calibrated abstention, (3) Practical value addressing significant industrial problem.

> To ensure acceptance, you MUST: (1) Include preliminary results (100-1000 Juliet samples), (2) Fix the tool mismatch (specify JPF for Java), (3) Clarify conformal prediction for text-outputting LLMs.

> With these improvements, your paper will be a strong contribution to NeurIPS. We look forward to seeing the completed work."

---

## Contact & Resources

**Generated Artifacts**:
- Meta-review: `/home/sandbox/meta_review_v2.md`
- Reviewer 1 report: `/home/sandbox/reviewer_1_report_v2.md`
- Reviewer 2 report: `/home/sandbox/reviewer_2_report_v2.md`
- Reviewer 3 report: `/home/sandbox/reviewer_3_report_v2.md`
- Review comparison: `/home/sandbox/review_comparison_summary.md`
- This complete report: `/home/sandbox/complete_reviewer_reports_round2.md`

**Previous Round**:
- Original meta-review: `/home/sandbox/meta_review.md`
- Original reviews: `reviewer_1_report.md`, `reviewer_2_report.md`, `reviewer_3_report.md`

**Improved Proposal**:
- Full document: `/home/sandbox/improved_evict_proposal.md`
- Quick reference: `/home/sandbox/quick_reference_improvements.md`
