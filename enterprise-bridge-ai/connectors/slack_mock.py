"""Mock Slack connector."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .base_connector import BaseConnector

SLACK_CHANNELS = {
    "#incidents": "C0123INCIDENTS",
    "#general": "C0123GENERAL",
    "#engineering": "C0123ENGINEERING",
    "#security": "C0123SECURITY",
    "#on-call": "C0123ONCALL",
}

SENT_MESSAGES: list[dict] = []


class SlackMockConnector(BaseConnector):
    system_name = "slack"

    def create_ticket(self, title: str, description: str, priority: str) -> dict[str, Any]:
        return self.send_notification(channel="#incidents", message=f"[{priority}] {title}: {description}")

    def get_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        return {"status": "not_applicable", "message": "Slack does not have ticketing functionality."}

    def list_open_incidents(self, status_filter: str = "open") -> dict[str, Any]:
        return {"status": "not_applicable", "message": "Use Jira or ServiceNow for incident listing."}

    def send_notification(self, channel: str, message: str, thread_ts: str | None = None) -> dict[str, Any]:
        channel_id = SLACK_CHANNELS.get(channel, f"C_UNKNOWN_{channel.strip('#').upper()}")
        ts = str(datetime.utcnow().timestamp())

        msg_record = {
            "channel": channel,
            "channel_id": channel_id,
            "message": message,
            "ts": ts,
            "sent_at": datetime.utcnow().isoformat() + "Z",
            "thread_ts": thread_ts,
        }
        SENT_MESSAGES.append(msg_record)

        result = {
            "status": "sent",
            "channel": channel,
            "message_ts": ts,
            "permalink": f"https://example.slack.com/archives/{channel_id}/p{ts.replace('.', '')}",
            "message": f"Message sent to {channel}.",
        }
        self._log("send_notification", {"channel": channel, "msg_len": len(message)}, result)
        return result

    def get_sent_messages(self) -> list[dict]:
        return SENT_MESSAGES
