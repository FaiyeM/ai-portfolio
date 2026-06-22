"""Threshold-based alerting — logs risk signals to sentinel_alerts.log."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from signals.risk_rules import RiskSignal

# ── Configuration ────────────────────────────────────────────────────────────
ALERT_LOG = os.getenv("ALERT_LOG", "sentinel_alerts.log")
ALERT_SEVERITIES = {"HIGH", "MEDIUM"}  # Only alert on these


def _setup_logger(log_path: str) -> logging.Logger:
    logger = logging.getLogger("finsentinel.alerter")
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def process_signals(
    signals: list[RiskSignal],
    log_path: str = ALERT_LOG,
    console: bool = True,
) -> list[dict[str, Any]]:
    """Evaluate signals, write alerts to log, return alert dicts.

    Args:
        signals:  list of RiskSignal objects from the aggregator
        log_path: path to the alert log file
        console:  whether to also print alerts to stdout

    Returns:
        List of alert dicts (only signals that met severity threshold)
    """
    logger = _setup_logger(log_path)
    alerts = []

    for signal in signals:
        if signal.severity not in ALERT_SEVERITIES:
            continue

        alert = {
            "alert_id": f"{signal.ticker}_{signal.rule}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
            "rule": signal.rule,
            "ticker": signal.ticker,
            "severity": signal.severity,
            "message": signal.message,
            "evidence_count": len(signal.evidence),
            "triggered_at": signal.triggered_at,
        }
        alerts.append(alert)

        log_line = json.dumps(alert)
        logger.info(log_line)

        if console:
            severity_icon = "🔴" if signal.severity == "HIGH" else "🟡"
            print(f"  {severity_icon} ALERT [{signal.severity}] {signal.rule} — {signal.ticker}: {signal.message}")

    return alerts


def summarise_alerts(alerts: list[dict[str, Any]]) -> str:
    """Return a human-readable summary of triggered alerts."""
    if not alerts:
        return "No alerts triggered."

    high = [a for a in alerts if a["severity"] == "HIGH"]
    medium = [a for a in alerts if a["severity"] == "MEDIUM"]

    lines = [f"=== Alert Summary: {len(alerts)} alert(s) ==="]
    if high:
        lines.append(f"  HIGH ({len(high)}): " + ", ".join(f"{a['ticker']} ({a['rule']})" for a in high))
    if medium:
        lines.append(f"  MEDIUM ({len(medium)}): " + ", ".join(f"{a['ticker']} ({a['rule']})" for a in medium))
    return "\n".join(lines)
