# Workshop 1 | Online Retail

**Course:** Business Intelligence IIB423T-1  
**Team:** Moisés Medina and Ignacia Castillo  
**Version:** 25 September 2026  
**Submission identifier:** `Medina_Castillo` (team surnames; no numeric group ID has been assigned).

This package presents our Workshop 1 analysis of the UCI Online Retail dataset. The report and notebook are in English. The PDF is the self-contained submission narrative; the Python files and CSV provide reproducible evidence.

## Reading order

1. `report/GROUP_Medina_Castillo_W1_Report.pdf` — two candidate lines, data checks, comparison, provisional preference, process record and references.
2. `analysis/W1_online_retail.ipynb` — executed notebook with saved outputs.
3. `data/online_retail_2010dec_2011nov_input.csv` — uncleaned input extract used by the notebook.
4. `analysis/retail_analysis.py` — extraction and analysis functions; `analysis/make_notebook.py` regenerates and executes the notebook.
5. `report/GROUP_Medina_Castillo_W1_Report.tex` — editable LaTeX source.

## Reproduce

The analysis was run with Python 3.12.5, pandas 2.2.2, matplotlib 3.9.2, openpyxl 3.1.5, nbformat 5.11.1, nbclient 0.11.0 and ipykernel 6.29.5. From this package root, install Python dependencies with `python -m pip install -r requirements.txt`. Start Jupyter from `analysis/`, open `W1_online_retail.ipynb`, restart its kernel, run all cells and save. The notebook also works when started from the package root. It reads the packaged CSV; it does not need an internet connection or the original XLSX.

To regenerate the tables and figures directly, run `python analysis/retail_analysis.py`. To regenerate the executed notebook, run `python analysis/make_notebook.py`. The LaTeX report was compiled with Tectonic 0.17.0; with Tectonic installed, run `tectonic -X compile GROUP_Medina_Castillo_W1_Report.tex` from `report/`. The report is a fixed snapshot: if analysis or data change, update its numbers and interpretation before compiling again.

## Source and file roles

Source: Daqing Chen (2015), *Online Retail*, UCI Machine Learning Repository, DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), [dataset page and dictionary](https://archive.ics.uci.edu/dataset/352/online+retail), CC BY 4.0. UCI offers `Online Retail.xlsx` as a 22.6 MB download. Our source workbook has 541,909 rows and eight columns. It matches the file downloaded directly from UCI byte for byte: SHA-256 `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`. The source and extract hashes are recorded in `data/source_manifest.json`.

The submitted input retains all original columns and every row with `2010-12-01 <= InvoiceDate < 2011-12-01`: 516,384 rows, with no cleaning or sampling. This includes all 12 complete calendar months in the source. December 2011 was excluded because the source ends on 9 December. The original workbook is omitted from the archive; the reduced CSV is included. To reconstruct it from a fresh package, download `Online Retail.xlsx` from the UCI page, place it at `data/Online Retail.xlsx`, remove the packaged reduced CSV, and run `python analysis/retail_analysis.py`. This regenerates the extract and manifest. The `extract_case(source_xlsx, output_csv, manifest_path)` function also accepts explicit paths.

The generated `data/case_checks.json`, `data/customer_concentration.csv`, `data/monthly_purchase_value.csv`, `data/monthly_cancellations.csv`, `data/top_products.csv` and `data/country_comparison.csv` are processed outputs. The PNG files in `analysis/figures/` are generated charts. We do not alter or deduplicate the packaged input. The report states the eligibility filters applied to each candidate measure.

## Completion before the course upload

- If the instructor later assigns a numeric group ID or specifies a required naming convention, update the submission filenames before upload.
- Add the instructor's response when received. The C1 preference remains provisional.

The executed notebook and PDF were checked against the included CSV. No unresolved execution error remains.
