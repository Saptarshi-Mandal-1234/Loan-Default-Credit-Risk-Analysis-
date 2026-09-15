# Business Objective & KPIs

## Business Context
A retail lending institution's Credit Risk Department needs to reduce losses from
loan defaults while maintaining healthy loan approval volume (avoiding excessive
rejection of creditworthy applicants). Currently, approval decisions rely on
manual underwriter judgement and static bureau grades, which is slow, inconsistent,
and does not quantify default probability at the individual applicant level.

## Business Objective
Build an AI-powered Credit Risk Advisory System that:
1. Quantifies the probability of default (PD) for each applicant at underwriting time.
2. Explains *why* an applicant is risky, in language underwriters and credit
   committees can act on.
3. Converts PD into a standardized Credit Risk Score (300–900) and risk tier.
4. Recommends an approval action (Approve / Approve with Conditions / Manual
   Review / Reject) with business justification.
5. Gives portfolio-level visibility (dashboards, executive reporting) so risk
   managers can monitor exposure and default trends over time.

## Primary Stakeholders
- Credit Risk Department (model owner, monitoring)
- Underwriters / Credit Committee (decision consumers)
- Executive / CFO (portfolio exposure, loss trends)

## Key Performance Indicators (KPIs)

### Model Performance KPIs
| KPI | Target / Rationale |
|---|---|
| ROC-AUC | ≥ 0.75 acceptable for a first-generation PD model on this feature set |
| Recall (Default class) | Prioritized — missing a true default (false negative) is costlier than a false positive in credit risk |
| Precision (Default class) | Monitored to control false-positive rejection of good customers |
| F1 Score | Balances precision/recall trade-off |

### Business / Portfolio KPIs
| KPI | Description |
|---|---|
| Portfolio Default Rate | % of loans in default — headline risk metric |
| Total Portfolio Exposure | Sum of `loan_amnt` across all active loans |
| Average Loan Amount / Average Income | Portfolio composition monitoring |
| High-Risk Customer Count | Applicants in "High" / "Very High" risk tiers |
| Approval Rate by Risk Tier | Are risk-based decisions being applied consistently? |
| Cost of False Approvals | Estimated financial loss from approving loans that later default |
| Default Rate by Loan Purpose / Segment | Identifies concentrated risk segments |

These KPIs will be operationalized in Phase 9 (Portfolio Risk Dashboard) and
referenced throughout EDA (Phase 3) and the Business Advisory Report (Phase 10).
