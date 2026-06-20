# Review 3 — Software Engineering / Program Analysis Perspective

**Rating:** 6 — Weak accept
**Confidence:** 4 — Confident

---

## Summary

EVICT frames static-analysis alert triage as selective prediction, combines evidence-conditioned LLM reasoning with conformal calibration, and reserves symbolic verification for uncertain or high-risk cases. The paper derives supporting theory, presents a preliminary study on 1,000 Juliet samples, and describes a detailed evaluation plan for a larger study. I review from the perspective of program analysis and SE research.

---

## Strengths

1. **Right problem, right framing.** False-positive triage is a genuine bottleneck in industrial static analysis. The selective-prediction framing — "the model should say 'I don't know' rather than guess" — is exactly the right response to the over-confidence problems documented in prior LLM triage work. The paper makes this case persuasively.

2. **Evidence extraction is well-engineered.** The EvidencePack design (SARIF parsing, bounded forward/backward slices, normalized path constraints, language-specific AST tooling for Java and C/C++) reflects careful attention to what analyzers actually produce and where their outputs are reliable. Preserving incompleteness as a signal rather than hiding it is an important design choice.

3. **Schema-guided prompting grounded in bug preconditions.** Requiring the model to enumerate and check bug preconditions against extracted evidence — rather than asking whether the alert "looks plausible" — is a principled improvement over free-form chain-of-thought. The structure makes failures inspectable.

4. **Selective symbolic escalation is the right tradeoff.** Applying SMT + symbolic execution to 18.4% of alerts, rather than universally, is the operationally correct design given solver cost. The framing of symbolic tools as targeted auditors rather than universal verifiers is coherent and practical.

5. **Limitations are honestly stated.** The paper explicitly acknowledges Juliet's limitations (synthetic, single analyzer, no cross-project signal), flags the simulated baselines, and defers deployment claims to the planned evaluation. This intellectual honesty is notable and appropriate.

---

## Weaknesses

### W1 — Juliet is too easy and too unlike real static analysis workloads

Juliet is a synthetic suite designed to exercise specific CWE patterns. Alerts from real analyzers on Juliet are typically well-localized, have clean path evidence, and have balanced TP/FP ratios by construction. These conditions are unusually favorable for EVICT:
- Real-world analyzers on production code produce highly imbalanced alert populations (often 60–90% FP).
- Path evidence is frequently incomplete, cross-function, or analyzer-internal and not SARIF-exportable.
- CWE-89 (SQL injection) and CWE-78 (OS command injection) in Juliet often have explicit taint sources that an LLM can identify almost lexically, making structural evidence extraction less critical.

The paper acknowledges this but does not quantify how favorable Juliet is relative to the planned NASCAR and DZA datasets. Without this context, the reader cannot calibrate how much of the 91.2% precision reflects EVICT's design versus the simplicity of the task.

**Suggested fix:** Add one or two sentences characterizing the alert-complexity and evidence-completeness distribution in the Juliet sample (e.g., what fraction of alerts had complete SARIF paths, what the TP/FP ratio was before and after filtering). This would help readers assess the scope of the preliminary result.

### W2 — No ablation of evidence component value at the bug-type level

Table 1 shows aggregate precision gains from evidence conditioning, but the value of structured slices, flow summaries, and path constraints presumably varies across CWE families. CWE-190 (integer overflow) is much harder to verify from local slices than CWE-89 (SQL injection). A per-CWE breakdown of precision and abstention rate would reveal whether EVICT's gains are concentrated in easy cases or robust across the three families tested.

**Suggested fix:** Add a per-CWE breakdown in the appendix. This is a cheap analysis on an existing dataset that significantly enriches the mechanistic story.

### W3 — Incomplete evidence handling is described but not evaluated

The paper describes preserving incomplete evidence (from reflection, native calls, or unresolved paths) as a signal rather than hallucinating context. This is a good design. However, no result quantifies how often incompleteness occurs in the Juliet sample, whether incomplete-evidence alerts are more likely to be deferred, and whether the precision/abstention rate on incomplete-evidence alerts differs from the full population. Without this, the robustness claim remains unvalidated even in the preliminary study.

### W4 — Symbolic back-end characterization is thin

Table 2 reports 184 symbolic invocations, an 8.1% SMT UNKNOWN rate, 23 LLM error corrections, and 4.2s average verification time. But there is no breakdown of:
- How many invocations were triggered by abstention vs. high-severity dismissal.
- How many corrections came from SMT (feasibility) vs. bounded symbolic execution (counterexample search).
- Whether the 23 corrections were predominantly FP→TP or TP→FP flips (which has asymmetric safety implications).
- Whether the 15 UNKNOWN outcomes were treated as abstentions, or whether the system still committed to a label.

These details matter for understanding the safety properties of the symbolic escalation path.

### W5 — Prompt template is too brief for reproducibility

The appendix provides a single representative prompt:
> "You are reviewing a static-analysis alert. Restate the analyzer claim, list the conditions required for the alert to be a real bug, evaluate each condition using only the supplied evidence, then output one of TP, FP, or ABSTAIN with a confidence score and concise rationale."

This is the structural schema, but the actual prompt includes "rule-specific instructions, analyzer metadata, and optional self-consistency prompts." Readers cannot replicate EVICT without the full templates, at minimum one per CWE category. The stated intention to release code and prompts is welcome but does not substitute for sufficient detail in the submission.

---

## Questions for Authors

1. What is the TP/FP ratio in the Juliet sample, and what fraction of alerts had complete SARIF-reported paths? How does the abstention rate vary between complete- and incomplete-evidence alerts?

2. Can you report precision and abstention rate broken down by CWE category (CWE-89, CWE-78, CWE-190)? This would reveal whether gains are driven by easy taint cases or hold across all three families.

3. For the 23 LLM errors corrected by symbolic checks: how many were FP→TP corrections vs. TP→FP corrections? The asymmetric cost framing in the paper assigns higher penalty to false negatives, so the direction of symbolic corrections is directly relevant to the safety argument.

4. How does EVICT handle alerts for which the analyzer reports no path (no SARIF flow)? Does it fall back to PDG slicing for all such cases, or is the EvidencePack sometimes empty, and what happens at the calibration stage in that case?

5. On NASCAR or DZA, where labels come from developer triage or bug-fix deltas, do you plan to treat label noise explicitly (e.g., via confident learning or noise-transition modeling as mentioned in Algorithm A4)? How might label noise interact with conformal calibration if the calibration split contains mislabeled examples?

---

## Overall Assessment

EVICT addresses the right problem with a technically sound and practically motivated design. The combination of structured evidence extraction, schema-guided reasoning, conformal calibration, and selective symbolic escalation is coherent and well-reasoned. The preliminary results, taken at face value, support the mechanism. My main concerns are that the Juliet setup is too favorable to be convincing on its own, that several important mechanistic questions (per-CWE breakdown, incomplete-evidence behavior, symbolic correction direction) are unanswered, and that the simulated baselines should be removed from the results table.

Relative to the Stanford-1 review already in the system, I weight the program-analysis realism concerns more heavily and the theory concerns somewhat less. The conformal guarantee and VC bound are standard but appropriate; the more pressing gap is the absence of evidence that EVICT's design choices matter in realistic settings beyond synthetic Juliet.

I lean toward weak accept on the strength of the conceptual contribution and the honesty with which limitations are stated, conditional on the authors (a) removing simulated baseline rows from Table 1, (b) adding a per-CWE precision/abstention breakdown, and (c) providing a more complete prompt template in the appendix.

**Score: 6 — Weak accept**
