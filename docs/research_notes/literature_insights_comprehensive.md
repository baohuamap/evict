## TL;DR

EVICT sits at the intersection of three promising but partial trends: LLM-assisted false positive filtering, neurosymbolic grounding, and dataset-aware ML for static alerts. Existing work shows strong precision gains but lacks calibrated abstention, robust cross-project generalization, and standardized, high-quality benchmarks.

----

## LLM for static analysis

This section summarizes recent LLM-driven systems that aim to reduce static-analysis false positives and contrasts their methods, evidence, and limitations. The literature shows two dominant patterns: (a) LLMs as post-refiners that inspect analyzer outputs, and (b) hybrid/neuro-symbolic systems that validate model outputs against program facts or solvers.

- **BugLens post-refinement** uses structured multi-step LLM prompts to validate static taint-style warnings and reports a roughly seven-fold precision improvement on Linux-kernel taint-style findings while uncovering new vulnerabilities, showing the utility of LLM-guided structured reasoning for large codebases [1].  
- **Llm4sa bulk inspection** extracts relevant snippets via dependence traversal and applies LLM prompts to triage thousands of warnings, reporting high precision (81.1%) and recall (94.6%) on Juliet plus 11 real-world C/C++ projects, demonstrating scalability of prompt-based inspection when careful snippet extraction is used [2].  
- **LLift automated pipeline** couples a classical analyzer with an LLM to triage use-before-init bugs at scale in large codebases; it reports ~50% precision in a large Linux-kernel study and discovered 13 previously unknown UBI bugs, highlighting practical gains but also issues of non-determinism and problem-scope management [3].  
- **AdaTaint neurosymbolic** combines LLM-inferred source/sink specifications with symbolic constraint validation and reports a mean 43.7% false‑positive reduction and 11.2% recall improvement versus CodeQL/Joern and LLM-only baselines on Juliet, SV-COMP benchmarks, and three real projects, illustrating the value of grounding LLM outputs in program facts [4].  
- **LLM4PFA iterative feasibility** uses LLM agents for inter-procedural path feasibility reasoning and reports very large FP filtering (72–96%) on static-detection outputs in its evaluation, claiming substantial outperformance of baselines while missing few true positives in the reported experiments [5] [6].  
- **FAMiT and related path-feasibility agents** propose similar LLM-driven path checks to detect conflicts in paths and mitigate alarms; these works emphasize targeted constraint checks complementary to LLM judgments [7].  
- **ZeroFalse CWE-specialized adjudication** treats analyzer outputs as structured contracts enriched with flow traces and CWE knowledge, achieving high F1 on OWASP Java Benchmark and OpenVuln (F1 0.912 and 0.955 respectively) by combining LLM adjudication with CWE-focused prompting [8].  
- **LLM4FPM context engineering** emphasizes precise and complete code context extraction via extended CPG slicing and file-reference discovery, claiming near-perfect F1 on Juliet and highlighting that inadequate context is a key failure mode for LLM triage [9].  
- **SkipAnalyzer multi-task agent** demonstrates LLMs can combine detection, FP filtering, and patch generation for null‑deref and resource leaks, improving static-detector precision and producing high-quality patches in their dataset [10].  
- **SAST‑Genius and LASHED industrial-style studies** report large FP reductions (e.g., SAST‑Genius ~91% FP reduction vs Semgrep; LASHED reports ~87.5% plausible CWEs in hardware) when combining LLM reasoning and static techniques, indicating strong practical potential in applied settings [11] [12].

Observed limitations and gaps that EVICT could target
- Many systems improve precision but vary widely in reported datasets and metrics, making apples-to-apples comparison difficult.  
- LLM-only or prompt-heavy pipelines remain vulnerable to hallucination and non-determinism; grounding via symbolic checks yields more reliable gains but increases complexity [4] [6].  
- Context extraction quality is critical; missing or noisy context drives errors [9].  
- Large reported gains are often on benchmarks (Juliet, OWASP) or limited industrial case studies; cross-project and long-term robustness remain underexplored [2] [3] [8].  

