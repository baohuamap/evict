# EVICT Proposal: Quick Reference Guide to Critical Improvements

## 🚨 Critical Issues from Peer Review (Why it was REJECTED)

### Reviewer Scores:
- **Reviewer 1 (Methods & Theory)**: 4/10 - Weak Reject
- **Reviewer 2 (Experiments & Practical Impact)**: 5/10 - Borderline Reject  
- **Reviewer 3 (Clarity & Positioning)**: 5/10 - Borderline Reject
- **Meta-Review Decision**: REJECT

### Top 3 Critical Weaknesses:
1. ❌ **NO PRELIMINARY RESULTS** - Entirely prospective, no feasibility demonstration
2. ❌ **MISSING THEORETICAL FOUNDATIONS** - No formal definitions, guarantees, or optimality analysis
3. ❌ **UNCLEAR ADVANTAGE** - Recent work achieves 94-99% precision; why will EVICT be better?

---

## ✅ MUST-HAVE Improvements for NeurIPS Acceptance

### 1. Add Theoretical Foundations (Addresses Reviewer 1's Main Concern)

**What to Add:**
- **Formal Problem Definition**: Define selective classifier as pair (f,g) with selective risk R_s and coverage θ
- **Theorem 1**: PAC bound on selective risk with sample complexity O((d/ε²)log(1/δ))
- **Theorem 2**: Risk-coverage tradeoff showing R_s(θ) ≤ R_full + O(√((1-θ)/θ))
- **Theorem 3**: Conformal prediction guarantee for finite-sample error control
- **Theorem 4**: Surrogate consistency for predictor-rejector training
- **Complexity Analysis**: O(n·T_LLM + k·T_symbolic) where k is selective invocation rate

**Key Citations:**
- El-Yaniv et al. (JMLR 2010) - Selective prediction foundations
- Wald et al. (NeurIPS 2021) - Calibrated selective classification
- Angelopoulos & Bates (2023) - Conformal prediction tutorial
- Mao & Mohri (2023) - Predictor-rejector multi-class abstention

**Impact**: Transforms from engineering contribution to theoretical contribution suitable for NeurIPS

---

### 2. Conduct Preliminary Experiments (Addresses ALL Reviewers' Concerns)

**Minimum Viable Experiments (1-2 weeks each):**

**Experiment 1: Evidence-Conditioned Prompting Works**
- Dataset: Juliet CWE-89 SQL injection (100 true bugs, 100 false positives)
- Compare: (a) baseline LLM, (b) +code snippet, (c) +EvidencePack
- Metric: Precision, Recall, F1
- Expected: EvidencePack improves precision by 15-20%

**Experiment 2: Calibration Improves Reliability**
- Use Experiment 1 setup
- Compare: (a) raw LLM scores, (b) temperature scaling, (c) conformal prediction
- Metric: ECE (Expected Calibration Error), Brier score
- Expected: Conformal reduces ECE from 0.15 to 0.05

**Experiment 3: Selective Prediction Enables Risk-Coverage Tradeoff**
- Use calibrated scores from Experiment 2
- Vary rejection threshold, plot risk-coverage curve
- Compare to non-selective baseline
- Expected: At 80% coverage, selective risk < 5% vs 15% for full coverage

**Experiment 4: Symbolic Checks Reduce Hallucinations**
- Subset with infeasible paths (50 samples)
- Compare: (a) LLM only, (b) LLM + SMT validation
- Metric: False positive rate on infeasible paths
- Expected: SMT reduces FP rate from 30% to 5%

**Experiment 5: Comparison to Strong Baseline**
- Implement simplified LLM4PFA (path feasibility checking)
- Compare on same Juliet subset
- Metric: Precision, Recall, F1, Runtime
- Expected: EVICT matches precision with 2-3× speedup via selective symbolic checks

**Timeline**: 6-8 weeks for all 5 experiments

**Impact**: Demonstrates feasibility, validates core claims, shows advantage over baselines

---

### 3. Detailed Algorithmic Specifications (Addresses Reviewer 1 & 2)

**Algorithm 1: EvidencePack Construction**
```
Input: Alert a, Source code S, Analyzer trace T
Output: EvidencePack P

1. Extract alert metadata (rule, CWE, severity, location)
2. Compute minimal slice:
   - Statement-level slice around source/sink (±5 lines)
   - Dependency slice following analyzer flow
   - CPG-based slice (optional, if available)
3. Normalize flow trace:
   - Extract call chain from T
   - Identify taint edges and sanitizers
   - Format as structured JSON
4. Extract constraints:
   - Parse branch conditions along path
   - Simplify using symbolic execution engine
   - Represent as SMT-LIB format
5. Package as JSON with schema validation
Return P
```

