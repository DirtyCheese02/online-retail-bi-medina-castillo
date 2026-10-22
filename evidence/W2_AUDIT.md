# W2 rubric audit — 21 October 2026

## Scope and conclusion

This audit checks the specific *Workshop 2: From Exploratory Analysis to Credible Validation* brief against the primary notebook, its actual data subsets, the README and supplemental report. The 23 scoring components in `rubric_matrix.csv` sum to 100 available points. The table below maps full-credit evidence; it is not an awarded or guaranteed score.

The revised delivery has evidence for every rubric component. Automated acceptance checks pass, including source conservation, unchanged C1 results, actual split and sample contents, fitted-parameter boundaries and notebook outputs. Methodological limitations are disclosed rather than hidden to imply a stronger result.

## Findings corrected during this audit

| Finding | Why it mattered | Correction and evidence |
|---|---|---|
| The three chronological subsets were valid, but the code did not make the nested development/validation construction explicit. | The brief asks for validation drawn from training data, never from test. | Reserve October–November test first; carve August–September validation from the earlier December–September development pool. The final fit set remains December–July. Assertions and `split_hierarchy.csv` verify the parent sets and proportions. Dates and memberships are unchanged. |
| The preprocessing loop applied the rule in order, but the validation decision was chiefly explained in prose. | Criterion F requires an implemented validation plan without test tuning. | An explicit applicability gate checks finite values, positive invoice totals, unique invoice keys and frozen training parameters. Execution stops before test transformation on failure. `validation_execution.csv` records fit → validation → test. No performance threshold is invented. |
| Monthly evidence existed in EDA, but there was no compact, explicitly labelled descriptive holdout finding. | A descriptive holdout should assess robustness of the actual research question. | Add `holdout_monthly_kpi.csv` and `holdout_robustness.csv`, with monthly K10, coverage and population sizes. Means weight months equally; they are neither pooled-window K10 nor predictive scores. Interpretation explicitly retains the prior-exposure limitation. |
| References followed the management summary in the notebook. | The brief says to close with a 120–180-word management summary. | Move references/AI disclosure before the final 141-word summary. The verifier checks that the saved final output contains that summary. |
| The dictionary did not explicitly define all three preprocessing fields. | Their units and availability differ from monetary KPI inputs. | Add invoice value in GBP, log1p invoice value and dimensionless scaled log value, including constraints and missingness. |
| Minor grammar and traceability details needed updating. | Report, notebook and repository should describe the same version. | Correct the timestamp-span phrasing; rebuild the PDF; update README, rubric evidence and artifact hashes. Preserve the original `w2-submission` tag and identify the revised delivery separately. |

These changes are retrospective audit amendments. They do not claim that earlier W1/C1 exploration never occurred or that this is an untouched prospective test.

## Full-credit evidence by criterion

| Criterion | Available points | Evidence checked |
|---|---:|---|
| A. Continuity and feedback | 15 | Same problem, customer/invoice/line units and KPI; C1 reproduction assertions; five grounded self-audit/extension entries with actions, evidence and effects on conclusions. The team-reported C1 grade is distinguished from actual instructor comments. |
| B. Revised EDA | 15 | Four saved figures: distribution, frequency–value relationship, concentration and monthly comparison. Correct GBP/percentage denominators, monthly N, skew/extremes, arithmetic dependence and noncausal interpretation. |
| C. Data validation | 15 | Nineteen dictionary entries; seventeen executable quality checks with PASS/FLAG, affected counts, treatment and rationale; all 516,384 source rows retained; mutually exclusive analytical groups; timestamp and country exception exports. |
| D. Sampling | 10 | Target/observed/analytical populations and coverage biases; seed 4232026; approximately 25% invoices per month with complete invoice lines; actual 25.35% row sample; K10, ID-value coverage and UK-value proportion compared in percentage points. Sampling limits distinguish invoices from customers. |
| E. Leakage | 15 | Month-end decision time and data availability; seven contextual risks, each with evidence, status, consequence and mitigation. Recurring IDs and prior full-case exposure are disclosed; there is no invented predictive target. |
| F. Holdout and validation | 25 | Nested chronological construction; actual train/validation/test files and counts; zero row/invoice/source-record overlap; reported permitted customer overlap; scaler fit only on train; executable validation gate before unchanged test transform; monthly descriptive assessment and exposure limits. |
| G. Communication and reproducibility | 5 | Executed English notebook, README and pinned dependencies; final 141-word management summary; AI disclosure; preserved W1/C1 artifacts; identifiable Git history and audited tag. |

## Checks and numerical interpretation

- `verification.json` records 33 passing acceptance checks. This count is separate from the seventeen source-data quality checks; a source FLAG is an observed condition with treatment, not a failed submission check.
- The baseline remains 4,293 known IDs, K10 **60.500139%**, and ID-value coverage **85.662768%**.
- Mean monthly K10 is **48.91%** in training, **51.01%** in validation and **49.28%** in test. Test differs from training by **+0.37 percentage points**. The annual 60.50% pools longer histories and is not the expected K10 of every month.
- Sample K10 is **54.01%**; its difference from the complete case reflects a different observed history/population, not proof of market representativeness or an unbiased annual estimator.
- The PDF compiles in the integrated editor and bundled Tectonic. All twelve pages were reviewed in a contact sheet; dense/revised pages were reviewed individually, with no overflowing tables or clipped content. See `latex_verification.json`.
- `clean_clone_verification.json` identifies the analysis commit used for independent reproduction from a clean checkout. Execution timestamps are expected to differ and are not numerical evidence.

## Remaining limitations, not unresolved rubric omissions

The retailer and period are historical; some eligible value lacks CustomerID; the item-code rule remains provisional; costs, settlement data and verified purchase–cancellation links are absent. Recurrent accounts create dependence between temporal subsets. W1/C1 already explored the held months. No prediction, causal effect, profit estimate, prospective performance or grade is claimed. Recent transactions and verified identity/code definitions are needed before operational use.

The primary hand-in remains the executed notebook plus repository link and an identifiable commit/tag. The PDF is complementary. W2 does not require a new presentation or ZIP.
