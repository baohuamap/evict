# Reviewer 3 Report: Clarity, Positioning & Broader Impact Specialist

## Summary

This proposal introduces EVICT (Evidence-conditioned Verifier for Investigating Code Triage), a system for reducing false positives in static analysis alerts using large language models with calibrated selective prediction and conditional symbolic verification. The approach constructs structured evidence bundles containing alert metadata, code slices, analyzer flows, and constraints; applies LLM-based verification through schema-guided prompting; employs calibrated uncertainty estimation to enable abstention; uses contrastive learning to identify false-positive patterns; and conditionally invokes SMT solvers and symbolic execution. The evaluation strategy encompasses NASCAR (1M Java warnings), DZA (differential analysis labels), Juliet/SARD (synthetic benchmarks), and CWE-Bench-Java (120 validated vulnerabilities), with emphasis on standardized SARIF interchange and leakage-resistant evaluation protocols.

## Soundness: 3/5

From the perspective of clarity, positioning, and broader impact, the proposal demonstrates reasonable soundness with some concerns:

**Positioning and Related Work:**
- The literature survey is comprehensive and demonstrates strong awareness of recent work (BugLens, LLM4PFA, LLM4FPM, AdaTaint, industrial studies)
- The positioning relative to existing work is generally clear, though the distinction between EVICT and very recent systems could be sharper
- The proposal correctly identifies that calibrated abstention is underexplored in this domain
- However, the claim of novelty for evidence-conditioned verification is overstated—multiple recent systems already use this approach

**Problem Formulation:**
- The problem (static analysis false positive reduction) is important and well-motivated with concrete evidence (Tencent study: 10-20 minutes per alarm manually)
- Three formulations are mentioned (classification, ranking, selective prediction) but their relationship is unclear
- The distinction between "actionable" (NASCAR), "true positive," and "fixed bug" (DZA) is acknowledged but not fully resolved in the problem definition

**Methodological Clarity:**
- The high-level approach is clear: evidence extraction → LLM verification → calibrated decision → optional symbolic checks
- However, many technical details are vague or missing (see Presentation section)
- The integration of multiple components (contrastive learning, calibration, symbolic verification) is conceptually reasonable but their interactions are not fully specified

**Ethical and Societal Considerations:**
- The proposal acknowledges safety concerns: "Over-filtering true positives can silently increase risk, especially for security findings"
- Mitigation strategies are reasonable: abstention for high-risk cases, separation of workflows, logging for auditability
- However, the analysis of potential harms is somewhat superficial—more depth on security implications would strengthen this section

## Presentation: 2.5/5

**Strengths:**
1. **Well-Structured:** Clear section organization with logical flow from motivation → literature → method → evaluation → challenges
2. **Comprehensive Literature Review:** Strong coverage of recent work with concrete citations and comparisons
3. **Explicit Acknowledgment of Limitations:** The "Challenges, ethics, reproducibility" section honestly discusses issues (hallucinations, distribution shift, label noise)
4. **Visual Aids:** Includes flowchart and Gantt chart to illustrate the approach and timeline
5. **Concrete Anchors:** Uses specific examples (Tencent study costs, BugLens precision improvements) to ground claims

**Weaknesses:**

1. **Excessive Length and Verbosity:**
   - The proposal is ~12 pages of dense text, far too long for a NeurIPS paper (typically 9 pages + references)
   - Contains substantial material that belongs in supplementary material (detailed dataset descriptions, full literature review, implementation timeline)
   - Reads more like a grant proposal or technical report than a research paper
   - Would require cutting ~40% of content for a conference submission

2. **Inconsistent Technical Depth:**
   - Some sections are highly detailed (dataset tables, literature survey) while others are vague (algorithms, prompts, symbolic verification)
   - The imbalance makes it difficult to assess technical feasibility
   - Critical technical details are often described in prose rather than formal notation or pseudocode