**Algorithm 2: Schema-Guided Claim Verification**
```
Input: EvidencePack P, LLM model M
Output: (prediction, confidence, rationale)

1. Construct verification prompt:
   - System: "You are a security auditor..."
   - Evidence: Inject P fields (slice, trace, constraints)
   - Schema: Force structured output (JSON schema)
2. LLM query with schema constraints:
   - Restate analyzer claim
   - List preconditions for bug
   - Check each precondition against evidence
   - Output: TP/FP/ABSTAIN + confidence [0,1] + rationale
3. Parse and validate response
4. Apply calibration:
   - If logits available: temperature scaling
   - Else: conformal prediction on calibration set
5. Return (prediction, calibrated_confidence, rationale)
```

**Algorithm 3: Conditional Symbolic Invocation**
```
Input: Alert a, LLM confidence c, threshold τ_low, τ_high
Output: Final decision d

1. If c > τ_high:
   - Return LLM prediction (high confidence, no symbolic check)
2. Else if c < τ_low:
   - Return ABSTAIN (too uncertain, defer to human)
3. Else (τ_low ≤ c ≤ τ_high):
   - Determine check type:
     - If path-feasibility issue: invoke SMT solver
     - If data-flow issue: invoke sanitizer validator
   - Run symbolic check with timeout (5 seconds)
   - If check confirms LLM: return LLM prediction
   - If check contradicts: return opposite or ABSTAIN
   - If timeout: return ABSTAIN
4. Log decision and evidence for audit trail
```

**Impact**: Enables reproducibility, clarifies technical contributions

---

### 4. Sharpen Novelty Claims (Addresses Reviewer 3)

**Current Problem**: Overstated novelty - "evidence-conditioned verification" sounds novel but multiple recent systems already do this

**Revised Positioning**:

| Aspect | LLM4FPM | LLM4PFA | BugLens | AdaTaint | **EVICT (Novel)** |
|--------|---------|---------|---------|----------|-------------------|
| Evidence type | eCPG slice | Path constraints | Flow trace | Source/sink | **Unified EvidencePack** |
| Adjudication | Binary TP/FP | Iterative reasoning | Structured guidance | Adaptive rules | **Calibrated selective** |
| Uncertainty | None | None | None | None | **Conformal + abstention** |
| Symbolic integration | None | Full (expensive) | None | Adaptive (heuristic) | **Conditional (principled)** |
| Theoretical guarantees | None | None | None | None | **PAC bounds + conformal** |

**Primary Novel Contribution**: 
> "EVICT is the first LLM-based static analysis system with **formal selective prediction guarantees** (PAC bounds on selective risk, conformal finite-sample error control). While evidence-conditioned prompting is established, our **calibrated abstention with provable risk-coverage tradeoffs** is novel."

**Secondary Contributions**:
- Unified evidence representation (SARIF-based, cross-tool)
- Principled conditional symbolic invocation (cost-aware, threshold-based)
- Contrastive FP signature learning (domain adaptation for cross-project transfer)

**Impact**: Honest positioning, focuses on genuine novelty

---

### 5. Restructure for 9-Page NeurIPS Format (Addresses Reviewer 3)

**Current**: ~12 pages dense text, reads like grant proposal

**Target Structure** (9 pages + unlimited references):

```
Page 1: Abstract (250 words) + Introduction (0.75 pages)
  - Problem: Static analysis FPs waste developer time
  - Gap: Recent LLM work lacks formal guarantees
  - Solution: EVICT with selective prediction + conformal calibration
  - Contributions: (1) Theory, (2) Algorithms, (3) Experiments

Pages 2-3: Background & Related Work (1.5 pages)
  - Selective prediction theory (0.3 pages)
  - LLM for code analysis (0.5 pages)
  - Neuro-symbolic verification (0.3 pages)
  - Comparison table (0.4 pages)

Pages 3-5: Method (2 pages)
  - Problem formulation (0.5 pages) - formal definitions
  - EVICT architecture (0.5 pages) - Figure 1 (system diagram)
  - Algorithms 1-3 (1 page) - pseudocode boxes

Pages 5-6: Theoretical Analysis (1 page)
  - Theorem 1: PAC bound (0.25 pages)
  - Theorem 2: Risk-coverage tradeoff (0.25 pages)
  - Theorem 3: Conformal guarantee (0.25 pages)
  - Complexity analysis (0.25 pages)

Pages 6-8: Experiments (2 pages)
  - Setup: datasets, baselines, metrics (0.5 pages)
  - Results: Table 1 (main results), Figure 2 (risk-coverage curves) (1 page)
  - Ablations: Table 2 (component contributions) (0.5 pages)

Page 8-9: Discussion & Conclusion (1 page)
  - Key findings (0.3 pages)
  - Limitations & future work (0.3 pages)
  - Broader impact (0.2 pages)
  - Conclusion (0.2 pages)

Pages 10+: References (unlimited)

Supplementary Material (unlimited):
  - Detailed proofs
  - Full prompt templates
  - Extended experimental results
  - Implementation details
  - Reproducibility checklist
```

