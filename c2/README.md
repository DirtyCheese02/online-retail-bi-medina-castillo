# C2 — Monthly customer purchase profiles

The updated IIB423T-1 brief supplied by the team sets **8 November 2026 end of day Santiago** for ZIP delivery and **10 November** for presentation. It overrides the old calendar and W2 delivery instructions.

## Submit the ZIP

`delivery/GROUP_Medina_Castillo_C2.zip` contains exactly:

1. `01_C2_Customer_Profiles.ipynb` — executed, English, all project functions inline, saved tables/figures, contribution/AI notes and defense checkpoints.
2. `GROUP_Medina_Castillo_C2_Brief.pdf` — three pages including references, generated from notebook results.
3. `GROUP_Medina_Castillo_C2_Presentation.pptx` — editable presentation, 13 main slides plus a source/defense backup, with speaking notes for approximately 14 minutes including pauses. Slide 2 summarizes the C1 analysis and conclusion before introducing C2.

No data, environment, source sidecars, README or extra report is inside the ZIP. Saved notebook outputs are readable without running code. Rerunning uses the preserved local W2 input when available, otherwise an exact SHA-256-checked public input at an immutable GitHub commit. That download is documented inside the notebook; all analysis functions are inline.

## Method and W2 continuity

Route: descriptive clustering. One modeling record is one active identified CustomerID in one calendar month. Frequency and average eligible invoice value separate more invoices from larger invoices. Log1p plus StandardScaler and KMeans(k=3) are fitted only on December–July records. The reference groups monthly value using the training 50th/90th percentiles. Validation is August–September, test October–November. Both methods compare on identical records. No predictive target, classification accuracy or untouched-test claim is invented.

The model provides more specific purchase-pattern descriptions than a value tier alone. Test silhouette is 0.464 vs 0.289 for the value rule, an internal geometry diagnostic rather than evidence of better commercial outcomes. The fixed earlier top-decile account group still contributes in later months. Unidentified purchases remain a separate value category; November has 21.45% outside customer profiling.

## Reproduction and audit in the development repository

`c2_analysis.py` is the maintained source embedded by `build_notebook.py`. Execute `python c2/execute_notebook.py` from the repository to rerun the notebook, then `python c2/build_brief.py` to update LaTeX. The built-in LaTeX editor compiles `report/main.tex`. The presentation builder writes native tables/charts in Artifact Session and exports an editable PPTX. `package_submission.py` creates the exact three-file ZIP; `verify_submission.py` checks structure and agreement across artifacts. Those development files are not Canvas hand-in extras.

`C2_PROTOCOL.md` records fixed choices before the model run. `outputs/C2_results.json` is the shared numerical source for brief and presentation. The notebook includes defense questions for rubric F–H. No automatic check can guarantee the individual oral score or a Canvas upload receipt.

## Presentation revision

The revised deck follows the team's C1 visual reference: Montserrat titles, large figures, navy/paper backgrounds and teal/orange charts. Ten native charts replace most tables: chronological populations, validation silhouette, two complete held-record scatter plots, profile sizes and medians, reference-tier composition, later account contribution and unidentified value. All charts have embedded editable workbooks. The backup retains the exact cross-table.

`presentation/prepare_visual_data.py` reconstructs the held coordinates and assignments from the saved monthly records and frozen model parameters without retraining. `presentation/build_visual_deck.mjs` authors the revised deck through Artifact Session using `visual_data.json`, the two C1 cover assets and `speaker_notes_source.json`. Monetary chart medians display two decimals; scatter coordinates use six decimals and chart percentage fractions use ten solely for Excel portability. Calculations in the notebook remain unchanged.

The original C2 submission and both visual revisions remain preserved at their tags. The release `c2-audited-2026-11-08` clarifies the model verdict in notebook, brief and presentation. The analytical code, settings and numerical conclusions are unchanged. The revised notebook was freshly executed outside the repository and reproduced the frozen parameters, profiles, metrics and business follow-up. See `outputs/model_verdict_rerun.json`.

The role update `c2-roles-2026-11-08` records the agreed division of responsibilities for final review and defense. Moisés covers data preparation, features, model and evaluation; Ignacia covers profiles, reference comparison and business conclusions; both cover the question, methodology, final review and presentation. Allocation does not certify that every review task is complete. Rubric F–H assess each student's own explanation; file checks do not certify those 40 individual points.

`presentation/C2_Presentation_Dialogue_EN.md` is the English rehearsal script for the current 13 main slides, with no assigned speakers. It includes a backup-table explanation and plain-language defense answers on KMeans, the reference rule, silhouette, temporal splitting and possible future marketing studies. The target is 12–13 minutes with chart pauses; actual duration requires rehearsal. It is a preparation aid outside the three-file Canvas ZIP.

## Contributions and AI disclosure

Moisés supplied project materials, the updated brief and actual W2 feedback. The notebook records the agreed review/defense responsibilities above. Codex assisted with code/text/layout drafts and automated verification; students remain responsible for review and defense.

Source: Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33, CC BY 4.0. Exact input attribution and limits are inside the notebook. Earlier W1/C1/W2 files and tags are preserved.
