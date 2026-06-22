"""FinSentinel — CLI entry point.

Usage:
    python main.py --demo           # Single-run demo (no API key, no model download)
    python main.py --live           # Single-run with FinBERT + ZSC + Claude
    python main.py --monitor        # Continuous monitor loop (demo mode)
    streamlit run dashboard/app.py  # Interactive dashboard
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def load_news() -> list[dict]:
    with open(ROOT / "data" / "sample_news_feed.json") as f:
        return json.load(f)


def load_tickers() -> list[str]:
    with open(ROOT / "data" / "portfolio_tickers.json") as f:
        return [t["ticker"] for t in json.load(f)]


def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════╗
║  📡  FinSentinel — AI Financial Risk Monitor  v1.0  ║
╚══════════════════════════════════════════════════════╝
""")


def run_once(demo: bool = True, verbose: bool = False) -> None:
    """Run the full pipeline once and print results."""
    from signals.aggregator import aggregate_signals
    from signals.alerter import process_signals, summarise_alerts
    from llm.summariser import MarketBriefing

    mode_label = "DEMO" if demo else "LIVE"
    print(f"  [FinSentinel] Running in {mode_label} mode...")

    news = load_news()
    tickers = load_tickers()
    print(f"  Loaded {len(news)} articles | {len(tickers)} tickers")

    print("  Enriching articles (NLP pipeline)...")
    results = aggregate_signals(news, tickers, demo=demo)

    enriched = results["enriched_articles"]
    signals = results["signals"]
    summary = results["summary"]
    risk_by_ticker = results["risk_by_ticker"]

    # ── Summary table ──────────────────────────────────────────────────────
    print()
    print("━" * 60)
    print("  PORTFOLIO RISK SNAPSHOT")
    print("━" * 60)
    print(f"  Articles analysed : {summary['total_articles']}")
    print(f"  Signals triggered : {summary['total_signals']}")
    print(f"  Portfolio sentiment: {summary['portfolio_avg_sentiment']:+.3f}")
    print()

    for ticker, risk in risk_by_ticker.items():
        icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "⚪")
        print(f"    {icon}  {ticker:<6} {risk}")

    print()

    # ── Alerts ─────────────────────────────────────────────────────────────
    if signals:
        print("━" * 60)
        print("  RISK SIGNALS")
        print("━" * 60)
        alerts = process_signals(signals, console=True)
        print()
        print(summarise_alerts(alerts))

        # LLM briefings for HIGH signals
        high_signals = [s for s in signals if s.severity == "HIGH"]
        if high_signals:
            print()
            print("━" * 60)
            print("  AI BRIEFINGS (high-risk signals)")
            print("━" * 60)
            briefer = MarketBriefing(demo=demo)
            briefings = briefer.generate_batch(high_signals)
            for b in briefings:
                print(f"\n  [{b['ticker']}] {b['rule']}:")
                print(f"  {b['briefing']}")
    else:
        print("  ✅ No risk signals triggered.")

    if verbose:
        print()
        print("━" * 60)
        print("  ENRICHED ARTICLES (first 5)")
        print("━" * 60)
        for art in enriched[:5]:
            print(
                f"  {art.get('ticker','?'):5} | {art.get('sentiment_label','?'):8} "
                f"({art.get('sentiment_score',0):+.2f}) | {art.get('topic','?'):20} | "
                f"{art.get('headline', art.get('title',''))[:60]}"
            )


def run_monitor(interval: int = 60, demo: bool = True) -> None:
    """Continuous monitoring loop."""
    print(f"  Monitoring every {interval}s (Ctrl+C to stop)...")
    try:
        while True:
            run_once(demo=demo)
            print(f"\n  Next check in {interval}s...\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Monitoring stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FinSentinel — AI financial news risk monitor"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="Single run in demo mode (no API key)")
    group.add_argument("--live", action="store_true", help="Single run with live NLP + LLM")
    group.add_argument("--monitor", action="store_true", help="Continuous monitor loop (demo)")
    parser.add_argument("--interval", type=int, default=60, help="Monitor interval in seconds (default: 60)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show enriched article details")

    args = parser.parse_args()
    print_banner()

    if args.demo:
        run_once(demo=True, verbose=args.verbose)
    elif args.live:
        run_once(demo=False, verbose=args.verbose)
    elif args.monitor:
        run_monitor(interval=args.interval, demo=True)


if __name__ == "__main__":
    main()
