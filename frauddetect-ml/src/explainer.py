"""SHAP explainability for fraud predictions."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

MODELS_DIR = Path(__file__).parent.parent / "models"


def get_shap_explainer(model):
    """Create a SHAP TreeExplainer for the XGBoost model."""
    return shap.TreeExplainer(model)


def explain_prediction(model, X_single: pd.DataFrame, feature_names: list[str]) -> dict:
    """Compute SHAP values for a single prediction.

    Returns:
        dict with shap_values, base_value, top_features
    """
    explainer = get_shap_explainer(model)
    shap_values = explainer.shap_values(X_single)

    # shap_values shape: (1, n_features)
    sv = shap_values[0] if isinstance(shap_values, list) else shap_values[0]

    top_idx = np.argsort(np.abs(sv))[::-1][:3]
    top_features = [
        {
            "feature": feature_names[i],
            "value": float(X_single.iloc[0, i]),
            "shap_value": float(sv[i]),
            "direction": "increases" if sv[i] > 0 else "decreases",
        }
        for i in top_idx
    ]

    return {
        "shap_values": sv,
        "base_value": float(explainer.expected_value),
        "top_features": top_features,
    }


def plot_waterfall(model, X_single: pd.DataFrame, feature_names: list[str]) -> plt.Figure:
    """Generate a SHAP waterfall plot for a single transaction."""
    explainer = get_shap_explainer(model)
    explanation = shap.Explanation(
        values=explainer.shap_values(X_single)[0] if isinstance(explainer.shap_values(X_single), list)
               else explainer.shap_values(X_single)[0],
        base_values=explainer.expected_value,
        data=X_single.values[0],
        feature_names=feature_names,
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    shap.plots.waterfall(explanation, max_display=10, show=False)
    fig = plt.gcf()
    fig.tight_layout()
    return fig


def plot_summary(model, X: pd.DataFrame, feature_names: list[str]) -> plt.Figure:
    """Generate a SHAP summary beeswarm plot over a dataset sample."""
    explainer = get_shap_explainer(model)
    sample = X.sample(min(500, len(X)), random_state=42)
    shap_vals = explainer.shap_values(sample)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals

    fig, ax = plt.subplots(figsize=(9, 6))
    shap.summary_plot(shap_vals, sample, feature_names=feature_names, show=False)
    fig = plt.gcf()
    fig.tight_layout()
    return fig
