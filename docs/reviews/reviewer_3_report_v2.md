# Reviewer 3 Report (Fresh Review - Round 2): ML for Software Engineering & Human-AI Collaboration Specialist

## Summary

This revised EVICT proposal presents a comprehensive improvement roadmap for static analysis alert triage using evidence-conditioned LLMs with calibrated selective prediction and conditional symbolic verification. As an ML for software engineering and human-AI collaboration specialist, I focus on: (1) the practical feasibility and usability of the system, (2) the human-in-the-loop aspects of selective prediction, (3) the evaluation on realistic software engineering tasks, and (4) the broader impact on developer workflows. The revision shows **major improvement** in addressing previous concerns, particularly in clarifying the human-AI collaboration model and providing concrete evaluation plans.

## Soundness: 4.5/5

From an ML-for-SE and human-AI collaboration perspective, the proposal demonstrates strong soundness:

**Human-in-the-Loop Design (Major Improvement):**

The selective prediction framework now explicitly models human-AI collaboration:

- **Three-way decision:** TP (auto-accept), FP (auto-dismiss), ABSTAIN (human review)
  - This is the right model for high-stakes decisions
  - Abstention enables safe automation while preserving human judgment
  - Addresses safety concerns from first review

- **Cost-sensitive formulation:** R(h,g) = α·R_FN + β·R_FP + γ·R_abstain
  - Explicitly models asymmetric costs (FN > FP in security contexts)
  - Abstention cost γ represents human review time
  - Enables optimization of human workload vs. error risk tradeoff

- **Calibrated confidence:** Multiple methods (logit-based, ensemble, conformal)
  - Appropriate for different LLM access levels (open-source vs. API-only)
  - Conformal prediction provides distribution-free guarantees
  - Addresses trust and reliability concerns

**Strengths:**
- Clear human-AI collaboration model
- Explicit modeling of human review cost
- Multiple confidence estimation methods
- Safety-conscious design (abstain when uncertain)

**Concerns:**
- **User study missing:** The proposal doesn't include plans for user studies to validate that developers trust and use the abstention mechanism appropriately.
- **Abstention rate:** Expected 10-20% abstention. Is this acceptable to developers? Too high may reduce adoption; too low may miss uncertain cases.
- **Feedback loop:** The proposal mentions "feedback labels" (Algorithm 2, Line 12) but doesn't specify how developer feedback is collected, validated, and incorporated into model updates.

**Practical Feasibility (Significant Improvement):**

The proposal now addresses deployment considerations:

- **Lightweight verification:** 10s timeout, 2GB memory, depth ≤50, max 100 paths
  - Reasonable for practical deployment
  - But: still need average-case overhead estimates

- **SARIF standardization:** Enables integration with multiple analyzers
  - Practical value for industrial adoption
  - Reduces integration effort

- **Cost-benefit analysis:** Expected minutes saved vs. verification overhead
  - Tencent study: 10-20 min/alarm manually
  - EVICT: seconds per alarm (LLM inference + optional symbolic checks)
  - ROI is clear if precision is high

**Strengths:**
- Concrete deployment considerations
- Clear cost-benefit analysis
- SARIF integration reduces adoption barriers

**Concerns:**
- **Integration effort:** Converting analyzer outputs to SARIF, setting up LLM API, configuring symbolic tools - how much engineering effort?
- **Maintenance:** LLM API changes, analyzer updates, evolving codebases - how is the system maintained over time?
- **Customization:** Different projects may have different cost profiles (α, β, γ). How are these tuned per project?

**Evaluation on Realistic SE Tasks (Major Improvement):**

The evaluation plan now includes multiple realistic datasets:

- **NASCAR (1M Java warnings):** Large-scale actionability corpus
  - Reflects real developer triage decisions
  - "Actionable" ≠ "true bug" - proposal acknowledges this
  - Good for training and large-scale evaluation

- **DZA (differential analysis):** Realistic labels from bug-fix commits
  - Weak supervision but scalable
  - Proposal acknowledges label noise
  - Good for cross-project evaluation

- **CWE-Bench-Java (120 validated vulnerabilities):** High-stakes evaluation
  - Manually validated, high-quality labels
  - Small but important for security-critical assessment
  - Good for testing on real vulnerabilities

- **Juliet/SARD (synthetic):** Controlled evaluation
  - Known ground truth
  - Good for debugging and ablations
  - But: may not reflect real-world patterns (proposal acknowledges this)

