#!/bin/bash
set -e

# Configuration
SPOTBUGS_VERSION="4.8.4"
SPOTBUGS_URL="https://github.com/spotbugs/spotbugs/releases/download/${SPOTBUGS_VERSION}/spotbugs-${SPOTBUGS_VERSION}.zip"

# Create directories
mkdir -p data/juliet_java
mkdir -p bin
mkdir -p artifacts/exports

# Download and Setup SpotBugs
if [ ! -d "bin/spotbugs-${SPOTBUGS_VERSION}" ]; then
    echo "Downloading SpotBugs ${SPOTBUGS_VERSION}..."
    curl -L "$SPOTBUGS_URL" -o bin/spotbugs.zip
    unzip -q bin/spotbugs.zip -d bin/
    rm bin/spotbugs.zip
fi
SPOTBUGS_BIN="$(pwd)/bin/spotbugs-${SPOTBUGS_VERSION}/bin/spotbugs"

# Ensure Juliet is compiled, as SpotBugs requires class files
echo "Compiling Juliet subsets..."
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
cd data/juliet_java
./gradlew :support:classes :cwe89:classes :cwe78:classes :cwe23:classes -x test
cd ../..

echo "Running SpotBugs on Juliet subset (CWE 23, 78, 89)..."
# SpotBugs requires compiled class files. We analyze the classes directories.
$SPOTBUGS_BIN -textui -sarif \
    -output data/juliet_alerts_spotbugs.sarif \
    -effort:max \
    -low \
    -auxclasspath data/juliet_java/juliet-support/build/classes/java/main \
    data/juliet_java/juliet-cwe89/build/classes/java/main \
    data/juliet_java/juliet-cwe78/build/classes/java/main \
    data/juliet_java/juliet-cwe23/build/classes/java/main || true

echo "Setup complete. SARIF generated at data/juliet_alerts_spotbugs.sarif"
