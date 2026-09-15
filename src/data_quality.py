"""
Data Quality Assessment module for the Credit Risk dataset.
Produces a structured report covering missingness, duplicates, outliers,
invalid values, feature consistency, and class balance.

This module only DIAGNOSES issues — no cleaning/imputation happens here.
Cleaning decisions are applied later (Phase 4: Feature Engineering) so the
raw data and the audit trail of issues found remain intact.
"""

import pandas as pd
import numpy as np


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    miss = df.isnull().sum()
    pct = (miss / len(df) * 100).round(2)
    out = pd.DataFrame({"missing_count": miss, "missing_pct": pct})
    return out[out["missing_count"] > 0].sort_values("missing_pct", ascending=False)


def duplicate_report(df: pd.DataFrame) -> dict:
    return {
        "full_duplicate_rows": int(df.duplicated().sum()),
        "pct_of_total": round(df.duplicated().sum() / len(df) * 100, 2),
    }


def invalid_value_report(df: pd.DataFrame) -> dict:
    """Business-rule based invalid value checks (not statistical outliers)."""
    return {
        "age_over_100": int((df["person_age"] > 100).sum()),
        "emp_length_over_60yrs": int((df["person_emp_length"] > 60).sum()),
        "emp_length_exceeds_age": int((df["person_emp_length"] > df["person_age"]).sum()),
        "zero_or_negative_income": int((df["person_income"] <= 0).sum()),
        "zero_or_negative_loan_amount": int((df["loan_amnt"] <= 0).sum()),
    }


def iqr_outlier_report(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    rows = []
    for col in columns:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lb, ub = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((df[col] < lb) | (df[col] > ub)).sum())
        rows.append({
            "feature": col, "lower_bound": round(lb, 2), "upper_bound": round(ub, 2),
            "n_outliers": n_out, "pct_outliers": round(n_out / len(df) * 100, 2)
        })
    return pd.DataFrame(rows)


def feature_consistency_report(df: pd.DataFrame) -> dict:
    """Cross-checks loan_percent_income against loan_amnt / person_income."""
    computed = df["loan_amnt"] / df["person_income"]
    diff = (computed - df["loan_percent_income"]).abs()
    return {
        "max_abs_diff": round(diff.max(), 4),
        "rows_diff_gt_0.01": int((diff > 0.01).sum()),
    }


def class_balance_report(df: pd.DataFrame, target: str = "loan_status") -> pd.DataFrame:
    counts = df[target].value_counts()
    pct = df[target].value_counts(normalize=True).round(4) * 100
    return pd.DataFrame({"count": counts, "pct": pct})


def run_full_assessment(df: pd.DataFrame) -> dict:
    numeric_cols = ["person_income", "loan_amnt", "loan_int_rate",
                     "loan_percent_income", "cb_person_cred_hist_length"]
    return {
        "missing_values": missing_value_report(df),
        "duplicates": duplicate_report(df),
        "invalid_values": invalid_value_report(df),
        "iqr_outliers": iqr_outlier_report(df, numeric_cols),
        "feature_consistency": feature_consistency_report(df),
        "class_balance": class_balance_report(df),
    }


if __name__ == "__main__":
    df = pd.read_csv("data/raw/credit_risk_dataset.csv")
    results = run_full_assessment(df)
    for k, v in results.items():
        print(f"\n--- {k} ---")
        print(v)
