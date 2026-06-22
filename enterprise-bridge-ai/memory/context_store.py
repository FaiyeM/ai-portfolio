"""Thread-safe in-memory conversation context store."""
from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Any


class ContextStore:
    """Thread-safe in-memory store for conversation context keyed by thread_id."""

    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def create_thread(self) -> str:
        """Create a new conversation thread and return its ID."""
        thread_id = str(uuid.uuid4())[:8]
        with self._lock:
            self._store[thread_id] = {
                "thread_id": thread_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": [],
                "tool_calls": [],
            }
        return thread_id

    def add_message(self, thread_id: str, role: str, content: str) -> None:
        with self._lock:
            if thread_id not in self._store:
                self._store[thread_id] = {"thread_id": thread_id, "messages": [], "tool_calls": []}
            self._store[thread_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            })

    def add_tool_call(self, thread_id: str, tool_name: str, tool_input: dict, result: dict) -> None:
        with self._lock:
            if thread_id in self._store:
                self._store[thread_id]["tool_calls"].append({
                    "tool": tool_name,
                    "input": tool_input,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                })

    def get_thread(self, thread_id: str) -> dict | None:
        with self._lock:
            return self._store.get(thread_id)

    def list_threads(self) -> list[str]:
        with self._lock:
            return list(self._store.keys())

    def clear_thread(self, thread_id: str) -> None:
        with self._lock:
            self._store.pop(thread_id, None)


# Global singleton
context_store = ContextStore()
