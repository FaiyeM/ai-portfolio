# VendorRisk AI

> Automated third-party vendor risk assessment tool that scores vendors against a security questionnaire using LLM analysis and produces structured PDF risk reports.

---

## Overview

VendorRisk AI automates the most laborious part of third-party risk management: evaluating vendor security questionnaire responses at scale. It ingests vendor responses against a configurable questionnaire (14–25 questions across 5 security domains), sends each response to Claude for structured JSON scoring with rationale and risk flags, aggregates domain-weighted scores into an overall risk tier, and generates a professional PDF report including an executive summary, domain score table, radar chart, top-5 findings, and remediation roadmap. The full pipeline runs in demo mode without an API key using pre-loaded sample responses for two contrasting vendors — Acme Corp (LOW risk) and FinCo Services (HIGH risk).

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                   VendorRisk AI Pipeline                          │
│                                                                    │
│  Input                        Processing                Output    │
│  ┌──────────────┐            ┌────────────────────┐              │
│  │ Questionnaire│            │ LLM Analyst        │              │
│  │ (JSON)       │──────────▶ │ (Claude / Demo)    │              │
│  └──────────────┘  Q+A       │ Score 0-10 per Q   │              │
│  ┌──────────────┐            │ + rationale        │              │
│  │ Vendor       │            │ + risk_flags       │              │
│  │ Responses    │──────────▶ └────────┬───────────┘              │
│  │ (JSON)       │                     │                           │
│  └──────────────┘                     ▼                           │
│                           ┌───────────────────────┐              │
│                           │ Aggregator            │              │
│                           │ Domain-weighted score │              │
│                           │ Risk tier             │              │
│                           │ Top-5 findings        │              │
│                           └────────┬──────────────┘              │
│                                    │                              │
│                          ┌─────────▼───────────┐                 │
│                          │   PDF Generator      │                 │
│                          │   (ReportLab)        │                 │
│                          │   Radar chart        │                 │
│                          │   + Remediation      │                 │
│                          └─────────────────────-┘                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Structured LLM scoring**: Claude returns `{"score": 0-10, "rationale": "...", "risk_flags": [...]}` JSON per question — enabling programmatic downstream processing, not just text output
- **Configurable domain weighting**: `domain_weights.py` allows different weight profiles per context (default vs financial sector)
- **Risk tier mapping**: Overall scores map to CRITICAL (0–39) / HIGH (40–59) / MEDIUM (60–79) / LOW (80–100) — aligning with standard vendor risk registers
- **Two contrasting sample vendors**: Acme Corp (score ~85, LOW risk) and FinCo Services (score ~28, HIGH risk) demonstrate the full scoring range
- **Professional PDF report**: ReportLab-generated PDF with cover page, executive summary table, domain score table, matplotlib radar chart embedded as image, top-5 findings, and remediation action plan
- **JSON output**: Every assessment also produces a machine-readable JSON file for integration with GRC platforms
- **Demo mode**: Complete pipeline with realistic scores and remediation using canned LLM responses — no API key required

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Scoring | Anthropic claude-sonnet-4-6 | Structured JSON scoring per question |
| PDF Generation | ReportLab 4.2 | Professional risk report with tables and charts |
| Radar Chart | Matplotlib 3.9 | Domain score visualisation embedded in PDF |
| Data Processing | Pandas 2.2 | Score tabulation |
| Templates | Jinja2 3.1 | Report template rendering |
| Config | python-dotenv | Environment management |

---

## Project Structure

```
vendorrisk-ai/
├── main.py                         # CLI entrypoint
├── requirements.txt
├── .env.example
├── questionnaires/
│   ├── default_questionnaire.json  # 14 questions across 5 domains
│   └── financial_sector.json       # 25 questions for financial sector
├── assessment/
│   ├── scorer.py                   # Load questionnaire, load responses, call LLM scorer
│   ├── domain_weights.py           # Configurable domain weights
│   └── aggregator.py               # Weighted domain + overall score aggregation
├── llm/
│   ├── analyst.py                  # LLM scoring + remediation (live + demo modes)
│   └── prompts.py                  # System + user prompt templates
├── reporting/
│   └── pdf_generator.py            # Full PDF report with radar chart
├── sample_data/
│   ├── vendor_acme_responses.json  # 14 responses — strong/LOW risk profile
│   └── vendor_finco_responses.json # 14 responses — weak/HIGH risk profile
└── tests/
    └── test_scorer.py              # 9 tests for scoring and aggregation
```

