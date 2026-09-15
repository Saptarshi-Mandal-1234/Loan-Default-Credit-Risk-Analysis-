"""
Phase 4 — Feature Engineering
1. Applies the cleaning decisions from the Phase 2 Data Quality Report.
2. Creates business-meaningful engineered features.
Outputs the processed dataset to data/processed/credit_risk_clean.csv
"""

import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Drop exact duplicates
    df = df.drop_duplicates()

    # 2. Drop clearly corrupted rows (NaN-safe so rows pending imputation aren't dropped)
    df = df[df["person_age"] <= 100]
    df = df[df["person_emp_length"].isna() | (df["person_emp_length"] <= 60)]
    df = df[df["person_emp_length"].isna() | (df["person_emp_length"] <= df["person_age"])]

    # 3. Impute missing loan_int_rate by loan_grade group median (rate is grade-driven)
    df["loan_int_rate"] = df.groupby("loan_grade")["loan_int_rate"].transform(
        lambda x: x.fillna(x.median())
    )

    # 4. Impute missing person_emp_length with overall median (after invalid-value filtering)
    df["person_emp_length"] = df["person_emp_length"].fillna(df["person_emp_length"].median())

    # 5. Recompute loan_percent_income for consistency (source column had drift)
    df["loan_percent_income"] = (df["loan_amnt"] / df["person_income"]).round(4)

    return df.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Debt-to-Income proxy (loan_percent_income already is loan-to-income;
    # here we build an "implied annual debt burden" using rate + amount)
    df["debt_to_income_ratio"] = (
        (df["loan_amnt"] * (df["loan_int_rate"] / 100)) / df["person_income"]
    ).round(4)

    # Loan-to-Income ratio (recomputed already as loan_percent_income; alias for clarity)
    df["loan_to_income_ratio"] = df["loan_percent_income"]

    # Income Band (categorical, matches EDA bands)
    df["income_band"] = pd.cut(
        df["person_income"], bins=[0, 25000, 50000, 75000, 100000, np.inf],
        labels=["<25k", "25-50k", "50-75k", "75-100k", "100k+"]
    )

    # Age Group
    df["age_group"] = pd.cut(
        df["person_age"], bins=[0, 25, 35, 45, 100],
        labels=["18-25", "26-35", "36-45", "46+"]
    )

    # Employment Stability (tenure-based)
    df["employment_stability"] = pd.cut(
        df["person_emp_length"], bins=[-1, 1, 3, 7, np.inf],
        labels=["Unstable(<1y)", "Early(1-3y)", "Established(3-7y)", "Stable(7y+)"]
    )

    # Credit Utilization / History Category
    df["credit_history_category"] = pd.cut(
        df["cb_person_cred_hist_length"], bins=[-1, 2, 5, 10, np.inf],
        labels=["New(<=2y)", "Building(2-5y)", "Established(5-10y)", "Deep(10y+)"]
    )

    # Risk Flags (binary business rules from EDA findings)
    df["flag_prior_default"] = (df["cb_person_default_on_file"] == "Y").astype(int)
    df["flag_high_loan_burden"] = (df["loan_percent_income"] > 0.40).astype(int)
    df["flag_low_income_high_grade_risk"] = (
        (df["person_income"] < 25000) & (df["loan_grade"].isin(["D", "E", "F", "G"]))
    ).astype(int)
    df["flag_renter"] = (df["person_home_ownership"] == "RENT").astype(int)

    return df


if __name__ == "__main__":
    raw = pd.read_csv("data/raw/credit_risk_dataset.csv")
    print("Raw shape:", raw.shape)

    cleaned = clean_data(raw)
    print("After cleaning:", cleaned.shape, "(removed", raw.shape[0] - cleaned.shape[0], "rows)")
    print("Remaining missing values:", cleaned.isnull().sum().sum())

    featured = engineer_features(cleaned)
    print("After feature engineering:", featured.shape)
    print("\nNew columns:", [c for c in featured.columns if c not in raw.columns])

    featured.to_csv("data/processed/credit_risk_clean.csv", index=False)
    print("\nSaved to data/processed/credit_risk_clean.csv")
