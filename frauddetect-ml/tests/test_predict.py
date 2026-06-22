"""Tests for predict module (mocks model to avoid dependency on trained artifact)."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.predict import score_transaction, get_risk_label
from src.features import get_feature_matrix, engineer_features


SAMPLE_TRANSACTION = {
    "amount": 250.0,
    "merchant_category": "online",
    "card_present": 0,
    "hour_of_day": 3,
    "day_of_week": 5,
    "country_mismatch": 1,
    "previous_fraud_flag": 0,
}


def make_mock_model(proba: float = 0.85):
    """Create a mock XGBoost model returning a fixed fraud probability."""
    mock = MagicMock()
    mock.predict_proba.return_value = np.array([[1 - proba, proba]])
    return mock


def test_score_transaction_returns_required_keys():
    mock_model = make_mock_model(0.85)
    with patch("src.predict.load_model", return_value=mock_model):
        result = score_transaction(SAMPLE_TRANSACTION)
    assert "fraud_probability" in result
    assert "risk_level" in result
    assert "feature_row" in result


def test_high_risk_classification():
    mock_model = make_mock_model(0.80)
    with patch("src.predict.load_model", return_value=mock_model):
        result = score_transaction(SAMPLE_TRANSACTION)
    assert result["risk_level"] == "HIGH"


def test_medium_risk_classification():
    mock_model = make_mock_model(0.45)
    with patch("src.predict.load_model", return_value=mock_model):
        result = score_transaction(SAMPLE_TRANSACTION)
    assert result["risk_level"] == "MEDIUM"


def test_low_risk_classification():
    mock_model = make_mock_model(0.10)
    with patch("src.predict.load_model", return_value=mock_model):
        result = score_transaction(SAMPLE_TRANSACTION)
    assert result["risk_level"] == "LOW"


def test_probability_within_bounds():
    mock_model = make_mock_model(0.60)
    with patch("src.predict.load_model", return_value=mock_model):
        result = score_transaction(SAMPLE_TRANSACTION)
    assert 0.0 <= result["fraud_probability"] <= 1.0


def test_get_risk_label():
    assert "HIGH" in get_risk_label(0.80)
    assert "MEDIUM" in get_risk_label(0.50)
    assert "LOW" in get_risk_label(0.10)


if __name__ == "__main__":
    tests = [
        test_score_transaction_returns_required_keys,
        test_high_risk_classification,
        test_medium_risk_classification,
        test_low_risk_classification,
        test_probability_within_bounds,
        test_get_risk_label,
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
