"""
Phase 5 — Predictive Modeling
Logistic Regression as primary model: split -> encode -> scale -> train -> evaluate.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix, classification_report)

TARGET = "loan_status"

# Core features chosen from EDA + engineered features (Phase 3 & 4 findings)
NUMERIC_FEATURES = [
    "person_age", "person_income", "person_emp_length", "loan_amnt",
    "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length",
    "debt_to_income_ratio"
]
CATEGORICAL_FEATURES = [
    "person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"
]
# Note: flag_prior_default duplicates cb_person_default_on_file (one-hot),
# and flag_renter duplicates person_home_ownership_RENT (one-hot) — excluded
# from the model matrix to avoid perfect collinearity, though both flags are
# retained elsewhere (Phase 7/8) for rule-based scoring/decisioning logic.
FLAG_FEATURES = ["flag_high_loan_burden", "flag_low_income_high_grade_risk"]


def load_processed(path="data/processed/credit_risk_clean.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def build_model_frame(df: pd.DataFrame):
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + FLAG_FEATURES].copy()
    y = df[TARGET].copy()
    X_encoded = pd.get_dummies(X, columns=CATEGORICAL_FEATURES, drop_first=True)
    return X_encoded, y


def train_and_evaluate(X, y, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Non-Default", "Default"])

    return {
        "model": model, "scaler": scaler,
        "X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test,
        "y_pred": y_pred, "y_proba": y_proba,
        "metrics": metrics, "confusion_matrix": cm, "classification_report": report,
        "feature_names": list(X.columns),
    }


def interpret_coefficients(model, feature_names, scaler):
    """Business-readable coefficient interpretation (standardized scale)."""
    coefs = pd.DataFrame({
        "feature": feature_names,
        "coefficient": model.coef_[0]
    }).sort_values("coefficient", ascending=False)
    coefs["direction"] = np.where(coefs["coefficient"] > 0, "Increases Default Risk", "Decreases Default Risk")
    coefs["abs_impact"] = coefs["coefficient"].abs()
    return coefs.sort_values("abs_impact", ascending=False).drop(columns="abs_impact")


if __name__ == "__main__":
    df = load_processed()
    X, y = build_model_frame(df)
    print("Model matrix shape:", X.shape)

    results = train_and_evaluate(X, y)

    print("\n=== METRICS ===")
    for k, v in results["metrics"].items():
        print(f"{k}: {v:.4f}")

    print("\n=== CONFUSION MATRIX ===")
    print(results["confusion_matrix"])

    print("\n=== CLASSIFICATION REPORT ===")
    print(results["classification_report"])

    coefs = interpret_coefficients(results["model"], results["feature_names"], results["scaler"])
    print("\n=== TOP 10 RISK-INCREASING FACTORS ===")
    print(coefs[coefs.coefficient > 0].head(10).to_string(index=False))
    print("\n=== TOP 10 RISK-DECREASING FACTORS ===")
    print(coefs[coefs.coefficient < 0].head(10).to_string(index=False))

    # Persist artifacts for later phases
    joblib.dump(results["model"], "models/logistic_regression_model.pkl")
    joblib.dump(results["scaler"], "models/scaler.pkl")
    joblib.dump(results["feature_names"], "models/feature_names.pkl")
    coefs.to_csv("reports/business/model_coefficients.csv", index=False)
    print("\nModel, scaler, and coefficients saved.")
