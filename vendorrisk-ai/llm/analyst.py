"""LLM analyst for VendorRisk AI — live and demo modes."""
from __future__ import annotations

import json
import os
from typing import Any

from .prompts import SYSTEM_PROMPT, SCORE_PROMPT, REMEDIATION_PROMPT

# ── Demo mode canned scores ────────────────────────────────────── #

DEMO_SCORES_ACME = {
    1: {"score": 9, "rationale": "Excellent — AES-256 with AWS KMS, automatic key rotation, and annual audit. Full coverage confirmed.", "risk_flags": []},
    2: {"score": 9, "rationale": "Strong — TLS 1.3 default, HSTS enforced, deprecated older protocols. Certificate management automated.", "risk_flags": []},
    3: {"score": 8, "rationale": "Good — GDPR and APA compliant, DPO appointed, PIA process in place. Minor gap: no mention of data subject rights SLA.", "risk_flags": ["No data subject rights SLA mentioned"]},
    4: {"score": 8, "rationale": "Good — defined retention periods, NIST 800-88 deletion, automated workflows. Quarterly review cycle is appropriate.", "risk_flags": []},
    5: {"score": 9, "rationale": "Excellent — specific RTO/RPO for tiered services, tested annually, contractually committed.", "risk_flags": []},
    6: {"score": 9, "rationale": "Excellent — annual full test plus quarterly tabletop exercises. Results shared with customers. Recent test March 2024 passed.", "risk_flags": []},
    7: {"score": 8, "rationale": "Good — hourly backups, cross-region, 90-day retention, monthly restoration tests. Cold storage for critical data is good practice.", "risk_flags": []},
    8: {"score": 8, "rationale": "Good — DPAs in place with named sub-processors. 24-hour incident notification requirement from sub-processors is strong.", "risk_flags": []},
    9: {"score": 8, "rationale": "Good — annual SOC 2 review for Tier 1 sub-processors and formal approval process. Well-structured.", "risk_flags": []},
    10: {"score": 9, "rationale": "Excellent — ISO 27001:2022, SOC 2 Type II, and PCI DSS Level 1 held. Reports available under NDA. All certifications current.", "risk_flags": []},
    11: {"score": 8, "rationale": "Good — regulatory register covering GDPR, APA, and APRA CPS 234. Board-level reporting and external legal counsel engaged.", "risk_flags": []},
    12: {"score": 9, "rationale": "Excellent — 24-hour contractual notification commitment and 72-hour written report. Clear escalation contacts.", "risk_flags": []},
    13: {"score": 9, "rationale": "Excellent — NIST framework, named SIRT with 24/7 coverage, annual tabletop testing. Comprehensive and well-documented.", "risk_flags": []},
    14: {"score": 7, "rationale": "Good — transparent disclosure of credential stuffing incident. Quick detection and response. RCA completed. Minor concern: only one incident noted in 2 years.", "risk_flags": ["Limited transparency on whether additional unreported incidents occurred"]},
}

