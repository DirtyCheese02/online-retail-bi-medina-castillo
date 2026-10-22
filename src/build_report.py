"""Generate the supplemental LaTeX report from verified W2 CSV/JSON outputs."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/processed'
M=json.loads((P/'w2_metrics.json').read_text())
B=M['baseline']; S=M['sampling'][1]; D=M['quality_details']; T=M['preprocessing']

def esc(s):
    s=str(s)
    for old,new in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#'),('$',r'\$')]: s=s.replace(old,new)
    return s.replace('£',r'\pounds{}').replace('–','--').replace('—','---').replace('’',"'")

def table(headers,rows,spec=None):
    if spec is None: spec='@{}'+'Y'*len(headers)+'@{}'
    body='\n'.join(' & '.join(esc(x) for x in row)+r' \\' for row in rows)
    return r'\begin{tabularx}{\linewidth}{'+spec+'}\n'+r'\toprule'+ '\n'+' & '.join(r'\textbf{'+esc(x)+'}' for x in headers)+r' \\ \midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabularx}'+'\n'

def figure(name,caption,width='.95'):
    return r'\begin{figure}[H]\centering\includegraphics[width='+width+r'\linewidth]{'+name+r'}\caption{'+caption+r'}\end{figure}'+'\n'

chunks=[r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=1.95cm,top=2.2cm,bottom=2.05cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,booktabs,tabularx,array,graphicx,xcolor}
\usepackage{enumitem,caption,fancyhdr,xurl,float,amsmath,needspace}
\usepackage[unicode,colorlinks=true,urlcolor=blue!65!black,linkcolor=black]{hyperref}
\graphicspath{{../analysis/figures/}}
\definecolor{ink}{HTML}{202A32}\definecolor{navy}{HTML}{173E56}
\definecolor{muted}{HTML}{586974}\definecolor{rule}{HTML}{CED8DD}
\color{ink}\setlength{\parindent}{0pt}\setlength{\parskip}{0.30em}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\emergencystretch}{2em}\renewcommand{\arraystretch}{1.18}
\captionsetup{font=small,labelfont=bf}\setlist[itemize]{leftmargin=1.25em,itemsep=.1em,topsep=.15em}
\pagestyle{fancy}\setlength{\headheight}{22pt}\fancyhf{}
\fancyhead[L]{\footnotesize\color{muted} IIB423T-1 / Workshop 2}
\fancyhead[R]{\footnotesize\color{muted} Medina \& Castillo}
\fancyfoot[R]{\footnotesize\color{muted}\thepage}\renewcommand{\headrulewidth}{.35pt}
\newcommand{\sectionhead}[1]{\Needspace{8\baselineskip}\vspace{.4em}{\large\bfseries\color{navy}#1}\par\vspace{.1em}}
\newcommand{\subhead}[1]{\vspace{.2em}{\bfseries #1}\par}
\begin{document}\thispagestyle{empty}
{\small\bfseries\color{navy} BUSINESS INTELLIGENCE / WORKSHOP 2}\par\vspace{.6em}
{\LARGE\bfseries Customer concentration: from EDA to credible validation}\par\vspace{.35em}
{\large A descriptive validation and sampling study of UCI Online Retail}\par\vspace{.5em}
{\color{muted}Mois\'es Medina and Ignacia Castillo\hfill 20 October 2026}\par
\vspace{.6em}{\color{rule}\hrule height .65pt}\vspace{.6em}
\textbf{Submission role.} This is a supplemental report. The primary W2 evidence is the executable English notebook \path{notebooks/W2_project.ipynb}, with saved outputs, data and execution instructions in the GitHub repository. The specific W2 brief sets the deadline at 29 October 2026, 23:59, Chile. Its printed release date is 22 October; that header is not a claim about when this work was performed.

\sectionhead{1\quad Continuity, decision and measurement}
We retain the W1/C1 question: how much eligible recorded purchase value is attributable to the highest-value 10\% of identifiable customers, and how much value cannot enter that ranking because an ID is missing? A proposed commercial analyst could use the evidence for a retrospective account review and a review of ID capture. This is a proposed use, not the anonymous retailer's documented strategy.

The team reports 100/100 in C1. No specific instructor correction text was supplied for this stage. We therefore identify self-audits and new W2 extensions explicitly; a new validation requirement is not presented as proof that C1 was incorrect. The original W1/C1 submissions are preserved under \path{assessments/}.

Let $v_i$ denote eligible recorded value for known customer $i$, $N$ the known-ID population and $k=\lceil0.10N\rceil$. Sorting $v_i$ from highest to lowest,
\[
K_{10}=100\frac{\sum_{i=1}^{k}v_i}{\sum_{i=1}^{N}v_i},\qquad
C_{ID}=100\frac{\text{known-ID eligible value}}{\text{all eligible purchase value}}.
\]
Values use pounds sterling; both measures are percentages. Cutoffs round upward to whole IDs. ID coverage is value-weighted, not a fraction of rows. Neither measure is net revenue, margin, loyalty, lifetime value or an established risk tolerance.
''']
chunks.append(table(['Reproduced C1 baseline','W2 result'],[
    ('Source invoice lines',f'{M["source_rows_before"]:,}'),('Eligible positive purchase lines',f'{B["purchase_lines"]:,}'),
    ('Identifiable customers / top-decile IDs',f'{B["known_customers"]:,} / {B["top_ids"]:,}'),
    ('K10 / ID-value coverage',f'{B["K10_pct"]:.4f}% / {B["ID_coverage_pct"]:.4f}%'),
    ('Eligible value / known-ID value',f'£{B["eligible_value_gbp"]:,.2f} / £{B["known_value_gbp"]:,.2f}')]))
chunks.append(r'''The baseline matches C1 numerically within the executable floating-point tolerance. We retain its bounded concentration conclusion. W2 strengthens the checkable evidence and the interpretation of coverage and validation; it does not establish a current operational effect.
\clearpage
\sectionhead{2\quad Source, dictionary and analytical scope}
UCI Online Retail (Chen, 2015; DOI 10.24432/C5BW33; CC BY 4.0) describes an online gift retailer based in the UK with many wholesale customers. Its original file has 541,909 records from 1 December 2010 to 9 December 2011. The unchanged case input keeps all 516,384 rows through 30 November 2011, excluding only the final nine-day December fragment. Complete months have unequal lengths and activity; complete date coverage does not prove complete capture of real transactions.

One row is one recorded invoice line. An invoice contains multiple lines and a CustomerID can link multiple invoices. InvoiceNo is therefore not a unique row key. A C prefix identifies a cancellation record; there is no verified original-purchase link. Country is a label on the record, not a verified delivery destination or a necessarily stable attribute of an ID.
''')
dic=pd.read_csv(P/'data_dictionary.csv')
chunks.append(r'{\small'+'\n'+table(['Original field','Meaning / unit','Type and missingness'],[
    (r.variable,r.meaning_and_unit,r.expected_type+'; '+r.missing_meaning) for r in dic.head(8).itertuples()])+ '}\n')
chunks.append(r'''The full machine-readable dictionary also covers derived flags, source row, row groups, split membership, value and KPI formulas.\par
\textbf{Eligibility.} A purchase must have positive Quantity and UnitPrice, no C prefix and a StockCode matching five digits with an optional final letter. The pattern is a provisional scope rule, not a verified commercial classification. Eligible line value is Quantity times UnitPrice. Eligible cancellation records instead require a C prefix, negative quantity, positive price and the same code rule. All remaining rows stay in the prepared file outside both measures.

\textbf{Retention rationale.} A missing ID prevents ranking but does not erase recorded value. A missing description alone does not affect the calculation. A zero or negative price is outside the positive-value measure; substituting another price would invent a charge without knowing the reason. Exact repeats remain in the baseline because no source-line identifier establishes which are erroneous. We test alternatives instead of silently deleting records. An undefined derived value outside the purchase scope is not an observed zero.
''')
flow=pd.read_csv(P/'row_flow.csv')
chunks.append(table(['Mutually exclusive group','Rows'],[(r.row_group,f'{r.rows:,}') for r in flow.itertuples()]))
chunks.append(r'''The input SHA-256 is checked before analysis. Original fields and the one-to-one source-row identifier are preserved in the prepared table. No source lines are lost; flags may overlap, whereas the three row groups do not.
\clearpage
\sectionhead{3\quad Quality validation and consequential checks}
The notebook implements seventeen checks. Structural violations stop execution; scoped exceptions are flagged with a documented treatment. ``Flag'' does not mean the record has been proved wrong. The source and prepared counts both remain 516,384.
''')
quality=pd.read_csv(P/'quality_checks.csv')
chunks.append(r'{\small'+'\n'+table(['Check','Count / status','Treatment'],[
    (r.check_id+' '+r.check,f'{r.affected_count:,} / {r.status}',r.treatment) for r in quality.itertuples()],
    r'@{}P{.43\linewidth}P{.15\linewidth}Y@{}')+'}\n')
chunks.append(f'Invoice timestamps vary within {D["invoice_multiple_timestamps"]} InvoiceNo values; the maximum observed span, in minutes, is {D["invoice_timestamp_span_max_minutes"]:.0f}, and {D["invoice_timestamp_exceptions_cross_day"]} of these intervals cross a calendar day. We preserve original timestamps and use first/last times to verify boundaries. None crosses the specified train/validation/test boundaries. Eight IDs have multiple country labels. We retain country at line level rather than asserting fixed residence or overwriting an ID\'s history. Exception tables list the affected identifiers and evidence.\n')
chunks.append(r'''\clearpage
\sectionhead{4\quad Feedback-to-action and changes to conclusions}
The entries below are self-audits or W2 extensions. They are not attributed to the instructor. The full table includes notebook sections, generated evidence paths and the reason for each action.
''')
feedback=pd.read_csv(P/'feedback_to_action.csv')
chunks.append(r'{\small'+'\n'+table(['Issue','Action','Consequence'],[(r.issue,r.action_and_reason,r.effect_on_conclusion) for r in feedback.itertuples()])+ '}\n')
chunks.append(r'''\subhead{What changed and what did not}
The numerical full-case K10 and coverage remain unchanged. The product-code interpretation is made explicitly provisional. Invoice time and country consistency receive new executable checks. The monthly narrative states that population mix and missingness are possible explanations, rather than claiming a causal mechanism. The temporal holdout is documented as reused historical evidence because W1/C1 already inspected all periods. No claim of predictive performance is added.

\subhead{Five Cs carried forward}
Clean: observable checks and justified retention are exported. Consistent: unchanged purchase and KPI rules apply across the twelve months. Conformed: no external join is forced; cross-source agreement is not applicable. Current: 2010--2011 records support historical analysis; recent data are needed for operational use. Comprehensive: unidentified value, provisional product scope, missing financial costs/payments and absent purchase--cancellation links remain limitations.
\clearpage
\sectionhead{5\quad Revised exploratory evidence}
''')
chunks.append(figure('customer_value_distribution.png','Known-ID eligible purchase value over the full twelve-month case. The logarithmic x-axis makes the long upper range visible; it does not remove large accounts.'))
chunks.append(f'The median is \\pounds{{}}{M["median_customer_value"]:,.2f}, the mean \\pounds{{}}{M["mean_customer_value"]:,.2f}, and the maximum \\pounds{{}}{M["max_customer_value"]:,.2f}. The mean is not representative of every customer. A large recorded account is not, by itself, proof of an error or of loyalty.\n')
chunks.append(figure('frequency_value_relationship.png','Eligible invoice frequency and recorded value per known ID. Both axes use logarithms; each point is a known customer in this window.'))
chunks.append(f'Spearman correlation is {M["spearman_frequency_value"]:.3f}; Pearson correlation is {M["pearson_frequency_value"]:.3f}. More observed invoices give more opportunities to accumulate value, so the relationship is partly arithmetic. It does not establish that an intervention would cause higher loyalty, revenue or profit.\n')
chunks.append(r'\clearpage'+'\n')
chunks.append(figure('concentration_curve.png','Cumulative known-ID value ranked from highest to lowest; the diagonal is an equal-value reference. The top group is rounded to 430 IDs.'))
chunks.append(f'The top {B["top_ids"]:,} of {B["known_customers"]:,} identified customers account for {B["K10_pct"]:.1f}\\% of known purchase value. This concentration is conditional on IDs covering {B["ID_coverage_pct"]:.1f}\\% of all eligible value. Sensitivity checks give K10 between {M["sensitivity_min_K10"]:.2f}\\% and {M["sensitivity_max_K10"]:.2f}\\%; they do not recover unidentified purchases.\n')
chunks.append(figure('monthly_kpi_coverage_population.png','Monthly K10 and ID-value coverage share a 0--100 percent scale; the lower panel reports known-ID population N. IDs are re-ranked within each month.'))
chunks.append(r'''October K10 is 50.8\% and November K10 47.8\%, while ID coverage falls from 91.1\% to 78.6\%. This does not establish diversification or prove that missing IDs caused the change. Different account mixes, identification processes and activity could affect the observed ranking. One annual cycle cannot establish a recurring Christmas effect.
\clearpage
\sectionhead{6\quad Sampling and representativeness}
The historical target is relevant purchase activity for the retailer during the selected year. The observed population consists of the available source records within our complete-month extract. The value dataset includes eligible purchase lines; K10 additionally requires identifiable customer aggregates. None is a probability sample of UK retailers. A future operational target would require recent accounts and processes.

Plausible coverage biases include unidentified purchases, unrecorded activity in the operational source, the single historical gift retailer and provisional item-code exclusions. Splitting records cannot repair these source-coverage mechanisms.

We select approximately 25\% of distinct invoices within each earliest-invoice-month, using seed 4232026 and whole-invoice rounding. All lines of selected invoices remain together. The size is an instructional subsampling exercise, not a claim of population power or precision. Varying invoice sizes and rounding make the realized row percentage slightly different. The seed is fixed; it is not selected to make the sample look representative.
''')
comparison=pd.read_csv(P/'sample_comparison.csv')
chunks.append(table(['Measure','Complete case','Invoice sample','Difference'],[
    ('Source rows',f'{B["source_lines"]:,}',f'{int(S["source_lines"]):,}',f'{S["fraction_source_rows_pct"]:.2f}% of source rows'),
    ('Known customers',f'{B["known_customers"]:,}',f'{int(S["known_customers"]):,}','Ranking population changes'),
    ('K10',f'{B["K10_pct"]:.2f}%',f'{S["K10_pct"]:.2f}%',f'{S["K10_pct_difference_pp"]:+.2f} pp'),
    ('ID-value coverage',f'{B["ID_coverage_pct"]:.2f}%',f'{S["ID_coverage_pct"]:.2f}%',f'{S["ID_coverage_pct_difference_pp"]:+.2f} pp'),
    ('UK share of eligible value',f'{B["UK_value_share_pct"]:.2f}%',f'{S["UK_value_share_pct"]:.2f}%',f'{S["UK_value_share_pct_difference_pp"]:+.2f} pp')]))
chunks.append(r'''UK share uses the recorded country of each eligible purchase line and includes unidentified value. It does not force a permanent country onto a customer. Invoice sampling reduces observed history per ID and removes some IDs entirely; the observed top decile therefore changes. Sample K10 is not an unbiased reconstruction guarantee for the full customer's annual portfolio. These differences describe one fixed sample, not confidence intervals or proof of sampling bias. The complete case remains our main descriptive population. Sampling is separate from the chronological split and is not used to decide which rows fit preprocessing.
''')
strata=pd.read_csv(P/'sample_strata.csv')
chunks.append(r'{\small'+'\n'+table(['Month','Invoices: available / sampled','Rows: available / sampled'],[(r.month,f'{r.available_invoices:,} / {r.sampled_invoices:,}',f'{r.available_rows:,} / {r.sample_rows:,}') for r in strata.itertuples()])+ '}\n')
chunks.append(r'''\clearpage
\sectionhead{7\quad Temporal holdout and validation procedure}
The proposed decision time is after month-end. Completed invoices up to the cut-off are available for account review. Full-year future totals and ranks would not be legitimate earlier-period features. We partition the complete source case, not its 25\% invoice sample. All row groups, including missing-ID and non-measure records, are saved in the actual split files.

First, October--November is reserved as test. The earlier December--September development pool is the initial training pool before validation is removed. Second, August--September is carved out of that pool as validation, leaving December--July for fitting. Validation contains no test rows. This hierarchy and its parent-relative proportions are exported in \path{data/processed/split_hierarchy.csv}.
''')
splits=pd.read_csv(P/'split_summary.csv')
chunks.append(table(['Partition / inclusive months','Source rows','Row share','Invoices','Eligible known IDs'],[
    (r.split+': '+{'train':'Dec 2010--Jul 2011','validation':'Aug--Sep 2011','test':'Oct--Nov 2011'}[r.split],f'{r.rows:,}',f'{r.row_fraction_pct:.2f}%',f'{r.invoices:,}',f'{r.eligible_known_ids:,}') for r in splits.itertuples()],
    r'@{}P{.34\linewidth}rrrr@{}'))
chunks.append(r'''The boundaries are 1 August, 1 October and 1 December 2011, with half-open intervals. Calendar duration is not an imposed 80/20 row ratio; activity differs across months. Structural checks confirm every source row belongs to one partition, no invoice crosses a boundary and no exact source-record hash appears in two partitions.
''')
ov=pd.read_csv(P/'split_overlap.csv');customers=ov[ov.unit.eq('known_customer_ids')]
chunks.append(table(['Comparison','Source-row overlap','Invoice overlap','Known-ID overlap'],[(r.left+' / '+r.right,'0','0',str(r.overlap_count)) for r in customers.itertuples()]))
chunks.append(r'''Repeated customers are intentional for reviewing the same account population in later periods. The held periods are separate observations, but not independent new-customer samples. A new-customer generalization claim would require grouped validation. We use period-specific aggregates and explicitly report overlap instead of asserting customer independence.

\subhead{Training-only fitted operation}
For each eligible invoice we sum its positive purchase value, apply log1p and fit StandardScaler on training invoices only. Invoice value is available after completion for the stated review; it would not be a valid predictor of itself before purchase. No CustomerID or price is imputed. K10 continues to use original pounds, not scaled values.
''')
pre=pd.read_csv(P/'preprocessing_by_split.csv')
chunks.append(table(['Partition','Eligible invoices','Mean scaled log value','SD scaled log value'],[(r.split,f'{r.invoices:,}',f'{r.mean_scaled_value:.4f}',f'{r.sd_scaled_value_ddof0:.4f}') for r in pre.itertuples()]))
chunks.append(f'The fitted mean is {T["mean"]:.6f} and scale {T["scale"]:.6f}, estimated from {T["fitted_invoice_count"]:,} training invoices. The validation gate requires finite transformed values, positive eligible invoice totals, unique invoice keys and unchanged training parameters. Failure stops execution before test transformation. The ordered fit, validation gate and test transformation are exported in \\path{{data/processed/validation_execution.csv}}. These are applicability checks; no predictive-performance target or test-driven tuning is introduced. Nonzero held-period means do not justify refitting on them.\n')
chunks.append(r'''\textbf{Exposure limit.} W1/C1 already inspected all twelve months. The protocol was fixed before W2 result tables, but the current holdout cannot become an untouched prospective test by relabeling it. It is a descriptive robustness comparison. We report monthly KPIs rather than interpreting unequal-duration partition totals as comparable. No predictive model, outcome label or accuracy metric is produced.
\clearpage
\sectionhead{7\quad Temporal holdout: descriptive findings}
After validation, we recalculate K10 and coverage separately within each month using only that month's purchases and known IDs. Each month receives equal weight in the summary below. These are means of monthly shares, not a pooled-period K10 or a comparison of raw totals from unequal windows.
''')
held=pd.read_csv(P/'holdout_robustness.csv')
chunks.append(table(['Partition / months','Mean monthly K10','Monthly K10 range','Mean monthly ID coverage'],[
    (r.split+f' / {r.months}',f'{r.mean_monthly_K10_pct:.2f}%',f'{r.min_monthly_K10_pct:.2f}% -- {r.max_monthly_K10_pct:.2f}%',f'{r.mean_monthly_ID_coverage_pct:.2f}%') for r in held.itertuples()]))
h=held.loc[held.split.eq('test')].iloc[0]
chunks.append(f'Test mean monthly K10 differs from training by {h.mean_K10_difference_from_train_pp:+.2f} percentage points. Concentration remains substantial in the held months, while its level varies. The annual K10 of {B["K10_pct"]:.2f}\\% pools longer customer histories; it is not a target expected in every month.\n')
chunks.append(r'''\textbf{Interpretation.} Observed customer mix, invoice histories and ID coverage differ between months. These descriptive differences do not identify a cause, establish a seasonal effect or measure predictive accuracy. The detailed monthly table includes each denominator and is saved as \path{data/processed/holdout_monthly_kpi.csv}.

\textbf{Audit amendment, 21 October 2026.} The explicit development hierarchy, ordered validation gate and this holdout table strengthen the evidence for criterion F. They preserve the previously fixed dates, eligibility and scaler. They were added after prior full-case exposure; no claim of newly unseen test data is made, and no observed difference selects a transformation or rule. A genuinely later period remains necessary for prospective evaluation.

\clearpage
\sectionhead{8\quad Context-specific leakage audit}
The audit reports observed risks, conditional future risks and implemented safeguards. Status is contextual: shared customer IDs do not alone imply inappropriate leakage for the same-account scenario, but invalidate an independent new-customer claim.
''')
audit=pd.read_csv(P/'leakage_audit.csv')
chunks.append(r'{\small'+'\n'+table(['Risk / status','Evidence','Consequence and mitigation'],[(r.risk+' / '+r.status,r.dataset_evidence,r.potential_consequence+'. '+r.mitigation) for r in audit.itertuples()],
    r'@{}P{.23\linewidth}P{.27\linewidth}Y@{}')+'}\n')
chunks.append(r'''A future predictive task must specify an outcome and horizon, and restrict inputs to what exists at the decision cut-off. Customer-profile clustering remains a possible later descriptive extension with no invented target labels. W2 establishes boundaries and a fitted transformation, not model feasibility or performance.
\clearpage
\sectionhead{9\quad Management summary}
''')
summary=(ROOT/'evidence/management_summary.txt').read_text().strip()
chunks.append(esc(summary)+'\n')
chunks.append(r'''\sectionhead{10\quad Process record and rubric evidence}
\subhead{Decisions and checks}
The unchanged input hash, source-row conservation, baseline reproduction, seventeen quality checks, whole-invoice sample, partition overlaps and scaler parameters are executable evidence. \path{evidence/protocol.json} records seed, row rules, time windows, exposure history and the no-test-tuning policy. The notebook is run from a fresh kernel with saved outputs. Exported tables and figures are regenerated from that same code; this report's numeric content is generated from those outputs.

\subhead{Feedback and contributions}
The team-reported C1 result is 100/100. No case-specific correction text is fabricated. Section 4 records five self-audit/extension entries. The members are Mois\'es Medina and Ignacia Castillo; no new individual task division or personal reflection has been invented for W2.

\subhead{AI use and verification}
OpenAI Codex assisted with code, notebook/report drafts and formatting. The implementation request prescribed continuity, invoice sampling, fixed seed, time partitions and a training-only scaler. Accepted suggestions include explicit flags and exported check evidence. Claims that zero prices have a proven discount cause, repeats are proven errors, C invoices establish matched returns, or the holdout is pristine are excluded. Assertions and automated reruns verify consequential suggestions. Those are automated checks, not claims that a particular student personally performed each check. The team is responsible for reviewing and defending the final analysis.
''')
chunks.append(r'{\small'+'\n'+table(['W2 criterion','Inspectable evidence'],[
    ('A Continuity and feedback','Notebook 1--3; preserved assessments; feedback_to_action.csv; unchanged baseline'),
    ('B Revised EDA','Notebook 4; four labelled figures; statistics, denominators and limits'),
    ('C Validation','Notebook 2--3; dictionary; quality_checks.csv; row_flow.csv; exception tables'),
    ('D Sampling','Notebook 5; sample_strata.csv; actual sample; KPI/UK comparison and bias discussion'),
    ('E Leakage','Notebook 7; seven contextual risks with evidence, status and safeguards'),
    ('F Holdout and validation','Notebook 6; actual split files, counts, overlaps, fit parameters and prior-exposure limit'),
    ('G Communication','Executed English notebook; README; summary; AI statement; repository commit/tag')])+ '}\n')
chunks.append(r'''\clearpage
\sectionhead{References and source attribution}
\begin{enumerate}
\item Chen, D. (2015). \emph{Online Retail}. UCI Machine Learning Repository. DOI: \href{https://doi.org/10.24432/C5BW33}{10.24432/C5BW33}. Dataset/dictionary/licence: \url{https://archive.ics.uci.edu/dataset/352/online-retail}. CC BY 4.0. Original retrieval evidence remains in the preserved source manifest; W2 uses the unchanged local extract.
\item Fontecilla, T. (2026). \emph{Workshop 2: From Exploratory Analysis to Credible Validation}. Student brief and rubric supplied in the course workspace. Deadline printed: 29 October 2026.
\item Course notebooks (2026): \emph{Validation, Leakage and Reproducible Pipelines}; \emph{Guided Validation Case}; \emph{Sampling, Regression and Classification}. Used for split selection, leakage and training-only preprocessing. Course files are cited but not redistributed.
\item Medina, M., and Castillo, I. (2026). W1 and C1 submitted project reports and executed notebooks, preserved under \path{assessments/}. Prior concentration evidence and source limitations are retained for continuity.
\end{enumerate}
\end{document}
''')
source='\n'.join(chunks)
path=ROOT/'report/GROUP_Medina_Castillo_W2_Report.tex'
path.write_text(source,encoding='utf-8')
print(path)
print('Management summary words:',len(summary.split()))
