# Meta-Review: Evidence-Conditioned LLM Investigation for Static-Analysis Alert Triage

## Overview

This submission proposes EVICT (Evidence-conditioned Verifier for Investigating Code Triage), a system for reducing false positives in static analysis using LLMs with calibrated selective prediction and conditional symbolic verification. The proposal has been reviewed by three experts with complementary perspectives: methods & theory (R1), experiments & practical impact (R2), and clarity & positioning (R3). All three reviewers recognize the importance of the problem and appreciate several aspects of the proposal, but all recommend rejection due to significant concerns about novelty, presentation, and lack of empirical validation.

**Reviewer Scores:**
- Reviewer 1 (Methods & Theory): 4/10 (Weak Reject)
- Reviewer 2 (Experiments & Practical Impact): 5/10 (Borderline Reject)
- Reviewer 3 (Clarity & Positioning): 5/10 (Borderline Reject)

**Meta-Reviewer Recommendation: REJECT**

## Summary of Reviewer Assessments

### Areas of Agreement

All three reviewers agree on several key points:

**Strengths:**
1. **Important problem:** Static analysis false positive reduction is a significant practical problem with clear industrial demand (10-20 minutes per alarm manually per Tencent study)
2. **Comprehensive literature review:** Strong awareness of recent work (BugLens, LLM4PFA, LLM4FPM, AdaTaint) with detailed comparisons
3. **Novel focus on selective prediction:** Calibrated abstention for alert triage is genuinely underexplored and represents the proposal's strongest contribution
4. **Rigorous evaluation philosophy:** Emphasis on leakage-resistant protocols, cross-project generalization, and multiple complementary datasets addresses known issues
5. **Practical grounding:** Inclusion of cost-benefit metrics and industrial evidence shows real-world awareness

**Weaknesses:**
1. **No preliminary results:** All reviewers emphasize that the proposal is entirely prospective without even pilot experiments to demonstrate feasibility
2. **Unclear advantage over strong recent baselines:** Recent work achieves 94-99% precision; the proposal doesn't explain why EVICT will outperform
3. **Presentation issues:** Excessive length, vague terminology, missing visual elements, and unclear problem formulation
4. **Overstated novelty claims:** Evidence-conditioned verification is presented as novel, but multiple recent systems already use this approach
5. **Missing theoretical foundations:** Selective prediction lacks formal definitions, guarantees, or optimality analysis
6. **Label quality issues not addressed:** All datasets have known problems, but the proposal only acknowledges without proposing solutions
7. **Insufficient algorithmic detail:** Key components lack precise specifications

### Areas of Disagreement

The reviewers have some differences in emphasis:

**Reviewer 1 (Methods & Theory)** is most concerned about:
- Lack of theoretical foundations (no formal guarantees, no optimality analysis)
- Insufficient algorithmic detail (vague descriptions of key components)
- Questionable technical assumptions (FP signatures are learnable, symbolic checks can be "lightweight")
- Gives the lowest score (4/10) due to theoretical gaps

**Reviewer 2 (Experiments & Practical Impact)** emphasizes:
- Missing experimental details (LLM selection, prompts, symbolic verification tools)
- Scalability and cost concerns (1M warnings × seconds per warning = days of compute)
- Reproducibility challenges (LLM non-determinism, API version changes)
- Statistical power issues (only 120 samples in CWE-Bench-Java)
- Gives 5/10, noting that preliminary experiments would substantially strengthen the work

