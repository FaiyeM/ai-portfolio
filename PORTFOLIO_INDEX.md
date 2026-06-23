### 6 Production-Grade Projects

---

## Projects

| # | Project | Domain | Key Technologies | Demo Mode |
|---|---------|--------|-----------------|-----------|
| 1 | [CyberSentry](#1-cybersentry) | Cybersecurity / GRC | Anthropic SDK, ChromaDB RAG, MITRE ATT&CK, CVSS | ✅ |
| 2 | [ComplianceRAG](#2-compliancerag) | Regulatory Compliance | FAISS RAG, Sentence-Transformers, Streamlit, APRA/ISO/SOC2 | ✅ |
| 3 | [FraudDetect ML](#3-frauddetect-ml) | Financial Fraud Detection | XGBoost, SHAP, Streamlit, imbalanced-learn | ✅ |
| 4 | [EnterpriseBridge AI](#4-enterprisebridge-ai) | Enterprise Integration | Anthropic tool_use agentic loop, FastAPI, Mock Jira/ServiceNow/Slack | ✅ |
| 5 | [VendorRisk AI](#5-vendorrisk-ai) | Third-Party Risk | Anthropic SDK, ReportLab PDF, domain-weighted scoring | ✅ |
| 6 | [FinSentinel](#6-finsentinel) | Financial Intelligence | FinBERT, spaCy NER, Zero-Shot ZSC, Anthropic Claude | ✅ |

---

## 1. CyberSentry

**Directory:** `cybersentry/`

Automated CVE ingestion pipeline that maps vulnerabilities to MITRE ATT&CK tactics, computes composite risk scores, and generates POAM (Plan of Action and Milestones) documents using a ChromaDB RAG knowledge base and Anthropic Claude analysis.

**Quick start:**
```bash
cd cybersentry
pip install -r requirements.txt
python main.py --demo
```

**Highlights:**
- NVD API client with 10-CVE sample fallback (CVE-2024-21413, CVE-2024-3400, etc.)
- ChromaDB vector store with 3 threat advisory documents
- MITRE ATT&CK keyword-to-tactic mapping (all 10 tactics)
- Composite risk score: CVSS (60%) + asset criticality (40%) × exploitation multiplier
- POAM output: CSV + JSON with due dates, owners, remediation steps
- Rich terminal table output

---

## 2. ComplianceRAG

**Directory:** `compliance-rag/`

Retrieval-Augmented Generation system over APRA CPS 234, ISO 27001:2022, and SOC 2 Trust Service Criteria. Features a Streamlit Q&A interface, FAISS cosine-similarity retrieval, and a built-in evaluation harness with precision@k scoring.

**Quick start:**
```bash
cd compliance-rag
pip install -r requirements.txt
streamlit run app.py
```

**Highlights:**
- FAISS IndexFlatIP with normalised embeddings (cosine similarity)
- all-MiniLM-L6-v2 sentence-transformer embeddings
- 3 regulatory frameworks with markdown section chunking
- Framework-filtered retrieval
- 10-question eval suite with precision@k and framework accuracy metrics
- Demo answers for 3 canonical questions (no API key needed)

---

## 3. FraudDetect ML

**Directory:** `frauddetect-ml/`

End-to-end ML pipeline for financial transaction fraud detection. Generates 5000 synthetic transactions with domain-informed fraud rules, trains an XGBoost classifier with class-imbalance handling, and provides SHAP waterfall explanations per prediction via a Streamlit dashboard.

**Quick start:**
```bash
cd frauddetect-ml
pip install -r requirements.txt
python data/generate_synthetic_data.py   # already generated
python src/train.py                       # trains + saves model
streamlit run app/dashboard.py
```

**Highlights:**
- 7 engineered features: amount_log, is_night, merchant_risk_score, no_card_high_amount, etc.
- XGBoost with StratifiedKFold CV and scale_pos_weight for 97:3 class imbalance
- SHAP TreeExplainer for per-prediction waterfall charts
- ROC-AUC, average precision, confusion matrix evaluation
- Streamlit sidebar with transaction sliders for live scoring

> **Note:** Run `python src/train.py` before launching the dashboard to generate `models/fraud_model.pkl`.

---

## 4. EnterpriseBridge AI

**Directory:** `enterprise-bridge-ai/`

Agentic middleware that accepts natural-language enterprise commands and orchestrates tool calls against mock Jira, ServiceNow, and Slack connectors using Anthropic's native `tool_use` API. Exposes a FastAPI REST server alongside the CLI.

**Quick start:**
```bash
cd enterprise-bridge-ai
pip install -r requirements.txt
python main.py --demo "Create a P1 incident for the payment gateway outage"
python main.py --server   # FastAPI on http://localhost:8000
```

**Highlights:**
- Full Anthropic `tool_use` agentic loop (multi-turn `tool_result → continue`)
- 5 enterprise tools: create_ticket, query_ticket_status, send_slack_notification, escalate_incident, summarise_open_incidents
- BaseConnector ABC with pre-seeded mock tickets (PAY-1042, INFRA-891, SEC-234)
- Thread-safe in-memory ContextStore with RLock
- FastAPI with POST /command, GET /health, GET /demo endpoints
- Connector call audit log to `connector_calls.log`

---

## 5. VendorRisk AI

**Directory:** `vendorrisk-ai/`

LLM-powered vendor security questionnaire scoring platform. Evaluates vendor responses across 5 weighted risk domains, computes an overall risk tier, and generates a polished PDF report with embedded radar chart using ReportLab.

**Quick start:**
```bash
cd vendorrisk-ai
pip install -r requirements.txt
python main.py --vendor acme --demo
python main.py --vendor finco --demo   # HIGH risk example
```

**Highlights:**
- 14-question default questionnaire + 25-question financial sector questionnaire
- Domain-weighted scoring: Data Security (30%), BC/DR (25%), Third-Party (15%), Compliance (15%), IR (15%)
- LLM scoring: 0-10 per question with rationale + risk flags
- ReportLab PDF: cover page, executive summary, domain scores table, radar chart, remediation plan
- ACME (LOW risk) and FinCo (HIGH risk) sample vendor responses
- Financial sector weights variant for APRA-regulated environments

---

## 6. FinSentinel

**Directory:** `finsentinel/`

AI-powered financial news intelligence platform. Ingests news feeds, applies a three-stage NLP pipeline (FinBERT sentiment → spaCy NER → zero-shot topic classification), evaluates three risk rules, and generates Anthropic Claude executive briefings for high-risk signals via an interactive Streamlit dashboard.

**Quick start:**
```bash
cd finsentinel
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py --demo
streamlit run dashboard/app.py
```

**Highlights:**
- 50-article synthetic news feed · 30-day × 10-ticker sentiment history
- FinBERT (ProsusAI/finbert) for financial-domain sentiment
- spaCy en_core_web_sm for ORG/MONEY/GPE entity extraction
- facebook/bart-large-mnli zero-shot topic classification (5 labels)
- Three risk rules: SENTIMENT_CRASH, REGULATORY_FLAG, CONCENTRATION_RISK
- Claude claude-3-5-haiku-20241022 for 2-sentence executive briefings
- Plotly sentiment timeline with crash threshold annotation
- Structured JSON alert log (`sentinel_alerts.log`)

---

## Technical Themes

### RAG & Vector Search
CyberSentry (ChromaDB) and ComplianceRAG (FAISS) both demonstrate retrieval-augmented generation with sentence-transformer embeddings. ComplianceRAG uses IndexFlatIP with L2-normalised vectors for cosine similarity; CyberSentry uses ChromaDB's PersistentClient with cosine distance.

### Agentic Tool Use
EnterpriseBridge AI implements the full Anthropic `tool_use` agentic loop pattern — receiving `tool_use` blocks from the model, executing the corresponding Python function, and returning `tool_result` blocks in a subsequent turn until the model responds with a final text message. No LangChain dependency.

### ML Explainability
FraudDetect ML pairs XGBoost gradient boosting with SHAP TreeExplainer to provide per-prediction waterfall explanations. This addresses the "black box" criticism of ensemble models in regulated financial contexts.

### Multi-Model NLP Pipelines
FinSentinel chains three independent models — FinBERT (fine-tuned BERT), spaCy (statistical NER), and BART-large-MNLI (zero-shot NLI) — in a single enrichment pass, demonstrating practical multi-model orchestration.

### Demo/Live Architecture
All six projects implement a consistent dual-mode pattern: demo mode uses pre-computed responses, canned data, or keyword matching so every project runs instantly without API keys or large model downloads. Live mode activates the full AI stack.

### Structured LLM Output
CyberSentry, VendorRisk AI, and FinSentinel all prompt Claude to return structured JSON (scores, rationale, risk flags, MITRE mappings) and parse the responses programmatically — demonstrating production-safe LLM output handling.

---

## How to Run Each Project

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-portfolio

# ── Project 1: CyberSentry ──────────────────────────────────────────
cd cybersentry && pip install -r requirements.txt
python main.py --demo
cd ..

# ── Project 2: ComplianceRAG ────────────────────────────────────────
cd compliance-rag && pip install -r requirements.txt
streamlit run app.py          # or: python -c "from rag.vector_store import build_index; build_index()"
cd ..

# ── Project 3: FraudDetect ML ───────────────────────────────────────
cd frauddetect-ml && pip install -r requirements.txt
python src/train.py           # trains model (required once)
streamlit run app/dashboard.py
cd ..

# ── Project 4: EnterpriseBridge AI ──────────────────────────────────
cd enterprise-bridge-ai && pip install -r requirements.txt
python main.py --demo-all     # runs 3 demo commands
cd ..

# ── Project 5: VendorRisk AI ────────────────────────────────────────
cd vendorrisk-ai && pip install -r requirements.txt
python main.py --vendor acme --demo
python main.py --vendor finco --demo
cd ..

# ── Project 6: FinSentinel ──────────────────────────────────────────
cd finsentinel && pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py --demo
streamlit run dashboard/app.py
cd ..
```

**For live mode** (any project), copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`, then replace `--demo` with `--live`.

---

## Repository Structure

```
ai-portfolio/
├── PORTFOLIO_INDEX.md          ← this file
├── LICENSE                     ← MIT
├── cybersentry/                ← Project 1
├── compliance-rag/             ← Project 2
├── frauddetect-ml/             ← Project 3
├── enterprise-bridge-ai/       ← Project 4
├── vendorrisk-ai/              ← Project 5
└── finsentinel/                ← Project 6
```

---

## AI/ML Competencies Demonstrated

| Competency | Projects |
|---|---|
| Retrieval-Augmented Generation (RAG) | CyberSentry, ComplianceRAG |
| Agentic tool_use loops | EnterpriseBridge AI |
| Financial NLP (domain-tuned BERT) | FinSentinel |
| Zero-shot classification | FinSentinel |
| Named entity recognition | FinSentinel |
| Gradient boosting + explainability (SHAP) | FraudDetect ML |
| Structured LLM output / JSON prompting | CyberSentry, VendorRisk AI, FinSentinel |
| Vector similarity search | CyberSentry, ComplianceRAG |
| Risk scoring & aggregation | VendorRisk AI, CyberSentry |
| REST API design (FastAPI) | EnterpriseBridge AI |
| PDF report generation | VendorRisk AI |
| Streamlit dashboards | ComplianceRAG, FraudDetect ML, FinSentinel |
| Demo/live dual-mode architecture | All 6 projects |

---

## License

All projects are released under the [MIT License](LICENSE).
