"""Mock ServiceNow connector."""
from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Any

from .base_connector import BaseConnector

MOCK_INCIDENTS = {
    "INC0012847": {
        "number": "INC0012847",
        "short_description": "ERP system unresponsive — Finance team impacted",
        "state": "In Progress",
        "priority": "2 - High",
        "assignment_group": "Enterprise Apps Support",
        "opened_at": "2024-06-21T06:30:00Z",
        "caller_id": "sarah.johnson@example.com",
    },
    "INC0012901": {
        "number": "INC0012901",
        "short_description": "Email delivery failures — external recipients",
        "state": "New",
        "priority": "3 - Moderate",
        "assignment_group": "Messaging Team",
        "opened_at": "2024-06-21T11:00:00Z",
        "caller_id": "it-helpdesk@example.com",
    },
}


class ServiceNowMockConnector(BaseConnector):
    system_name = "servicenow"

    def create_ticket(self, title: str, description: str, priority: str) -> dict[str, Any]:
        inc_id = "INC" + "".join(random.choices(string.digits, k=7))
        priority_map = {"P1": "1 - Critical", "P2": "2 - High", "P3": "3 - Moderate", "P4": "4 - Low"}
        snow_priority = priority_map.get(priority.upper(), "3 - Moderate")

        result = {
            "status": "created",
            "incident_number": inc_id,
            "sys_id": "abc" + "".join(random.choices(string.hexdigits[:16], k=29)),
            "title": title,
            "priority": snow_priority,
            "url": f"https://example.service-now.com/incident.do?sys_id={inc_id}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "state": "New",
            "message": f"Incident {inc_id} created in ServiceNow.",
        }
        MOCK_INCIDENTS[inc_id] = {
            "number": inc_id,
            "short_description": title,
            "state": "New",
            "priority": snow_priority,
            "description": description,
        }
        self._log("create_ticket", {"title": title, "priority": priority}, result)
        return result

    def get_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        incident = MOCK_INCIDENTS.get(ticket_id.upper())
        if incident:
            result = {"status": "found", "incident": incident}
        else:
            result = {"status": "not_found", "ticket_id": ticket_id}
        self._log("get_ticket_status", {"ticket_id": ticket_id}, result)
        return result

    def list_open_incidents(self, status_filter: str = "open") -> dict[str, Any]:
        open_states = {"new", "in progress", "pending"}
        filtered = [i for i in MOCK_INCIDENTS.values() if i["state"].lower() in open_states]
        result = {
            "status": "success",
            "total": len(filtered),
            "incidents": filtered,
            "source": "servicenow",
        }
        self._log("list_open_incidents", {"status_filter": status_filter}, result)
        return result

    def escalate_incident(self, incident_number: str, reason: str) -> dict[str, Any]:
        result = {
            "status": "escalated",
            "incident_number": incident_number,
            "escalated_to": "Major Incident Team",
            "reason": reason,
            "notification_sent": ["ops-manager@example.com", "cto@example.com"],
            "escalated_at": datetime.utcnow().isoformat() + "Z",
        }
        self._log("escalate_incident", {"incident_number": incident_number}, result)
        return result
