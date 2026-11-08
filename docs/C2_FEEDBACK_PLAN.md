# C2 continuation from the actual W2 feedback

Recorded 8 November 2026 from the instructor feedback relayed by the team. This is a proposed next-stage protocol, not completed C2 evidence or an inferred C2 rubric.

## 1. Concentration in a later period or recently observed cohort

The existing monthly K10 analysis re-ranks customers every month. It does not establish that the same important accounts remain important. C2 should distinguish concentration level from account persistence.

- Fix a reference window ending 30 September 2011; identify its highest-value 10% using only information recorded by that date.
- Follow that fixed group during October–November 2011. Compare its share of eligible known-ID value, active-account counts and coverage with the contemporaneous re-ranked top decile. State each denominator explicitly. A missing subsequent purchase is not proof of churn.
- As a separate cohort analysis, define a customer's first observed purchase date from eligible identified records. Use equal follow-up durations and exclude or flag incomplete follow-up. First observed in this file does not mean a genuinely newly acquired customer; the source is left-truncated.
- These are later periods within the historical file, already exposed in W1/C1/W2. They are retrospective extensions, not pristine prospective tests or evidence about current 2026 customers. A genuinely recent cohort requires additional recent data, which are not currently available.
- Fix comparison windows, grouping rules and interpretation before calculating the extension. If a predictive method is required by the C2 brief, first define its future outcome, prediction time and leakage-safe evaluation; do not invent churn labels from silence.

## 2. Decisions when unidentified value is a separate category

Keep three mutually exclusive value buckets: purchases attributed to the known-ID top group, purchases attributed to other known IDs, and purchases without a CustomerID. Use **all eligible positive purchase value** as their common denominator. Keep K10 itself unchanged and based on known IDs.

`evidence/value_scope_bridge.csv` supplies the initial accounting decomposition from the existing baseline. It is not a ranking of unidentified customers. An unidentified-value bucket can contain many real people and must never be counted as one customer or assigned an invented ID.

Decisions to evaluate:

- **Defensible:** inspect the identified major accounts and their invoices; investigate ID capture for the separate unidentified bucket; monitor concentration together with coverage.
- **Not established:** the known top group is the top group of all real customers; unidentified value belongs to small accounts; a loyalty/discount campaign would raise profit; missing IDs caused a monthly K10 change.
- **Further evidence needed:** verified customer linkage, product-code definitions, costs and intervention outcomes before customer-specific allocation, profitability claims or causal recommendations.

## 3. Submission controls

Attach the executed English notebook and README when requested. Include source modules and data through a direct, versioned public repository link. Put repository URL, full submitted SHA, release tag and notebook link into the hand-in text and PDF. Verify that every link opens the intended version. Keep the original assessed W2 history; a corrective release is not evidence that the missing files were received on time.

The exact C2 deliverables and dates must follow its specific brief when available. No new model, dashboard or presentation is asserted to be required merely by this plan.
