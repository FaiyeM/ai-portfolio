"""Aggregate NLP scores and risk rules into per-asset risk signals."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from signals.risk_rules import (
    RiskSignal,
    check_concentration_risk,
    check_regulatory_flag,
    check_sentiment_crash,
)


def enrich_article(article: dict[str, Any], demo: bool = True) -> dict[str, Any]:
    """Run NLP pipeline on a single article and add derived fields.

    In demo mode uses pre-computed sentiment / article_type from sample data.
    In live mode runs FinBERT + spaCy + zero-shot classifier.
    """
    from nlp.sentiment_classifier import sentiment_from_precomputed, classify_sentiment
    from nlp.entity_extractor import extract_entities
    from nlp.topic_classifier import classify_topic_keywords, classify_topic_live

    text = article.get("content", article.get("headline", ""))

    if demo:
        # Use pre-computed fields embedded in sample data
        sentiment = sentiment_from_precomputed(article.get("sentiment_score", 0.0))
        topic_result = classify_topic_keywords(
            text, article_type=article.get("article_type")
        )
    else:
        sentiment = classify_sentiment(text)
        topic_result = classify_topic_live(text)

    entities = extract_entities(text)

    enriched = dict(article)
    enriched.update(
        {
            "sentiment_label": sentiment["label"],
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_confidence": sentiment["confidence"],
            "topic": topic_result["topic"],
            "topic_confidence": topic_result["confidence"],
            "entities": entities,
        }
    )
    return enriched


def aggregate_signals(
    articles: list[dict[str, Any]],
    tickers: list[str],
    demo: bool = True,
    reference_time: datetime | None = None,
) -> dict[str, Any]:
    """Run all enrichment + rule evaluation across the article feed.

    Returns:
        {
            "enriched_articles": [...],
            "signals": [RiskSignal, ...],
            "risk_by_ticker": {"CBA": "HIGH", ...},
            "summary": {...}
        }
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    # Step 1: Enrich articles
    enriched = [enrich_article(a, demo=demo) for a in articles]

    # Step 2: Evaluate rules
    signals: list[RiskSignal] = []

    for article in enriched:
        reg_signal = check_regulatory_flag(article)
        if reg_signal:
            signals.append(reg_signal)

    for ticker in tickers:
        crash_signal = check_sentiment_crash(enriched, ticker)
        if crash_signal:
            signals.append(crash_signal)

        conc_signal = check_concentration_risk(enriched, ticker, reference_time)
        if conc_signal:
            signals.append(conc_signal)

    # Step 3: Aggregate risk tier per ticker
    severity_rank = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}
    risk_by_ticker: dict[str, str] = {t: "LOW" for t in tickers}
    for sig in signals:
        current = risk_by_ticker.get(sig.ticker, "LOW")
        if severity_rank.get(sig.severity, 0) > severity_rank.get(current, 0):
            risk_by_ticker[sig.ticker] = sig.severity

    # Step 4: Build summary
    avg_sentiment = (
        sum(a.get("sentiment_score", 0.0) for a in enriched) / len(enriched)
        if enriched
        else 0.0
    )
    summary = {
        "total_articles": len(enriched),
        "total_signals": len(signals),
        "high_risk_tickers": [t for t, r in risk_by_ticker.items() if r == "HIGH"],
        "medium_risk_tickers": [t for t, r in risk_by_ticker.items() if r == "MEDIUM"],
        "portfolio_avg_sentiment": round(avg_sentiment, 4),
        "evaluated_at": reference_time.isoformat(),
    }

    return {
        "enriched_articles": enriched,
        "signals": signals,
        "risk_by_ticker": risk_by_ticker,
        "summary": summary,
    }