**Strengths:**
- Multiple complementary datasets
- Realistic evaluation scenarios (actionability, bug fixes, real vulnerabilities)
- Honest about dataset limitations

**Concerns:**
- **Developer validation:** No plans for developer studies to validate that EVICT's decisions align with human judgment.
- **Longitudinal evaluation:** No plans to evaluate EVICT over time as codebases evolve.
- **Organizational context:** Different organizations may have different triage priorities. How does EVICT adapt?

**Preliminary Experiments (Addresses Critical Gap):**

The phased plan is concrete and feasible:

- **Phase 1 (Weeks 1-4):** 1000 Juliet samples
  - Proof-of-concept on controlled data
  - Evidence-conditioned vs. baseline prompting
  - Preliminary calibration analysis
  - Expected: precision 85-95%, ECE <0.1, abstention 10-20%

- **Phase 2 (Weeks 5-8):** 5000 Juliet samples + LLM4FPM comparison
  - Scale up and compare to strong baseline
  - Implement contrastive learning
  - Cross-bug-type evaluation

**Strengths:**
- Feasible timeline (8 weeks)
- Phased approach reduces risk
- Appropriate baseline (LLM4FPM)
- Realistic expectations given recent work

**Concerns:**
- **Still no actual results:** This is still a plan, not completed work.
- **Juliet-only:** Synthetic data may not reflect real-world patterns. Should include DZA or NASCAR subset in Phase 2.
- **No developer feedback:** Preliminary experiments don't include human validation of decisions.

## Presentation: 4.5/5

The presentation is vastly improved:

**Strengths:**

1. **Clear structure:** Part 1 (improvements), Part 2 (theory), Part 3 (methodology), Part 4 (evaluation), Part 5 (roadmap). Logical and easy to follow.

2. **Visual elements:** Architecture diagram, risk-coverage curves, calibration plots, example EvidencePack. These clarify the approach significantly.

3. **Precise terminology:** "Lightweight" (10s timeout, 2GB memory), "targeted" (depth ≤50, max 100 paths). No more vague language.

4. **Human-AI collaboration model:** Figure 2 (risk-coverage curves) clearly illustrates the tradeoff between automation and human review.

5. **Concrete examples:** EvidencePack example (Figure 4) shows actual SARIF encoding with code snippet, slice, flow, and constraints.

6. **Algorithmic clarity:** Algorithms 1-3 are clear and implementable.

7. **Honest about limitations:** Discusses failure modes, label quality issues, and when EVICT is expected to struggle.

8. **Appropriate length:** Structured for 9-page NeurIPS format with supplementary material clearly delineated.

**Weaknesses:**

1. **No user interface mockups:** For a human-in-the-loop system, showing how developers interact with EVICT would be valuable. What does the abstention workflow look like?

2. **No developer feedback mechanism:** Algorithm 2, Line 12 mentions "collect feedback" but doesn't show how. Is it a button click? A form? Integrated into the IDE?

3. **No longitudinal evaluation plan:** How is EVICT evaluated over time? Do developers continue to trust it? Does performance degrade as codebases evolve?

4. **Limited discussion of adoption barriers:** What prevents developers from using EVICT? Trust issues? Integration effort? False sense of security?

5. **No comparison to human performance:** What is human precision/recall on these tasks? How close does EVICT get to human-level performance?

## Contribution: 4/5

From an ML-for-SE and human-AI collaboration perspective:

**Contribution 1: Human-in-the-Loop Alert Triage with Calibrated Abstention (High Value)**

- **Novelty:** First work to formalize alert triage as selective prediction with explicit human-AI collaboration model
- **Impact:** Enables safe automation in high-stakes security contexts
- **Practical value:** Very high - addresses trust and reliability concerns critical for adoption

**Assessment:** This is the strongest contribution. The explicit modeling of human review cost and calibrated abstention is novel and valuable for ML-for-SE.

**Contribution 2: Evidence-Based LLM Reasoning for Program Analysis (Moderate Value)**

- **Novelty:** Moderate - recent work (LLM4FPM, LLM4PFA) also uses evidence-based reasoning
- **Impact:** High for improving precision
- **Practical value:** High - structured reasoning reduces hallucination

**Assessment:** The evidence-based approach is well-executed but not particularly novel. The value is in the integration with selective prediction.