**Essential Figures/Tables** (minimum 8):
1. **Figure 1**: EVICT system architecture (pipeline diagram)
2. **Figure 2**: Example EvidencePack (JSON visualization)
3. **Figure 3**: Schema-guided verification prompt (example)
4. **Figure 4**: Risk-coverage curves (selective vs. non-selective)
5. **Table 1**: Main results (precision/recall/F1 vs. baselines)
6. **Table 2**: Ablation study (component contributions)
7. **Table 3**: Comparison to related work (feature matrix)
8. **Figure 5**: Calibration plot (reliability diagram)

**Impact**: Professional presentation suitable for NeurIPS

---

## 📊 Success Criteria for Resubmission

### Minimum Bar for Acceptance:
1. ✅ Preliminary results on Juliet showing **15-20% precision improvement** over baseline
2. ✅ Formal theorems with **PAC bounds and conformal guarantees**
3. ✅ Risk-coverage curves showing **selective prediction works** (e.g., 5% error at 80% coverage vs 15% at 100%)
4. ✅ Comparison to **at least one strong baseline** (LLM4PFA or LLM4FPM)
5. ✅ **9-page format** with 8+ figures/tables
6. ✅ **Reproducibility**: code + data release commitment

### Stretch Goals for Strong Accept:
1. ⭐ Results on **all 4 datasets** (Juliet, NASCAR, D2A, CWE-Bench-Java)
2. ⭐ **State-of-the-art performance**: >95% precision at >90% recall
3. ⭐ **Cross-project generalization**: train on NASCAR, test on D2A
4. ⭐ **Cost analysis**: show 10× speedup vs. full symbolic verification
5. ⭐ **Failure analysis**: characterize when EVICT fails

---

## 🎯 6-Month Implementation Roadmap

### Month 1-2: Theory + Algorithms
- Week 1-2: Formalize selective prediction framework
- Week 3-4: Prove Theorems 1-4
- Week 5-6: Implement EvidencePack construction
- Week 7-8: Implement schema-guided verification

### Month 3-4: Preliminary Experiments
- Week 9-10: Experiment 1 (evidence-conditioned prompting)
- Week 11-12: Experiment 2 (calibration)
- Week 13-14: Experiment 3 (selective prediction)
- Week 15-16: Experiment 4-5 (symbolic checks + baseline comparison)

### Month 5: Full Evaluation
- Week 17-18: Scale to full Juliet dataset
- Week 19-20: Ablation studies
- Week 21-22: Cross-project evaluation (NASCAR→D2A)

### Month 6: Writing + Submission
- Week 23-24: Draft paper in NeurIPS format
- Week 25: Create all figures/tables
- Week 26: Internal review + revision
- Week 27: Submit to NeurIPS 2026

---

## 📚 Key Literature to Cite

### Theoretical Foundations (10 papers):
1. El-Yaniv & Wiener (JMLR 2010) - Selective prediction foundations
2. Geifman & El-Yaniv (ICML 2017) - SelectiveNet
3. Wald et al. (NeurIPS 2021) - Calibrated selective classification
4. Mao & Mohri (2023) - Predictor-rejector abstention
5. Angelopoulos & Bates (2023) - Conformal prediction tutorial
6. Angelopoulos et al. (2022) - Conformal risk control
7. Gangrade et al. (JMLR 2021) - One-sided prediction
8. Gelbhart & El-Yaniv (JMLR 2019) - Disagreement coefficient
9. Löfström et al. (2025) - Classification with reject option
10. Shafer & Vovk (2008) - Tutorial on conformal prediction

### LLM for Code Analysis (8 papers):
11. Lin et al. (2025) - AdaTaint (LLM-driven adaptive taint)
12. Iranmanesh & Wilson (2025) - ZeroFalse (LLM precision improvement)
13. Li et al. (2024) - Uncertainty awareness in code LLMs
14. Hu et al. (2023) - CodeS (distribution shift benchmark)
15. Li et al. (2023) - LLM4FPM (eCPG-based slicing)
16. Chen et al. (2024) - LLM4PFA (path feasibility analysis)
17. Mohajer et al. (2023) - SkipAnalyzer (embodied agent)
18. Wagner et al. (2025) - Complementary security analysis

