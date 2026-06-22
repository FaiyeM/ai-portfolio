"""XGBoost fraud detection model training.

Run: python src/train.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.features import engineer_features, get_feature_matrix, FEATURE_COLS

DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic_transactions.csv"
MODEL_PATH = Path(__file__).parent.parent / "models" / "fraud_model.pkl"
MODEL_META_PATH = Path(__file__).parent.parent / "models" / "model_meta.pkl"


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load and prepare training data."""
    df = pd.read_csv(DATA_PATH)
    X = get_feature_matrix(df)
    y = df["is_fraud"]
    return X, y


def train_model(X: pd.DataFrame, y: pd.Series) -> tuple[xgb.XGBClassifier, dict]:
    """Train XGBoost model with imbalance handling."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Class imbalance weight
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / max(pos_count, 1)

    print(f"  Training set: {len(X_train)} samples | "
          f"Fraud rate: {y_train.mean():.1%} | "
          f"scale_pos_weight: {scale_pos_weight:.1f}")

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Cross-validation AUC
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    print(f"  CV ROC-AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    meta = {
        "feature_cols": FEATURE_COLS,
        "scale_pos_weight": scale_pos_weight,
        "cv_roc_auc_mean": float(cv_scores.mean()),
        "cv_roc_auc_std": float(cv_scores.std()),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "X_test": X_test,
        "y_test": y_test,
    }

    return model, meta


def save_model(model, meta: dict) -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    meta_save = {k: v for k, v in meta.items() if k not in ("X_test", "y_test")}
    joblib.dump(meta_save, MODEL_META_PATH)
    print(f"  Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    print("Loading data...")
    X, y = load_data()
    print(f"  Dataset: {len(X)} rows | Features: {len(FEATURE_COLS)}")

    print("Training model...")
    model, meta = train_model(X, y)

    print("Saving model...")
    save_model(model, meta)

    # Quick evaluate on test set
    from src.evaluate import evaluate_model
    evaluate_model(model, meta["X_test"], meta["y_test"])
