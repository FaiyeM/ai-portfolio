"""Mock Jira connector — returns realistic fake responses."""
from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Any

from .base_connector import BaseConnector

MOCK_TICKETS = {
    "PAY-1042": {
        "id": "PAY-1042",
        "title": "Payment gateway intermittent failures",
        "status": "In Progress",
        "priority": "P2",
        "assignee": "alex.chen@example.com",
        "created": "2024-06-20T09:15:00Z",
        "updated": "2024-06-21T14:30:00Z",
    },
    "INFRA-891": {
        "id": "INFRA-891",
        "title": "Database replication lag exceeding threshold",
        "status": "Open",
        "priority": "P2",
        "assignee": "maria.santos@example.com",
        "created": "2024-06-21T08:00:00Z",
        "updated": "2024-06-21T08:00:00Z",
    },
    "SEC-234": {
        "id": "SEC-234",
        "title": "CVE-2024-3400 patching — Palo Alto GlobalProtect",
        "status": "In Review",
        "priority": "P1",
        "assignee": "security-team@example.com",
        "created": "2024-06-19T11:00:00Z",
        "updated": "2024-06-21T16:00:00Z",
    },
}


class JiraMockConnector(BaseConnector):
    system_name = "jira"

    def create_ticket(self, title: str, description: str, priority: str) -> dict[str, Any]:
        ticket_id = "PAY-" + "".join(random.choices(string.digits, k=4))
        result = {
            "status": "created",
            "ticket_id": ticket_id,
            "title": title,
            "priority": priority,
            "url": f"https://jira.example.com/browse/{ticket_id}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "assigned_to": "on-call-engineer@example.com",
            "message": f"Ticket {ticket_id} created successfully in Jira.",
        }
        MOCK_TICKETS[ticket_id] = {
            "id": ticket_id,
            "title": title,
            "status": "Open",
            "priority": priority,
            "assignee": "on-call-engineer@example.com",
            "description": description,
        }
        self._log("create_ticket", {"title": title, "priority": priority}, result)
        return result

    def get_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        ticket = MOCK_TICKETS.get(ticket_id.upper())
        if ticket:
            result = {
                "status": "found",
                "ticket": ticket,
            }
        else:
            result = {
                "status": "not_found",
                "ticket_id": ticket_id,
                "message": f"Ticket {ticket_id} not found in Jira.",
            }
        self._log("get_ticket_status", {"ticket_id": ticket_id}, result)
        return result

    def list_open_incidents(self, status_filter: str = "open") -> dict[str, Any]:
        filtered = [t for t in MOCK_TICKETS.values() if t["status"].lower() != "closed"]
        result = {
            "status": "success",
            "total": len(filtered),
            "tickets": filtered,
            "source": "jira",
        }
        self._log("list_open_incidents", {"status_filter": status_filter}, result)
        return result