### Neuro-Symbolic (5 papers):
19. Si et al. (2022) - Neural termination analysis
20. Yang (2025) - Learning-directed systems with certificates
21. Bridging correctness gap (2025) - Neuro-symbolic synthesis
22. LLMDFA (NeurIPS 2024) - Decomposition + tool checks
23. LLMSAN (EMNLP 2024) - Sanitizers for hallucinated paths

### Datasets & Benchmarks (4 papers):
24. D2A (2021) - Differential analysis labeling
25. Juliet/SARD - Synthetic bug benchmarks
26. NASCAR - Large-scale actionability corpus
27. CWE-Bench-Java - Validated vulnerabilities

---

## 💡 Key Insights from Literature Review

### Recent Advances (2023-2025):
1. **Hybrid pipelines** (LLM + static analysis) achieve 94-99% precision
2. **Adaptive neuro-symbolic** methods reduce FPs while preserving recall
3. **Two-phase training** (synthetic→real) mitigates distribution shift
4. **Probabilistic methods** improve calibration in code LLMs
5. **CodeS benchmark** defines 5 types of distribution shift for code

### Gaps EVICT Addresses:
1. ❌ **No formal selective prediction** in LLM-based static analysis
2. ❌ **No provable calibration guarantees** (conformal, PAC bounds)
3. ❌ **No principled cost model** for symbolic check invocation
4. ❌ **No cross-project generalization** studies with rigorous splits
5. ❌ **No standardized evaluation** (most use different datasets/metrics)

### Methodological Best Practices:
1. ✅ **Two-phase training** to handle synthetic→real shift
2. ✅ **Contrastive learning** for robust representations
3. ✅ **Held-out calibration sets** for conformal prediction
4. ✅ **Project-level splits** to avoid leakage
5. ✅ **Risk-coverage curves** for selective prediction evaluation
6. ✅ **Large-scale evaluation** (1000s of warnings, not toy examples)
7. ✅ **Ablation studies** to isolate component contributions

---

## 🚀 Quick Start Actions (Next 2 Weeks)

### Week 1: Theory
- [ ] Write formal problem definition (2 pages)
- [ ] Prove Theorem 1 (PAC bound) - adapt from El-Yaniv (2010)
- [ ] Prove Theorem 2 (risk-coverage) - adapt from Wald et al. (2021)
- [ ] Draft theory section for paper (1 page)

### Week 2: Pilot Experiment
- [ ] Download Juliet CWE-89 dataset (200 samples)
- [ ] Implement baseline LLM prompting (GPT-4)
- [ ] Implement EvidencePack construction (minimal version)
- [ ] Run Experiment 1, generate results table
- [ ] Create Figure: precision comparison (baseline vs. evidence-conditioned)

**Deliverable**: 2-page theory draft + 1-page preliminary results

---

## 📞 Contact & Resources

**Original Proposal**: `/home/sandbox/Evidence-Conditioned LLM Investigation for Static-Analysis Alert Triage.pdf`

**Generated Artifacts**:
- Full improved proposal: `/home/sandbox/improved_evict_proposal.md`
- Peer review reports: `/home/sandbox/meta_review.md`, `reviewer_1_report.md`, `reviewer_2_report.md`, `reviewer_3_report.md`
- Literature insights: `/home/sandbox/literature_insights.md`, `/home/sandbox/selective_prediction_theory.md`
- Research summary: `/home/sandbox/research_proposal_summary.md`

**Literature Search Results**:
- 609 papers on LLM code analysis, selective prediction, etc.: `/home/sandbox/combined_neurips_quality_literature_review.papertable`
- 220 papers on selective/conformal prediction theory: `/home/sandbox/combined_selective_conformal_results.papertable`

---

## ✨ Bottom Line

**Original Status**: REJECTED (scores 4-5/10)
- No preliminary results
- No theoretical foundations  
- Unclear advantage over 94-99% precision baselines

**Path to Acceptance**:
1. Add formal theory (Theorems 1-4) → Addresses Reviewer 1
2. Run 5 pilot experiments (6-8 weeks) → Addresses all reviewers
3. Show 15-20% precision improvement → Demonstrates advantage
4. Restructure to 9 pages with 8 figures → Addresses Reviewer 3
5. Sharpen novelty to "first with formal selective prediction guarantees"

**Timeline**: 6 months to NeurIPS-ready submission

**Confidence**: With these changes, strong chance of acceptance (7-8/10 scores)
