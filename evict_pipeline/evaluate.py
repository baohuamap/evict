import os
import json
import argparse
from rich.console import Console
from rich.table import Table
from evict_pipeline import (
    Extractor, Verifier, Calibrator, Escalator, EvictPipeline, Label
)

def main():
    parser = argparse.ArgumentParser(description="Run EVICT pipeline on a SARIF file.")
    parser.add_argument("sarif", help="Path to the SARIF file.")
    parser.add_argument("--project-root", default=".", help="Root directory of the project.")
    parser.add_argument("--api-key", help="API key for the LLM provider.")
    parser.add_argument("--provider", default="openai", choices=["openai", "gemini"], help="LLM provider (openai or gemini).")
    parser.add_argument("--model", help="Specific model name to use.")
    parser.add_argument("--debug", action="store_true", help="Print detailed LLM rationales.")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples for vote-share (default: 5).")
    args = parser.parse_args()

    console = Console()
    
    # Provider-specific API key handling
    provider = args.provider.lower()
    api_key = args.api_key
    if not api_key:
        if provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            
    if not api_key:
        console.print(f"[red]Error: API key for {provider} not provided. Use --api-key or set appropriate env var.[/red]")
        return

    # Initialize components
    extractor = Extractor()
    verifier = Verifier(api_key=api_key, provider=provider, model_name=args.model)
    calibrator = Calibrator(threshold=0.5) # Default threshold
    escalator = Escalator()
    pipeline = EvictPipeline(extractor, verifier, calibrator, escalator)

    console.print(f"[bold blue]Running EVICT on {args.sarif}...[/bold blue]")
    
    try:
        # Run manually to pass num_samples
        with open(args.sarif, "r") as f:
            sarif_data = json.load(f)
        alerts = extractor.extract_from_sarif(sarif_data)
        results = []
        for alert in alerts:
            # Step-by-step pipeline run
            extractor.populate_evidence(alert, args.project_root)
            decision = verifier.get_decision(alert, num_samples=args.num_samples)
            calibrated = calibrator.calibrate(decision)
            if calibrated.label == Label.ABSTAIN:
                final = escalator.escalate(alert, calibrated)
            else:
                final = calibrated
            results.append(final)
    except Exception as e:
        console.print(f"[red]Error during execution: {str(e)}[/red]")
        return

    # Display results
    table = Table(title="EVICT Triage Results")
    table.add_column("Alert ID", style="cyan")
    table.add_column("Final Label", style="magenta")
    table.add_column("Confidence", justify="right")
    table.add_column("Stage", style="green")
    table.add_column("Escalated", justify="center")

    tps, fps, abstains = 0, 0, 0
    for res in results:
        table.add_row(
            res.alert_id,
            res.label.value,
            f"{res.confidence:.2f}",
            res.stage,
            "Yes" if res.is_escalated else "No"
        )
        if res.label == Label.TP: tps += 1
        elif res.label == Label.FP: fps += 1
        else: abstains += 1

    console.print(table)
    
    if args.debug:
        for res in results:
            console.print(f"\n[bold yellow]Rationale for {res.alert_id} (Final: {res.label}):[/bold yellow]\n{res.rationale}")
    
    # Summary metrics
    total = len(results)
    coverage = (total - abstains) / total if total > 0 else 0
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total Alerts: {total}")
    console.print(f"TP: {tps}, FP: {fps}, Abstain: {abstains}")
    console.print(f"Coverage: {coverage:.2%}")

if __name__ == "__main__":
    main()
