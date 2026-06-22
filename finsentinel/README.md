# FinSentinel
### AI-Powered Financial News Sentiment & Risk Signal Monitor

---

## Overview

FinSentinel is a production-grade financial intelligence platform that ingests real-time news feeds, applies a multi-model NLP pipeline, and surfaces portfolio risk signals through an interactive Streamlit dashboard. It combines FinBERT financial sentiment classification, spaCy named entity recognition, zero-shot topic classification, and Anthropic Claude briefing generation to give portfolio managers AI-driven early-warning on market-moving events.

The system operates in **demo mode** (no API key, no model download required) using pre-computed sentiment from realistic synthetic news data, and in **live mode** where it downloads FinBERT (~440MB), the zero-shot classifier (~1.6GB), and calls the Anthropic API to generate real-time briefings.

---

## ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     FinSentinel Pipeline                        │
│                                                                  │
│  ┌──────────────┐    ┌────────────────────────────────────┐     │
│  │  News Feed   │───▶│         NLP Pipeline               │     │
│  │  (JSON/API)  │    │  ┌──────────────────────────────┐  │     │
│  └──────────────┘    │  │  FinBERT Sentiment Classifier │  │     │
│                       │  │  (ProsusAI/finbert)          │  │     │
│  ┌──────────────┐    │  └──────────────┬───────────────┘  │     │
│  │  Portfolio   │    │  ┌──────────────▼───────────────┐  │     │
│  │  Tickers     │    │  │  spaCy NER Extractor         │  │     │
│  │  (JSON)      │    │  │  (ORG, MONEY, GPE entities)  │  │     │
│  └──────┬───────┘    │  └──────────────┬───────────────┘  │     │
│         │             │  ┌──────────────▼───────────────┐  │     │
│         │             │  │  Zero-Shot Topic Classifier  │  │     │
│         │             │  │  (facebook/bart-large-mnli)  │  │     │
│         │             │  └──────────────┬───────────────┘  │     │
│         │             └─────────────────┼──────────────────┘     │
│         │                               │                         │
│         ▼                               ▼                         │
│  ┌──────────────────────────────────────────────────────┐        │
│  │                  Signal Engine                        │        │
│  │  SENTIMENT_CRASH   │  REGULATORY_FLAG   │  CONCENTRATION │     │
│  │  (rolling avg<-0.6)│  (topic+negative)  │  RISK (>3/1hr) │    │
│  └───────────────────────────────┬──────────────────────┘        │
│                                   │                               │
│         ┌─────────────────────────▼──────────────┐               │
│         │           Anthropic Claude              │               │
│         │        2-sentence LLM Briefings         │               │
│         └─────────────────────────┬──────────────┘               │
│                                   │                               │
│  ┌────────────────────────────────▼─────────────────────────┐    │
│  │              Streamlit Dashboard / CLI                     │    │
│  │    Sentiment Timeline · Risk Badges · Alert Log            │    │
│  └───────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **FinBERT Sentiment** — financial-domain BERT model for positive/negative/neutral classification with confidence scoring
- **spaCy NER** — extracts companies, monetary amounts, and geographic locations from news text
- **Zero-Shot Topic Classification** — categorises articles into earnings, regulatory action, macroeconomic, fraud allegation, or merger/acquisition without labelled training data
- **Three Risk Rules** — SENTIMENT_CRASH, REGULATORY_FLAG, and CONCENTRATION_RISK with configurable thresholds
- **Anthropic LLM Briefings** — 2-sentence executive briefings per high-risk signal via Claude
- **Streamlit Dashboard** — interactive ticker selector, sentiment timeline (Plotly), signal severity badges, and drill-down evidence
- **Demo Mode** — fully functional without any API key or model download using pre-computed synthetic data
- **Alert Logging** — structured JSON alerts to `sentinel_alerts.log`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Financial Sentiment | ProsusAI/finbert (HuggingFace transformers) |
| Named Entity Recognition | spaCy en_core_web_sm |
| Topic Classification | facebook/bart-large-mnli (zero-shot) |
| LLM Briefings | Anthropic Claude claude-3-5-haiku-20241022 |
| Dashboard | Streamlit 1.35 + Plotly 5.22 |
| Data | pandas 2.2, numpy 1.26 |
| Testing | pytest |

---

## Project Structure