3. **Missing Visual Elements:**
   - **No architectural diagram** showing how components interact
   - **No example EvidencePack** showing what the structured representation looks like
   - **No example prompts** demonstrating schema-guided claim checking
   - **No result visualizations** (even hypothetical ones showing expected outcomes)
   - The flowchart is too high-level to convey technical details

4. **Vague Terminology:**
   - "Lightweight SMT" - what makes it lightweight?
   - "Targeted symbolic execution" - how is it targeted?
   - "Minimal slice" - what defines minimal?
   - "Progressive prompting" - what is the progression strategy?
   - "Schema-guided claim checking" - what is the schema?
   - These terms are used repeatedly without precise definitions

5. **Unclear Problem Formulation:**
   - Three formulations mentioned (classification, ranking, selective prediction) but never clarified which one EVICT optimizes
   - The mathematical notation (C_i, Y_i) is introduced but never used consistently
   - No formal definition of "risk," "coverage," or "calibration error" despite being central concepts

6. **Weak Integration Narrative:**
   - The proposal presents four main contributions but doesn't clearly explain how they work together
   - The relationship between contrastive learning and the main LLM verifier is unclear
   - How does calibration interact with symbolic verification?
   - The integration story is more "we combine these techniques" than "these techniques synergize in the following ways"

7. **Citation and Reference Issues:**
   - Many informal URLs rather than proper academic citations
   - Several key references are unpublished preprints (LLM4PFA, LLM4FPM, Tencent study)
   - Some citations are to project pages or blog posts rather than peer-reviewed papers
   - Inconsistent citation format throughout

8. **No Preliminary Results:**
   - The proposal is entirely forward-looking with no pilot experiments or preliminary results
   - Even small-scale proof-of-concept results would greatly strengthen credibility
   - Figures showing expected result patterns (e.g., risk-coverage curves) would help readers understand the approach

9. **Abstract and Introduction Missing:**
   - The document starts with "Executive recommendation" rather than a traditional abstract
   - No clear introduction section setting up the problem, contributions, and paper structure
   - For a conference paper, these would be essential

10. **Writing Quality Issues:**
    - Some sentences are overly long and complex
    - Occasional grammatical issues ("the same rule patterns can produce both actionable and non-actionable outcomes, implying context matters beyond rule id")
    - Inconsistent terminology (FP vs. false positive, TP vs. true positive)
    - Some claims are imprecise ("drastically raise precision" - how much is drastic?)

## Contribution: 3/5

**Assessment from Positioning and Broader Impact Perspective:**

**Contribution 1: Risk-Controlled Adjudication**
- **Positioning:** This is the strongest contribution and addresses a clear gap. No existing LLM-based static analysis work systematically applies selective prediction with calibrated abstention.
- **Clarity:** The motivation is clear (enable safe automation with human oversight), but the technical approach lacks detail.
- **Impact:** High potential practical impact for industrial adoption. Scientific impact depends on theoretical development.

**Contribution 2: False-Positive Signature Learning**
- **Positioning:** Contrastive learning for FP patterns is novel to this domain, but the proposal doesn't clearly explain why it's better than existing supervised approaches.
- **Clarity:** The description is vague. What exactly is a "false-positive signature"? How are they represented? What makes them transferable?
- **Impact:** Moderate potential impact if FP patterns are indeed learnable across projects, but this assumption is untested.

**Contribution 3: Neuro-Symbolic Integration with Conditional Invocation**
- **Positioning:** Neuro-symbolic approaches exist (AdaTaint, WARP, Laurel), but conditional invocation based on uncertainty is less explored.
- **Clarity:** The description is too vague to assess. "Lightweight" and "targeted" are not defined. When exactly are symbolic checks invoked?
- **Impact:** Moderate practical impact if cost-benefit tradeoffs are favorable, but this needs empirical validation.

**Contribution 4: Standardized Evidence Interchange**
- **Positioning:** SARIF is an existing standard; using it is good practice but not a research contribution.
- **Clarity:** The benefits are clearly stated (reproducibility, cross-tool comparison), but this is primarily engineering.
- **Impact:** High practical value for the community, low scientific novelty.

