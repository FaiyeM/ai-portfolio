"""LLM agent orchestrator using Anthropic's native tool_use API."""
from __future__ import annotations

import json
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOL_DEFINITIONS, execute_tool

# Demo mode canned responses
DEMO_RESPONSES = {
    "payment gateway": {
        "tool_calls": [
            {
                "tool": "create_ticket",
                "input": {
                    "system": "jira",
                    "title": "P1 — Payment gateway outage",
                    "description": "Payment gateway is experiencing complete outage affecting all transactions. Customers cannot complete purchases.",
                    "priority": "P1",
                },
            },
            {
                "tool": "send_slack_notification",
                "input": {
                    "channel": "#incidents",
                    "message": "🚨 P1 INCIDENT: Payment gateway outage. Ticket created. All transactions failing. Engineers please join #incidents war room immediately.",
                },
            },
        ],
        "summary": "Created P1 Jira ticket for payment gateway outage and notified #incidents channel.",
    },
    "status": {
        "tool_calls": [
            {
                "tool": "summarise_open_incidents",
                "input": {"system": "both"},
            }
        ],
        "summary": "Retrieved open incidents from Jira and ServiceNow. 3 open tickets found.",
    },
    "escalate": {
        "tool_calls": [
            {
                "tool": "escalate_incident",
                "input": {
                    "ticket_id": "INC0012847",
                    "escalation_reason": "Issue has persisted for 4 hours without resolution and is impacting 200+ users.",
                },
            },
            {
                "tool": "send_slack_notification",
                "input": {
                    "channel": "#incidents",
                    "message": "⚡ ESCALATION: INC0012847 has been escalated to Major Incident Team. CTO notified.",
                },
            },
        ],
        "summary": "Escalated INC0012847 to Major Incident Team and notified #incidents.",
    },
}


class AgentOrchestrator:
    """Agentic orchestrator that routes natural-language commands to enterprise tools."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._client = None
        if not demo_mode:
            self._init_client()

    def _init_client(self) -> None:
        import anthropic
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Use demo mode or set the key in .env")
        self._client = anthropic.Anthropic(api_key=api_key)

    def run(self, command: str, thread_id: str | None = None) -> dict[str, Any]:
        """Process a natural-language command.

        Returns:
            dict with 'tool_calls_made', 'tool_results', 'final_response', 'mode'
        """
        if self.demo_mode:
            return self._run_demo(command)
        return self._run_live(command, thread_id)

    def _run_demo(self, command: str) -> dict[str, Any]:
        """Demo mode: pattern-match command to canned responses."""
        cmd_lower = command.lower()

        demo_key = "payment gateway"
        if "status" in cmd_lower or "open" in cmd_lower or "list" in cmd_lower:
            demo_key = "status"
        elif "escalat" in cmd_lower:
            demo_key = "escalate"
        elif "payment" in cmd_lower or "gateway" in cmd_lower:
            demo_key = "payment gateway"

        template = DEMO_RESPONSES.get(demo_key, DEMO_RESPONSES["payment gateway"])

        tool_calls_made = []
        tool_results = []

        for call in template["tool_calls"]:
            result = execute_tool(call["tool"], call["input"])
            tool_calls_made.append({"tool": call["tool"], "input": call["input"]})
            tool_results.append(result)

        return {
            "tool_calls_made": tool_calls_made,
            "tool_results": tool_results,
            "final_response": self._format_demo_response(template, tool_results),
            "mode": "demo",
        }

    def _format_demo_response(self, template: dict, results: list) -> str:
        lines = [f"✅ {template['summary']}", ""]
        for i, (call, result) in enumerate(zip(template["tool_calls"], results), 1):
            lines.append(f"**Action {i}: {call['tool']}**")
            # Extract key fields from result
            for key in ["ticket_id", "incident_number", "permalink", "message", "escalated_to", "total"]:
                if key in result:
                    lines.append(f"  • {key}: {result[key]}")
            lines.append("")
        return "\n".join(lines)

    def _run_live(self, command: str, thread_id: str | None) -> dict[str, Any]:
        """Live mode: use Anthropic tool_use API for real agentic loop."""
        import os
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

        messages = [{"role": "user", "content": command}]
        tool_calls_made = []
        tool_results = []

        while True:
            response = self._client.messages.create(
                model=model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            # Collect tool uses from response
            tool_uses = [b for b in response.content if b.type == "tool_use"]

            if not tool_uses:
                # No more tool calls — extract final text response
                final_text = " ".join(
                    b.text for b in response.content if hasattr(b, "text")
                )
                return {
                    "tool_calls_made": tool_calls_made,
                    "tool_results": tool_results,
                    "final_response": final_text,
                    "mode": "live",
                }

            # Execute each tool call
            tool_result_content = []
            for tool_use in tool_uses:
                result = execute_tool(tool_use.name, tool_use.input)
                tool_calls_made.append({"tool": tool_use.name, "input": tool_use.input})
                tool_results.append(result)
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                })

            # Feed results back into conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_result_content})
