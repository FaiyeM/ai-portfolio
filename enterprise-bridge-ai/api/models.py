"""Pydantic request/response models for the FastAPI server."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    command: str = Field(..., description="Natural-language command to execute")
    thread_id: str | None = Field(None, description="Conversation thread ID for context continuity")
    demo_mode: bool = Field(True, description="Use demo mode (no API key required)")


class ToolCallRecord(BaseModel):
    tool: str
    input: dict[str, Any]


class CommandResponse(BaseModel):
    status: str
    command: str
    tool_calls_made: list[ToolCallRecord]
    tool_results: list[dict[str, Any]]
    final_response: str
    thread_id: str | None
    mode: str