DEMO_SCORES_FINCO = {
    1: {"score": 3, "rationale": "Below standard — vague reference to 'industry standard methods' with acknowledged legacy encryption. No AES-256 confirmation or key management details.", "risk_flags": ["Legacy encryption in use", "No AES-256 confirmation", "No key management details"]},
    2: {"score": 2, "rationale": "Inadequate — acknowledges internal APIs still use HTTP. This is a critical control failure for any data-carrying API.", "risk_flags": ["Unencrypted internal API traffic", "TLS not universally enforced"]},
    3: {"score": 4, "rationale": "Below standard — references privacy policy but no mention of data mapping, PIAs, or DPO. Insufficient for financial sector compliance.", "risk_flags": ["No data mapping mentioned", "No DPO or privacy impact assessments"]},
    4: {"score": 3, "rationale": "Below standard — very vague. No specific retention periods, no mention of secure deletion method, no evidence of enforcement.", "risk_flags": ["No specific retention periods", "No secure deletion methodology"]},
    5: {"score": 1, "rationale": "Inadequate — explicitly states no defined RTO/RPO. This is a critical gap for any vendor handling production data.", "risk_flags": ["No defined RTO", "No defined RPO", "Critical BC gap"]},
    6: {"score": 2, "rationale": "Inadequate — last test 18 months ago and testing described as only 'periodic'. Insufficient frequency for critical vendor.", "risk_flags": ["DR test overdue (18 months)", "No defined testing frequency"]},
    7: {"score": 3, "rationale": "Below standard — nightly backups only (not hourly/continuous), no mention of encryption, and restoration not recently tested.", "risk_flags": ["No backup restoration testing", "Backup encryption not confirmed", "Nightly only (not continuous)"]},
    8: {"score": 3, "rationale": "Below standard — vague reference to 'standard contracts' with no mention of security requirements, DPAs, or incident notification flow-down.", "risk_flags": ["No DPAs confirmed with sub-processors", "No security requirements flow-down"]},
    9: {"score": 3, "rationale": "Below standard — sub-processor security review folded into general procurement. No SOC 2 review or dedicated security assessment framework.", "risk_flags": ["No dedicated sub-processor security assessment"]},
    10: {"score": 1, "rationale": "Inadequate — no ISO 27001, SOC 2, or PCI DSS certification held. Reliance on 'internal security reviews' is insufficient for financial sector.", "risk_flags": ["No ISO 27001", "No SOC 2 Type II", "No third-party attestation"]},
    11: {"score": 3, "rationale": "Below standard — compliance monitoring limited to primary jurisdiction with no APRA or cross-border compliance evidence.", "risk_flags": ["Limited regulatory compliance evidence", "No APRA compliance mentioned"]},
    12: {"score": 2, "rationale": "Inadequate — vague 'as required by law' commitment. No defined timeframe, no named escalation contacts. Unacceptable for financial sector vendor.", "risk_flags": ["No defined notification timeframe", "Contractual notification commitment unclear"]},
    13: {"score": 3, "rationale": "Below standard — no named SIRT, no mention of 24/7 coverage, no testing frequency. Generic description insufficient for critical vendor.", "risk_flags": ["No named incident response team", "No defined escalation path", "No testing evidence"]},
    14: {"score": 2, "rationale": "Inadequate — vague reference to 'minor security events' handled internally. Lack of transparency and absence of formal classification framework is a red flag.", "risk_flags": ["Undisclosed security incidents", "No formal incident classification", "Transparency concern"]},
}

DEMO_REMEDIATION_FINCO = {
    "remediation_actions": [
        {"priority": "IMMEDIATE", "action": "Require FinCo to provide a written commitment to encrypt all API traffic within 30 days, with monthly progress updates.", "rationale": "Unencrypted internal API traffic represents an immediate data exposure risk.", "timeline": "30 days"},
        {"priority": "IMMEDIATE", "action": "Require FinCo to define and contractually commit to RTO/RPO for all Tier 1 services within 30 days.", "rationale": "Absence of recovery objectives makes the vendor unsuitable for any production critical workload.", "timeline": "30 days"},
        {"priority": "SHORT_TERM", "action": "Request FinCo's 12-month roadmap to ISO 27001 certification or equivalent, with quarterly checkpoints.", "rationale": "No third-party attestation is a fundamental gap for financial sector vendor.", "timeline": "90 days"},
        {"priority": "SHORT_TERM", "action": "Conduct an onsite security assessment or commission a third-party penetration test at FinCo's expense.", "rationale": "Self-reported assessments are insufficient given the number of gaps identified.", "timeline": "90 days"},
        {"priority": "MEDIUM_TERM", "action": "Include contractual right-to-audit and annual security attestation requirements in the vendor agreement renewal.", "rationale": "Formal oversight mechanisms are required to manage ongoing risk from this vendor.", "timeline": "At contract renewal"},
    ],
    "executive_summary": "FinCo Services presents a HIGH risk profile with critical gaps across all five assessment domains. The vendor does not hold any third-party security certifications, lacks defined business continuity commitments, and has unencrypted internal API traffic. Engagement with FinCo for any data-sensitive or production-critical workload is not recommended without immediate remediation of the critical findings. If the relationship must continue, enhanced contractual protections and monitoring are required."
}

