# EVICT: Evidence-Conditioned Investigation with Calibrated Triage

This repository implements the EVICT framework for static analysis alert triage.

## Pipeline Architecture
1.  **Evidence Extraction:** Converts SARIF analyzer output into structured `EvidencePack`.
2.  **LLM Verification:** Applies schema-guided reasoning (TP/FP/Abstain).
3.  **Confidence Calibration:** Uses split-conformal prediction for reliable triage.
4.  **Symbolic Escalation:** Invokes Z3/JPF/KLEE for uncertain or high-risk cases.

## Installation
```bash
pip install -e ".[dev]"
```

## Usage
```python
from evict_pipeline import EvictPipeline
pipeline = EvictPipeline()
result = pipeline.run("alert.sarif")
```
