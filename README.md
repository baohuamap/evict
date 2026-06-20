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
  - `ANTHROPIC_API_KEY`: For Claude 3.5 Sonnet / Haiku / Opus.
  - `LOCAL_LLM_URL` + `LOCAL_MODEL_NAME`: For on-prem OpenAI-compatible servers (vLLM, SGLang, Ollama, TGI). See [On-Prem LLM Benchmarking](#-on-prem-llm-benchmarking) below.

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

## 🖥 On-Prem LLM Benchmarking

EVICT can target any **OpenAI-compatible** on-prem LLM server (vLLM, SGLang, Ollama, TGI) instead of a hosted API. This is the recommended setup for benchmarking open models such as **GLM-4.5/4.6**, **Kimi K2**, **DeepSeek-V3/R1**, or **Qwen2.5-Coder**.

### 1. Serve the model with vLLM (on the GPU box)

`scripts/serve_local_model.sh` launches vLLM with sensible per-model defaults (context length, `--trust-remote-code`, tensor parallelism). Run it on the GPU host:

```bash
# GLM-4.5 on a single GPU
bash scripts/serve_local_model.sh glm-4.5 --tp 1

# Kimi K2 across 8 GPUs (1T MoE)
bash scripts/serve_local_model.sh kimi-k2 --tp 8

# DeepSeek-R1, 4 GPUs, custom port
bash scripts/serve_local_model.sh deepseek-r1 --tp 4 --port 8001

# Qwen2.5-Coder-32B
bash scripts/serve_local_model.sh qwen-coder-32b --tp 4

# Inside Docker (mounts HF cache, exposes the port)
bash scripts/serve_local_model.sh glm-4.5 --docker

# Just print the vLLM command without launching
bash scripts/serve_local_model.sh kimi-k2 --dry-run
```

Supported aliases: `glm-4.5`, `glm-4.6`, `kimi-k2`, `deepseek-v3`, `deepseek-r1`, `qwen-coder-32b`, `qwen-coder-7b`. Run `bash scripts/serve_local_model.sh --help` for the full flag list (`--host`, `--port`, `--tp`, `--max-model-len`, `--gpu-util`, `--name`, `--docker`, `--dry-run`).

The server listens on `0.0.0.0:8000` and advertises an OpenAI-compatible `/v1/chat/completions` endpoint. Verify it is up:

```bash
curl http://gpu-host:8000/v1/models
```

### 2. Run the benchmark (on your laptop)

Point the benchmark scripts at the remote server with `--base_url` and `--model`:

```bash
# Juliet conformal PoC (k=5 self-consistency + 5-fold CV) against GLM-4.5
python scripts/benchmark_juliet_conformal.py --live \
    --base_url http://gpu-host:8000/v1 \
    --model glm-4.5

# CWE-Bench-Java against Kimi K2 with k=5 vote-share
python scripts/benchmark_cwe_bench.py \
    --base_url http://gpu-host:8000/v1 \
    --model kimi-k2 \
    --num_samples 5
```

Or use environment variables (e.g. for `run_juliet_poc.py`, which already reads them):

```bash
export LOCAL_LLM_URL=http://gpu-host:8000/v1
export LOCAL_MODEL_NAME=glm-4.5
python scripts/benchmark_juliet_conformal.py --live
```

### Notes

- When `--base_url` is set, the script forces `provider=openai` and uses `api_key=EMPTY` (vLLM accepts any string). Set `LOCAL_LLM_API_KEY` or `OPENAI_API_KEY` if your server enforces a real key.
- `--model` **must** match the `--served-model-name` advertised by the server (the alias passed to `serve_local_model.sh`, unless overridden with `--name`).
- `benchmark_juliet_conformal.py` uses `num_samples=5` per alert for self-consistency voting, i.e. 5x the LLM calls. Local inference is free but not necessarily fast — budget accordingly. Decisions are cached to `.cache.json` next to the output for resumability.
- For thinking models (DeepSeek-R1), the JSON triage decision is parsed out of the final assistant message via regex, so chain-of-thought traces in the response are tolerated.

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

