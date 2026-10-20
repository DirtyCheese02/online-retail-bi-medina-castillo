# Data attribution and modifications

**Source:** Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33). [Dataset and dictionary](https://archive.ics.uci.edu/dataset/352/online-retail).

**Source licence:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). No endorsement by the data creator or UCI is implied.

The uncleaned case is a source-order extract of the original eight columns for `2010-12-01 <= InvoiceDate < 2011-12-01`. It retains 516,384 of 541,909 rows, excluding the incomplete final December 2011. Original retrieval/exact-workbook evidence and hashes are preserved in `data/raw/source_manifest.json`.

W1/C1 and W2 derivatives add eligibility flags, a positional row key, monetary aggregates, statistical summaries, month-stratified invoice sampling, chronological partitions and a training-fitted log-value scaler. They retain the scoped exceptions and document exclusions from each measure. Monetary measures are positive recorded purchase value, not audited net revenue or profit. All prepared tables and figures are project-derived material; changes are identified in the notebook and report.

The source licence statement applies to UCI data. It is not a licence grant for instructor materials or third-party course documents, which are not included in the public repository.
