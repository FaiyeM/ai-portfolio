"""Feature engineering for fraud detection.

Transforms raw transaction data into model-ready features.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


MERCHANT_RISK = {
    "online": 3,
    "travel": 3,
    "entertainment": 2,
    "retail": 1,
    "restaurant": 1,
    "grocery": 0,
    "fuel": 0,
    "healthcare": 0,
}

FEATURE_COLS = [
    "amount",
    "card_present",
    "hour_of_day",
    "day_of_week",
    "country_mismatch",
    "previous_fraud_flag",
    "amount_log",
    "is_night",
    "is_weekend",
    "merchant_risk_score",
    "amount_bucket",
    "no_card_high_amount",
    "mismatch_no_card",
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering transformations to transaction DataFrame.

    Returns a copy with additional engineered features.
    """
    df = df.copy()

    # Log-transform amount (reduces skewness)
    df["amount_log"] = np.log1p(df["amount"])

    # Time-based features
    df["is_night"] = ((df["hour_of_day"] >= 22) | (df["hour_of_day"] <= 5)).astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Merchant risk encoding
    df["merchant_risk_score"] = df["merchant_category"].map(MERCHANT_RISK).fillna(1)

    # Amount buckets (0=low<50, 1=mid 50-500, 2=high>500)
    df["amount_bucket"] = pd.cut(
        df["amount"],
        bins=[0, 50, 500, float("inf")],
        labels=[0, 1, 2],
    ).astype(int)

    # Interaction features
    df["no_card_high_amount"] = ((df["card_present"] == 0) & (df["amount"] > 200)).astype(int)
    df["mismatch_no_card"] = ((df["country_mismatch"] == 1) & (df["card_present"] == 0)).astype(int)

    return df


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the model feature columns from a DataFrame."""
    df = engineer_features(df)
    return df[FEATURE_COLS]


def get_feature_names() -> list[str]:
    """Return ordered feature names used by the model."""
    return FEATURE_COLS