**Overall Contribution Assessment:**
The proposal makes one strong contribution (selective prediction) and several moderate contributions (contrastive learning, conditional symbolic verification, standardized evaluation). However, the presentation doesn't clearly articulate why these contributions matter or how they advance the state of the art beyond recent strong baselines.

**Comparison to Recent Work:**
The proposal's positioning section does a good job of surveying recent work, but the comparison is primarily descriptive rather than analytical. A clearer statement of "System X does A and B; System Y does B and C; EVICT uniquely does A, B, C, and D" would help readers understand the contribution.

## Strengths

1. **Important and Timely Problem:** Static analysis false positives are a major pain point with clear industrial demand. The problem is well-motivated with concrete evidence (Tencent: 10-20 min/alarm).

2. **Strong Literature Survey:** Comprehensive coverage of recent work (2022-2025) with specific comparisons. The proposal demonstrates deep familiarity with the field.

3. **Novel Focus on Selective Prediction:** Calibrated abstention for alert triage is genuinely underexplored and could enable safer automation in high-stakes security contexts.

4. **Rigorous Evaluation Philosophy:** Emphasis on leakage-resistant protocols, cross-project generalization, and multiple complementary datasets addresses known evaluation issues.

5. **Honest Discussion of Challenges:** The proposal explicitly acknowledges limitations (hallucinations, distribution shift, label noise, scalability) and proposes mitigations.

6. **Practical Grounding:** Inclusion of cost-benefit metrics (minutes saved, dollars per alert) and industrial evidence shows awareness of real-world deployment concerns.

7. **Reproducibility Focus:** SARIF standardization, public datasets, and emphasis on sharing code/prompts/protocols would improve reproducibility.

8. **Ethical Awareness:** The proposal considers safety implications (missed true positives in security contexts) and proposes mitigations (abstention, auditing).

9. **Comprehensive Baseline Plan:** Comparison to static analyzers alone, heuristic filters, classic ML, recent LLM systems, and neuro-symbolic approaches provides thorough coverage.

10. **Realistic Resource Planning:** The Gantt chart and resource estimates show careful planning and awareness of implementation challenges.

## Weaknesses

1. **Presentation Issues:** Excessive length, inconsistent detail, missing visuals, vague terminology, and unclear problem formulation make the proposal difficult to assess (see Presentation section for details).

2. **Overstated Novelty Claims:** Evidence-conditioned verification is presented as novel, but multiple recent systems (LLM4PFA, LLM4FPM, BugLens, AdaTaint) already use this approach. The proposal should more clearly distinguish EVICT's contributions.

3. **Unclear Advantage Over Strong Baselines:** Recent work achieves 94-99% precision. The proposal doesn't explain what performance level would constitute success or why EVICT will outperform these strong baselines.

4. **Weak Integration Narrative:** The proposal lists four contributions but doesn't clearly explain how they synergize or why integration is better than using components independently.

5. **Missing Theoretical Foundations:** Selective prediction is presented informally without formal definitions, guarantees, or optimality analysis. This weakens the scientific contribution.

6. **No Preliminary Results:** The proposal is entirely prospective. Even small-scale pilot experiments would greatly increase confidence in feasibility.

7. **Label Quality Issues Acknowledged but Not Addressed:** All datasets have known label problems, but the proposal only acknowledges this without proposing systematic solutions.

8. **Vague Technical Details:** Key components (EvidencePack construction, schema-guided prompting, conditional symbolic invocation, contrastive learning) lack precise specifications.

9. **Questionable Assumptions:**
   - That FP "signatures" are learnable and transferable across projects (untested)
   - That symbolic checks can be made "lightweight" enough for practical use (unsubstantiated)
   - That LLM calibration techniques will transfer effectively to code analysis (unvalidated)

