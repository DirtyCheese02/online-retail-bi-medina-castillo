"""Create the English W2 notebook; execution is a separate explicit step."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# Workshop 2 — Customer concentration: from EDA to credible validation
**Business Intelligence · Moisés Medina and Ignacia Castillo · 20 October 2026**

This notebook is the primary W2 submission. Its question remains: **how much eligible recorded purchase value comes from the highest-value 10% of identifiable customers, and how much value is outside that ranking because an ID is missing?** Our proposed user is a commercial analyst reviewing a historical customer portfolio. The proposed action is to examine major accounts together with the ID-capture process. This is not a claim about the anonymous retailer's actual strategy.

The team reports **100/100 in C1**; no specific instructor correction text was supplied for W2. We therefore label the following new checks and clarifications as **self-audits or W2 extensions**, rather than inventing negative feedback. Preserved W1/C1 artifacts are under `assessments/`.

The specific W2 brief takes precedence over the old calendar: its deadline is **29 October 2026, 23:59, Chile**. The brief prints 22 October as its release date; we do not use that header to invent a work date. This notebook develops the existing descriptive project and fits no predictive model.

## 1. Reproducible setup and prespecified protocol
Run all cells in order. The seed and temporal boundaries are fixed before generating W2 tables. Input data and outputs are project-relative. The protocol records prior W1/C1 exposure to the complete period; freezing this procedure does not erase that exposure.''')
code('''from pathlib import Path
import sys, json, hashlib, platform
import pandas as pd
from IPython.display import display, Image, Markdown
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'src/w2_analysis.py').exists())
sys.path.insert(0, str(ROOT/'src'))
import w2_analysis as w2
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_colwidth', 105)
protocol = w2.freeze_protocol()
display(pd.DataFrame([{'seed':protocol['seed'], 'source_start':protocol['case_start'],
                      'source_end_exclusive':protocol['case_end_exclusive'],
                      'protocol_sha256':protocol['protocol_sha256']}]))
print('Python:', platform.python_version())
print(json.dumps(protocol['split_dates'], indent=2))''')
md('''## 2. Source, observation units and unchanged KPI
UCI Online Retail (Daqing Chen, 2015; DOI **10.24432/C5BW33**, CC BY 4.0) contains 541,909 invoice-line records from 1 December 2010 to 9 December 2011. Our preserved case extract includes **all 516,384 source lines from December 2010 through November 2011**. Only the final incomplete December 2011 was omitted in W1. December 2010 and November 2011 are complete calendar months within the source bounds. Their row counts need not be equal. Complete calendar coverage does not prove that the operational system captured every real transaction.

One source row is an **item entry on an invoice**. Several lines form one invoice; several invoices can be linked to one CustomerID. A C-prefixed invoice is a cancellation record under UCI's dictionary, without a verified link to an original purchase. `Country` is a country label recorded on the line, not a verified delivery destination.

The baseline purchase measure uses positive Quantity, positive UnitPrice, a non-C invoice and a provisional merchandise-code pattern of five digits with an optional final letter. Eligible line value is `Quantity × UnitPrice` in GBP. Original lines remain in the prepared dataset; rows outside these conditions are outside the measure, not silently deleted.

For known IDs, aggregate eligible purchase value over the stated window, rank descending and let **N** be the number of known IDs. **K10 = value of top ceil(0.10N) IDs / all known-ID value × 100.** The number is rounded upward to whole IDs; ties are ordered by ID for reproducibility. **ID coverage = known-ID eligible value / all eligible purchase value × 100.** It is value coverage, not the percentage of rows identified. Neither quantity is audited net revenue, profit, loyalty or lifetime value.

The uncleaned extract has a SHA-256 checked against the retained manifest before preparation. Unavailable line values are left undefined outside the positive-purchase scope; they are not recorded zeros.''')
code('''raw, data = w2.load_and_prepare()
display(pd.DataFrame({'field':raw.columns,'dtype':raw.dtypes.astype(str).to_numpy()}))
display(raw.head(3))
print('Source rows:',len(raw),'Prepared rows:',len(data))
dictionary = w2.dictionary()
display(dictionary)''')
md('''## 3. Executable quality checks, treatments and feedback-to-action
`PASS` means the checked violation was absent. `FLAG` identifies observed exceptions, not an automatic deletion or proof of invalid records. Structural violations stop execution; scoped exceptions remain visible with their treatment. Flags overlap and must not be subtracted as a row-flow diagram. The row groups are mutually exclusive.

Missing IDs are retained in total eligible value but omitted from customer ranking. Missing descriptions alone do not invalidate a priced purchase. We do not replace zero/negative prices with another month's price: doing so would invent a positive charge, and the reason for the recorded price is not available. Exact repeats remain in the baseline because no unique source-line ID proves them accidental. Product-code exceptions stay auditable and are examined through sensitivity.

The following exception tables inspect two additional assumptions: whether every invoice has one timestamp, and whether an ID has one stable country label. We use minimum/maximum invoice times to check boundaries without rewriting source timestamps. Country proportions use recorded line value rather than forcing a permanent country onto an ID.''')
code('''quality, quality_details = w2.validate(raw, data)
display(quality)
display(pd.read_csv(w2.OUT/'row_flow.csv'))
display(pd.DataFrame([quality_details]))
display(pd.read_csv(w2.OUT/'invoice_timestamp_exceptions.csv').head(12))
display(pd.read_csv(w2.OUT/'customer_country_exceptions.csv'))
feedback = w2.feedback_table(quality_details)
display(feedback)''')
md('''**Consequences for C1.** The timestamp and country findings qualify record interpretation; they do not by themselves refute customer concentration. We retain all source lines and avoid converting these exceptions into asserted causes. The new validation check prevents an invoice interval from crossing a partition unnoticed. The country exception means that country-based proportions cannot establish each ID's fixed residence. The next cell checks whether the original K10 and coverage actually reproduce.''')
md('''## 4. Revised EDA and sensitivity
This is retrospective descriptive evidence already partly examined in W1/C1. The W2 protocol and transformation have been specified independently of the later test statistics. We report population sizes and coverage whenever comparing periods; the monthly top decile is recalculated from each month's observed IDs.

The distribution identifies asymmetry and large accounts. The frequency–value figure explores a relevant relationship, but both are constructed from the same purchase history, so association is partly mechanical. The concentration curve directly answers the main question. The temporal figure shows K10, ID coverage and N together rather than treating a change in K10 as proof of diversification.''')
code('''stats, monthly, sensitivity = w2.analyze(data)
display(pd.DataFrame([stats['baseline']]))
display(pd.DataFrame([{k:v for k,v in stats.items() if not isinstance(v,dict)}]))
display(monthly[['month','known_customers','top_ids','K10_pct','ID_coverage_pct']])
figure_paths = w2.figures(data, monthly)
for path in figure_paths:
    display(Markdown('**'+path.stem.replace('_',' ').title()+'**'))
    display(Image(filename=str(path)))
display(sensitivity[['rule','known_customers','K10_pct','ID_coverage_pct']])''')
code('''b=stats['baseline']
display(Markdown(f"""**Interpretation.** The median known-ID value is £{stats['median_customer_value']:,.2f}, compared with a mean of £{stats['mean_customer_value']:,.2f}; large accounts influence the mean. K10 reproduces C1 at {b['K10_pct']:.4f}% and coverage at {b['ID_coverage_pct']:.4f}%. Therefore, the numerical C1 conclusion is retained, conditional on known IDs and the same eligibility rules.

