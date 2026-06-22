"""FastAPI server for EnterpriseBridge AI."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from api.models import CommandRequest, CommandResponse, ToolCallRecord
from agent.orchestrator import AgentOrchestrator
from memory.context_store import context_store

app = FastAPI(
    title="EnterpriseBridge AI",
    description="Agentic AI middleware — natural language → enterprise system actions",
    version="1.0.0",
)

DEMO_COMMANDS = [
    "Create a P1 Jira ticket for the payment gateway outage and notify the #incidents Slack channel",
    "List all open incidents from both Jira and ServiceNow",
    "Escalate INC0012847 — the ERP issue has been unresolved for 4 hours and is impacting the Finance team",
]


@app.get("/")
def root():
    return {
        "service": "EnterpriseBridge AI",
        "version": "1.0.0",
        "endpoints": {
            "POST /command": "Execute a natural-language enterprise command",
            "GET /demo": "Run 3 sample commands automatically",
            "GET /health": "Service health check",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "EnterpriseBridge AI"}


@app.post("/command", response_model=CommandResponse)
def execute_command(request: CommandRequest):
    """Execute a natural-language enterprise command."""
    try:
        orchestrator = AgentOrchestrator(demo_mode=request.demo_mode)

        # Create or use existing thread
        thread_id = request.thread_id or context_store.create_thread()
        context_store.add_message(thread_id, "user", request.command)

        result = orchestrator.run(request.command, thread_id=thread_id)

        # Store context
        context_store.add_message(thread_id, "assistant", result["final_response"])
        for tool_call, tool_result in zip(result["tool_calls_made"], result["tool_results"]):
            context_store.add_tool_call(thread_id, tool_call["tool"], tool_call["input"], tool_result)

        return CommandResponse(
            status="success",
            command=request.command,
            tool_calls_made=[ToolCallRecord(**tc) for tc in result["tool_calls_made"]],
            tool_results=result["tool_results"],
            final_response=result["final_response"],
            thread_id=thread_id,
            mode=result["mode"],
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/demo")
def run_demo():
    """Run through 3 sample commands and return all results."""
    orchestrator = AgentOrchestrator(demo_mode=True)
    demo_results = []

    for command in DEMO_COMMANDS:
        thread_id = context_store.create_thread()
        result = orchestrator.run(command, thread_id=thread_id)
        demo_results.append({
            "command": command,
            "tool_calls_made": result["tool_calls_made"],
            "final_response": result["final_response"],
            "mode": result["mode"],
        })

    return {"demo_results": demo_results, "total_commands": len(demo_results)}
