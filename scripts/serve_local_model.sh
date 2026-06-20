#!/bin/bash
#
# serve_local_model.sh -- Launch a vLLM OpenAI-compatible server for an
# on-prem model (GLM, Kimi K2, DeepSeek, Qwen Coder, ...) so the EVICT
# benchmark scripts can point at it via --base_url.
#
# Topology: run this on the GPU box. Then from your laptop run:
#   export LOCAL_LLM_URL=http://<gpu-host>:8000/v1
#   export LOCAL_MODEL_NAME=<served-model-name>
#   python scripts/benchmark_juliet_conformal.py --live \
#       --base_url "$LOCAL_LLM_URL" --model "$LOCAL_MODEL_NAME"
#
# Usage:
#   bash scripts/serve_local_model.sh <model-alias> [options]
#
# Model aliases:
#   glm-4.5        THUDM/glm-4.5              (128k ctx, trust-remote-code)
#   glm-4.6        THUDM/glm-4.6              (128k ctx, trust-remote-code)
#   kimi-k2        moonshotai/Kimi-K2-Instruct (128k ctx, 1T MoE)
#   deepseek-v3    deepseek-ai/DeepSeek-V3    (128k ctx)
#   deepseek-r1    deepseek-ai/DeepSeek-R1    (128k ctx, thinking model)
#   qwen-coder-32b Qwen/Qwen2.5-Coder-32B-Instruct (128k ctx)
#   qwen-coder-7b  Qwen/Qwen2.5-Coder-7B-Instruct  (128k ctx)
#
# Options:
#   --tp N           tensor-parallel size (default: 1; use # of GPUs)
#   --port PORT      vLLM port (default: 8000)
#   --host HOST      bind address (default: 0.0.0.0 -> listen on all IFs)
#   --max-model-len N  override context length (useful to fit GPU memory)
#   --gpu-util F     gpu-memory-utilization (default: 0.90)
#   --name NAME      --served-model-name override (default: <model-alias>)
#   --docker         launch inside an nvidia/cuda docker container
#   --dry-run        print the vLLM command without executing
#
set -e

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
TP=1
PORT=8000
HOST=0.0.0.0
GPU_UTIL=0.90
MAX_MODEL_LEN=""
SERVED_NAME=""
USE_DOCKER=0
DRY_RUN=0
EXTRA_ARGS=""

# ---------------------------------------------------------------------------
# Model registry: alias -> "huggingface_id|default_max_len|extra_vllm_flags"
# ---------------------------------------------------------------------------
get_model_info() {
    case "$1" in
        glm-4.5)
            echo "THUDM/glm-4.5|131072|--trust-remote-code";;
        glm-4.6)
            echo "THUDM/glm-4.6|131072|--trust-remote-code";;
        kimi-k2)
            echo "moonshotai/Kimi-K2-Instruct|131072|--trust-remote-code";;
        deepseek-v3)
            echo "deepseek-ai/DeepSeek-V3|131072|";;
        deepseek-r1)
            echo "deepseek-ai/DeepSeek-R1|131072|";;
        qwen-coder-32b)
            echo "Qwen/Qwen2.5-Coder-32B-Instruct|131072|--trust-remote-code";;
        qwen-coder-7b)
            echo "Qwen/Qwen2.5-Coder-7B-Instruct|131072|--trust-remote-code";;
        *)
            echo "ERROR: Unknown model alias '$1'" >&2
            echo "Known aliases: glm-4.5, glm-4.6, kimi-k2, deepseek-v3, deepseek-r1, qwen-coder-32b, qwen-coder-7b" >&2
            exit 1;;
    esac
}

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
# Handle --help / -h before requiring the model alias positional arg.
for a in "$@"; do
    if [ "$a" = "--help" ] || [ "$a" = "-h" ]; then
        sed -n '2,40p' "$0"
        exit 0
    fi
done

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/serve_local_model.sh <model-alias> [options]" >&2
    echo "Run with --help for details." >&2
    exit 1
fi

MODEL_ALIAS="$1"
shift

while [ $# -gt 0 ]; do
    case "$1" in
        --tp)            TP="$2"; shift 2;;
        --port)          PORT="$2"; shift 2;;
        --host)          HOST="$2"; shift 2;;
        --max-model-len) MAX_MODEL_LEN="$2"; shift 2;;
        --gpu-util)      GPU_UTIL="$2"; shift 2;;
        --name)          SERVED_NAME="$2"; shift 2;;
        --docker)        USE_DOCKER=1; shift;;
        --dry-run)       DRY_RUN=1; shift;;
        --help|-h)       sed -n '2,40p' "$0"; exit 0;;
        *)               EXTRA_ARGS="$EXTRA_ARGS $1"; shift;;
    esac
