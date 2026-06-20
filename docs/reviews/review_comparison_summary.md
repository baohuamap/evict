# EVICT Proposal: Review Comparison Summary (Round 1 vs Round 2)

## 🎯 Bottom Line

**Round 1 (Original Proposal)**: **REJECT** - Average score 4.67/10  
**Round 2 (Improved Proposal)**: **CONDITIONAL ACCEPT** - Average score 7.17/10  

**Improvement**: +2.5 points (53% increase) 🚀

---

## 📊 Score Comparison

| Aspect | Round 1 Score | Round 2 Score | Improvement |
|--------|---------------|---------------|-------------|
| **Reviewer 1** | 4/10 (Weak Reject) | 7/10 (Accept w/ revisions) | +3 points |
| **Reviewer 2** | 5/10 (Borderline Reject) | 7/10 (Accept w/ revisions) | +2 points |
| **Reviewer 3** | 5/10 (Borderline Reject) | 7.5/10 (Accept) | +2.5 points |
| **Average** | **4.67/10** | **7.17/10** | **+2.5 points** |
| **Decision** | **REJECT** | **CONDITIONAL ACCEPT** | ✅ **Success!** |

---

## 🔄 Critical Issues: Before & After

### Issue 1: Theoretical Foundations

**Round 1 (CRITICAL GAP):**
> "No formal definitions of risk, coverage, or optimality criteria... no theoretical guarantees or bounds... For NeurIPS, this is a critical gap." - R1 (2/5 soundness)

**Round 2 (RESOLVED):**
> "The addition of formal selective prediction theory is the most significant enhancement... PAC-style framework with formal definitions... This is a strong contribution for NeurIPS." - R1 (4/5 soundness)

**Status**: ✅ **RESOLVED** (+2 points on soundness)

**What Changed:**
- Added PAC-style framework with predictor-rejector formulation
- Formal risk definition: R(h,g) = α·R_FN + β·R_FP + γ·R_abstain
- Coverage bounds: P(g(x)=1) ≥ 1-δ
- Risk bounds: R(h,g) ≤ ε with high probability
- Conformal prediction integration for distribution-free guarantees
- References to foundational work (El-Yaniv, Geifman, Vovk, Angelopoulos)

**Remaining Minor Gaps:**
- Disagreement coefficient definition for alert triage
- Distribution shift theory (how bounds degrade)
- Conformal prediction details for text-outputting LLMs

---

### Issue 2: Preliminary Experiments

**Round 1 (MOST SIGNIFICANT BARRIER):**
> "No preliminary results... entirely prospective without even pilot experiments... For NeurIPS, preliminary results are essential." - All Reviewers

**Round 2 (SUBSTANTIALLY IMPROVED):**
> "The phased preliminary experiment plan is concrete and feasible... Phase 1: 1000 Juliet samples, Phase 2: 5000 samples + LLM4FPM comparison... This addresses the most critical weakness from the first review." - R2

**Status**: ⚠️ **SUBSTANTIALLY IMPROVED, BUT INCOMPLETE**

**What Changed:**
- **Phase 1 (Weeks 1-4)**: 1000 Juliet samples, evidence-conditioned vs. baseline
- **Phase 2 (Weeks 5-8)**: 5000 samples, contrastive learning, LLM4FPM comparison
- **Expected outcomes**: Precision 85-95%, ECE <0.1, abstention 10-20%
- **Feasible timeline**: 8 weeks is realistic
- **Appropriate baseline**: LLM4FPM chosen for comparison

**What's Still Missing:**
- **No actual results yet** - still a plan, not completed work
- All reviewers want to see at least 100-1000 sample pilot results

**Reviewer Consensus:**
- "With preliminary results, it's a clear accept (8/10)" - R1
- "Even 50-100 samples would strengthen significantly" - R2
- "Even 50-100 sample pilot results would strengthen enormously" - R3

---

### Issue 3: Algorithmic Detail

**Round 1 (INSUFFICIENT):**
> "Key components lack precise specifications... vague descriptions... no pseudocode... making it difficult to assess technical soundness or reproducibility." - R1 & R2

**Round 2 (RESOLVED):**
> "Algorithms 1-3 provide precise pseudocode that could be implemented... Algorithm 1 (EvidencePack construction) is now well-specified... Clear algorithmic specification." - R2 (4/5 soundness)

**Status**: ✅ **RESOLVED**

**What Changed:**
- **Algorithm 1**: EvidencePack construction (slicing, flow extraction, constraints)
- **Algorithm 2**: Calibrated selective triage (LLM verification, confidence, symbolic invocation)
- **Algorithm 3**: Contrastive FP learning (InfoNCE loss, hard-negative mining)
- All with clear pseudocode and step-by-step logic

