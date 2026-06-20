"""EVICT proof-of-concept benchmark with split-conformal calibration.

Implements the evaluation described in sections/preliminary_results.tex:
  - CWE-89, CWE-78, CWE-190 on the Juliet benchmark
  - Random sampling (50-100 alerts per CWE, seeded for reproducibility)
  - pass@5 self-consistency (k=5 samples, temperature 0.7) for vote-share confidence
  - 5-fold cross-validation with 60/20/20 train/calibration/test split
  - Split-conformal q-hat threshold fitting (alpha = 0.1)
  - Selective prediction (abstain when nonconformity > q-hat)
  - Symbolic escalation of abstained alerts (Z3 + sanitization detection)
  - Metrics: Precision, Recall, F1, Coverage, ECE, Selective Risk (mean +/- std)

Modes:
  --live   Run the real LLM verifier (requires OPENAI/GEMINI/ANTHROPIC API key).
  --mock   Use a deterministic mock verifier (no API key) to validate the
           calibration + escalation mechanics end-to-end.

Usage:
  python scripts/benchmark_juliet_conformal.py --mock
  python scripts/benchmark_juliet_conformal.py --live --model gpt-4o-mini
"""

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "evict_pipeline" / "src"))

from evict_pipeline import Alert, Decision, Label
from evict_pipeline.calibrator import Calibrator
from evict_pipeline.escalator import Escalator
from evict_pipeline.extractor import Extractor
from evict_pipeline.verifier import Verifier

# Re-use the Juliet ground-truth heuristic from the analysis script.
sys.path.append(str(PROJECT_ROOT / "scripts"))
from analyze_juliet_performance import determine_ground_truth  # noqa: E402

POC_CWES = ["89", "78", "190"]
ALPHA = 0.1
N_FOLDS = 5
SEED = 42


def load_and_sample_alerts(
    sarif_dir: str, sample_min: int, sample_max: int, seed: int
) -> List[Tuple[Alert, str]]:
    """Loads alerts for the PoC CWEs, determines ground truth, and samples.

    Returns a list of (Alert, ground_truth) pairs where ground_truth is
    'TP', 'FP', or 'Unknown'. Alerts with Unknown ground truth are dropped.
    """
    rng = random.Random(seed)
    extractor = Extractor()
    sampled: List[Tuple[Alert, str]] = []

    for cwe in POC_CWES:
        sarif_path = Path(sarif_dir) / f"cwe{cwe}.sarif"
        if not sarif_path.exists():
            print(f"Warning: {sarif_path} not found, skipping CWE-{cwe}")
            continue
        with open(sarif_path) as f:
            sarif_data = json.load(f)
        alerts = extractor.extract_from_sarif(sarif_data)
        if not alerts:
            continue

        sample_size = rng.randint(sample_min, sample_max)
        if len(alerts) <= sample_size:
            chosen = alerts
        else:
            chosen = rng.sample(alerts, sample_size)

        project_root = str(PROJECT_ROOT)
        for alert in chosen:
            extractor.populate_evidence(alert, project_root=project_root)
            gt = determine_ground_truth(alert.file_path, alert.line_number)
            if gt in ("TP", "FP"):
                sampled.append((alert, gt))
        print(
            f"CWE-{cwe}: sampled {sum(1 for _, g in sampled if True)} alerts "
            f"(running total {len(sampled)})"
        )

    return sampled