**Reviewer 3 (Clarity & Positioning)** focuses on:
- Presentation problems (too long, missing visuals, vague terminology)
- Weak integration narrative (doesn't explain how components synergize)
- Incomplete broader impact analysis (security implications, societal impacts)
- Limited generalization discussion (focus on Java, applicability to other languages)
- Gives 5/10, suggesting restructuring for conference format and conducting pilot studies

## Detailed Assessment

### 1. Novelty and Contribution (Low-Moderate)

**Claimed Contributions:**
1. Risk-controlled adjudication via selective prediction
2. False-positive signature learning via contrastive learning
3. Verifier with symbolic hooks and abstention
4. Standardized evidence interchange via SARIF

**Assessment:**

**Contribution 1 (Selective Prediction): Moderate-High Novelty**
- All reviewers agree this is the strongest contribution
- Calibrated abstention is not systematically applied in existing LLM-based static analysis work
- However, R1 notes that without theoretical development, it's primarily an engineering contribution
- R2 emphasizes that practical value depends on whether calibration actually works in practice
- R3 observes that the contribution is weakened by lack of formal definitions and guarantees

**Contribution 2 (Contrastive Learning): Low-Moderate Novelty**
- R1: "Contrastive learning is a standard technique; applying it to code alert triage is reasonable but not particularly novel"
- R2: "Unclear if it's better than simpler alternatives"
- R3: "Novel to this domain, but doesn't clearly explain why it's better than existing supervised approaches"
- All reviewers note that the assumption that FP patterns transfer across projects is untested

**Contribution 3 (Neuro-Symbolic Integration): Low Novelty**
- All reviewers note that recent work (AdaTaint, WARP, Laurel) already demonstrates neuro-symbolic integration
- The "conditional invocation" aspect is a practical contribution but not a fundamental advance
- R1 and R2 emphasize that without algorithmic detail, it's hard to assess the technical contribution

**Contribution 4 (SARIF Standardization): Low Scientific Novelty**
- All reviewers agree this is primarily an engineering contribution
- R3: "High practical value for the community, low scientific novelty"

**Overall Novelty:** The proposal makes one moderately novel contribution (selective prediction) and several incremental contributions. For NeurIPS, this is insufficient without either strong theoretical foundations or compelling empirical evidence of superiority.

### 2. Technical Soundness (Low-Moderate)

**Theoretical Foundations:**
- R1 (2/5 soundness): "No formal definitions of risk, coverage, or optimality criteria... no theoretical guarantees or bounds"
- R2 (2.5/5 soundness): "Calibration methods mentioned but not adapted to alert triage structure"
- R3 (3/5 soundness): "Selective prediction presented informally without rigorous mathematical formulation"

**Algorithmic Detail:**
- All reviewers note that key components lack precise specifications:
  - EvidencePack construction algorithm
  - Schema-guided claim checking structure
  - Conditional symbolic invocation decision logic
  - Contrastive learning procedure (loss function, training details)
- R1: "Simply applying off-the-shelf techniques may not yield valid guarantees"

**Methodological Concerns:**
- R1: "Progressive prompting could lead to unbounded loops... no termination guarantees"
- R2: "No strategy for validating or correcting labels beyond acknowledging the problem"
- R3: "Integration of multiple components is conceptually reasonable but their interactions are not fully specified"

**Experimental Design:**
- R2 identifies multiple issues: dataset quality, baseline implementation, metrics selection, cross-project evaluation strategy, statistical testing
- R1 notes missing cost model for conditional symbolic invocation
- R3 observes that with only 120 samples in CWE-Bench-Java, statistical power will be limited

**Verdict:** The technical soundness is questionable due to missing theoretical foundations, vague algorithmic details, and incomplete experimental design. This needs substantial development before publication.

### 3. Presentation Quality (Low-Moderate)

All reviewers identify significant presentation issues:

**Length and Structure:**
- R3 (2.5/5 presentation): "~12 pages of dense text, far too long for NeurIPS (typically 9 pages + references)... would require cutting ~40% of content"
- R1 (3/5): "Excessive length and verbosity... reads more like a position paper or grant proposal"
- R2 (3.5/5): "Reads like a grant proposal or position paper, not a research paper"

**Missing Visual Elements:**
- All reviewers note the lack of:
  - System architecture diagram
  - Example EvidencePacks
  - Example prompts
  - Result visualizations (even hypothetical)
  - Detailed algorithmic pseudocode

**Vague Terminology:**
- All reviewers cite examples: "lightweight," "targeted," "minimal," "progressive," "schema-guided"
- R1: "Used without precise definitions"
- R3: "These terms are used repeatedly without precise definitions"

**Problem Formulation:**
- R1: "Mentions three formulations but doesn't clearly specify which EVICT optimizes"
- R2: "Relationship between classification, ranking, selective prediction is unclear"
- R3: "Choose one primary formulation and formalize it mathematically"

**Citation Issues:**
- R3: "Many informal URLs rather than proper academic citations... several key references are unpublished preprints"

**Verdict:** The presentation needs substantial revision. The document must be restructured for conference format, condensed significantly, and enhanced with visual elements and precise definitions.

### 4. Empirical Validation (Critical Gap)

This is the most significant weakness identified by all reviewers:

**No Preliminary Results:**
- R1: "The proposal doesn't provide compelling evidence that it will [outperform baselines]"
- R2: "The proposal would be much stronger with even small-scale pilot experiments demonstrating feasibility"
- R3: "The proposal is entirely prospective. Even small-scale proof-of-concept results would greatly increase confidence"

**Unclear Performance Expectations:**
- All reviewers note that recent work achieves 94-99% precision (LLM4FPM, LLM4PFA, Tencent study)
- R1: "If EVICT achieves similar performance, the incremental value is limited"
- R2: "Doesn't specify what performance level would constitute success"
- R3: "Doesn't explain why EVICT will outperform these strong baselines"

**Verdict:** The lack of any empirical validation is a critical gap. For NeurIPS, preliminary results are essential to demonstrate feasibility and potential impact.

### 5. Broader Impact and Practical Considerations

**Positive Aspects:**
- All reviewers appreciate the practical grounding (cost-benefit metrics, industrial evidence)
- R3 notes the ethical awareness (safety implications, mitigation strategies)
- R2 values the emphasis on reproducibility and standardized evaluation

**Concerns:**
- R3: "Broader impact analysis is brief and somewhat superficial... deeper analysis of security implications would strengthen"
- R2: "Scalability and cost concerns not addressed... 1M warnings × seconds per warning = days of compute"
- R1: "Implementation complexity... 6-month timeline may be optimistic"

**Verdict:** While the proposal shows practical awareness, deeper analysis of deployment challenges, security implications, and societal impacts would strengthen the submission.

## Comparison to NeurIPS Standards

NeurIPS typically expects papers to include:
1. **Novel algorithms with theoretical analysis** - EVICT lacks theoretical foundations
2. **Significant empirical improvements on established benchmarks** - No empirical results provided
3. **New problem formulations with broad applicability** - Selective prediction is interesting but underdeveloped
4. **Theoretical insights that advance understanding** - Missing

The proposal is more aligned with systems/engineering venues (ICSE, FSE, ASE) that value:
- Practical systems contributions
- Comprehensive evaluation on real-world problems
- Integration of existing techniques for practical impact

## Decision Rationale

After careful consideration of all three reviews, I recommend **REJECT** for the following reasons:

### Critical Issues (Must Address for Any Venue)

1. **No empirical validation:** The complete absence of preliminary results makes it impossible to assess whether the approach is feasible or promising. Even small-scale pilot experiments on Juliet would substantially strengthen the submission.

2. **Unclear advantage over strong recent baselines:** With recent work achieving 94-99% precision, the proposal must either:
   - Demonstrate empirically that EVICT outperforms these baselines, OR
   - Provide theoretical analysis showing why EVICT should outperform, OR
   - Identify specific scenarios where existing work fails and EVICT succeeds
   None of these are provided.

3. **Missing theoretical foundations:** For NeurIPS, the selective prediction contribution needs formal definitions, theoretical guarantees, or optimality analysis. Without this, it's primarily an engineering contribution.

4. **Insufficient algorithmic detail:** Key components are described conceptually but lack precise specifications, making it difficult to assess technical soundness or reproduce the work.

### Major Issues (Significant Revision Needed)

5. **Presentation problems:** The document is too long, lacks essential visual elements, uses vague terminology, and doesn't clearly formulate the problem. Substantial restructuring is needed for conference format.

6. **Overstated novelty claims:** Evidence-conditioned verification is presented as novel, but multiple recent systems already use this approach. The proposal should more clearly distinguish EVICT's unique contributions.

7. **Label quality issues not addressed:** All datasets have known problems, but the proposal only acknowledges without proposing systematic solutions.

### Minor Issues (Would Strengthen Submission)

8. **Weak integration narrative:** The proposal doesn't clearly explain how the four contributions synergize or why integration is better than using components independently.

9. **Limited scope discussion:** Focus on Java raises questions about generalization to other languages. Cross-language evaluation is not addressed.

10. **Incomplete broader impact analysis:** Security implications, potential for misuse, and societal impacts need deeper treatment.

## Recommendations for Revision

To make this work suitable for publication, the authors should:

### Essential Changes

1. **Conduct preliminary experiments:**
   - Start with Juliet (manageable scale, controlled setting)
   - Demonstrate that evidence-conditioned prompting works
   - Show that calibration improves reliability
   - Compare to at least one strong recent baseline (LLM4FPM or LLM4PFA)
   - Include results in the paper to establish feasibility

2. **Develop theoretical foundations:**
   - Formalize selective prediction with mathematical definitions
   - Prove theoretical guarantees (coverage bounds, risk bounds)
   - Characterize when abstention is optimal
   - Provide complexity analysis

3. **Provide detailed algorithms:**
   - EvidencePack construction
   - Schema-guided claim checking (include the schema)
   - Conditional symbolic invocation decision logic
   - Contrastive learning procedure

4. **Restructure for conference format:**
   - Add abstract and introduction
   - Condense to 9 pages + references
   - Move detailed literature review and timelines to supplementary material
   - Add visual elements (architecture, examples, results)

### Important Changes

5. **Sharpen novelty claims:**
   - Focus on selective prediction as primary contribution
   - Clearly distinguish from recent work (LLM4FPM, LLM4PFA, BugLens)
   - Acknowledge what's not novel

6. **Address label quality systematically:**
   - Propose noise-robust learning methods
   - Use validation techniques (fuzzing, manual auditing)
   - Report inter-annotator agreement

7. **Develop cost-benefit analysis:**
   - Formal cost model (LLM inference, symbolic verification, developer time)
   - Analysis of when symbolic checks are cost-effective
   - End-to-end cost per alert and savings vs. manual triage

8. **Strengthen experimental design:**
   - Specify LLM selection, prompts, hyperparameters
   - Describe symbolic verification tools and settings
   - Define primary metrics and statistical testing procedures
   - Address reproducibility challenges

### Useful Changes

9. **Expand broader impact analysis:**
   - Security implications (missed vulnerabilities)
   - Potential for misuse
   - Societal impacts (automation, developer workflows)
   - Environmental impact (carbon footprint)

10. **Add failure analysis:**
    - When does EVICT fail?
    - Which bug types are hardest?
    - How does performance vary across categories?

11. **Address generalization:**
    - Discuss applicability to C/C++, Python, JavaScript
    - Include cross-language evaluation if feasible
    - Analyze language-specific challenges

## Alternative Venues

Given the current state of the work, the authors should consider:

1. **Software Engineering Venues (ICSE, FSE, ASE):**
   - More receptive to systems contributions
   - Value practical impact and comprehensive evaluation
   - Accept longer papers with more implementation detail
   - ICSE 2025 (deadline typically August) or FSE 2025 (deadline typically March)

2. **Workshop Papers:**
   - Present preliminary results and get feedback
   - NeurIPS workshops, ICSE/FSE workshops
   - Lower bar for preliminary work

3. **Technical Reports or ArXiv:**
   - Share ideas with the community
   - Get feedback before submitting to a conference
   - Establish priority for ideas

4. **Resubmit to NeurIPS 2026:**
   - With preliminary results, theoretical foundations, and revised presentation
   - After addressing all critical issues identified by reviewers

## Final Recommendation

**Decision: REJECT**

**Reasoning:** While this proposal addresses an important problem and makes valuable contributions (particularly the focus on calibrated selective prediction), it is not ready for publication at NeurIPS in its current form. The absence of any empirical validation, lack of theoretical foundations, unclear advantage over strong recent baselines, and significant presentation issues make it unsuitable for acceptance. With substantial revision—especially conducting preliminary experiments and developing theoretical foundations—this could become a strong submission.

**Confidence: High (4/5)**

All three reviewers are experienced in their respective areas and agree on the main weaknesses. The decision is clear and well-supported by detailed reviews.

**Suggested Action for Authors:**

1. **Short term (3-6 months):**
   - Conduct pilot experiments on Juliet
   - Develop theoretical foundations for selective prediction
   - Restructure for conference format
   - Submit to ICSE/FSE or a workshop

2. **Medium term (6-12 months):**
   - Complete full evaluation on all datasets
   - Implement and compare to strong baselines
   - Conduct ablation studies
   - Resubmit to NeurIPS 2026 or major SE venue

The core ideas have merit, and with proper development and validation, this could make a valuable contribution to the field. However, more work is needed before it's ready for publication at a top-tier venue like NeurIPS.
