# Tableau Dashboard Build Guide — Credit Risk Portfolio

This guide replaces the Excel dashboard (Phase 9) with a Tableau workbook.
Two data sources are provided — use whichever fits your setup:

| File | Use When |
|---|---|
| `dashboard/tableau/credit_risk_data.hyper` | **Preferred.** Native Tableau extract — open directly, zero import steps, fastest performance. |
| `data/processed/tableau_credit_risk_data.csv` | Fallback if `.hyper` won't open (e.g. Tableau Public web version) — connect as a Text File. |

**Note on dates:** the source dataset has no real transaction dates, so
`origination_date` / `origination_month` were **synthetically generated**
(uniformly randomized across 2023-2024) purely so you can build a Monthly
Trend view as requested in the original spec. This is clearly a simulated
field — call it out as such in any presentation of this project.

---

## 1. Connect

**Tableau Desktop / Public:**
1. Open Tableau → **Connect → To a File → More...**
2. Select `credit_risk_data.hyper` (or the `.csv` if using the fallback)
3. Drag `CreditRiskData` (or the CSV) onto the canvas → go to a new Sheet

Field roles you should double-check after connecting:
- `loan_id` → set to **Dimension**, String
- `origination_date` → should auto-detect as **Date**
- `loan_status` (0/1) → keep as **Measure**, but you'll mostly use `loan_status_label` (Dimension) for visuals
- `default_probability` → **Measure**, format as Percentage
- `credit_risk_score` → **Measure**, Number (whole)

---

## 2. Calculated Fields to Create

Go to **Analysis → Create Calculated Field** and add each of these:

### Default Rate
```
SUM([loan_status]) / COUNTD([loan_id])
```
Format as Percentage.

### Approval Rate
```
(COUNTD(IF [loan_decision] = "Approve" OR [loan_decision] = "Approve with Conditions"
 THEN [loan_id] END))
/ COUNTD([loan_id])
```

### High-Risk Customer Count
```
COUNTD(IF [risk_tier] = "High" OR [risk_tier] = "Very High" THEN [loan_id] END)
```

### Total Portfolio Exposure
```
SUM([loan_amnt])
```

### Revenue (True Approvals) — for the Business Impact view
```
SUM(IF [loan_decision] != "Reject" AND [loan_status] = 0
    THEN [loan_amnt] * [loan_int_rate] / 100 ELSE 0 END)
```

### Loss (False Approvals) — assumes 60% Loss Given Default (LGD), matching the Python model's assumption
```
SUM(IF [loan_decision] != "Reject" AND [loan_status] = 1
    THEN [loan_amnt] * 0.60 ELSE 0 END)
```

### Net Business Impact
```
[Revenue (True Approvals)] - [Loss (False Approvals)]
```

### Portfolio Health Score (simplified Tableau version of the Python composite score)
```
(
  (100 - ([Default Rate] * 100 * 2)) * 0.35 +
  ((AVG([credit_risk_score]) - 300) / 600 * 100) * 0.30 +
  (100 - ((COUNTD(IF [risk_tier] = "High" OR [risk_tier] = "Very High" THEN [loan_id] END)
           / COUNTD([loan_id])) * 100 * 1.5)) * 0.20 +
  ([Approval Rate] * 100) * 0.15
)
```
Wrap the whole thing in `MAX(0, MIN(100, ...))` if you want to hard-clip the 0-100 range.

---

## 3. Recommended Worksheets → Dashboard Layout

Build these individual sheets, then assemble into **one Executive Dashboard**
(Dashboard → New Dashboard, size: 1300x900 "Desktop"):

| # | Sheet Name | Chart Type | Fields |
|---|---|---|---|
| 1 | KPI Cards | Text/Big Number tiles | Total Loans (`COUNTD([loan_id])`), Default Rate, Total Exposure, Avg Loan Amount, Avg Income, High-Risk Count, Approval Rate |
| 2 | Default by Purpose | Horizontal Bar | Rows: `loan_intent`, Columns: `Default Rate`, sort descending |
| 3 | Default by Income Band | Bar | Rows: `income_band` (sort using a custom sort matching `<25k → 100k+`), Columns: `Default Rate` |
| 4 | Risk Tier Distribution | Pie or Donut | Angle: `COUNTD([loan_id])`, Color: `risk_tier` (use a Red→Green diverging palette, reversed so red = high risk) |
| 5 | Approval Distribution | Pie or Donut | Angle: `COUNTD([loan_id])`, Color: `loan_decision` |
| 6 | Monthly Trend | Line chart | Columns: `origination_month` (continuous), Rows: `Default Rate` — *label clearly as illustrative/simulated dates* |
| 7 | Risk Heatmap | Heatmap (Highlight Table) | Rows: `loan_grade`, Columns: `income_band`, Color: `Default Rate` |
| 8 | Persona Breakdown | Bar | Rows: `persona`, Columns: `Default Rate`, Color by `persona`, sort descending |
| 9 | Business Impact | Bar or Bullet | `Revenue (True Approvals)` vs `Loss (False Approvals)` vs `Net Business Impact` as 3 bars |

**Filters to add as dashboard-level controls:**
- `loan_grade` (multi-select)
- `income_band`
- `risk_tier`
- `origination_month` (date range slider)

**Actions:** Add a **Dashboard Action → Filter** so clicking a bar in "Risk Tier
Distribution" filters all other sheets — this is what makes it feel like a
real executive tool rather than a set of static charts.

---

## 4. Color & Formatting Guidance

- Use a **consistent risk palette** across every sheet: e.g.
  `Very Low = #2E7D32, Low = #66BB6A, Moderate = #FDD835, High = #FB8C00, Very High = #C62828`
  Set this once as a custom color palette (Tableau → Preferences → Edit Colors) so it applies everywhere.
- Format every rate/percentage field to 1 decimal (`0.0%`).
- Format currency fields with `$` and thousands separators (`$#,##0`).
- Title the dashboard **"Credit Risk Portfolio — Executive Dashboard"** and add
  a subtitle noting the data snapshot date and that `origination_date` is simulated.

---

## 5. Optional — Publish to Tableau Public

If you want a shareable link:
1. **Server → Tableau Public → Save to Tableau Public**
2. Sign in / create a free account
3. The workbook publishes with the extract embedded (no live connection needed)

---

## Files Provided for This Phase

- `dashboard/tableau/credit_risk_data.hyper` — native extract (32,409 rows, 32 columns)
- `data/processed/tableau_credit_risk_data.csv` — CSV fallback, same data
- This guide (`docs/tableau_build_guide.md`)

All Python-side analysis (EDA, modeling, SHAP, business impact, personas) from
the earlier phases remains valid — this phase only changes *how the portfolio
dashboard is delivered* (Tableau instead of Excel), per your request.
