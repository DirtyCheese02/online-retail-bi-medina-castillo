"""Three-page LaTeX brief generated from the executed C2 notebook's results."""
from pathlib import Path
import json
import pandas as pd

HERE=Path(__file__).resolve().parent
R=json.loads((HERE/'outputs/C2_results.json').read_text(encoding='utf-8'))
P=pd.DataFrame(R['test_profiles']);M=pd.DataFrame(R['metrics']);S=pd.DataFrame(R['stability']);B=pd.DataFrame(R['value_bridge'])
F=R['frozen_model']
def n(x,d=0): return f'{x:,.{d}f}'
def table(headers,rows,spec=None):
    spec=spec or ('@{}'+'X'*len(headers)+'@{}')
    body='\n'.join(' & '.join(str(x).replace('%',r'\%') for x in row)+r' \\' for row in rows)
    return r'\begin{tabularx}{\linewidth}{'+spec+'}\n'+r'\toprule'+' & '.join(r'\textbf{'+x+'}' for x in headers)+r' \\ \midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabularx}'

tmetric=M[M.partition.eq('test')].set_index('method').silhouette
vmetric=M[M.partition.eq('validation')].set_index('method').silhouette
groups=P[P.method.eq('KMeans')]
parts=pd.DataFrame(R['model_partitions'])
sourceparts=pd.DataFrame(R['source_partitions'])
content=[r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=1.8cm,top=1.65cm,bottom=1.7cm]{geometry}
\usepackage[T1]{fontenc}\usepackage{lmodern,microtype,booktabs,tabularx,array,graphicx,xcolor,amsmath,fancyhdr,xurl}
\usepackage[colorlinks=true,urlcolor=blue!60!black]{hyperref}
\definecolor{navy}{HTML}{173E56}\definecolor{teal}{HTML}{087F85}\definecolor{muted}{HTML}{586974}
\graphicspath{{../outputs/}}\setlength{\parindent}{0pt}\setlength{\parskip}{.35em}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}\renewcommand{\arraystretch}{1.16}
\setlength{\emergencystretch}{2em}\pagestyle{fancy}\fancyhf{}\setlength{\headheight}{15pt}
\fancyhead[L]{\small\color{muted}Business Intelligence / C2}\fancyhead[R]{\small\color{muted}Medina \& Castillo}
\fancyfoot[R]{\small\thepage}\renewcommand{\headrulewidth}{.3pt}
\newcommand{\heading}[1]{\vspace{.3em}{\large\bfseries\color{navy}#1}\par}
\begin{document}\thispagestyle{empty}
{\small\bfseries\color{teal} IIB423T-1 / C2 BRIEF}\par
{\LARGE\bfseries Monthly customer purchase profiles}\par
{\color{muted}Mois\'es Medina and Ignacia Castillo\hfill 8 November 2026}\par
\heading{1. Question and continuity}
Can monthly purchase frequency and invoice size distinguish useful customer profiles beyond a simple value-only grouping rule? We choose descriptive clustering to support a proposed month-end account review. W2 found that 430 of 4,293 identified customers contributed 60.5\% of identified annual purchase value, with IDs covering 85.7\% of eligible value. That ranking measures contribution but does not distinguish more invoices from larger invoices.

We reuse UCI Online Retail and W2's unchanged complete-month extract: 516,384 invoice lines, December 2010--November 2011. A source line is an item entry on an invoice. Our \textbf{modeling row is one active identified CustomerID-month}; recurring IDs are intentional. Accounts without an eligible identified purchase in a month do not become artificial zero records.

\textbf{W2 feedback response.} The received W2 hand-in lacked executable evidence and version links. C2 now includes an executed notebook with all project functions inline, readable outputs and a source link. We also follow an earlier fixed account group into later months and keep unidentified value separate. The ZIP contains only that notebook, this three-page brief and the presentation, following the updated C2 format.

\heading{2. Preparation and evaluation records}
Purchases require positive quantity/price, no C prefix and a provisional five-digit item code with an optional final letter. We retain every source row, keep exact repeats as in W2, and do not impute IDs or prices. Missing IDs stay in value coverage but cannot enter either customer grouping. The code pattern is a scope assumption, not a verified commercial category.
''']
partrows=[]
for i,k in enumerate(['train','validation','test']):
    row=parts.loc[parts.split.eq(k)].iloc[0];raw=sourceparts.loc[sourceparts.split.eq(k)].iloc[0]
    count=row.get('active_ID_months',row.get('monthly_records'))
    unique=row.get('unique_active_IDs',row.get('unique_active_ids'))
    partrows.append(({'train':'Train: Dec--Jul','validation':'Validation: Aug--Sep','test':'Test: Oct--Nov'}[k],n(raw.source_rows),n(count),n(unique)))
content.append(table(['Period','Source lines','Active ID-months','Unique active IDs'],partrows,'@{}Yrrr@{}'))
content.append(r'''
Test is reserved first; validation comes from the earlier development pool. No invoice or ID-month crosses partitions. Shared CustomerIDs mean these are not independent new-customer populations. All periods were explored in earlier EDA: the later assessment is retrospective, not pristine prospective evidence.

\heading{3. First model and reference}
For each ID-month, $F$ is the number of distinct eligible invoices and $A$ is eligible purchase value per invoice (GBP). Monthly value is $F\times A$; adding it as a third clustering input would repeat the information. Inputs are available only after the month's invoices are recorded. This is grouping, not a forecast.

We apply $\log(1+x)$ to $F$ and $A$, then fit StandardScaler and KMeans \textbf{only on 7,195 training ID-months}. Logarithms reduce the influence of large ranges, and scaling prevents GBP from dominating counts. Large accounts remain. Settings are fixed: $k=3$, 20 initializations, 300 maximum iterations, Lloyd updates and seed 4232026. Three groups are a manageable first description, not an estimated optimal $k$.
''')
content.append(f'The reference groups monthly value using training percentiles: lower up to \\pounds{{}}{F["reference_p50_gbp"]:.2f}, middle up to \\pounds{{}}{F["reference_p90_gbp"]:.3f}, and higher above that cutoff. Both methods keep their learned rules fixed for validation and test. Validation checks finite inputs, complete assignments, populated groups and invariant fitted parameters before test assessment. No test result selects settings.\n')
content.append(r'''\newpage
\heading{4. Results on the same 3,021 test ID-months}
The test contains 2,405 distinct active IDs across October--November. A person can appear in both months and can change profile, so group sizes count ID-month records rather than permanent customer types.
''')
content.append(table(['KMeans profile','Records','Share','Median $F$','Median $A$ (GBP)','Median monthly GBP'],[
    (r.group,n(r.records),f'{r.record_share_pct:.1f}%',f'{r.median_invoices:.0f}',f'{r.median_invoice_value_gbp:.2f}',f'{r.median_monthly_value_gbp:.2f}') for r in groups.itertuples()],
    '@{}Yrrrrr@{}'))
content.append(r'''The $A$ column is the median of each ID-month's average eligible invoice value. Separately calculated group medians need not multiply to median monthly value. Profile 1 has smaller invoices; Profile 2 mostly has one larger invoice; Profile 3 has more frequent purchases. Those descriptions follow observed medians, not known labels such as loyal or profitable.

\begin{center}\includegraphics[width=\linewidth]{reference_vs_profiles.png}\end{center}
{\small Each point is an active identified test ID-month. Axes use logarithms; all records remain. Left: the fixed training-value reference. Right: the frozen KMeans assignment.}
''')
content.append(table(['Internal separation metric','Validation: KMeans / reference','Test: KMeans / reference'],[
    ('Silhouette',f'{vmetric["KMeans"]:.3f} / {vmetric["Value rule"]:.3f}',f'{tmetric["KMeans"]:.3f} / {tmetric["Value rule"]:.3f}')], '@{}YYY@{}'))
content.append(r'''Silhouette compares within-group distances with distances to the nearest other group; larger values indicate clearer separation in this scaled feature space. Both methods use identical evaluation records and inputs. It is \textbf{not classification accuracy}, and there are no target labels. KMeans optimizes a related distance objective, so this advantage does not establish better commercial outcomes.

The reference's higher-value group contains 380 test ID-months (12.6\%); its share need not remain 10\% because the training cutoff stays fixed. Of those 380 records, 124 fall in Profile 2 and 256 in Profile 3. Thus high recorded value can reflect different purchase patterns. The notebook includes the complete cross-table and both sets of profiles.
''')
p3=groups.loc[groups['group'].eq('Profile 3')].iloc[0]
content.append(f'Profile 3 represents {p3.record_share_pct:.1f}\\% of test ID-months and {p3.known_value_share_pct:.1f}\\% of identified test value. This supports examining its accounts and invoices, while the value-only rule remains a simpler option when contribution alone is the question. Neither description estimates profit or an intervention effect.\n')
content.append(r'''\newpage
\heading{5. Later account contribution and unidentified value}
Using December--September records only, we freeze the highest-value 362 of 3,613 known IDs and follow that same review group later. This addresses the instructor's stability question. Its size differs from each monthly top decile, so the table is a persistence diagnostic, not a like-sized model contest.
''')
content.append(table(['Later month','Frozen IDs active','Frozen group / known value','Re-ranked K10','Unidentified / all value'],[
    (r.month,f'{r.frozen_ids_active:.0f} / {r.frozen_review_ids:.0f}',f'{r.frozen_group_known_value_pct:.2f}%',f'{r.reranked_K10_pct:.2f}%',f'{100-r.ID_coverage_pct:.2f}%') for r in S.itertuples()],
    '@{}YYYYY@{}'))
content.append(r'''The earlier review group continues to contribute substantial identified value, with varying activity. Missing purchases in one later month do not establish churn. Different coverage and account mixes prevent attributing the change to one cause.
''')
content.append(table(['Share of all eligible value','October','November'],[
    (col,f'{B.iloc[0][col]:.2f}%',f'{B.iloc[1][col]:.2f}%') for col in ['Known top-decile purchases','Other identified purchases','Unidentified purchases']], '@{}Yrr@{}'))
content.append(r'''Each month's three shares sum to 100\% before rounding. Unidentified value may belong to many people and is never treated as one customer or one cluster. In November, 21.45\% of eligible value is outside customer profiling. The annual 60.5\% K10 and these monthly shares have different windows and denominators.

\heading{6. Model verdict, limit and improvement}
\textbf{Model verdict.} Retain this first model for descriptive profiling. It assigns all later records to three interpretable groups. Test silhouette 0.464 exceeds the value rule's 0.289 and is close to validation 0.472. This supports describing the selected purchase patterns; commercial usefulness remains unvalidated. There is no universal silhouette pass mark or pristine prospective test.

\textbf{Proposed use.} Structure manual account review with the profiles and investigate ID capture. Retain the simple value rule when contribution alone is the question. Automated actions and campaign effects require further evidence.

\textbf{Important limits.} The profiles cover purchase-active identified historical records. Missing identities, provisional item codes, repeated participation and varying month lengths limit interpretation. KMeans imposes three Euclidean groups and depends on the chosen scaling/features. Previous full-period exploration limits any claim of untouched testing. We do not establish current market behavior, permanent segments, future loss or causal effects.

\textbf{Next improvement.} Obtain recent transactions and verified customer linkage, apply the frozen rule to comparable complete months, and review profile usefulness with a commercial stakeholder. That would provide evidence beyond this already-explored historical period.

\textbf{AI and responsibility.} Codex assisted with code/text/layout drafts and automated execution/consistency checks. The notebook records documented inputs, planned member reviews and verification. Each member remains responsible for reviewing and explaining the submitted work.

\heading{References and submitted evidence}
{\small
Chen, D. (2015). \emph{Online Retail}. UCI Machine Learning Repository. \href{https://doi.org/10.24432/C5BW33}{doi:10.24432/C5BW33}. CC BY 4.0.\par
scikit-learn 1.5.2: \href{https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.KMeans.html}{KMeans}, \href{https://scikit-learn.org/1.5/modules/generated/sklearn.preprocessing.StandardScaler.html}{StandardScaler}, \href{https://scikit-learn.org/1.5/modules/generated/sklearn.metrics.silhouette_score.html}{silhouette score}.\par
Fontecilla, T. (2026). \emph{C2: Train and explain your first model}, updated IIB423T-1 brief; course notebooks on clustering and validation.\par
Executed evidence: \path{01_C2_Customer_Profiles.ipynb}. Presentation: \path{GROUP_Medina_Castillo_C2_Presentation.pptx}. \href{https://github.com/DirtyCheese02/online-retail-bi-medina-castillo/tree/c2-audited-2026-11-08}{Versioned project repository}. The ZIP contains only notebook, brief and presentation.
}
\end{document}
''')
path=HERE/'report/main.tex';path.write_text('\n'.join(content),encoding='utf-8');print(path)
