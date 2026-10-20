# C1 process record

## Decision and scope

- The case question was narrowed to customer concentration in recorded positive priced purchase value. The anonymous source provides no mission, vision, financial target or account-management policy, so the report frames a proposed portfolio-review decision rather than attributing one to the retailer.
- W1 compared customer concentration with monitoring C-coded cancellation records. Candidate A advanced because its customer-value denominator and missing-ID boundary can be measured; Candidate B remains descriptive because the file lacks an original-purchase link and cancellation reason. A single-year November peak was not used as a seasonal claim.
- The unit of source observation is an invoice line. Positive purchase lines are aggregated to invoices and identifiable customers; cancellation records are a separate row group. The period is 12 complete months from December 2010 through November 2011; the source's partial December 2011 is outside this case.
- The top-decile share is calculated only within known-ID eligible value. Known-ID coverage is displayed as a validity guardrail. No missing ID or zero price is imputed.

## AI assistance and checks

- As in W1, AI assisted with first drafts of the written report and Python code, including `analysis/c1_analysis.py`, the executed notebook generator, figures and LaTeX layout. The request was to close Candidate A, build and validate an analytical dataset, perform directed EDA, define the KPI and its action rule, and produce a report like the W1 report. The team chose the business question, analytical population, KPI scope, final interpretation and decision implications.
- Accepted: row-level flags before exclusion, mutually exclusive analytical groups, mean/median and ECDF comparisons, monthly ID-coverage checks, and explicit sensitivity populations.
- After reviewing the three course lecture files, added IQR and MAD to the report, compared Pearson with Spearman, and displayed one-invoice versus two-or-more-invoice groups. This supports the EDA insight while keeping it descriptive.
- Rejected as claims: that the retailer actually follows the proposed strategy; that zero prices are known discounts; that exact repeats are proven errors; that one-invoice IDs are new or churned customers; that C-coded rows can be matched to original purchases; that November's pattern proves a Christmas mechanism.
- Verification: the script asserts source schema, date range, 516,384 rows, disjoint row groups totaling the source, positive eligible line values and invoice-to-ID consistency. The notebook was executed from first cell to last. The PDF was compiled and visually inspected; reported numbers were cross-checked against generated CSV and JSON outputs.

## Remaining questions for discussion

- Can a decision-maker supply a meaningful concentration tolerance or review cost? The current rule triggers investigation, not an automatic intervention.
- Are missing customer IDs concentrated in a particular order process? The recorded file cannot establish why they are absent.
- Can product-code definitions, payments, cancellations and customer identity be verified from operational records before a financial or retention claim?
