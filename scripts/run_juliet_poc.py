import json
import csv
import os
import sys
import time
from pathlib import Path
from typing import List, Set

# Add evict_pipeline to path if not installed
sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))

from evict_pipeline import EvictPipeline, Alert, Decision, Label
from evict_pipeline.extractor import Extractor
from evict_pipeline.verifier import Verifier
from evict_pipeline.calibrator import Calibrator
from evict_pipeline.escalator import Escalator

def get_alert_fingerprint(alert_id: str, file_path: str, line: str) -> str:
    """Creates a unique key for an alert to prevent duplicates."""
    return f"{alert_id}@{file_path}:{line}"

def run_poc(sarif_path: str, base_output_path: str, limit: int = 15305):
    print(f"Loading alerts from {sarif_path}...")
    
    # Initialize components
    extractor = Extractor()
    
    # 1. Configuration
    local_url = os.getenv("LOCAL_LLM_URL")
    local_model = os.getenv("LOCAL_MODEL_NAME")
    api_key = os.getenv("OPENAI_API_KEY")
    provider = "openai"
    base_url = None

    if local_url:
        print(f"Using Local LLM at {local_url}")
        base_url = local_url
        provider = "openai"
        model_override = local_model or "local-model"
        if not api_key:
            api_key = "local-key"
    else:
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
            provider = "gemini"
        model_override = local_model # Use the override if provided in env/args

    if not api_key:
        print("Error: No API key found (OPENAI_API_KEY or GEMINI_API_KEY) and no LOCAL_LLM_URL set.")
        return

    verifier = Verifier(api_key=api_key, provider=provider, model_name=model_override, base_url=base_url)
    calibrator = Calibrator(threshold=0.4)
    escalator = Escalator()
    
    # 2. Resumable Filename Generation
    safe_model_name = verifier.model_name.replace("/", "_").replace(".", "_").replace("-", "_")
    output_csv = base_output_path.replace(".csv", f"_{safe_model_name}.csv")
    
    # Load processed alerts if they exist using fingerprint
    processed_fingerprints: Set[str] = set()
    file_exists = os.path.exists(output_csv)
    if file_exists:
        try:
            with open(output_csv, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Create fingerprint from CSV columns
                    fp = get_alert_fingerprint(row["Alert ID"], row["File"], row["Line"])
                    processed_fingerprints.add(fp)
            print(f"Found existing results. {len(processed_fingerprints)} unique alerts already triaged.")
        except Exception as e:
            print(f"Error reading existing results: {e}. Starting fresh.")
            file_exists = False

    # Load SARIF and extract alerts
    with open(sarif_path, "r") as f:
        sarif_data = json.load(f)
    
    all_alerts = extractor.extract_from_sarif(sarif_data)
    
    # Filter using fingerprints
    selected_alerts = []
    for a in all_alerts[:limit]:
        fp = get_alert_fingerprint(a.alert_id, a.file_path, str(a.line_number))
        if fp not in processed_fingerprints:
            selected_alerts.append(a)
    
    if not selected_alerts:
        print("All requested alerts have already been processed.")
        return

    print(f"Total alerts remaining: {len(selected_alerts)}")
    print(f"Logging to: {output_csv}")
    
    project_root = str(Path(__file__).resolve().parent.parent)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Define CSV headers
    fieldnames = ["Alert ID", "CWE", "File", "Line", "Analyzer", "EVICT Label", "Confidence", "Stage", "Escalated", "Rationale"]

    # Open file in append mode if resuming
    mode = "a" if file_exists else "w"
    with open(output_csv, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        f.flush()

        for i, alert in enumerate(selected_alerts):
            print(f"[{i+1}/{len(selected_alerts)}] Triage alert {alert.alert_id} in {alert.file_path}...")
            try:
                extractor.populate_evidence(alert, project_root=project_root)
                decision = verifier.get_decision(alert, num_samples=1)
                decision = calibrator.calibrate(decision)
                if decision.label == Label.ABSTAIN:
                    decision = escalator.escalate(alert, decision)

                writer.writerow({
                    "Alert ID": alert.alert_id,
                    "CWE": alert.cwe_id,
                    "File": alert.file_path,
                    "Line": alert.line_number,
                    "Analyzer": alert.analyzer_name,
                    "EVICT Label": decision.label.value,
                    "Confidence": f"{decision.confidence:.2f}",
                    "Stage": decision.stage,
                    "Escalated": decision.is_escalated,
                    "Rationale": decision.rationale.replace("\n", " ")
                })
                f.flush()
                
                if not local_url:
                    time.sleep(4)
            except Exception as e:
                print(f"Error processing alert {alert.alert_id}: {e}")

    print(f"POC completed. Results saved to {output_csv}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run EVICT POC on Juliet SARIF results.")
    parser.add_argument("--sarif", default="data/juliet_alerts_pmd.sarif", help="Path to the input SARIF file.")
    parser.add_argument("--output", default="artifacts/exports/juliet_evict_results.csv", help="Base path for the output CSV.")
    parser.add_argument("--limit", type=int, default=15305, help="Limit the number of alerts to process.")
    parser.add_argument("--model", help="Optional model name override.")
    
    args = parser.parse_args()
    
    # If model is provided, we'll need to pass it down or let the script handle it via env
    if args.model:
        os.environ["LOCAL_MODEL_NAME"] = args.model
        # Also could be used to set provider or other logic if needed, 
        # but the script uses Verifier's logic.
    
    run_poc(args.sarif, args.output, limit=args.limit)
