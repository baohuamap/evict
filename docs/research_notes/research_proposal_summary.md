## Comprehensive Summary of the Research Proposal

### Main Research Problem and Objectives
- **Problem**: Static-analysis alert triage involves deciding which warnings are genuine bugs and worth developer time. Warnings can be 'true bugs', 'false positives', or 'non-actionable' due to various factors like risk/benefit or project policy. Large datasets indicate that the same rule patterns can lead to both actionable and non-actionable outcomes, highlighting the importance of context beyond just the rule ID [1].
- **Objective**: The proposal aims to formalize alert triage as selective prediction under distribution shift, introduce contrastive learning of false-positive signatures, and deliver a reproducible benchmark suite using public datasets (NASCAR, D2A, Juliet/SARD, CWE-Bench-Java) encoded in SARIF [2]. The ultimate goal is to build an evidence-conditioned LLM verifier that triages static-analysis alerts, leveraging analyzer evidence, calibrated uncertainty, abstention, and lightweight symbolic checks [2].

### Proposed Methodology and Approach
- **EVICT Pipeline**: The core proposal is EVICT (Evidence-conditioned Verifier for Investigating Code Triage), a pipeline that converts each static-analysis alert into a structured evidence bundle. It then performs calibrated, selective adjudication and optionally triggers symbolic checks .
- **EvidencePack Schema**: For each alert, EVICT builds an EvidencePack containing :
  - **Alert core**: Rule/CWE, severity/confidence, and SARIF locations.
  - **Minimal slice**: A statement-level slice around the source/sink, a dependency slice along the analyzer-reported flow, and optionally a CPG-based slice.
  - **Flow trace**: A normalized representation of the analyzer's path (call chain, taint edges).
  - **Constraints**: Extracted branch predicates/guards; if missing, the LLM can request additional context through 'progressive prompting' .
- **Decision Logic**: EVICT outputs `(p, d, r)`, where `p` is a calibrated true positive probability, `d` is the decision (`TP`, `FP`, `ABSTAIN`), and `r` is a structured rationale with references to evidence artifacts. For `ABSTAIN` cases, the system routes to human triage and logs 'missing evidence requests' .
- **LLM Model Family**: EVICT is designed to work in two operational regimes :
  - **API-only GPT-style models**: Relies on prompt engineering, self-consistency, and conformal wrappers.
  - **Open Llama-style models**: Uses logits for stronger calibration and allows fine-tuning adapters (LoRA) on large warning corpora .
- **Prompting and Representation**: Utilizes a schema-constrained verifier prompt to force the LLM to restate the analyzer claim, list preconditions, check each precondition against evidence, and output `TP/FP/ABSTAIN` with a confidence score and referenced evidence IDs. Context length is minimized via EvidencePack .
- **Fine-tuning vs. Few-shot**: Starts with few-shot learning using curated `TP/FP` exemplars. Progresses to parameter-efficient fine-tuning (LoRA) on datasets like NASCAR/D2A, with strict de-duplication and project-based splits. For contrastive FP-signature learning, an embedding head is trained on EvidencePack representations with hard-negative mining .
- **Calibration and Uncertainty Estimation**: Applies temperature scaling if logits are accessible . Uses conformal prediction for LLMs without logit access to build uncertainty estimates with statistical guarantees . Ensemble-style uncertainty (self-consistency vote entropy, stochastic decoding) is also used .
- **Symbolic Checks and Lightweight Symbolic Execution**: For path-feasibility-dominated false positives, branch constraints are extracted, and SMT solvability is invoked. For data-flow hallucinations, syntactic/semantic properties of reported flows are validated using parsers and sanitizer checks. Conditional invocation of symbolic hooks is used when confidence is borderline or the action is costly .

### Key Contributions Claimed
- **Risk-controlled Adjudication**: EVICT treats alert triage as selective prediction under asymmetric costs, optimizing risk-coverage and calibrating confidence, which is not the primary focus of prior post-refinement systems .
- **False-positive Signature Learning**: Introduces contrastive learning over EvidencePacks to model recurring false-positive 'signatures' (e.g., infeasible path motifs, missing context patterns) and improve cross-project generalization, addressing concerns about duplication and label leakage .
- **Verifier with Symbolic Hooks and Abstention**: Integrates lightweight SMT/targeted symbolic execution conditionally, producing auditable certificates (SAT/UNSAT, reachability checks). This combines strengths of LLM4PFA and sanitization approaches while controlling cost and hallucination .
- **Standardized Evidence Interchange**: EVICT encodes alerts and evidence using SARIF as a lingua franca, enabling cross-tool evaluation and reproducibility .

