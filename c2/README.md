# C2 — Monthly customer purchase profiles

The updated IIB423T-1 brief supplied by the team sets **8 November 2026 end of day Santiago** for ZIP delivery and **10 November** for presentation. It overrides the old calendar and W2 delivery instructions.

## Submit the ZIP

`delivery/GROUP_Medina_Castillo_C2.zip` contains exactly:

1. `01_C2_Customer_Profiles.ipynb` — executed, English, all project functions inline, saved tables/figures, contribution/AI notes and defense checkpoints.
2. `GROUP_Medina_Castillo_C2_Brief.pdf` — three pages including references, generated from notebook results.
3. `GROUP_Medina_Castillo_C2_Presentation.pptx` — editable presentation, 11 main slides plus a source/defense backup, with speaking notes for approximately 12 minutes including pauses.

No data, environment, source sidecars, README or extra report is inside the ZIP. Saved notebook outputs are readable without running code. Rerunning uses the preserved local W2 input when available, otherwise an exact SHA-256-checked public input at an immutable GitHub commit. That download is documented inside the notebook; all analysis functions are inline.

## Method and W2 continuity

Route: descriptive clustering. One modeling record is one active identified CustomerID in one calendar month. Frequency and average eligible invoice value separate more invoices from larger invoices. Log1p plus StandardScaler and KMeans(k=3) are fitted only on December–July records. The reference groups monthly value using the training 50th/90th percentiles. Validation is August–September, test October–November. Both methods compare on identical records. No predictive target, classification accuracy or untouched-test claim is invented.

The model provides more specific purchase-pattern descriptions than a value tier alone. Test silhouette is 0.464 vs 0.289 for the value rule, an internal geometry diagnostic rather than evidence of better commercial outcomes. The fixed earlier top-decile account group still contributes in later months. Unidentified purchases remain a separate value category; November has 21.45% outside customer profiling.

## Reproduction and audit in the development repository

`c2_analysis.py` is the maintained source embedded by `build_notebook.py`. Execute `python c2/execute_notebook.py` from the repository to rerun the notebook, then `python c2/build_brief.py` to update LaTeX. The built-in LaTeX editor compiles `report/main.tex`. The presentation builder writes native tables/charts in Artifact Session and exports an editable PPTX. `package_submission.py` creates the exact three-file ZIP; `verify_submission.py` checks structure and agreement across artifacts. Those development files are not Canvas hand-in extras.

`C2_PROTOCOL.md` records fixed choices before the model run. `outputs/C2_results.json` is the shared numerical source for brief and presentation. The notebook includes defense questions for rubric F–H. No automatic check can guarantee the individual oral score or a Canvas upload receipt.

## Contributions and AI disclosure

Moisés supplied project materials, the updated brief and actual W2 feedback. Preparation/training review is assigned to Moisés and profiles/reference/interpretation review to Ignacia as planned responsibilities; their completion was not confirmed. The notebook does not invent completed contributions. Codex assisted with code/text/layout drafts and automated verification; students remain responsible for review and defense.

Source: Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33, CC BY 4.0. Exact input attribution and limits are inside the notebook. Earlier W1/C1/W2 files and tags are preserved.