----

## Selective prediction and calibration

This section examines whether the literature provides frameworks for abstention, calibrated uncertainty, or risk-controlled triage in static-analysis contexts and what calibration techniques are shown to help LLM-based triage. The supplied corpus contains only limited direct work on formal selective-prediction frameworks applied to code triage; instead, papers emphasize ensemble prompts, repeated reasoning, and agentic risk heuristics.

- **Ensembling and self‑consistency** have been used to reduce FP rates: combining multiple LLM outputs or asking the model to "think again" (self-consistency) improves precision in SAST triage experiments reported by Wagner et al. and by hardware-focused LASHED [13] [12].  
- **Agentic risk‑triage prototypes** use heuristic risk scoring, model-based reasoning, and normalization across tools to prioritize alerts and potentially abstain from low‑confidence decisions in operational settings, but these are presented as systems rather than formal risk‑guarantee frameworks [14].  

Insufficient evidence for formal selective‑prediction or calibrated abstention
- There is no clear example in the supplied corpus of a risk-controlled classifier or formal abstention policy (e.g., guaranteed coverage vs risk bounds) applied to static-analysis triage; therefore **insufficient evidence** exists in the provided literature to conclude that formal selective‑prediction methods are integrated into LLM triage pipelines.  

Practical calibration techniques reported or implied
- **Model ensembling and repeated sampling** (self-consistency) to stabilize judgments and reduce hallucinations [13] [12].  
- **Domain‑specific prompting and CWE specialization** to constrain LLM outputs and improve reliability [8].  

How EVICT can contribute
- Implement explicit confidence calibration, abstention thresholds, and risk‑controlled coverage guarantees for LLM triage, and evaluate whether calibrated abstention reduces developer workload while controlling missed‑bug risks — a gap not addressed in the supplied literature.

----

## Contrastive learning and distribution shift

This section reviews ML approaches for learning false‑positive signatures, cross-project generalization, and whether contrastive learning has been applied to code or bug detection. The corpus contains examples of learned classifiers and path‑based representations but little explicit contrastive learning for FP signatures.

- **Transformer classifiers for FP detection** demonstrated precision gains: a 2022 Transformer approach improved static-analysis precision by ~17.5% and showed generalizability across null-dereference and resource-leak types [15].  
- **Path-based semantic encoders** use control-flow graph path sequences and fine-tuned PLMs to capture alarm semantics and improve automated warning identification across multiple open-source projects [16].  
- **FPDetection and ensemble approaches** convert defect logs to embeddings and combine deep learning with fine‑tuned LLMs and similarity ensembles to classify false positives in industrial settings [17].  
- **FuzzSlice empirical audit** shows dataset-label issues and evaluates cross-project behavior: it validated Juliet labels and confirmed substantial FP pruning in real repositories, underscoring distributional and labeling challenges when evaluating learned triage models [18].

Insufficient evidence for contrastive learning
- The supplied corpus does not present an explicit contrastive‑learning method (e.g., InfoNCE on code-positive/negative pairs) applied to false‑positive signature learning or domain adaptation; therefore **insufficient evidence** exists to claim prior use of contrastive learning for FP detection in these works.

Research gaps EVICT could address
- Develop contrastive or metric‑learning representations that discriminate true positives from false positives across projects and language ecosystems.  
- Systematic evaluation of distribution shift (cross-project, cross-tool, cross-CWE) with domain adaptation or transfer‑learning techniques to improve triage robustness.

----

## Neuro-symbolic program analysis

This section catalogs recent hybrid approaches that combine LLMs with SMT, symbolic execution, or other formal methods to validate reasoning and reduce hallucinations. The evidence shows neurosymbolic methods improve reliability and reduce false positives by validating model outputs against solver/analysis facts.

