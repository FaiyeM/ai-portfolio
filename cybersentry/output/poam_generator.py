"""POAM (Plan of Action and Milestones) generator.

Produces structured JSON and CSV POAM entries from enriched CVE data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR
from enrichment.risk_scorer import get_recommended_control, calculate_due_date

POAM_COLUMNS = [
    "CVE_ID",
    "Severity",
    "MITRE_Tactic",
    "MITRE_Technique",
    "Risk_Score",
    "Recommended_Control",
    "Due_Date",
    "Owner",
    "Remediation_Steps",
    "Detection_Opportunities",
    "Compensating_Controls",
    "Affected_Products",
    "CVSS_Score",
    "CVSS_Vector",
]


def build_poam_entry(
    cve: dict[str, Any],
    mitre_result: dict[str, Any],
    risk_result: dict[str, Any],
    poam_details: dict[str, Any],
) -> dict[str, Any]:
    """Assemble a single POAM entry from all analysis results."""
    tactic = mitre_result.get("mitre_tactic", "Unknown")
    risk_level = risk_result.get("risk_level", "MEDIUM")

    return {
        "CVE_ID": cve["cve_id"],
        "Severity": cve.get("severity", "UNKNOWN"),
        "MITRE_Tactic": tactic,
        "MITRE_Technique": mitre_result.get("mitre_technique", "Unknown"),
        "Risk_Score": risk_result.get("risk_score", 0.0),
        "Recommended_Control": poam_details.get(
            "recommended_control",
            get_recommended_control(tactic, cve.get("severity", "MEDIUM")),
        ),
        "Due_Date": calculate_due_date(risk_level),
        "Owner": poam_details.get("owner", "Security Operations"),
        "Remediation_Steps": " | ".join(poam_details.get("remediation_steps", [])),
        "Detection_Opportunities": poam_details.get("detection_opportunities", ""),
        "Compensating_Controls": poam_details.get("compensating_controls", ""),
        "Affected_Products": ", ".join(cve.get("affected_products", [])),
        "CVSS_Score": cve.get("cvss_score", 0.0),
        "CVSS_Vector": cve.get("cvss_vector", ""),
    }


def save_poam_csv(entries: list[dict[str, Any]], filename: str = "poam_entries.csv") -> Path:
    """Save POAM entries to CSV."""
    output_path = OUTPUT_DIR / filename
    df = pd.DataFrame(entries, columns=POAM_COLUMNS)

    # Sort by risk score descending
    df = df.sort_values("Risk_Score", ascending=False).reset_index(drop=True)

    df.to_csv(output_path, index=False)
    return output_path


def save_poam_json(entries: list[dict[str, Any]], filename: str = "poam_entries.json") -> Path:
    """Save POAM entries to JSON."""
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w") as f:
        json.dump(entries, f, indent=2)
    return output_path
