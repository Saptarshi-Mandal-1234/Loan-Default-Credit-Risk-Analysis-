"""
Phase 7 — Risk Scoring Engine
Converts model-predicted default probability (PD) into a standardized
Credit Risk Score (300-900, higher = safer, mirrors familiar bureau-style scores)
and assigns a risk tier.
"""

import pandas as pd
import numpy as np

SCORE_MIN, SCORE_MAX = 300, 900


def pd_to_score(pd_value: float) -> int:
    """
    Linear inverse mapping: PD=0.0 -> 900 (safest), PD=1.0 -> 300 (riskiest).
    This is the simplest, most transparent scaling — defensible to a credit
    committee because the logic is fully auditable (no black-box scaling).
    """
    pd_value = np.clip(pd_value, 0, 1)
    score = SCORE_MAX - (pd_value * (SCORE_MAX - SCORE_MIN))
    return int(round(score))


def score_to_tier(score: int) -> str:
    """
    Risk tiers calibrated against the score range.
    Boundaries chosen so 'Very Low'/'Low' correspond to strong bureau grades (A/B)
    and 'Very High' captures the worst grades (F/G) observed in EDA (Phase 3).
    """
    if score >= 780:
        return "Very Low"
    elif score >= 680:
        return "Low"
    elif score >= 580:
        return "Moderate"
    elif score >= 480:
        return "High"
    else:
        return "Very High"


def score_dataframe(df: pd.DataFrame, proba_col: str = "default_probability") -> pd.DataFrame:
    df = df.copy()
    df["credit_risk_score"] = df[proba_col].apply(pd_to_score)
    df["risk_tier"] = df["credit_risk_score"].apply(score_to_tier)
    return df


if __name__ == "__main__":
    import joblib
    from modeling import load_processed, build_model_frame

    model = joblib.load("models/logistic_regression_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")

    df = load_processed()
    X, y = build_model_frame(df)
    X_scaled = scaler.transform(X[feature_names])
    proba = model.predict_proba(X_scaled)[:, 1]

    scored = df.copy()
    scored["default_probability"] = proba
    scored = score_dataframe(scored)

    print("Sample scored records:")
    print(scored[["default_probability", "credit_risk_score", "risk_tier"]].head(10))

    print("\nRisk Tier Distribution:")
    tier_dist = scored["risk_tier"].value_counts()
    tier_pct = scored["risk_tier"].value_counts(normalize=True).round(4) * 100
    print(pd.DataFrame({"count": tier_dist, "pct": tier_pct}))

    print("\nActual default rate by risk tier (sanity check — should increase monotonically):")
    print(scored.groupby("risk_tier", observed=True)["loan_status"].mean().sort_values())

    scored.to_csv("data/processed/credit_risk_scored.csv", index=False)
    print("\nSaved scored dataset to data/processed/credit_risk_scored.csv")