The frequency–value Spearman association is {stats['spearman_frequency_value']:.3f} (Pearson {stats['pearson_frequency_value']:.3f}). More recorded invoices give more opportunities to accumulate value; this does not show that inducing purchases would cause retention or profit. Outliers are not removed just because the distribution is skewed. Sensitivities place K10 between {stats['sensitivity_min_K10']:.2f}% and {stats['sensitivity_max_K10']:.2f}%.

From October to November, K10 changes from {monthly.iloc[-2].K10_pct:.1f}% to {monthly.iloc[-1].K10_pct:.1f}% while coverage changes from {monthly.iloc[-2].ID_coverage_pct:.1f}% to {monthly.iloc[-1].ID_coverage_pct:.1f}%. Changing coverage, customer mix and ranking populations are plausible explanations; we cannot establish that missing IDs caused the K10 change. A single annual cycle cannot establish Christmas seasonality."""))''')
md('''## 5. Sampling and representativeness
**Target population:** for the historical question, all relevant purchase activity of the source retailer during the selected year. For any future operational decision, the target would instead be that retailer's recent accounts and processes, which this file cannot represent by assumption.

**Observed population:** the invoice-line records present in the public file within the complete-month extract. These are available administrative records, not a probability sample of UK retailers or all actual purchases. **Final analytical populations:** eligible purchase lines for value/coverage, and identified customer aggregates for K10.

Plausible biases include unrecorded activity in the source system, missing customer identification, an anonymous historical gift retailer with wholesale customers, and provisional product-code exclusions. A precise train/test split does not correct any of these coverage mechanisms.

We sample **25% of distinct invoices within each earliest-invoice-month**, rounding the count to a whole invoice with the fixed seed. We retain all lines of selected invoices. Each invoice within a month has the same inclusion probability; slight rounding and invoice-size variation mean the realized row fraction is not exactly 25%. We do not search for a seed that resembles the full dataset. This samples invoices, not customers: some IDs lose much of their observed history or disappear, changing N and the top decile. The UK comparison uses value by recorded country on each eligible line, including unidentified purchases.''')
code('''sample, strata, comparison = w2.sample_invoices(data)
display(strata)
display(comparison[['dataset','source_lines','known_customers','top_ids','fraction_source_rows_pct',
                    'K10_pct','K10_pct_difference_pp','ID_coverage_pct','ID_coverage_pct_difference_pp',
                    'UK_value_share_pct','UK_value_share_pct_difference_pp']])
s=comparison.iloc[1]
display(Markdown(f"""**Interpretation.** The sample contains {len(sample):,} rows ({s.fraction_source_rows_pct:.2f}% of the available case) and {s.known_customers:,.0f} known IDs. Sample K10 is {s.K10_pct:.2f}%, a difference of {s.K10_pct_difference_pp:.2f} percentage points. Coverage differs by {s.ID_coverage_pct_difference_pp:.2f} points and UK value share by {s.UK_value_share_pct_difference_pp:.2f} points. These differences describe this one fixed sample; they are not confidence limits or evidence of systematic bias. The smaller customer history changes the estimand's observed population. We therefore retain the complete case for the main descriptive result and use the subsample only to demonstrate sampling effects. Sampling representativeness and train/test information boundaries answer different questions."""))''')
md('''## 6. Chronological holdout and train-only preprocessing
The decision moment is a review **after month-end**, when recorded invoices up to the cut-off are available. We preserve the direction past → later. Training uses December–July, validation August–September and test October–November. Eight calendar months do not imply 80% of rows; year-end activity is larger. These dates were chosen before W2 result inspection and are not optimized from the test.

This is a descriptive robustness design, not a predictive accuracy experiment. W1/C1 already examined the test months. The held partitions are separate by source row and invoice; they are not statistically independent customer populations. Customer recurrence is intentional for reviewing existing accounts over time. Generalization to entirely new customers would require grouped validation instead. We report customer overlap so it cannot be mistaken for independence.

The partitions are constructed from the **complete case, not the sampling demonstration**. All groups, including unidentified purchases and records outside the value measure, are saved. Comparison of the main KPI remains monthly; we do not interpret totals over an eight-month period and two-month periods as directly comparable.

For the preprocessing demonstration, an eligible invoice's completed purchase value is available at a later month-end review. We apply log1p and fit StandardScaler on training invoices only; validation and test receive the unchanged rule. This could support a future order-size descriptor. It would leak information if used to predict that same invoice's value before it occurred. Standardization is not needed to compute K10 and does not replace GBP in the KPI.''')
code('''splits, split_summary, overlap = w2.make_splits(data)
display(split_summary)
display(overlap)
preprocessing_table, preprocessing_parameters = w2.preprocess(splits)
display(pd.DataFrame([preprocessing_parameters]))
display(preprocessing_table)
print('Validation inspected after the train-only fit; test transformed afterward without refitting.')
print('No model, target, model selection or predictive performance score is computed.')''')
md('''**Validation decision.** We inspect whether validation can be transformed under the fixed rule and whether the train-fitted parameters remain unchanged. We keep the prespecified transformation: there is no predictive objective or tuning criterion in W2. The same rule is then applied to test without refit. Nonzero validation/test means are expected under changed invoice distributions; they do not justify refitting on the test. A genuinely later dataset, not previously explored, is still needed before claiming prospective validity.''')
md('''## 7. Contextual leakage audit
The table distinguishes an observed overlap, an actual information violation and a hypothetical future misuse. A shared CustomerID is not automatically inappropriate for the stated same-account time scenario, but it precludes a claim of independent new-customer evaluation. Target-derived leakage is assessed conditionally because the present project has no predictive target.''')
code('''leakage = w2.leakage_audit(data, overlap, preprocessing_parameters)
display(leakage)''')
md('''## 8. Management interpretation and next step
The summary below is generated from verified outputs and has 120–180 words. Observed facts, scope assumptions and proposed managerial actions remain distinct.''')
code('''results = w2.finalize(stats, quality_details, comparison, preprocessing_parameters, quality, split_summary)
summary = w2.management_summary(stats, comparison, quality_details)
print('Management summary word count:',len(summary.split()))
display(Markdown(summary))
print('Verified outputs:', len(json.loads((ROOT/'evidence/artifact_manifest.json').read_text())))''')
md('''## 9. References, AI use and traceability
- Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5BW33. Dataset and dictionary: https://archive.ics.uci.edu/dataset/352/online-retail. Source licence: CC BY 4.0. The original retrieval/check is recorded in the preserved manifest; no new download is claimed.
- Fontecilla, T. (2026). *Workshop 2: From Exploratory Analysis to Credible Validation*, student brief and rubric supplied in the course workspace.
- Course notebooks: *Validation, Leakage and Reproducible Pipelines*; *Guided Validation Case*; *Sampling, Regression and Classification*. Consulted locally for sampling/split distinctions and train-only transformations. Teacher materials are not redistributed in this repository.
- W1/C1 self-contained reports and executed notebooks: `assessments/W1/` and `assessments/C1/`. Their original text is preserved as historical submission evidence, including its stated uncertainties.

**AI assistance and verification.** OpenAI Codex assisted with code, report/notebook drafts and layout. The team's implementation request fixed the same KPI, seed, invoice sampling and chronological periods. Accepted suggestions include explicit flags, period-specific aggregates and an exported check table. Unsupported claims about price-zero reasons, customer loyalty, net revenue or a pristine holdout are excluded. Executable assertions and automated reruns check consequential suggestions against the source; those are automated checks, not claims that a student personally performed each verification. The team remains responsible for reviewing, understanding and defending the submitted work. No individual contribution or instructor comment has been invented.

The source extract is unchanged. `evidence/protocol.json` records analytical assumptions; `data/processed/` contains checkable tables, actual samples and prepared lines; `data/splits/` contains actual partition files. The README provides reproduction instructions and the final submission identifies the Git commit and tag. The supplemental LaTeX report uses these same generated outputs.''')

nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                                         'language_info':{'name':'python','version':'3.12'}})
path=ROOT/'notebooks/W2_project.ipynb'
nbf.write(nb,path)
print(path)
