# EnterpriseBridge AI

> Agentic AI middleware that translates natural-language business requests into orchestrated API calls across enterprise systems (Jira, ServiceNow, Slack simulacra).

---

## Overview

EnterpriseBridge AI demonstrates the agentic AI design pattern at the enterprise layer — the crucial bridge between human intent expressed in natural language and the complex API ecosystem of enterprise tools. Using Anthropic's native `tool_use` API directly (not LangChain or AutoGen abstractions), the orchestrator receives a natural-language command, reasons about which tools to call and in what sequence, executes them against mock Jira, ServiceNow, and Slack connectors, and synthesises a structured response. A FastAPI server exposes the agent as a REST endpoint with full request/response logging and conversation context management. In demo mode, the system runs without any API key — all tool calls execute against realistic mock connectors that log to file.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                   EnterpriseBridge AI Architecture                │
│                                                                    │
│  User Input (CLI / REST API)                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │           AgentOrchestrator                                  │  │
│  │                                                              │  │
│  │  Natural language ──▶ Anthropic tool_use API ──▶ Tool calls │  │
│  │                              ▲                              │  │
│  │                              │ tool_results                 │  │
│  │                              │                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │              Tool Execution Layer                     │   │  │
│  │  │  create_ticket │ query_status │ send_slack │ escalate │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│            ┌─────────────────┼─────────────────┐                  │
│            ▼                 ▼                 ▼                  │
│    ┌───────────────┐ ┌──────────────┐ ┌────────────────┐         │
│    │  Jira Mock    │ │ServiceNow    │ │  Slack Mock    │         │
│    │  Connector    │ │Mock Connector│ │  Connector     │         │
│    └───────────────┘ └──────────────┘ └────────────────┘         │
│                              │                                     │
│                    connector_calls.log                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Anthropic native tool_use**: Uses the Anthropic SDK's tool_use API directly — no LangChain, no AutoGen — demonstrating direct competency with the underlying API that all higher-level frameworks wrap
- **Agentic loop**: Full multi-step agentic loop where the LLM reasons, calls tools, receives results, and calls additional tools if needed before synthesising a final response
- **5 enterprise tools**: `create_ticket`, `query_ticket_status`, `send_slack_notification`, `escalate_incident`, `summarise_open_incidents`
- **Dual-system routing**: Agent intelligently routes to Jira (engineering) vs ServiceNow (ITSM) based on command context
- **Connector call logging**: Every connector invocation logged to `connector_calls.log` with timestamp, system, operation, and result status
- **FastAPI REST interface**: `POST /command` for agentic execution; `GET /demo` for automated 3-command demonstration; full OpenAPI docs at `/docs`
- **Thread-safe context store**: In-memory conversation context tracking per thread_id, supporting multi-turn interactions
- **Demo mode**: All connectors return realistic fake responses — full agentic workflow observable without API key

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Agent | Anthropic claude-sonnet-4-6 (tool_use) | Agentic reasoning and tool selection |
| API Server | FastAPI 0.111 | REST interface with OpenAPI docs |
| Server Runtime | Uvicorn 0.30 | ASGI server |
| Data Validation | Pydantic 2.7 | Request/response models |
| CLI | Rich 13.7 | Formatted console output |
| HTTP Client | httpx 0.27 | Async HTTP (for future live connectors) |
| Config | python-dotenv | Environment management |

---

## Project Structure

```
enterprise-bridge-ai/
├── main.py                     # CLI entrypoint
├── requirements.txt
├── .env.example
├── api/
│   ├── server.py               # FastAPI app with /command, /demo, /health
│   └── models.py               # Pydantic CommandRequest / CommandResponse
├── agent/
│   ├── orchestrator.py         # AgentOrchestrator — demo and live agentic loops
│   ├── tools.py                # Tool definitions + execution dispatch
│   └── prompts.py              # System prompt for enterprise agent
├── connectors/
│   ├── base_connector.py       # Abstract base with file logging
│   ├── jira_mock.py            # Mock Jira with pre-seeded tickets
│   ├── servicenow_mock.py      # Mock ServiceNow with pre-seeded incidents
│   └── slack_mock.py           # Mock Slack with in-memory message store
├── memory/
│   └── context_store.py        # Thread-safe in-memory context store
├── examples/
│   └── demo_commands.txt       # 10 example commands with expected tool flows
└── tests/
    ├── test_orchestrator.py    # 7 tests for demo-mode orchestrator
    └── test_tools.py           # 8 tests for tool execution layer
```

---

## Setup & Installation

