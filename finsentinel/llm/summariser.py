"""LLM market briefing generator using Anthropic Claude.

Generates 2-sentence briefings per high-risk signal.
Falls back to template-based briefings in demo mode.
"""
from __future__ import annotations

import os
from typing import Any

from signals.risk_rules import RiskSignal

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

SYSTEM_PROMPT = """You are FinSentinel, an AI market intelligence assistant for financial risk management.
When presented with risk signals from NLP analysis of news articles, produce concise 2-sentence briefings.
Each briefing must: (1) state the nature and severity of the risk, and (2) suggest a concrete next step for a portfolio manager.
Be factual, professional, and actionable. Do not use emojis or markdown."""

BRIEFING_PROMPT = """Risk Signal Details:
- Rule: {rule}
- Ticker: {ticker}
- Severity: {severity}
- Summary: {message}
- Evidence headlines:
{headlines}

Generate a 2-sentence executive briefing for a portfolio manager."""


# ── Demo-mode template briefings ────────────────────────────────────────────
DEMO_BRIEFINGS = {
    "SENTIMENT_CRASH": (
        "A sharp deterioration in market sentiment has been detected for {ticker}, "
        "with the rolling 3-article sentiment score falling to critically negative territory. "
        "Portfolio managers should review position sizing and consider reducing exposure "
        "pending stabilisation of the news cycle."
    ),
    "REGULATORY_FLAG": (
        "Regulatory scrutiny has been identified for {ticker} based on negative sentiment "
        "in news articles classified as regulatory actions. "
        "Immediate review of compliance exposure and consultation with legal counsel is recommended."
    ),
    "CONCENTRATION_RISK": (
        "An unusual concentration of negative news coverage has been detected for {ticker} "
        "within the last hour, indicating potential emerging adverse developments. "
        "Monitor real-time feeds closely and assess whether stop-loss thresholds need adjustment."
    ),
}


class MarketBriefing:
    """Generates LLM briefings for risk signals."""

    def __init__(self, demo: bool = True):
        self.demo = demo
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return self._client

    def generate(self, signal: RiskSignal) -> str:
        """Generate a 2-sentence briefing for a risk signal."""
        if self.demo:
            return self._demo_briefing(signal)
        return self._live_briefing(signal)

    def _demo_briefing(self, signal: RiskSignal) -> str:
        template = DEMO_BRIEFINGS.get(signal.rule, DEMO_BRIEFINGS["SENTIMENT_CRASH"])
        return template.format(ticker=signal.ticker)

    def _live_briefing(self, signal: RiskSignal) -> str:
        headlines = "\n".join(
            f"  - {e.get('headline', e.get('title', 'Unknown headline'))}"
            for e in signal.evidence[:5]
        )
        prompt = BRIEFING_PROMPT.format(
            rule=signal.rule,
            ticker=signal.ticker,
            severity=signal.severity,
            message=signal.message,
            headlines=headlines or "  - (no headlines available)",
        )
        client = self._get_client()
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    def generate_batch(self, signals: list[RiskSignal]) -> list[dict[str, Any]]:
        """Generate briefings for a list of signals."""
        results = []
        for signal in signals:
            briefing = self.generate(signal)
            results.append(
                {
                    "rule": signal.rule,
                    "ticker": signal.ticker,
                    "severity": signal.severity,
                    "briefing": briefing,
                    "triggered_at": signal.triggered_at,
                }
            )
        return results
