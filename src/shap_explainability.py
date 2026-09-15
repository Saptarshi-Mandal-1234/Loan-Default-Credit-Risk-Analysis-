"""
SHAP Explainability — supplements the coefficient-based explanations in
explainability.py with SHAP values, which properly account for feature
interactions and per-observation deviations (not just standardized coefficients).
"""

import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt

from modeling import load_processed, build_model_frame

model = joblib.load("models/logistic_regression_model.pkl")
scaler = joblib.load("models/scaler.pkl")
feature_names = joblib.load("models/feature_names.pkl")

df = load_processed()
X, y = build_model_frame(df)
X = X[feature_names]

# Use a sample for SHAP (32k rows would be slow; 1,000-row sample is standard practice)
sample = X.sample(1000, random_state=42)
sample_scaled = scaler.transform(sample)

explainer = shap.LinearExplainer(model, sample_scaled, feature_names=feature_names)
shap_values = explainer(sample_scaled)

# ---------- Global SHAP summary plot ----------
plt.figure()
shap.summary_plot(shap_values, sample_scaled, feature_names=feature_names, show=False, max_display=12)
plt.tight_layout()
plt.savefig("reports/figures/12_shap_summary.png", dpi=110, bbox_inches="tight")
plt.close()

# ---------- Global SHAP importance (mean |SHAP value|) ----------
mean_abs_shap = pd.DataFrame({
    "feature": feature_names,
    "mean_abs_shap": np.abs(shap_values.values).mean(axis=0)
}).sort_values("mean_abs_shap", ascending=False)

print("=== TOP 10 FEATURES BY SHAP IMPORTANCE ===")
print(mean_abs_shap.head(10).to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5))
top10 = mean_abs_shap.head(10).iloc[::-1]
ax.barh(top10["feature"], top10["mean_abs_shap"], color="#2E86AB")
ax.set_title("Global Feature Importance (Mean |SHAP Value|)")
ax.set_xlabel("Mean |SHAP Value|")
plt.tight_layout()
plt.savefig("reports/figures/13_shap_importance_bar.png", dpi=110)
plt.close()

mean_abs_shap.to_csv("reports/business/shap_feature_importance.csv", index=False)


def explain_with_shap(row_idx: int):
    """Borrower-level SHAP explanation for one sampled row (demo)."""
    contrib = pd.DataFrame({
        "feature": feature_names,
        "shap_value": shap_values.values[row_idx]
    }).sort_values("shap_value", key=abs, ascending=False)
    return contrib.head(5)


print("\n=== SAMPLE BORROWER SHAP EXPLANATION (row 0 of sample) ===")
print(explain_with_shap(0).to_string(index=False))

print("\nSHAP artifacts saved: reports/figures/12_shap_summary.png, "
      "reports/figures/13_shap_importance_bar.png, "
      "reports/business/shap_feature_importance.csv")
