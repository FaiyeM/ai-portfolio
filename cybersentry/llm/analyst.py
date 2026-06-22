"""Anthropic LLM analyst for CyberSentry.

Provides both live (Anthropic API) and demo (canned responses) modes.
"""
from __future__ import annotations

import json
from typing import Any

from .prompts import SYSTEM_PROMPT, MITRE_MAP_PROMPT, POAM_GENERATION_PROMPT, THREAT_REPORT_PROMPT

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL


# --------------------------------------------------------------------------- #
# Demo mode canned responses                                                   #
# --------------------------------------------------------------------------- #

DEMO_MITRE_RESPONSES: dict[str, dict] = {
    "CVE-2024-21413": {
        "mitre_tactic": "Initial Access",
        "mitre_technique": "T1566.002 - Spearphishing Link",
        "mitre_rationale": "CVE-2024-21413 exploits Outlook's handling of hyperlinks to bypass Protected View, enabling credential theft and RCE via a crafted email link. The attack vector is email-based and requires minimal user interaction — consistent with spearphishing link delivery.",
        "secondary_tactics": ["Credential Access", "Execution"],
    },
    "CVE-2024-3400": {
        "mitre_tactic": "Initial Access",
        "mitre_technique": "T1190 - Exploit Public-Facing Application",
        "mitre_rationale": "CVE-2024-3400 is a command injection in Palo Alto GlobalProtect, an internet-facing VPN gateway. Unauthenticated exploitation grants root shell on the firewall, making this a textbook public-facing application exploitation vector.",
        "secondary_tactics": ["Execution", "Privilege Escalation"],
    },
}

DEMO_POAM_RESPONSES: dict[str, dict] = {
    "CVE-2024-21413": {
        "recommended_control": "Apply Microsoft February 2024 cumulative update immediately. Block UNC path hyperlinks at email gateway. Enable Extended Protection for Authentication to prevent NTLM relay.",
        "remediation_steps": [
            "Deploy Microsoft KB5034763 (February 2024 Patch Tuesday) to all Outlook clients",
            "Configure email gateway to strip or block emails containing UNC-style hyperlinks",
            "Enable EPA (Extended Protection for Authentication) on Exchange and IIS",
        ],
        "owner": "Infrastructure Team",
        "detection_opportunities": "Monitor for NTLM authentication attempts from Outlook.exe to external IPs; alert on processes spawned by outlook.exe that initiate network connections.",
        "compensating_controls": "Disable automatic preview of external content in Outlook; block outbound NTLM (TCP 445) at perimeter firewall.",
    },
}

DEMO_REPORT_TEMPLATE = """## Executive Summary

The CyberSentry analysis identified {total_cves} CVEs requiring immediate attention, including {critical_count} critical-severity vulnerabilities actively targeted by threat actors. The current threat landscape is dominated by exploitation of network perimeter devices, CI/CD platform authentication bypasses, and Microsoft Office remote code execution chains. Immediate patching action is required to prevent ransomware deployment and supply chain compromise.

## Key Findings

**Finding 1 — Critical Network Perimeter Exposure**: Multiple CVSS 10.0 vulnerabilities affect SSL VPN concentrators and next-generation firewalls. Nation-state actors (notably APT29) are actively exploiting these vulnerabilities within hours of public disclosure. Dwell time before lateral movement is measured in minutes, not days.

**Finding 2 — CI/CD Supply Chain Risk**: Authentication bypass vulnerabilities in JetBrains TeamCity and Jenkins expose software build pipelines to compromise. Successful exploitation enables code injection into production artefacts, with catastrophic downstream supply chain impact.

**Finding 3 — Email Attack Surface**: Microsoft Outlook CVE-2024-21413 bypasses Protected View to steal NTLM credentials without requiring file execution. This attack is trivially scalable via phishing campaigns.

## Strategic Recommendations

- **Establish a 24-hour SLA** for patching CVSS ≥ 9.0 vulnerabilities on internet-facing systems
- **Implement Zero Trust Network Access** to replace legacy VPN architectures that present large, exploitable attack surfaces
- **Harden CI/CD environments** by isolating build servers, rotating all secrets, and implementing artefact signing
- **Deploy MFA universally** with phishing-resistant authenticators (FIDO2/WebAuthn) to mitigate credential-based attacks

## Risk Posture Assessment

**Overall Risk Level: HIGH**. The organisation faces a concentrated wave of critical vulnerabilities across multiple technology domains. Without immediate patching, the probability of successful exploitation is HIGH. The recommended POAM entries provide a structured remediation roadmap targeting complete closure within 90 days for non-critical and 15 days for critical findings."""


