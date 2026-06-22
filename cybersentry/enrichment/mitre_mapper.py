"""MITRE ATT&CK tactic/technique mapper.

Uses keyword heuristics in demo mode, LLM analysis in live mode.
"""
from __future__ import annotations

from typing import Any

# Keyword-based MITRE mapping for demo/offline mode
KEYWORD_TACTIC_MAP: dict[str, tuple[str, str]] = {
    # Initial Access
    "phishing": ("Initial Access", "T1566 - Phishing"),
    "exploit public-facing": ("Initial Access", "T1190 - Exploit Public-Facing Application"),
    "remote code execution": ("Initial Access", "T1190 - Exploit Public-Facing Application"),
    "authentication bypass": ("Initial Access", "T1078 - Valid Accounts"),
    "vpn": ("Initial Access", "T1133 - External Remote Services"),
    "initial access": ("Initial Access", "T1190 - Exploit Public-Facing Application"),
    # Execution
    "command injection": ("Execution", "T1059 - Command and Scripting Interpreter"),
    "arbitrary code": ("Execution", "T1203 - Exploitation for Client Execution"),
    "deserialization": ("Execution", "T1203 - Exploitation for Client Execution"),
    "execute arbitrary": ("Execution", "T1059 - Command and Scripting Interpreter"),
    # Persistence
    "persistence": ("Persistence", "T1136 - Create Account"),
    "administrator account": ("Persistence", "T1136 - Create Account"),
    "supply chain": ("Persistence", "T1195 - Supply Chain Compromise"),
    "ci/cd": ("Persistence", "T1195 - Supply Chain Compromise"),
    # Privilege Escalation
    "privilege escalation": ("Privilege Escalation", "T1068 - Exploitation for Privilege Escalation"),
    "root privileges": ("Privilege Escalation", "T1068 - Exploitation for Privilege Escalation"),
    "administrative access": ("Privilege Escalation", "T1078 - Valid Accounts"),
    # Defense Evasion
    "defense evasion": ("Defense Evasion", "T1562 - Impair Defenses"),
    "bypass": ("Defense Evasion", "T1562 - Impair Defenses"),
    "protected view": ("Defense Evasion", "T1562 - Impair Defenses"),
    # Credential Access
    "credential": ("Credential Access", "T1552 - Unsecured Credentials"),
    "credential access": ("Credential Access", "T1552 - Unsecured Credentials"),
    "password": ("Credential Access", "T1110 - Brute Force"),
    "credentials exposed": ("Credential Access", "T1552 - Unsecured Credentials"),
    # Discovery
    "discovery": ("Discovery", "T1082 - System Information Discovery"),
    "file read": ("Discovery", "T1083 - File and Directory Discovery"),
    # Lateral Movement
    "lateral movement": ("Lateral Movement", "T1210 - Exploitation of Remote Services"),
    "remote access": ("Lateral Movement", "T1021 - Remote Services"),
    # Collection
    "file content": ("Collection", "T1005 - Data from Local System"),
    "sensitive data": ("Collection", "T1213 - Data from Information Repositories"),
    # Exfiltration
    "exfiltration": ("Exfiltration", "T1041 - Exfiltration Over C2 Channel"),
    "secret exfiltration": ("Exfiltration", "T1552 - Unsecured Credentials"),
    # Impact
    "denial of service": ("Impact", "T1499 - Endpoint Denial of Service"),
    "ddos": ("Impact", "T1498 - Network Denial of Service"),
    "resource exhaustion": ("Impact", "T1499 - Endpoint Denial of Service"),
    "availability": ("Impact", "T1499 - Endpoint Denial of Service"),
}


def map_cve_to_mitre_demo(cve: dict[str, Any]) -> tuple[str, str]:
    """Map a CVE to a MITRE ATT&CK tactic/technique using keyword heuristics (demo mode)."""
    text = (cve.get("description", "") + " " + " ".join(cve.get("keywords", []))).lower()

    for keyword, (tactic, technique) in KEYWORD_TACTIC_MAP.items():
        if keyword in text:
            return tactic, technique

    # Default fallback
    return "Initial Access", "T1190 - Exploit Public-Facing Application"


def map_cve_to_mitre_live(cve: dict[str, Any], analyst_func) -> tuple[str, str]:
    """Map a CVE to MITRE ATT&CK using the LLM analyst (live mode)."""
    result = analyst_func("mitre_map", cve)
    tactic = result.get("mitre_tactic", "Initial Access")
    technique = result.get("mitre_technique", "T1190 - Exploit Public-Facing Application")
    return tactic, technique
