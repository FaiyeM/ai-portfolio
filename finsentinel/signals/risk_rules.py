"""Risk signal rules for FinSentinel.

Rules:
  SENTIMENT_CRASH    — 3-article rolling average sentiment drops below -0.6
  REGULATORY_FLAG    — topic == 'regulatory action' AND sentiment == 'negative'
  CONCENTRATION_RISK — >3 negative articles hit the same ticker within 1 hour
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── Rule thresholds ──────────────────────────────────────────────────────────
SENTIMENT_CRASH_THRESHOLD = -0.6
SENTIMENT_CRASH_WINDOW = 3          # rolling articles
CONCENTRATION_RISK_WINDOW_HOURS = 1
CONCENTRATION_RISK_MIN_ARTICLES = 3


@dataclass
class RiskSignal:
    rule: str          # SENTIMENT_CRASH | REGULATORY_FLAG | CONCENTRATION_RISK
    ticker: str
    severity: str      # HIGH | MEDIUM | LOW
    message: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    triggered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def check_sentiment_crash(articles: list[dict[str, Any]], ticker: str) -> RiskSignal | None:
    """Detect SENTIMENT_CRASH: rolling avg of last N articles < threshold.

    Args:
        articles: list of article dicts with 'sentiment_score' key, sorted oldest-first
        ticker:   the ticker being assessed
    """
    ticker_articles = [a for a in articles if a.get("ticker") == ticker]
    if len(ticker_articles) < SENTIMENT_CRASH_WINDOW:
        return None

    window = ticker_articles[-SENTIMENT_CRASH_WINDOW:]
    scores = [float(a.get("sentiment_score", 0.0)) for a in window]
    rolling_avg = sum(scores) / len(scores)

    if rolling_avg < SENTIMENT_CRASH_THRESHOLD:
        return RiskSignal(
            rule="SENTIMENT_CRASH",
            ticker=ticker,
            severity="HIGH",
            message=(
                f"Rolling {SENTIMENT_CRASH_WINDOW}-article sentiment for {ticker} is "
                f"{rolling_avg:.3f} (threshold {SENTIMENT_CRASH_THRESHOLD})"
            ),
            evidence=window,
        )
    return None


def check_regulatory_flag(article: dict[str, Any]) -> RiskSignal | None:
    """Detect REGULATORY_FLAG: topic == 'regulatory action' AND negative sentiment."""
    topic = article.get("topic", "")
    sentiment = article.get("sentiment_label", article.get("sentiment", ""))
    ticker = article.get("ticker", "UNKNOWN")

    if topic == "regulatory action" and sentiment == "negative":
        return RiskSignal(
            rule="REGULATORY_FLAG",
            ticker=ticker,
            severity="HIGH",
            message=(
                f"Regulatory action detected for {ticker}: "
                f"\"{article.get('headline', article.get('title', ''))[:80]}\""
            ),
            evidence=[article],
        )
    return None


def check_concentration_risk(
    articles: list[dict[str, Any]],
    ticker: str,
    reference_time: datetime | None = None,
) -> RiskSignal | None:
    """Detect CONCENTRATION_RISK: >N negative articles for same ticker within window.

    Args:
        articles:       all articles with 'published_at' and 'ticker' keys
        ticker:         the ticker being assessed
        reference_time: window end (default: now UTC)
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    cutoff_ts = reference_time.timestamp() - CONCENTRATION_RISK_WINDOW_HOURS * 3600

    recent_negative = [
        a for a in articles
        if a.get("ticker") == ticker
        and (a.get("sentiment_label", a.get("sentiment", "")) == "negative")
        and _parse_ts(a.get("published_at", "")) >= cutoff_ts
    ]

    if len(recent_negative) > CONCENTRATION_RISK_MIN_ARTICLES:
        return RiskSignal(
            rule="CONCENTRATION_RISK",
            ticker=ticker,
            severity="MEDIUM",
            message=(
                f"{len(recent_negative)} negative articles for {ticker} "
                f"in the last {CONCENTRATION_RISK_WINDOW_HOURS}h "
                f"(threshold >{CONCENTRATION_RISK_MIN_ARTICLES})"
            ),
            evidence=recent_negative,
        )
    return None


def _parse_ts(ts_str: str) -> float:
    """Parse ISO-8601 timestamp to unix float; return 0.0 on failure."""
    if not ts_str:
        return 0.0
    try:
        # Handle both 'Z' suffix and '+00:00'
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str).timestamp()
    except ValueError:
        return 0.0
