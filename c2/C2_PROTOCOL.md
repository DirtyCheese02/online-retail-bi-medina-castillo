# C2 protocol fixed before this model run

Recorded 8 November 2026. Source: the specific updated IIB423T-1 C2 brief supplied by the team. It overrides the old calendar and prior W2 delivery format.

## Required delivery

One ZIP containing only executed working notebook(s), a PDF brief of at most three pages including references, and a presentation file. No datasets, environment, README, separate process log or additional reports inside the ZIP. Submit 8 November 2026 end of day Santiago; present 10 November. This workspace preparation does not upload to Canvas.

## One route: descriptive clustering

Question: can monthly purchase frequency and invoice size distinguish useful customer profiles beyond a simple value-only grouping rule?

- Reuse the unchanged W2 raw extract, positive-purchase eligibility and complete calendar months. Retain source repeats; keep missing-ID value outside both grouping methods and visible in a separate value category.
- Modeling unit: one **active identified CustomerID in one calendar month**. A customer can occur in multiple months. Months without an eligible identified purchase do not create an artificial zero record. This studies purchase-active records, not all retailer accounts or churn.
- Inputs: distinct eligible invoice count and mean eligible purchase value per invoice (GBP) within that month. Total monthly value equals their product and is reported for interpretation, but is not added as a redundant third clustering input. No customer ID, country, future purchases or external labels enter the distance calculation.
- Decision time: month-end retrospective account review after the included invoices are recorded. This is not a prediction of a future purchase.
- Apply log1p to the two positive features, then StandardScaler fit only on December 2010–July 2011 records. W2's invoice-value scaler was an illustrative operation at a different unit; C2 needs its own training-only scaler for its actual two monthly features.
- Model: KMeans with k=3, n_init=20, max_iter=300, random_state=4232026 and Lloyd updates. k=3 is an a priori manageable profile count, not an estimated optimal number. Do not search multiple algorithms or k values.
- Reference: group monthly total value using the 50th and 90th percentiles learned on the same training records. Keep those GBP cutoffs fixed for validation/test. This is a simple low/middle/high value rule, not a classifier or known ground truth.
- Reuse W2 split boundaries: training before 1 August 2011, validation August–September, test October–November. Compare both groupings on identical records and scaled inputs. Disclose recurring IDs and prior full-case EDA.
- Validation checks fixed before test: finite features, unchanged fitted parameters, all records assigned, group sizes and silhouette diagnostics. Retain the fixed first model without optimizing from the test. Poor separation is a finding, not a reason to hide or tune the test result.
- Required results: group sizes and original-unit feature profiles, direct reference comparison and limits. Silhouette is a supplementary internal geometry metric on the same records, not accuracy or evidence that actions work.

## Actual W2 feedback

Put all implementation needed for the analysis inside the submitted notebook and retain readable outputs. Use a pinned public input download only when the local raw extract is unavailable; never package data in the ZIP.

After freezing the model/procedure, assess the instructor's business follow-up: freeze the top decile from December–September, follow that same group in October and November, and contrast its value share with each month's re-ranked decile. Report unidentified value as a separate category with all eligible value as denominator. This is a later historical period already explored, not a pristine prospective test or recent 2026 cohort. No extra cohort analysis is required because the feedback offered later-period **or** recent-cohort evidence.

## Contributions and AI

Document Moisés's supplied brief, source/project context and feedback. Assign preparation/training review to Moisés and profiles/reference/conclusions review to Ignacia as **planned responsibilities**, not completed personal work. No completed contribution by Ignacia was confirmed in the conversation. Codex assists with drafts, implementation and automated verification; the team remains responsible for review and individual defense. Do not invent completed contributions or instructor comments.
