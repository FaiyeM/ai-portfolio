"""Tool definitions for the EnterpriseBridge AI agent (Anthropic tool_use format)."""
from __future__ import annotations

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from connectors.jira_mock import JiraMockConnector
from connectors.servicenow_mock import ServiceNowMockConnector
from connectors.slack_mock import SlackMockConnector

# Singleton connectors
_jira = JiraMockConnector()
_servicenow = ServiceNowMockConnector()
_slack = SlackMockConnector()


# ── Tool definitions for Anthropic tool_use API ──────────────────── #

TOOL_DEFINITIONS = [
    {
        "name": "create_ticket",
        "description": (
            "Create a ticket or incident in either Jira (for engineering/software issues) "
            "or ServiceNow (for IT service management incidents). Returns ticket ID and URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "enum": ["jira", "servicenow"],
                    "description": "Which system to create the ticket in",
                },
                "title": {"type": "string", "description": "Short title / summary of the issue"},
                "description": {"type": "string", "description": "Detailed description of the issue"},
                "priority": {
                    "type": "string",
                    "enum": ["P1", "P2", "P3", "P4"],
                    "description": "P1=Critical/production-down, P2=High, P3=Medium, P4=Low",
                },
            },
            "required": ["system", "title", "description", "priority"],
        },
    },
    {
        "name": "query_ticket_status",
        "description": "Retrieve the current status and details of an existing ticket or incident by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "enum": ["jira", "servicenow"],
                    "description": "Which system to query",
                },
                "ticket_id": {"type": "string", "description": "The ticket or incident ID"},
            },
            "required": ["system", "ticket_id"],
        },
    },
    {
        "name": "send_slack_notification",
        "description": "Send a notification message to a Slack channel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "Slack channel name including # prefix, e.g. #incidents",
                },
                "message": {"type": "string", "description": "Message text to send"},
            },
            "required": ["channel", "message"],
        },
    },
    {
        "name": "escalate_incident",
        "description": "Escalate a ServiceNow incident to the Major Incident Team with a reason.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string", "description": "ServiceNow incident number"},
                "escalation_reason": {"type": "string", "description": "Reason for escalation"},
            },
            "required": ["ticket_id", "escalation_reason"],
        },
    },
    {
        "name": "summarise_open_incidents",
        "description": "Retrieve and summarise all open incidents/tickets from a system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "enum": ["jira", "servicenow", "both"],
                    "description": "Which system(s) to query",
                },
                "status_filter": {
                    "type": "string",
                    "default": "open",
                    "description": "Status filter (open, in-progress, all)",
                },
            },
            "required": ["system"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call and return the result."""
    if tool_name == "create_ticket":
        system = tool_input["system"]
        conn = _jira if system == "jira" else _servicenow
        return conn.create_ticket(
            title=tool_input["title"],
            description=tool_input["description"],
            priority=tool_input["priority"],
        )

    elif tool_name == "query_ticket_status":
        system = tool_input["system"]
        conn = _jira if system == "jira" else _servicenow
        return conn.get_ticket_status(tool_input["ticket_id"])

    elif tool_name == "send_slack_notification":
        return _slack.send_notification(
            channel=tool_input["channel"],
            message=tool_input["message"],
        )

    elif tool_name == "escalate_incident":
        return _servicenow.escalate_incident(
            incident_number=tool_input["ticket_id"],
            reason=tool_input["escalation_reason"],
        )

    elif tool_name == "summarise_open_incidents":
        system = tool_input.get("system", "both")
        status = tool_input.get("status_filter", "open")
        results = {}
        if system in ("jira", "both"):
            results["jira"] = _jira.list_open_incidents(status)
        if system in ("servicenow", "both"):
            results["servicenow"] = _servicenow.list_open_incidents(status)
        return results

    else:
        return {"error": f"Unknown tool: {tool_name}"}
