# Data Dictionary — Credit Risk Dataset

**Source file:** `data/raw/credit_risk_dataset.csv`
**Rows:** 32,581 | **Columns:** 12
**Grain:** One row = one historical loan application/borrower record

| # | Column | Type | Description | Business Meaning |
|---|--------|------|-------------|-------------------|
| 1 | `person_age` | int | Applicant's age (years) | Demographic risk factor; also used for regulatory fair-lending checks |
| 2 | `person_income` | int | Applicant's annual income (USD) | Core repayment capacity indicator |
| 3 | `person_home_ownership` | category (RENT, OWN, MORTGAGE, OTHER) | Housing status | Proxy for financial stability / collateral |
| 4 | `person_emp_length` | float | Years in current employment | Income stability signal |
| 5 | `loan_intent` | category (PERSONAL, EDUCATION, MEDICAL, VENTURE, HOMEIMPROVEMENT, DEBTCONSOLIDATION) | Stated purpose of loan | Different purposes carry different historical default rates |
| 6 | `loan_grade` | category (A–G) | Internal/bureau credit grade at origination | Ordinal risk grade, A = lowest risk, G = highest |
| 7 | `loan_amnt` | int | Approved/requested loan amount (USD) | Exposure size |
| 8 | `loan_int_rate` | float | Interest rate (%) charged on the loan | Risk-based pricing; correlates with grade |
| 9 | `loan_status` | int (0/1) | **TARGET.** 1 = Default, 0 = Non-default (fully paid/current) | What we are predicting |
| 10 | `loan_percent_income` | float | `loan_amnt / person_income` | Debt-service burden ratio |
| 11 | `cb_person_default_on_file` | category (Y/N) | Has a prior default on credit bureau file | Historical delinquency flag |
| 12 | `cb_person_cred_hist_length` | int | Length of credit history (years) | Depth of credit track record |

## Known Data Quality Flags (to be formally profiled in Phase 2)
- `person_age`: max value = 144 (implausible; needs outlier treatment)
- `person_emp_length`: max value = 123 years (implausible; needs outlier treatment)
- `person_emp_length`: 895 missing values
- `loan_int_rate`: 3,116 missing values
- 165 duplicate rows detected

These are noted here for transparency but **not treated yet** — formal treatment occurs in Phase 2 (Data Quality Assessment) per the agreed workflow.
