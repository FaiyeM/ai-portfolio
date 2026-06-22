# SOC 2 — Trust Service Criteria Summary

**Framework:** SOC 2 (System and Organisation Controls 2)  
**Standard Body:** American Institute of Certified Public Accountants (AICPA)  
**Report Types:** SOC 2 Type I (design only) | SOC 2 Type II (design + operating effectiveness over period)  
**Common Criteria Version:** 2022 (based on COSO 2013 internal control framework)

---

## Overview

SOC 2 evaluates controls relevant to one or more of five Trust Service Criteria (TSC): Security (mandatory), Availability, Processing Integrity, Confidentiality, and Privacy. Security is required in every SOC 2 examination; the other four categories are optional and selected based on the services provided and customer requirements.

---

## Security — Common Criteria (CC)

Security is the foundational TSC and applies to all SOC 2 examinations.

### CC1 — Control Environment
The organisation demonstrates commitment to integrity, ethical values, and competence. This includes:
- A defined **code of conduct** and accountability structures
- Board and management oversight of internal controls
- Policies for attracting, developing, and retaining competent personnel

### CC6 — Logical and Physical Access Controls
The most scrutinised section in most SOC 2 audits:

**CC6.1** — Logical access security measures restrict access to systems:
- Multi-factor authentication (MFA) is implemented for access to systems containing sensitive data
- Access is provisioned based on authorised roles
- Access is reviewed at defined intervals and upon change of role or termination

**CC6.2** — Prior to issuing system credentials, authorisation is confirmed:
- Unique user IDs are assigned
- Passwords meet complexity and rotation requirements
- Service accounts are inventoried and controlled

**CC6.3** — Access is removed when no longer required:
- Off-boarding procedures ensure timely access revocation
- Terminated user accounts are disabled within defined timeframes (typically same day)

**CC6.6** — Logical access security measures protect against threats from external sources:
- Firewalls, IDS/IPS, and network segmentation are implemented
- Vulnerability management is conducted at defined intervals
- Penetration testing is performed at least annually

**CC6.7** — Transmission and storage protections:
- Data in transit is encrypted using TLS 1.2 or higher
- Data at rest is encrypted using AES-256 or equivalent
- Removable media controls are in place

### CC7 — System Operations
**CC7.1** — Detection of anomalies and security events:
- Security monitoring tools (SIEM) are in place
- Alerts are configured for anomalous access patterns, privilege escalation, and data exfiltration
- Log retention meets defined periods (typically 90 days hot, 1 year archived)

**CC7.2** — Monitoring of system components:
- System performance and availability are monitored
- Capacity planning is conducted to prevent degradation

**CC7.3** — Evaluation of security events:
- Security events are triaged, classified, and escalated per defined procedures
- Incident response procedures are documented and tested

### CC8 — Change Management
- Changes to infrastructure, software, and data undergo a formal change management process
- Changes are authorised, tested, and documented before deployment
- Emergency changes have post-hoc review and approval

### CC9 — Risk Mitigation
- Risks from business disruption are identified and mitigated
- Business continuity and disaster recovery plans are documented and tested
- Vendor risk assessments are conducted for critical third parties

---

## Availability Criteria (A Series)

**A1.1** — The organisation establishes availability commitments:
- Service Level Agreements (SLAs) define uptime targets
- Monitoring systems detect and alert on availability degradation

**A1.2** — Environmental protections support availability:
- Data centres have redundant power, cooling, and network connectivity
- Backup and recovery procedures are tested at defined intervals

**A1.3** — Recovery procedures are tested:
- Disaster recovery tests are conducted at least annually
- Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO) are defined and validated

---

## Confidentiality Criteria (C Series)

**C1.1** — Confidential information is identified and classified  
**C1.2** — Confidential information is protected during processing and storage  
**C1.3** — Confidential information is disposed of when no longer needed using secure deletion or physical destruction

---

## Privacy Criteria (P Series)

Applies to organisations processing personal information. Covers notice, choice, collection, use, retention, and disposal of personal data. Aligns with GDPR and US state privacy law requirements.

---

## SOC 2 vs ISO 27001 — Key Differences

| Dimension | SOC 2 | ISO 27001 |
|-----------|-------|-----------|
| Origin | US (AICPA) | International (ISO/IEC) |
| Focus | Control effectiveness | ISMS management system |
| Output | Audit report | Certification |
| Renewal | Annual audit | 3-year certification cycle |
| Mandatory criteria | Security | Information security risk management |

---

## Common Compliance Questions

**Q: What are the notification obligations under SOC 2 if a data breach occurs?**  
A: SOC 2 itself does not mandate specific breach notification timeframes — it requires that the organisation's defined incident response procedures are followed. However, CC7 requires documented and tested incident response plans. Notification obligations are driven by applicable law (GDPR 72 hours, APRA 72 hours, HIPAA 60 days, US state laws vary).

**Q: How does SOC 2 address sub-processors?**  
A: Under CC9, organisations must assess risks from vendors and critical sub-processors. Agreements with sub-processors should include security requirements and the right to audit or obtain attestation (e.g., the sub-processor's own SOC 2 report).

**Q: What is the difference between SOC 2 Type I and Type II?**  
A: Type I reports on the design of controls at a point in time. Type II reports on the design AND operating effectiveness of controls over a period (typically 6–12 months). Most enterprise customers require Type II.
