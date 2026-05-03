import json
import csv
import os
import sys
import random
import time
from pathlib import Path
from typing import List, Dict, Any

# Add evict_pipeline to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))

from evict_pipeline import EvictPipeline, Alert, Decision, Label
from evict_pipeline.extractor import Extractor
from evict_pipeline.verifier import Verifier
from evict_pipeline.calibrator import Calibrator
from evict_pipeline.escalator import Escalator

def run_sampling_benchmark(sarif_dir: str, output_dir: str, model_name: str = None, sample_min: int = 50, sample_max: int = 100, temperature: float = None):
    print(f"Starting sampled Juliet evaluation from {sarif_dir}...")
    
    # Initialize components
    extractor = Extractor()
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("OPENAI_API_KEY"):
        provider = "openai"
    elif os.getenv("GEMINI_API_KEY"):
        provider = "gemini"
    elif os.getenv("ANTHROPIC_API_KEY"):
        provider = "anthropic"
    else:
        provider = "gemini" # Default fallback
    
    if not api_key:
        print("Error: No API key found.")
        return

    verifier = Verifier(api_key=api_key, provider=provider, model_name=model_name, temperature=temperature)
    calibrator = Calibrator(threshold=0.4)
    escalator = Escalator()
    
    # Construct output path with model suffix
    safe_model_name = verifier.model_name.replace("/", "_").replace(".", "_").replace("-", "_")
    output_path = os.path.join(output_dir, f"juliet_sampled_results_{safe_model_name}.csv")
    
    project_root = str(Path(__file__).resolve().parent.parent)
    sarif_files = list(Path(sarif_dir).glob("*.sarif"))
    
    if not sarif_files:
        print(f"No SARIF files found in {sarif_dir}")
        return

    fieldnames = ["CWE", "Alert ID", "File", "Line", "EVICT Label", "Confidence", "Stage", "Rationale"]
    os.makedirs(output_dir, exist_ok=True)

    processed_cwes = set()
    if os.path.exists(output_path):
        with open(output_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_cwes.add(row["CWE"])
    
    print(f"Logging to: {output_path}")
    
    # Open file in append mode if it exists
    mode = "a" if os.path.exists(output_path) else "w"
    with open(output_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()

        for sarif_file in sarif_files:
            cwe_id = sarif_file.stem
            if cwe_id in processed_cwes:
                print(f"Skipping {cwe_id} (already processed)")
                continue
                
            print(f"--- Processing {cwe_id} ---")
            
            with open(sarif_file, "r") as sf:
                try:
                    sarif_data = json.load(sf)
                except Exception as e:
                    print(f"Error loading {sarif_file}: {e}")
                    continue
            
            all_alerts = extractor.extract_from_sarif(sarif_data)
            if not all_alerts:
                print(f"No alerts found for {cwe_id}")
                continue

            # Randomly sample 50-100 cases
            sample_size = random.randint(sample_min, sample_max)
            if len(all_alerts) <= sample_size:
                sampled_alerts = all_alerts
                print(f"Using all {len(all_alerts)} alerts (less than sample size {sample_size})")
            else:
                sampled_alerts = random.sample(all_alerts, sample_size)
                print(f"Sampled {sample_size} alerts out of {len(all_alerts)}")

            for i, alert in enumerate(sampled_alerts):
                print(f"[{i+1}/{len(sampled_alerts)}] Triage {alert.alert_id}...")
                try:
                    extractor.populate_evidence(alert, project_root=project_root)
                    decision = verifier.get_decision(alert, num_samples=1) # Fast PoC
                    decision = calibrator.calibrate(decision)
                    if decision.label == Label.ABSTAIN:
                        decision = escalator.escalate(alert, decision)

                    writer.writerow({
                        "CWE": cwe_id,
                        "Alert ID": alert.alert_id,
                        "File": alert.file_path,
                        "Line": alert.line_number,
                        "EVICT Label": decision.label.value,
                        "Confidence": f"{decision.confidence:.2f}",
                        "Stage": decision.stage,
                        "Rationale": decision.rationale.replace("\n", " ")
                    })
                    f.flush()
                except Exception as e:
                    print(f"Error processing alert {alert.alert_id}: {e}")

    print(f"Benchmark completed. Results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run sampled Juliet benchmark.")
    parser.add_argument("--sarif_dir", default="data/juliet_sarifs", help="Directory containing SARIF files.")
    parser.add_argument("--output_dir", default="artifacts/exports/v2", help="Directory for output results.")
    parser.add_argument("--model", help="Optional model name override.")
    parser.add_argument("--temperature", type=float, help="Optional temperature override.")
    
    args = parser.parse_args()
    
    run_sampling_benchmark(args.sarif_dir, args.output_dir, model_name=args.model, temperature=args.temperature)
