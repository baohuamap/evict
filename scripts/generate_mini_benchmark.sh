#!/bin/bash

# scripts/generate_mini_benchmark.sh
# Automates the generation of CodeQL results for a small subset of CWE-Bench-Java.

set -e

# 1. Define the Mini-Benchmark Targets
# We pick one CVE for each of the 4 primary CWEs in the benchmark
# and one extra for robustness.
PROJECTS=(
    "DSpace__DSpace_CVE-2016-10726_4.4"                    # CWE-22 Path Traversal
    "x-stream__xstream_CVE-2013-7285_1.4.6"                 # CWE-078 OS Command Injection
    "xwiki__xwiki-commons_CVE-2023-31126_14.10.3"           # CWE-079 Cross-site Scripting
    "spring-projects__spring-framework_CVE-2022-22965_5.2.19.RELEASE" # CWE-094 Code Injection
    "apache__tika_CVE-2018-11762_1.18"                      # CWE-022 Extra
)

PROJECT_ROOT=$(pwd)
IRIS_DIR="$PROJECT_ROOT/data/iris-v2"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/codeql_results"

mkdir -p "$OUTPUT_DIR"

echo "=== Starting Mini-Benchmark Generation ==="
echo "Note: This requires Docker to be running."

for slug in "${PROJECTS[@]}"; do
    echo "----------------------------------------------------"
    echo "Processing $slug..."
    
    # Step A: Build the project and CodeQL database
    # IRIS v2 uses build_one.py to set up the environment and build.
    # We will use their build_codeql_dbs.py if it supports single project runs.
    
    echo "Building CodeQL database..."
    # We use their existing script. We might need to adjust paths.
    cd "$IRIS_DIR"
    python3 scripts/build_codeql_dbs.py --project "$slug"
    
    # Step B: Run security queries
    echo "Running CodeQL security queries..."
    # This assumes 'codeql' is in the PATH and queries are available.
    # IRIS v2 usually has queries in src/cwe-queries/
    database_path="data/codeql-dbs/$slug"
    output_sarif="$OUTPUT_DIR/$slug.sarif"
    
    codeql database analyze "$database_path" \
        java/ql/src/Security/ \
        --format=sarif-latest \
        --output="$output_sarif"
        
    echo "Done! SARIF saved to $output_sarif"
    cd "$PROJECT_ROOT"
done

echo "=== Mini-Benchmark Generation Complete! ==="
echo "You can now run: python3 scripts/benchmark_cwe_bench.py"
