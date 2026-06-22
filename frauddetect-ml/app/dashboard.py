"""FraudDetect ML — Streamlit dashboard.

Run: streamlit run app/dashboard.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="FraudDetect ML",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 FraudDetect ML")
st.caption("Explainable fraud detection — XGBoost + SHAP")

# ─── Load model ──────────────────────────────────────────────────────── #
@st.cache_resource(show_spinner="Loading fraud detection model...")
def load_model_cached():
    from src.predict import load_model
    return load_model()

try:
    model = load_model_cached()
    model_loaded = True
except FileNotFoundError:
    st.error("Model not found. Run `python src/train.py` first.")
    model_loaded = False
    st.stop()

from src.features import FEATURE_COLS, engineer_features
from src.predict import score_transaction, get_risk_label
from src.explainer import get_shap_explainer, explain_prediction

# ─── Sidebar — transaction input ─────────────────────────────────────── #
st.sidebar.header("🏧 Transaction Details")

amount = st.sidebar.slider("Amount ($)", min_value=1.0, max_value=5000.0, value=150.0, step=10.0)
merchant_category = st.sidebar.selectbox(
    "Merchant Category",
    ["grocery", "restaurant", "retail", "travel", "online", "entertainment", "fuel", "healthcare"],
    index=4,  # Default: online
)
card_present = st.sidebar.radio("Card Present?", ["Yes", "No"], index=1)
hour_of_day = st.sidebar.slider("Hour of Day", 0, 23, 3, help="0=midnight, 12=noon")
day_of_week = st.sidebar.slider("Day of Week", 0, 6, 5, help="0=Mon, 6=Sun")
country_mismatch = st.sidebar.checkbox("Country Mismatch", value=True)
previous_fraud_flag = st.sidebar.checkbox("Previous Fraud on Account", value=False)

score_btn = st.sidebar.button("🔍 Score Transaction", type="primary", use_container_width=True)

# ─── Pre-built example transactions ──────────────────────────────────── #
st.subheader("📋 Example Transactions")
examples = {
    "Suspicious (online, night, mismatch)": {
        "amount": 892.50,
        "merchant_category": "online",
        "card_present": 0,
        "hour_of_day": 3,
        "day_of_week": 5,
        "country_mismatch": 1,
        "previous_fraud_flag": 1,
    },
    "Legitimate (grocery, morning)": {
        "amount": 47.30,
        "merchant_category": "grocery",
        "card_present": 1,
        "hour_of_day": 10,
        "day_of_week": 1,
        "country_mismatch": 0,
        "previous_fraud_flag": 0,
    },
    "Borderline (travel, high amount)": {
        "amount": 1200.0,
        "merchant_category": "travel",
        "card_present": 0,
        "hour_of_day": 14,
        "day_of_week": 3,
        "country_mismatch": 0,
        "previous_fraud_flag": 0,
    },
}

col1, col2, col3 = st.columns(3)
selected_example = None
for col, (name, txn) in zip([col1, col2, col3], examples.items()):
    if col.button(name, use_container_width=True):
        selected_example = txn

# ─── Build transaction dict ───────────────────────────────────────────── #
if selected_example:
    transaction = selected_example
else:
    transaction = {
        "amount": amount,
        "merchant_category": merchant_category,
        "card_present": 1 if card_present == "Yes" else 0,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "country_mismatch": int(country_mismatch),
        "previous_fraud_flag": int(previous_fraud_flag),
    }

# ─── Score and display ────────────────────────────────────────────────── #
if score_btn or selected_example:
    result = score_transaction(transaction)
    proba = result["fraud_probability"]
    risk = result["risk_level"]
    features = result["feature_row"]

    st.subheader("📊 Scoring Result")

    col1, col2, col3 = st.columns(3)
    col1.metric("Fraud Probability", f"{proba:.1%}")
    col2.metric("Risk Level", get_risk_label(proba))
    col3.metric("Amount", f"${transaction['amount']:.2f}")

    # SHAP explanation
    st.subheader("🔬 SHAP Explanation")
    try:
        explanation = explain_prediction(model, features, FEATURE_COLS)

        st.write("**Top 3 contributing features:**")
        for feat in explanation["top_features"]:
            direction = "⬆️" if feat["shap_value"] > 0 else "⬇️"
            st.write(
                f"{direction} **{feat['feature']}** = `{feat['value']:.3f}` "
                f"(SHAP: {feat['shap_value']:+.4f} — {feat['direction']} fraud risk)"
            )

        # Waterfall plot
        from src.explainer import plot_waterfall
        fig = plot_waterfall(model, features, FEATURE_COLS)
        st.pyplot(fig)
        plt.close("all")

    except Exception as e:
        st.info(f"SHAP plot not available in this environment: {e}")

    # Feature values table
    with st.expander("📋 All Feature Values"):
        display_df = features.T.reset_index()
        display_df.columns = ["Feature", "Value"]
        st.dataframe(display_df, use_container_width=True)

st.divider()
st.caption("FraudDetect ML | XGBoost + SHAP | Synthetic training data")
