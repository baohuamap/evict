# EVICT: Evidence-Conditioned Investigation with Calibrated Triage

EVICT is a research framework designed to improve the triage of static analysis alerts. It combines LLM-based reasoning, automated evidence extraction, confidence calibration via conformal prediction, and symbolic execution for escalation.

This repository contains both the academic manuscript and the functional Python implementation of the EVICT pipeline.

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Java JRE/JDK** (Required for static analyzers like PMD and SpotBugs)
- **Environment Variables**: You will need an API key for the LLM provider of your choice.
  - `OPENAI_API_KEY`: For GPT-4o, GPT-4o-mini, etc.
  - `GEMINI_API_KEY`: For Gemini 1.5 Pro/Flash.
  - `LOCAL_LLM_URL`: (Optional) If using a local server like Ollama or vLLM.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/evict.git
   cd evict
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the pipeline in editable mode:
   ```bash
   pip install -e "./evict_pipeline[dev]"
   ```

---

## 📊 Benchmarking

We evaluate EVICT on two primary datasets: **Juliet (Java)** and **CWE-Bench-Java**.

### 1. Juliet Benchmark (NIST)
Synthetic test cases with known vulnerabilities (True Positives) and "good" counterparts (False Positives).

#### **Option A: Quick POC (PMD)**
Best for verifying the pipeline works on a small subset of CWEs.
```bash
# Downloads PMD, clones Juliet, and runs PMD on CWE-23, 78, 89
bash scripts/setup_juliet_pmd.sh

# Runs EVICT triage on the generated SARIF
python scripts/run_juliet_poc.py
```

#### **Option B: Full/Sampled Evaluation (SpotBugs)**
Best for comparative research across many CWEs.
```bash
# 1. Setup SpotBugs and Juliet
bash scripts/setup_juliet_spotbugs.sh

# 2. Generate SARIFs for all Juliet modules (requires ~20 mins)
bash scripts/generate_full_juliet_sarif.sh

# 3. Run comparative evaluation on a random sample
python scripts/benchmark_juliet_sampling.py
```

### 2. CWE-Bench-Java
Real-world vulnerabilities and fixes from various open-source projects.

**Setup & Generation:**
```bash
# 1. Clone CWE-Bench-Java and IRIS v2
bash scripts/setup_cwe_bench.sh

# 2. Build databases and run CodeQL (requires Docker)
bash scripts/generate_sarifs.sh
```

**Run Triage:**
```bash
# Runs EVICT on CWE-Bench-Java alerts and compares against ground truth
python scripts/benchmark_cwe_bench.py
```

---

## 🛠 Project Structure

- `evict_pipeline/`: Core implementation.
  - `src/evict_pipeline/`: Source code (Extractor, Verifier, Calibrator, Escalator).
  - `tests/`: Unit and integration tests.
- `scripts/`: Automation scripts for setup and benchmarking.
- `data/`: Dataset storage (Juliet, CWE-Bench-Java).
- `sections/`, `main.tex`: LaTeX source for the research paper.
- `figures/`: Generated plots and diagrams.

---

## 🧪 Testing & Development

Run the test suite to ensure everything is configured correctly:
```bash
pytest evict_pipeline/tests
```