**Contribution 3: Cross-Tool Evaluation with SARIF (High Practical Value, Low Scientific Novelty)**

- **Novelty:** Low - SARIF is an existing standard
- **Impact:** High for reproducibility and cross-tool comparison
- **Practical value:** Very high - enables systematic evaluation

**Assessment:** This is primarily an engineering contribution, but it's valuable for the community. Cross-tool evaluation is rare and important.

**Contribution 4: Rigorous Evaluation Protocols (High Value for Community)**

- **Novelty:** Low - leakage-resistant protocols are known
- **Impact:** High - addresses known issues in ML-for-SE evaluation
- **Practical value:** High - improves rigor

**Assessment:** Not novel scientifically, but implementing these protocols rigorously is valuable and sets a good example.

**Overall Assessment:**

The proposal makes one strong contribution (human-in-the-loop with calibrated abstention) and several moderate contributions (evidence-based reasoning, cross-tool evaluation, rigorous protocols). This is appropriate for NeurIPS, especially if preliminary results demonstrate practical value.

**Comparison to Recent Work:**

The proposal now clearly distinguishes EVICT:

- **vs. LLM4FPM:** EVICT adds selective prediction and human-in-the-loop workflow
- **vs. LLM4PFA:** EVICT adds formal guarantees and explicit abstention mechanism
- **vs. BugLens:** EVICT adds quantitative risk control and cross-tool evaluation
- **vs. AdaTaint:** EVICT adds selective prediction and systematic evaluation

This is much clearer than the original proposal.

## Strengths

1. **Addresses Critical Human-AI Collaboration Challenges:**
   - Explicit modeling of human review cost
   - Calibrated abstention for safe automation
   - Trust and reliability through formal guarantees
   - Auditable certificates for transparency

2. **Strong Practical Motivation:**
   - Clear industrial demand (10-20 min/alarm manually)
   - Concrete cost-benefit analysis
   - ROI metrics and deployment considerations
   - SARIF standardization reduces adoption barriers

3. **Rigorous Evaluation Design:**
   - Multiple realistic datasets (NASCAR, DZA, CWE-Bench-Java, Juliet)
   - Leakage-resistant protocols address known issues
   - Cross-tool evaluation (SpotBugs, Infer, CodeQL)
   - Comprehensive ablations

4. **Feasible Preliminary Experiment Plan:**
   - Phased approach (1000 → 5000 samples)
   - Concrete timeline (8 weeks)
   - Appropriate baseline (LLM4FPM)
   - Realistic expectations

5. **Excellent Presentation:**
   - Clear structure and logical flow
   - Visual elements (architecture, risk-coverage, calibration, example)
   - Precise terminology (no more vague language)
   - Honest about limitations

6. **Safety-Conscious Design:**
   - Abstain when uncertain
   - Verify high-severity dismissals
   - Auditable certificates with counterexamples
   - Explicit modeling of false negative risk

7. **Responsive to Feedback:**
   - Addresses all major concerns from first review
   - Substantial improvement in technical depth
   - Clear acknowledgment of previous weaknesses

8. **Reproducibility Focus:**
   - SARIF standardization
   - Public datasets
   - Detailed protocols
   - Code release plan

9. **Honest About Limitations:**
   - Discusses failure modes
   - Acknowledges label quality issues
   - Recognizes symbolic verification limitations
   - Discusses when EVICT is expected to struggle

10. **Strong Integration of Multiple Techniques:**
    - Evidence-based reasoning + selective prediction + symbolic verification
    - Demonstrates how components work together
    - Clear value proposition for integration

## Weaknesses

1. **No Actual Preliminary Results:**
   - Still a roadmap, not completed work
   - Even 50-100 sample pilot results would strengthen enormously
   - For NeurIPS, preliminary results are strongly expected

2. **Missing User Studies:**
   - No plans for developer studies to validate decisions
   - No evaluation of whether developers trust and use abstention appropriately
   - No assessment of developer satisfaction or workflow impact

3. **Developer Feedback Mechanism Not Specified:**
   - Algorithm 2, Line 12 mentions "collect feedback" but doesn't show how
   - How is feedback validated? How is it incorporated into model updates?
   - What if developers disagree with EVICT's decisions?

4. **Abstention Rate Validation:**
   - Expected 10-20% abstention. Is this acceptable to developers?
   - Too high may reduce adoption; too low may miss uncertain cases
   - No user research to validate this range

