import os
import glob
import csv
import re

def parse_summary(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    metrics = {}
    patterns = {
        "Total Alerts": r"\| Total Alerts \| (\d+) \|",
        "Coverage": r"\| Coverage \| ([\d\.]+)% \|",
        "Precision": r"\| Precision \| ([\d\.]+)% \|",
        "Recall": r"\| Recall \| ([\d\.]+)% \|",
        "Accuracy": r"\| Accuracy \| ([\d\.]+)% \|",
        "ECE": r"\| ECE \| ([\d\.]+) \|"
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            metrics[name] = match.group(1)
            
    return metrics

def generate_csv():
    summaries = glob.glob("artifacts/exports/*_summary.md")
    if not summaries:
        print("No summary files found.")
        return
    
    output_path = "artifacts/exports/performance_comparison.csv"
    fieldnames = ["Model", "Precision", "Recall", "Accuracy", "Coverage", "ECE"]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for summary in sorted(summaries):
            model_name = os.path.basename(summary).replace("juliet_evict_results_", "").replace("_summary.md", "")
            metrics = parse_summary(summary)
            
            writer.writerow({
                "Model": model_name,
                "Precision": metrics.get("Precision", "0"),
                "Recall": metrics.get("Recall", "0"),
                "Accuracy": metrics.get("Accuracy", "0"),
                "Coverage": metrics.get("Coverage", "0"),
                "ECE": metrics.get("ECE", "0")
            })
            
    print(f"CSV saved to {output_path}")

if __name__ == "__main__":
    generate_csv()
