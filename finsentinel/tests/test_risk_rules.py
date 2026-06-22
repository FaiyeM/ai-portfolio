"""Tests for signals/risk_rules.py."""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from signals.risk_rules import (
    check_sentiment_crash,
    check_regulatory_flag,
    check_concentration_risk,
    SENTIMENT_CRASH_THRESHOLD,
    SENTIMENT_CRASH_WINDOW,
    CONCENTRATION_RISK_MIN_ARTICLES,
)


def _make_article(ticker="CBA", sentiment="negative", sentiment_score=-0.8,
                  topic="macroeconomic", article_type="macro",
                  published_at=None, headline="Test headline"):
    if published_at is None:
        published_at = datetime.now(timezone.utc).isoformat()
    return {
        "ticker": ticker,
        "sentiment_label": sentiment,
        "sentiment_score": sentiment_score,
        "topic": topic,
        "article_type": article_type,
        "published_at": published_at,
        "headline": headline,
    }


class TestSentimentCrash:
    def test_triggers_when_rolling_avg_below_threshold(self):
        articles = [_make_article(sentiment_score=-0.8) for _ in range(3)]
        signal = check_sentiment_crash(articles, "CBA")
        assert signal is not None
        assert signal.rule == "SENTIMENT_CRASH"
        assert signal.ticker == "CBA"
        assert signal.severity == "HIGH"

    def test_no_trigger_above_threshold(self):
        articles = [_make_article(sentiment_score=0.3) for _ in range(3)]
        signal = check_sentiment_crash(articles, "CBA")
        assert signal is None

    def test_insufficient_articles_returns_none(self):
        articles = [_make_article(sentiment_score=-0.9) for _ in range(SENTIMENT_CRASH_WINDOW - 1)]
        signal = check_sentiment_crash(articles, "CBA")
        assert signal is None

    def test_only_considers_target_ticker(self):
        # 3 very negative articles for NAB, not for CBA
        articles = [_make_article(ticker="NAB", sentiment_score=-0.9) for _ in range(3)]
        signal = check_sentiment_crash(articles, "CBA")
        assert signal is None

    def test_uses_rolling_window(self):
        # 2 positive + 3 very negative = crash signal
        articles = (
            [_make_article(sentiment_score=0.9) for _ in range(2)]
            + [_make_article(sentiment_score=-0.85) for _ in range(3)]
        )
        signal = check_sentiment_crash(articles, "CBA")
        assert signal is not None


class TestRegulatoryFlag:
    def test_triggers_on_regulatory_negative(self):
        article = _make_article(sentiment="negative", topic="regulatory action")
        signal = check_regulatory_flag(article)
        assert signal is not None
        assert signal.rule == "REGULATORY_FLAG"
        assert signal.severity == "HIGH"

    def test_no_trigger_regulatory_positive(self):
        article = _make_article(sentiment="positive", topic="regulatory action")
        signal = check_regulatory_flag(article)
        assert signal is None

    def test_no_trigger_non_regulatory_negative(self):
        article = _make_article(sentiment="negative", topic="earnings")
        signal = check_regulatory_flag(article)
        assert signal is None

    def test_no_trigger_neutral_regulatory(self):
        article = _make_article(sentiment="neutral", topic="regulatory action")
        signal = check_regulatory_flag(article)
        assert signal is None


class TestConcentrationRisk:
    def _recent_ts(self, minutes_ago: int = 10) -> str:
        t = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        return t.isoformat()

    def test_triggers_when_exceeds_threshold(self):
        articles = [
            _make_article(ticker="CBA", sentiment="negative", published_at=self._recent_ts(i * 5))
            for i in range(CONCENTRATION_RISK_MIN_ARTICLES + 1)
        ]
        signal = check_concentration_risk(articles, "CBA")
        assert signal is not None
        assert signal.rule == "CONCENTRATION_RISK"
        assert signal.severity == "MEDIUM"

    def test_no_trigger_at_threshold(self):
        articles = [
            _make_article(ticker="CBA", sentiment="negative", published_at=self._recent_ts(i * 5))
            for i in range(CONCENTRATION_RISK_MIN_ARTICLES)
        ]
        signal = check_concentration_risk(articles, "CBA")
        assert signal is None

    def test_old_articles_ignored(self):
        # Articles older than window hours should not count
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        articles = [
            _make_article(ticker="CBA", sentiment="negative", published_at=old_ts)
            for _ in range(CONCENTRATION_RISK_MIN_ARTICLES + 2)
        ]
        signal = check_concentration_risk(articles, "CBA")
        assert signal is None

    def test_only_counts_negative_articles(self):
        articles = [
            _make_article(ticker="CBA", sentiment="positive", published_at=self._recent_ts(i))
            for i in range(CONCENTRATION_RISK_MIN_ARTICLES + 2)
        ]
        signal = check_concentration_risk(articles, "CBA")
        assert signal is None
