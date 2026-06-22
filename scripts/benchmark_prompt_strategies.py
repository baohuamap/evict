"""Compare prompt strategies for EVICT alert triage.

Tests 4 prompt strategies on the same Juliet PoC alerts (CWE-89/78/190):
  - default: Original baseline prompt
  - contrastive: Force both TP and FP arguments before deciding
  - decomposed: Break into sub-questions (source, sink, sanitizer, path)
  - few_shot: Calibrated TP/FP examples before triage

Usage:
  python scripts/benchmark_prompt_strategies.py --provider gemini --model gemini-2.5-flash-lite
  python scripts/benchmark_prompt_strategies.py --base_url http://localhost:8000/v1 --model r1-distill-14b
"""

import argparse
import csv
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "evict_pipeline" / "src"))

from evict_pipeline import Alert, Decision, Label
from evict_pipeline.extractor import Extractor
from evict_pipeline.verifier import Verifier

sys.path.append(str(PROJECT_ROOT / "scripts"))
from analyze_juliet_performance import determine_ground_truth  # noqa: E402

POC_CWES = ["89", "78", "190"]
SEED = 42


def load_and_sample_alerts(sarif_dir: str, sample_min: int, sample_max: int, seed: int):
    rng = random.Random(seed)
    extractor = Extractor()
    sampled = []
    for cwe in POC_CWES:
        sarif_path = Path(sarif_dir) / f"cwe{cwe}.sarif"
        if not sarif_path.exists():
            continue
        with open(sarif_path) as f:
            sarif_data = json.load(f)
        alerts = extractor.extract_from_sarif(sarif_data)
        if not alerts:
            continue
        sample_size = rng.randint(sample_min, sample_max)
        chosen = rng.sample(alerts, min(sample_size, len(alerts)))
        project_root = str(PROJECT_ROOT)
        for alert in chosen:
            extractor.populate_evidence(alert, project_root=project_root)
            gt = determine_ground_truth(alert.file_path, alert.line_number)
            if gt in ("TP", "FP"):
                sampled.append((alert, gt))
    return sampled


def run_strategy(sampled, verifier, strategy_name, cache_path):
    """Run a single prompt strategy on all sampled alerts."""
    verifier.prompt_strategy = strategy_name
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            pass

    results = []
    total = len(sampled)
    t0 = time.time()

    for i, (alert, gt) in enumerate(sampled):
        cache_key = f"{alert.alert_id}_{alert.file_path}_{alert.line_number}"
        if cache_key in cache:
            entry = cache[cache_key]
            d = Decision(
                alert_id=entry["alert_id"],
                label=Label(entry["label"]),
                confidence=entry["confidence"],
                rationale=entry["rationale"],
                stage=entry["stage"],
            )
            results.append((d, gt))
            continue

        elapsed = time.time() - t0
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        print(
            f"  [{strategy_name}] [{i+1}/{total}] {alert.cwe_id} {alert.alert_id[:35]:<35} "
            f"({elapsed:.0f}s, {rate:.1f}/s)"
        )

        try:
            d = verifier.get_decision(alert, num_samples=5)
        except Exception as e:
            print(f"    ERROR: {e}")
            d = Decision(
                alert_id=alert.alert_id,
                label=Label.ABSTAIN,
                confidence=0.0,
                rationale=f"Error: {e}",
                stage="LLM",
            )

        results.append((d, gt))
        cache[cache_key] = {
            "alert_id": d.alert_id,
            "label": d.label.value,
            "confidence": d.confidence,
            "rationale": d.rationale[:500],
            "stage": d.stage,
        }
        cache_path.write_text(json.dumps(cache, indent=2))

    print(f"  {strategy_name} complete: {len(results)} alerts in {time.time()-t0:.0f}s")
    return results