class ThreatAnalyst:
    """Threat intelligence analyst backed by Anthropic Claude or demo mode."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._client = None
        if not demo_mode:
            self._init_client()

    def _init_client(self) -> None:
        """Initialise the Anthropic client."""
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Run with --demo flag or set the key in .env"
            )
        import anthropic
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def analyse_mitre(self, cve: dict[str, Any], threat_context: str = "") -> dict[str, Any]:
        """Map a CVE to MITRE ATT&CK."""
        if self.demo_mode:
            return DEMO_MITRE_RESPONSES.get(cve["cve_id"], {
                "mitre_tactic": "Initial Access",
                "mitre_technique": "T1190 - Exploit Public-Facing Application",
                "mitre_rationale": f"Based on CVE description keywords, {cve['cve_id']} maps to exploitation of a public-facing application allowing initial network access.",
                "secondary_tactics": ["Execution"],
            })

        prompt = MITRE_MAP_PROMPT.format(
            cve_id=cve["cve_id"],
            description=cve.get("description", "")[:800],
            cvss_score=cve.get("cvss_score", "N/A"),
            affected_products=", ".join(cve.get("affected_products", [])),
            keywords=", ".join(cve.get("keywords", [])),
            threat_context=threat_context[:1000],
        )

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    def generate_poam_details(self, cve: dict[str, Any], mitre_result: dict, threat_context: str = "") -> dict[str, Any]:
        """Generate POAM details for a CVE."""
        if self.demo_mode:
            return DEMO_POAM_RESPONSES.get(cve["cve_id"], {
                "recommended_control": f"Apply the vendor patch for {cve['cve_id']} immediately. Implement network-level mitigations and monitor for IOCs.",
                "remediation_steps": [
                    f"Apply vendor security advisory patch for {cve['cve_id']}",
                    "Verify patch deployment via vulnerability scanner",
                    "Review logs for indicators of prior exploitation",
                ],
                "owner": "Security Operations",
                "detection_opportunities": "Monitor SIEM for CVE-specific IOCs and anomalous process execution patterns.",
                "compensating_controls": "Restrict network access to affected service; increase logging verbosity on affected systems.",
            })

        prompt = POAM_GENERATION_PROMPT.format(
            cve_id=cve["cve_id"],
            description=cve.get("description", "")[:600],
            cvss_score=cve.get("cvss_score", "N/A"),
            severity=cve.get("severity", "UNKNOWN"),
            mitre_tactic=mitre_result.get("mitre_tactic", ""),
            mitre_technique=mitre_result.get("mitre_technique", ""),
            risk_score=cve.get("risk_score", "N/A"),
            affected_products=", ".join(cve.get("affected_products", [])),
            threat_context=threat_context[:800],
        )

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    def generate_threat_report(self, analysis_summary: dict[str, Any]) -> str:
        """Generate an executive threat intelligence report."""
        if self.demo_mode:
            return DEMO_REPORT_TEMPLATE.format(
                total_cves=analysis_summary.get("total_cves", 0),
                critical_count=analysis_summary.get("critical_count", 0),
            )

        prompt = THREAT_REPORT_PROMPT.format(
            total_cves=analysis_summary["total_cves"],
            critical_count=analysis_summary.get("critical_count", 0),
            high_count=analysis_summary.get("high_count", 0),
            medium_count=analysis_summary.get("medium_count", 0),
            low_count=analysis_summary.get("low_count", 0),
            top_cves_summary=analysis_summary.get("top_cves_summary", ""),
            tactic_summary=analysis_summary.get("tactic_summary", ""),
        )

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
