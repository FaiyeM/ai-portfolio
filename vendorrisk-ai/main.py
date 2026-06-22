#!/usr/bin/env python3
"""VendorRisk AI — CLI entrypoint.

Usage:
    python main.py --vendor "Acme Corp" --questionnaire default --demo
    python main.py --vendor "FinCo Services" --questionnaire default --demo
    python main.py --vendor "Acme Corp" --questionnaire default --live
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VendorRisk AI — Automated vendor security assessment")
    parser.add_argument("--vendor", required=True, help="Vendor name (must match sample_data/ file)")
    parser.add_argument("--questionnaire", default="default", choices=["default", "financial_sector"])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Demo mode (no API key required)")
    mode.add_argument("--live", action="store_true", help="Live mode (requires ANTHROPIC_API_KEY)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    demo_mode = args.demo

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()

    console.print(Panel(
        f"[bold cyan]VendorRisk AI[/bold cyan]\n"
        f"Vendor: [white]{args.vendor}[/white] | "
        f"Questionnaire: [white]{args.questionnaire}[/white] | "
        f"Mode: [yellow]{'DEMO' if demo_mode else 'LIVE'}[/yellow]",
        title="🏢 VendorRisk AI",
        border_style="cyan",
    ))

    from assessment.scorer import load_questionnaire, load_vendor_responses, score_all_questions
    from assessment.aggregator import aggregate_scores
    from assessment.domain_weights import get_weights
    from llm.analyst import VendorRiskAnalyst
    from reporting.pdf_generator import generate_pdf_report

    # Load data
    console.print("\n[bold]Step 1:[/bold] Loading questionnaire and vendor responses...")
    questionnaire = load_questionnaire(args.questionnaire)
    vendor_responses = load_vendor_responses(args.vendor, args.questionnaire)
    vendor_name = vendor_responses["vendor_name"]
    console.print(f"  Loaded {sum(len(d['questions']) for d in questionnaire['domains'])} questions across {len(questionnaire['domains'])} domains")

    # Initialise analyst
    analyst = VendorRiskAnalyst(demo_mode=demo_mode)

    # Score questions
    console.print(f"\n[bold]Step 2:[/bold] Scoring questionnaire responses...")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analysing responses...", total=None)
        scored_questions = score_all_questions(questionnaire, vendor_responses, analyst)
        progress.update(task, description=f"Scored {len(scored_questions)} responses ✓")

    # Aggregate
    console.print(f"\n[bold]Step 3:[/bold] Aggregating domain scores...")
    weights = get_weights(args.questionnaire)
    aggregation = aggregate_scores(scored_questions, weights)

    # Generate remediation
    console.print(f"\n[bold]Step 4:[/bold] Generating remediation recommendations...")
    remediation = analyst.generate_remediation(vendor_name, aggregation)

    # Display results
    risk_tier = aggregation["risk_tier"]
    overall_score = aggregation["overall_score"]
    tier_colors = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
    tier_style = tier_colors.get(risk_tier, "white")

    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"  Overall Score: [bold]{overall_score}/100[/bold]")
    console.print(f"  Risk Tier:     [{tier_style}]{risk_tier}[/{tier_style}]")

    # Domain table
    table = Table(title="Domain Scores", show_header=True, header_style="bold cyan")
    table.add_column("Domain")
    table.add_column("Score/100", justify="center")
    table.add_column("Weight", justify="center")

    for domain, data in aggregation["domain_scores"].items():
        score_100 = data["score_out_of_100"]
        style = "green" if score_100 >= 70 else "yellow" if score_100 >= 50 else "red"
        table.add_row(domain, f"[{style}]{score_100:.0f}[/{style}]", f"{data['weight']:.0%}")
    console.print(table)

    # Generate PDF report
    console.print(f"\n[bold]Step 5:[/bold] Generating PDF report...")
    pdf_path = generate_pdf_report(
        vendor_name=vendor_name,
        assessment_date=vendor_responses.get("assessment_date", "2024-06-21"),
        aggregation=aggregation,
        scored_questions=scored_questions,
        remediation=remediation,
    )

    # Save JSON
    json_path = pdf_path.parent / pdf_path.name.replace("_risk_report.pdf", "_risk_data.json")
    with open(json_path, "w") as f:
        json.dump({
            "vendor_name": vendor_name,
            "overall_score": overall_score,
            "risk_tier": risk_tier,
            "domain_scores": aggregation["domain_scores"],
            "top_findings": aggregation["top_findings"],
            "remediation": remediation,
            "scored_questions": scored_questions,
        }, f, indent=2)

    console.print(Panel(
        f"[green]✓[/green] PDF Report: [cyan]{pdf_path}[/cyan]\n"
        f"[green]✓[/green] JSON Data:  [cyan]{json_path}[/cyan]",
        title="📄 Output Files",
        border_style="green",
    ))


if __name__ == "__main__":
    main()
