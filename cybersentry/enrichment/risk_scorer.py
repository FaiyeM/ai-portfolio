"""Composite risk scorer for CVEs.

Combines CVSS base score with asset criticality context to produce a
0–100 composite risk score.
"""
from __future__ import annotations

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CVSS_WEIGHT, ASSET_CRITICALITY_WEIGHT


# Asset criticality weights by product category
ASSET_CRITICALITY: dict[str, float] = {
    "firewall": 10.0,
    "vpn": 10.0,
    "active directory": 10.0,
    "domain controller": 10.0,
    "database": 9.5,
    "email": 9.0,
    "outlook": 9.0,
    "ci/cd": 8.5,
    "teamcity": 8.5,
    "jenkins": 8.5,
    "itsm": 8.0,
    "helpdesk": 8.0,
    "web server": 7.5,
    "http": 7.0,
    "remote access": 9.0,
    "default": 6.0,
}

# Exploitation status multipliers
EXPLOITATION_MULTIPLIERS: dict[str, float] = {
    "actively exploited": 1.25,
    "proof of concept available": 1.10,
    "no known exploit": 1.00,
}


def calculate_risk_score(cve: dict[str, Any]) -> dict[str, Any]:
    """Calculate a composite risk score for a CVE.

    Returns:
        dict with risk_score (0-100), risk_level, asset_criticality,
        and score_breakdown.
    """
    cvss = float(cve.get("cvss_score", 5.0))
    description = (cve.get("description", "") + " " + " ".join(cve.get("keywords", []))).lower()
    products = [p.lower() for p in cve.get("affected_products", [])]

    # Normalise CVSS to 0-100
    cvss_normalised = (cvss / 10.0) * 100.0

    # Determine asset criticality
    asset_score = ASSET_CRITICALITY["default"]
    matched_category = "general"
    for category, score in ASSET_CRITICALITY.items():
        if category == "default":
            continue
        if any(category in p for p in products) or category in description:
            if score > asset_score:
                asset_score = score
                matched_category = category

    asset_normalised = (asset_score / 10.0) * 100.0

    # Exploitation multiplier
    multiplier = 1.0
    if "actively exploited" in description or "exploited in the wild" in description:
        multiplier = EXPLOITATION_MULTIPLIERS["actively exploited"]
    elif "proof of concept" in description or "poc" in description:
        multiplier = EXPLOITATION_MULTIPLIERS["proof of concept available"]

    # Composite score
    base_score = (cvss_normalised * CVSS_WEIGHT) + (asset_normalised * ASSET_CRITICALITY_WEIGHT)
    composite = min(100.0, base_score * multiplier)

    # Risk level
    if composite >= 90:
        risk_level = "CRITICAL"
    elif composite >= 70:
        risk_level = "HIGH"
    elif composite >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": round(composite, 1),
        "risk_level": risk_level,
        "asset_category": matched_category,
        "asset_criticality_score": asset_score,
        "exploitation_multiplier": multiplier,
        "score_breakdown": {
            "cvss_contribution": round(cvss_normalised * CVSS_WEIGHT, 1),
            "asset_contribution": round(asset_normalised * ASSET_CRITICALITY_WEIGHT, 1),
            "multiplier_applied": multiplier,
        },
    }


def get_recommended_control(tactic: str, severity: str) -> str:
    """Return a recommended security control based on MITRE tactic and severity."""
    control_map: dict[str, str] = {
        "Initial Access": "Apply vendor patch immediately; restrict external-facing service exposure; enforce MFA on all remote access points.",
        "Execution": "Deploy application allowlisting; restrict script interpreter execution; enable EDR process monitoring.",
        "Persistence": "Audit privileged accounts; review startup items and scheduled tasks; implement privileged access workstations.",
        "Privilege Escalation": "Apply least-privilege principle; patch immediately; monitor for anomalous privilege use via SIEM.",
        "Defense Evasion": "Enable tamper protection on security tools; implement integrity monitoring; review AV/EDR exclusions.",
        "Credential Access": "Rotate all credentials on affected systems; enable MFA; audit credential stores and secrets management.",
        "Discovery": "Implement network segmentation; restrict LDAP/RPC access; deploy honeytokens to detect enumeration.",
        "Lateral Movement": "Enforce network micro-segmentation; disable unnecessary remote services; monitor east-west traffic.",
        "Collection": "Classify sensitive data; apply DLP controls; restrict access to sensitive file shares.",
        "Exfiltration": "Implement egress filtering; deploy DLP on endpoints; monitor for large data transfers to untrusted IPs.",
        "Impact": "Implement rate limiting and DDoS mitigation; deploy redundant architecture; test business continuity plans.",
        "Command and Control": "Block known C2 domains/IPs; inspect TLS traffic; deploy DNS filtering.",
    }
    return control_map.get(tactic, "Apply vendor-recommended patch and review system for indicators of compromise.")


def calculate_due_date(risk_level: str) -> str:
    """Calculate POAM due date based on risk level (from today)."""
    from datetime import date, timedelta

    today = date.today()
    days_map = {"CRITICAL": 15, "HIGH": 30, "MEDIUM": 90, "LOW": 180}
    days = days_map.get(risk_level, 90)
    due = today + timedelta(days=days)
    return due.strftime("%Y-%m-%d")
