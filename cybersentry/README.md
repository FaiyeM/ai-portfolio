# CyberSentry

> LLM-powered threat intelligence analyst that ingests CVE feeds, maps them to MITRE ATT&CK tactics, and generates actionable POAM entries.

---

## Overview

CyberSentry is a production-grade cybersecurity pipeline that automates the most labour-intensive parts of a vulnerability management workflow. It ingests CVE data from the NVD API (or bundled sample data), enriches each record with MITRE ATT&CK tactic mapping using an LLM, calculates composite risk scores that account for both CVSS severity and asset criticality context, and generates structured POAM (Plan of Action and Milestones) entries ready for GRC platforms. A ChromaDB-backed RAG layer retrieves relevant threat advisory context for each CVE before the LLM analysis, producing richer and more accurate outputs. The tool runs fully offline in demo mode — no API key required for evaluators.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CyberSentry Pipeline                      │
│                                                                   │
│  ┌──────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │  NVD API /   │───▶│   Enrichment    │───▶│  LLM Analyst   │  │
│  │  sample_cves │    │  ┌───────────┐  │    │  (Claude)      │  │
│  │  .json       │    │  │MITRE Map  │  │    │                │  │
│  └──────────────┘    │  │Risk Score │  │    └───────┬────────┘  │
│                      │  └───────────┘  │            │           │
│  ┌──────────────┐    └─────────────────┘            │           │
│  │  Threat Docs │                                    │           │
│  │  (Markdown   │───▶┌─────────────────┐            │           │
│  │   Advisories)│    │  ChromaDB RAG   │───▶context─┘           │
│  └──────────────┘    │  Vector Store   │                         │
│                      └─────────────────┘                         │
│                                                                   │
│                            ┌──────────────────────────────────┐  │
│                            │         Output Layer              │  │
│                            │  ┌────────────┐ ┌─────────────┐  │  │
│                            │  │threat_report│ │poam_entries │  │  │
│                            │  │   .md      │ │   .csv      │  │  │
│                            │  └────────────┘ └─────────────┘  │  │
│                            └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Dual-mode operation**: `--demo` runs fully offline with canned LLM responses; `--live` calls the real Anthropic API
- **NVD API integration**: Fetches real-time CVE data with automatic fallback to bundled sample data
- **MITRE ATT&CK mapping**: Maps each CVE to the most relevant tactic and technique across all 14 ATT&CK tactics
- **Composite risk scoring**: Blends CVSS base score (60%) with asset criticality context (40%) plus exploitation status multiplier
- **ChromaDB RAG**: Indexes threat advisory documents and retrieves semantically relevant context per CVE
- **POAM generation**: Produces CSV output with `CVE_ID | Severity | MITRE_Tactic | Technique | Risk_Score | Recommended_Control | Due_Date | Owner`
- **Rich CLI output**: Colour-coded risk table with severity-driven due dates (CRITICAL=15 days, HIGH=30, MEDIUM=90, LOW=180)
- **Automated due dates**: Calculated from today's date based on risk level, aligned with NIST SP 800-53 patch cadence guidelines

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Analysis | Anthropic claude-sonnet-4-6 | MITRE mapping, POAM generation, executive report |
| Vector Store | ChromaDB 0.5 | Persistent threat advisory index for RAG |
| Embeddings | ChromaDB default (all-MiniLM) | Semantic similarity for context retrieval |
| Data Processing | Pandas 2.2 | POAM CSV generation and sorting |
| CVE Data | NVD REST API v2 / sample JSON | Vulnerability ingestion |
| CLI | Rich 13.7 | Formatted console output and progress display |
| Config | python-dotenv | Environment variable management |

---

## Project Structure

```
cybersentry/
├── main.py                     # CLI entrypoint — ingest → enrich → report
├── config.py                   # Config loader from .env with defaults
├── requirements.txt            # Pinned dependencies
├── .env.example                # Environment variable template
├── ingestion/
│   ├── nvd_client.py           # NVD API client with sample data fallback
│   └── sample_cves.json        # 10 realistic CVE records for offline demo
├── enrichment/
│   ├── mitre_mapper.py         # Keyword + LLM MITRE ATT&CK mapper
│   └── risk_scorer.py          # Composite risk score (CVSS + asset context)
├── rag/
│   ├── vector_store.py         # ChromaDB setup and document ingestion
│   ├── retriever.py            # Top-k semantic retrieval per CVE
│   └── threat_docs/            # 3 markdown threat advisories for RAG context
│       ├── advisory_001.md     # Network perimeter RCE (Palo Alto, FortiOS, Ivanti)
│       ├── advisory_002.md     # CI/CD supply chain (TeamCity, Jenkins)
│       └── advisory_003.md     # Microsoft Office/Outlook exploitation
├── llm/
│   ├── analyst.py              # ThreatAnalyst class — live and demo modes
│   └── prompts.py              # System + user prompt templates
├── output/
│   ├── poam_generator.py       # Structured POAM entry builder → CSV + JSON
│   └── report.py               # Markdown threat intelligence report generator
└── tests/
    ├── test_mitre_mapper.py    # 5 unit tests for MITRE keyword mapping
    └── test_risk_scorer.py     # 7 unit tests for risk scoring logic
```

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone or navigate to the project folder
cd ai-portfolio/cybersentry

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional — for live mode only) Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

---

## Usage / How to Run

### Demo mode (no API key required)
```bash
python main.py --demo
```

### Live mode (requires Anthropic API key in .env)
```bash
python main.py --live
```

### Run tests
```bash
python tests/test_mitre_mapper.py
python tests/test_risk_scorer.py
```

