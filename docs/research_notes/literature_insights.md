## TL;DR

LLM-assisted static analysis advanced rapidly via hybrid pipelines, neuro-symbolic verification, and targeted false‑positive filters; distribution shift and calibration remain open problems with some benchmarks and contrastive techniques emerging. Key gaps include provable abstention, standard metrics for OOD code, and scalable verification-in-the-loop.

----

## Method advances

LLM integrations with static analysis now favor hybrid, retrieval, and neuro-symbolic designs that preserve analyzer coverage while reducing false positives. Recent papers report practical pipelines that combine static traces, program-dependence extraction, and LLM adjudication or patching to scale to real projects.

- **Hybrid pipelines** combine static analyzers with LLM adjudicators to filter or triage warnings, improving precision without sacrificing coverage, as demonstrated by SkipAnalyzer and LLift for real-world bug types and large codebases [1] [2].  
- **Mass inspection at scale** uses program-dependence snippet extraction plus LLM queries to inspect thousands of warnings with high precision and recall in Juliet and real projects [3].  
- **Adaptive neuro-symbolic filtering** grounds LLM suggestions in symbolic checks (source/sink inference with constraint validation), reducing false positives substantially while maintaining recall in benchmarks such as Juliet and SV‑COMP-style suites [4].  
- **Structured-contract adjudication** enriches analyzer outputs with flow-sensitive traces and CWE-specific context before LLM adjudication to reach high F1 on OWASP/OpenVuln benchmarks [5].  
- **Retrieval‑augmented fixes** use analysis predicates to retrieve high‑quality key examples for RAG pipelines that improve repair correctness across CodeQL and GoInsight alerts [6].  
- **Contrastive and representation learning** have been applied to align models to real bug distributions, improving robustness to mismatch between synthetic and real bugs [7].  
- **Neuro‑symbolic verification primitives** (e.g., neural ranking functions for termination and certified synthesis frameworks) provide mechanisms to derive formal certificates from learned artifacts and to reject unverified outputs [8] [9] [10].

References: SkipAnalyzer [1] LLift [2] Llm4sa [3] AdaTaint [4] ZeroFalse [5] SAST‑Genius [11] PredicateFix [6] On distribution shift and contrastive methods [7] Neural termination and neuro‑symbolic works [8] [9] [10].

----

## Selective prediction

Selective prediction for code analyzers—making a model abstain when uncertain—has conceptual support from verification‑in‑the‑loop and certification work, but explicit LLM‑based abstention schemes with end‑to‑end theoretical guarantees are scarce in the corpus. Existing research supplies building blocks (formal certificates, differentiable verification) rather than a standardized, provably calibrated abstention protocol for LLM outputs.

- **Limited direct evidence** for fully specified selective‑prediction algorithms with provable risk‑coverage tradeoffs in LLM-based static analysis; the corpus does not present a canonical abstention theorem for these systems. Insufficient evidence  
- **Verification‑in‑the‑loop** approaches produce safety/robustness certificates or differentiable verification signals that can be used to trigger abstention when proofs fail or when counterexamples are found, enabling conservative behavior with formal signals [12].  
- **Neural certificates and symbolic checks** (e.g., neural ranking functions for termination, differentiable symbolic execution) show how learned components can be validated or rejected via symbolic reasoning, supporting deterministic abstention decisions when verification fails [8] [12].  
- **Practical abstention pattern** used implicitly in hybrid pipelines: LLM suggestions are accepted only after symbolic validation or constraint checks (thus abstaining when validation fails) as in adaptive taint or certified synthesis pipelines [4] [10].

References: verification and verification‑in‑the‑loop [12] neural termination and certificate examples [8] neuro‑symbolic synthesis and provable outputs [10] AdaTaint and adaptive grounding [4].

----

## Calibration and uncertainty

Work on uncertainty and calibration for code LLMs has begun to evaluate probabilistic methods and OOD detectors but detailed, code‑specific alternatives to temperature scaling are still emergent. Benchmarks and empirical studies have compared multiple probabilistic approaches and OOD detectors on code distribution shifts.