- **WARP worst‑case symbolic constraints** integrates LLMs with symbolic solving and reinforcement learning to generalize constraints; the neurosymbolic pipeline improves constraint‑reasoning performance and shows gains over baselines on a curated constraint dataset, demonstrating that incremental, solver‑aligned LLM reasoning can handle symbolic program tasks better than LLMs alone [6].  
- **Laurel assertion generation for verifiers** uses domain‑specific prompting, error‑message localization, and proof‑similarity examples to have LLMs generate assertions that unblock SMT‑based verifiers; Laurel produced the required assertions in over 56.6% of cases on a benchmark of complex Dafny lemmas, indicating practical assistance to formal verification workflows [19].  
- **AdaTaint grounding** couples LLM-inferred taint specifications with symbolic constraint validation to filter spurious alerts, reporting a 43.7% average FP reduction and recall improvement on benchmarks and real projects, which supports the claim that grounding LLM outputs reduces hallucination‑driven errors [4].  
- **WARP and related neurosymbolic designs** emphasize solver alignment and incremental reasoning to scale symbolic checks while leveraging LLM generalization capabilities [6].

Limitations and open issues
- Neurosymbolic gains come at engineering cost: integrating solvers and LLMs raises scalability and latency concerns in large codebases.  
- Existing neurosymbolic work focuses on specific verification tasks (constraints, assertions, taint) rather than general-purpose alert triage pipelines that must operate across many CWE types and analyzer outputs.

Opportunity for EVICT
- Build a scalable neuro-symbolic triage layer that (a) uses lightweight solver/alignment checks to validate LLM triage decisions, (b) prioritizes solver effort via selective prediction/abstention, and (c) measures tradeoffs between extra verification cost and reduced developer triage workload.

----

## Benchmarks and evaluation

This section summarizes datasets, evaluation protocols, label‑quality concerns, and cross‑project evaluation practices observed in the corpus. The literature relies repeatedly on a small set of benchmarks, with recurring concerns about label fidelity and generalization.

Common benchmarks and datasets used
- **Juliet / SARD** is widely used for controlled evaluations and is the basis for many reported results (Llm4sa, AdaTaint, LLM4FPM, FuzzSlice) [2] [4] [9] [18].  
- **OWASP Java Benchmark and OpenVuln** are used for CWE-focused SAST evaluations; ZeroFalse reports F1 above 0.90 on these datasets [8].  
- **Linux kernel and large real projects** are used for large-scale, practical evaluations in BugLens and LLift, which stress scalability and real-world noise [1] [3].  
- **SV‑COMP style benchmarks** were used alongside Juliet in some neurosymbolic evaluations [4].  

Concerns about labels, leakage, and cross‑project evaluation
- **Label quality issues**: FuzzSlice identified substantial false positives in Juliet ground truth (e.g., 864 FP instances) and used function-level fuzzing to validate or refute warnings, highlighting that synthetic benchmark labels may be imperfect for triage evaluation [18].  
- **Context extraction and leakage risks**: studies that obtain near-perfect scores on Juliet (e.g., LLM4FPM claiming >99% F1) emphasize that careful context extraction and potential dataset artifacts can inflate performance if not controlled [9].  
- **Cross‑project generalization is limited**: a small number of works validate generalizability (Transformer-based FP classifier across two bug types; LLift on kernel UBI bugs), but systematic cross-project holdout protocols and long-tail CWE coverage evaluations are uncommon [15] [3].  

Insufficient evidence for NASCAR, DZA, CWE-Bench-Java comparison
- The supplied corpus does not contain data or comparisons for NASCAR, DZA, or CWE‑Bench‑Java; therefore **insufficient evidence** exists to compare those specific benchmarks with Juliet, OWASP, or SV‑COMP in this collection.

How EVICT can improve evaluation practice
- Use verified, developer‑labeled real‑project datasets and report cross‑project and time-split evaluations to assess distributional robustness.  
- Include falsification steps (e.g., function‑level fuzzing or symbolic checks) to validate ground truth labels and avoid overfitting to benchmark artifacts.  
- Report calibrated confidence, abstention rates, and cost‑benefit tradeoffs (verification time vs developer triage time) rather than only precision/recall.

----