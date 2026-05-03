# EVICT Framework Implementation Details

This document consolidates key implementation details of the EVICT (Evidence-Conditioned Investigation with Calibrated Triage) framework to assist with manuscript writing.

## 1. Core Architecture Components (`evict_pipeline`)

The EVICT pipeline operates in four main stages:

### A. Evidence Extractor (`extractor.py`)
- **Purpose**: Converts raw SARIF analyzer output into a structured `EvidencePack`.
- **Outputs**: `source_location`, `sink_location`, `flow_path`, `program_slice`, `path_constraints`.
- **Key Techniques**: Uses AST traversal for extracting path constraints from code. Handles cases where flow is partial or constraints are missing.

### B. LLM Verifier (`verifier.py`)
- **Purpose**: Applies schema-guided reasoning to evaluate the alert and evidence.
- **Outputs**: Label (`TP`, `FP`, `ABSTAIN`), Confidence score, Rationale.
- **Key Techniques**: Prompting enhancements (Chain-of-Thought, Few-Shot, Role-Prompting) condition the LLM on the `EvidencePack`.

### C. Confidence Calibrator (`calibrator.py`)
- **Purpose**: Ensures reliable triage through confidence calibration.
- **Key Techniques**: Implements **Split-Conformal Prediction** (Algorithm 3 in the paper) for text-outputting LLMs. Computes conformity scores and establishes prediction sets based on exchangeability. Maps raw LLM confidence to calibrated probability to minimize Expected Calibration Error (ECE).

### D. Symbolic Escalator (`escalator.py`)
- **Purpose**: A neuro-symbolic fallback mechanism for uncertain or high-risk cases.
- **Key Techniques**:
  - Invokes SMT solvers (Z3) or symbolic execution tools.
  - **Tool Mismatch Handled**: Uses **Java PathFinder (JPF)** for Java and **KLEE** for C/C++.
  - Explicit handling for SMT `UNKNOWN` results (treated as uncertain/abstain). Corrects LLM errors when confidence falls below the calibrated threshold.

---

## 2. Datasets

The evaluation plan spans both synthetic benchmarks and real-world vulnerability datasets.

- **Juliet Benchmark (Java)**: Used for preliminary results (1,000 samples). Synthetic but highly structured data for testing fundamental capabilities.
  - **CWE-Based Evaluation**: The pipeline evaluates Juliet data by systematically iterating through isolated SARIF files, where each file maps to a specific Common Weakness Enumeration (CWE). This allows for granular performance tracking per vulnerability type.
  - **Sampling Strategy**: To maintain a balanced and efficient evaluation scale, the benchmark script employs a randomized sampling strategy. For each CWE, it randomly selects between 50 and 100 alerts. If a CWE has fewer alerts than the requested sample size, all available alerts are utilized.
  - **Resumable Processing**: To handle large-scale datasets, the evaluation pipeline utilizes an alert fingerprinting mechanism (based on Alert ID, file path, and line number). This ensures that evaluation can be safely resumed across multiple execution sessions without duplicating triage efforts.
- **CWE-Bench-Java**: A benchmark of real-world Java vulnerabilities.


---

## 3. Baselines

- **Evidence-Free LLM**: Standard zero-shot LLM prediction using only the alert description without the structured `EvidencePack`.
- **Evidence-Conditioned (No Calibration)**: LLM prediction with `EvidencePack` but relying on raw, uncalibrated confidence scores.
- **IRIS**: State-of-the-art literature baseline for comparative evaluation.

---

## 4. Evaluation Metrics

- **Precision**: Accuracy of `TP` predictions. EVICT achieved **91.2%** in prelims (+7.7 pp over baseline).
- **Recall (Sensitivity)**: Ability to capture all true positive vulnerabilities (low false negatives).
- **Accuracy**: Overall correctness across TP and FP classifications.
- **Coverage**: The fraction of total alerts the system makes a confident prediction on (vs. abstaining/escalating). EVICT prelim: **87.3%**.
- **Expected Calibration Error (ECE)**: The difference between predicted confidence and empirical accuracy. EVICT prelim: **0.08** (47% reduction).
- **Selective Risk (Error Rate)**: The error rate measured specifically on the subset of covered predictions.

---

## 5. Hyperparameters and Models

### Models Evaluated (PoC)
- **Anthropic Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022`): Added via the official Anthropic SDK as a new state-of-the-art (SOTA) baseline.
- **GPT-5 Nano / o1**: Supported with automatic strict temperature=1.0 constraints required by restricted reasoning models.
- **Gemini 3.1 Flash Lite / Preview**: Validated with dynamic API version routing (v1/v1beta).
- **Gemini 2.5 Flash Lite**: Highest recall (64.51%), best for catching real bugs in initial baselines.
- **GPT-4o Mini**: Best precision (55%) and coverage (96%), strong all-rounder in initial baselines.
- **DeepSeek 7B**: Lower performance in PoC without advanced prompting.

---

## 6. Experimental Setup and Evaluation Workflow

### A. Triage Execution (`pass@5`)
To ensure robust reasoning and handle stochasticity in LLM outputs, EVICT employs a **self-consistency (SC)** mechanism, specifically a **pass@5** setup:
- **Multiple Sampling**: For every alert, the LLM Verifier is queried $k=5$ times independently with a temperature of 0.7 (or 1.0 for restricted models).
- **Vote-Share Aggregation**:
  - The final label (`TP`, `FP`, or `ABSTAIN`) is determined by a simple **majority vote** among the 5 samples.
  - The **Confidence Score** is calculated as the fraction of samples that agree with the majority label (e.g., if 4 out of 5 samples predicted `TP`, confidence is 0.80).
- **Result Averaging**: When reporting aggregate metrics (Precision, Recall, etc.) across a dataset, the results reflect the **average performance** across all triaged alerts using this pass@5 majority decision.

### B. Running a Benchmark
To generate a new evaluation result, follow these steps:
1. **Setup Environment**: Ensure `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY` is exported.
2. **Execute Script**:
   ```bash
   # For synthetic Juliet data:
   python scripts/benchmark_juliet_sampling.py --model claude-3-5-sonnet-20241022

   # For real-world CWE-Bench data:
   python scripts/benchmark_cwe_bench.py --model gpt-5-nano
   ```
3. **Resumability**: If a run is interrupted, re-running the script with the same parameters will skip already processed alerts by checking the output CSV.

### C. Analyzing Results
Output CSVs (located in `artifacts/exports/`) provide a granular view of every triage decision.
1. **Metric Calculation**: Use `scripts/analyze_juliet_performance.py` to compute aggregate metrics from the generated CSV.
2. **Interpreting ECE**: A high **Expected Calibration Error (ECE)** indicates that the LLM's confidence does not match its empirical accuracy. EVICT's Calibrator stage aims to minimize this.
3. **Selective Risk ($R_{sel}$)**: Analyze the error rate on only the high-confidence (Calibrated) predictions. A successful triage system should show significantly higher accuracy on its "covered" set than on its "abstain/escalate" set.
4. **Rationale Review**: For problematic CWEs, inspect the `Rationale` column in the CSV to identify recurring reasoning failures (e.g., "lost track of tainted variable" or "misunderstood sanitizer logic").