def mock_verifier_decision(alert: Alert, gt: str, rng: random.Random) -> Decision:
    """Deterministic-ish mock verifier simulating pass@5 vote-share.

    Simulates a lite LLM with ~55% precision: TP ground truth is usually
    predicted TP with high vote share; FP ground truth is often wrongly
    predicted TP (the main failure mode) but sometimes correctly FP. A
    realistic spread of vote shares (2/5 through 5/5) produces uncertain cases
    that conformal calibration can abstain on and symbolic escalation can
    resolve, exercising the full pipeline.
    """
    if gt == "TP":
        # 70% correct TP (vote 4-5), 15% uncertain (vote 2-3), 10% wrong FP, 5% abstain
        roll = rng.random()
        if roll < 0.70:
            agree = rng.choices([4, 5], weights=[3, 2])[0]
            label = Label.TP
        elif roll < 0.85:
            agree = rng.choices([2, 3], weights=[1, 2])[0]
            label = Label.TP
        elif roll < 0.95:
            agree = rng.choices([3, 4, 5], weights=[2, 2, 1])[0]
            label = Label.FP
        else:
            return Decision(
                alert_id=alert.alert_id,
                label=Label.ABSTAIN,
                confidence=0.0,
                rationale="mock abstain",
                stage="LLM",
            )
    else:  # FP
        # 35% correct FP (vote 4-5), 20% uncertain (vote 2-3), 40% wrong TP, 5% abstain
        roll = rng.random()
        if roll < 0.35:
            agree = rng.choices([4, 5], weights=[3, 2])[0]
            label = Label.FP
        elif roll < 0.55:
            agree = rng.choices([2, 3], weights=[1, 2])[0]
            label = Label.FP
        elif roll < 0.95:
            agree = rng.choices([3, 4, 5], weights=[2, 2, 1])[0]
            label = Label.TP
        else:
            return Decision(
                alert_id=alert.alert_id,
                label=Label.ABSTAIN,
                confidence=0.0,
                rationale="mock abstain",
                stage="LLM",
            )
    confidence = agree / 5.0
    return Decision(
        alert_id=alert.alert_id,
        label=label,
        confidence=confidence,
        rationale="mock rationale",
        stage="LLM",
    )


def run_conformal_evaluation(
    sampled: List[Tuple[Alert, str]],
    verifier: Optional[Verifier],
    escalator: Escalator,
    n_folds: int,
    alpha: float,
    seed: int,
    use_mock: bool,
) -> List[Dict[str, Any]]:
    """Runs n_folds of 60/20/20 train/cal/test conformal evaluation.

    Returns per-fold metrics.
    """
    rng = random.Random(seed)
    n = len(sampled)
    indices = list(range(n))
    rng.shuffle(indices)
    fold_size = n // n_folds
    fold_results: List[Dict[str, Any]] = []

    configs = {
        "Evidence-Free": "no_cal",
        "Evidence-Cond. (No Cal.)": "no_cal",
        "EVICT (No Symb.)": "cal_no_symb",
        "EVICT (Full)": "cal_full",
    }

    for fold in range(n_folds):
        test_idx = set(indices[fold * fold_size : (fold + 1) * fold_size])
        remaining = [i for i in indices if i not in test_idx]
        cal_split = int(len(remaining) * 0.25)  # 25% of 80% = 20% total
        cal_idx = set(remaining[:cal_split])
        # train_idx = set(remaining[cal_split:])  # 60%, unused for zero-shot LLM

        test_items = [sampled[i] for i in range(n) if i in test_idx]
        cal_items = [sampled[i] for i in range(n) if i in cal_idx]

        # 1. Get raw LLM decisions on calibration + test sets.
        cal_decisions: List[Decision] = []
        test_decisions: List[Tuple[Decision, str, Alert]] = []

        for alert, gt in cal_items:
            d = _get_decision(verifier, alert, use_mock, rng)
            cal_decisions.append(d)

        for alert, gt in test_items:
            d = _get_decision(verifier, alert, use_mock, rng)
            test_decisions.append((d, gt, alert))

        # 2. Fit q-hat from calibration nonconformity scores.
        #    Nonconformity A(x,y) = 1 - confidence(predicted label).
        #    (For the predicted label; conformal validity uses the true label,
        #    but for selective prediction we threshold on predicted-label
        #    confidence which is the vote share of the majority class.)
        cal_scores = [
            1.0 - d.confidence for d in cal_decisions if d.label != Label.ABSTAIN
        ]
        calibrator = Calibrator()
        if cal_scores:
            q_hat = calibrator.fit_threshold(cal_scores, alpha=alpha)
        else:
            q_hat = 0.5

        # 3. Evaluate configurations on the test set.
        fold_metrics: Dict[str, Dict[str, float]] = {}
        for config_name, mode in configs.items():
            metrics = _eval_config(test_decisions, q_hat, escalator, mode)
            fold_metrics[config_name] = metrics
        fold_metrics["_q_hat"] = q_hat
        fold_metrics["_fold"] = fold
        fold_results.append(fold_metrics)
        print(
            f"  Fold {fold+1}/{n_folds}: q_hat={q_hat:.3f}, "
            f"test_n={len(test_items)}, cal_n={len(cal_items)}"
        )

    return fold_results