done

# ---------------------------------------------------------------------------
# Resolve model
# ---------------------------------------------------------------------------
MODEL_INFO=$(get_model_info "$MODEL_ALIAS")
if [ -z "$MODEL_INFO" ]; then exit 1; fi

MODEL_ID=$(echo "$MODEL_INFO"   | cut -d'|' -f1)
DEFAULT_LEN=$(echo "$MODEL_INFO" | cut -d'|' -f2)
MODEL_FLAGS=$(echo "$MODEL_INFO" | cut -d'|' -f3)

MAX_LEN="${MAX_MODEL_LEN:-$DEFAULT_LEN}"
SERVED_NAME="${SERVED_NAME:-$MODEL_ALIAS}"

echo "=== vLLM launch plan ==="
echo "  alias:           $MODEL_ALIAS"
echo "  huggingface id:  $MODEL_ID"
echo "  served-model-name: $SERVED_NAME"
echo "  tensor parallel: $TP"
echo "  host:port:       $HOST:$PORT"
echo "  max-model-len:   $MAX_LEN"
echo "  gpu-util:        $GPU_UTIL"
echo "  extra vllm flags:$MODEL_FLAGS $EXTRA_ARGS"
echo "  docker:          $USE_DOCKER"
echo "  dry-run:         $DRY_RUN"
echo

# ---------------------------------------------------------------------------
# Build the vLLM command
# ---------------------------------------------------------------------------
# Notes:
#  --api-key EMPTY: vLLM accepts any string for OpenAI compat; we publish
#                   "EMPTY" so clients can pass it as the bearer token.
#  --enable-auto-tool-choice / --tool-call-parser: not all models support
#                   this; left off by default. EVICT only needs plain chat
#                   completions + JSON-in-text, so default parsing is fine.
#  --enforce-eager: not set by default; GLM/Kimi benefit from CUDA graphs.
VLLM_ARGS=(
    --host "$HOST"
    --port "$PORT"
    --model "$MODEL_ID"
    --served-model-name "$SERVED_NAME"
    --tensor-parallel-size "$TP"
    --max-model-len "$MAX_LEN"
    --gpu-memory-utilization "$GPU_UTIL"
    --api-key EMPTY
    --dtype auto
)
# Append model-specific flags (e.g. --trust-remote-code)
for f in $MODEL_FLAGS $EXTRA_ARGS; do
    VLLM_ARGS+=( "$f" )
done

# ---------------------------------------------------------------------------
# Launch (native or docker)
# ---------------------------------------------------------------------------
run_native() {
    echo "Launching vLLM (native)..."
    echo "Command: vllm serve ${VLLM_ARGS[*]}"
    if [ "$DRY_RUN" = "1" ]; then
        echo "[dry-run] not executing."
        return 0
    fi
    exec vllm serve "${VLLM_ARGS[@]}"
}

run_docker() {
    local IMAGE="vllm/vllm-openai:latest"
    echo "Launching vLLM inside Docker ($IMAGE)..."
    local DOCKER_ARGS=(
        --rm
        --gpus all
        --shm-size 32g
        -p "${PORT}:${PORT}"
        -v "${HOME}/.cache/huggingface:/root/.cache/huggingface"
        "$IMAGE"
        --host 0.0.0.0
    )
    # Strip our --host and replace with the container-friendly 0.0.0.0.
    local FILTERED=()
    local skip=0
    for a in "${VLLM_ARGS[@]}"; do
        if [ "$skip" = "1" ]; then skip=0; continue; fi
        if [ "$a" = "--host" ]; then skip=1; continue; fi
        FILTERED+=( "$a" )
    done
    echo "Command: docker run ${DOCKER_ARGS[*]} ${FILTERED[*]}"
    if [ "$DRY_RUN" = "1" ]; then
        echo "[dry-run] not executing."
        return 0
    fi
    exec docker run "${DOCKER_ARGS[@]}" "${FILTERED[@]}"
}

if [ "$USE_DOCKER" = "1" ]; then
    run_docker
else
    run_native
fi
