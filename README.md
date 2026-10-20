# Online Retail BI — Medina and Castillo

**Business Intelligence IIB423T-1 · Workshop 2 · 20 October 2026**  
**Authors:** Moisés Medina and Ignacia Castillo  
**Specific W2 deadline:** 29 October 2026, 23:59, Chile  
**Repository:** https://github.com/DirtyCheese02/online-retail-bi-medina-castillo

We continue the W1/C1 descriptive question: how concentrated is eligible recorded purchase value among identifiable customers, and how much value cannot enter that ranking? The proposed user is a commercial analyst reviewing historical accounts and ID capture. We retain K10 and ID-value coverage; no model or predictive accuracy is claimed. The team reports 100/100 in C1. New concerns are labelled self-audits or W2 extensions, not invented instructor feedback.

## Open the submission

1. **[notebooks/W2_project.ipynb](notebooks/W2_project.ipynb)** — primary English-language W2 submission, executed from a fresh kernel with saved tables and four figures. It contains the 120–180 word management summary, interpretation, leakage audit and AI disclosure.
2. **[report/GROUP_Medina_Castillo_W2_Report.pdf](report/GROUP_Medina_Castillo_W2_Report.pdf)** — supplemental self-contained report; LaTeX source and `main.tex` wrapper are alongside it. The PDF is additional evidence, not a replacement for the notebook.
3. **[evidence/rubric_matrix.csv](evidence/rubric_matrix.csv)** — subcriterion-to-evidence map; **[evidence/verification.json](evidence/verification.json)** records executable acceptance checks. This mapping does not guarantee an instructor score.
4. **[assessments/](assessments/)** — preserved W1/C1 snapshots, including the final 15-slide C1 presentation. Snapshot PDFs/notebooks remain historical records; new W2 interpretations are in the primary notebook.

## Reproduce from a clean clone

Tested with **Python 3.12.5**; exact directly used package versions are in `requirements.txt` and `evidence/environment.json`.

```sh
git clone https://github.com/DirtyCheese02/online-retail-bi-medina-castillo.git
cd online-retail-bi-medina-castillo
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on macOS/Linux, then:

```sh
python -m pip install -r requirements.txt
python src/execute_notebook.py
python src/build_report.py
python src/verify_submission.py
```

The notebook runner selects the current Python interpreter for its fresh kernel; it does not silently rely on another registered environment. The supplied PDF allows verification without TeX. If rebuilding it after a report-source change, compile `report/main.tex` with the built-in Codex LaTeX editor and export the PDF, or run `tectonic GROUP_Medina_Castillo_W2_Report.tex` from `report/` using a compatible Tectonic installation. Re-run the verifier after rebuilding. The submitted PDF was checked with the integrated editor and exported with bundled Tectonic 0.17.0.

`src/w2_analysis.py` contains the maintained analysis functions. `src/build_notebook.py` rebuilds the notebook template only when intentional edits are made; run `src/execute_notebook.py` afterward to restore all outputs. Do not clear the submitted notebook. No network download is needed to execute the included case after installing dependencies.

## Files and data flow

| Location | Role |
|---|---|
| `data/raw/` | Unchanged, uncleaned 12-month input and original source manifest |
| `src/w2_analysis.py` | Preparation, checks, EDA, sampling, split and train-only transformation |
| `data/processed/validated_lines.csv.gz` | All 516,384 lines, original fields, `source_row` and derived flags; not deduplicated |
| `data/processed/invoice_sample_25pct.csv.gz` | Actual whole-invoice sample, separate from holdout |
| `data/processed/sample_*.csv` | Selected invoice IDs, monthly strata and KPI/segment comparison |
| `data/splits/{train,validation,test}.csv.gz` | Actual chronological subsets, including records outside the purchase measure |
| `data/processed/quality_checks.csv` | Seventeen checks, outcomes, treatments and reasons |
| `data/processed/*exceptions.csv` | Invoice-time and customer-country exceptions retained for audit |
| `data/processed/invoice_preprocessing.csv` | Eligible invoice values and the unchanged train-fitted transformation |
| `data/processed/w2_metrics.json` | Shared numerical source for the notebook and report |
| `analysis/figures/` | Four regenerated analytical figures |
| `evidence/protocol.json` | Fixed seed/rules/boundaries, intended use and prior-exposure disclosure |
| `evidence/preprocessing_parameters.json` | Training-only fitted mean, scale, fit count and parameter invariance |
| `evidence/artifact_manifest.json` | SHA-256 for source, generated tables, subsets and figures |

Gzip files contain ordinary CSV; use `pd.read_csv(path)` or any gzip-capable decompressor. Monetary values are GBP. `source_row` is the one-based position in the unchanged input; it is not a real-world transaction identifier. Original fields appear in prepared/subset files so their construction can be inspected.

## Source, licence and scope

Daqing Chen (2015), **Online Retail**, UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5BW33. Source/dictionary: https://archive.ics.uci.edu/dataset/352/online-retail. **CC BY 4.0 applies to the source dataset.** See `DATA_ATTRIBUTION.md` for attribution and modifications; no licence is invented for course materials or the entire repository.

The original XLSX has 541,909 invoice-line records from 1 December 2010 through 9 December 2011. The supplied uncleaned extract preserves all eight original columns and all 516,384 rows satisfying `2010-12-01 <= InvoiceDate < 2011-12-01`, in source order. It excludes only the source's partial final December. The source and extract SHA-256 values, original URL and extraction rule are in `data/raw/source_manifest.json`. Download the original XLSX from UCI and apply that filter to reconstruct it; the unchanged extract is already included. No new retrieval date is claimed for W2.

Eligible purchases have positive quantity/price, a non-C invoice and a provisional code pattern of five digits with an optional final letter. Customer ranking additionally requires CustomerID. Missing IDs remain in coverage's denominator. Zero prices are not imputed; repeated rows remain in the baseline. Item-code exceptions and C records are not silently discarded from the source. K10 is a share of known-ID positive purchase value, not audited net revenue or profit.

## Sampling, holdout and exposure limits

Seed **4232026** selects 25% of invoices within month, keeping all their lines. It yields 130,912 rows, 25.35% of the complete case, and K10 54.01% versus full-case 60.50%. This does not make the sample representative of all customers or the retail market: fewer observed invoices change customer coverage and ranking. The UK segment comparison is based on recorded eligible line value.

Chronological boundaries are fixed: training December 2010–July 2011; validation August–September; test October–November. Source-row counts are 285,421 / 85,510 / 145,453. No row, invoice or exact source-record hash crosses partitions. Customer recurrence is reported and allowed for the same-account time scenario; this does not evaluate new-customer generalization. Period-specific aggregates prevent future full-case profiles from entering earlier decisions.

The entire period was explored in W1/C1. The held periods are descriptive robustness checks with prior exposure, not pristine or prospective test data. No model is trained or tuned. A StandardScaler on log1p eligible invoice value is fit only on training invoices and applied unchanged to validation/test. K10 uses original GBP throughout. No test data select a transformation, threshold or feature.

## Submission traceability

W1/C1 snapshots were committed before W2 development. The final submission is tagged **`w2-submission`**. Retrieve its immutable commit with `git rev-parse w2-submission^{commit}` and submit that full SHA with the repository link; the final handoff message supplies the direct tree URL. A commit's own hash is not embedded inside itself.

The original rubric/course notebooks are referenced in the submission but are not republished. Earlier teacher-related statements inside assessment snapshots are historical records. The W2 feedback table identifies self-audits explicitly. The team remains responsible for reviewing and defending the work; automated checks are not represented as personal student verification.
