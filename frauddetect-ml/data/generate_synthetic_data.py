#!/usr/bin/env python3
"""Generate synthetic transaction data for FraudDetect ML.

Produces synthetic_transactions.csv with realistic fraud patterns.
Run: python data/generate_synthetic_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
N_TRANSACTIONS = 5000
FRAUD_RATE = 0.03  # 3% fraud rate

OUTPUT_PATH = Path(__file__).parent / "synthetic_transactions.csv"


def generate(n: int = N_TRANSACTIONS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ── Timestamps ──────────────────────────────────────────────── #
    base_date = pd.Timestamp("2024-01-01")
    timestamps = [
        base_date + pd.Timedelta(seconds=int(s))
        for s in rng.integers(0, 365 * 24 * 3600, size=n)
    ]
    timestamps = sorted(timestamps)

    df = pd.DataFrame({"timestamp": timestamps})
    df["transaction_id"] = [f"TXN{str(i).zfill(7)}" for i in range(n)]

    # ── Time features ────────────────────────────────────────────── #
    df["hour_of_day"] = df["timestamp"].apply(lambda t: t.hour)
    df["day_of_week"] = df["timestamp"].apply(lambda t: t.weekday())  # 0=Mon, 6=Sun

    # ── Merchant category ────────────────────────────────────────── #
    categories = ["grocery", "restaurant", "retail", "travel", "online", "entertainment", "fuel", "healthcare"]
    cat_weights = [0.25, 0.18, 0.20, 0.08, 0.15, 0.05, 0.06, 0.03]
    df["merchant_category"] = rng.choice(categories, size=n, p=cat_weights)

    # ── Amount (log-normal, realistic distribution) ──────────────── #
    df["amount"] = np.round(np.exp(rng.normal(loc=3.5, scale=1.2, size=n)), 2)
    df["amount"] = df["amount"].clip(0.50, 15000.0)

    # ── Card present ────────────────────────────────────────────── #
    df["card_present"] = rng.choice([1, 0], size=n, p=[0.65, 0.35])

    # ── Country mismatch (card registered country != merchant country) ─ #
    df["country_mismatch"] = rng.choice([0, 1], size=n, p=[0.92, 0.08])

    # ── Previous fraud flag on account ─────────────────────────── #
    df["previous_fraud_flag"] = rng.choice([0, 1], size=n, p=[0.95, 0.05])

    # ── Fraud label ─────────────────────────────────────────────── #
    # Fraud is more likely when:
    # - card not present (online) + high amount
    # - country mismatch
    # - unusual hour (2am–5am)
    # - previous fraud flag on account

    fraud_prob = np.full(n, 0.005)
    fraud_prob[df["card_present"] == 0] += 0.02
    fraud_prob[df["amount"] > 500] += 0.02
    fraud_prob[df["country_mismatch"] == 1] += 0.04
    fraud_prob[df["previous_fraud_flag"] == 1] += 0.05
    fraud_prob[(df["hour_of_day"] >= 2) & (df["hour_of_day"] <= 5)] += 0.03
    fraud_prob[df["merchant_category"] == "online"] += 0.01
    fraud_prob[df["merchant_category"] == "travel"] += 0.01

    fraud_prob = np.clip(fraud_prob, 0, 0.90)
    df["is_fraud"] = rng.binomial(1, fraud_prob).astype(int)

    # Ensure target fraud rate by adjusting
    current_rate = df["is_fraud"].mean()
    if current_rate < FRAUD_RATE * 0.7:
        extra_idx = rng.choice(df[df["is_fraud"] == 0].index, size=int(n * FRAUD_RATE * 0.3), replace=False)
        df.loc[extra_idx, "is_fraud"] = 1

    # ── Column ordering ──────────────────────────────────────────── #
    cols = [
        "transaction_id", "timestamp", "amount", "merchant_category",
        "card_present", "hour_of_day", "day_of_week", "country_mismatch",
        "previous_fraud_flag", "is_fraud",
    ]
    df = df[cols]

    return df


if __name__ == "__main__":
    df = generate()
    df.to_csv(OUTPUT_PATH, index=False)

    fraud_count = df["is_fraud"].sum()
    total = len(df)
    print(f"Generated {total} transactions | Fraud: {fraud_count} ({fraud_count/total:.1%})")
    print(f"Saved to: {OUTPUT_PATH}")
    print(df.head(5).to_string())