- **Probabilistic methods improve uncertainty awareness** in code LLMs (CodeLlama) under realistic code shifts, with gains in calibration and uncertainty‑estimation precision reported across evaluated techniques [13].  
- **Softmax‑based OOD detectors remain competitive for code** in benchmark studies, but detectors from vision/NLP do not always transfer directly to code tasks, motivating code‑specific calibration strategies [14].  
- **Empirical tradeoffs**: studies report differing impacts of methods on calibration error versus misclassification detection and highlight efficiency versus efficacy tradeoffs that must be considered in engineering choices [13].  
- **Practical implication**: combine probabilistic uncertainty estimators with symbolic validation or verification steps to convert soft uncertainty into actionable abstention or human‑in‑the‑loop workflows [13] [4].

References: empirical uncertainty study [13] CodeS benchmarking on OOD detectors [14].

----

## Distribution shift and evaluation

Distribution shift in code is widely recognized; several benchmarks and experimental designs target code‑specific OOD scenarios and concept drift, and some works propose contrastive or two‑phase training to close synthetic/real gaps. These artifacts are immediately useful for proposal evaluations.

- **Benchmarks and simulated shifts**: CodeS defines task, programmer, timestamp, token, and CST shifts for Java/Python and shows representation-based shifts are most harmful to models [14].  
- **Systematic OOD simulation** (SimSCOOD) exposes failure modes across model families and tasks, enabling controlled stress tests for robustness and inductive bias analysis [15].  
- **Two‑phase and contrastive training** mitigate synthetic→real distribution mismatch: pretrain on synthetic bugs then fine‑tune on curated real bugs while using contrastive learning and focal loss to improve real‑world precision [7].  
- **Concept drift detection and adaptation** use moving‑window statistics and hypothesis testing to detect drift in defect prediction and drive adaptation (resampling or model updates) [16].  
- **Experimental best practices** seen in the corpus: (1) evaluate on real project scans at scale (thousands of warnings), (2) report precision/recall plus F1 and coverage preservation, (3) include OOD and drift stress tests rather than only IID holdouts [3] [14] [15] [3].

References: CodeS and its findings [14] SimSCOOD systematic OOD [15] two‑phase/contrastive detector training [7] CODE concept drift detector [16] large‑scale LLM inspection evaluations [3].

----

## Gaps and methodological weaknesses

The literature reveals recurring weaknesses that EVICT can target and avoid, plus theoretical frameworks to adopt. Key gaps include lacking provable abstention, transferable OOD detectors for code, and scalable, certified neuro‑symbolic loops.

- **Gaps to address for EVICT**  
  - **Provable abstention protocols** for LLM adjudication of static warnings are missing; current works provide verification primitives but not integrated selective‑prediction guarantees [12] [8] [10].  
  - **Code‑specific OOD detectors and metrics** are underdeveloped; vision/NLP detectors often fail to generalize to code shifts identified by CodeS [14].  
  - **Scalable neuro‑symbolic verification in CI/CD** remains immature: many proposals verify isolated artifacts or small benchmarks rather than continuous integration on large projects [10] [4].  
  - **Standardized evaluation for FP reduction with coverage constraints** (i.e., preserve recall while reducing FPs) needs broader adoption; a few works report F1 and coverage preservation but formats vary [5] [3].

- **Methodological weaknesses to avoid**  
  - **Training only on synthetic bugs** without realistic fine‑tuning leads to catastrophic precision drops in practice; two‑phase training or real‑bug fine‑tuning is necessary [7].  
  - **Blind reliance on LLM outputs** without symbolic grounding causes hallucination and non-deterministic mistakes; always couple LLMs with deterministic checks for critical decisions [4] [10].  
  - **Evaluating on small or non‑representative datasets** inflates reported performance; favor large‑scale, real‑project scans and OOD stress tests [3] [14] [15].  
  - **Filtering that sacrifices coverage** undermines utility; design filters that prioritize FP reduction while bounding missed true positives and report those tradeoffs explicitly [5].

- **Theoretical frameworks to adopt**  
  - **Verification in the learning loop** and differentiable symbolic execution supply mechanisms for formal safety signals and training‑time feedback [12].  
  - **Neural certificate constructions** (e.g., neural ranking functions, symbolic validators) enable formal claims about termination or absence of certain runtime errors and can be used as reject criteria [8] [9] [10].

References: gaps and weaknesses supported by CodeS, two‑phase learning, and neuro‑symbolic works [14] [7] [4] [5] [12] [8] [10].

----