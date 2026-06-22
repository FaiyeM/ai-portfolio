"""Tests for tool execution layer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.tools import execute_tool


def test_create_jira_ticket():
    result = execute_tool("create_ticket", {
        "system": "jira",
        "title": "Test incident",
        "description": "Test description",
        "priority": "P2",
    })
    assert result["status"] == "created"
    assert "ticket_id" in result
    assert "url" in result


def test_create_servicenow_ticket():
    result = execute_tool("create_ticket", {
        "system": "servicenow",
        "title": "Test ServiceNow incident",
        "description": "Test",
        "priority": "P1",
    })
    assert result["status"] == "created"
    assert "incident_number" in result


def test_query_existing_jira_ticket():
    result = execute_tool("query_ticket_status", {
        "system": "jira",
        "ticket_id": "PAY-1042",
    })
    assert result["status"] == "found"
    assert "ticket" in result


def test_query_missing_ticket():
    result = execute_tool("query_ticket_status", {
        "system": "jira",
        "ticket_id": "NONEXISTENT-9999",
    })
    assert result["status"] == "not_found"


def test_send_slack_notification():
    result = execute_tool("send_slack_notification", {
        "channel": "#incidents",
        "message": "Test notification",
    })
    assert result["status"] == "sent"
    assert "message_ts" in result


def test_summarise_jira_incidents():
    result = execute_tool("summarise_open_incidents", {
        "system": "jira",
    })
    assert "jira" in result
    assert result["jira"]["status"] == "success"


def test_summarise_both_systems():
    result = execute_tool("summarise_open_incidents", {
        "system": "both",
    })
    assert "jira" in result
    assert "servicenow" in result


def test_unknown_tool_returns_error():
    result = execute_tool("nonexistent_tool", {})
    assert "error" in result


if __name__ == "__main__":
    tests = [
        test_create_jira_ticket,
        test_create_servicenow_ticket,
        test_query_existing_jira_ticket,
        test_query_missing_ticket,
        test_send_slack_notification,
        test_summarise_jira_incidents,
        test_summarise_both_systems,
        test_unknown_tool_returns_error,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
