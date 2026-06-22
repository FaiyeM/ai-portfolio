"""Single-transaction scoring function."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.features import engineer_features, FEATURE_COLS

MODEL_PATH = Path(__file__).parent.parent / "models" / "fraud_model.pkl"

_model_cache = None


def load_model():
    global _model_cache
    if _model_cache is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run: python src/train.py"
            )
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def score_transaction(transaction: dict[str, Any]) -> dict[str, Any]:
    """Score a single transaction for fraud probability.

    Args:
        transaction: Dict with keys: amount, merchant_category, card_present,
                     hour_of_day, day_of_week, country_mismatch, previous_fraud_flag

    Returns:
        Dict with fraud_probability, risk_level, feature_row
    """
    model = load_model()

    # Build a single-row DataFrame
    df = pd.DataFrame([transaction])
    features = engineer_features(df)[FEATURE_COLS]

    proba = float(model.predict_proba(features)[0, 1])

    if proba >= 0.7:
        risk_level = "HIGH"
    elif proba >= 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "fraud_probability": round(proba, 4),
        "risk_level": risk_level,
        "feature_row": features,
    }


def get_risk_label(proba: float) -> str:
    if proba >= 0.7:
        return "🔴 HIGH"
    elif proba >= 0.3:
        return "🟡 MEDIUM"
    return "🟢 LOW"
