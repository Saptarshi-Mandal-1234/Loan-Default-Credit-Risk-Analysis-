"""
Schema validation for the Credit Risk dataset.
Ensures raw data conforms to the expected structure before any analysis begins.
"""

import pandas as pd

EXPECTED_SCHEMA = {
    "person_age": "int64",
    "person_income": "int64",
    "person_home_ownership": "object",
    "person_emp_length": "float64",
    "loan_intent": "object",
    "loan_grade": "object",
    "loan_amnt": "int64",
    "loan_int_rate": "float64",
    "loan_status": "int64",
    "loan_percent_income": "float64",
    "cb_person_default_on_file": "object",
    "cb_person_cred_hist_length": "int64",
}

EXPECTED_CATEGORIES = {
    "person_home_ownership": {"RENT", "OWN", "MORTGAGE", "OTHER"},
    "loan_intent": {"PERSONAL", "EDUCATION", "MEDICAL", "VENTURE",
                     "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"},
    "loan_grade": {"A", "B", "C", "D", "E", "F", "G"},
    "cb_person_default_on_file": {"Y", "N"},
    "loan_status": {0, 1},
}


def load_data(path: str) -> pd.DataFrame:
    """Load the raw credit risk CSV into a DataFrame."""
    return pd.read_csv(path)


def validate_schema(df: pd.DataFrame) -> dict:
    """
    Validate column presence, types, and category domains.
    Returns a dict summary; raises no exceptions so callers can log/report issues.
    """
    report = {"missing_columns": [], "unexpected_dtypes": {}, "unexpected_categories": {}}

    # 1. Column presence
    for col in EXPECTED_SCHEMA:
        if col not in df.columns:
            report["missing_columns"].append(col)

    # 2. Data types (loosely — object columns may show as 'str' in newer pandas)
    for col, expected_type in EXPECTED_SCHEMA.items():
        if col in df.columns:
            actual = str(df[col].dtype)
            if expected_type not in actual and not (expected_type == "object" and actual in ("object", "str")):
                report["unexpected_dtypes"][col] = actual

    # 3. Category domains
    for col, allowed in EXPECTED_CATEGORIES.items():
        if col in df.columns:
            found = set(df[col].dropna().unique())
            unexpected = found - allowed
            if unexpected:
                report["unexpected_categories"][col] = list(unexpected)

    report["n_rows"] = len(df)
    report["n_cols"] = df.shape[1]
    report["passed"] = not (report["missing_columns"] or report["unexpected_categories"])

    return report


if __name__ == "__main__":
    df = load_data("data/raw/credit_risk_dataset.csv")
    result = validate_schema(df)
    print("Schema Validation Report")
    print("=" * 40)
    for k, v in result.items():
        print(f"{k}: {v}")