10. **Scope Too Ambitious:** Integrating evidence extraction, LLM reasoning, calibration, contrastive learning, symbolic verification, and multi-analyzer support in 6 months may be unrealistic.

11. **Limited Generalization Discussion:** Focus on Java (NASCAR, CWE-Bench-Java) raises questions about applicability to C/C++, Python, etc. Cross-language generalization is not addressed.

12. **Incomplete Broader Impact Analysis:** The ethical considerations section is brief and somewhat superficial. Deeper analysis of security implications, potential for misuse, and societal impacts would strengthen this section.

13. **Reproducibility Challenges Not Fully Addressed:** LLM non-determinism, API version changes, and lack of logit access pose significant reproducibility challenges. The proposal acknowledges these but doesn't provide concrete solutions.

14. **Statistical Issues:** With only 120 samples in CWE-Bench-Java, cross-project evaluation will have limited statistical power. No power analysis is provided.

15. **Missing Failure Analysis:** No discussion of when EVICT is expected to fail, what bug types are hardest, or how performance varies across categories.

## Suggestions

### Critical for Improving Presentation

1. **Restructure for Conference Format:**
   - Add abstract (150-200 words) summarizing problem, approach, contributions, and expected results
   - Add introduction (1-1.5 pages) with clear problem statement, motivating example, contributions list, and paper structure
   - Move detailed literature review to related work section (1-1.5 pages), focusing on key comparisons
   - Condense method section to core technical content (2-3 pages)
   - Move dataset details, timeline, and resource estimates to supplementary material
   - Target 9 pages + references total

2. **Add Visual Elements:**
   - System architecture diagram showing component interactions
   - Example EvidencePack with actual code snippet, slice, flow, and constraints
   - Example schema-guided prompt with LLM response
   - Hypothetical result visualizations (risk-coverage curves, calibration plots)
   - Decision tree or flowchart for conditional symbolic invocation

3. **Clarify Problem Formulation:**
   - Choose one primary formulation (selective prediction) and formalize it mathematically
   - Define risk, coverage, calibration error, and optimality criteria precisely
   - Use consistent mathematical notation throughout
   - Provide formal problem statement: "Given X, output Y, such that Z is optimized subject to constraints W"

4. **Define Technical Terms Precisely:**
   - "Lightweight SMT": specify timeout, memory limits, solver configuration
   - "Targeted symbolic execution": specify depth limits, path pruning strategy, scope
   - "Minimal slice": define minimality criterion (e.g., smallest slice preserving dependencies)
   - "Progressive prompting": specify iteration limit, termination condition, context expansion strategy
   - "Schema-guided claim checking": provide the actual schema structure

5. **Strengthen Integration Narrative:**
   - Explain how components synergize: "Calibration enables conditional symbolic invocation, which reduces costs while maintaining safety"
   - Provide concrete example: "When the LLM is uncertain (entropy > threshold), invoke SMT to validate path feasibility, which resolves X% of uncertain cases"
   - Discuss emergent benefits: "Integration enables cost-benefit tradeoffs not possible with individual components"

### Important for Strengthening Contribution

6. **Sharpen Novelty Claims:**
   - Clearly distinguish EVICT from recent systems: "Unlike LLM4FPM which focuses on context extraction, EVICT adds calibrated abstention and conditional symbolic verification"
   - Focus on selective prediction as primary contribution: "Our main contribution is formalizing alert triage as selective prediction with calibrated abstention"
   - Acknowledge what's not novel: "Evidence-based LLM verification is established (LLM4PFA, BugLens); our contribution is adding risk control"

7. **Provide Preliminary Results:**
   - Conduct small-scale experiments on Juliet (100-1000 samples)
   - Show that evidence-conditioned prompting outperforms simple prompting
   - Demonstrate that calibration improves reliability
   - Compare to at least one recent baseline (e.g., LLM4FPM)
   - Include in paper as "Preliminary Results" section to establish feasibility