5. **No Longitudinal Evaluation:**
   - How does EVICT perform over time as codebases evolve?
   - Do developers continue to trust it?
   - Does performance degrade (concept drift)?

6. **Customization Not Addressed:**
   - Different projects may have different cost profiles (α, β, γ)
   - How are these tuned per project?
   - Can developers adjust sensitivity (more/less abstention)?

7. **Integration Effort Not Quantified:**
   - Converting analyzer outputs to SARIF
   - Setting up LLM API
   - Configuring symbolic tools
   - How much engineering effort is required?

8. **Maintenance and Evolution:**
   - LLM API changes over time
   - Analyzers update with new rules
   - Codebases evolve
   - How is EVICT maintained?

9. **No Comparison to Human Performance:**
   - What is human precision/recall on these tasks?
   - How close does EVICT get to human-level?
   - Are there cases where EVICT outperforms humans?

10. **Juliet-Only Preliminary Experiments:**
    - Phase 1 and 2 use only Juliet (synthetic)
    - Should include real-world data (DZA or NASCAR subset)
    - Synthetic patterns may not reflect real-world FP patterns

11. **Adoption Barriers Not Discussed:**
    - What prevents developers from using EVICT?
    - Trust issues? Integration effort? False sense of security?
    - How to address these barriers?

12. **Limited Discussion of Organizational Context:**
    - Different organizations have different triage priorities
    - Security-focused vs. feature-focused teams
    - How does EVICT adapt to organizational context?

## Suggestions

1. **Conduct Minimal Preliminary Experiments with Developer Feedback:**
   - 50-100 Juliet samples with actual results (precision, calibration, abstention rate)
   - Show 10-20 abstained cases to 3-5 developers for validation
   - Report inter-rater agreement and developer feedback
   - This would strengthen the proposal enormously

2. **Add User Study Plans:**
   - Phase 3 (Weeks 9-12): User study with 10-15 developers
   - Evaluate trust, usability, workflow impact
   - Measure time saved, developer satisfaction, perceived usefulness
   - This is critical for ML-for-SE work

3. **Specify Developer Feedback Mechanism:**
   - Design UI mockup showing abstention workflow
   - Specify how feedback is collected (button click, form, IDE integration)
   - Describe how feedback is validated and incorporated
   - Include in supplementary material

4. **Validate Abstention Rate:**
   - Survey developers: what abstention rate is acceptable?
   - Analyze tradeoff: automation benefit vs. review burden
   - Provide guidance on tuning abstention threshold

5. **Add Longitudinal Evaluation Plan:**
   - Phase 4 (Months 3-6): Deploy EVICT on a real project
   - Monitor performance over time (3-6 months)
   - Track concept drift, developer trust, continued usage
   - This demonstrates long-term viability

6. **Provide Customization Mechanism:**
   - Allow developers to adjust cost parameters (α, β, γ)
   - Provide presets (security-focused, feature-focused, balanced)
   - Enable per-project tuning based on historical data

7. **Quantify Integration Effort:**
   - Estimate engineering hours for SARIF conversion, LLM setup, symbolic tool configuration
   - Provide step-by-step integration guide
   - Discuss common integration challenges and solutions

8. **Discuss Maintenance and Evolution:**
   - Plan for LLM API changes (version pinning, fallback strategies)
   - Handle analyzer updates (re-train? fine-tune?)
   - Address concept drift (periodic re-calibration?)

9. **Compare to Human Performance:**
   - Collect human labels on a subset (100-500 alerts)
   - Report human precision, recall, inter-rater agreement
   - Compare EVICT to human performance
   - Identify cases where EVICT outperforms or underperforms humans

10. **Add Real-World Data to Preliminary Experiments:**
    - Phase 2.5 (Weeks 7-8): 500 DZA samples or 1000 NASCAR samples
    - Show that approach works on real-world data
    - Compare synthetic (Juliet) vs. real-world patterns

11. **Discuss Adoption Barriers:**
    - Trust: How to build developer trust in EVICT?
    - Integration: How to reduce integration effort?
    - False security: How to prevent over-reliance on automation?
    - Provide strategies for addressing each barrier

12. **Address Organizational Context:**
    - Discuss how EVICT adapts to different organizational priorities
    - Provide case studies or scenarios (security-focused, feature-focused)
    - Enable customization for different contexts

