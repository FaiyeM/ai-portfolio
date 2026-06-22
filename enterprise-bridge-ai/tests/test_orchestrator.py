"""Tests for AgentOrchestrator in demo mode."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.orchestrator import AgentOrchestrator


def test_demo_mode_returns_required_keys():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("Create a P1 ticket for the payment gateway outage")
    assert "tool_calls_made" in result
    assert "tool_results" in result
    assert "final_response" in result
    assert "mode" in result


def test_demo_mode_is_demo():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("any command")
    assert result["mode"] == "demo"


def test_payment_gateway_triggers_ticket_creation():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("Create a P1 ticket for the payment gateway outage and notify #incidents")
    tools_used = [tc["tool"] for tc in result["tool_calls_made"]]
    assert "create_ticket" in tools_used


def test_payment_gateway_triggers_slack():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("Create a P1 ticket for the payment gateway outage and notify #incidents")
    tools_used = [tc["tool"] for tc in result["tool_calls_made"]]
    assert "send_slack_notification" in tools_used


def test_status_command_triggers_summarise():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("List all open incidents")
    tools_used = [tc["tool"] for tc in result["tool_calls_made"]]
    assert "summarise_open_incidents" in tools_used


def test_tool_results_are_non_empty():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("Create a P1 ticket for the payment gateway outage")
    assert len(result["tool_results"]) > 0
    for tr in result["tool_results"]:
        assert isinstance(tr, dict)


def test_final_response_is_string():
    orchestrator = AgentOrchestrator(demo_mode=True)
    result = orchestrator.run("any command")
    assert isinstance(result["final_response"], str)
    assert len(result["final_response"]) > 0


if __name__ == "__main__":
    tests = [
        test_demo_mode_returns_required_keys,
        test_demo_mode_is_demo,
        test_payment_gateway_triggers_ticket_creation,
        test_payment_gateway_triggers_slack,
        test_status_command_triggers_summarise,
        test_tool_results_are_non_empty,
        test_final_response_is_string,
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