**Remaining Minor Gaps:**
- Constraint extraction details ("extract branch conditions" - how exactly?)
- SMT UNKNOWN handling not specified
- Optimal threshold selection algorithm

---

### Issue 4: Presentation

**Round 1 (EXCESSIVE LENGTH, MISSING VISUALS):**
> "~12 pages vs. 9-page NeurIPS limit... missing visual elements... vague terminology... unclear problem formulation." - All Reviewers (2.5-3.5/5)

**Round 2 (VASTLY IMPROVED):**
> "The presentation is vastly improved... Clear structure, visual elements added, precise terminology, formal notation, appropriate length for 9-page NeurIPS format." - R3 (4.5/5)

**Status**: ✅ **RESOLVED** (+1.5-2 points on presentation)

**What Changed:**
- **Structure**: 9-page NeurIPS format with supplementary material
- **Visual elements**: Architecture diagram, risk-coverage curves, calibration plots, example EvidencePack
- **Precise terminology**: "lightweight" (10s timeout, 2GB), "targeted" (depth ≤50, max 100 paths)
- **Formal notation**: Consistent use of h, g, R throughout
- **Clear problem formulation**: Selective prediction as primary objective

**Remaining Minor Gaps:**
- Example prompts missing (can go in supplementary)
- UI mockups for human-in-the-loop
- Complexity analysis

---

### Issue 5: Novelty Claims

**Round 1 (OVERSTATED):**
> "Evidence-conditioned verification is presented as novel, but multiple recent systems already use this approach... should more clearly distinguish EVICT's contributions." - All Reviewers

**Round 2 (MUCH CLEARER):**
> "The proposal now clearly distinguishes EVICT from recent systems... vs. LLM4FPM: EVICT adds selective prediction... vs. LLM4PFA: EVICT adds formal guarantees... This is much clearer than the original proposal." - R3

**Status**: ✅ **RESOLVED**

**What Changed:**
- **Clear comparison table**: EVICT vs. LLM4FPM, LLM4PFA, BugLens, AdaTaint
- **Honest acknowledgment**: Evidence-based reasoning is established
- **Focus on genuine novelty**: Selective prediction framework as primary contribution
- **Explicit distinctions**: What each system does and how EVICT differs

**Primary Novel Contribution (Now Clear):**
> "EVICT is the first LLM-based static analysis system with formal selective prediction guarantees (PAC bounds on selective risk, conformal finite-sample error control)."

---

### Issue 6: Label Quality

**Round 1 (NOT ADDRESSED):**
> "All datasets have known problems... proposal only acknowledges without proposing solutions." - All Reviewers

**Round 2 (ACKNOWLEDGED BUT INCOMPLETE):**
> "Acknowledges label issues but doesn't propose concrete solutions... 'Treat DZA as weak supervision' - but what noise-robust methods?" - R2

**Status**: ⚠️ **ACKNOWLEDGED BUT NOT FULLY RESOLVED**

**What Changed:**
- Explicit acknowledgment of label quality issues
- Mentions "weak supervision" for DZA
- Emphasizes leakage-resistant protocols (deduplication, project splits)

**What's Still Missing:**
- Concrete noise-robust learning methods (confident learning, noise adaptation)
- Label validation strategy (fuzzing, manual auditing)

**Reviewer Suggestions:**
- Use noise-robust methods (confident learning, noise adaptation layer)
- Validate labels on subset
- Report experiments with varying noise levels

---

## 📈 Detailed Score Breakdown

### Soundness

| Reviewer | Round 1 | Round 2 | Improvement | Key Driver |
|----------|---------|---------|-------------|------------|
| R1 (Theory) | 2/5 | 4/5 | +2 | PAC-style framework added |
| R2 (Systems) | 2.5/5 | 4/5 | +1.5 | Clear algorithms & neuro-symbolic integration |
| R3 (ML-SE) | 3/5 | 4.5/5 | +1.5 | Human-in-the-loop design & practical feasibility |

**Average Soundness**: 2.5/5 → 4.17/5 (+1.67 points, 67% improvement)

---

### Presentation

| Reviewer | Round 1 | Round 2 | Improvement | Key Driver |
|----------|---------|---------|-------------|------------|
| R1 (Theory) | 3/5 | 4.5/5 | +1.5 | Visual elements, formal notation, precise terminology |
| R2 (Systems) | 3.5/5 | 4/5 | +0.5 | Clear structure, algorithmic clarity |
| R3 (ML-SE) | 2.5/5 | 4.5/5 | +2 | Vastly improved structure, 9-page format |

