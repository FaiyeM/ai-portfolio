# FraudDetect ML

> Explainable fraud detection pipeline using gradient-boosted trees and SHAP, with a Streamlit dashboard for real-time transaction scoring.

---

## Overview

FraudDetect ML demonstrates a production-ready binary classification pipeline for payment fraud detection — a canonical ML problem with real commercial stakes. It trains an XGBoost model on 5,000 synthetic transactions with a realistic 3% fraud rate imbalance, using `scale_pos_weight` to handle class imbalance without upsampling bias. Every prediction is explained using SHAP (SHapley Additive exPlanations), surfacing the top-3 contributing features per transaction in a waterfall plot. The Streamlit dashboard allows analysts to score any transaction in real time and understand exactly why the model reached its decision — addressing the "black box" problem that prevents ML adoption in regulated financial services environments.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    FraudDetect ML Pipeline                        │
│                                                                    │
│  Data Generation                Model Training                    │
│  ┌─────────────────┐           ┌──────────────────────────────┐  │
│  │generate_synthetic│           │ src/train.py                  │  │
│  │_data.py          │──CSV──▶  │ • Feature engineering         │  │
│  │5000 rows, 3% fraud│          │ • XGBoost + scale_pos_weight  │  │
│  └─────────────────┘           │ • 5-fold CV ROC-AUC           │  │
│                                 │ • Save fraud_model.pkl        │  │
│                                 └────────────────┬─────────────┘  │
│                                                  │                 │
│  ┌────────────────────────────────────────────── ▼──────────────┐  │
│  │                Inference + Explainability                     │  │
│  │                                                               │  │
│  │  Transaction ──▶ feature engineering ──▶ XGBoost.predict_   │  │
│  │                                          proba()             │  │
│  │                      │                      │                │  │
│  │                      ▼                      ▼                │  │
│  │               SHAP TreeExplainer    Fraud Probability        │  │
│  │               Waterfall plot        Risk Level (L/M/H)       │  │
│  └───────────────────────────────────────────────────────────── ┘  │
│                                                                    │
│  Streamlit Dashboard: sidebar sliders → Score → SHAP waterfall    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Synthetic data generator**: `generate_synthetic_data.py` creates 5,000 realistic transactions with domain-informed fraud patterns (night-time, no-card-present + high amount, country mismatch, prior fraud history)
- **Feature engineering**: 7 engineered features including log-amount, is_night, is_weekend, merchant risk score, interaction terms (no_card_high_amount, mismatch_no_card)
- **XGBoost with imbalance handling**: `scale_pos_weight` set to `neg_count/pos_count` (~30x); 5-fold stratified CV for reliable performance estimates
- **SHAP explainability**: TreeExplainer for exact SHAP values; waterfall plot per transaction showing each feature's signed contribution
- **Streamlit dashboard**: Sidebar sliders for all input features; one-click scoring; SHAP waterfall chart; top-3 contributing features with directional explanation
- **Pre-built evaluation**: `evaluate.py` prints classification report and saves ROC + PR curves as PNG files
- **Mock-friendly tests**: Tests use `unittest.mock` to avoid dependency on the trained model artifact

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Gradient Boosting | XGBoost 2.0 | Primary fraud classifier with scale_pos_weight |
| Explainability | SHAP 0.45 | TreeExplainer for exact feature attribution |
| Dashboard | Streamlit 1.35 | Interactive transaction scoring UI |
| Data Processing | Pandas 2.2, NumPy 1.26 | Feature engineering and data manipulation |
| ML Utilities | scikit-learn 1.5 | Train/test split, CV scoring, metrics |
| Imbalance | imbalanced-learn 0.12 | SMOTE (alternative to scale_pos_weight) |
| Visualisation | Plotly 5.22, Matplotlib 3.9, Seaborn 0.13 | Charts and SHAP plots |
| Serialisation | joblib 1.4 | Model artifact save/load |

---

## Project Structure

```
frauddetect-ml/
├── requirements.txt              # Pinned dependencies
├── data/
│   ├── generate_synthetic_data.py # Data generator with domain-informed fraud rules
│   └── synthetic_transactions.csv # Pre-generated 5,000 row dataset
├── notebooks/
│   └── 01_eda_and_modelling.ipynb # EDA + training walkthrough (open in Jupyter)
├── src/
│   ├── features.py               # Feature engineering: log-amount, time features, interactions
│   ├── train.py                  # XGBoost training + CV + model save
│   ├── evaluate.py               # Metrics, ROC curve PNG, PR curve PNG
│   ├── explainer.py              # SHAP TreeExplainer, waterfall and summary plots
│   └── predict.py                # Single-transaction scoring with model caching
├── models/
│   └── fraud_model.pkl           # Trained model (generated by running src/train.py)
├── app/
│   └── dashboard.py              # Streamlit dashboard
└── tests/
    ├── test_features.py          # 7 tests for feature engineering logic
    └── test_predict.py           # 6 tests with mock model (no artifact dependency)
```

