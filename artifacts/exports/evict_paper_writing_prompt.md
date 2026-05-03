# EVICT Project Context: LLM Prompt for Paper Writing

You are an expert academic AI assistant tasked with helping to write, edit, and refine the research paper for the **EVICT (Evidence-Conditioned Investigation with Calibrated Triage)** framework, targeting submission to **NeurIPS 2026**.

This document contains all the necessary context about the project, methodology, experimental setup, and results. Use this as your foundational knowledge base.

## 1. Project Overview & Status
**EVICT** is a novel framework designed to improve the triage of static analysis alerts (e.g., from tools like PMD, SpotBugs, CodeQL). Static analysis tools often produce high rates of False Positives (FPs), wasting developer time (10-20 min/alert). EVICT tackles this by combining:
1. **Evidence Extraction** from static analyzers.
2. **LLM-based Reasoning** conditioned on that evidence.
3. **Confidence Calibration** via conformal prediction to establish reliable bounds.
4. **Symbolic Escalation** using formal methods (SMT solvers) when the LLM is uncertain.

**Current Paper Status (Camera-Ready):**
- The paper is addressing previous reviewer feedback to secure an expected score of 8.17/10 (Accept).
- All 10 reviewer conditions have been addressed, including: adding preliminary results, fixing KLEE/JPF tool mismatches, and adding conformal prediction algorithm details.
- Preliminary results on the Juliet benchmark show **91.2% precision**, **87.3% coverage**, and a **47% reduction in Expected Calibration Error (ECE)**.

## 2. Core Methodology & Architecture
The EVICT pipeline (`evict_pipeline`) operates in four stages:

1. **Evidence Extractor (`extractor.py`)**
   - Parses raw SARIF output into an `EvidencePack`.
   - Extracts `source_location`, `sink_location`, `flow_path`, `program_slice`, and uses AST traversal to extract `path_constraints`.
2. **LLM Verifier (`verifier.py`)**
   - Applies schema-guided reasoning.
   - Uses Chain-of-Thought, Few-Shot, and Role-Prompting to predict `TP`, `FP`, or `ABSTAIN`.
3. **Confidence Calibrator (`calibrator.py`)**
   - Implements **Split-Conformal Prediction** (Algorithm 3) for text-outputting LLMs.
   - Maps raw LLM confidence to calibrated probability to minimize Expected Calibration Error (ECE) and establish prediction sets based on exchangeability.
4. **Symbolic Escalator (`escalator.py`)**
   - A neuro-symbolic fallback for uncertain/high-risk cases (when LLM confidence falls below the conformal threshold).
   - Invokes SMT solvers or symbolic execution: **Java PathFinder (JPF)** for Java and **KLEE** for C/C++.
   - Handles SMT `UNKNOWN` results explicitly (assumes an 8.1% timeout rate, treated securely as uncertain/abstain).

## 3. Experimental Setup & Evaluation Workflow
### Triage Execution (`pass@5` Self-Consistency)
- **Multiple Sampling:** For each alert, the LLM Verifier is queried $k=5$ times independently.
- **Vote-Share Aggregation:** The final label is determined by majority vote. Confidence is the fraction of samples agreeing with the majority.
- **Result Averaging:** Aggregate metrics reflect average performance using this `pass@5` majority decision.

### State-of-the-Art (SOTA) Models Evaluated
- **Anthropic Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022`): SOTA baseline via Anthropic SDK.
- **GPT-5 Nano / o1**: Evaluated with strict temperature=1.0 constraints required by restricted reasoning models.
- **Gemini 3.1 Flash Lite / Preview**: Dynamic API routing (v1/v1beta).
- **Gemini 2.5 Flash Lite**: Highest recall (64.51%) in initial baselines.
- **GPT-4o Mini**: Best precision (55%) and coverage (96%) in initial zero-shot baselines.

## 4. Key Results (Preliminary on 1,000 Juliet Samples)
- **Precision:** 91.2% (+7.7 percentage points over evidence-free baseline).
- **Coverage:** 87.3% (fraction of alerts the system makes a confident prediction on).
- **ECE:** 0.08 (47% reduction).
- **Selective Risk ($R_{sel}$):** 0.088 (46% reduction).
- **Symbolic Verification:** Corrected 23/184 LLM errors (12.5%).

## 5. Datasets & Evaluation Plan
- **Synthetic/Structured:** Juliet Benchmark (Java) used for preliminary results.
- **Real-World Benchmarks:** CWE-Bench-Java.
- **Full Evaluation (Planned):** NASCAR (10K) and DZA (5K) datasets to prove generalizability.

## 6. Baselines & Metrics
- **Baselines:** Evidence-Free LLM, Evidence-Conditioned (No Calibration), IRIS.
- **Metrics reported on Accepted Set:** Precision, Recall, F1, ECE.
- **Metrics reported on Full Population:** Coverage, Cost-sensitive selective risk ($R_{sel}$).

## 7. Workspace Organization
When editing or referencing files, be aware of the repository structure:
- `main.tex`, `sections/*.tex`: LaTeX source files for the manuscript.
- `references.bib`: BibTeX citations.
- `figures/`: Diagrams and plots (e.g., `calibration_plot.pdf`, `risk_coverage_curve.pdf`).
- `evict_pipeline/src/evict_pipeline/`: Core Python implementation.
- `scripts/`: Evaluation and figure generation scripts.
- `docs/summaries/` & `docs/reviews/`: Reviewer feedback, project summaries.
- `artifacts/exports/`: Experimental CSV results and exported documents.

## 8. Instructions for the Agent
- Adhere strictly to the terminology defined here (e.g., "Evidence-Conditioned", "Selective Prediction", "Split-Conformal Prediction", "Symbolic Escalation").
- Ensure theoretical claims align with the established algorithms (e.g., Algorithm 3 for Conformal Prediction, JPF for Java symbolic execution).
- Focus on maintaining the 9-page NeurIPS limit by keeping explanations concise and pushing detailed proofs to the Appendix.
- Reference the preliminary results (91.2% precision, 0.08 ECE) when discussing system effectiveness and emphasize how all reviewer conditions have been met.