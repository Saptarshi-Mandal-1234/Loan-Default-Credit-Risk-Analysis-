"""
Customer Personas — translates statistical segments into named, memorable
borrower personas for non-technical stakeholders (credit committee, execs).
Rule-based (not clustering) so each persona maps transparently to policy.
"""

import pandas as pd

df = pd.read_csv("data/processed/credit_risk_decisions.csv")


def assign_persona(row) -> str:
    if row["loan_grade"] in ["A", "B"] and row["person_income"] >= 50000:
        return "The Steady Earner"
    if row["cb_person_default_on_file"] == "Y":
        return "The Repeat Risk"
    if row["person_age"] <= 26 and row["person_emp_length"] <= 2:
        return "The Fresh Starter"
    if row["loan_percent_income"] > 0.40:
        return "The Overextended Borrower"
    if row["loan_intent"] == "DEBTCONSOLIDATION" and row["person_home_ownership"] == "RENT":
        return "The Debt Juggler"
    if row["loan_grade"] in ["F", "G"]:
        return "The High-Risk Applicant"
    if row["person_home_ownership"] == "MORTGAGE" and row["cb_person_cred_hist_length"] >= 10:
        return "The Established Homeowner"
    return "The Moderate Borrower"


df["persona"] = df.apply(assign_persona, axis=1)

persona_summary = df.groupby("persona").agg(
    count=("loan_status", "size"),
    default_rate=("loan_status", "mean"),
    avg_income=("person_income", "mean"),
    avg_loan_amnt=("loan_amnt", "mean"),
    avg_credit_score=("credit_risk_score", "mean"),
).round(2).sort_values("default_rate", ascending=False)

persona_summary["pct_of_portfolio"] = (persona_summary["count"] / len(df) * 100).round(1)

print("=== CUSTOMER PERSONAS ===")
print(persona_summary.to_string())

PERSONA_DESCRIPTIONS = {
    "The Steady Earner": "High grade (A/B), solid income ($50k+). Lowest risk — fast-track approval candidate.",
    "The Repeat Risk": "Has a prior bureau default on file. Requires mandatory manual review regardless of score.",
    "The Fresh Starter": "Young (<=26) with limited employment history (<=2y). Thin credit file, moderate risk.",
    "The Overextended Borrower": "Loan-to-income ratio above 40%. High debt service burden regardless of grade.",
    "The Debt Juggler": "Renter consolidating debt. Signals existing financial strain.",
    "The High-Risk Applicant": "Grade F/G. Very high statistical default probability — reject by default policy.",
    "The Established Homeowner": "Mortgage holder with 10+ years credit history. Strong stability signal.",
    "The Moderate Borrower": "Does not fit a distinct high/low-risk pattern — standard underwriting applies.",
}

print("\n=== PERSONA DESCRIPTIONS ===")
for name, desc in PERSONA_DESCRIPTIONS.items():
    print(f"- {name}: {desc}")

persona_summary_out = persona_summary.reset_index()
persona_summary_out["description"] = persona_summary_out["persona"].map(PERSONA_DESCRIPTIONS)
persona_summary_out.to_csv("reports/business/customer_personas.csv", index=False)
print("\nSaved to reports/business/customer_personas.csv")
