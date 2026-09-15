# Data Quality Report — Credit Risk Dataset

**Dataset:** `data/raw/credit_risk_dataset.csv` | 32,581 rows × 12 columns
**Prepared by:** Credit Risk Analytics | **Phase:** 2 — Data Quality Assessment
**Status:** Diagnosed only — no cleaning applied yet (treatment happens in Phase 4)

---

## 1. Missing Values

| Feature | Missing Count | Missing % |
|---|---|---|
| `loan_int_rate` | 3,116 | 9.56% |
| `person_emp_length` | 895 | 2.75% |

**Assessment:** Moderate missingness in `loan_int_rate`, likely Missing Not At
Random (MNAR) if certain loan grades have rates assigned later in the process —
should not be dropped, needs group-aware imputation (e.g., by `loan_grade`).
`person_emp_length` missingness is low-impact.

---

## 2. Duplicate Records

- **165 fully duplicate rows (0.51% of data).**
- **Recommendation:** Remove — duplicate borrower/loan records would
  artificially inflate confidence in patterns during EDA and bias model training.

---

## 3. Invalid / Business-Rule Violations

| Check | Count |
|---|---|
| `person_age` > 100 | 5 |
| `person_emp_length` > 60 years | 2 |
| `person_emp_length` > `person_age` (logically impossible) | 2 |
| Zero/negative income | 0 |
| Zero/negative loan amount | 0 |

**Assessment:** A handful of clearly corrupted records (e.g., age 144,
employment length 123 years). Small in count (≤5 rows) but must be removed —
they are data entry errors, not genuine tail-risk borrowers, and would distort
both EDA and model coefficients.

---

## 4. Statistical Outliers (IQR method, 1.5×IQR fences)

| Feature | Outlier Count | % of Data |
|---|---|---|
| `loan_amnt` | 1,689 | 5.18% |
| `person_income` | 1,484 | 4.55% |
| `cb_person_cred_hist_length` | 1,142 | 3.51% |
| `loan_percent_income` | 651 | 2.00% |
| `loan_int_rate` | 6 | 0.02% |

**Assessment:** These are *not* data errors — high income, large loans, and long
credit histories are legitimate (if less common) borrower profiles. **Do not
delete** these rows; they carry real risk signal. Flag for Winsorization or
robust scaling only if they destabilize the model in Phase 5.

---

## 5. Data Type Validation

All 12 columns match expected schema (confirmed in Phase 1 `schema_validation.py`
run: `passed: True`). No type coercion issues.

---

## 6. Feature Consistency Check

Cross-validated `loan_percent_income` against the computed ratio
`loan_amnt / person_income`:
- Max absolute discrepancy: 0.093
- 388 rows (1.2%) differ by more than 0.01

**Assessment:** Minor rounding/derivation inconsistency, not a major integrity
issue. We will recompute `loan_percent_income` ourselves in Phase 4 to guarantee
consistency rather than trust the source column.

---

## 7. Class Balance (Target: `loan_status`)

| Class | Count | % |
|---|---|---|
| 0 — Non-Default | 25,473 | 78.18% |
| 1 — Default | 7,108 | 21.82% |

**Assessment:** Moderately imbalanced (~1:3.6). Not severe enough to mandate
SMOTE/resampling by default, but model evaluation **must** prioritize
Recall/F1/ROC-AUC over raw Accuracy, and we will test `class_weight='balanced'`
in Phase 5 as a first mitigation.

---

## Summary of Required Actions (deferred to Phase 4 — Feature Engineering)

| Issue | Action | Priority |
|---|---|---|
| 165 duplicate rows | Drop | High |
| 5 age >100, 2 emp_length illogical rows | Drop (data entry errors) | High |
| `loan_int_rate` missing (9.56%) | Impute by `loan_grade` group median | High |
| `person_emp_length` missing (2.75%) | Impute by median | Medium |
| `loan_percent_income` inconsistency | Recompute from source columns | Medium |
| Statistical outliers (income, loan amount, credit history) | Retain; consider capping only if model destabilized | Low |

**Net effect:** ~172 rows (0.53%) will be removed as invalid; the rest of the
data quality issues are treatable via imputation/recomputation without losing
sample size — the dataset is fundamentally sound for modeling.
