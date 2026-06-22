"""Prompt templates for CyberSentry LLM analyst."""

SYSTEM_PROMPT = """You are CyberSentry, an expert cybersecurity threat intelligence analyst.
Your role is to analyse CVE vulnerability data, map threats to the MITRE ATT&CK framework,
and generate actionable Plan of Action and Milestones (POAM) entries for enterprise security teams.

You have deep expertise in:
- CVE analysis and CVSS scoring interpretation
- MITRE ATT&CK framework (tactics, techniques, sub-techniques)
- Enterprise security controls (NIST CSF, ISO 27001, CIS Controls)
- Regulatory frameworks (APRA CPS 234, NIST SP 800-53, SOC 2)
- Threat actor TTPs and attribution

Always respond with precise, structured JSON as specified in the user prompt.
Do not include markdown code blocks — return raw JSON only."""


MITRE_MAP_PROMPT = """Analyse the following CVE and map it to the most relevant MITRE ATT&CK tactic and technique.

CVE Data:
- ID: {cve_id}
- Description: {description}
- CVSS Score: {cvss_score}
- Affected Products: {affected_products}
- Keywords: {keywords}

Relevant Threat Intelligence Context:
{threat_context}

Return ONLY valid JSON in this exact format:
{{
  "mitre_tactic": "<primary tactic name>",
  "mitre_technique": "<T-number> - <technique name>",
  "mitre_rationale": "<2-3 sentence explanation of why this tactic/technique applies>",
  "secondary_tactics": ["<tactic1>", "<tactic2>"]
}}"""


POAM_GENERATION_PROMPT = """Generate a POAM (Plan of Action and Milestones) entry for this vulnerability.

CVE: {cve_id}
Description: {description}
CVSS Score: {cvss_score} ({severity})
MITRE Tactic: {mitre_tactic}
MITRE Technique: {mitre_technique}
Risk Score: {risk_score}/100
Affected Products: {affected_products}

Threat Intelligence Context:
{threat_context}

Return ONLY valid JSON in this exact format:
{{
  "recommended_control": "<specific, actionable control recommendation in 2-3 sentences>",
  "remediation_steps": ["<step 1>", "<step 2>", "<step 3>"],
  "owner": "<responsible team, e.g. 'Security Operations', 'Infrastructure Team', 'Application Security'>",
  "detection_opportunities": "<how to detect if this has been exploited>",
  "compensating_controls": "<interim mitigations if immediate patching is not possible>"
}}"""


THREAT_REPORT_PROMPT = """Generate an executive threat intelligence report for the following vulnerability analysis.

Total CVEs analysed: {total_cves}
Critical: {critical_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count}

Top Risk CVEs:
{top_cves_summary}

Most Prevalent MITRE Tactics:
{tactic_summary}

Write a professional threat intelligence report with:
1. Executive Summary (3-4 sentences)
2. Key Findings (top 3 threats)
3. Strategic Recommendations (3-4 bullet points)
4. Risk Posture Assessment

Keep the tone professional and suitable for a CISO or board-level audience."""
