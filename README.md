# AI-Powered Credit Risk Advisory System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-orange)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-E97627)
![License](https://img.shields.io/badge/License-MIT-green)

A production-style credit risk analytics project built for a simulated bank
Credit Risk Department. Covers the full lifecycle: data quality, EDA, feature
engineering, predictive modeling, explainability, risk scoring, automated loan
decisioning, executive dashboarding, and business advisory reporting.

**Model performance:** ROC-AUC 0.876 · Recall 78.8% (default class) · Accuracy 80.6%

---

## Business Objective

Reduce loan default losses while preserving healthy approval volume, by
replacing manual, inconsistent underwriter judgement with a quantified,
explainable, auditable default-probability model and decision engine.

See `docs/business_objective.md` for full objective and KPI definitions.

---

## Project Architecture

```
Raw Data → Data Quality Assessment → EDA → Feature Engineering →
Logistic Regression Model → Explainability (XAI) → Risk Scoring (300-900) →
Loan Decision Engine → Portfolio Dashboard (Excel) + Advisory Report (Word) →
Recommendation Simulator (single-applicant, real-time)
```

Each stage is a standalone, reusable Python module in `src/`, chained via
simple function calls (no hidden global state) — the pipeline can be re-run
end-to-end from `data/raw/credit_risk_dataset.csv` to final decisions.

---

## Folder Structure

```
credit_risk_project/
├── data/
│   ├── raw/                    # Original source data (untouched)
│   └── processed/              # Cleaned, engineered, scored, decisioned datasets
├── src/                        # All pipeline modules (see below)
├── models/                     # Serialized model, scaler, feature list (.pkl)
├── reports/
│   ├── figures/                # 11 EDA/model PNG charts
│   └── business/                # Data quality, EDA insights, coefficients, Word report
├── dashboard/                  # Excel dashboard + Tableau extract (dashboard/tableau/)
├── docs/                       # Business objective, data dictionary, Tableau build guide
└── requirements.txt
```

---

## Pipeline Modules (`src/`)

| File | Phase | Purpose |
|---|---|---|
| `schema_validation.py` | 1 | Validates raw data structure/types/categories |
| `data_quality.py` | 2 | Missing values, duplicates, outliers, class balance diagnostics |
| `eda.py` | 3 | Generates 10 univariate/bivariate/multivariate charts |
| `feature_engineering.py` | 4 | Cleans data + engineers 10 business features |
| `modeling.py` | 5 | Logistic Regression pipeline: split/encode/scale/train/evaluate |
| `explainability.py` | 6 | Global feature importance + borrower-level explanations |
| `risk_scoring.py` | 7 | Converts PD → Credit Risk Score (300-900) → Risk Tier |
| `loan_decision_engine.py` | 8 | Rule-based approval decisioning with justifications |
| `build_dashboard.py` | 9 | Builds the Excel Portfolio Risk Dashboard |
| `build_report.js` | 10 | Builds the Word Business Advisory Report |
| `recommendation_simulator.py` | 11 | Single-applicant real-time recommendation function |

---

## Feature Descriptions

See `docs/data_dictionary.md` for the original 12 source columns, and
`reports/business/data_quality_report.md` for known issues and remediation.

**Key engineered features** (Phase 4):
- `loan_percent_income` — recomputed loan-to-income ratio
- `debt_to_income_ratio` — implied annual debt burden (amount × rate / income)
- `income_band`, `age_group`, `employment_stability`, `credit_history_category` — binned segments for reporting
- `flag_prior_default`, `flag_high_loan_burden`, `flag_low_income_high_grade_risk`, `flag_renter` — rule-based risk flags used in dashboarding and decisioning

---

## Methodology

1. **Data Quality (Phase 2):** identified 165 duplicates, 7 corrupted rows
   (implausible age/employment length), and missing values in 2 columns.
2. **EDA (Phase 3):** identified loan grade, loan-to-income ratio, prior
   bureau default, income, and home ownership as the dominant risk drivers.
3. **Feature Engineering (Phase 4):** removed 172 invalid rows (0.53%),
   imputed missing values, added 10 engineered features.
4. **Modeling (Phase 5):** Logistic Regression with `class_weight='balanced'`
   to address the 78/22 class imbalance; standardized features for
   interpretable coefficients.
5. **Explainability (Phase 6):** global importance from standardized
   coefficients; borrower-level narrative explanations from per-feature
   contribution decomposition.
6. **Risk Scoring (Phase 7):** linear PD→score mapping (300-900) for full
   auditability — validated by monotonically increasing observed default
   rate across tiers (3.98% → 70.5%).
7. **Decision Engine (Phase 8):** rule-based layer combining risk tier with
   hard policy overrides (e.g., mandatory review for prior bureau defaults).

---

## Results

| Metric | Value |
|---|---|
| ROC-AUC | 0.876 |
| Recall (Default class) | 78.8% |
| Precision (Default class) | 53.8% |
| F1 Score (Default class) | 0.640 |
| Accuracy | 80.6% |

**Portfolio decisioning:** 52.4% Approve, 10.4% Approve with Conditions,
17.0% Manual Review, 20.2% Reject.

---

## Installation & Reproduction

```bash
pip install -r requirements.txt

# Run the full pipeline in order:
python src/schema_validation.py
python src/data_quality.py
python src/eda.py
python src/feature_engineering.py
python src/modeling.py
python src/explainability.py
python src/risk_scoring.py
python src/loan_decision_engine.py
python src/build_dashboard.py
node src/build_report.js          # requires: npm install docx
python src/recommendation_simulator.py
```

### Using the Simulator Programmatically

```python
from src.recommendation_simulator import simulate_applicant

applicant = {
    "person_age": 30, "person_income": 60000, "person_home_ownership": "RENT",
    "person_emp_length": 3, "loan_intent": "PERSONAL", "loan_grade": "C",
    "loan_amnt": 8000, "loan_int_rate": 12.5,
    "cb_person_default_on_file": "N", "cb_person_cred_hist_length": 5,
}
result = simulate_applicant(applicant)
print(result)
```

---

## Key Deliverables

- 📊 `dashboard/Credit_Risk_Portfolio_Dashboard.xlsx` — Excel executive KPI dashboard
- 📊 `dashboard/tableau/credit_risk_data.hyper` — Native Tableau extract (open directly in Tableau Desktop/Public); see `docs/tableau_build_guide.md` for the full dashboard build spec (calculated fields, worksheet layout, cross-filter actions)
- 📄 `reports/business/Credit_Risk_Advisory_Report.docx` — Consulting-style advisory report
- 📈 `reports/figures/` — 16+ analytical charts (EDA, SHAP, threshold optimization, risk heatmaps)
- 🗂️ `data/processed/credit_risk_decisions.csv` — Full scored & decisioned portfolio
- 🧠 `models/` — Trained model artifacts (Logistic Regression + challenger models)

---

## Future Scope

- Add macroeconomic indicators for through-the-cycle risk sensitivity
- Test challenger models (Gradient Boosting, XGBoost, Random Forest)
- Extend explainability with SHAP values
- Deploy as a real-time scoring API integrated into loan origination systems
- Add cost-sensitive threshold optimization (business impact calculator)

## Reproducibility and limitations
See [setup and validation notes](docs/REPRODUCING.md).
