# C2 audit against the updated IIB423T-1 brief

Prepared 8 November 2026. This maps evidence to available rubric points; it does not assign an instructor grade or certify personal understanding. The specific C2 brief overrides the old calendar and W2 packaging instructions.

## Team deliverable: 60 available points

| Criterion | Maximum | Evidence in the actual ZIP |
|---|---:|---|
| A. Task and W2 feedback | 5 | Notebook sections 1–4 define the descriptive grouping question, active identified ID-month unit, two available month-end inputs and W2 preparation. Section 1 explains missing received W2 executable evidence; all project functions are now inline. Section 7 implements the instructor's later-period and separate-unidentified-value recommendations. Brief pages 1 and 3 summarize that continuity. |
| B. Training and reference comparison | 20 | The notebook visibly fits KMeans with k=3, n_init=20, max_iter=300, Lloyd updates and seed 4232026 on 7,195 training records. The simple reference learns monthly-value training percentiles and reuses fixed cutoffs. Both methods assign the same held records. Brief pages 1–2 and slides 5–8 explain the choice, settings and comparison. |
| C. Evaluation and metrics | 20 | W2 raw counts/windows reproduce; 7,195 / 2,192 / 3,021 active ID-months are explicit. Scaler and centers fit only training. The validation gate precedes final test assignment; unchanged parameters are asserted. Both methods report profiles, group sizes, cross-table and silhouette on identical records/inputs. No true labels, accuracy, predictive score, independent-customer sample or pristine-test claim is invented. |
| D. Interpretation | 10 | Profiles distinguish frequency and invoice size; the reference remains adequate for contribution-only questions. The silhouette advantage is limited to the specified geometry. Missing IDs, repeated accounts, feature/scaling choices and historical/prior exposure limits are stated. Recent linked transactions and stakeholder review are proposed improvements. |
| E. Clear and complete submission | 5 | The ZIP contains one executed English notebook, a three-page brief including references and an editable presentation. Numeric outputs are shared and checked. Source/AI/contribution notes are inside the notebook. Documented inputs and planned personal reviews are distinguished honestly; their completion is not fabricated. |

## Individual defense: 40 available points

| Criterion | Maximum | Preparation provided, not an awarded score |
|---|---:|---|
| F. Method | 15 | Notebook section 10 covers unit, eligibility, aggregation, two-feature choice, log1p/scaling, KMeans centers, k and train/validation/test use. Slides 3–6 and their notes explain the same procedure. |
| G. Results | 15 | Sections 5–7 and slides 6–10 explain silhouette, profile medians/counts, reference cross-table and value denominators. Distinguish internal separation from accuracy and from business impact. |
| H. Conclusions and limits | 10 | Section 8 and slides 10–12 connect manual account review/ID capture to the evidence, explain historical/missing-ID/recurrence limits, and justify recent linked data as an improvement. Each member must explain those ideas independently. |

## Final checks and scope

- `outputs/C2_verification.json` records 53 passing structural and numerical acceptance checks, including the exact three-file ZIP and editable chart/table evidence. Each scatter is independently checked against the saved held records and frozen model parameters.
- `outputs/standalone_zip_verification.json` records a full execution from the extracted ZIP outside the repository, with no project code sidecars. The notebook downloaded the pinned public input, checked SHA-256 and reproduced model/business results.
- The brief compiles with the built-in LaTeX editor and bundled Tectonic, stays within three pages and has no overfull content warnings. All three pages were visually reviewed.
- All thirteen slides were rendered and reviewed. Ten native charts and one backup table remain editable. Finalization verifies chart caches against ten embedded literal workbooks, slide dimensions, fonts, structure and first-party re-import. This is not a claim of opening the file in native PowerPoint.
- The presentation has twelve main slides for a target rehearsal of about thirteen minutes including pauses, plus one source/defense backup. Speaking notes are included. The duration is a rehearsal target, not a measured student performance.
- Personal preparation review remains the students' responsibility. Neither a grade nor a Canvas receipt is asserted. Earlier W1/C1/W2 files and tags remain preserved.

## Corrections during verification

The final brief explicitly explains that separately calculated group medians need not multiply to the median monthly total. Executable code and outputs were unchanged by that prose clarification. In the presentation revision, chart fractions use ten decimal places, scatter coordinates six, and displayed GBP medians two, solely for portable Excel/PPTX storage and legibility. Notebook/brief calculations retain full precision. The ten chart caches are independently checked against notebook outputs or frozen-parameter transformations with those rounding tolerances. The notebook and brief remain byte-identical to the original C2 release.

The Canvas hand-in is **only** `GROUP_Medina_Castillo_C2.zip`. It contains no dataset, README, environment, separate process log, extra report or source sidecar. Those development/audit files remain in the repository outside the ZIP.
