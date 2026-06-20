#!/bin/bash

# scripts/generate_sarifs.sh
# Phase 1: Build CodeQL databases and generate raw SARIF alerts for the benchmark.

set -e

PROJECT_ROOT=$(pwd)
IRIS_DIR="$PROJECT_ROOT/data/iris-v2"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/codeql_results"
DB_DIR="$IRIS_DIR/data/codeql-dbs"

# CodeQL query configuration.
# The query path "java/ql/src/Security/" previously used here does not exist in
# the bundled IRIS CodeQL distribution and caused a fatal "not a .ql file, .qls
# file, a directory, or a query pack specification" error (0 SARIFs generated).
# The IRIS CodeQL distro ships query packs under
# qlpacks/codeql/java-queries/<version>/; only version 0.8.3 is present, so the
# version MUST match what is on disk (data/iris-v2/src/config.py also expects
# this version). We run the java-security-alerts query suite (a thin wrapper over
# java-code-scanning.qls that excludes IRIS's experimental myqueries/) with
# --search-path so the qlpack dependencies (codeql/suite-helpers, codeql/java-all) resolve.
CODEQL_BIN="${CODEQL_BIN:-codeql}"
CODEQL_QUERY_VERSION="${CODEQL_QUERY_VERSION:-0.8.3}"
CODEQL_QUERIES="$IRIS_DIR/codeql/qlpacks/codeql/java-queries/$CODEQL_QUERY_VERSION"
SECURITY_SUITE="${SECURITY_SUITE:-$CODEQL_QUERIES/codeql-suites/java-security-alerts.qls}"
SEARCH_PATH="$IRIS_DIR/codeql/qlpacks"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$DB_DIR"

# Bootstrap the custom query suite on first run. The suite lives inside the
# qlpack's codeql-suites dir (required for `import`/`from` pack references to
# resolve); the IRIS codeql distro is gitignored, so we generate the file here
# rather than committing it. It re-uses the standard code-scanning selector
# (problem/path-problem kinds, high precision, security-tagged) and excludes
# IRIS's experimental myqueries/ so only standard CodeQL security alerts run.
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
    
    # Run the java-security-alerts query suite. --search-path lets CodeQL resolve
    # the codeql/java-queries and codeql/suite-helpers qlpacks from the bundled
    # IRIS distribution rather than requiring a global query pack install.
    "$CODEQL_BIN" database analyze "$db" \
        "$SECURITY_SUITE" \
        --search-path="$SEARCH_PATH" \
        --format=sarif-latest \
        --threads=2 \
        --output="$output_sarif"
done

echo ""
echo "=== Generation Complete ==="
echo "All raw alert files are located in: $OUTPUT_DIR"
echo "You can now run Phase 2 (the EVICT triage) for any model."
