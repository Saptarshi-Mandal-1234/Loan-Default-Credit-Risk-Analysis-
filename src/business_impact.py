"""
Business Impact Suite:
  1. Threshold Optimization — finds the PD cutoff that minimizes total business cost.
  2. Cost of False Approvals — quantifies $ loss from approving loans that default.
  3. Business Impact Calculator — net portfolio profit/loss under different policies.

Assumptions (clearly documented for auditability):
  - Loss Given Default (LGD) = 60% of loan amount (industry-typical assumption
    for unsecured personal loans; recoverable ~40% via collections/write-off recovery).
  - Revenue per approved non-default loan = loan_amnt * loan_int_rate (simplified;
    ignores time value of money / duration, acceptable for a portfolio-level estimate).
  - Cost of a false reject (rejecting a would-be non-defaulter) = forgone interest revenue.
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from modeling import load_processed, build_model_frame

LGD = 0.60  # Loss Given Default assumption

model = joblib.load("models/logistic_regression_model.pkl")
scaler = joblib.load("models/scaler.pkl")
feature_names = joblib.load("models/feature_names.pkl")

df = load_processed()
X, y = build_model_frame(df)
X_scaled = scaler.transform(X[feature_names])
proba = model.predict_proba(X_scaled)[:, 1]

work = df[["loan_amnt", "loan_int_rate", "loan_status"]].copy()
work["default_probability"] = proba


def business_cost(threshold: float, work: pd.DataFrame) -> dict:
    """
    Approve if predicted PD < threshold. Compute:
      - False Approvals (approved, actually defaulted) -> loss = loan_amnt * LGD
      - False Rejects (rejected, actually would NOT have defaulted) -> lost revenue
      - True Approvals (approved, non-default) -> revenue = loan_amnt * rate%
    """
    approve = work["default_probability"] < threshold

    false_approvals = work[approve & (work["loan_status"] == 1)]
    false_rejects = work[~approve & (work["loan_status"] == 0)]
    true_approvals = work[approve & (work["loan_status"] == 0)]

    loss_false_approvals = (false_approvals["loan_amnt"] * LGD).sum()
    lost_revenue_false_rejects = (false_rejects["loan_amnt"] * false_rejects["loan_int_rate"] / 100).sum()
    revenue_true_approvals = (true_approvals["loan_amnt"] * true_approvals["loan_int_rate"] / 100).sum()

    net_impact = revenue_true_approvals - loss_false_approvals - lost_revenue_false_rejects

    return {
        "threshold": threshold,
        "approval_rate": approve.mean(),
        "n_false_approvals": len(false_approvals),
        "loss_false_approvals": loss_false_approvals,
        "n_false_rejects": len(false_rejects),
        "lost_revenue_false_rejects": lost_revenue_false_rejects,
        "revenue_true_approvals": revenue_true_approvals,
        "net_business_impact": net_impact,
    }


# ---------- Threshold sweep ----------
thresholds = np.arange(0.05, 0.85, 0.02)
sweep = pd.DataFrame([business_cost(t, work) for t in thresholds])

best_row = sweep.loc[sweep["net_business_impact"].idxmax()]
default_row = sweep.iloc[(sweep["threshold"] - 0.50).abs().idxmin()]

print("=== THRESHOLD OPTIMIZATION ===")
print(f"Standard 0.50 threshold -> Net Business Impact: ${default_row['net_business_impact']:,.0f} "
      f"(Approval Rate: {default_row['approval_rate']:.1%})")
print(f"Optimal threshold ({best_row['threshold']:.2f}) -> Net Business Impact: ${best_row['net_business_impact']:,.0f} "
      f"(Approval Rate: {best_row['approval_rate']:.1%})")
print(f"Improvement from optimization: ${best_row['net_business_impact'] - default_row['net_business_impact']:,.0f}")

# ---------- Chart: Net Business Impact vs Threshold ----------
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(sweep["threshold"], sweep["net_business_impact"] / 1e6, color="#2E86AB", linewidth=2)
ax.axvline(best_row["threshold"], color="#C73E3E", linestyle="--",
           label=f"Optimal threshold = {best_row['threshold']:.2f}")
ax.axvline(0.50, color="gray", linestyle=":", label="Default threshold = 0.50")
ax.set_xlabel("Approval Threshold (Predicted Default Probability Cutoff)")
ax.set_ylabel("Net Business Impact ($ Millions)")
ax.set_title("Threshold Optimization — Net Business Impact")
ax.legend()
plt.tight_layout()
plt.savefig("reports/figures/14_threshold_optimization.png", dpi=110)
plt.close()

# ---------- Cost of False Approvals at current (0.50) threshold ----------
print(f"\n=== COST OF FALSE APPROVALS (threshold=0.50) ===")
print(f"False Approvals (approved loans that defaulted): {int(default_row['n_false_approvals']):,}")
print(f"Total Loss from False Approvals: ${default_row['loss_false_approvals']:,.0f}")
print(f"(Assumption: Loss Given Default = {LGD:.0%} of loan amount)")

# ---------- Business Impact Summary Table ----------
summary = pd.DataFrame({
    "Scenario": ["Current Policy (0.50 threshold)", f"Optimized Policy ({best_row['threshold']:.2f} threshold)"],
    "Approval Rate": [default_row["approval_rate"], best_row["approval_rate"]],
    "Revenue (True Approvals)": [default_row["revenue_true_approvals"], best_row["revenue_true_approvals"]],
    "Loss (False Approvals)": [default_row["loss_false_approvals"], best_row["loss_false_approvals"]],
    "Forgone Revenue (False Rejects)": [default_row["lost_revenue_false_rejects"], best_row["lost_revenue_false_rejects"]],
    "Net Business Impact": [default_row["net_business_impact"], best_row["net_business_impact"]],
})
print("\n=== BUSINESS IMPACT SUMMARY ===")
print(summary.to_string(index=False))

sweep.to_csv("reports/business/threshold_optimization_sweep.csv", index=False)
summary.to_csv("reports/business/business_impact_summary.csv", index=False)
print("\nSaved: threshold_optimization_sweep.csv, business_impact_summary.csv, "
      "reports/figures/14_threshold_optimization.png")
