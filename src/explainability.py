"""
Phase 6 — Explainable AI
Provides global feature importance (standardized logistic coefficients) and
borrower-level natural-language explanations for individual predictions.
"""

import pandas as pd
import numpy as np
import joblib
from modeling import load_processed, build_model_frame, interpret_coefficients


def load_artifacts():
    model = joblib.load("models/logistic_regression_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    return model, scaler, feature_names


def global_feature_importance(model, feature_names, top_n=10):
    """Absolute standardized coefficient magnitude = global importance ranking."""
    coefs = pd.DataFrame({"feature": feature_names, "coefficient": model.coef_[0]})
    coefs["abs_importance"] = coefs["coefficient"].abs()
    coefs = coefs.sort_values("abs_importance", ascending=False)
    coefs["direction"] = np.where(coefs["coefficient"] > 0, "risk-increasing", "risk-decreasing")
    return coefs.head(top_n)[["feature", "coefficient", "direction"]]


def explain_borrower(row: pd.Series, model, scaler, feature_names, top_n=3) -> dict:
    """
    Generate a borrower-level explanation for one row of the model matrix
    (already one-hot encoded, matching feature_names).
    """
    x = row[feature_names].values.reshape(1, -1).astype(float)
    x_scaled = scaler.transform(x)

    proba = model.predict_proba(x_scaled)[0, 1]
    pred = int(proba >= 0.5)

    # Contribution of each feature = standardized_value * coefficient
    contributions = x_scaled[0] * model.coef_[0]
    contrib_df = pd.DataFrame({
        "feature": feature_names,
        "contribution": contributions
    }).sort_values("contribution", ascending=False)

    top_risk_factors = contrib_df[contrib_df.contribution > 0].head(top_n)
    top_protective_factors = contrib_df[contrib_df.contribution < 0].head(top_n)

    def humanize(feat):
        return feat.replace("_", " ").replace("person ", "").replace("loan ", "loan ").title()

    risk_reasons = [f"{humanize(f)}" for f in top_risk_factors["feature"]]
    protective_reasons = [f"{humanize(f)}" for f in top_protective_factors["feature"]]

    explanation = {
        "default_probability": round(float(proba), 4),
        "predicted_class": "Default" if pred == 1 else "Non-Default",
        "top_risk_factors": risk_reasons,
        "top_protective_factors": protective_reasons,
    }

    if risk_reasons:
        narrative = f"This applicant is {'high' if proba >= 0.5 else 'moderate'} risk primarily because of: " \
                    f"{', '.join(risk_reasons)}."
    else:
        narrative = "This applicant shows no dominant risk-increasing factors."
    explanation["narrative"] = narrative

    return explanation


if __name__ == "__main__":
    model, scaler, feature_names = load_artifacts()

    print("=== GLOBAL FEATURE IMPORTANCE (Top 10) ===")
    importance = global_feature_importance(model, feature_names)
    print(importance.to_string(index=False))

    # Demonstrate borrower-level explanation on a few sample rows
    df = load_processed()
    X, y = build_model_frame(df)

    print("\n=== SAMPLE BORROWER-LEVEL EXPLANATIONS ===")
    for idx in [0, 5, 20]:
        row = X.iloc[idx]
        actual = y.iloc[idx]
        exp = explain_borrower(row, model, scaler, feature_names)
        print(f"\nBorrower #{idx} (actual={'Default' if actual==1 else 'Non-Default'}):")
        print(f"  Predicted: {exp['predicted_class']} (PD={exp['default_probability']:.2%})")
        print(f"  {exp['narrative']}")

    importance.to_csv("reports/business/global_feature_importance.csv", index=False)
    print("\nSaved global feature importance to reports/business/global_feature_importance.csv")
