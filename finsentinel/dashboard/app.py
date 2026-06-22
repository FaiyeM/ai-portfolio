"""FinSentinel Streamlit Dashboard.

Run:
    streamlit run dashboard/app.py

Features:
  - Ticker selector
  - Date range slider
  - Sentiment timeline (Plotly)
  - Signal severity badges
  - Top-5 recent news headlines
  - LLM briefing for high-risk signals
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSentinel — Portfolio Risk Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data loading ─────────────────────────────────────────────────────────────
DATA_DIR = ROOT / "data"


@st.cache_data
def load_tickers() -> list[dict]:
    with open(DATA_DIR / "portfolio_tickers.json") as f:
        return json.load(f)


@st.cache_data
def load_historical_sentiment() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "historical_sentiment.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_news() -> list[dict]:
    with open(DATA_DIR / "sample_news_feed.json") as f:
        return json.load(f)


@st.cache_data
def run_pipeline(demo: bool = True) -> dict:
    """Run the full NLP + signals pipeline (cached)."""
    from signals.aggregator import aggregate_signals

    news = load_news()
    tickers_data = load_tickers()
    tickers = [t["ticker"] for t in tickers_data]
    return aggregate_signals(news, tickers, demo=demo)


# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.shields.io/badge/FinSentinel-v1.0-blue", width=200)
st.sidebar.title("⚙️ Configuration")

demo_mode = st.sidebar.toggle("Demo Mode (no API key required)", value=True)

tickers_data = load_tickers()
ticker_options = [t["ticker"] for t in tickers_data]
selected_tickers = st.sidebar.multiselect(
    "Portfolio Tickers", ticker_options, default=ticker_options[:5]
)

hist_df = load_historical_sentiment()
min_date = hist_df["date"].min().date()
max_date = hist_df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(max_date - timedelta(days=14), max_date),
    min_value=min_date,
    max_value=max_date,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Mode:** " + ("🟢 Demo (pre-computed)" if demo_mode else "🔵 Live (FinBERT + ZSC)")
)

# ── Main header ──────────────────────────────────────────────────────────────
st.title("📡 FinSentinel — Portfolio Risk Monitor")
st.caption("AI-powered financial news sentiment analysis & risk signal detection")

# ── Run pipeline ─────────────────────────────────────────────────────────────
with st.spinner("Analysing news feed..."):
    pipeline_results = run_pipeline(demo=demo_mode)

signals = pipeline_results["signals"]
enriched_articles = pipeline_results["enriched_articles"]
risk_by_ticker = pipeline_results["risk_by_ticker"]
summary = pipeline_results["summary"]

# ── Top-row KPI metrics ──────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Articles Analysed", summary["total_articles"])
col2.metric("Active Signals", summary["total_signals"])
col3.metric(
    "Portfolio Sentiment",
    f"{summary['portfolio_avg_sentiment']:.3f}",
    delta_color="normal",
)
col4.metric("High-Risk Tickers", len(summary["high_risk_tickers"]))

st.markdown("---")

# ── Sentiment timeline ────────────────────────────────────────────────────────
st.subheader("📈 Sentiment Timeline")

# Filter historical data
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_hist = hist_df[
    (hist_df["date"].dt.date >= start_date)
    & (hist_df["date"].dt.date <= end_date)
    & (hist_df["ticker"].isin(selected_tickers))
]

if not filtered_hist.empty:
    fig = go.Figure()
    for ticker in selected_tickers:
        t_data = filtered_hist[filtered_hist["ticker"] == ticker]
        if not t_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=t_data["date"],
                    y=t_data["sentiment_score"],
                    name=ticker,
                    mode="lines+markers",
                    marker=dict(size=5),
                )
            )
    fig.add_hline(y=-0.6, line_dash="dash", line_color="red", annotation_text="Crash threshold")
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(
        height=350,
        yaxis_title="Sentiment Score",
        xaxis_title="Date",
        legend_title="Ticker",
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for selected tickers / date range.")

st.markdown("---")

# ── Risk signals ─────────────────────────────────────────────────────────────
st.subheader("🚨 Active Risk Signals")

if not signals:
    st.success("No risk signals triggered on current news feed.")
else:
    for sig in signals:
        severity_colour = "red" if sig.severity == "HIGH" else "orange"
        severity_icon = "🔴" if sig.severity == "HIGH" else "🟡"

        with st.expander(
            f"{severity_icon} **{sig.rule}** — {sig.ticker} [{sig.severity}]",
            expanded=(sig.severity == "HIGH"),
        ):
            st.markdown(f"**Message:** {sig.message}")
            st.markdown(f"**Triggered at:** {sig.triggered_at[:19].replace('T', ' ')} UTC")

            if sig.evidence:
                st.markdown("**Evidence headlines:**")
                for ev in sig.evidence[:3]:
                    headline = ev.get("headline", ev.get("title", ""))
                    st.markdown(f"  - {headline}")

            # LLM briefing button
            briefing_key = f"briefing_{sig.ticker}_{sig.rule}"
            if st.button(f"Generate LLM Briefing", key=briefing_key):
                from llm.summariser import MarketBriefing
                briefer = MarketBriefing(demo=demo_mode)
                with st.spinner("Generating briefing..."):
                    briefing_text = briefer.generate(sig)
                st.info(f"💬 **AI Briefing:** {briefing_text}")

st.markdown("---")

# ── Ticker risk overview ──────────────────────────────────────────────────────
st.subheader("🗂 Portfolio Risk Overview")

risk_colour = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

risk_rows = []
for t in tickers_data:
    if t["ticker"] in selected_tickers:
        risk = risk_by_ticker.get(t["ticker"], "LOW")
        risk_rows.append(
            {
                "Ticker": t["ticker"],
                "Name": t["name"],
                "Sector": t["sector"],
                "Weight": f"{t['weight']*100:.0f}%",
                "Risk": f"{risk_colour.get(risk, '🟢')} {risk}",
            }
        )

if risk_rows:
    st.dataframe(pd.DataFrame(risk_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# ── Top 5 recent news ─────────────────────────────────────────────────────────
st.subheader("📰 Top-5 Recent Articles")

filtered_articles = [
    a for a in enriched_articles if a.get("ticker") in selected_tickers
][:5]

for art in filtered_articles:
    ticker = art.get("ticker", "N/A")
    headline = art.get("headline", art.get("title", "No headline"))
    sentiment = art.get("sentiment_label", "neutral")
    topic = art.get("topic", "unknown")
    score = art.get("sentiment_score", 0.0)

    sent_colour = {"positive": "green", "negative": "red", "neutral": "gray"}.get(
        sentiment, "gray"
    )
    st.markdown(
        f"**[{ticker}]** {headline}  "
        f"&nbsp;&nbsp; `{topic}` &nbsp;&nbsp; :{sent_colour}[{sentiment} ({score:+.2f})]"
    )

st.markdown("---")
st.caption("FinSentinel v1.0 | Built with FinBERT · spaCy · Anthropic Claude · Streamlit")