---

## Setup & Installation

```bash
cd ai-portfolio/vendorrisk-ai

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# For live mode
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

---

## Usage / How to Run

### Demo mode — LOW risk vendor
```bash
python main.py --vendor "Acme Corp" --questionnaire default --demo
```

### Demo mode — HIGH risk vendor
```bash
python main.py --vendor "FinCo Services" --questionnaire default --demo
```

### Live mode
```bash
python main.py --vendor "Acme Corp" --questionnaire default --live
```

### Run tests
```bash
python tests/test_scorer.py
```

---

## Sample Output

```
╭─── 🏢 VendorRisk AI ─────────────────────────────────────────╮
│ Vendor: FinCo Services | Questionnaire: default | Mode: DEMO   │
╰─────────────────────────────────────────────────────────────────╯

Results:
  Overall Score: 27.4/100
  Risk Tier:     CRITICAL

         Domain Scores
┌────────────────────────────┬──────────┬────────┐
│ Domain                     │ Score/100│ Weight │
├────────────────────────────┼──────────┼────────┤
│ Data Security & Privacy    │    40    │  30%   │
│ Business Continuity & DR   │    20    │  25%   │
│ Third-Party Sub-processors │    30    │  15%   │
│ Regulatory Compliance      │    20    │  15%   │
│ Incident Response          │    25    │  15%   │
└────────────────────────────┴──────────┴────────┘

Output Files:
✓ PDF Report: output/finco_services_risk_report.pdf
✓ JSON Data:  output/finco_services_risk_data.json
```

**Top 5 Risk Findings (FinCo Services):**
| Finding | Domain | Score | Key Flags |
|---------|--------|-------|-----------|
| Q5 RTO/RPO | BC & DR | 1/10 | No defined RTO, No defined RPO |
| Q10 Certifications | Regulatory | 1/10 | No ISO 27001, No SOC 2 |
| Q2 TLS | Data Security | 2/10 | Unencrypted internal APIs |
| Q12 Incident Notification | IR | 2/10 | No defined notification timeframe |
| Q6 DR Testing | BC & DR | 2/10 | Test overdue (18 months) |

---

## How This Demonstrates AI/ML Competency

- **Structured LLM output engineering**: Designs prompts that elicit consistent, machine-parsable JSON from the LLM — a critical production skill where the downstream code must reliably parse LLM responses without fragile string manipulation.
- **LLM as a reasoning layer**: Uses LLM not for generation but for domain-expert evaluation — each score comes with a rationale and specific risk flags, demonstrating how LLMs can augment human expertise rather than replace structured processes.
- **End-to-end automated workflow**: Chains data ingestion → LLM scoring → weighted aggregation → PDF generation into a single CLI command, demonstrating system design that bridges AI output with business-ready deliverables.
- **Risk quantification**: Translates qualitative LLM assessments into quantitative composite scores using configurable domain weights — showing understanding of how AI outputs must be made interpretable and auditable for regulated business contexts.

---

## Future Enhancements

- **Real questionnaire intake**: Build a web form or email parser to receive vendor responses, eliminating the manual JSON preparation step
- **Comparative benchmarking**: Score multiple vendors in batch and produce a comparative ranking report across a vendor portfolio
- **Historical trending**: Store assessment results in a database and generate trend charts showing risk score improvement or deterioration over annual cycles
- **Control mapping**: Map each question and finding to specific ISO 27001 Annex A controls and NIST CSF functions for regulatory alignment reporting
- **AI-assisted remediation tracking**: Integration with Jira/ServiceNow to automatically create remediation tickets from top findings and track completion

---

## License

MIT License
