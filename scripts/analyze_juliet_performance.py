import csv
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

def get_method_ranges(file_path: str) -> List[Tuple[str, int, int]]:
    """
    Parses a Juliet Java file to find method names and their line ranges.
    Returns a list of (method_name, start_line, end_line).
    """
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    methods = []
    # Simplified regex for Juliet method signatures
    method_regex = re.compile(r'\s+(?:public|private|protected)\s+void\s+([a-zA-Z0-9_]+)\s*\(')
    
    current_method = None
    start_line = 0
    brace_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Look for method start
        match = method_regex.search(line)
        if match and current_method is None:
            current_method = match.group(1)
            start_line = line_num
            brace_count = 0
        
        if current_method:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if brace_count == 0 and '{' in "".join(lines[start_line-1:line_num]): # Ensure we actually started
                # Method end found
                methods.append((current_method, start_line, line_num))
                current_method = None
                
    return methods

def determine_ground_truth(file_path: str, line_num: int) -> str:
    """
    Determines if a line in a Juliet file is in a 'bad' or 'good' method.
    Returns 'TP' for bad, 'FP' for good, and 'Unknown' otherwise.
    """
    # Juliet files are in data/juliet_java/...
    local_path = file_path
    if file_path.startswith("file://"):
        local_path = file_path.replace("file://", "")
    
    if not os.path.exists(local_path):
        filename = os.path.basename(local_path)
        search_results = list(Path("data/juliet_java").rglob(filename))
        if search_results:
            local_path = str(search_results[0])
        else:
            return "Unknown"

    methods = get_method_ranges(local_path)
    for name, start, end in methods:
        if start <= line_num <= end:
            if name.lower() == "bad" or name.lower().startswith("bad"):
                return "TP"
            if name.lower().startswith("good"):
                return "FP"
    
    return "Unknown"

def calculate_metrics(data: List[Dict[str, Any]]) -> Dict[str, float]:
    tp_correct = sum(1 for r in data if r["EVICT Label"] == "TP" and r["Ground Truth"] == "TP")
    fp_correct = sum(1 for r in data if r["EVICT Label"] == "FP" and r["Ground Truth"] == "FP")
    tp_wrong = sum(1 for r in data if r["EVICT Label"] == "TP" and r["Ground Truth"] == "FP")
    fp_wrong = sum(1 for r in data if r["EVICT Label"] == "FP" and r["Ground Truth"] == "TP")
    
    total_gt_tp = sum(1 for r in data if r["Ground Truth"] == "TP")
    total_gt_fp = sum(1 for r in data if r["Ground Truth"] == "FP")
    
    abstains = sum(1 for r in data if r["EVICT Label"] == "ABSTAIN")
    total = len(data)
    covered = total - abstains
    
    precision = tp_correct / (tp_correct + tp_wrong) if (tp_correct + tp_wrong) > 0 else 0
    recall = tp_correct / total_gt_tp if total_gt_tp > 0 else 0
    accuracy = (tp_correct + fp_correct) / covered if covered > 0 else 0
    coverage = covered / total if total > 0 else 0
    
    # FP Mitigation: Rate of real FPs correctly identified as FP
    fp_mitigation = fp_correct / total_gt_fp if total_gt_fp > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "coverage": coverage,
        "fp_mitigation": fp_mitigation,
        "tp_correct": tp_correct,
        "fp_correct": fp_correct,
        "total_gt_tp": total_gt_tp,
        "total_gt_fp": total_gt_fp,
        "abstains": abstains,
        "total": total
    }