def compute_metrics(results):
    total = len(results)
    if total == 0:
        return {"precision": 0, "recall": 0, "f1": 0, "ece": 0, "unanimous": 0}

    tp = sum(1 for d, g in results if d.label.value == "TP" and g == "TP")
    fp = sum(1 for d, g in results if d.label.value == "TP" and g == "FP")
    fn = sum(1 for d, g in results if d.label.value == "FP" and g == "TP")
    tn = sum(1 for d, g in results if d.label.value == "FP" and g == "FP")
    abst = sum(1 for d, g in results if d.label.value == "ABSTAIN")
    gt_tp = tp + fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / gt_tp if gt_tp > 0 else 0
    f1 = (
        2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    )

    confs = [d.confidence for d, g in results if d.label.value != "ABSTAIN"]
    unanimous = sum(1 for c in confs if c >= 1.0)
    unanimous_rate = unanimous / len(confs) if confs else 0

    # ECE
    ece = 0.0
    covered = [(d, g) for d, g in results if d.label.value != "ABSTAIN"]
    if covered:
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        bin_data = {
            i: {"count": 0, "correct": 0, "conf_sum": 0.0} for i in range(len(bins) - 1)
        }
        for d, g in covered:
            is_correct = d.label.value == g
            for j in range(len(bins) - 1):
                if bins[j] <= d.confidence <= bins[j + 1]:
                    bin_data[j]["count"] += 1
                    if is_correct:
                        bin_data[j]["correct"] += 1
                    bin_data[j]["conf_sum"] += d.confidence
                    break
        for j in range(len(bins) - 1):
            c = bin_data[j]["count"]
            if c > 0:
                acc = bin_data[j]["correct"] / c
                conf = bin_data[j]["conf_sum"] / c
                ece += (c / len(covered)) * abs(acc - conf)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "ece": ece,
        "unanimous": unanimous_rate,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "abstain": abst,
        "total": total,
        "tp_pred": tp + fp,
        "fp_pred": tn + fn,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare EVICT prompt strategies")
    parser.add_argument("--sarif_dir", default="data/juliet_sarifs")
    parser.add_argument("--output_dir", default="artifacts/exports/v2")
    parser.add_argument("--model", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--base_url", default=None)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--sample_min", type=int, default=50)
    parser.add_argument("--sample_max", type=int, default=100)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--strategies",
        default="default,contrastive,decomposed,few_shot",
        help="Comma-separated strategy names",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    print("=== EVICT Prompt Strategy Comparison ===")
    strategies = args.strategies.split(",")

    # Load and sample alerts (same for all strategies)
    sampled = load_and_sample_alerts(
        args.sarif_dir, args.sample_min, args.sample_max, args.seed
    )
    print(f"Sampled {len(sampled)} alerts with ground truth")
    gt_dist = Counter(g for _, g in sampled)
    print(f"Ground truth: {gt_dist}")

    # Build verifier
    if args.mock:
        print("ERROR: mock mode not supported for strategy comparison (needs real LLM)")
        sys.exit(1)

    base_url = args.base_url or os.getenv("LOCAL_LLM_URL")
    if base_url:
        provider = "openai"
        api_key = (
            os.getenv("OPENAI_API_KEY") or os.getenv("LOCAL_LLM_API_KEY") or "EMPTY"
        )
        model_name = args.model or os.getenv("LOCAL_MODEL_NAME") or "local-model"
    elif args.provider:
        provider = args.provider
        api_key = os.getenv(f"{provider.upper()}_API_KEY") or os.getenv(
            "OPENAI_API_KEY"
        )
        model_name = args.model
    else:
        provider = "openai"
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = args.model

    if not api_key:
        print("ERROR: No API key found")
        sys.exit(1)

    verifier = Verifier(
        api_key=api_key,
        provider=provider,
        model_name=model_name,
        base_url=base_url,
        temperature=args.temperature,
    )
    model_label = model_name or verifier.model_name
    print(f"Model: {model_label}, Provider: {provider}")

    # Run each strategy
    all_results = {}
    for strategy in strategies:
        print(f"\n--- Running strategy: {strategy} ---")
        cache_path = (
            Path(args.output_dir)
            / f"prompt_strategy_{strategy}_{model_label.replace('/', '_')}.cache.json"
        )
        results = run_strategy(sampled, verifier, strategy.strip(), cache_path)
        all_results[strategy.strip()] = results

    # Compute and display metrics
    print(f"\n{'='*90}")
    print(
        f"{'Strategy':<15} {'Precision':<12} {'Recall':<12} {'F1':<12} {'ECE':<12} {'Unanimous':<12} {'TP-pred':<10} {'FP-pred':<10} {'Abstain':<10}"
    )
    print("-" * 90)

    summary_rows = []
    for strategy, results in all_results.items():
        m = compute_metrics(results)
        print(
            f"{strategy:<15} {m['precision']:.1%}{'':>5} {m['recall']:.1%}{'':>5} "
            f"{m['f1']:.3f}{'':>6} {m['ece']:.3f}{'':>6} {m['unanimous']:.1%}{'':>5} "
            f"{m['tp_pred']:<10} {m['fp_pred']:<10} {m['abstain']:<10}"
        )
        summary_rows.append({"strategy": strategy, **m})

    # Save summary
    out_path = (
        Path(args.output_dir)
        / f"prompt_strategy_comparison_{model_label.replace('/', '_')}.csv"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\nSummary saved to {out_path}")

    # Save label distributions
    print(f"\n--- Label Distributions ---")
    for strategy, results in all_results.items():
        labels = Counter(d.label.value for d, g in results)
        confs = [d.confidence for d, g in results if d.label.value != "ABSTAIN"]
        conf_dist = Counter(confs)
        print(f"  {strategy}: {labels}")
        print(f"    Confidence: {dict(sorted(conf_dist.items()))}")


if __name__ == "__main__":
    main()
