"""Tests for feature engineering."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.features import engineer_features, get_feature_matrix, FEATURE_COLS


def make_sample_df(n: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "transaction_id": [f"T{i}" for i in range(n)],
        "amount": rng.uniform(10, 2000, n),
        "merchant_category": rng.choice(["grocery", "online", "travel"], n),
        "card_present": rng.integers(0, 2, n),
        "hour_of_day": rng.integers(0, 24, n),
        "day_of_week": rng.integers(0, 7, n),
        "country_mismatch": rng.integers(0, 2, n),
        "previous_fraud_flag": rng.integers(0, 2, n),
        "is_fraud": rng.integers(0, 2, n),
    })


def test_engineer_features_adds_columns():
    df = make_sample_df()
    enriched = engineer_features(df)
    for col in ["amount_log", "is_night", "is_weekend", "merchant_risk_score",
                "amount_bucket", "no_card_high_amount", "mismatch_no_card"]:
        assert col in enriched.columns, f"Missing column: {col}"


def test_amount_log_is_positive():
    df = make_sample_df()
    enriched = engineer_features(df)
    assert (enriched["amount_log"] > 0).all()


def test_is_night_binary():
    df = make_sample_df()
    enriched = engineer_features(df)
    assert set(enriched["is_night"].unique()).issubset({0, 1})


def test_is_weekend_binary():
    df = make_sample_df()
    enriched = engineer_features(df)
    assert set(enriched["is_weekend"].unique()).issubset({0, 1})


def test_get_feature_matrix_correct_columns():
    df = make_sample_df()
    X = get_feature_matrix(df)
    assert list(X.columns) == FEATURE_COLS


def test_no_card_high_amount_logic():
    df = pd.DataFrame({
        "transaction_id": ["T0"],
        "amount": [300.0],
        "merchant_category": ["online"],
        "card_present": [0],  # No card
        "hour_of_day": [12],
        "day_of_week": [1],
        "country_mismatch": [0],
        "previous_fraud_flag": [0],
        "is_fraud": [0],
    })
    enriched = engineer_features(df)
    assert enriched["no_card_high_amount"].iloc[0] == 1


def test_feature_matrix_no_nulls():
    df = make_sample_df(100)
    X = get_feature_matrix(df)
    assert not X.isnull().any().any(), "Feature matrix should have no null values"


if __name__ == "__main__":
    tests = [
        test_engineer_features_adds_columns,
        test_amount_log_is_positive,
        test_is_night_binary,
        test_is_weekend_binary,
        test_get_feature_matrix_correct_columns,
        test_no_card_high_amount_logic,
        test_feature_matrix_no_nulls,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
