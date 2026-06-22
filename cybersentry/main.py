#!/usr/bin/env python3
"""CyberSentry — LLM-powered threat intelligence analyst.

Usage:
    python main.py --demo     # Run fully offline demo (no API key required)
    python main.py --live     # Run with real Anthropic API (requires ANTHROPIC_API_KEY in .env)
    python main.py --demo --output ./my_reports   # Custom output directory
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from collections import Counter

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CyberSentry — AI-powered CVE threat intelligence analyst"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Run in offline demo mode (no API key required)")
    mode.add_argument("--live", action="store_true", help="Run with live Anthropic API")
    parser.add_argument("--output", type=Path, default=None, help="Override output directory")
    parser.add_argument("--max-cves", type=int, default=10, help="Maximum CVEs to process (default: 10)")
    return parser.parse_args()


def run_pipeline(demo_mode: bool, max_cves: int) -> None:
    """Run the full CyberSentry analysis pipeline."""
    from config import OUTPUT_DIR
    from ingestion.nvd_client import load_sample_cves, fetch_recent_cves
    from enrichment.mitre_mapper import map_cve_to_mitre_demo
    from enrichment.risk_scorer import calculate_risk_score
    from rag.vector_store import get_client, get_or_create_collection, ingest_threat_docs
    from rag.retriever import retrieve_threat_context, format_context_for_prompt
    from llm.analyst import ThreatAnalyst
    from output.poam_generator import build_poam_entry, save_poam_csv, save_poam_json
    from output.report import generate_markdown_report

    mode_label = "DEMO" if demo_mode else "LIVE (Anthropic API)"
    console.print(Panel(
        f"[bold cyan]CyberSentry[/bold cyan] — AI Threat Intelligence Analyst\n"
        f"Mode: [yellow]{mode_label}[/yellow] | Max CVEs: {max_cves}",
        title="🛡️  CyberSentry",
        border_style="cyan",
    ))

    # ── Step 1: Ingest CVEs ──────────────────────────────────────────────── #
    console.print("\n[bold]Step 1:[/bold] Ingesting CVE data...")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Loading CVEs...", total=None)
        if demo_mode:
            cves = load_sample_cves()
        else:
            cves = fetch_recent_cves(days_back=7, max_results=max_cves)
        cves = cves[:max_cves]
        progress.update(task, description=f"Loaded {len(cves)} CVEs ✓")
        time.sleep(0.3)

    # ── Step 2: Set up RAG vector store ─────────────────────────────────── #
    console.print("\n[bold]Step 2:[/bold] Initialising RAG vector store...")
    try:
        chroma_client = get_client()
        collection = get_or_create_collection(chroma_client)
        ingest_threat_docs(collection)
        rag_available = True
    except Exception as exc:
        console.print(f"  [yellow]Warning: ChromaDB unavailable ({exc}). Continuing without RAG context.[/yellow]")
        collection = None
        rag_available = False

    # ── Step 3: Initialise analyst ──────────────────────────────────────── #
    console.print("\n[bold]Step 3:[/bold] Initialising threat analyst...")
    analyst = ThreatAnalyst(demo_mode=demo_mode)
    console.print(f"  Analyst ready ({'demo canned responses' if demo_mode else 'Anthropic ' + __import__('config').ANTHROPIC_MODEL})")

    # ── Step 4: Enrich CVEs ─────────────────────────────────────────────── #
    console.print(f"\n[bold]Step 4:[/bold] Enriching {len(cves)} CVEs...")
    enriched_cves = []
    poam_entries = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Processing CVEs...", total=len(cves))

        for cve in cves:
            cve_id = cve["cve_id"]
            progress.update(task, description=f"Processing {cve_id}...")

            # Retrieve RAG context
            threat_context = ""
            if rag_available and collection:
                contexts = retrieve_threat_context(collection, cve)
                threat_context = format_context_for_prompt(contexts)

            # MITRE mapping
            if demo_mode:
                mitre_tactic, mitre_technique = map_cve_to_mitre_demo(cve)
                mitre_result = {
                    "mitre_tactic": mitre_tactic,
                    "mitre_technique": mitre_technique,
                    "mitre_rationale": f"Keyword-based mapping for {cve_id}.",
                    "secondary_tactics": [],
                }
            else:
                mitre_result = analyst.analyse_mitre(cve, threat_context)

            # Risk scoring
            risk_result = calculate_risk_score(cve)

            # POAM details
            poam_details = analyst.generate_poam_details(cve, mitre_result, threat_context)

            # Merge results into CVE record
            enriched_cve = {
                **cve,
                "mitre_tactic": mitre_result.get("mitre_tactic", "Unknown"),
                "mitre_technique": mitre_result.get("mitre_technique", "Unknown"),
                "mitre_rationale": mitre_result.get("mitre_rationale", ""),
                "risk_score": risk_result.get("risk_score", 0.0),
                "risk_level": risk_result.get("risk_level", "MEDIUM"),
                "asset_category": risk_result.get("asset_category", "general"),
            }
            enriched_cves.append(enriched_cve)

            # Build POAM entry
            poam_entry = build_poam_entry(enriched_cve, mitre_result, risk_result, poam_details)
            poam_entries.append(poam_entry)

            progress.advance(task)
            if not demo_mode:
                time.sleep(0.5)  # Rate limiting for live mode

    # ── Step 5: Generate outputs ────────────────────────────────────────── #
    console.print("\n[bold]Step 5:[/bold] Generating outputs...")

    # Build analysis summary for report
    severity_counts = Counter(c.get("severity", "UNKNOWN") for c in enriched_cves)
    tactic_counts = Counter(c.get("mitre_tactic", "Unknown") for c in enriched_cves)
    top_cves_summary = "\n".join(
        f"- {c['cve_id']} (CVSS {c.get('cvss_score', 'N/A')}): {c.get('description', '')[:100]}..."
        for c in sorted(enriched_cves, key=lambda x: x.get("risk_score", 0), reverse=True)[:5]
    )
    tactic_summary = "\n".join(f"- {t}: {cnt} CVE(s)" for t, cnt in tactic_counts.most_common(5))

    analysis_summary = {
        "total_cves": len(enriched_cves),
        "critical_count": severity_counts.get("CRITICAL", 0),
        "high_count": severity_counts.get("HIGH", 0),
        "medium_count": severity_counts.get("MEDIUM", 0),
        "low_count": severity_counts.get("LOW", 0),
        "top_cves_summary": top_cves_summary,
        "tactic_summary": tactic_summary,
    }

    executive_summary = analyst.generate_threat_report(analysis_summary)

    report_path = generate_markdown_report(enriched_cves, poam_entries, executive_summary)
    poam_csv_path = save_poam_csv(poam_entries)
    poam_json_path = save_poam_json(poam_entries)

    # ── Step 6: Display results ──────────────────────────────────────────── #
    console.print("\n[bold]Step 6:[/bold] Analysis complete!\n")

    table = Table(title="CVE Risk Summary", show_header=True, header_style="bold cyan")
    table.add_column("CVE ID", style="cyan", no_wrap=True)
    table.add_column("Severity", justify="center")
    table.add_column("CVSS", justify="center")
    table.add_column("Risk Score", justify="center")
    table.add_column("MITRE Tactic", style="yellow")
    table.add_column("Due Date", justify="center")

    severity_styles = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
    for entry in sorted(poam_entries, key=lambda x: x.get("Risk_Score", 0), reverse=True):
        sev = entry.get("Severity", "UNKNOWN")
        table.add_row(
            entry["CVE_ID"],
            f"[{severity_styles.get(sev, 'white')}]{sev}[/{severity_styles.get(sev, 'white')}]",
            str(entry.get("CVSS_Score", "N/A")),
            f"{entry.get('Risk_Score', 0):.1f}",
            entry.get("MITRE_Tactic", "Unknown"),
            entry.get("Due_Date", "N/A"),
        )

    console.print(table)

    console.print(Panel(
        f"[green]✓[/green] Threat report: [cyan]{report_path}[/cyan]\n"
        f"[green]✓[/green] POAM CSV:      [cyan]{poam_csv_path}[/cyan]\n"
        f"[green]✓[/green] POAM JSON:     [cyan]{poam_json_path}[/cyan]",
        title="📄 Output Files",
        border_style="green",
    ))


def main() -> None:
    args = parse_args()
    run_pipeline(demo_mode=args.demo, max_cves=args.max_cves)


if __name__ == "__main__":
    main()
