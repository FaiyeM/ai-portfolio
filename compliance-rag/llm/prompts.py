"""Prompt templates for ComplianceRAG."""

SYSTEM_PROMPT = """You are a senior compliance analyst specialising in information security regulation.
You provide accurate, precise answers to compliance questions based strictly on the provided regulatory context.

Rules:
- Answer based ONLY on the provided context. Do not use general knowledge to fill gaps.
- If the context does not contain enough information to answer, say so explicitly.
- Cite the specific framework and section when possible.
- Be concise but complete — compliance teams need actionable answers.
- Use professional language appropriate for a legal/regulatory audience."""

QA_PROMPT = """Answer the following compliance question using ONLY the provided regulatory context.

Question: {question}

Regulatory Context:
{context}

Provide a structured response with:
1. Direct answer to the question
2. Specific citations (framework + section/paragraph where applicable)
3. Any important caveats or limitations
4. Confidence: HIGH / MEDIUM / LOW (based on how directly the context addresses the question)"""

DEMO_ANSWERS = {
    "cps 234": {
        "question_keywords": ["cps 234", "apra", "information security capability", "capability"],
        "answer": """**Answer:** APRA CPS 234 requires entities to maintain information security capability **commensurate with the size and extent of threats** to their information assets (Paragraph 15).

**Specific Requirements:**
- Maintain an Information Security Policy reviewed and approved by the Board at least annually
- Ensure Board and senior management maintain active oversight of information security
- Define roles and responsibilities for information security at all organisational levels
- Ensure staff have appropriate skills and resources to fulfil their security responsibilities

**Citation:** CPS 234, Paragraphs 15–20 — Information Security Capability.

**Important Caveat:** The "commensurate" standard is principles-based, meaning APRA assesses adequacy relative to the entity's specific risk profile. Larger entities with greater digital exposure will face higher capability expectations.

**Confidence:** HIGH — The context directly addresses information security capability requirements.""",
    },
    "notification": {
        "question_keywords": ["notification", "breach", "notify", "apra", "72 hours", "material"],
        "answer": """**Answer:** Under CPS 234, entities must notify APRA **as soon as possible and no later than 72 hours** after becoming aware of a material information security incident or an unremediated control weakness.

**Notification Triggers:**
1. An information security incident that **materially affected or could affect** the entity or interested parties → notify within 72 hours
2. An information security **control weakness** expected to remain unremediated in a timely manner → notify as soon as possible

**Citation:** CPS 234, Paragraphs 33–39 — Incident Management and Notification Obligations.

**Important Caveat:** The 72-hour clock starts from when the entity **becomes aware** — not when the incident commenced. Entities should consider when first-level triage creates "awareness" for notification purposes.

**Confidence:** HIGH — Notification timeframes are explicitly stated in the context.""",
    },
    "iso access control": {
        "question_keywords": ["iso 27001", "access control", "annex a", "a.5", "access rights"],
        "answer": """**Answer:** ISO 27001:2022 Annex A addresses access control through four primary controls:

- **A.5.15 — Access Control Policy**: Requires a documented policy based on least privilege and need-to-know principles
- **A.5.16 — Identity Management**: Unique identification for all users; lifecycle management from provisioning to deprovisioning
- **A.5.18 — Access Rights**: Formal provisioning based on role; regular periodic review (typically quarterly/annual); prompt revocation on role change or termination
- **A.8.2 — Privileged Access Rights**: Enhanced controls for admin/DBA/security accounts including separate accounts and increased monitoring frequency

**Citation:** ISO/IEC 27001:2022, Annex A, Controls A.5.15, A.5.16, A.5.18, A.8.2.

**Important Caveat:** ISO 27001 is a risk-based standard — organisations select applicable controls from Annex A based on their risk assessment. All four access controls listed above are typically applicable to most organisations.

**Confidence:** HIGH — The context directly covers ISO 27001 access control requirements.""",
    },
}
