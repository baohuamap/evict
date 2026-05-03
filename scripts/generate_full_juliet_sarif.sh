#!/bin/bash
set -e

# Configuration
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
SPOTBUGS_VERSION="4.8.4"
SPOTBUGS_BIN="$(pwd)/bin/spotbugs-${SPOTBUGS_VERSION}/bin/spotbugs"
JULIET_DIR="data/juliet_java"
SARIF_OUT_DIR="data/juliet_sarifs"

mkdir -p "$SARIF_OUT_DIR"

# Ensure support classes are built first
echo "Building Juliet support classes..."
cd "$JULIET_DIR"
./gradlew :support:classes -x test
cd ../..

# Get all CWE modules from settings.gradle.kts
# They look like myInclude("cwe15")
CWES=$(grep "myInclude(\"cwe" "$JULIET_DIR/settings.gradle.kts" | sed 's/.*myInclude("\(cwe.*\)")/\1/')

for cwe in $CWES; do
    echo "Processing $cwe..."
    
    # 1. Build the module
    cd "$JULIET_DIR"
    ./gradlew ":$cwe:classes" -x test
    cd ../..
    
    # 2. Run SpotBugs on this module
    classes_dir="$JULIET_DIR/juliet-$cwe/build/classes/java/main"
    if [ -d "$classes_dir" ]; then
        $SPOTBUGS_BIN -textui -sarif \
            -output "$SARIF_OUT_DIR/$cwe.sarif" \
            -effort:max \
            -low \
            -auxclasspath "$JULIET_DIR/juliet-support/build/classes/java/main" \
            "$classes_dir" || true
        echo "Generated $SARIF_OUT_DIR/$cwe.sarif"
        
        # Optional: Clean up classes to save space if needed, 
        # but for 50-100 cases later we might need them.
        # However, EVICT reads source code, not class files.
    else
        echo "Warning: Classes directory not found for $cwe"
    fi
done

echo "Full Juliet SpotBugs analysis complete."