### Custom output directory
```bash
python main.py --demo --output ./my_reports
```

---

## Sample Output

```
╭──────────────────────────────────────────────────────────────────╮
│ 🛡️  CyberSentry                                                  │
│ CyberSentry — AI Threat Intelligence Analyst                      │
│ Mode: DEMO | Max CVEs: 10                                         │
╰──────────────────────────────────────────────────────────────────╯

Step 1: Ingesting CVE data...
  [NVD] Loaded 10 sample CVEs from sample_cves.json.

Step 2: Initialising RAG vector store...
  [ChromaDB] Created new collection 'threat_advisories'.
  [ChromaDB] Ingested 24 document sections from rag/threat_docs.

Step 3: Initialising threat analyst...
  Analyst ready (demo canned responses)

Step 4: Enriching 10 CVEs...
  Processing CVE-2024-21413...
  Processing CVE-2024-3400...
  [...]

                     CVE Risk Summary
┌──────────────────┬──────────┬──────┬────────────┬────────────────────────────┬────────────┐
│ CVE ID           │ Severity │ CVSS │ Risk Score │ MITRE Tactic               │ Due Date   │
├──────────────────┼──────────┼──────┼────────────┼────────────────────────────┼────────────┤
│ CVE-2024-3400    │ CRITICAL │ 10.0 │ 97.5       │ Initial Access             │ 2024-07-08 │
│ CVE-2024-1709    │ CRITICAL │ 10.0 │ 95.0       │ Persistence                │ 2024-07-08 │
│ CVE-2024-21413   │ CRITICAL │ 9.8  │ 91.2       │ Initial Access             │ 2024-07-08 │
│ CVE-2024-27198   │ CRITICAL │ 9.8  │ 88.4       │ Persistence                │ 2024-07-08 │
│ CVE-2024-28986   │ CRITICAL │ 9.8  │ 86.7       │ Execution                  │ 2024-07-08 │
│ CVE-2024-21762   │ CRITICAL │ 9.6  │ 85.1       │ Initial Access             │ 2024-07-08 │
│ CVE-2024-23897   │ CRITICAL │ 9.8  │ 83.6       │ Credential Access          │ 2024-07-08 │
│ CVE-2023-46805   │ HIGH     │ 8.2  │ 77.8       │ Initial Access             │ 2024-07-23 │
│ CVE-2024-20353   │ HIGH     │ 8.6  │ 74.2       │ Impact                     │ 2024-07-23 │
│ CVE-2023-44487   │ HIGH     │ 7.5  │ 62.5       │ Impact                     │ 2024-07-23 │
└──────────────────┴──────────┴──────┴────────────┴────────────────────────────┴────────────┘

╭─── 📄 Output Files ──────────────────────────────────────────────╮
│ ✓ Threat report: reports/threat_report.md                         │
│ ✓ POAM CSV:      reports/poam_entries.csv                         │
│ ✓ POAM JSON:     reports/poam_entries.json                        │
╰──────────────────────────────────────────────────────────────────╯
```

**POAM CSV sample (first 3 rows):**
```
CVE_ID,Severity,MITRE_Tactic,MITRE_Technique,Risk_Score,Recommended_Control,Due_Date,Owner
CVE-2024-3400,CRITICAL,Initial Access,T1190 - Exploit Public-Facing Application,97.5,"Apply vendor patch immediately; restrict external-facing service exposure; enforce MFA on all remote access points.",2024-07-08,Security Operations
CVE-2024-1709,CRITICAL,Persistence,T1136 - Create Account,95.0,"Apply ConnectWise ScreenConnect patch 23.9.8+; audit all admin accounts for unauthorised creation; rotate all credentials.",2024-07-08,Infrastructure Team
CVE-2024-21413,CRITICAL,Initial Access,T1566.002 - Spearphishing Link,91.2,"Apply Microsoft February 2024 CU; block UNC hyperlinks at email gateway; enable Extended Protection for Authentication.",2024-07-08,Infrastructure Team
```

---

## How This Demonstrates AI/ML Competency

- **RAG architecture implementation**: Demonstrates end-to-end Retrieval-Augmented Generation — document ingestion into ChromaDB, semantic retrieval, context augmentation, and LLM generation — the most widely deployed production AI pattern in enterprise security tooling.
- **LLM prompt engineering for structured output**: Uses carefully crafted system and user prompts to elicit consistent JSON-structured responses from Claude, a critical skill for production LLM deployments where downstream code must parse LLM output reliably.
- **Dual-mode design pattern**: The demo/live separation shows understanding of how to build AI systems that are reviewable and testable without API costs — essential for real-world team environments.
- **Domain-grounded AI**: Combines LLM capabilities with authoritative external data (CVSS scoring, MITRE ATT&CK taxonomy, NIST patch cadence) rather than relying solely on LLM knowledge — demonstrating responsible AI engineering.

---

## Future Enhancements

- **Real-time NVD streaming**: Webhook or polling integration for continuous CVE monitoring with alert on CVSS ≥ 9.0 discoveries
- **STIX/TAXII integration**: Ingest threat intelligence from commercial feeds (Recorded Future, VirusTotal) in STIX 2.1 format
- **Jira/ServiceNow POAM sync**: Auto-create POAM tickets in enterprise GRC platforms via API integration
- **Multi-LLM comparison**: A/B test MITRE mapping accuracy between Claude, GPT-4o, and Gemini to build an accuracy benchmark dataset
- **Graph-based attack path analysis**: Use NetworkX to model how chained CVEs create attack paths through the enterprise environment

---

## License

MIT License — see [LICENSE](../LICENSE) for details.