### Experimental Design
- **Evaluation Protocol**: A NeurIPS-quality evaluation must be leakage-resistant, shift-aware, and utility-centric. The proposal uses a tiered dataset strategy combining synthetic benchmarks, large-scale actionability corpora, and realistic vulnerability benchmarks .
- **Datasets**: Key datasets include    :
  - **NASCAR**: Over 1 million Java warnings labeled actionable/non-actionable.
  - **D2A**: Differential-analysis-labeled static-analysis issues from bug-fix commit pairs.
  - **Juliet/SARD**: Synthetic labeled buggy/bug-free cases for controlled verification.
  - **CWE-Bench-Java**: Manually validated security vulnerabilities in Java projects.
  - **Sonar-style FP datasets**: Labeled warning samples from prior ML filtering studies.
- **Data Collection and Labeling Protocol**: Prefers commit-differential labeling (D2A-style) as scalable but noisy, explicitly modeling it as weak supervision and reserving manual auditing for calibration/test sets . Emphasizes project-level and time-based splits, and de-duplication to avoid train/test contamination .
- **Baselines**: Includes static analyzer alone, heuristic filters, classic supervised ML triage, prior LLM triage/FP-reduction pipelines (BUGLENS, LLM4FPM, LLM4PFA), and neuro-symbolic bug reasoning baselines (LLMDFA)   [3].
- **Metrics**: Classification (precision/recall/F1, FPR, AUC, class-conditional calibration), Ranking (precision@k, recall@k, NDCG@k), and Selective Prediction (risk-coverage curves, coverage at fixed risk)   . Human-in-the-loop cost proxies like minutes saved per 1k alerts are also considered .
- **Ablations**: Planned ablations include EvidencePack composition (function-only vs. slice vs. slice+trace vs. slice+trace+constraints) , verifier scaffold (unstructured prompting vs. schema-guided verification vs. multi-turn investigation) , uncertainty estimation (self-consistency entropy vs. logit-based margins vs. conformal wrappers) , and symbolic hook usage (no hooks vs. SMT-only vs. symex-only vs. conditional hooks) .

### Current Limitations or Gaps
- **Hallucinations**: LLM hallucinations and spurious rationales are well-documented, and self-consistency may not reliably fix them, necessitating hybrid verification .
- **Distribution Shift**: Severe distribution shift exists, as warning actionability and FP patterns vary by project practices and tool configurations .
- **Label Noise**: Pervasive in auto-labeled datasets, with D2A explicitly framing labels as 'very likely' with limited accuracy .
- **Operational Complexity**: Hybrid symbolic-LLM pipelines can have operational complexity and potential runtime overhead, motivating conditional invocation .

### Related Work Mentioned
- **BUGLENS (ASE)**: Proposes a post-refinement framework with Structured Analysis Guidance, improving precision on Linux-kernel taint-style bugs from 0.10 to 0.72 [4].
- **LLM4PFA**: Frames false positives as largely caused by infeasible paths and uses iterative, agentic constraint reasoning to validate reachability, filtering 72%-96% of false positives [5].
- **LLM4FPM**: Argues against coarse snippets and proposes eCPG-based slicing plus file-dependency expansion, achieving F1 > 99% on Juliet and significant FP elimination [6].
- **Tencent Empirical Study**: Reports developers spend 10-20 minutes per alarm manually, and hybrid LLM + static-analysis techniques can eliminate 94%-98% of false positives [7].
- **LLMDFA (NeurIPS 2024)**: Shows that decomposition + external tool checks reduce hallucination in code reasoning [3].
- **LLMSAN (Findings of EMNLP 2024)**: Explicitly treats hallucinated bug paths as false positives and introduces 'sanitizers' to validate data-flow path properties [8].
- **D2A (2021)**: Uses differential analysis on before/after bug-fix commits to label analyzer issues and notes that static analyzers generate excess false positives [9].
- **Kang et al. (ICSE 2022)**: Highlights that 'golden feature' performance can be inflated by data leakage and duplication, motivating leakage-resistant splits and calibration-aware evaluation [10].

### Preliminary Results
- The proposal does not present new preliminary results but references existing industrial evidence and prior research findings to support its claims. For example, it cites a Tencent study indicating that hybrid LLM + static-analysis techniques can eliminate 94%-98% of false positives with high recall, and reports per-alarm runtime and monetary costs in seconds and fractions of a dollar [7]. It also mentions BUGLENS's reported precision improvement from 0.10 to 0.72 and LLM4PFA's 72%-96% false positive filtering [4] [5].

In summary, this research proposal outlines a rigorous approach to enhancing static-analysis alert triage through an evidence-conditioned LLM verifier (EVICT). It emphasizes risk-controlled adjudication, learning false-positive signatures, and integrating symbolic checks, all within a framework designed for reproducibility and robustness against distribution shifts and label noise.