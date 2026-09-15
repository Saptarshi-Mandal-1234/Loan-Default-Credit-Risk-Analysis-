"""
Phase 9 — Portfolio Risk Dashboard (Excel)
Builds an executive-facing workbook: raw data + KPI formulas + charts.
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter

df = pd.read_csv("data/processed/credit_risk_decisions.csv")

# Keep dashboard-relevant columns to keep file size reasonable
cols = ["person_age","person_income","person_home_ownership","person_emp_length",
        "loan_intent","loan_grade","loan_amnt","loan_int_rate","loan_status",
        "loan_percent_income","cb_person_default_on_file","cb_person_cred_hist_length",
        "income_band","age_group","default_probability","credit_risk_score",
        "risk_tier","loan_decision"]
data = df[cols].copy()

wb = Workbook()

# ---------- Sheet 1: Raw Data ----------
ws_data = wb.active
ws_data.title = "Loan_Data"
ws_data.append(cols)
for r in data.itertuples(index=False):
    ws_data.append(list(r))

header_fill = PatternFill("solid", start_color="1F4E78", end_color="1F4E78")
header_font = Font(bold=True, color="FFFFFF", name="Arial")
for cell in ws_data[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")
ws_data.freeze_panes = "A2"
for i, col in enumerate(cols, 1):
    ws_data.column_dimensions[get_column_letter(i)].width = max(14, len(col) + 2)

n_rows = len(data) + 1  # including header
data_range = f"Loan_Data!$A$2:$A${n_rows}"

# Column letter lookup
col_letter = {c: get_column_letter(i+1) for i, c in enumerate(cols)}

def rng(col):
    return f"Loan_Data!${col_letter[col]}$2:${col_letter[col]}${n_rows}"

# ---------- Sheet 2: Executive KPIs ----------
ws_kpi = wb.create_sheet("Executive_KPIs")
ws_kpi.sheet_view.showGridLines = False

title_font = Font(bold=True, size=16, name="Arial", color="1F4E78")
label_font = Font(bold=True, size=11, name="Arial")
value_font = Font(size=14, bold=True, name="Arial", color="1F4E78")

ws_kpi["A1"] = "Credit Risk Portfolio — Executive Dashboard"
ws_kpi["A1"].font = title_font
ws_kpi.merge_cells("A1:D1")

kpis = [
    ("Total Loans", f"=COUNTA({rng('loan_status')})", "#,##0"),
    ("Default Rate", f"=AVERAGE({rng('loan_status')})", "0.0%"),
    ("Average Loan Amount ($)", f"=AVERAGE({rng('loan_amnt')})", "$#,##0"),
    ("Average Income ($)", f"=AVERAGE({rng('person_income')})", "$#,##0"),
    ("Total Portfolio Exposure ($)", f"=SUM({rng('loan_amnt')})", "$#,##0"),
    ("High-Risk Customers (High+Very High)",
     f'=COUNTIF({rng("risk_tier")},"High")+COUNTIF({rng("risk_tier")},"Very High")', "#,##0"),
    ("Approval Rate", f'=(COUNTIF({rng("loan_decision")},"Approve")+COUNTIF({rng("loan_decision")},"Approve with Conditions"))/COUNTA({rng("loan_decision")})', "0.0%"),
    ("Reject Rate", f'=COUNTIF({rng("loan_decision")},"Reject")/COUNTA({rng("loan_decision")})', "0.0%"),
]

row = 3
for label, formula, numfmt in kpis:
    ws_kpi.cell(row=row, column=1, value=label).font = label_font
    c = ws_kpi.cell(row=row, column=3, value=formula)
    c.font = value_font
    c.number_format = numfmt
    row += 1

# ---------- Aggregation tables (for charts) ----------
ws_agg = wb.create_sheet("Chart_Data")
ws_agg.sheet_view.showGridLines = False

# Default rate by loan_intent
intents = sorted(data["loan_intent"].unique())
ws_agg["A1"] = "Loan Purpose"
ws_agg["B1"] = "Default Rate"
for i, val in enumerate(intents, start=2):
    ws_agg.cell(row=i, column=1, value=val)
    ws_agg.cell(row=i, column=2,
                value=f'=AVERAGEIF({rng("loan_intent")},A{i},{rng("loan_status")})').number_format = "0.0%"

# Default rate by income band
bands = ["<25k","25-50k","50-75k","75-100k","100k+"]
start_row = len(intents) + 3
ws_agg.cell(row=start_row, column=1, value="Income Band")
ws_agg.cell(row=start_row, column=2, value="Default Rate")
for i, val in enumerate(bands, start=start_row+1):
    ws_agg.cell(row=i, column=1, value=val)
    ws_agg.cell(row=i, column=2,
                value=f'=AVERAGEIF({rng("income_band")},A{i},{rng("loan_status")})').number_format = "0.0%"

# Risk tier distribution
tiers = ["Very Low","Low","Moderate","High","Very High"]
start_row2 = start_row + len(bands) + 3
ws_agg.cell(row=start_row2, column=1, value="Risk Tier")
ws_agg.cell(row=start_row2, column=2, value="Count")
for i, val in enumerate(tiers, start=start_row2+1):
    ws_agg.cell(row=i, column=1, value=val)
    ws_agg.cell(row=i, column=2, value=f'=COUNTIF({rng("risk_tier")},A{i})')

# Approval distribution
decisions = ["Approve","Approve with Conditions","Manual Review","Reject"]
start_row3 = start_row2 + len(tiers) + 3
ws_agg.cell(row=start_row3, column=1, value="Decision")
ws_agg.cell(row=start_row3, column=2, value="Count")
for i, val in enumerate(decisions, start=start_row3+1):
    ws_agg.cell(row=i, column=1, value=val)
    ws_agg.cell(row=i, column=2, value=f'=COUNTIF({rng("loan_decision")},A{i})')

ws_agg.column_dimensions["A"].width = 24
ws_agg.column_dimensions["B"].width = 14

# ---------- Sheet 3: Charts ----------
ws_charts = wb.create_sheet("Dashboard_Charts")
ws_charts.sheet_view.showGridLines = False
ws_charts["A1"] = "Portfolio Risk Charts"
ws_charts["A1"].font = title_font

# Chart 1: Default by Purpose
c1 = BarChart()
c1.title = "Default Rate by Loan Purpose"
c1.y_axis.title = "Default Rate"
data_ref = Reference(ws_agg, min_col=2, min_row=1, max_row=1+len(intents))
cats_ref = Reference(ws_agg, min_col=1, min_row=2, max_row=1+len(intents))
c1.add_data(data_ref, titles_from_data=True)
c1.set_categories(cats_ref)
ws_charts.add_chart(c1, "A3")

# Chart 2: Default by Income Band
c2 = BarChart()
c2.title = "Default Rate by Income Band"
c2.y_axis.title = "Default Rate"
data_ref2 = Reference(ws_agg, min_col=2, min_row=start_row, max_row=start_row+len(bands))
cats_ref2 = Reference(ws_agg, min_col=1, min_row=start_row+1, max_row=start_row+len(bands))
c2.add_data(data_ref2, titles_from_data=True)
c2.set_categories(cats_ref2)
ws_charts.add_chart(c2, "A20")

# Chart 3: Risk Distribution (Pie)
c3 = PieChart()
c3.title = "Risk Tier Distribution"
data_ref3 = Reference(ws_agg, min_col=2, min_row=start_row2, max_row=start_row2+len(tiers))
cats_ref3 = Reference(ws_agg, min_col=1, min_row=start_row2+1, max_row=start_row2+len(tiers))
c3.add_data(data_ref3, titles_from_data=True)
c3.set_categories(cats_ref3)
ws_charts.add_chart(c3, "J3")

# Chart 4: Approval Distribution (Pie)
c4 = PieChart()
c4.title = "Approval Decision Distribution"
data_ref4 = Reference(ws_agg, min_col=2, min_row=start_row3, max_row=start_row3+len(decisions))
cats_ref4 = Reference(ws_agg, min_col=1, min_row=start_row3+1, max_row=start_row3+len(decisions))
c4.add_data(data_ref4, titles_from_data=True)
c4.set_categories(cats_ref4)
ws_charts.add_chart(c4, "J20")

wb.save("dashboard/Credit_Risk_Portfolio_Dashboard.xlsx")
print("Dashboard saved.")
