"""
Phase 3 — Exploratory Data Analysis
Generates univariate, bivariate, and multivariate charts saved to reports/figures/.
Uses raw data (pre-cleaning) purely for pattern discovery; cleaning happens in Phase 4.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110
FIG_DIR = "reports/figures"

df = pd.read_csv("data/raw/credit_risk_dataset.csv")
# Light filtering ONLY for visualization clarity (raw data untouched elsewhere)
df_viz = df[(df.person_age <= 100) & (df.person_emp_length <= 60)].copy()
df_viz["default_label"] = df_viz["loan_status"].map({0: "Non-Default", 1: "Default"})

PALETTE = {"Non-Default": "#2E86AB", "Default": "#C73E3E"}

# ---------- 1. Loan amount distribution (univariate) ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
sns.histplot(df_viz["loan_amnt"], bins=40, kde=True, color="#2E86AB", ax=ax)
ax.set_title("Distribution of Loan Amounts")
ax.set_xlabel("Loan Amount (USD)")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/01_loan_amount_distribution.png")
plt.close()

# ---------- 2. Income distribution (univariate) ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
sns.histplot(df_viz[df_viz.person_income < 200000]["person_income"], bins=40,
             kde=True, color="#2E86AB", ax=ax)
ax.set_title("Distribution of Applicant Income (< $200k)")
ax.set_xlabel("Annual Income (USD)")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/02_income_distribution.png")
plt.close()

# ---------- 3. Age & employment length (univariate) ----------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
sns.histplot(df_viz["person_age"], bins=30, color="#2E86AB", ax=axes[0])
axes[0].set_title("Applicant Age Distribution")
sns.histplot(df_viz["person_emp_length"], bins=20, color="#2E86AB", ax=axes[1])
axes[1].set_title("Employment Length Distribution")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/03_age_employment_distribution.png")
plt.close()

# ---------- 4. Credit history & loan purpose (univariate) ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
sns.histplot(df_viz["cb_person_cred_hist_length"], bins=20, color="#2E86AB", ax=axes[0])
axes[0].set_title("Credit History Length Distribution")
order = df_viz["loan_intent"].value_counts().index
sns.countplot(data=df_viz, y="loan_intent", order=order, color="#2E86AB", ax=axes[1])
axes[1].set_title("Loan Purpose Frequency")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/04_credit_history_purpose.png")
plt.close()

# ---------- 5. Default rate by income band (bivariate) ----------
df_viz["income_band"] = pd.cut(df_viz["person_income"],
                                bins=[0, 25000, 50000, 75000, 100000, 1e9],
                                labels=["<25k", "25-50k", "50-75k", "75-100k", "100k+"])
rate_by_income = df_viz.groupby("income_band", observed=True)["loan_status"].mean() * 100
fig, ax = plt.subplots(figsize=(7, 4.5))
rate_by_income.plot(kind="bar", color="#C73E3E", ax=ax)
ax.set_title("Default Rate by Income Band")
ax.set_ylabel("Default Rate (%)")
ax.set_xlabel("Income Band")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/05_default_rate_by_income.png")
plt.close()

# ---------- 6. Default vs loan amount (bivariate) ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
sns.boxplot(data=df_viz, x="default_label", y="loan_amnt", hue="default_label",
            palette=PALETTE, legend=False, ax=ax)
ax.set_title("Loan Amount by Default Status")
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/06_loan_amount_vs_default.png")
plt.close()

# ---------- 7. Default rate by home ownership & loan grade (bivariate) ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
rate_home = df_viz.groupby("person_home_ownership", observed=True)["loan_status"].mean() * 100
rate_home.sort_values(ascending=False).plot(kind="bar", color="#C73E3E", ax=axes[0])
axes[0].set_title("Default Rate by Home Ownership")
axes[0].set_ylabel("Default Rate (%)")
plt.setp(axes[0].get_xticklabels(), rotation=0)

rate_grade = df_viz.groupby("loan_grade", observed=True)["loan_status"].mean() * 100
rate_grade.sort_index().plot(kind="bar", color="#C73E3E", ax=axes[1])
axes[1].set_title("Default Rate by Loan Grade")
axes[1].set_ylabel("Default Rate (%)")
plt.setp(axes[1].get_xticklabels(), rotation=0)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/07_default_by_ownership_grade.png")
plt.close()

# ---------- 8. Default rate by loan purpose & credit bureau default flag (bivariate) ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
rate_intent = df_viz.groupby("loan_intent", observed=True)["loan_status"].mean().sort_values(ascending=False) * 100
rate_intent.plot(kind="barh", color="#C73E3E", ax=axes[0])
axes[0].set_title("Default Rate by Loan Purpose")
axes[0].set_xlabel("Default Rate (%)")

rate_cbdefault = df_viz.groupby("cb_person_default_on_file", observed=True)["loan_status"].mean() * 100
rate_cbdefault.plot(kind="bar", color="#C73E3E", ax=axes[1])
axes[1].set_title("Default Rate by Prior Bureau Default Flag")
axes[1].set_ylabel("Default Rate (%)")
plt.setp(axes[1].get_xticklabels(), rotation=0)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/08_default_by_purpose_cbflag.png")
plt.close()

# ---------- 9. Correlation heatmap (multivariate) ----------
num_cols = ["person_age", "person_income", "person_emp_length", "loan_amnt",
            "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length", "loan_status"]
fig, ax = plt.subplots(figsize=(8, 6.5))
corr = df_viz[num_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
ax.set_title("Correlation Matrix — Numeric Features")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/09_correlation_heatmap.png")
plt.close()

# ---------- 10. Loan-to-income ratio vs default, segmented (multivariate) ----------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df_viz, x="loan_grade", y="loan_percent_income", hue="default_label",
            palette=PALETTE, order=sorted(df_viz.loan_grade.unique()), ax=ax)
ax.set_title("Loan-to-Income Ratio by Grade, Split by Default Status")
ax.set_ylabel("Loan Percent of Income")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/10_loanpct_by_grade_default.png")
plt.close()

print("All 10 charts generated in", FIG_DIR)

# Print key stats referenced in insights
print("\nDefault rate by grade:\n", rate_grade)
print("\nDefault rate by home ownership:\n", rate_home)
print("\nDefault rate by loan intent:\n", rate_intent)
print("\nDefault rate by cb_default_on_file:\n", rate_cbdefault)
print("\nDefault rate by income band:\n", rate_by_income)
print("\nCorrelation with target:\n", corr["loan_status"].sort_values(ascending=False))