8. **Develop Theoretical Foundations:**
   - Formalize selective prediction for alert triage with mathematical definitions
   - Prove theoretical guarantees (e.g., coverage bounds, risk bounds under assumptions)
   - Characterize when abstention is optimal given cost model
   - This would substantially strengthen the scientific contribution

9. **Clarify Expected Performance:**
   - State what performance level would demonstrate EVICT's value
   - Explain why EVICT might outperform recent baselines despite their 94-99% precision
   - Provide analysis: "Baselines achieve high precision on Juliet but may struggle with cross-project generalization; EVICT's contrastive learning should help"

10. **Expand Broader Impact Analysis:**
    - Discuss security implications more deeply: what happens if EVICT misses critical vulnerabilities?
    - Consider potential for misuse: could attackers exploit EVICT's weaknesses?
    - Analyze societal impacts: does automation reduce jobs or change developer workflows?
    - Discuss fairness: does performance vary across project types, organizations, or communities?
    - Consider environmental impact: what is the carbon footprint of processing millions of alerts?

### Useful for Improving Quality

11. **Improve Writing Quality:**
    - Break up long, complex sentences
    - Use consistent terminology (choose "FP" or "false positive" and stick with it)
    - Define all acronyms on first use
    - Proofread for grammatical errors
    - Use active voice where possible ("we propose" rather than "is proposed")

12. **Strengthen Citations:**
    - Convert informal URLs to proper academic citations
    - For preprints, indicate status: "LLM4FPM (arXiv preprint, under review)"
    - Prioritize peer-reviewed sources over blog posts or project pages
    - Use consistent citation format throughout

13. **Add Failure Analysis:**
    - Discuss when EVICT is expected to fail
    - Analyze which bug types are hardest (e.g., concurrency bugs, algorithmic issues)
    - Characterize abstention patterns (when does the system abstain?)
    - Identify limitations explicitly

14. **Address Generalization:**
    - Discuss applicability to other languages (C/C++, Python, JavaScript)
    - Analyze language-specific challenges
    - Consider including C/C++ evaluation if feasible
    - Discuss generalization to other program analysis tasks beyond alert triage

15. **Improve Reproducibility Discussion:**
    - Propose concrete solutions to LLM non-determinism (e.g., temperature=0, fixed seeds, multiple runs with variance reporting)
    - Discuss how to handle API version changes (version pinning, fallback strategies)
    - Explain how to construct calibration sets without leakage
    - Provide detailed reproducibility checklist

## Questions

1. **Problem Formulation:** Is EVICT optimizing for classification accuracy, ranking quality, or risk-coverage tradeoffs? Can you formalize this mathematically?

2. **Novelty:** How exactly does EVICT differ from LLM4FPM (which also uses evidence-based context extraction) and LLM4PFA (which also uses path feasibility reasoning)?

3. **Performance Expectations:** Given that recent work achieves 94-99% precision, what performance level would demonstrate EVICT's value? What improvement is needed to justify the added complexity?

4. **Preliminary Results:** Do you have any pilot experiments, even on a small scale? Can you show that the approach is feasible?

5. **Integration:** How do the four contributions (selective prediction, contrastive learning, symbolic verification, SARIF) work together? What are the emergent benefits of integration?

6. **Selective Prediction Theory:** Can you provide formal definitions of risk and coverage? What theoretical guarantees can you prove?

7. **Calibration:** How will you ensure that calibration methods provide valid guarantees for alert triage? What calibration set will you use?

8. **Contrastive Learning:** What evidence suggests that FP patterns are consistent across projects? Have you analyzed FP signature transferability?

9. **Symbolic Verification:** When exactly are symbolic checks invoked? What is the decision algorithm? What makes the approach "lightweight" and "targeted"?

10. **Cost-Benefit:** What is the cost model for deciding when symbolic verification is worth the overhead? How do you balance verification cost against error reduction?

11. **Label Quality:** How will you address label quality issues in NASCAR (actionable ≠ bug), DZA (weak labels), and Juliet (864 documented FPs)?

