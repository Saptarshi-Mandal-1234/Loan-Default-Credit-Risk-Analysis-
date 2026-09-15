"""
Phase 8 — Loan Decision Engine
Translates risk tier + key business flags into an actionable loan decision,
each with an auditable business justification (required for credit committee sign-off).
"""

import pandas as pd


def decide(risk_tier: str, loan_percent_income: float, prior_default: str,
           default_probability: float) -> dict:
    """
    Decision logic layers a rule-based overlay on top of the statistical risk
    tier — mirrors real bank practice where hard policy rules can override a
    borderline model score (e.g., mandatory review for prior defaults).
    """
    reasons = []

    # Hard policy override: prior bureau default always forces at least manual review,
    # regardless of model score (EDA Phase 3: prior default ~doubles default rate).
    if prior_default == "Y" and risk_tier not in ("High", "Very High"):
        decision = "Manual Review"
        reasons.append("Applicant has a prior bureau default on file — policy requires manual review "
                        "even though the statistical risk tier is otherwise acceptable.")
        return {"decision": decision, "reasons": reasons}

    if risk_tier == "Very Low":
        decision = "Approve"
        reasons.append(f"Very Low risk tier (PD={default_probability:.1%}) — strong repayment profile.")

    elif risk_tier == "Low":
        decision = "Approve"
        reasons.append(f"Low risk tier (PD={default_probability:.1%}) — acceptable risk under standard policy.")
        if loan_percent_income > 0.30:
            decision = "Approve with Conditions"
            reasons.append("Loan-to-income ratio exceeds 30% — recommend reduced loan amount "
                            "or additional income verification.")

    elif risk_tier == "Moderate":
        decision = "Approve with Conditions"
        reasons.append(f"Moderate risk tier (PD={default_probability:.1%}) — approve with adjusted terms "
                        "(higher rate and/or lower approved amount).")

    elif risk_tier == "High":
        decision = "Manual Review"
        reasons.append(f"High risk tier (PD={default_probability:.1%}) — requires underwriter judgement "
                        "and possibly additional collateral/guarantor.")

    else:  # Very High
        decision = "Reject"
        reasons.append(f"Very High risk tier (PD={default_probability:.1%}) — default probability too "
                        "high for approval under current risk appetite.")

    if prior_default == "Y":
        reasons.append("Note: applicant also has a prior bureau default on file.")

    return {"decision": decision, "reasons": reasons}


def decide_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    results = df.apply(
        lambda r: decide(r["risk_tier"], r["loan_percent_income"],
                          r["cb_person_default_on_file"], r["default_probability"]),
        axis=1
    )
    df["loan_decision"] = results.apply(lambda x: x["decision"])
    df["decision_reasons"] = results.apply(lambda x: " | ".join(x["reasons"]))
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/credit_risk_scored.csv")
    decided = decide_dataframe(df)

    print("Decision Distribution:")
    print(decided["loan_decision"].value_counts())
    print()
    print("Decision distribution (%):")
    print((decided["loan_decision"].value_counts(normalize=True) * 100).round(2))

    print("\nSample decisions:")
    print(decided[["risk_tier", "default_probability", "cb_person_default_on_file",
                    "loan_decision"]].sample(5, random_state=1))

    print("\nSample reasoning (1 example):")
    sample = decided.iloc[5]
    print(f"Risk Tier: {sample.risk_tier} | Decision: {sample.loan_decision}")
    print(f"Reasons: {sample.decision_reasons}")

    decided.to_csv("data/processed/credit_risk_decisions.csv", index=False)
    print("\nSaved to data/processed/credit_risk_decisions.csv")