def _get_decision(
    verifier: Optional[Verifier], alert: Alert, use_mock: bool, rng: random.Random
) -> Decision:
    if use_mock:
        # Determine GT for the mock by looking up the alert in the sampled list
        # is not available here; mock_verifier_decision needs gt. We pass a
        # best-effort: use a hash-based pseudo-gt so the mock is deterministic
        # but NOT cheating (it doesn't see real gt). For a true mock we thread
        # gt through; handled by caller in the mock path.
        raise RuntimeError("mock path should not call _get_decision")
    return verifier.get_decision(alert, num_samples=5)


def _eval_config(
    test_decisions: List[Tuple[Decision, str, Alert]],
    q_hat: float,
    escalator: Escalator,
    mode: str,
) -> Dict[str, float]:
    """Evaluates one configuration on the test set and returns metrics."""
    total_test = len(test_decisions)
    results: List[Tuple[str, str, float]] = []  # (predicted, gt, confidence)
    for raw_decision, gt, alert in test_decisions:
        d = raw_decision.model_copy()
        if mode == "no_cal":
            # No calibration: accept everything (100% coverage), raw label.
            if d.label == Label.ABSTAIN:
                # Force a decision for evidence-free/no-cal configs.
                d.label = Label.TP if d.confidence >= 0.5 else Label.FP
            results.append((d.label.value, gt, d.confidence))
        elif mode == "cal_no_symb":
            # Conformal calibration, no escalation: abstain if score > q_hat.
            if d.label == Label.ABSTAIN or (1.0 - d.confidence) > q_hat:
                continue  # abstained -> not covered
            results.append((d.label.value, gt, d.confidence))
        elif mode == "cal_full":
            # Conformal calibration + escalation of abstained.
            if d.label != Label.ABSTAIN and (1.0 - d.confidence) <= q_hat:
                results.append((d.label.value, gt, d.confidence))
            else:
                # Escalate.
                esc_d = escalator.escalate(alert, d.model_copy())
                if esc_d.label != Label.ABSTAIN:
                    results.append((esc_d.label.value, gt, esc_d.confidence))
                # else: remains abstained -> not covered
    metrics = _compute_metrics(results)
    metrics["coverage"] = len(results) / total_test if total_test > 0 else 0.0
    return metrics


def _compute_metrics(results: List[Tuple[str, str, float]]) -> Dict[str, float]:
    """Computes Precision, Recall, F1, Coverage, ECE, Selective Risk."""
    total = len(results)
    if total == 0:
        return {
            "precision": 0,
            "recall": 0,
            "f1": 0,
            "coverage": 0,
            "ece": 0,
            "selective_risk": 0,
            "n": 0,
        }
    tp = sum(1 for p, g, _ in results if p == "TP" and g == "TP")
    fp = sum(1 for p, g, _ in results if p == "TP" and g == "FP")
    fn = sum(1 for p, g, _ in results if p == "FP" and g == "TP")
    tn = sum(1 for p, g, _ in results if p == "FP" and g == "FP")
    gt_tp = tp + fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / gt_tp if gt_tp > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    errors = fp + fn
    selective_risk = errors / total

    # ECE on the accepted (covered) set.
    ece = 0.0
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bin_data = {
        i: {"count": 0, "correct": 0, "conf_sum": 0.0} for i in range(len(bins) - 1)
    }
    for p, g, conf in results:
        is_correct = p == g
        for i in range(len(bins) - 1):
            if bins[i] <= conf <= bins[i + 1]:
                bin_data[i]["count"] += 1
                if is_correct:
                    bin_data[i]["correct"] += 1
                bin_data[i]["conf_sum"] += conf
                break
    for i in range(len(bins) - 1):
        c = bin_data[i]["count"]
        if c > 0:
            acc = bin_data[i]["correct"] / c
            conf = bin_data[i]["conf_sum"] / c
            ece += (c / total) * abs(acc - conf)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "coverage": 1.0,
        "ece": ece,
        "selective_risk": selective_risk,
        "n": total,
    }


