"""NVD API client for fetching CVE data.

Falls back to sample_cves.json when offline or no API key is provided.
"""
import json
import time
from pathlib import Path
from typing import Any

import requests

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import NVD_API_KEY, NVD_BASE_URL, SAMPLE_CVES_PATH


def fetch_recent_cves(days_back: int = 7, max_results: int = 20) -> list[dict[str, Any]]:
    """Fetch recent CVEs from the NVD API.

    Falls back to sample data if the API is unavailable or no key is provided.
    """
    if not NVD_API_KEY:
        print("  [NVD] No API key configured — loading sample CVEs from file.")
        return load_sample_cves()

    try:
        from datetime import datetime, timedelta, timezone

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)

        params = {
            "pubStartDate": start_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "pubEndDate": end_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": min(max_results, 100),
        }
        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}

        response = requests.get(NVD_BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        cves = []
        for item in data.get("vulnerabilities", []):
            cve_data = item.get("cve", {})
            cve_id = cve_data.get("id", "UNKNOWN")

            descriptions = cve_data.get("descriptions", [])
            description = next(
                (d["value"] for d in descriptions if d.get("lang") == "en"), ""
            )

            metrics = cve_data.get("metrics", {})
            cvss_score = 0.0
            cvss_vector = ""
            severity = "UNKNOWN"

            for metric_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                if metric_key in metrics and metrics[metric_key]:
                    m = metrics[metric_key][0]
                    cvss_data = m.get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    cvss_vector = cvss_data.get("vectorString", "")
                    severity = m.get("baseSeverity", cvss_data.get("baseSeverity", "UNKNOWN"))
                    break

            published = cve_data.get("published", "")[:10]

            cves.append({
                "cve_id": cve_id,
                "description": description,
                "cvss_score": cvss_score,
                "cvss_vector": cvss_vector,
                "severity": severity.upper(),
                "published_date": published,
                "affected_products": _extract_products(cve_data),
                "cwe": _extract_cwe(cve_data),
                "references": [r.get("url", "") for r in cve_data.get("references", [])[:3]],
                "keywords": _extract_keywords(description),
            })

        print(f"  [NVD] Fetched {len(cves)} CVEs from NVD API.")
        return cves

    except requests.RequestException as exc:
        print(f"  [NVD] API error ({exc}) — falling back to sample data.")
        return load_sample_cves()


def load_sample_cves() -> list[dict[str, Any]]:
    """Load CVE records from the bundled sample file."""
    with open(SAMPLE_CVES_PATH) as f:
        cves = json.load(f)
    print(f"  [NVD] Loaded {len(cves)} sample CVEs from {SAMPLE_CVES_PATH.name}.")
    return cves


def _extract_products(cve_data: dict) -> list[str]:
    """Extract affected product names from CPE configuration."""
    products = []
    configs = cve_data.get("configurations", [])
    for config in configs[:1]:
        for node in config.get("nodes", [])[:3]:
            for cpe_match in node.get("cpeMatch", [])[:2]:
                cpe = cpe_match.get("criteria", "")
                parts = cpe.split(":")
                if len(parts) >= 5:
                    vendor = parts[3].replace("_", " ").title()
                    product = parts[4].replace("_", " ").title()
                    products.append(f"{vendor} {product}")
    return products or ["Unknown"]


def _extract_cwe(cve_data: dict) -> str:
    """Extract CWE identifier."""
    weaknesses = cve_data.get("weaknesses", [])
    for weakness in weaknesses:
        for desc in weakness.get("description", []):
            if desc.get("lang") == "en":
                return desc.get("value", "Unknown")
    return "Unknown"


def _extract_keywords(description: str) -> list[str]:
    """Extract simple keywords from description text."""
    keyword_map = {
        "remote code execution": "remote code execution",
        "authentication bypass": "authentication bypass",
        "privilege escalation": "privilege escalation",
        "sql injection": "sql injection",
        "cross-site scripting": "cross-site scripting",
        "denial of service": "denial of service",
        "buffer overflow": "buffer overflow",
        "deserialization": "deserialization",
        "command injection": "command injection",
        "path traversal": "path traversal",
        "credentials": "credential access",
        "phishing": "phishing",
        "lateral movement": "lateral movement",
        "exfiltration": "exfiltration",
    }
    desc_lower = description.lower()
    return [v for k, v in keyword_map.items() if k in desc_lower]
