#!/bin/bash

# scripts/run_full_cwe_bench.sh
# Orchestrates the full build, analysis, and evaluation cycle for CWE-Bench-Java.

set -e

PROJECT_ROOT=$(pwd)
IRIS_DIR="$PROJECT_ROOT/data/iris-v2"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/codeql_results"
EVICT_RESULTS_DIR="$PROJECT_ROOT/artifacts/exports"

# CodeQL query configuration (see generate_sarifs.sh for rationale).
# The previous query path "java/ql/src/Security/" was invalid and produced a
# fatal error; only version 0.8.3 of the java-queries pack ships with IRIS.
CODEQL_BIN="${CODEQL_BIN:-codeql}"
CODEQL_QUERY_VERSION="${CODEQL_QUERY_VERSION:-0.8.3}"
CODEQL_QUERIES="$IRIS_DIR/codeql/qlpacks/codeql/java-queries/$CODEQL_QUERY_VERSION"
SECURITY_SUITE="${SECURITY_SUITE:-$CODEQL_QUERIES/codeql-suites/java-security-alerts.qls}"
SEARCH_PATH="$IRIS_DIR/codeql/qlpacks"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$EVICT_RESULTS_DIR"

# Bootstrap the custom query suite on first run (see generate_sarifs.sh).
if [ ! -f "$SECURITY_SUITE" ]; then
    mkdir -p "$(dirname "$SECURITY_SUITE")"
    cat > "$SECURITY_SUITE" <<'QLS'
- description: Standard CodeQL code-scanning security alert queries for Java.
    Derived from java-code-scanning.qls but excludes IRIS's experimental
    myqueries/ (LLM-generated per-CVE queries) so only standard, high-precision
    security queries run.
- import: codeql-suites/java-code-scanning.qls
- exclude:
    query path:
      - /^myqueries\/.*/
QLS
    echo "Created query suite: $SECURITY_SUITE"
fi

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
    "$CODEQL_BIN" database analyze "$db" \
        "$SECURITY_SUITE" \
        --search-path="$SEARCH_PATH" \
        --format=sarif-latest \
        --threads=2 \
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
