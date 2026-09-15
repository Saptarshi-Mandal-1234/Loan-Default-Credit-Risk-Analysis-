# Exploratory Data Analysis — Business Insights Report

**Phase:** 3 | 10 charts generated in `reports/figures/`
**Note:** For visualization clarity only, the ~7 corrupted rows (age>100, illogical
employment length) were excluded from these charts. Full cleaning happens in Phase 4.

---

### 1. Loan Amount Distribution (`01_loan_amount_distribution.png`)
**Insight:** Right-skewed; most loans cluster between $5,000–$15,000, with a long
tail up to $35,000.
**Risk implication:** A small number of large-ticket loans carry disproportionate
exposure — worth monitoring as concentration risk even if individually low-probability.
**Recommendation:** Apply tiered scrutiny for loans above ~$20,000 regardless of grade.

### 2. Income Distribution (`02_income_distribution.png`)
**Insight:** Heavily right-skewed; bulk of applicants earn $30,000–$70,000/year.
**Risk implication:** Income alone is noisy — needs to be paired with loan size
(loan-to-income ratio) to be a useful risk signal.
**Recommendation:** Engineer a debt/loan-to-income ratio rather than relying on raw income (done in Phase 4).

### 3. Age & Employment Length (`03_age_employment_distribution.png`)
**Insight:** Applicant base skews young (concentrated 20s–30s); employment length
is similarly concentrated under 10 years.
**Risk implication:** A young portfolio means less credit-history depth on average —
elevated baseline risk vs. a more seasoned borrower base.
**Recommendation:** Weight employment stability and credit history length in the risk model.

### 4. Credit History & Loan Purpose (`04_credit_history_purpose.png`)
**Insight:** Credit history is short for most applicants (median ~4 years);
`DEBTCONSOLIDATION`, `EDUCATION`, and `MEDICAL` are the most common loan purposes.
**Risk implication:** Debt consolidation and medical loans often signal existing
financial strain.
**Recommendation:** Treat loan purpose as a meaningful categorical risk feature, not a formality field.

### 5. Default Rate by Income Band (`05_default_rate_by_income.png`)
**Insight:** Default rate falls sharply as income rises — **51.5%** for <$25k
down to **9.6%** for $100k+.
**Risk implication:** Income is one of the strongest single risk drivers in this portfolio.
**Recommendation:** Apply stricter debt-to-income thresholds for the <$50k income segment.

### 6. Loan Amount by Default Status (`06_loan_amount_vs_default.png`)
**Insight:** Defaulted loans skew toward larger amounts relative to non-defaults.
**Risk implication:** Larger loans are harder to service, compounding risk from other factors.
**Recommendation:** Cap maximum loan-to-income ratio more tightly as loan size increases.

### 7. Default Rate by Home Ownership & Loan Grade (`07_default_by_ownership_grade.png`)
**Insight:** Renters (**31.1%**) and "Other" housing (**30.8%**) default far more
than mortgage holders (**12.5%**) or owners (**6.9%**). Grade is a near-perfect
risk ladder: A=9.6% → G=98.4% default rate.
**Risk implication:** Loan grade is (as expected) the single strongest predictor
— but home ownership adds meaningful independent signal beyond grade.
**Recommendation:** Use loan grade as the anchor risk driver, home ownership as a key secondary filter.

### 8. Default Rate by Loan Purpose & Bureau Default Flag (`08_default_by_purpose_cbflag.png`)
**Insight:** Debt consolidation (28.4%) and medical (26.5%) loans default most;
venture (14.7%) and education (14.7%) least. Applicants with a prior bureau
default file default at **37.6%** vs **18.1%** for those without.
**Risk implication:** Prior default history roughly doubles default risk — a
strong, simple screening signal.
**Recommendation:** Flag `cb_person_default_on_file = Y` for mandatory manual review regardless of model score.

### 9. Correlation Heatmap (`09_correlation_heatmap.png`)
**Insight:** `loan_percent_income` (r=0.38) and `loan_int_rate` (r=0.34) are the
strongest linear correlates with default; `person_income` is negatively correlated (r=-0.16).
**Risk implication:** No single feature dominates — risk is multi-factor,
supporting a multivariate model over simple rule-based scoring.
**Recommendation:** Prioritize `loan_percent_income`, `loan_int_rate`, `loan_grade`,
and `person_income` as core model features.

### 10. Loan-to-Income Ratio by Grade, Split by Default (`10_loanpct_by_grade_default.png`)
**Insight:** Within every grade band, defaulted loans consistently show a higher
loan-to-income ratio than non-defaults — the effect holds even after controlling for grade.
**Risk implication:** Loan-to-income ratio is an independent risk driver, not just
a proxy for grade — it adds real predictive value on top of the bureau grade.
**Recommendation:** Include `loan_percent_income` explicitly in the model rather
than assuming grade captures it.

---

## EDA Summary — Top Risk Drivers Identified
1. **Loan grade** (A→G near-monotonic default ladder, 9.6%→98.4%)
2. **Prior bureau default flag** (roughly doubles risk)
3. **Loan-to-income ratio** (independent effect within every grade)
4. **Income level** (strong inverse relationship)
5. **Home ownership** (renters >> mortgage/own)
6. **Loan purpose** (debt consolidation/medical > venture/education)

These findings directly inform Phase 4 (Feature Engineering) and Phase 5 (Modeling).
