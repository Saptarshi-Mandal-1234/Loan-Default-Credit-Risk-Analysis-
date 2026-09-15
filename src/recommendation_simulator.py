"""
Phase 11 — Recommendation Simulator
Given a new applicant's raw details, returns: Default Probability, Risk Score,
Risk Tier, Approval Recommendation, Reasons, and Suggested Mitigation.
"""

import pandas as pd
import joblib

from modeling import NUMERIC_FEATURES, CATEGORICAL_FEATURES, FLAG_FEATURES
from risk_scoring import pd_to_score, score_to_tier
from loan_decision_engine import decide

MODEL = joblib.load("models/logistic_regression_model.pkl")
SCALER = joblib.load("models/scaler.pkl")
FEATURE_NAMES = joblib.load("models/feature_names.pkl")


def _build_input_row(applicant: dict) -> pd.DataFrame:
    """
    applicant keys expected (raw, business-friendly):
      person_age, person_income, person_home_ownership, person_emp_length,
      loan_intent, loan_grade, loan_amnt, loan_int_rate,
      cb_person_default_on_file, cb_person_cred_hist_length
    Engineered fields (loan_percent_income, debt_to_income_ratio, flags) are
    computed automatically so the caller only supplies raw application data.
    """
    row = dict(applicant)
    row["loan_percent_income"] = round(row["loan_amnt"] / row["person_income"], 4)
    row["debt_to_income_ratio"] = round(
        (row["loan_amnt"] * (row["loan_int_rate"] / 100)) / row["person_income"], 4
    )
    row["flag_high_loan_burden"] = int(row["loan_percent_income"] > 0.40)
    row["flag_low_income_high_grade_risk"] = int(
        row["person_income"] < 25000 and row["loan_grade"] in ["D", "E", "F", "G"]
    )

    df = pd.DataFrame([row])
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + FLAG_FEATURES]
    X_encoded = pd.get_dummies(X, columns=CATEGORICAL_FEATURES, drop_first=True)

    # Align to training feature space (missing dummy columns = 0)
    X_aligned = X_encoded.reindex(columns=FEATURE_NAMES, fill_value=0)
    return X_aligned


def _suggest_mitigation(decision: str, applicant: dict, loan_percent_income: float) -> list:
    tips = []
    if decision in ("Manual Review", "Reject"):
        if loan_percent_income > 0.30:
            tips.append("Reduce requested loan amount to bring loan-to-income ratio under 30%.")
        if applicant.get("cb_person_default_on_file") == "Y":
            tips.append("Provide updated proof of resolved prior delinquency or a guarantor.")
        if applicant.get("person_emp_length", 0) < 2:
            tips.append("Reapply after building a longer employment tenure track record (2+ years).")
        if not tips:
            tips.append("Consider a smaller loan amount or a co-signer with stronger credit history.")
    elif decision == "Approve with Conditions":
        tips.append("Offer approval at a reduced amount or a modestly higher interest rate to offset risk.")
    else:
        tips.append("No mitigation required — applicant meets standard approval criteria.")
    return tips


def simulate_applicant(applicant: dict) -> dict:
    """Main entry point: returns the full recommendation package for one applicant."""
    X_input = _build_input_row(applicant)
    X_scaled = SCALER.transform(X_input)

    proba = float(MODEL.predict_proba(X_scaled)[0, 1])
    score = pd_to_score(proba)
    tier = score_to_tier(score)

    loan_pct_income = round(applicant["loan_amnt"] / applicant["person_income"], 4)
    decision_result = decide(tier, loan_pct_income,
                              applicant.get("cb_person_default_on_file", "N"), proba)

    mitigation = _suggest_mitigation(decision_result["decision"], applicant, loan_pct_income)

    return {
        "default_probability": round(proba, 4),
        "credit_risk_score": score,
        "risk_tier": tier,
        "recommendation": decision_result["decision"],
        "reasons": decision_result["reasons"],
        "suggested_mitigation": mitigation,
    }


if __name__ == "__main__":
    # Example 1: strong applicant
    applicant_a = {
        "person_age": 34, "person_income": 85000, "person_home_ownership": "MORTGAGE",
        "person_emp_length": 8, "loan_intent": "EDUCATION", "loan_grade": "B",
        "loan_amnt": 10000, "loan_int_rate": 9.5,
        "cb_person_default_on_file": "N", "cb_person_cred_hist_length": 9,
    }

    # Example 2: risky applicant
    applicant_b = {
        "person_age": 23, "person_income": 21000, "person_home_ownership": "RENT",
        "person_emp_length": 0.5, "loan_intent": "DEBTCONSOLIDATION", "loan_grade": "E",
        "loan_amnt": 12000, "loan_int_rate": 18.2,
        "cb_person_default_on_file": "Y", "cb_person_cred_hist_length": 2,
    }

    for name, app in [("Applicant A (strong profile)", applicant_a),
                       ("Applicant B (risky profile)", applicant_b)]:
        result = simulate_applicant(app)
        print(f"\n=== {name} ===")
        for k, v in result.items():
            print(f"{k}: {v}")
