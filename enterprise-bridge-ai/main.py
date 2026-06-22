#!/usr/bin/env python3
"""EnterpriseBridge AI — CLI entrypoint.

Usage:
    python main.py --demo "Create a P1 Jira ticket for the payment gateway outage and notify #incidents"
    python main.py --live "What are all open incidents?"
    python main.py --server          # Start FastAPI server
    python main.py --demo-all        # Run all 3 sample commands
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EnterpriseBridge AI — Natural language → enterprise actions")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", type=str, metavar="COMMAND", help="Run command in demo mode")
    group.add_argument("--live", type=str, metavar="COMMAND", help="Run command with live Anthropic API")
    group.add_argument("--server", action="store_true", help="Start FastAPI server")
    group.add_argument("--demo-all", action="store_true", help="Run all 3 sample commands in demo mode")
    return parser.parse_args()


def run_command(command: str, demo_mode: bool) -> None:
    from agent.orchestrator import AgentOrchestrator

    mode_label = "DEMO" if demo_mode else "LIVE (Anthropic API)"
    console.print(Panel(
        f"[bold cyan]EnterpriseBridge AI[/bold cyan]\n"
        f"Mode: [yellow]{mode_label}[/yellow]\n"
        f"Command: [white]{command}[/white]",
        title="🤖 EnterpriseBridge AI",
        border_style="cyan",
    ))

    orchestrator = AgentOrchestrator(demo_mode=demo_mode)
    result = orchestrator.run(command)

    # Tool calls table
    if result["tool_calls_made"]:
        table = Table(title="🔧 Tool Calls Made", show_header=True, header_style="bold green")
        table.add_column("Step", justify="center", style="dim")
        table.add_column("Tool", style="cyan")
        table.add_column("Key Parameters", style="white")

        for i, (tc, tr) in enumerate(zip(result["tool_calls_made"], result["tool_results"]), 1):
            params = ", ".join(f"{k}={v}" for k, v in list(tc["input"].items())[:3])
            table.add_row(str(i), tc["tool"], params[:80])

        console.print(table)
        console.print()

    # Tool results
    for i, (tc, tr) in enumerate(zip(result["tool_calls_made"], result["tool_results"]), 1):
        result_str = json.dumps(tr, indent=2)[:400]
        console.print(Panel(result_str, title=f"Result {i}: {tc['tool']}", border_style="blue"))

    # Final response
    console.print(Panel(
        Markdown(result["final_response"]),
        title="💬 Agent Response",
        border_style="green",
    ))


def main() -> None:
    args = parse_args()

    if args.server:
        import uvicorn
        console.print("[bold cyan]Starting EnterpriseBridge AI FastAPI server...[/bold cyan]")
        console.print("API docs: http://localhost:8000/docs")
        console.print("Demo endpoint: http://localhost:8000/demo")
        import os
        uvicorn.run(
            "api.server:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=True,
        )

    elif args.demo_all:
        from agent.orchestrator import DEMO_COMMANDS
        for cmd in DEMO_COMMANDS:
            run_command(cmd, demo_mode=True)
            console.print()

    elif args.demo:
        run_command(args.demo, demo_mode=True)

    elif args.live:
        run_command(args.live, demo_mode=False)


if __name__ == "__main__":
    main()