```bash
cd ai-portfolio/enterprise-bridge-ai

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# For live mode only
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

---

## Usage / How to Run

### Demo mode CLI (no API key needed)
```bash
python main.py --demo "Create a P1 Jira ticket for the payment gateway outage and notify the #incidents Slack channel"
```

### Run all 3 sample commands
```bash
python main.py --demo-all
```

### Live mode CLI (requires ANTHROPIC_API_KEY)
```bash
python main.py --live "List all open incidents across Jira and ServiceNow"
```

### Start FastAPI server
```bash
python main.py --server
# Then visit http://localhost:8000/docs
# Or: curl http://localhost:8000/demo
```

### Run tests
```bash
python tests/test_tools.py
python tests/test_orchestrator.py
```

---

## Sample Output

```
╭─── 🤖 EnterpriseBridge AI ────────────────────────────────────╮
│ EnterpriseBridge AI                                             │
│ Mode: DEMO                                                      │
│ Command: Create a P1 Jira ticket for the payment gateway        │
│          outage and notify the #incidents Slack channel         │
╰─────────────────────────────────────────────────────────────────╯

         🔧 Tool Calls Made
┌──────┬───────────────────────────┬──────────────────────────────┐
│ Step │ Tool                      │ Key Parameters               │
├──────┼───────────────────────────┼──────────────────────────────┤
│  1   │ create_ticket             │ system=jira, priority=P1     │
│  2   │ send_slack_notification   │ channel=#incidents           │
└──────┴───────────────────────────┴──────────────────────────────┘

Result 1: create_ticket
{
  "status": "created",
  "ticket_id": "PAY-8231",
  "title": "P1 — Payment gateway outage",
  "priority": "P1",
  "url": "https://jira.example.com/browse/PAY-8231",
  "message": "Ticket PAY-8231 created successfully in Jira."
}

Result 2: send_slack_notification
{
  "status": "sent",
  "channel": "#incidents",
  "message_ts": "1719216043.12345",
  "permalink": "https://example.slack.com/archives/C0123INCIDENTS/p171921604312345"
}

╭─── 💬 Agent Response ─────────────────────────────────────────╮
│ ✅ Created P1 Jira ticket for payment gateway outage and        │
│    notified #incidents channel.                                 │
│                                                                 │
│ Action 1: create_ticket                                         │
│   • ticket_id: PAY-8231                                         │
│   • url: https://jira.example.com/browse/PAY-8231              │
│                                                                 │
│ Action 2: send_slack_notification                               │
│   • message: 🚨 P1 INCIDENT: Payment gateway outage            │
│   • permalink: https://example.slack.com/...                   │
╰─────────────────────────────────────────────────────────────────╯
```

**connector_calls.log:**
```
2024-06-21 14:32:01 | connector | INFO | CALL system=jira op=create_ticket params={'title': 'P1 — Payment gateway outage', 'priority': 'P1'} result_status=created
2024-06-21 14:32:01 | connector | INFO | CALL system=slack op=send_notification params={'channel': '#incidents', 'msg_len': 112} result_status=sent
```

---

## How This Demonstrates AI/ML Competency

- **Anthropic tool_use API mastery**: Implements the complete agentic loop using Anthropic's native `tool_use` API — including the multi-turn `tool_use → tool_result → continue` cycle — demonstrating direct SDK competency rather than reliance on framework abstractions.
- **Agentic system design**: The architecture demonstrates key agentic AI patterns: tool selection reasoning, sequential multi-tool execution, state management across turns, and graceful fallback to demo mode — the core building blocks of production AI agents.
- **Enterprise integration thinking**: The connector abstraction layer (BaseConnector → JiraMock/SNowMock/SlackMock) mirrors real enterprise integration architecture — the mocks are easily replaced with live HTTP clients when real API credentials are available.
- **Production engineering**: FastAPI + Pydantic for type-safe APIs, thread-safe context store for concurrent requests, structured file logging for audit trails — demonstrates awareness of the operational requirements beyond just "making the LLM work."

---

## Future Enhancements

- **Live connector implementation**: Replace mock connectors with real Jira REST API v3, ServiceNow Table API, and Slack Web API clients — the abstract base class makes this a drop-in replacement
- **PagerDuty integration**: Add `page_on_call_engineer` tool for triggering on-call alerting during P1 incidents
- **Persistent memory**: Replace in-memory context store with Redis for multi-instance deployment and session persistence across restarts
- **Webhook receiver**: FastAPI endpoint to receive Jira/ServiceNow webhooks and trigger automated triage workflows
- **Multi-agent handoff**: Chain specialised agents (triage agent → remediation agent → communications agent) using the orchestrator as a router

---

## License

MIT License
