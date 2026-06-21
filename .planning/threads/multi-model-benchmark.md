# Thread: Multi-Model Benchmarking on H100

**Created:** 2026-06-21
**Status:** ACTIVE
**Type:** Cross-session tracking thread
**SSH Host:** `evict-gpu` (root@103.73.232.225, port 52194)
**GPU:** 1x H100 80GB, CUDA 12.4, vLLM 0.7.3, PyTorch 2.5.1

## Purpose

Track the multi-model EVICT benchmarking campaign on the remote H100 GPU server.
Each model runs the Juliet PoC (k=5, 247 alerts, CWE-89/78/190) and CWE-Bench-Java
(k=1, 549 alerts, 45 projects). Results are saved to `FINDINGS_AND_RESULTS.md`
after each model completes.

## Model Queue

| # | Model | Size | Status | Results Saved |
|---|-------|------|--------|---------------|
| 1 | Qwen2.5-Coder-32B-Instruct | 65.5 GB | DONE | Yes (E8, E9) |
| 2 | glm-4-9b-chat | 18.8 GB | PENDING | - |
| 3 | DeepSeek-R1-Distill-Qwen-32B | 65.5 GB | PENDING | - |
| 4 | DeepSeek-Coder-V2-Lite-Instruct | 31.4 GB | PENDING | - |

## Completed Models

### Qwen2.5-Coder-32B-Instruct (vLLM, 2026-06-20)
- **Juliet PoC:** Precision 37.0%, Recall 81.5%, F1 50.7%, ECE 0.565, 85.8% unanimous
- **CWE-Bench:** Precision 1.5%, Recall 40.0%, F1 0.030, 62% abstention (very conservative)
- **Files:** `artifacts/exports/v2/juliet_conformal_poc_qwen_coder_32b.csv`, `artifacts/exports/cwe_bench_evict_results_qwen_coder_32b.csv`
- **Key finding:** 62% abstention on CWE-Bench (vs Gemini's 13%) — more conservative but degenerate vote-share (85.8% unanimous)

## Host Setup Notes

- venv: `/root/evict_venv` (vLLM 0.7.3, torch 2.5.1+cu121, transformers 4.49.0)
- Repo: `/root/evict/` (pipeline + scripts + juliet_sarifs + juliet_java + codeql_results)
- vLLM launch pattern: `tmux new -d -s vllm-<model> 'source /root/evict_venv/bin/activate && python -m vllm.entrypoints.openai.api_server --host 0.0.0.0 --port 8000 --model <hf-id> --served-model-name <alias> --tensor-parallel-size 1 --max-model-len 8192 --gpu-memory-utilization 0.92 --api-key EMPTY --dtype auto [--trust-remote-code]'`
- Benchmark: `cd /root/evict && python3 -u scripts/benchmark_juliet_conformal.py --live --base_url http://localhost:8000/v1 --model <alias> --output artifacts/exports/v2/juliet_conformal_poc_<alias>.csv`
- CWE-Bench: `cd /root/evict && python3 -u scripts/benchmark_cwe_bench.py --base_url http://localhost:8000/v1 --model <alias> --num_samples 1 --output artifacts/exports/cwe_bench_evict_results_<alias>.csv`
- Download results: `ssh evict-gpu "cat /root/evict/<path>" > <local_path>`

## Resume Instructions

If this thread is resumed in a new session:
1. Re-add SSH key: `SSH_AUTH_SOCK=/private/tmp/com.apple.launchd.2wuZVjhV4N/Listeners expect -c 'spawn ssh-add ~/.ssh/lxbach.key; expect "Enter passphrase"; send "824388\r"; expect eof'`
2. Check which model is next from the queue above
3. Check `FINDINGS_AND_RESULTS.md` for completed experiments
4. Continue from the next PENDING model
