# C1 | Customer portfolio concentration

**Course:** Business Intelligence IIB423T-1  
**Authors:** Moisés Medina and Ignacia Castillo  
**Case:** UCI Online Retail, 1 December 2010–30 November 2011  
**Version:** 29 September 2026 — final presentation PDF

The report and presentation are in English. They incorporate the W1 comparison of customer concentration (A) and C-coded cancellation records (B), then explain why A advanced. They define a proposed business decision and KPI, document source and row-level preparation, validate the analytical population, present decision-focused EDA, state the main insight, and check sensitivity. They do not assert the anonymous retailer's real mission, targets, profit, customer churn, or causal effects.

## Reading order

1. `report/GROUP_Medina_Castillo_C1_Report.pdf` — the self-contained report.
2. `presentation/GROUP_Medina_Castillo_C1_Slides.pdf` — final 15-slide presentation exported from Canva on 29 September 2026. The editable design is [Customer Concentration in Canva](https://www.canva.com/design/DAHWhvSX3_U/D4-Wlo5F4k7fk6IA_7uMGA/edit); the included PDF is the fixed submission copy.
3. `analysis/C1_customer_portfolio.ipynb` — executed evidence notebook.
4. `analysis/c1_analysis.py` — maintained preparation, validation, EDA and figure generation.
5. `data/online_retail_2010dec_2011nov_input.csv` — unchanged 12-month source extract.
6. `data/prepared_lines.csv` — one record per source row, with its positional `source_row` key, quality flags, mutually exclusive group and eligible line value. Original fields remain in the unchanged input CSV.
7. `data/report_metrics.json`, `data/sensitivity.csv`, `data/monthly_kpi.csv`, `data/invoice_frequency_groups.csv` — checkable figures behind the report and slides.

## Reproduce

The submitted analysis was reproduced from an extracted copy on Python 3.12.5 with NumPy 2.1.0, pandas 2.2.2, Matplotlib 3.9.2, nbformat 5.11.1, nbclient 0.11.0 and ipykernel 6.29.5. Compatible versions are specified in `requirements.txt`. From this folder, run:

```powershell
python -m pip install -r requirements.txt
python analysis/c1_analysis.py
python analysis/make_notebook.py
```

The analysis script checks the input and writes the prepared data, summary CSV files, figures and `report_metrics.json`. The notebook builder runs the same maintained code and saves all notebook outputs. It does not need internet access. The LaTeX source is `report/GROUP_Medina_Castillo_C1_Report.tex`; the submitted PDF was compiled with bundled Tectonic 0.17.0. If code, data or results change, update the report values and interpretation before compiling.

## Source and scope

Source: Daqing Chen (2015), [*Online Retail*, UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0. The original XLSX holds 541,909 rows; the included CSV retains all 516,384 source lines dated `2010-12-01 <= InvoiceDate < 2011-12-01`, with all eight original columns. The source file and extraction details are documented in `data/source_manifest.json`. The C1 script asserts the extract's schema, dates and size and records its SHA-256 in `data/report_metrics.json`.

To reconstruct the reduced input if needed, download `Online Retail.xlsx` from the UCI page above, check its SHA-256 against `data/source_manifest.json`, retain every row satisfying the stated half-open date filter in source order, and retain the eight original columns without deduplication or imputation. The reduced CSV is already included, so reproduction of the submitted results does not depend on a new download.

Rows are never removed from the prepared file. The baseline KPI uses eligible positive priced merchandise lines with a known customer ID. Its numerator and denominator are precisely defined in the report. Alternate row treatments appear in `data/sensitivity.csv`; they are not silently mixed into the baseline.

## Status

The final presentation PDF has 15 slides. Earlier local PowerPoint files and presenter notes were drafts and are not part of this submission. The report records that case-specific instructor feedback on the retail-domain fit is pending. The course's generic filename convention uses a two-digit group ID; this team has not received one, so the Medina_Castillo identifier is used consistently in the package.
