#!/bin/bash

# scripts/generate_sarifs.sh
# Phase 1: Build CodeQL databases and generate raw SARIF alerts for the benchmark.

set -e

PROJECT_ROOT=$(pwd)
IRIS_DIR="$PROJECT_ROOT/data/iris-v2"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/codeql_results"
DB_DIR="$IRIS_DIR/data/codeql-dbs"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$DB_DIR"

# Ensure virtual environment is active for dependencies (like 'docker' python package)
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo "=== [Phase 1] Building CodeQL Databases ==="
echo "Note: This uses Docker and handles complex Java dependencies."

cd "$IRIS_DIR"
# This script iterates through all projects in build_info.csv
python3 scripts/build_codeql_dbs.py --use-container --db-path "$DB_DIR"

echo ""
echo "=== [Phase 2] Analyzing Databases with CodeQL ==="

# Iterate through each created database
for db in "$DB_DIR"/*-docker; do
    [ -d "$db" ] || continue
    
    # Extract the original project slug (remove -docker suffix)
    slug=$(basename "$db" | sed 's/-docker//')
    output_sarif="$OUTPUT_DIR/$slug.sarif"
    
    # Resumability: Skip if the SARIF for this project already exists
    if [ -f "$output_sarif" ]; then
        echo "Skipping $slug (SARIF already exists at $output_sarif)"
        continue
    fi
    
    echo "----------------------------------------------------"
    echo "Analyzing $slug..."
    
    # Run standard security queries
    # Note: Ensure the 'codeql' command is in your PATH.
    codeql database analyze "$db" \
        java/ql/src/Security/ \
        --format=sarif-latest \
        --output="$output_sarif"
done

echo ""
echo "=== Generation Complete ==="
echo "All raw alert files are located in: $OUTPUT_DIR"
echo "You can now run Phase 2 (the EVICT triage) for any model."
