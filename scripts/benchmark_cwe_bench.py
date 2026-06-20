import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set

# Add evict_pipeline to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))

from evict_pipeline import Alert, Decision, EvictPipeline, Label
from evict_pipeline.calibrator import Calibrator
from evict_pipeline.escalator import Escalator
from evict_pipeline.extractor import Extractor
from evict_pipeline.verifier import Verifier


def load_ground_truth(csv_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Loads ground truth from fix_info.csv, keyed by project slug."""
    gt = {}
    if not os.path.exists(csv_path):
        print(f"Warning: Ground truth file {csv_path} not found.")
        return gt

    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row["project_slug"]
            if slug not in gt:
                gt[slug] = []
            gt[slug].append(
                {
                    "file": row["file"],
                    "start": int(row["method_start"]) if row["method_start"] else 0,
                    "end": int(row["method_end"]) if row["method_end"] else 0,
                }
            )
    return gt


def is_true_positive(
    alert: Alert, project_slug: str, ground_truth: Dict[str, List[Dict[str, Any]]]
) -> bool:
    """Checks if an alert matches any ground truth vulnerability for the project."""
    if project_slug not in ground_truth:
        return False

    for bug in ground_truth[project_slug]:
        # Simple match: same file and line within method range
        if alert.file_path.endswith(bug["file"]):
            if bug["start"] <= alert.line_number <= bug["end"]:
                return True
    return False


def run_benchmark(
    sarif_dir: str,
    gt_path: str,
    output_path: str,
    model_name: str = None,
    temperature: float = None,
    provider_name: str = None,
    num_samples: int = 1,
):
    print(f"Starting CWE-Bench-Java evaluation (k={num_samples})...")

    # Initialize components
    extractor = Extractor()

    # Determine provider: explicit > model heuristic > env keys
    if provider_name:
        provider = provider_name
    elif model_name:
        ml = model_name.lower()
        if "gemini" in ml or "flash" in ml or ("pro" in ml and "gpt" not in ml):
            provider = "gemini"
        elif "claude" in ml or "sonnet" in ml or "haiku" in ml or "opus" in ml:
            provider = "anthropic"
        else:
            provider = "openai"
    elif os.getenv("OPENAI_API_KEY"):
        provider = "openai"
    elif os.getenv("GEMINI_API_KEY"):
        provider = "gemini"
    elif os.getenv("ANTHROPIC_API_KEY"):
        provider = "anthropic"
    else:
        provider = "gemini"  # Default fallback

    api_key = (
        os.getenv(f"{provider.upper()}_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
    )

    if not api_key:
        print("Warning: No API key found, using mock.")
        provider = "mock"
        api_key = "mock-key"

    verifier = Verifier(
        api_key=api_key,
        provider=provider,
        model_name=model_name,
        temperature=temperature,
    )
    calibrator = Calibrator(threshold=0.4)
    escalator = Escalator()

    ground_truth = load_ground_truth(gt_path)

    # Resumable cache for LLM decisions (important for low-budget runs).
    cache_path = output_path.replace(".csv", ".cache.json")
    cache: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(cache_path):
        try:
            cache = json.load(open(cache_path))
            print(f"Loaded cache: {len(cache)} decisions from {cache_path}")
        except Exception:
            pass

    results = []
    sarif_files = list(Path(sarif_dir).glob("*.sarif"))

    if not sarif_files:
        print(f"No SARIF files found in {sarif_dir}")
        return

    total_alerts = 0
    for sarif_file in sarif_files:
        with open(sarif_file, "r") as f:
            sarif_data = json.load(f)
        total_alerts += len(extractor.extract_from_sarif(sarif_data))
    print(f"Total alerts across {len(sarif_files)} SARIF files: {total_alerts}")

    processed = 0
    import time

    t0 = time.time()

    for sarif_file in sarif_files:
        project_slug = sarif_file.stem
        with open(sarif_file, "r") as f:
            sarif_data = json.load(f)

        alerts = extractor.extract_from_sarif(sarif_data)
        if not alerts:
            continue

        print(f"\nProcessing {project_slug} ({len(alerts)} alerts)...")

        for alert in alerts:
            actual_is_tp = is_true_positive(alert, project_slug, ground_truth)
            cache_key = (
                f"{project_slug}_{alert.alert_id}_{alert.file_path}_{alert.line_number}"
            )
            processed += 1

            if cache_key in cache:
                entry = cache[cache_key]
                prediction = entry["prediction"]
                confidence = entry["confidence"]
                rationale = entry["rationale"]
            else:
                try:
                    extractor.populate_evidence(alert, project_root=".")
                    decision = verifier.get_decision(alert, num_samples=num_samples)
                    decision = calibrator.calibrate(decision)
                    if decision.label == Label.ABSTAIN:
                        decision = escalator.escalate(alert, decision)

                    prediction = decision.label.value
                    confidence = f"{decision.confidence:.2f}"
                    rationale = decision.rationale[:100] + "..."

                    cache[cache_key] = {
                        "prediction": prediction,
                        "confidence": confidence,
                        "rationale": rationale,
                    }
                    with open(cache_path, "w") as cf:
                        json.dump(cache, cf, indent=2)
                except Exception as e:
                    print(f"  Error: {e}")
                    prediction = "ABSTAIN"
                    confidence = "0.00"
                    rationale = f"Error: {e}"

            elapsed = time.time() - t0
            rate = processed / elapsed if elapsed > 0 else 0
            print(
                f"  [{processed}/{total_alerts}] {alert.alert_id[:35]:<35} "
                f"GT={'TP' if actual_is_tp else 'FP'} Pred={prediction} "
                f"({elapsed:.0f}s, {rate:.1f}/s)"
            )

            results.append(
                {
                    "Project": project_slug,
                    "Alert ID": alert.alert_id,
                    "File": alert.file_path,
                    "Line": alert.line_number,
                    "Ground Truth": "TP" if actual_is_tp else "FP",
                    "EVICT Prediction": prediction,
                    "Confidence": confidence,
                    "Rationale": rationale,
                }
            )

    # Write Results
    if results:
        fieldnames = [
            "Project",
            "Alert ID",
            "File",
            "Line",
            "Ground Truth",
            "EVICT Prediction",
            "Confidence",
            "Rationale",
        ]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        # Calculate Metrics
        tp = sum(
            1
            for r in results
            if r["Ground Truth"] == "TP" and r["EVICT Prediction"] == "TP"
        )
        fp = sum(
            1
            for r in results
            if r["Ground Truth"] == "FP" and r["EVICT Prediction"] == "TP"
        )
        fn = sum(
            1
            for r in results
            if r["Ground Truth"] == "TP" and r["EVICT Prediction"] == "FP"
        )
        tn = sum(
            1
            for r in results
            if r["Ground Truth"] == "FP" and r["EVICT Prediction"] == "FP"
        )

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        print("\n--- Benchmark Summary ---")
        print(f"Total Alerts: {len(results)}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 Score: {f1:.2f}")
        print(f"Results saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run CWE-Bench-Java benchmark.")
    parser.add_argument(
        "--sarif_dir",
        default="artifacts/codeql_results",
        help="Directory containing SARIF files.",
    )
    parser.add_argument(
        "--gt_path",
        default="data/cwe-bench-java/data/fix_info.csv",
        help="Path to ground truth CSV.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/exports/cwe_bench_evict_results.csv",
        help="Output path.",
    )
    parser.add_argument("--model", help="Optional model name override.")
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "anthropic"],
        help="LLM provider (auto-detected from model name if omitted).",
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=1,
        help="Number of LLM samples per alert (k=1 saves budget, k=5 for vote-share).",
    )
    parser.add_argument(
        "--temperature", type=float, help="Optional temperature override."
    )

    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    run_benchmark(
        args.sarif_dir,
        args.gt_path,
        args.output,
        model_name=args.model,
        temperature=args.temperature,
        provider_name=args.provider,
        num_samples=args.num_samples,
    )