## Questions

1. **Preliminary Results:** Do you have any preliminary results, even on 10-50 samples? This would greatly strengthen the proposal.

2. **User Studies:** Do you plan to conduct user studies with developers? When and how?

3. **Developer Feedback:** How will developer feedback be collected, validated, and incorporated? Can you show a UI mockup?

4. **Abstention Rate:** Is 10-20% abstention acceptable to developers? Have you validated this with user research?

5. **Longitudinal Evaluation:** How will you evaluate EVICT over time (3-6 months) as codebases evolve?

6. **Customization:** How can developers adjust cost parameters (α, β, γ) for their project-specific needs?

7. **Integration Effort:** How much engineering effort is required to integrate EVICT? Can you provide estimates?

8. **Maintenance:** How is EVICT maintained over time as LLM APIs, analyzers, and codebases evolve?

9. **Human Performance:** What is human precision/recall on these tasks? How close does EVICT get?

10. **Real-World Data:** Will preliminary experiments include real-world data (DZA, NASCAR), or only Juliet?

11. **Adoption Barriers:** What prevents developers from using EVICT? How do you address trust, integration effort, and false security concerns?

12. **Organizational Context:** How does EVICT adapt to different organizational priorities (security-focused vs. feature-focused)?

13. **Concept Drift:** How do you handle concept drift as codebases and bug patterns evolve over time?

14. **Feedback Loop:** If developers consistently disagree with EVICT's decisions, how is the model updated?

15. **Comparison to Baselines:** How will you ensure fair comparison to LLM4FPM (which uses different slicing)?

## Rating: 7.5/10 (Accept)

**Justification:**

This revised proposal shows **major improvement** over the original submission. From an ML-for-SE and human-AI collaboration perspective, the approach is sound and valuable:

✓ **Human-in-the-loop design:** Clear model with calibrated abstention  
✓ **Practical feasibility:** Concrete deployment considerations and cost-benefit analysis  
✓ **Realistic evaluation:** Multiple datasets reflecting real SE tasks  
✓ **Preliminary experiment plan:** Feasible and well-designed  
✓ **Excellent presentation:** Clear, visual, honest about limitations  

**Remaining concerns:**

- **No actual results:** Still a roadmap, but the plan is concrete and feasible
- **Missing user studies:** Critical for ML-for-SE work, but can be added before camera-ready
- **Developer feedback mechanism:** Needs specification, but can be added

**Why Accept:**

1. **Novel human-AI collaboration model:** Formalizing alert triage as selective prediction with explicit human review cost is new and valuable.

2. **Addresses critical practical problem:** Static analysis false positives waste significant developer time (10-20 min/alarm).

3. **Strong practical value:** High potential for industrial adoption with clear ROI.

4. **Rigorous methodology:** Leakage-resistant protocols, cross-tool evaluation, comprehensive ablations.

5. **Feasible plan:** The preliminary experiment plan is concrete, phased, and achievable.

6. **Excellent presentation:** Clear structure, visual elements, precise terminology.

7. **Responsive to feedback:** Addresses all major concerns from first review.

**Conditions for acceptance:**

1. **Should include preliminary results:** At least 50-100 samples with actual numbers before camera-ready. This would raise my score to 8/10.

2. **Should add user study plans:** Even a small pilot study (5-10 developers) would strengthen the human-AI collaboration claims.

3. **Must specify developer feedback mechanism:** Show how developers interact with abstention workflow.

**Why higher score than other reviewers:**

From an ML-for-SE perspective, the human-in-the-loop design and practical deployment considerations are particularly strong. The explicit modeling of human review cost and calibrated abstention addresses critical trust and reliability concerns. While preliminary results would strengthen the work, the plan is concrete enough that I believe the authors can execute it successfully.

**Alternative:** If preliminary results and user studies are not available, this could be a **strong poster** or **workshop paper**. But with the improvements, I believe it's ready for the main conference track.

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have strong expertise in ML for software engineering, human-AI collaboration, and empirical evaluation of SE tools. I am familiar with the practical challenges of deploying ML systems in SE contexts. My main uncertainty is whether developers will actually trust and use the abstention mechanism appropriately - this requires user studies to validate. However, based on the quality of the revision, the feasibility of the plan, and the practical value of the contribution, I believe this work is ready for NeurIPS acceptance (with minor revisions).
