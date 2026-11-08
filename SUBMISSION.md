# W2 corrective hand-in — 8 November 2026

**Team:** Moisés Medina and Ignacia Castillo  
**Repository:** https://github.com/DirtyCheese02/online-retail-bi-medina-castillo  
**Corrective release:** `w2-feedback-2026-11-08`  
**Versioned tree:** https://github.com/DirtyCheese02/online-retail-bi-medina-castillo/tree/w2-feedback-2026-11-08

This release addresses feedback about evidence absent from the received hand-in. It does not assert that those files were delivered on time or that a grade has been changed.

## Attach these files when submitting

1. **Executed English notebook:** `notebooks/W2_project.ipynb`.
2. **Execution/provenance instructions:** `README.md`.
3. **Supplemental PDF:** `report/GROUP_Medina_Castillo_W2_Report.pdf`.
4. Include the repository/tree link and full submitted commit SHA in the submission text. The code modules and data are part of the repository: downloading only the notebook without its relative dependencies is insufficient to rerun it.

[Open notebook](https://github.com/DirtyCheese02/online-retail-bi-medina-castillo/blob/w2-feedback-2026-11-08/notebooks/W2_project.ipynb) · [Download notebook](https://raw.githubusercontent.com/DirtyCheese02/online-retail-bi-medina-castillo/w2-feedback-2026-11-08/notebooks/W2_project.ipynb) · [README](https://github.com/DirtyCheese02/online-retail-bi-medina-castillo/blob/w2-feedback-2026-11-08/README.md)

## Inspect the evidence behind the feedback

| Feedback | Evidence in this repository |
|---|---|
| C2: programmatic quality checks | `src/w2_analysis.py`, function `validate`; notebook section 3; `data/processed/quality_checks.csv` |
| D2: reproducible invoice sample | Function `sample_invoices`; `sample_invoice_ids.csv`, `sample_strata.csv`, actual `invoice_sample_25pct.csv.gz` |
| F2: real subsets and overlap | Function `make_splits`; `data/splits/{train,validation,test}.csv.gz`; `split_membership.csv`, `split_overlap.csv` |
| F3: training-only scaler | Function `preprocess`; `preprocessing_parameters.json`; `invoice_preprocessing.csv` |
| F4: validation/test boundary | Function `preprocess`; `validation_execution.csv`; `split_hierarchy.csv` |
| G1: primary artifacts | Executed notebook and README above; code and data remain included in the versioned tree |
| G2: verifiable identity | PDF front page and evidence index; `evidence/submission_identity.json`; release tag |

The immutable analytical baseline is commit `d33a27c97a3bb9e6b31fb9cb23be83156c11d0f3`. Its rules, raw input and baseline results are unchanged. The corrective release adds feedback response, accessible evidence and an initial decomposition of unidentified value; it has its own later commit/tag.

To obtain the full corrective commit SHA after publication:

```sh
git rev-parse 'w2-feedback-2026-11-08^{commit}'
```

Do not submit only this document or only the PDF. See `evidence/W2_feedback_response.csv` for the response to all seven deductions and `docs/C2_FEEDBACK_PLAN.md` for the two next-stage research recommendations.
