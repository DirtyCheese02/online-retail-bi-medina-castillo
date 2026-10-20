"""Build and execute the C1 evidence notebook from the maintained analysis code."""

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "C1_customer_portfolio.ipynb"

cells = [
    nbf.v4.new_markdown_cell("""# C1 | Customer portfolio concentration
**Moisés Medina and Ignacia Castillo** · Business Intelligence · 26 September 2026

This notebook reproduces the C1 data preparation and diagnostic EDA. The decision, population, formulas, row treatments and interpretive limits are explained in the accompanying report. The source CSV is an uncleaned, date-filtered copy of the UCI Online Retail file; the original rows are preserved.

**From W1 to C1.** We compared customer-value concentration (Candidate A) with monitoring C-coded cancellation records (Candidate B). We chose A because it has a directly observable value numerator, identifiable customers and a measurable missing-ID boundary. B remains a useful descriptive process question, but the file cannot link a C record to its original purchase or provide its reason. We also set aside a November/Christmas explanation: one annual cycle does not establish seasonality."""),
    nbf.v4.new_markdown_cell("""## 1. Rebuild and validate
`c1_analysis.py` checks schema, date range, row counts, mutually exclusive analytical groups, positive eligible line values, and invoice-to-customer consistency. It writes `prepared_lines.csv` with row-level flags and never overwrites the source extract."""),
    nbf.v4.new_code_cell("""from pathlib import Path
import json
import pandas as pd
from IPython.display import display, Image
from c1_analysis import ROOT, main
main()
DATA = ROOT / 'data'
FIGURES = ROOT / 'analysis' / 'figures'
metrics = json.loads((DATA / 'report_metrics.json').read_text(encoding='utf-8'))
display(pd.Series({k: metrics[k] for k in ['source_rows', 'eligible_purchase_lines', 'eligible_c_lines', 'other_retained', 'missing_customer_id_raw', 'exact_duplicates_raw', 'nonpositive_price_raw', 'outside_merchandise_rule_raw']}))"""),
    nbf.v4.new_markdown_cell("""The quality flags overlap. The row groups do not: each source line is assigned to priced purchase, priced C record, or other retained. A blank customer ID excludes a line only from customer ranks; it remains in total eligible value and coverage calculations. Zero prices are not filled with another invoice's price because that would invent a charge."""),
    nbf.v4.new_code_cell("""quality = pd.read_csv(DATA / 'quality_by_month.csv')
display(quality)
prepared = pd.read_csv(DATA / 'prepared_lines.csv', usecols=['row_group', 'missing_customer_id', 'exact_duplicate'])
assert len(prepared) == metrics['source_rows']
display(prepared['row_group'].value_counts())
del prepared"""),
    nbf.v4.new_markdown_cell("""## 2. Provisional KPI and data-quality guardrail
For identifiable customers, sum eligible positive purchase-line value (`Quantity × UnitPrice`) over the observed year. Rank IDs by that value. The KPI is the share of known-ID value held by the highest-value `ceil(10% × N)` IDs. Known-ID value coverage is a mandatory guardrail, not another estimate of the same construct. This is recorded gross purchase value, not reconciled net revenue, profit, churn, or lifetime value."""),
    nbf.v4.new_code_cell("""display(pd.Series(metrics['baseline']))
display(pd.Series(metrics['customer_value_stats']))
display(pd.Series(metrics['customer_invoice_stats']))
print('Invoice-frequency/value Pearson:', round(metrics['pearson_customer_invoice_count_vs_value'], 3))
print('Invoice-frequency/value Spearman:', round(metrics['spearman_customer_invoice_count_vs_value'], 3))
print('Purchase invoices entirely without ID:', metrics['purchase_invoices_entirely_without_id'])
print('Purchase invoices with a mix of known and missing IDs:', metrics['purchase_invoices_with_mixed_known_missing_id'])"""),
    nbf.v4.new_markdown_cell("""## 3. Distribution and association after validation
The mean and median describe different customers because the observed value distribution is strongly skewed. The ECDF and quantiles show its shape without assuming normality. Pearson and Spearman differ in this long-tailed setting. Invoice frequency and value are associated, but value partly accumulates through more invoices; this relationship is descriptive and does not show that an intervention will cause repeat purchases."""),
    nbf.v4.new_code_cell("""for name in ['customer_value_distribution.png', 'customer_value_ecdf.png', 'frequency_value_scatter.png', 'concentration_curve.png']:
    display(Image(filename=str(FIGURES / name)))"""),
    nbf.v4.new_code_cell("""frequency_groups = pd.read_csv(DATA / 'invoice_frequency_groups.csv')
display(frequency_groups.round(2))"""),
    nbf.v4.new_markdown_cell("""## 4. Segmentation and coverage
Each monthly top-decile calculation reranks active known IDs, so its percentages are not directly equivalent to the full-year KPI. Monthly changes in known-ID coverage can change the observed customer population. UK and non-UK rows are descriptive customer-country segments, not verified shipping markets or a causal comparison."""),
    nbf.v4.new_code_cell("""monthly = pd.read_csv(DATA / 'monthly_kpi.csv')
segments = pd.read_csv(DATA / 'uk_segment_kpi.csv')
display(monthly[['month', 'purchase_value_gbp', 'known_id_customers', 'known_id_coverage_pct', 'top_decile_share_pct']].round(2))
display(segments.round(2))
display(Image(filename=str(FIGURES / 'monthly_concentration_coverage.png')))"""),
    nbf.v4.new_markdown_cell("""## 5. Sensitivity and decision limit
Removing exact repeats, narrowing or broadening the stock-code rule, and removing the largest ID are alternative populations, not repairs silently applied to the baseline. The last scenario diagnoses dependence on one account; it changes the target population. We cannot determine whether missing-ID purchases are distributed like identified purchases."""),
    nbf.v4.new_code_cell("""sensitivity = pd.read_csv(DATA / 'sensitivity.csv')
display(sensitivity[['scenario', 'customers', 'known_value_gbp', 'top_decile_share_pct', 'known_id_value_coverage_pct']].round(2))
assert abs(sensitivity.loc[0, 'top_decile_share_pct'] - metrics['baseline']['top_decile_share_pct']) < 1e-9"""),
    nbf.v4.new_markdown_cell("""**Main insight.** The concentration reflects a portfolio pattern, not just one extreme ID: the top 430 of 4,293 known IDs account for 60.5% of known-ID value; the largest single ID accounts for 3.25%. The 36.1% observed in only one eligible purchase invoice contribute 7.8% of known-ID value, while the two-or-more-invoice group contributes 92.2%. This supports a closer review of major observed accounts and ID capture. It does not prove loyalty or justify spending on retention. The unknown-ID share (14.3% of eligible value), one-year window, product-code convention and absence of linked payments prevent a claim about all customers, lifetime value or profit."""),
]

notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
client = NotebookClient(notebook, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(ROOT / "analysis")}})
executed = client.execute()
nbf.write(executed, OUT)
print(OUT)