def summarize(fold_results: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    """Aggregates per-fold metrics into mean +/- std strings."""
    configs = [
        "Evidence-Free",
        "Evidence-Cond. (No Cal.)",
        "EVICT (No Symb.)",
        "EVICT (Full)",
    ]
    metrics = ["precision", "recall", "f1", "ece", "selective_risk"]
    summary: Dict[str, Dict[str, str]] = {}
    for cfg in configs:
        summary[cfg] = {}
        for m in metrics:
            vals = [fr[cfg][m] for fr in fold_results if cfg in fr]
            if vals:
                mean = np.mean(vals)
                std = np.std(vals)
                summary[cfg][m] = f"{mean:.3f} +/- {std:.3f}"
            else:
                summary[cfg][m] = "n/a"
        # Coverage is per-config (depends on abstentions).
        coverages = [fr[cfg].get("coverage", 0) for fr in fold_results if cfg in fr]
        if coverages:
            summary[cfg][
                "coverage"
            ] = f"{np.mean(coverages):.3f} +/- {np.std(coverages):.3f}"
    return summary


def main():
    parser = argparse.ArgumentParser(description="EVICT conformal PoC benchmark")
    parser.add_argument("--sarif_dir", default="data/juliet_sarifs")
    parser.add_argument(
        "--output", default="artifacts/exports/v2/juliet_conformal_poc.csv"
    )
    parser.add_argument("--model", default=None, help="LLM model name (live mode)")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--sample_min", type=int, default=50)
    parser.add_argument("--sample_max", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=ALPHA)
    parser.add_argument("--folds", type=int, default=N_FOLDS)
    parser.add_argument("--seed", type=int, default=SEED)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true", help="Run real LLM verifier")
    mode.add_argument("--mock", action="store_true", help="Use mock verifier (no API)")
    args = parser.parse_args()

    print("=== EVICT Conformal PoC Benchmark ===")
    print(f"CWEs: {POC_CWES}, alpha={args.alpha}, folds={args.folds}, seed={args.seed}")

    # 1. Load and sample alerts.
    sampled = load_and_sample_alerts(
        args.sarif_dir, args.sample_min, args.sample_max, args.seed
    )
    print(f"Total sampled alerts with ground truth: {len(sampled)}")
    gt_dist = {
        "TP": sum(1 for _, g in sampled if g == "TP"),
        "FP": sum(1 for _, g in sampled if g == "FP"),
    }
    print(f"Ground truth distribution: {gt_dist}")

    # 2. Build verifier.
    verifier = None
    use_mock = args.mock
    if args.live:
        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        )
        if not api_key:
            print("ERROR: --live requires OPENAI/GEMINI/ANTHROPIC API key")
            sys.exit(1)
        provider = (
            "openai"
            if os.getenv("OPENAI_API_KEY")
            else "gemini" if os.getenv("GEMINI_API_KEY") else "anthropic"
        )
        verifier = Verifier(
            api_key=api_key,
            provider=provider,
            model_name=args.model,
            temperature=args.temperature,
        )
        print(f"Live mode: provider={provider}, model={verifier.model_name}")
    else:
        print("Mock mode: using deterministic mock verifier (no API calls)")

    escalator = Escalator()

    # 3. For mock mode, pre-compute decisions (needs gt for the mock).
    #    For live mode, decisions are computed inside run_conformal_evaluation.
    if use_mock:
        rng = random.Random(args.seed)
        mock_decisions: List[Tuple[Decision, str, Alert]] = []
        for alert, gt in sampled:
            d = mock_verifier_decision(alert, gt, rng)
            mock_decisions.append((d, gt, alert))
        # Run folds over pre-computed mock decisions.
        fold_results = _run_folds_on_decisions(
            mock_decisions, escalator, args.folds, args.alpha, args.seed
        )
    else:
        fold_results = run_conformal_evaluation(
            sampled,
            verifier,
            escalator,
            args.folds,
            args.alpha,
            args.seed,
            use_mock=False,
        )

    # 4. Summarize and report.
    summary = summarize(fold_results)
    print("\n=== Results (mean +/- std over {} folds) ===".format(args.folds))
    print(
        f"{'Method':<28} {'Precision':<16} {'Recall':<16} {'F1':<16} "
        f"{'Coverage':<16} {'ECE':<16} {'R_sel':<16}"
    )
    print("-" * 124)
    for cfg in [
        "Evidence-Free",
        "Evidence-Cond. (No Cal.)",
        "EVICT (No Symb.)",
        "EVICT (Full)",
    ]:
        s = summary[cfg]
        print(
            f"{cfg:<28} {s['precision']:<16} {s['recall']:<16} {s['f1']:<16} "
            f"{s['coverage']:<16} {s['ece']:<16} {s['selective_risk']:<16}"
        )

    # 5. Save detailed results.
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "fold",
                "q_hat",
                "config",
                "precision",
                "recall",
                "f1",
                "coverage",
                "ece",
                "selective_risk",
                "n",
            ]
        )
        for fr in fold_results:
            q_hat = fr.get("_q_hat", "")
            fold = fr.get("_fold", "")
            for cfg in [
                "Evidence-Free",
                "Evidence-Cond. (No Cal.)",
                "EVICT (No Symb.)",
                "EVICT (Full)",
            ]:
                m = fr[cfg]
                writer.writerow(
                    [
                        fold,
                        q_hat,
                        cfg,
                        m["precision"],
                        m["recall"],
                        m["f1"],
                        m["coverage"],
                        m["ece"],
                        m["selective_risk"],
                        m["n"],
                    ]
                )
    print(f"\nDetailed per-fold results saved to {out_path}")