DEMO_REMEDIATION_ACME = {
    "remediation_actions": [
        {"priority": "SHORT_TERM", "action": "Negotiate inclusion of explicit data subject rights SLA (e.g. 30-day response) in data processing agreement.", "rationale": "Minor gap in privacy programme completeness.", "timeline": "90 days"},
        {"priority": "SHORT_TERM", "action": "Request copy of most recent DR test results and BCP documentation for internal file.", "rationale": "Maintain evidence of continuity commitments for regulatory purposes.", "timeline": "60 days"},
        {"priority": "MEDIUM_TERM", "action": "Schedule annual vendor review meeting to discuss emerging risks and certification renewals.", "rationale": "ISO 27001 and SOC 2 attestations should be reviewed annually.", "timeline": "Annual"},
        {"priority": "MEDIUM_TERM", "action": "Review sub-processor list annually and confirm no high-risk additions without prior approval.", "rationale": "Sub-processor changes can introduce new risk without customer notification.", "timeline": "Annual"},
        {"priority": "MEDIUM_TERM", "action": "Confirm Acme Corp has reviewed and updated IRP following credential stuffing incident lessons learned.", "rationale": "Verify the 5 remediation actions from the 2023 incident were completed.", "timeline": "90 days"},
    ],
    "executive_summary": "Acme Corp presents a LOW risk profile with strong security controls across all assessment domains. The vendor holds ISO 27001:2022, SOC 2 Type II, and PCI DSS Level 1 certifications, has well-defined business continuity commitments, and demonstrated transparent incident handling. Minor gaps in privacy programme completeness and sub-processor transparency should be addressed through routine contract management. Acme Corp is assessed as suitable for data-sensitive and production-critical workloads subject to annual review."
}


class VendorRiskAnalyst:
    """Vendor risk analyst — live or demo mode."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._client = None
        if not demo_mode:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set. Use --demo or add key to .env")
            self._client = anthropic.Anthropic(api_key=api_key)

    def score_response(self, domain: str, question_id: int, question: str, response: str, vendor_name: str) -> dict[str, Any]:
        """Score a single questionnaire response."""
        if self.demo_mode:
            # Choose canned scores based on vendor name
            if "acme" in vendor_name.lower():
                return {
                    "domain": domain,
                    "question_id": question_id,
                    **DEMO_SCORES_ACME.get(question_id, {"score": 5, "rationale": "Demo score.", "risk_flags": []}),
                }
            else:
                return {
                    "domain": domain,
                    "question_id": question_id,
                    **DEMO_SCORES_FINCO.get(question_id, {"score": 3, "rationale": "Demo score.", "risk_flags": ["Generic risk flag"]}),
                }

        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        prompt = SCORE_PROMPT.format(
            domain=domain,
            question=question,
            response=response[:800],
            question_id=question_id,
        )

        resp = self._client.messages.create(
            model=model,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        result = json.loads(resp.content[0].text)
        return result

    def generate_remediation(self, vendor_name: str, aggregation: dict[str, Any]) -> dict[str, Any]:
        """Generate remediation recommendations."""
        if self.demo_mode:
            if "acme" in vendor_name.lower():
                return DEMO_REMEDIATION_ACME
            return DEMO_REMEDIATION_FINCO

        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        findings = "\n".join(
            f"- Q{f['question_id']} ({f['domain']}): Score {f['score']}/10 — {f['rationale'][:100]}"
            for f in aggregation.get("top_findings", [])
        )
        prompt = REMEDIATION_PROMPT.format(
            vendor_name=vendor_name,
            overall_score=aggregation["overall_score"],
            risk_tier=aggregation["risk_tier"],
            findings_summary=findings,
        )

        resp = self._client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(resp.content[0].text)
