# ISO/IEC 27001:2022 — Key Annex A Controls Summary

**Standard:** ISO/IEC 27001:2022 (Information Security Management Systems)  
**Publisher:** International Organization for Standardization / International Electrotechnical Commission  
**Latest Edition:** October 2022 (replaces 2013 edition)  
**Annex A Controls:** 93 controls across 4 themes (was 114 controls in 2013)

---

## Overview

ISO 27001:2022 Annex A provides a reference set of information security controls that organisations select to manage identified risks. Controls are organised into four themes: Organisational (37), People (8), Physical (14), and Technological (34).

---

## Access Control (Annex A, Theme: Technological)

ISO 27001:2022 addresses access control through multiple controls:

### A.5.15 — Access Control Policy
Organisations must establish, document, and review access control policies. The policy must be based on business and information security requirements and cover:
- The principle of **least privilege** — users receive only the access rights needed for their role
- **Need-to-know** — access to sensitive information is restricted to those who require it
- **Segregation of duties** — conflicting duties must be separated to reduce fraud and error risk

### A.5.16 — Identity Management
All identities — including service accounts, system accounts, and non-human identities — must be managed throughout their lifecycle. Requirements include:
- Unique identification for all users
- Process for identity provisioning, modification, and deprovisioning
- Regular review of identity assignments

### A.5.18 — Access Rights
Access rights must be provisioned, reviewed, and revoked in a controlled manner:
- Access rights must be **provisioned based on role** and business need
- Access rights must be **reviewed at regular intervals** (typically quarterly or annually)
- Access rights must be **revoked promptly** when employment ends or role changes
- Privileged access rights must receive enhanced scrutiny and more frequent review

### A.8.2 — Privileged Access Rights
Management of privileged access (system administrator, DBA, security admin) requires:
- Formal authorisation and time-limited grants
- Separate accounts for privileged and standard access
- Enhanced monitoring of privileged account activity

---

## Cryptography (Annex A 8.24)

The organisation must define and implement a **cryptography policy** covering:
- Appropriate cryptographic algorithms and key lengths
- Key management lifecycle (generation, storage, distribution, destruction)
- Requirements for protecting data at rest and in transit

---

## Incident Management (Annex A 5.24–5.28)

### A.5.24 — Information Security Incident Management Planning
Organisations must define roles, responsibilities, and procedures for detecting, reporting, assessing, and responding to incidents.

### A.5.26 — Response to Information Security Incidents
Response procedures must include containment, eradication, recovery, and post-incident review. Lessons learned must be incorporated into the ISMS.

### A.5.28 — Collection of Evidence
Evidence related to information security events must be collected and preserved in a manner suitable for forensic investigation and potential legal proceedings.

---

## Supplier Relationships (Annex A 5.19–5.22)

### A.5.19 — Information Security in Supplier Relationships
Organisations must define requirements for managing information security risks associated with suppliers and establish appropriate controls in supplier agreements.

### A.5.20 — Addressing Information Security in Agreements
Supplier contracts must include:
- Information security requirements and responsibilities
- Right to audit
- Incident notification obligations
- Requirements for sub-processors

---

## Risk Assessment and Treatment (Clause 6.1)

ISO 27001 requires organisations to:
- Define and apply an **information security risk assessment process**
- Identify risks associated with the loss of confidentiality, integrity, or availability
- Analyse and evaluate identified risks
- Select appropriate **risk treatment options** (mitigate, accept, transfer, avoid)
- Produce a **Statement of Applicability** documenting selected controls

---

## Key Differences: ISO 27001:2022 vs 2013

| Area | 2013 | 2022 |
|------|------|------|
| Total Annex A controls | 114 | 93 |
| Control themes | 14 domains | 4 themes |
| New controls (11) | N/A | Threat intelligence, cloud security, ICT readiness, web filtering, secure coding, data masking |
| Merged controls | N/A | 24 controls merged |

---

## Common Compliance Questions

**Q: How does ISO 27001 Annex A address access control?**  
A: Access control is addressed through A.5.15 (policy), A.5.16 (identity management), A.5.18 (access rights provisioning and review), and A.8.2 (privileged access). The standard requires least privilege, need-to-know, regular access reviews, and prompt revocation.

**Q: Is ISO 27001 mandatory?**  
A: ISO 27001 is a voluntary international standard, though it may be contractually required by customers or mandated by sector-specific regulation. Many financial sector regulators accept ISO 27001 certification as evidence of baseline security capability.

**Q: What is a Statement of Applicability?**  
A: The SoA is a required document that lists all Annex A controls, indicates which are applicable to the organisation, and provides justification for inclusion or exclusion.
