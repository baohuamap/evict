ChatGPT

# Evidence-Conditioned LLM Investigation for Static-
Analysis Alert Triage

Executive recommendation: Build an evidence-conditioned LLM verifier that triages static-analysis alerts
using the analyzer's own evidence (trace, slice, constraints) , and couples this with calibrated uncertainty
abstention and lightweight symbolic checks (SMT targeted symbolic execution) only when needed:
Recent systems show that LLMs can drastically raise precision when guided by structured reasoning and
precise context extraction (e.g-, post-refinement workflows and path-feasibility reasoning), and industry
evidence indicates large practical ROI in minutes saved per alert--yet rigorous ML treatment of risk
control, calibration, and cross-tool generalization remains underdeveloped: This proposal targets
NeurIPS-style contribution by formalizing alert triage as selective prediction under distribution shift,
introducing contrastive learning of false-positive signatures and delivering reproducible benchmark
suite using public datasets (NASCAR, DZA, Juliet/SARD, CWE-Bench-Java) encoded in SARIF

# Literature survey and positioning

A consistent theme in the last 5 years is that LLMs help most when placed "after" static analysis as an
evidence-aware adjudicator; not as a replacement for analyzers BUGLENS (ASE) proposes a post-refinement
framework with Structured Analysis Guidance workflow; it reports improving precision on Linux-kernel
taint-style bugs from 0.10 to 0.72 and also discusses correcting previously missed cases (Paper URL:
https [WWW . CS.ucr edu/~zhiyunq/pub/ase25 bug ens. pdf

Multiple preprints sharpen this idea: LLMAPFA frames false positives as largely caused by infeasible paths
and uses iterative, agentic constraint reasoning to validate reachability given traces and source/sink
variables. It reports filtering 72%-96% of false positives while maintaining high recall in its evaluations
(Paper URL: https rarxiv.org/abs 2506. 10322 ).

Another key bottleneck is context extraction. LLMAFPM argues that coarse snippets (e.g-, whole function
bodies) add noise and cost, and proposes eCPG-based slicing plus file-dependency expansion; it reports F1
99% on Juliet; label-quality improvements on DZA (e.g,, from 53% to 86% in their setting), and >85% false-
positive elimination on several open-source projects, with average inspection time around seconds per
warning: (Paper URL: https /arxiv.org /pdf, 2411.03079

Industrial evidence is now emerging: A 2026 empirical study at Tencent reports that developers spend
10-20 minutes per alarm manually; and that hybrid LLM static-analysis techniques can eliminate 94%-
98% of false positives with high recall; it also reports per-alarm runtime and monetary costs in a range of
seconds and fractions of a dollar (Paper URL: https /arxiv.org/abs/2601 . 18844

Adjacent research strengthens the ML angle: LLMDFA (NeurIPS 2024) shows that decomposition external
tool checks (e.g-, parsing, theorem proving) can reduce hallucination in code reasoning by offloading
delicate reasoning to verification tools. (Paper URL: https /proceedings.neurips.cc /paper files/

paper /2024/file/ed9dcdeleb9c597f68c1d375bbecf3fc-Paper-Conference.pdf Additionally;
LLMSAN (Findings of EMNLP 2024) explicitly treats hallucinated bug paths as false positives and introduces
"sanitizers" to validate data-flow path properties; it also shows that CoT and self-consistency do not reliably
mitigate hallucinations: (Paper URL: https: //aclanthology.org 2024.findings-emnlp.217.pdf

For datasets and evaluation practices, classic ML-based false-positive filtering work remains important: DZA
(2021) uses differential analysis on beforelafter bug-fix commits to label analyzer issues and notes that static
analyzers generate excess false positives; it also provides explicit caveats about "very likely" labels (Paper
URL: https /arxiv.org/pdf/2102. 07995 Kang et al. (ICSE 2022) show that "golden feature"
performance can be inflated by data leakage and duplication, and that common heuristic labeling can
disagree with humans directly motivating leakag Je-resistant splits and calibration-aware evaluation: (Paper
URL: https Tarxiv.org/pdf/2202.05982 ).

To broaden with program understanding; triage, and repair: large code LMs (e.g , CodeTS+) are established
building blocks for code understanding and generation: (Paper URL: https /aclanthology.org
2023 emnlp-main.68.pdf ). Real-world SE benchmarks (SWE-bench) show repository-scale tasks are
hard and highlight the importance of tool feedback loops: (Paper URL: https /proceedings.iclr _ Cc/
paper files/paper 2024/file/edac78c3e300629acfebcbe9ca88fb84-Paper-Conference.pdf

Program-repair work using LLMs (e.g-, conversational repair and fine-tuning studies) underscores the
need for verification signals (tests) and cost-aware search, which parallels our need for verifiable evidence
in alert adjudication. (URLs: https Ilingming _ CS illinois.edu/publications/issta2024.pdf
https 1 [ 'zhangj111.github.io/files/ASE23 APR_Study pdf

# Problem definition and formalization

Static-analysis alert triage is the task of deciding which warnings are real and worth developer time. In
practice, warnings may be "true bug; "false positive, or "non-actionable" due to risklbenefit or project
policy; large datasets show that the same rule patterns can produce both actionable and non-actionable
outcomes, implying context matters beyond rule id.

We formalize each alert i as an evidence-conditioned instance (Ci, Yi ) , where €i is an EvidencePack and
Yi {TP , FP} (or {TP , FP , UNCERTAIN} for   human-in-the-loop) EvidencePack includes alert
metadata, localized code slices, analyzer-produced flows (taintIvalue-flow paths) and optional extracted
constraints, mirroring the design used by post-refinement systems and feasibility frameworks_

The triage objective can be framed in three standard ML formulations Binary classification: minimize false
positives while preserving recall on true bugs (or vice versa depending on risk tolerance) Ranking: score
alerts {(1i so that reviewing the top k yields high precision@k and recall@k Selective   prediction
(abstention): output either a label or "defer" optimizing risk-coverage tradeoff where the system only
auto-adjudicates when calibrated confidence is sufficient:

Evaluation metrics should reflect both security quality and human cost: Required metrics include (i) FPR
precision recall F1 , (i) precision@k; recall@k, NDCG@k for ranking, (iii) calibration metrics like ECE and
Brier score, and (iv) human-in-the-loop cost proxies such as minutes saved per 1k alerts and remaining
manual workload under abstention: Tencents study provides concrete cost anchors (minutes per alert

manually; seconds and dollars per alert under some LLM pipelines), which we can use to report end-to-end
utility:

# Taxonomy of LLM-based triage approaches

LLM-as-oracle (one-shot classifier) The LLM receives warning code snippet and outputs TPIFP This is
easy to deploy but brittle with long contexts, unreliable rationales, and poor calibration, especially under
project shift: Evidence-focused studies show that prompt-only methods vary and often need better context
extraction:

LLM-as-explainer (human decides): The LLM summarizes evidence and produces a rationale; humans still
adjudicate. This can improve trust and throughput, and is consistent with practical adoption patterns
emphasizing transparency: However; it does not directly optimize false-positive reduction and can still
hallucinate explanations.

LLM-as-verifier (claim checking over evidence) The LLM is constrained to validatelrefute the analyzer's
claim using the analyzer's trace and precise slice, often via a structured workflow: BUGLENSs structured
guidance and LLMAPFAs iterative feasibility reasoning fall into this category and report large precision
gains. This is the most promising family for FP reduction because it transforms "reasoning" into "evidence-
conditioned verification_

Hybrid symbolic-LLM pipelines. The LLM extracts constraints or proposes checks; SMT parsing theorem
proving validates them LLMDFA, LLMSAN; and LLMAPFA exemplify the value of offloading brittle steps to
deterministic tooling,  which reduces hallucination-driven false positives The  downside is operational
complexity and potential runtime overhead, motivating conditional invocation (only for uncertain cases)

# Proposed method with novelty claims

We propose EVICT (Evidence-conditioned Verifier for Investigating Code Triage) a pipeline that converts
each static-analysis alert into a structured evidence bundle, then performs calibrated, selective adjudication
and optionally triggers symbolic checks

Novelty claims (relative to strong recent systems)

Risk-controlled adjudication: EVICT treats alert triage as selective prediction under asymmetric
costs, explicitly optimizing risk-coverage and calibrating confidence; this is not the primary focus of
prior post-refinement systems that mostly report precision/recall:

False-positive signature learning: EVICT introduces contrastive learning over EvidencePacks to
model recurring false-positive "signatures" (e.g-, infeasible path motifs, missing context patterns)
and to improve cross-project generalization while controlling leakage via deduplication-aware
sampling: This directly addresses ICSE22 concerns about duplication and label leakage:

Verifier with symbolic hooks and abstention: EVICT integrates lightweight SMT targeted symex
conditionally (uncertain or high-impact cases) and produces auditable certificates (SAT/UNSAT,
reachability checks), combining the strengths of LLMAPFA and sanitization approaches while
controlling cost and hallucination.

Standardized evidence interchange: EVICT encodes alerts and evidence using SARIF as a lingua
franca, enabling cross-tool evaluation and reproducibility across analyzers and projects. (Spec URL:
https- /docs.oasis-open.org/sarif/sarif/v2 1. 0/os/sarif-v2 _ 1 . 0-05 pdf )

# EvidencePack schema For each alert; build:

Alert core: rule/CWE, severitylconfidence, SARIF locations

Minimal slice: statement-level slice around sourcelsink dependency slice along the analyzer-
reported flow; optionally CPG-based slice if available (as in context-focused systems)

Flow trace: normalized representation of the analyzer's path (call chain, taint edges)

Constraints: extracted branch predicates guards; if missing, the LLM can request additional
context in a bounded multi-turn loop ("progressive prompting"), inspired by static+LLM integrated
systems_

Decision logic EVICT outputs (p,d,7), where p is a calibrated TP probability, d € {TP, FP , ABSTAIN},
and r is structured rationale with references to evidence artifacts_ For ABSTAIN, the system routes to
human triage and logs "missing evidence requests" to guide future context extraction improvements.

# Pipeline flowchart.

flowchart TD

A[Static analyzer output] --> B[SARIF normalization]

C[EvidencePack builderIn(slice flow constraints)]

-> D[LLM Verifier Inschema-guided claim checking]

-> E{UncertaintyIn& calibration}

~> confident F[Auto-adjudicatelnTP /FP rationale]

~>luncer tain| G[ABSTAINInhuman-in-loop]

H[Optional symbolic hooks InSMT lightweight symex]

~->

7-> I[Feedback labelsIn(fixes reviews _ suppressions) ]

# Experimental design and evaluation protocol

NeurIPS-quality evaluation must be leakage-resistant, shift-aware, and utility-centric. We propose
tiered dataset strategy that combines synthetic benchmarks, large-scale actionability corpora, and realistic
vulnerability benchmarks

# Datasets and benchmarks_

NASCAR: 1M Java warnings labeled actionable/non-actionable, released with tools and data (links:
https: WWW. nature com/articles 541597-025-06154-7 https: / /zenodo.org
records/17079912

DZA: differential-analysis-labeled static-analysis issues from bug-fix commit pairs; includes traces/
outputs and explicitly targets false-alarm reduction: (Links:
https: Tarxiv org/pdf/2102.07995 repo link included in paper):

Juliet SARD: synthetic labeled buggylbug-free cases; useful for controlled verification, and widely
used for SAST evaluation: (Link: https: Isamate.nist gov/SARD/test-suites/112 )

CWE-Bench-Java (from IRISIICLR): realistic, manually validated security vulnerabilities in Java
projects; crucial for high-stakes evaluation under repo context: (Paper URL: https arxiv.org
pdf/2405 . 7238

Optional: SonarQube-style FP datasets from prior ML filtering studies for classic baselines (e.g:,
large-scale FP filtering dataset releases) (Example dataset page URL: https 'Izenodo. org
records 5885654

# Data collection and labeling protocol:

Prefer commit-differential labeling (DZA-style) as scalable but noisy; explicitly model it as weak
supervision and reserve manual auditing for calibration/test sets.

For NASCAR, treat "actionable" as a triage target (work-saving), but separate "true vulnerability" from
"actionable" when evaluating security findings to avoid conflating "fixed" with "real bug:"

Enforce project-level and time-based splits, and de-duplicate near-identical warnings to avoid
train/test contamination implicated in prior work:

# Baselines

Static analyzer alone: raw warning output; severity ranking, and any built-in confidence scores:

Heuristic filters: suppression-based rule-based post-processing (where available), and context-
length truncation baselines

Classic supervised ML triage: warning-level classifiers trained on historical features; include a
leakage-safe reimplementation guided by ICSE'22.

Prior LLM triage/FP-reduction pipelines: instantiate representative methods from BUGLENS,
LLMAFPM, and LLMAPFA as strong baselines_

Neuro-symbolic bug reasoning baselines: LLMDFA-style decomposition tool checks for specific
bug types:

# Metrics and statistical tests

Classification: precision/recallF1 , FPR, AUC, and class-conditional calibration (ECE/Brier).

Ranking: precision@k recall@k NDcG@k (k aligned to realistic review budgets):

Selective prediction: risk-coverage curves, coverage at fixed risk (e.g- <1% FN among auto-
dismissed FPs, or <S% FP among auto-confirmed TPs, depending on workflow):

Tests: use paired bootstrap CIs over projects; McNemar tests for paired classification; avoid IID
assumptions by clustering within projects/files:

# Ablations (required for NeurIPS rigor)

EvidencePack ablation: function-only vS slice VS slicettrace VS slicettracetconstraints

Verifier scaffold ablation: unstructured prompting VS schema-guided verification VS multi-turn
investigation:

Uncertainty ablation: self-consistency entropy vs logit-based margins VS conformal wrappers for API-
only settings:

Symbolic hook ablation: no hooks vS SMT-only vs symex-only vs conditional hooks

# Datasets and resource estimate table:

Why it matters Expected
Dataset Benchmark What it provides for EVICT Scale signal compute
footprint
Large-scale Training:
Actionable vS supervised moderate
NASCAR https: / / learning and million"
non-actionable (LoRA)
zenodo.org Java warnings calibration; warnings Inference:
records/17079912 realistic reported
generator tools "actionability' large batch
task scoring
Weak
Differential Millions of Training:
DZA https: / / labels from bug- supervision issues moderate;
realistic FP
arxiv.org/pdf / fix commit pairs reduction; also originally; emphasize
2102.07995 with analyzer tests label-noise labeled uniques noise-robust
outputs handling reported learning
Controlled Low-to-
JulietISARD https: / / Synthetic labeled feasibility checks 64,099 CIC++ moderate; can
samate.nist.gov / buggylbug-free and ground testcases in subsample for
SARD/test-suites cases truth; SATE-style suite #112 rapid
112 evaluation prototyping
CWE-Bench-Java (IRIS) High-stakes Higher per-
https: / / Manually vetted evaluation 120 instance cost
arxiv.org/pdf/ vulnerabilities in repository vulnerabilities (repo context);
2405.17238 real Java projects context reported smaller
dataset
Sonar-style FP dataset Classic ML Low-to-
https: / / Labeled warning baseline and 224,484 moderate;
samples from samples useful for
zenodo.org many projects cross-tool reported transfer
records/5885654 transfer tests learning

# Model and training details with uncertainty and symbolic
integration

Because the target model family is unspecified, EVICT is designed to work in two operational regimes With
API-only GPT-style models (logits hidden), we rely on prompt engineering, self-consistency, and conformal
wrappers that do not require logit access With open Llama-style models, we additionally use logits for
stronger calibration and can fine-tune adapters (LoRA) on large warning corpora:

# Prompting and representation:

Use a schema-constrained verifier prompt that forces the LLM to () restate the analyzer claim, (ii)
list necessary preconditions, (iii) check each precondition against evidence; and (iv) output TP/FP /
ABSTAIN with a confidence score and referenced evidence IDs. This mirrors structured guidance
designs reported effective in post-refinement systems:

Limit context length via EvidencePack minimization; context extraction is a first-class algorithmic
component (as LLMAFPM emphasizes).

# Fine-tuning vs few-shot:

Start with few-shot using curated TPIFP exemplars per rule/CWE; empirically, prompt strategy
variation materially affects FP vs TP tradeoffs in production-like workflows_

Progress to parameter-efficient fine-tuning (LoRA) on NASCARIDZA, with strict de-duplication and
project-based splits to avoid data leakage issues highlighted in ICSE22

For contrastive FP-signature learning, train an embedding head on EvidencePack representations
with hard-negative mining (e.g-, same rule, similar slice, different label), explicitly controlling for
train/test contamination

# Calibration and uncertainty estimation:

If logits are accessible, apply temperature scaling for post-hoc calibration (foundational but
effective): (Classic URL: https rarxiv.org abs 706. 04599

If logits are not accessible, use conformal prediction for LLMs without logit access to build
uncertainty estimates with statistical guarantees: (Paper URL: https /aclanthology.org
2024 findings-emnlp.54.pdf

Use ensemble-style uncertainty: self-consistency vote entropy and/or stochastic decoding; note that
self-consistency does not always mitigate hallucination in code reasoning tasks, motivating
additional tool checks.

# Symbolic checks and lightweight symbolic execution.

For path-feasibility-dominated false positives, extract branch constraints and invoke SMT solvability
(SATIUNSAT) as a certificate, inspired by LLMAPFAs feasibility focus:

For data-flow hallucinations, validate syntactic/semantic properties of reported flows using parsers
and sanitizer checks (LLMSAN-style), then feed results back to the verifier stage

Use conditional invocation: only trigger symbolic hooks when confidence is borderline or when the
action is costly (e.g-, auto-dismissing high-severity security alert): This aligns with the industrial
emphasis on cost-effectiveness per alarm

# Challenges, ethics, reproducibility, and roadmap

Key technical  challenges: Hallucinations and spurious rationales are well-documented  in LLM bug
reasoning, and self-consistency can fail to reliably fix them, motivating hybrid verification. Distribution
shift is severe: warning actionability and FP patterns vary by project practices and tool configurations, and
naive "oracle" labels can be unstable or disagree with humans_ Label noise is pervasive in auto-labeled
datasets; even DZA explicitly frames labels as "very likely" and reports limited label accuracy, while later
pipelines attempt to improve label quality through better context:

Mitigations. Use conservative automation by default: abstain when uncertain, and calibrate thresholds to
meet   explicit   risk budgets: Require   evidence-grounded outputs with   citations to sliceltrace IDs;
integrate  symbolic  certificates for high-impact or  borderline calls. Evaluate with leakage-resistant
protocols (project/time splits, de-duplication, cluster-aware CIs), per ICSE'22 guidelines_

Safety and ethical considerations. Over-filtering true positives can silently increase risk, especially for
security findings_ We mitigate this by () using ABSTAIN for high-risk cases, (i) separating workflows for
"suggested FP" vs "auto-dismissed; and (iii) logging rationales and certificates for auditing: Industrial and
government-oriented discussions emphasize that LLM guidance should reduce fatigue while preserving
analyst judgment and traceability:

Reproducibility plan. Use SARIF for tool-agnostic alert interchange and publish the EvidencePack schema
plus conversion utilities Release cleaned dataset splits with  stable hashes for deduplication and
document the labeling pipeline; prefer fully public datasets (NASCAR, JulietISARD, DZA, CWE-Bench-Java) for
reproducible training and evaluation: Provide full prompt templates, evaluation scripts, calibration
code, and ablation configs; for API-only models, log prompts/responses and use deterministic seeds where
possible:

Prioritized experiment plan with timeline and resource estimates. The goal is to de-risk quickly, then
scale to large corpora and shift tests

Stage A (Weeks 1-4): EvidencePack construction baseline prompts. Replicate strong recent
baselines (structured prompting and context slicing) on a small subset of Juliet NASCAR:

Stage B (Weeks 3-8): Calibration selective prediction. Add abstention; evaluate risk-coverage
and conformal methods for API-only settings:

Stage € (Weeks 7-12): Contrastive FP-signature learning: Train LoRA contrastive head on
NASCAR; evaluate cross-project generalization, with strict deduplication.

Stage D (Weeks 10-16): Symbolic hooks ablation. Add SMT feasibility checks and sanitizer
validations; measure reduction in high-confidence errors and runtime overhead.

Stage E (Weeks 14-24): Cross-tool and high-stakes evaluation. Evaluate transfer from NASCAR/
Sonar-style datasets to CWE-Bench-Java tasks; report tool-shift robustness_

A small mermaid timeline:

gantt

title EVICT 6-month experimental roadmap
dateFormat YYYY-MM-DD

section Foundations
EvidencePack SARIF pipeline :a1 2026-04-01 21d
Baselines replication :a2 2026-04-10 , 28d
section ML Core
Calibration abstention :b1_ 2026-05-01 , 28d
Contrastive FP-signature learning :b2 2026-05-15, 35d
section Verification
Symbolic hooks sanitizers :C1 2026-06-10 , 35d
Cross-project/tool generalization :c2 2026-07-05 , 35d

Resource estimates (order-of-magnitude, because the model family is unspecified):

People: 2-3 researchers for 6 months (one ML calibration/uncertainty, one program analysis/slicing/
SMT, one integration/evaluation):

Compute: LoRA training on large warning corpora is typically manageable on a small GPU cluster;
inference dominates if scoring millions of warnings, so batching and caching EvidencePacks matter:

Dollar/time cost: in practice, per-alert LLM runtime and cost can be reported alongside accuracy;
industrial evidence provides ranges in seconds and small-dollar fractions per alarm for some hybrid
pipelines:

# Conclusion and next steps

This proposal targets NeurIPS-quality contribution by treating static-analysis false-positive reduction as
evidence-conditioned,  risk-controlled  decision-making under  real-world distribution shift The core
scientific deliverable is calibrated selective verifier (with abstention) plus contrastive FP-signature learning;
validated with leakage-resistant  protocols on large  public  datasets and strengthened with   symbolic
certificates. Recent work demonstrates that structured, evidence-aware LLM post-processing can drastically
improve precision in complex systems (Linux kernel, large enterprise pipelines) but there remains clear
opportunity to formalize and generalize these gains through calibrated ML and reproducible benchmarks

"1   2

cs.ucredu

https //WWW.CS ucredul-zhiyunq/publase25 buglens pdf

Minimizing False Positives in Static Bug Detection via LLM-Enhanced Path Feasibility

Analysis

https Ilarxiv org/pdf/2506.10322

Utilizing Precise and Complete Code Context to Guide LLM in Automatic False Positive

Mitigation

https //arxiv: org/pdfi241 .03079

Reducing False Positives in Static Bug Detection with LLMs: An Empirical Study in

Industry

https Ilarxiv org/pdf/2601.18844

proceedings neurips.cc

https:!/proceedings neurips cc/paper_files/paper/2024/file/ed9dcde1eb9c597f68c1d37Sbbecf3fc-Paper-Conference pdf

aclanthology.org

https Ilaclanthologyorg/2024.findings-emnlp.217.pdf

arxiv.org

https //arxivorg/pdf/2102.07995

Detecting False Alarms from Automatic Static Analysis Tools: How Far are We?

https /larxivorg/pdf/2202.05982

aclanthology org

https /laclanthologyorg/2023.emnlp-main.68. ~pdf

proceedings iclrcc

https I/proceedings iclrcc/paper_files/paper/2024/fileledac78c3e300629acfe6cbe9ca88fb84-Paper-Conference pdf

Automated Program Repair via Conversation: Fixing 162 out of 337 Bugs for $0.42 Each using ChatGPT

https:Illingming cs.illinois edulpublications/issta2024-pdf

A Large-Scale Collection Of (Non-JActionable Static Code Analysis Reports Scientific Data

https //wwWnature com/articles/s41597-025-06154-7

Using LLMs to Automate Static-Analysis Adjudication and Rationales

https:/ /wwwsei cmu eduldocuments/5887/using_LLMs_for_SA_alert_adjudication_and_rationales_CrossTalk_article pdf

Static Analysis Results Interchange Format (SARIF) Version 2.1.0

https //docs oasis-open_ org/sariflsariflv2. O/os/sarif-v2.1.0-os.pdf

Juliet CIC++ NIST Software Assurance Reference Dataset

https I/samate nist gov/SARDItest-suites/112

arxiv.org

https //arxiv: org/pdfi2405.17238

Static Code Analysis Alarms Filtering Reloaded: an ML Approach and its Empirical Evaluation on a New
Real-World Dataset

https //zenodo org/records/5885654

aclanthologyorg

https  laclanthologyorg/2024.findings-emnlp.54.pdf

NASCAR: (Non-JActionable Static Code Analysis Reports

10

https I/zenodo org/records/17079912

Using LLMs to filter out false positives from static code analysis Datadog

https://wwW datadoghg com/blog/using-Ilms-to-filter-out-false-positives/

# On Calibration of Modern Neural Networks

https //arxivorg/abs/1706.045997utm_source-chatgpt.com