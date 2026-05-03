#!/bin/bash
set -e

# Configuration
PMD_VERSION="7.1.0"
PMD_URL="https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.1.0/pmd-dist-${PMD_VERSION}-bin.zip"
JULIET_URL="https://sard.nist.gov/downloads/test-suites/2017-10-01-juliet-java-v1-3.zip"

# Create directories
mkdir -p data/juliet_java
mkdir -p bin
mkdir -p artifacts/exports

# Download and Setup PMD
if [ ! -d "bin/pmd-bin-${PMD_VERSION}" ]; then
    echo "Downloading PMD ${PMD_VERSION}..."
    curl -L "$PMD_URL" -o bin/pmd.zip
    unzip -q bin/pmd.zip -d bin/
    rm bin/pmd.zip
fi
PMD_BIN="$(pwd)/bin/pmd-bin-${PMD_VERSION}/bin/pmd"

# Download and Setup Juliet Java
if [ ! -d "data/juliet_java/juliet-cwe89" ]; then
    echo "Cloning Juliet Java mirror..."
    git clone --depth 1 https://github.com/UnitTestBot/juliet-java-test-suite.git data/juliet_java
fi

# Run PMD on a subset of Juliet (CWE-89, CWE-78, CWE-23) for the POC
echo "Running PMD on Juliet subset (CWE 23, 78, 89)..."
$PMD_BIN check \
    -d data/juliet_java/juliet-cwe89/src/main/java/juliet/testcases/CWE89_SQL_Injection \
    -d data/juliet_java/juliet-cwe78/src/main/java/juliet/testcases/CWE78_OS_Command_Injection \
    -d data/juliet_java/juliet-cwe23/src/main/java/juliet/testcases/CWE23_Relative_Path_Traversal \
    -R category/java/errorprone.xml,category/java/security.xml \
    -f sarif \
    -r data/juliet_alerts_pmd.sarif || true

echo "Setup complete. SARIF generated at data/juliet_alerts_pmd.sarif"
