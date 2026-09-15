"""
Risk Heatmap — visualizes default rate across two-dimensional borrower
segments (Loan Grade x Income Band, and Home Ownership x Loan Purpose),
surfacing concentration risk that single-variable charts can miss.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/processed/credit_risk_decisions.csv")

# ---------- Heatmap 1: Loan Grade x Income Band ----------
pivot1 = df.pivot_table(values="loan_status", index="loan_grade", columns="income_band",
                         aggfunc="mean", observed=True)
band_order = ["<25k", "25-50k", "50-75k", "75-100k", "100k+"]
pivot1 = pivot1[[c for c in band_order if c in pivot1.columns]].sort_index()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot1, annot=True, fmt=".1%", cmap="RdYlGn_r", ax=ax,
            cbar_kws={"label": "Default Rate"})
ax.set_title("Risk Heatmap — Default Rate by Loan Grade × Income Band")
ax.set_xlabel("Income Band")
ax.set_ylabel("Loan Grade")
plt.tight_layout()
plt.savefig("reports/figures/15_risk_heatmap_grade_income.png", dpi=110)
plt.close()

# ---------- Heatmap 2: Home Ownership x Loan Purpose ----------
pivot2 = df.pivot_table(values="loan_status", index="person_home_ownership", columns="loan_intent",
                         aggfunc="mean", observed=True)

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(pivot2, annot=True, fmt=".1%", cmap="RdYlGn_r", ax=ax,
            cbar_kws={"label": "Default Rate"})
ax.set_title("Risk Heatmap — Default Rate by Home Ownership × Loan Purpose")
ax.set_xlabel("Loan Purpose")
ax.set_ylabel("Home Ownership")
plt.tight_layout()
plt.savefig("reports/figures/16_risk_heatmap_ownership_purpose.png", dpi=110)
plt.close()

print("Heatmap 1 (Grade x Income Band):")
print(pivot1.round(3))
print("\nHeatmap 2 (Ownership x Purpose):")
print(pivot2.round(3))

# Highlight the single worst concentration cell in each heatmap
worst1 = pivot1.stack().idxmax()
worst2 = pivot2.stack().idxmax()
print(f"\nHighest-risk cell (Grade x Income): {worst1} -> {pivot1.stack().max():.1%} default rate")
print(f"Highest-risk cell (Ownership x Purpose): {worst2} -> {pivot2.stack().max():.1%} default rate")

print("\nSaved: reports/figures/15_risk_heatmap_grade_income.png, "
      "reports/figures/16_risk_heatmap_ownership_purpose.png")
