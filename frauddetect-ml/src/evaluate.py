"""Model evaluation — metrics, ROC curve, confusion matrix."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
)

OUTPUT_DIR = Path(__file__).parent.parent / "models"


def evaluate_model(model, X_test, y_test) -> dict:
    """Evaluate model and print formatted metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_proba)
    avg_precision = average_precision_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Legitimate", "Fraud"])

    print("\n" + "=" * 55)
    print("FraudDetect ML — Model Evaluation")
    print("=" * 55)
    print(f"ROC-AUC Score:          {roc_auc:.4f}")
    print(f"Average Precision:      {avg_precision:.4f}")
    print()
    print(report)
    print(f"Confusion Matrix:")
    print(f"  TP={cm[1,1]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TN={cm[0,0]}")
    print("=" * 55)

    _save_roc_curve(y_test, y_proba, roc_auc)
    _save_pr_curve(y_test, y_proba, avg_precision)

    return {
        "roc_auc": roc_auc,
        "avg_precision": avg_precision,
        "confusion_matrix": cm,
    }


def _save_roc_curve(y_test, y_proba, roc_auc: float) -> None:
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(fpr, tpr, color="#e74c3c", lw=2, label=f"ROC Curve (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Fraud Detection — ROC Curve")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = OUTPUT_DIR / "roc_curve.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f"  ROC curve saved to {path}")


def _save_pr_curve(y_test, y_proba, avg_precision: float) -> None:
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(recall, precision, color="#3498db", lw=2, label=f"PR Curve (AP = {avg_precision:.4f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Fraud Detection — Precision-Recall Curve")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = OUTPUT_DIR / "pr_curve.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