**Average Presentation**: 3/5 → 4.33/5 (+1.33 points, 44% improvement)

---

### Contribution

| Reviewer | Round 1 | Round 2 | Improvement | Key Driver |
|----------|---------|---------|-------------|------------|
| R1 (Theory) | 2.5/5 | 4/5 | +1.5 | Selective prediction framework (high novelty) |
| R2 (Systems) | 3/5 | 4/5 | +1 | Evidence-conditioned + selective prediction |
| R3 (ML-SE) | 3/5 | 4/5 | +1 | Human-in-the-loop with calibrated abstention |

**Average Contribution**: 2.83/5 → 4/5 (+1.17 points, 41% improvement)

---

## 🎓 What Made the Difference?

### Top 5 Changes That Moved the Needle

1. **Added Theoretical Foundations** (+2 points on soundness)
   - PAC-style framework with formal definitions
   - Coverage and risk bounds
   - Conformal prediction integration
   - **Impact**: Transformed from engineering to theoretical contribution

2. **Concrete Preliminary Experiment Plan** (+1.5 points overall)
   - Phased approach (1000 → 5000 samples)
   - Feasible timeline (8 weeks)
   - Appropriate baseline (LLM4FPM)
   - **Impact**: Demonstrated feasibility and competence

3. **Detailed Algorithmic Specifications** (+1.5 points on soundness)
   - Algorithm 1: EvidencePack construction
   - Algorithm 2: Calibrated selective triage
   - Algorithm 3: Contrastive FP learning
   - **Impact**: Enabled reproducibility and implementation

4. **Restructured Presentation** (+1.5 points on presentation)
   - 9-page NeurIPS format
   - Visual elements (4 figures, 3 tables)
   - Precise terminology definitions
   - **Impact**: Professional, conference-ready appearance

5. **Sharpened Novelty Claims** (+1 point on contribution)
   - Clear comparison table
   - Honest acknowledgment of what's not novel
   - Focus on selective prediction as primary contribution
   - **Impact**: Honest positioning, clear value proposition

---

## 🚧 Remaining Gaps & Conditions for Acceptance

### MUST Address (Required for Camera-Ready)

1. **Include Preliminary Results** (100-1000 Juliet samples)
   - Precision, recall, F1, calibration (ECE), abstention rate
   - Evidence-conditioned vs. baseline comparison
   - **Timeline**: 4-6 weeks
   - **Impact**: Would raise scores to 8/10

2. **Fix Tool Mismatch**
   - Change "KLEE" to "Java PathFinder (JPF)" for Java
   - Or add C/C++ evaluation with KLEE
   - **Timeline**: 1 day
   - **Impact**: Corrects technical error

3. **Clarify Conformal Prediction for Text-Outputting LLMs**
   - Algorithm for constructing prediction sets
   - Conformity score definition
   - Exchangeability assumption discussion
   - **Timeline**: 1 week
   - **Impact**: Completes theoretical framework

---

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

---

### NICE TO HAVE (Would Strengthen)

8. **Include Real-World Data in Preliminary Experiments**
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

## 📅 Timeline to Camera-Ready

**Assuming Conditional Acceptance at NeurIPS 2026 (notification in September):**

### Weeks 1-4 (September): Preliminary Experiments ⚠️ CRITICAL
- [ ] Week 1: Setup Juliet dataset (1000 samples, CWE-89 SQL injection)
- [ ] Week 2: Implement evidence-conditioned prompting + baseline
- [ ] Week 3: Run experiments, measure precision/calibration/abstention
- [ ] Week 4: Analyze results, create tables/figures

**Deliverable**: Actual preliminary results (precision, ECE, abstention rate)

---

### Weeks 5-6 (October): Technical Fixes
- [ ] Week 5: Fix tool mismatch (KLEE→JPF), clarify conformal prediction
- [ ] Week 6: Detail constraint extraction, specify SMT UNKNOWN handling

**Deliverable**: Technical issues resolved

---

### Weeks 7-8 (October): Enhancements
- [ ] Week 7: Add noise-robust learning methods, developer feedback mechanism
- [ ] Week 8: Polish presentation, create all figures/tables

**Deliverable**: Camera-ready draft

---

### Week 9 (October): Final Review
- [ ] Internal review and revision
- [ ] Check all conditions met
- [ ] Submit camera-ready

**Deliverable**: Final submission

---

## 💡 Key Lessons Learned

### What Worked