def _run_folds_on_decisions(
    mock_decisions: List[Tuple[Decision, str, Alert]],
    escalator: Escalator,
    n_folds: int,
    alpha: float,
    seed: int,
) -> List[Dict[str, Any]]:
    """Runs the conformal fold logic over pre-computed mock decisions."""
    rng = random.Random(seed)
    n = len(mock_decisions)
    indices = list(range(n))
    rng.shuffle(indices)
    fold_size = n // n_folds
    fold_results: List[Dict[str, Any]] = []
    configs = {
        "Evidence-Free": "no_cal",
        "Evidence-Cond. (No Cal.)": "no_cal",
        "EVICT (No Symb.)": "cal_no_symb",
        "EVICT (Full)": "cal_full",
    }
    for fold in range(n_folds):
        test_idx = set(indices[fold * fold_size : (fold + 1) * fold_size])
        remaining = [i for i in indices if i not in test_idx]
        cal_split = int(len(remaining) * 0.25)
        cal_idx = set(remaining[:cal_split])

        cal_items = [mock_decisions[i] for i in range(n) if i in cal_idx]
        test_items = [mock_decisions[i] for i in range(n) if i in test_idx]

        cal_scores = [
            1.0 - d.confidence for d, _, _ in cal_items if d.label != Label.ABSTAIN
        ]
        calibrator = Calibrator()
        q_hat = calibrator.fit_threshold(cal_scores, alpha=alpha) if cal_scores else 0.5

        fold_metrics: Dict[str, Dict[str, float]] = {}
        for config_name, mode in configs.items():
            fold_metrics[config_name] = _eval_config(test_items, q_hat, escalator, mode)
        fold_metrics["_q_hat"] = q_hat
        fold_metrics["_fold"] = fold
        fold_results.append(fold_metrics)
        print(
            f"  Fold {fold+1}/{n_folds}: q_hat={q_hat:.3f}, "
            f"test_n={len(test_items)}, cal_n={len(cal_items)}"
        )
    return fold_results


if __name__ == "__main__":
    main()
