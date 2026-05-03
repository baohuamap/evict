#!/bin/bash

# scripts/run_full_cwe_bench.sh
# Orchestrates the full build, analysis, and evaluation cycle for CWE-Bench-Java.

set -e

PROJECT_ROOT=$(pwd)
IRIS_DIR="$PROJECT_ROOT/data/iris-v2"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/codeql_results"
EVICT_RESULTS_DIR="$PROJECT_ROOT/artifacts/exports"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$EVICT_RESULTS_DIR"

echo "=== Starting FULL CWE-Bench-Java Evaluation ==="
echo "Estimated time: 20-60 hours."
echo "Note: Ensure Docker is running and CodeQL CLI is installed."

# 1. Build CodeQL Databases for ALL projects
# The IRIS script will iterate through all projects in build_info.csv by default.
# We use --use-container to handle complex Java environments.
echo "[Step 1/3] Building CodeQL databases (this will take a LONG time)..."
cd "$IRIS_DIR"
# Note: This will skip projects that are already built if IRIS logic supports it.
python3 scripts/build_codeql_dbs.py --use-container --db-path "$IRIS_DIR/data/codeql-dbs"

# 2. Run Security Queries on all generated databases
echo "[Step 2/3] Analyzing databases to generate SARIF results..."
DB_DIR="$IRIS_DIR/data/codeql-dbs"
# We look for all -docker databases created by the previous step
for db in "$DB_DIR"/*-docker; do
    [ -d "$db" ] || continue
    slug=$(basename "$db" | sed 's/-docker//')
    output_sarif="$OUTPUT_DIR/$slug.sarif"
    
    # Skip if already analyzed to allow resumption
    if [ -f "$output_sarif" ]; then
        echo "Skipping $slug (already analyzed)"
        continue
    fi
    
    echo "Analyzing $slug..."
    codeql database analyze "$db" \
        java/ql/src/Security/ \
        --format=sarif-latest \
        --output="$output_sarif"
done

# 3. Run EVICT Benchmark
echo "[Step 3/3] Running EVICT Triage Evaluation..."
cd "$PROJECT_ROOT"
# Ensure your LLM environment variables are set before running this!
source venv/bin/activate
python3 scripts/benchmark_cwe_bench.py

echo "=== FULL Benchmark Cycle Complete! ==="
echo "Consolidated metrics are in $EVICT_RESULTS_DIR/cwe_bench_evict_results.csv"