```
finsentinel/
├── data/
│   ├── portfolio_tickers.json       # 10-ticker portfolio (ASX + NYSE)
│   ├── sample_news_feed.json        # 50 synthetic news articles
│   └── historical_sentiment.csv    # 30-day × 10-ticker sentiment history
├── nlp/
│   ├── sentiment_classifier.py      # FinBERT pipeline + demo fallback
│   ├── entity_extractor.py          # spaCy NER
│   └── topic_classifier.py          # Zero-shot ZSC + keyword fallback
├── signals/
│   ├── risk_rules.py                # SENTIMENT_CRASH, REGULATORY_FLAG, CONCENTRATION_RISK
│   ├── aggregator.py                # Orchestrates NLP + rule evaluation
│   └── alerter.py                   # Threshold alerting + log writer
├── llm/
│   └── summariser.py                # Anthropic Claude briefing generator
├── dashboard/
│   └── app.py                       # Streamlit dashboard
├── tests/
│   ├── test_sentiment_classifier.py # 8 unit tests
│   └── test_risk_rules.py           # 13 unit tests
├── main.py                          # CLI entry point
├── requirements.txt
└── .env.example
```

---

## Setup

```bash
# 1. Clone and enter project
cd ai-portfolio/finsentinel

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. (Optional) Set API key for live mode
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

> **Note:** In demo mode, FinBERT (~440MB) and the zero-shot model (~1.6GB) are NOT downloaded. They are only loaded in live mode (`--live`).

---

## Usage

**Demo mode (no downloads, no API key):**
```bash
python main.py --demo
```

**Live mode (downloads NLP models + calls Anthropic API):**
```bash
python main.py --live
```

**Verbose article detail:**
```bash
python main.py --demo --verbose
```

**Continuous monitor loop (60-second interval):**
```bash
python main.py --monitor --interval 60
```

**Streamlit dashboard:**
```bash
streamlit run dashboard/app.py
```

**Run tests:**
```bash
pytest tests/ -v
```

---

## Sample Output

```
╔══════════════════════════════════════════════════════╗
║  📡  FinSentinel — AI Financial Risk Monitor  v1.0  ║
╚══════════════════════════════════════════════════════╝

  [FinSentinel] Running in DEMO mode...
  Loaded 50 articles | 10 tickers

  Enriching articles (NLP pipeline)...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PORTFOLIO RISK SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Articles analysed :  50
  Signals triggered :   4
  Portfolio sentiment: -0.142

    🔴  CBA    HIGH
    🟡  NAB    MEDIUM
    🟢  AAPL   LOW
    🟢  MSFT   LOW
    ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔴 ALERT [HIGH] REGULATORY_FLAG — CBA: Regulatory scrutiny...
  🔴 ALERT [HIGH] SENTIMENT_CRASH — CBA: Rolling 3-article...
  🟡 ALERT [MEDIUM] CONCENTRATION_RISK — NAB: 4 negative articles...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AI BRIEFINGS (high-risk signals)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [CBA] REGULATORY_FLAG:
  Regulatory scrutiny has been identified for CBA based on negative
  sentiment in news articles classified as regulatory actions.
  Immediate review of compliance exposure and consultation with
  legal counsel is recommended.
```

---

## AI/ML Competency Demonstrated

| Competency | Implementation |
|---|---|
| Financial NLP | FinBERT domain-specific sentiment classification |
| Transfer Learning | Pre-trained transformer fine-tuned for finance |
| Zero-Shot Learning | Topic classification without domain-specific training data |
| Named Entity Recognition | spaCy pipeline for financial entity extraction |
| Signal Detection | Rule-based risk engine with configurable thresholds |
| LLM Integration | Structured Anthropic API prompting for executive briefings |
| Demo/Live Architecture | Pre-computed demo mode for instant runability |
| Streaming Data Pattern | Article feed enrichment with incremental aggregation |

---

## Future Enhancements

- **Live news ingestion** — integrate NewsAPI, Bloomberg, or financial RSS feeds
- **Portfolio P&L correlation** — map sentiment signals to actual price movements
- **Alerting integrations** — Slack/Teams webhooks for real-time signal notifications
- **Custom ticker portfolios** — multi-portfolio support with separate signal thresholds
- **Historical backtesting** — evaluate rule effectiveness against past market events
- **Fine-tuned ZSC model** — domain-specific zero-shot model on financial datasets

---

## License

MIT License — see [LICENSE](../LICENSE) for details.