def analyze_results(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Analyzing {csv_path}...")
    
    results = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    processed_results = []
    unknowns = 0
    
    for row in results:
        try:
            if not row.get("File") or not row.get("Line") or not row.get("EVICT Label"):
                print(f"Skipping malformed row: {row}")
                continue
                
            file_path = row["File"]
            line_num_str = row["Line"]
            if line_num_str is None or line_num_str == "":
                print(f"Skipping row with missing line number: {row}")
                continue
            line_num = int(line_num_str)
            cwe = row.get("CWE", "Unknown")
            
            # Normalize CWE format (e.g., 'cwe571' -> 'CWE-571')
            if cwe and cwe.lower().startswith("cwe"):
                cwe_num = re.sub(r'\D', '', cwe)
                cwe = f"CWE-{cwe_num}"
            elif not cwe or cwe == "Unknown":
                match = re.search(r"CWE(\d+)", file_path)
                if match:
                    cwe = f"CWE-{match.group(1)}"
                else:
                    cwe = "Unknown"
            row["CWE"] = cwe
            
            gt = determine_ground_truth(file_path, line_num)
            row["Ground Truth"] = gt
            
            if gt == "Unknown":
                unknowns += 1
                continue
            
            processed_results.append(row)
        except (ValueError, TypeError) as e:
            print(f"Error processing row {row}: {e}")
            continue

    # Global Metrics
    overall = calculate_metrics(processed_results)
    
    # CWE-specific Metrics
    cwe_groups = {}
    for row in processed_results:
        cwe = row["CWE"]
        if cwe not in cwe_groups:
            cwe_groups[cwe] = []
        cwe_groups[cwe].append(row)
    
    cwe_stats = {}
    for cwe, data in cwe_groups.items():
        cwe_stats[cwe] = calculate_metrics(data)

    # ECE Calculation
    covered_results = [r for r in processed_results if r["EVICT Label"] != "ABSTAIN"]
    ece = 0
    if covered_results:
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        bin_data = {i: {"count": 0, "correct": 0, "conf_sum": 0} for i in range(len(bins)-1)}
        for row in covered_results:
            conf = float(row["Confidence"])
            is_correct = (row["EVICT Label"] == row["Ground Truth"])
            for i in range(len(bins)-1):
                if bins[i] <= conf <= bins[i+1]:
                    bin_data[i]["count"] += 1
                    if is_correct:
                        bin_data[i]["correct"] += 1
                    bin_data[i]["conf_sum"] += conf
                    break
        for i in range(len(bins)-1):
            if bin_data[i]["count"] > 0:
                acc = bin_data[i]["correct"] / bin_data[i]["count"]
                conf = bin_data[i]["conf_sum"] / bin_data[i]["count"]
                ece += (bin_data[i]["count"] / len(covered_results)) * abs(acc - conf)

    print("\n--- Overall Performance Metrics ---")
    print(f"Total Alerts with GT: {overall['total']}")
    print(f"Coverage: {overall['coverage']:.2%}")
    print(f"Precision: {overall['precision']:.2%}")
    print(f"Recall (TP Retention): {overall['recall']:.2%}")
    print(f"FP Mitigation: {overall['fp_mitigation']:.2%} ({overall['fp_correct']}/{overall['total_gt_fp']})")
    print(f"Accuracy: {overall['accuracy']:.2%}")
    print(f"ECE: {ece:.4f}")
    print(f"Unknowns (ignored): {unknowns}")
    
    print("\n--- Performance by CWE Category ---")
    print(f"{'CWE':<10} | {'Total':<6} | {'Cov.':<7} | {'Prec.':<7} | {'Recall':<7} | {'FP Mit.':<7}")
    print("-" * 60)
    for cwe in sorted(cwe_stats.keys()):
        s = cwe_stats[cwe]
        print(f"{cwe:<10} | {s['total']:<6} | {s['coverage']:<7.2%} | {s['precision']:<7.2%} | {s['recall']:<7.2%} | {s['fp_mitigation']:<7.2%}")

    # Save to a summary CSV
    summary_path = csv_path.replace(".csv", "_summary.md")
    with open(summary_path, "w") as f:
        f.write(f"# EVICT Performance Summary for {os.path.basename(csv_path)}\n\n")
        f.write("## Overall Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("| --- | --- |\n")
        f.write(f"| Total Alerts | {overall['total']} |\n")
        f.write(f"| Coverage | {overall['coverage']:.2%} |\n")
        f.write(f"| Precision | {overall['precision']:.2%} |\n")
        f.write(f"| Recall (TP Retention) | {overall['recall']:.2%} |\n")
        f.write(f"| FP Mitigation | {overall['fp_mitigation']:.2%} ({overall['fp_correct']}/{overall['total_gt_fp']}) |\n")
        f.write(f"| Accuracy | {overall['accuracy']:.2%} |\n")
        f.write(f"| ECE | {ece:.4f} |\n")
        
        f.write("\n## CWE-level Performance\n\n")
        f.write("| CWE | Total | Coverage | Precision | Recall | FP Mitigation |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for cwe in sorted(cwe_stats.keys()):
            s = cwe_stats[cwe]
            f.write(f"| {cwe} | {s['total']} | {s['coverage']:.2%} | {s['precision']:.2%} | {s['recall']:.2%} | {s['fp_mitigation']:.2%} |\n")
        
    print(f"\nSummary saved to {summary_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_results(sys.argv[1])
    else:
        target = "artifacts/exports/v2/juliet_sampled_results_gpt_4o_mini.csv"
        if os.path.exists(target):
            analyze_results(target)
        else:
            print(f"Usage: python scripts/analyze_juliet_performance.py <results.csv>")
            print(f"Default target not found: {target}")
