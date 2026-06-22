"""Abstract base class for enterprise system connectors."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_FILE = Path(__file__).parent.parent / "connector_calls.log"
_logger = logging.getLogger("connector")


def _setup_logging() -> None:
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


_setup_logging()


class BaseConnector(ABC):
    """Abstract base for all enterprise system connectors."""

    system_name: str = "unknown"

    def _log(self, operation: str, params: dict, result: dict) -> None:
        """Log all connector calls to file."""
        _logger.info(
            f"CALL system={self.system_name} op={operation} "
            f"params={params} result_status={result.get('status', 'unknown')}"
        )

    @abstractmethod
    def create_ticket(self, title: str, description: str, priority: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def list_open_incidents(self, status_filter: str = "open") -> dict[str, Any]:
        pass
