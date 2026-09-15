const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, PageBreak
} = require("docx");

const NAVY = "1F4E78";
const LIGHTGREY = "F2F2F2";

const h1 = (text) => new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
const h2 = (text) => new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } });
const p = (text, opts = {}) => new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
const bullet = (text) => new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });

function makeTable(headers, rows) {
  const headerRow = new TableRow({
    children: headers.map(hText => new TableCell({
      width: { size: Math.floor(9000 / headers.length), type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: NAVY },
      children: [new Paragraph({ children: [new TextRun({ text: hText, bold: true, color: "FFFFFF" })] })]
    }))
  });
  const dataRows = rows.map(r => new TableRow({
    children: r.map(cellText => new TableCell({
      width: { size: Math.floor(9000 / headers.length), type: WidthType.DXA },
      children: [new Paragraph({ text: String(cellText) })]
    }))
  }));
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: headers.map(() => Math.floor(9000 / headers.length)),
    rows: [headerRow, ...dataRows],
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Credit Risk Portfolio Advisory Report", bold: true, size: 44, color: NAVY })],
        spacing: { after: 100 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "Prepared for the Credit Risk Committee | AI-Powered Credit Risk Advisory System", italics: true, size: 22, color: "555555" })],
        spacing: { after: 400 }
      }),

      h1("1. Executive Summary"),
      p("This report summarizes findings from an end-to-end credit risk analytics initiative covering 32,409 cleaned loan records. The portfolio carries a default rate of 21.9%, with clear, statistically validated risk drivers identified through exploratory analysis and a logistic regression model achieving a ROC-AUC of 0.876 and 78.8% recall on defaulted loans."),
      p("A standardized Credit Risk Score (300-900) and a rule-based Loan Decision Engine were built on top of the model, translating statistical risk into auditable, committee-ready approval recommendations: 52.4% Approve, 10.4% Approve with Conditions, 17.0% Manual Review, and 20.2% Reject."),

      h1("2. Portfolio Overview"),
      makeTable(
        ["Metric", "Value"],
        [
          ["Total Loans (post-cleaning)", "32,409"],
          ["Overall Default Rate", "21.9%"],
          ["Total Portfolio Exposure", "$310,882,900"],
          ["Average Loan Amount", "$9,592"],
          ["Average Applicant Income", "$65,894"],
          ["High-Risk Customers (High + Very High tier)", "9,447 (29.2%)"],
        ]
      ),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h1("3. Key Findings"),
      bullet("Loan grade is the strongest single risk driver: default rate rises from 10.0% (Grade A) to 98.4% (Grade G), a near-monotonic risk ladder."),
      bullet("Loan-to-income ratio is the strongest driver in the multivariate model (largest standardized coefficient) — it adds predictive power independent of grade."),
      bullet("Applicants with a prior bureau default on file default at roughly double the rate of those without (37.6% vs 18.1%)."),
      bullet("Renters default at 31.1% versus 6.9% for outright homeowners — home ownership is a meaningful secondary risk signal."),
      bullet("Income is strongly protective: default rate falls from 51.5% (<$25k income) to 9.6% ($100k+ income)."),
      bullet("Debt consolidation and medical loans default most often among stated purposes (28.4% and 26.5%); venture and education loans default least (~14.7%)."),

      h1("4. High-Risk Segments"),
      p("The following borrower segments warrant elevated underwriting scrutiny or tightened policy:"),
      makeTable(
        ["Segment", "Observed Default Rate", "Recommended Action"],
        [
          ["Loan Grade F/G", "70.5% - 98.4%", "Reject by default; exception only via senior underwriter override"],
          ["Prior bureau default on file", "37.6%", "Mandatory manual review regardless of model score"],
          ["Income < $25k + Grade D-G", "High concentration of defaults", "Cap maximum loan-to-income ratio; require co-signer"],
          ["Renters with loan-to-income > 40%", "Elevated", "Approve with conditions (reduced amount, higher rate)"],
        ]
      ),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h1("5. Risk Drivers (Model-Based)"),
      p("Standardized logistic regression coefficients confirm the EDA findings and quantify relative impact:"),
      makeTable(
        ["Risk-Increasing Factors", "Risk-Decreasing Factors"],
        [
          ["Loan-to-income ratio (strongest)", "Loan amount (net of ratio effect)"],
          ["Loan Grade D/E/F/G", "Home ownership = Own"],
          ["Loan interest rate", "Loan purpose = Venture/Education"],
          ["Home ownership = Rent", "Longer applicant age"],
        ]
      ),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h1("6. Business Recommendations"),
      bullet("Adopt the Credit Risk Score (300-900) as the primary underwriting reference, replacing purely grade-based rules of thumb."),
      bullet("Enforce the loan-to-income ratio cap (recommend 35-40%) as a hard policy gate independent of bureau grade, since it carries independent predictive power."),
      bullet("Route all applicants with a prior bureau default to manual review, regardless of statistical score, as a compliance and prudence safeguard."),
      bullet("Introduce differentiated pricing (interest rate) for Grade C and below rather than binary approve/reject, to price for risk while preserving volume."),

      h1("7. Approval Strategy"),
      p("The Loan Decision Engine (Phase 8) operationalizes the above into four consistent actions: Approve (Very Low/Low risk), Approve with Conditions (Moderate risk or high loan burden), Manual Review (High risk or prior default flag), and Reject (Very High risk). This reduces underwriter inconsistency while preserving human oversight on borderline cases."),

      h1("8. Monitoring Strategy"),
      bullet("Track realized default rate by risk tier monthly; the model's calibration should be revisited if actual defaults drift more than 3-5 percentage points from the scored tier's historical rate."),
      bullet("Monitor the Approval Rate and Reject Rate trend to detect policy drift or unintended tightening/loosening of credit access."),
      bullet("Re-validate model coefficients quarterly as new loan performance data becomes available (concept drift risk)."),

      h1("9. Future Improvements"),
      bullet("Incorporate macroeconomic indicators (unemployment rate, interest rate environment) for through-the-cycle risk assessment."),
      bullet("Test ensemble models (Gradient Boosting, Random Forest) as challenger models against the logistic regression baseline."),
      bullet("Extend Explainable AI coverage with SHAP values for richer borrower-level explanations beyond linear coefficient contributions."),
      bullet("Build a real-time API-based scoring service to embed the model directly into the loan origination system."),

      new Paragraph({ text: "", spacing: { after: 200 } }),
      p("— End of Report —", { italics: true }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("reports/business/Credit_Risk_Advisory_Report.docx", buf);
  console.log("Report saved.");
});