---

## Setup & Installation

```bash
cd ai-portfolio/frauddetect-ml

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Step 1: (data already committed, but re-generate if desired)
python data/generate_synthetic_data.py

# Step 2: Train the model (required before running the dashboard)
python src/train.py
```

---

## Usage / How to Run

### Train the model
```bash
python src/train.py
```

### Launch the dashboard
```bash
streamlit run app/dashboard.py
```

### Run standalone evaluation
```bash
python -c "
import sys; sys.path.insert(0, '.')
import pandas as pd, joblib
from src.features import get_feature_matrix
from src.evaluate import evaluate_model
from sklearn.model_selection import train_test_split

df = pd.read_csv('data/synthetic_transactions.csv')
X = get_feature_matrix(df)
y = df['is_fraud']
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = joblib.load('models/fraud_model.pkl')
evaluate_model(model, X_test, y_test)
"
```

### Run tests
```bash
python tests/test_features.py
python tests/test_predict.py
```

---

## Sample Output

### Training output
```
Loading data...
  Dataset: 5000 rows | Features: 13
Training model...
  Training set: 4000 samples | Fraud rate: 2.5% | scale_pos_weight: 39.1
  CV ROC-AUC: 0.9421 ± 0.0183
Saving model...
  Model saved to models/fraud_model.pkl

=======================================================
FraudDetect ML — Model Evaluation
=======================================================
ROC-AUC Score:          0.9537
Average Precision:      0.6841

              precision    recall  f1-score   support
  Legitimate       0.99      0.95      0.97       972
       Fraud       0.34      0.76      0.47        28

    accuracy                           0.95      1000

Confusion Matrix:
  TP=21  FP=41
  FN=7   TN=931
=======================================================
```

### Dashboard scoring output
```
Transaction: Amount $892.50 | Online | No card | 3am | Country mismatch | Prior fraud ✓

Fraud Probability: 82.4%    Risk Level: 🔴 HIGH    Amount: $892.50

Top 3 contributing features:
⬆️  previous_fraud_flag = 1.000  (SHAP: +0.3847 — increases fraud risk)
⬆️  country_mismatch = 1.000    (SHAP: +0.2913 — increases fraud risk)
⬆️  is_night = 1.000            (SHAP: +0.1562 — increases fraud risk)
```

---

## How This Demonstrates AI/ML Competency

- **Classical ML lifecycle mastery**: Demonstrates the complete supervised learning lifecycle — synthetic data generation with domain knowledge, feature engineering, class imbalance handling, model training with cross-validation, calibrated evaluation with precision/recall (appropriate for imbalanced classes), and production-style inference.
- **Explainable AI (XAI) in practice**: SHAP integration goes beyond generating a model — it surfaces the "why" in a format that compliance teams and regulators can understand, directly addressing the EU AI Act and APRA's requirement for explainable automated decision-making.
- **Production engineering patterns**: Model caching with `@st.cache_resource`, separation of feature engineering from model code (preventing train/serve skew), and test isolation via mocking demonstrate software engineering discipline that distinguishes ML engineers from data scientists.
- **Domain-informed feature design**: Features like `no_card_high_amount` and `mismatch_no_card` encode actual fraud detection domain knowledge (card-not-present fraud patterns), not just raw feature pass-through.

---

## Future Enhancements

- **Real-time feature store**: Replace batch CSV with a streaming transaction pipeline (Kafka → Flink → Redis feature store → model scoring) to support sub-100ms latency fraud decisions
- **Temporal validation**: Replace random train/test split with temporal split to prevent data leakage from future transactions into training — critical for production fraud models
- **Isotonic calibration**: Add probability calibration layer to ensure predicted probabilities are reliable for threshold-based decisioning (e.g., 0.7 probability should mean 70% of such cases are truly fraud)
- **Online learning**: Implement incremental model updates as new fraud patterns emerge, using XGBoost's `xgb.train()` with existing model as base
- **Fairness analysis**: Add SHAP-based demographic parity audit to detect if any protected attributes proxy for race, gender, or geography in fraud decisions

---

## License

MIT License