12. **Scalability:** Can the approach scale to 1M warnings in reasonable time and cost? What are the computational requirements?

13. **Abstention Rate:** What abstention rate do you expect? Is 50% abstention acceptable? How do you balance automation vs. manual workload?

14. **Failure Modes:** When does EVICT fail? What bug types are hardest? How does performance vary across CWE categories?

15. **Generalization:** How well will the approach generalize to C/C++, Python, and other languages? What are language-specific challenges?

16. **Ethical Implications:** What happens if EVICT misses critical security vulnerabilities? How do you mitigate this risk?

17. **Reproducibility:** How will you handle LLM non-determinism and API version changes to ensure reproducibility?

18. **Statistical Power:** With only 120 samples in CWE-Bench-Java, how will you ensure sufficient power for cross-project evaluation?

19. **Baseline Implementation:** How will you implement recent baselines (LLM4FPM, LLM4PFA) fairly for comparison? Will you use the same LLM and prompts?

20. **Timeline Feasibility:** Is 6 months realistic for integrating LLMs, SMT solvers, symbolic execution, calibration, and multi-analyzer support?

## Rating: 5/10 (Borderline Reject)

**Justification:**

This proposal addresses an important problem (static analysis false positive reduction) and makes a valuable contribution by introducing calibrated selective prediction to LLM-based alert triage. The literature review is comprehensive, the evaluation philosophy is rigorous, and the practical grounding is strong. However, several significant weaknesses prevent me from recommending acceptance:

**Primary concerns:**
1. **Presentation issues:** The proposal is too long, lacks key visual elements, uses vague terminology, and doesn't clearly formulate the problem. For a NeurIPS submission, substantial revision would be needed.

2. **Unclear advantage over strong recent baselines:** Recent work (LLM4FPM, LLM4PFA, BugLens, Tencent study) achieves 94-99% precision. The proposal doesn't explain why EVICT will outperform or what performance level would constitute success.

3. **Overstated novelty:** Evidence-conditioned verification is presented as novel, but multiple recent systems already use this approach. The proposal should more clearly distinguish EVICT's unique contributions.

4. **No preliminary results:** The proposal is entirely prospective. Even small-scale pilot experiments would greatly increase confidence in feasibility and potential impact.

5. **Weak integration narrative:** The proposal lists four contributions but doesn't clearly explain how they synergize or why integration is better than using components independently.

**Secondary concerns:**
- Missing theoretical foundations for selective prediction
- Vague technical details for key components
- Label quality issues acknowledged but not addressed
- Ambitious scope may be unrealistic for 6-month timeline
- Limited discussion of cross-language generalization

**Positive aspects:**
- Selective prediction is a genuine contribution addressing a clear gap
- Rigorous evaluation philosophy with leakage-resistant protocols
- Strong awareness of recent work and evaluation challenges
- Practical grounding with cost-benefit focus
- Honest discussion of limitations

**Recommendation:** This work has potential but needs substantial revision before it's ready for publication at a top-tier venue like NeurIPS. I recommend:
1. Conduct preliminary experiments demonstrating feasibility and showing promise vs. baselines
2. Restructure for conference format with clear problem formulation and visual elements
3. Sharpen novelty claims to clearly distinguish from recent work
4. Develop theoretical foundations for selective prediction
5. Consider alternative venues (ICSE, FSE, ASE) that may be more receptive to systems contributions

With these revisions, this could become a strong paper. In its current form, it's a borderline reject.

## Confidence: 4/5 (High Confidence)

I am confident in this assessment. I have expertise in research communication, positioning within related work, and broader impact analysis for ML systems. I am familiar with the static analysis and LLM-for-code literature. My main uncertainty is whether the authors have preliminary results or additional technical details not included in this proposal that would substantially strengthen the work. However, based on the submitted material, my assessment stands. The presentation and positioning issues are clear and would need to be addressed regardless of additional results.