1. **Responsive to Feedback**: Authors addressed every major concern systematically
2. **Theoretical Rigor**: Adding PAC-style framework transformed the contribution
3. **Concrete Plans**: Specific algorithms, timelines, and expected outcomes
4. **Honest Positioning**: Clear about what's novel vs. incremental
5. **Professional Presentation**: Restructured for conference format with visuals

### What Still Needs Work

1. **Empirical Validation**: Need actual results, not just plans
2. **Technical Details**: Some gaps remain (conformal prediction, constraint extraction)
3. **Label Quality**: Need concrete noise-robust methods
4. **User Studies**: Important for human-in-the-loop work

---

## 🎯 Probability of Final Acceptance

### Current Status: CONDITIONAL ACCEPT (7.17/10)

**If conditions are met (preliminary results + technical fixes):**
- **Probability**: 85-90% acceptance
- **Expected score**: 8-8.5/10
- **Track**: Main conference

**If conditions are partially met (only technical fixes, no results):**
- **Probability**: 50-60% acceptance
- **Expected score**: 6.5-7/10
- **Track**: Poster or workshop

**If conditions are not met:**
- **Probability**: 10-20% acceptance
- **Expected score**: 5-6/10
- **Recommendation**: Resubmit next cycle

---

## 🏆 Success Criteria

### Minimum Bar for Acceptance
- ✅ Preliminary results on 100-1000 Juliet samples
- ✅ Precision improvement (15-20% over baseline)
- ✅ Calibration quality (ECE < 0.1)
- ✅ Selective prediction works (5% error at 80% coverage vs 15% at 100%)
- ✅ Technical issues fixed (tool mismatch, conformal prediction)
- ✅ 9-page format with 8+ figures/tables

### Stretch Goals for Strong Accept
- ⭐ Results on all 4 datasets (Juliet, NASCAR, D2A, CWE-Bench-Java)
- ⭐ State-of-the-art performance (>95% precision at >90% recall)
- ⭐ Cross-project generalization (train on NASCAR, test on D2A)
- ⭐ Cost analysis (10× speedup vs. full symbolic verification)
- ⭐ Failure analysis (characterize when EVICT fails)

---

## 📞 Next Steps

### Immediate Actions (This Week)
1. **Start Preliminary Experiments**: Download Juliet, setup baseline
2. **Fix Tool Mismatch**: Change KLEE to JPF in all documentation
3. **Draft Conformal Prediction Algorithm**: Write explicit algorithm for text LLMs

### Short-Term (Next 4 Weeks)
1. **Complete Phase 1 Experiments**: 1000 Juliet samples
2. **Generate Results Tables**: Precision, calibration, abstention
3. **Create Figures**: Risk-coverage curves, calibration plots

### Medium-Term (Weeks 5-8)
1. **Address Technical Gaps**: Constraint extraction, SMT UNKNOWN
2. **Add Noise-Robust Methods**: Confident learning for DZA
3. **Polish Presentation**: All figures/tables, camera-ready format

### Long-Term (Week 9)
1. **Final Review**: Check all conditions met
2. **Submit Camera-Ready**: NeurIPS 2026

---

## 🎉 Conclusion

**The improved proposal is a SUCCESS!**

- **Score improvement**: 4.67/10 → 7.17/10 (+53%)
- **Decision change**: REJECT → CONDITIONAL ACCEPT
- **Path to acceptance**: Clear with achievable conditions

**Key takeaway**: The authors demonstrated strong responsiveness to feedback and scientific rigor. With preliminary results and minor technical fixes, this will be a strong NeurIPS contribution.

**Confidence**: 85-90% chance of final acceptance if conditions are met.

---

## 📚 Generated Artifacts

1. **Original Review (Round 1)**:
   - Meta-review: `/home/sandbox/meta_review.md`
   - Individual reviews: `reviewer_1_report.md`, `reviewer_2_report.md`, `reviewer_3_report.md`

2. **Fresh Review (Round 2)**:
   - Meta-review: `/home/sandbox/meta_review_v2.md`
   - Individual reviews: `reviewer_1_report_v2.md`, `reviewer_2_report_v2.md`, `reviewer_3_report_v2.md`

3. **Improved Proposal**:
   - Full document: `/home/sandbox/improved_evict_proposal.md`
   - Quick reference: `/home/sandbox/quick_reference_improvements.md`

4. **Literature Review**:
   - Main insights: `/home/sandbox/literature_insights.md`
   - Selective prediction theory: `/home/sandbox/selective_prediction_theory.md`
   - 609 papers analyzed: `/home/sandbox/combined_neurips_quality_literature_review.papertable`

5. **This Summary**:
   - Review comparison: `/home/sandbox/review_comparison_summary.md`
