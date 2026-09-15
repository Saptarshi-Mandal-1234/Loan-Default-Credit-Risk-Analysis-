"""
Loan Portfolio Health Score — a single composite 0-100 index summarizing
overall portfolio risk health for executive consumption, combining:
  - Default rate (35% weight) — the headline risk metric
  - Average risk score, normalized (30% weight) — forward-looking risk composition
  - % High/Very-High risk tier concentration (20% weight, inverted)
  - Approval rate (15% weight) — proxy for growth/access balance
All weights and normalization are documented for auditability.
"""

import pandas as pd
import numpy as np

WEIGHTS = {
    "default_rate": 0.35,
    "avg_risk_score": 0.30,
    "high_risk_concentration": 0.20,
    "approval_rate": 0.15,
}


def compute_health_score(df: pd.DataFrame) -> dict:
    default_rate = df["loan_status"].mean()
    avg_score = df["credit_risk_score"].mean()
    high_risk_pct = df["risk_tier"].isin(["High", "Very High"]).mean()
    approval_rate = df["loan_decision"].isin(["Approve", "Approve with Conditions"]).mean()

    # Normalize each component to a 0-100 "healthier is higher" sub-score
    default_rate_score = max(0, 100 - default_rate * 100 * 2)          # 0% default = 100, 50%+ default = 0
    risk_score_component = (avg_score - 300) / (900 - 300) * 100        # 300->0, 900->100
    concentration_score = max(0, 100 - high_risk_pct * 100 * 1.5)       # penalize high-risk concentration
    approval_score = approval_rate * 100                                 # more approvals = healthier access

    composite = (
        default_rate_score * WEIGHTS["default_rate"] +
        risk_score_component * WEIGHTS["avg_risk_score"] +
        concentration_score * WEIGHTS["high_risk_concentration"] +
        approval_score * WEIGHTS["approval_rate"]
    )

    if composite >= 80:
        grade = "Excellent"
    elif composite >= 65:
        grade = "Good"
    elif composite >= 50:
        grade = "Fair"
    elif composite >= 35:
        grade = "Weak"
    else:
        grade = "Critical"

    return {
        "portfolio_health_score": round(composite, 1),
        "health_grade": grade,
        "components": {
            "default_rate_score": round(default_rate_score, 1),
            "avg_risk_score_component": round(risk_score_component, 1),
            "concentration_score": round(concentration_score, 1),
            "approval_score": round(approval_score, 1),
        },
        "raw_inputs": {
            "default_rate": round(default_rate, 4),
            "avg_credit_risk_score": round(avg_score, 1),
            "high_risk_concentration": round(high_risk_pct, 4),
            "approval_rate": round(approval_rate, 4),
        }
    }


if __name__ == "__main__":
    df = pd.read_csv("data/processed/credit_risk_decisions.csv")
    result = compute_health_score(df)

    print("=== LOAN PORTFOLIO HEALTH SCORE ===")
    print(f"Score: {result['portfolio_health_score']} / 100  |  Grade: {result['health_grade']}")
    print("\nComponent Breakdown:")
    for k, v in result["components"].items():
        print(f"  {k}: {v}")
    print("\nRaw Inputs:")
    for k, v in result["raw_inputs"].items():
        print(f"  {k}: {v}")

    pd.DataFrame([{
        "portfolio_health_score": result["portfolio_health_score"],
        "health_grade": result["health_grade"],
        **result["components"],
        **result["raw_inputs"],
    }]).to_csv("reports/business/portfolio_health_score.csv", index=False)
    print("\nSaved to reports/business/portfolio_health_score.csv")
