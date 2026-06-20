# Review 2 — Selective Prediction / ML Theory Perspective

**Rating:** 5 — Borderline reject
**Confidence:** 4 — Confident

---

## Summary

The paper proposes EVICT, a pipeline for triaging static-analysis false positives. It casts triage as selective prediction with asymmetric costs, applies conformal prediction to produce calibrated abstention, and falls back to symbolic verification (SMT + bounded symbolic execution) on uncertain or high-severity cases. Three theorems are stated: a VC-style selective risk bound, a standard conformal validity guarantee, and a cost-sensitive thresholding rule. Preliminary results on 1,000 synthetic Juliet samples show modest precision and ECE gains over an evidence-free baseline.

---

## Strengths

1. **Correct framing.** Recasting alert triage as selective prediction is the right conceptual move. Forced classification is unsuitable when evidence quality varies widely, and the paper explains this clearly.

2. **Tight theorem–design alignment.** Each theoretical result directly motivates a design choice: Theorem 1 justifies explicit abstention over post-hoc thresholding, Theorem 2 justifies conformal calibration, Theorem 3 justifies thresholding calibrated scores over raw logits.

3. **Honest scoping.** The paper is unusually candid about what the preliminary experiments do and do not establish. The distinction between "mechanism validation" and "deployment study" is stated explicitly, which is appreciated.

4. **Appendix depth.** Algorithm listings, calibration procedures, and prompt templates are detailed enough to enable replication, which is rare in systems-style ML papers.

---

## Weaknesses

### W1 — Theorem 1 is too weak to be informative

The VC-style selective risk bound (Theorem 1) is a direct corollary of Elyaniv & Wiener (2010) specialized to the cost-sensitive case. The VC dimension $d$ is not bounded, discussed, or approximated for any realistic model class used in EVICT (a GPT-4-class LLM + a threshold function on its logits). For such models $d$ is vacuously large, making the bound trivially loose. The paper acknowledges this in one sentence ("most useful as a structural justification") but never follows up with an alternative — e.g., PAC-Bayes bounds, algorithmic stability arguments, or even an empirical coverage calibration plot that substitutes for the bound. The theorem appears more as formal decoration than a load-bearing contribution.

**Suggested fix:** Either replace Theorem 1 with a more informative bound (algorithm-dependent, PAC-Bayes, or Rademacher-complexity-based for the rejector class alone) or demote it explicitly to a motivation/intuition role and add an empirical coverage calibration diagnostic that serves the practical purpose instead.

### W2 — Conformal validity is standard and the construction is underspecified

Theorem 2 is a verbatim restatement of the standard split-conformal guarantee (Vovk et al. 2005; Angelopoulos & Bates 2021). The only nontrivial design choice is the nonconformity score, but the paper gives two options (label margin for logit-access; vote share for API-only) without:
- Analyzing which choice leads to smaller prediction sets (and hence higher coverage) in practice.
- Justifying why these two are preferred over entropy, margin-to-second-class, or self-calibrated methods.
- Reporting how frequently the conformal set is a singleton versus empty versus multi-label in the preliminary study. This determines whether abstention is driven by conformal conservatism or by inherent ambiguity.

**Suggested fix:** Add a table or figure reporting singleton-set frequency, empty-set frequency, and two-label-set frequency by CWE category and model-access mode. This is the key diagnostic for conformal triage and is missing entirely.

### W3 — The interaction between conformal calibration and symbolic escalation is still insufficiently resolved

The appendix (§A.1.4) states the sequencing: conformal acceptance → abstention → symbolic audit. The main paper's theory section claims validity "for the pre-escalation selective predictor." But Table 1 reports a single EVICT (Full) precision of 91.2% without distinguishing pre- and post-escalation, and Figure 1 (risk–coverage curves) presumably combines both stages. If the 2.8 pp precision gain attributed to symbolic checks accrues inside the abstention set, the reported precision is not covered by the conformal guarantee, yet the paper presents it as a unified result. A reader could reasonably misconstrue the guarantee as applying to the full pipeline.

**Suggested fix:** Report pre-escalation and post-escalation precision/coverage/ECE separately in Table 1. Clarify in the caption which rows correspond to which guarantee scope. This does not require additional experiments — the split already exists.

### W4 — 1,000 synthetic samples is insufficient for the paper's claims

The empirical section itself acknowledges this ("A real submission would still require genuine cross-project results"). Yet the paper makes deployment-oriented claims in the abstract and introduction (e.g., "safe automation," "finite-sample validity") without qualifying them as pertaining only to the Juliet prototype. The evaluation plan is thorough, but a plan is not evidence. The gap between claim scope and evidence scope is too large for a NeurIPS submission.

### W5 — Simulated baselines undermine comparative claims

Table 1 includes five rows explicitly labeled "(sim.)": LLM4FPM, LLM4PFA, AdaTaint-Style, and Agentic LLM Workflow. The paper states these are "illustrative simulated baselines included for this mock submission." Reporting fabricated numbers in a results table — even with a footnote — is methodologically inappropriate for peer review, regardless of submission stage. The entire comparative story in §5 rests on numbers the authors generated themselves. This makes it impossible to evaluate the incremental contribution of EVICT over the prior state of the art.

**Suggested fix:** Remove simulated rows from Table 1, or replace them with a direct citation to published numbers from those papers (with appropriate caveats about dataset/setup differences). The narrative can still describe the intended comparison structure without presenting fabricated figures as data.

---

## Questions for Authors

1. What is the singleton-set frequency by CWE category and model-access mode in the preliminary study? How does this break down into empty sets vs. multi-label sets?

2. Theorem 1: Can you give any bound on the effective VC dimension of the rejector class used in EVICT? Even a rough argument (e.g., the rejector is a threshold on a one-dimensional calibrated score, so $d=1$) would make the theorem substantive.

3. In Table 1, EVICT (No Symb.) has lower precision than EVICT (Full) but the same coverage. Can you confirm this gain is entirely from symbolic corrections inside the abstention set, so that the precision improvement does not affect the pre-escalation conformal guarantee?

4. How is temperature scaling integrated with conformal calibration? Temperature scaling produces better-ranked probabilities, but conformal validity does not require any specific score quality. Is temperature scaling applied before computing nonconformity scores, and if so, does it affect the singleton-set frequency in a meaningful way?

5. For the API-only self-consistency protocol: how many samples are drawn, and how sensitive are results to this number? A vote share from 3 samples is noisy; from 20 it is more stable but expensive.

---

## Overall Assessment

EVICT has the right conceptual architecture: the problem framing, the design decomposition, and the connection between theory and system components are all sound. The limitations are not in the ideas but in the evidence. The paper currently presents one small synthetic study, several fabricated comparison rows, and a theoretical analysis where the key bound is vacuously loose. For NeurIPS, the bar requires either (a) a genuinely novel theoretical contribution that goes beyond restating standard results, or (b) substantial empirical evidence across multiple realistic settings. EVICT currently satisfies neither bar. I encourage the authors to run the planned experiments, replace simulated baselines with real results, and resubmit with the complete evaluation. The framework is worth publishing; the current manuscript is not ready.

**Score: 5 — Borderline reject**
