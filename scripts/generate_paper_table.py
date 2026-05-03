import os
import glob
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

def generate_table():
    summaries = glob.glob("artifacts/exports/*_summary.md")
    if not summaries:
        print("No summary files found.")
        return
    
    print("| Model | Precision | Recall | Accuracy | Coverage | ECE |")
    print("| --- | --- | --- | --- | --- | --- |")
    
    # Also write to a file
    output_path = "artifacts/exports/performance_comparison_table.md"
    with open(output_path, "w") as f:
        f.write("# EVICT Model Performance Comparison (Juliet Benchmark)\n\n")
        f.write("| Model | Precision | Recall | Accuracy | Coverage | ECE |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        
        for summary in sorted(summaries):
            model_name = os.path.basename(summary).replace("juliet_evict_results_", "").replace("_summary.md", "")
            metrics = parse_summary(summary)
            
            row = f"| {model_name} | {metrics.get('Precision', 'N/A')}% | {metrics.get('Recall', 'N/A')}% | {metrics.get('Accuracy', 'N/A')}% | {metrics.get('Coverage', 'N/A')}% | {metrics.get('ECE', 'N/A')} |"
            print(row)
            f.write(row + "\n")
            
    print(f"\nTable saved to {output_path}")

if __name__ == "__main__":
    generate_table()
