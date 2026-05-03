#!/bin/bash

# setup_cwe_bench.sh - Environment setup for IRIS and CWE-Bench-Java

set -e

PROJECT_ROOT=$(pwd)
DATA_DIR="$PROJECT_ROOT/data"

mkdir -p "$DATA_DIR"

echo "Cloning CWE-Bench-Java..."
if [ ! -d "$DATA_DIR/cwe-bench-java" ]; then
    git clone https://github.com/iris-sast/cwe-bench-java.git "$DATA_DIR/cwe-bench-java"
else
    echo "CWE-Bench-Java already exists, skipping clone."
fi

echo "Cloning IRIS v2..."
if [ ! -d "$DATA_DIR/iris-v2" ]; then
    git clone --branch v2 https://github.com/iris-sast/iris.git "$DATA_DIR/iris-v2"
else
    echo "IRIS v2 already exists, skipping clone."
fi

echo "Setup complete. Repositories are in $DATA_DIR"
