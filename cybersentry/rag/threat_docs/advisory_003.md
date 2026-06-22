# Threat Advisory TLP:WHITE — Microsoft Office and Email Platform Exploitation

**Advisory ID:** CSENTRY-ADV-003  
**Date:** 2024-02-20  
**Severity:** HIGH  
**TLP Classification:** WHITE (Unrestricted)

## Summary

A series of high and critical severity vulnerabilities affecting Microsoft Office, Outlook, and Exchange continue to be weaponised in targeted phishing campaigns. These vulnerabilities bypass email security controls and Office Protected View, enabling remote code execution upon opening malicious documents or clicking crafted hyperlinks. The threat is particularly acute in financial services, healthcare, and government sectors.

## Affected Technologies

- **Microsoft Outlook** (CVE-2024-21413): "MonikerLink" vulnerability allows RCE and credential harvesting via specially crafted hyperlinks. Bypasses Office Protected View. CVSS 9.8.
- **Microsoft Exchange** (CVE-2023-36745): Improper input validation enabling RCE by authenticated attackers. CVSS 8.0.
- **Microsoft SharePoint** (CVE-2023-29357): Authentication bypass allowing privilege escalation to Site Collection Administrator. CVSS 9.8.

## Attack Vector Analysis

**CVE-2024-21413 (MonikerLink)** is particularly dangerous because:
- Exploitation does not require the victim to save or execute a file — merely hovering over a link can trigger NTLM credential theft
- The attack bypasses Microsoft's Protected View sandbox
- Credentials captured via NTLM relay can be used for authenticated exploitation of other Microsoft services
- No user interaction beyond opening the email is required in some Outlook configurations

## Observed Campaigns

Financial sector organisations have been targeted with phishing emails containing:
- Fake invoice documents with embedded MonikerLink triggers
- Impersonation of Microsoft 365 login pages to harvest MFA tokens
- Malicious OneNote notebooks distributed via SharePoint

## MITRE ATT&CK Mapping

| Tactic | Technique | Description |
|--------|-----------|-------------|
| Initial Access | T1566.001 | Spearphishing Attachment |
| Initial Access | T1566.002 | Spearphishing Link |
| Execution | T1203 | Exploitation for Client Execution |
| Credential Access | T1187 | Forced Authentication (NTLM relay) |
| Defense Evasion | T1562.001 | Disable or Modify Tools (bypasses Protected View) |
| Lateral Movement | T1550.002 | Pass the Hash |

## Recommended Mitigations

1. **Patch MS Office and Outlook** to February 2024 or later cumulative update
2. **Block NTLM relay**: Enable Extended Protection for Authentication on Exchange, IIS
3. **Email gateway rules**: Block emails containing UNC path hyperlinks (\\server\share format)
4. **Disable NTLM where possible**: Use Kerberos for authentication in environments where NTLM is not required
5. **Security awareness training**: Educate users on MonikerLink attack patterns
6. **Conditional Access**: Require compliant device registration for all M365 access
7. **Attack Surface Reduction rules**: Enable ASR rule to block credential stealing from LSASS

## Indicators of Compromise

- NTLM authentication attempts to external IP addresses from endpoint processes
- Unusual processes spawned by `outlook.exe` or `winword.exe`
- Registry modifications associated with NTLM configuration
- Network connections to non-corporate NTLM relay infrastructure

## References

- Microsoft Security Update Guide: CVE-2024-21413
- Morphisec Blog: MonikerLink Attack Analysis
- CISA KEV: Known Exploited Vulnerabilities Catalog (February 2024 entries)
