"""Build a self-contained-code C2 notebook; the hand-in ZIP needs no source sidecars."""
from pathlib import Path
import ast
import nbformat as nbf

HERE=Path(__file__).resolve().parent
source=(HERE/'c2_analysis.py').read_text(encoding='utf-8')
tree=ast.parse(source)
functions={n.name:ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))
def defs(*names): return '\n\n'.join(functions[n] for n in names)

md('''# C2 — Monthly customer purchase profiles
**Moisés Medina and Ignacia Castillo · Business Intelligence IIB423T-1 · 8 November 2026**

**Route: descriptive clustering.** Our question is: **can monthly purchase frequency and invoice size distinguish useful customer profiles beyond a simple value-only grouping rule?** We propose using those profiles for an analyst's month-end account review, while keeping unidentified purchase value visible. This is a proposed decision aid, not the retailer's documented strategy or a forecast.

W2 found concentration among identified customers, but a value ranking does not explain whether an account contributes through more invoices or larger invoices. We train one KMeans model and compare it with one simple value grouping rule. There are no known target labels and no classification accuracy, churn prediction or claimed intervention effect.

## 1. W2 feedback and delivery correction

The actual W2 feedback reported missing **received executable evidence**: the notebook, sample identifiers, subsets, preprocessing/gate implementation and repository version links. The corrected W2 repository now exposes those files. For C2, **all functions needed below are visible inside this notebook**. We submit the executed notebook, a brief of at most three pages and an editable presentation in one ZIP, without data or environment folders, as the updated C2 brief requires.

The instructor also asked for later-period/cohort evidence and a separate unidentified-value category. Section 7 follows an earlier fixed review group into October–November and reports unidentified value separately. These historical months were already explored in W1/C1/W2, so they are not pristine prospective evidence.

## 2. Reproducible source and setup

Source: Chen (2015), **UCI Online Retail**, DOI 10.24432/C5BW33, CC BY 4.0. The original XLSX has 541,909 invoice lines from 1 December 2010 to 9 December 2011. We reuse W2's unchanged **516,384-line complete-month extract**, excluding only partial December 2011. A SHA-256 check verifies the extract. When the local project input is unavailable, this notebook downloads that exact public extract from an immutable repository commit. No dataset is embedded in the submission ZIP. Saved outputs remain readable without rerunning or network access.

The analysis used Python 3.12.5, numpy 2.1.0, pandas 2.2.2, matplotlib 3.9.2 and scikit-learn 1.5.2. All project code is inline. To rerun in a suitable Python/Jupyter environment, run cells in order; no new environment or installation package is required by the brief.''')
setup=source[:source.index('def load_source')].strip()
code(setup+'''
from IPython.display import display, Markdown, Image
import platform, sklearn
pd.set_option('display.max_columns',20)
pd.set_option('display.max_colwidth',110)
OUT=Path.cwd()/'outputs'
OUT.mkdir(exist_ok=True)
print('Python:',platform.python_version(),'scikit-learn:',sklearn.__version__)
print('Seed:',SEED,'Model: KMeans(k=3, n_init=20, max_iter=300, algorithm=lloyd)')
print('Preparation and windows remain fixed from W2. Model choices are fixed before the results below.')''')
md('''### What one source line means

One row is one **item entry on an invoice**. Several lines can form one invoice, and a CustomerID can link several invoices. The eight source fields are:

| Function | Original fields | Interpretation |
|---|---|---|
| Invoice and item keys | InvoiceNo, StockCode, Description | A C-prefixed invoice is a cancellation record; StockCode is not a verified commercial category. |
| Recorded activity | Quantity, InvoiceDate, UnitPrice | Signed units, recorded timestamp and unit price in GBP. |
| Customer context | CustomerID, Country | Account identifier and the country label on that source line. |

**The model uses a different unit:** one *active identified customer in one calendar month*. For example, a customer with two eligible invoices totalling £100 has frequency 2 and mean invoice value £50 for that month. This example explains the aggregation; it is not an asserted source record.''')
code(defs('load_source','check_preparation')+'''
data,source_info=load_source()
quality,row_flow,source_partitions=check_preparation(data)
display(pd.DataFrame([source_info]))
display(quality)
display(row_flow)
display(source_partitions)
display(data[['InvoiceNo','StockCode','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']].head(3))''')
md('''### Why the eligibility rules remain

An eligible purchase has positive quantity/price, a non-C invoice and a provisional StockCode pattern of five digits with an optional final letter. Value is `Quantity × UnitPrice` in GBP. We retain every source line and distinguish purchases, eligible C records and other retained lines. Only scoped positive purchases enter the value measure.

- Missing CustomerID: retain its eligible value in coverage, but neither grouping method can assign a profile to an unknown identity.
- Zero/negative prices or quantities: retain the source entry outside the positive-purchase measure. We do not invent a discount explanation or fill prices with another month.
- Exact repeats: retain W2's baseline because no unique line ID proves them erroneous.
- Missing descriptions: do not exclude solely for description; the recorded item key is StockCode.
- Code-pattern exceptions: retain the source record and disclose the provisional scope. This pattern is not a verified product taxonomy.

These rules reproduce W2's 500,531 eligible purchase lines and 4,293 annual known IDs. The descriptive value is not audited net revenue, profit, loyalty or lifetime value.''')
md('''## 3. Modeling records, features and chronological partitions

We aggregate eligible identified lines into invoices, then invoices into **CustomerID-month** records. Months without an eligible identified purchase do not become artificial zeros. The target population here is the *observed purchase-active identified account-months*, not all retailer customers or all real purchases. A customer may occur in several months and can have different profiles over time.

| Feature | Definition and unit | Why include it? |
|---|---|---|
| `invoices` | Distinct eligible InvoiceNo count per ID-month | Describes purchase frequency in the observed month. |
| `mean_invoice_value_gbp` | Eligible monthly value / invoice count, GBP per invoice | Distinguishes larger invoices from more frequent ones. |

Monthly value equals frequency × mean invoice value. We report it for business interpretation and the reference rule; adding it as a third clustering feature would repeat the same information. CustomerID and country never enter the distance calculation. A completed calendar month is the business review window; month lengths and activity still differ.

We reuse W2 dates: **train December–July; validation August–September; test October–November**. Test is reserved first; validation is drawn from the earlier development period. No invoice or ID-month crosses a partition. Recurrent CustomerIDs are allowed for a same-account temporal review and do not establish independent new-customer generalization.''')
code(defs('monthly_records')+'''
monthly,parts=monthly_records(data)
model_partitions=pd.DataFrame([{'split':k,'active_ID_months':len(v),'unique_active_IDs':v.CustomerID.nunique(),'months':v.month.nunique()} for k,v in parts.items()])
display(model_partitions)
overlap_rows=[]
for a,b in [('train','validation'),('train','test'),('validation','test')]:
    keys_a=set(zip(parts[a].month,parts[a].CustomerID));keys_b=set(zip(parts[b].month,parts[b].CustomerID))
    assert not(keys_a & keys_b)
    overlap_rows.append({'left':a,'right':b,'shared_ID_months':len(keys_a & keys_b),
                         'shared_CustomerIDs':len(set(parts[a].CustomerID)&set(parts[b].CustomerID))})
display(pd.DataFrame(overlap_rows))
display(parts['train'][['month','CustomerID',*FEATURES,'monthly_value_gbp']].head())''')
md('''## 4. One trained model and one reference

**KMeans** repeatedly assigns each record to its nearest center and updates the centers to minimize the sum of squared Euclidean distances. We fix **k=3**, seed 4232026, 20 initializations, at most 300 iterations and Lloyd updates. Three profiles are a manageable first description, not an empirically established optimal number. We do not search algorithms or k values.

Both inputs are positive and skewed. We apply `log1p` to reduce the influence of large ranges, then fit **StandardScaler only on training records** so GBP does not dominate invoice count. Large accounts remain in the data. Scaling changes distances and thus the meaning of similarity; it does not change GBP used for K10 or reporting. W2 demonstrated a scaler at invoice level. The actual C2 monthly features require a new training-only fit at their own unit.

**Reference:** a simple monthly-value rule. Learn the training 50th and 90th percentile cutoffs, then keep them fixed: lower, middle and higher recorded value. Its later-period proportions need not remain 50/40/10. It is a reference partition, not a set of true customer classes.

All features for an ID-month are available **after that month's close**. This is a retrospective grouping, not a before-purchase prediction. No information from future months enters an earlier record.''')
code(defs('fit_first_model','parameters_unchanged')+'''
scaler,model,cluster_names,cuts,frozen=fit_first_model(parts['train'])
frozen_fingerprint=hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()
display(pd.DataFrame({'feature':FEATURES,'training_log_mean':scaler.mean_,'training_log_SD':scaler.scale_}))
print('Training records used for fit:',scaler.n_samples_seen_)
print('Reference value cutoffs (GBP, exact):',cuts.tolist())
print('Frozen settings fingerprint:',frozen_fingerprint)
print('No fit is performed on validation or test.')''')
md('''## 5. Validation before test

We inspect whether the fixed model and reference can assign every validation record, whether all groups are populated, and whether the learned parameters remain unchanged. A structural failure stops execution before test. We show the profiles and an internal separation diagnostic. We retain this first model without searching for a better validation/test score.

**Silhouette** compares each record's average distance within its assigned group with its nearest other group. Its range is approximately −1 to 1: larger values indicate clearer separation in the specified scaled feature space. We calculate both methods on the **same records and same transformed inputs**. It is not accuracy and there are no known class labels. KMeans optimizes a related distance objective, so a geometric advantage does not show better commercial outcomes.''')
code(defs('assess','validation_gate')+'''
validation,validation_profiles,validation_metrics,validation_cross=assess(parts['validation'],scaler,model,cluster_names,cuts,frozen,'validation')
gate=validation_gate(validation,scaler,model,frozen)
display(validation_metrics)
display(validation_profiles[['method','group','records','record_share_pct','median_invoices','median_invoice_value_gbp','median_monthly_value_gbp']])
display(gate)
assert gate.passed.all()
parameters_unchanged(scaler,model,frozen)
assert hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()==frozen_fingerprint
print('Validation decision: keep the prespecified first model and reference. No refit or tuning follows.')''')
md('''## 6. Final test comparison on identical records

The settings, preprocessing and reference thresholds are now fixed. Test uses October–November active identified ID-months. We apply the unchanged transform and centers, then report group sizes, original-unit profiles and the reference comparison. Unique IDs within different groups can overlap across months, so **record counts, not sums of per-group unique IDs**, define the partition size.''')
code('''assert gate.passed.all()
test,test_profiles,test_metrics,test_cross=assess(parts['test'],scaler,model,cluster_names,cuts,frozen,'test')
parameters_unchanged(scaler,model,frozen)
assert hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()==frozen_fingerprint
display(test_metrics)
display(test_profiles[['method','group','records','record_share_pct','median_invoices','median_invoice_value_gbp','median_monthly_value_gbp','known_value_share_pct']])
display(test_cross)
assert test_cross.to_numpy().sum()==len(test)
print('Test ID-month records:',len(test),'Distinct active IDs:',test.CustomerID.nunique())
print('All model/reference comparisons use these same records.')''')
md('''### Interpretation of the first model

We describe Profile 1 as smaller-invoice months, Profile 2 as larger single-invoice months and Profile 3 as more frequent purchase months, based on the saved original-unit medians. These are descriptions of observed groups, not known customer types, proof of loyalty or permanent labels. The reference mostly answers how much value was recorded; the model separates frequency from invoice size. The cross-table shows where that distinction changes the description. Monthly value equals frequency times average invoice value for each record; separately calculated group medians need not satisfy that product identity.''')
md('''## 7. W2 follow-up: fixed earlier accounts and unidentified value

For a separate business diagnostic, freeze the top decile of known IDs using December–September purchases only, then follow those same accounts in October and November. Contrast their share with each month's re-ranked top decile. Group sizes differ, so this is a persistence diagnostic rather than a like-for-like model contest. A previously important ID without a purchase in one later month is not proven to have churned.

We also split **all eligible purchase value** into purchases attributed to the current known-ID top group, other identified purchases and unidentified purchases. The last bucket may contain many real people; it is not an artificial customer or a cluster. K10 itself keeps the known-ID denominator. These later historical periods were already exposed in prior EDA and provide no evidence about current 2026 customers.''')
code(defs('concentration_followup')+'''
stability,value_bridge,annual=concentration_followup(data)
display(pd.DataFrame([annual]))
display(stability)
display(value_bridge)
assert np.allclose(value_bridge.iloc[:,1:].sum(axis=1),100)
print('Annual W2 K10 and coverage reproduced; unidentified value remains separate.')''')
code(defs('make_figures')+'''
figure_paths=make_figures(test,test_profiles,stability,value_bridge,OUT)
for path in figure_paths:
    display(Image(filename=str(path)))''')
md('''## 8. Conclusions, limits and next improvement

**What the model adds.** It decomposes purchase activity into frequency and invoice size, enabling a more specific account review than a total-value tier alone. In the held records, the more frequent profile contributes a large fraction of identified value. This supports examining its invoices and account characteristics; it does not identify profitable or loyal accounts or prove that a campaign will work.

**What the later-period diagnostic adds.** The earlier fixed review group continues to contribute substantial identified value, while its active membership and contribution vary. Coverage worsens in November. The separate unidentified bucket prevents treating the known-ID ranking as the whole business.

**Important limits.** Only purchase-active identified records enter clustering. IDs recur and can change profile across months. KMeans imposes three Euclidean groups, the feature choice omits other behaviors, and the historical source has provisional item codes and unverified operational completeness. Both log/scaling choices and repeated monthly participation affect distances. Validation/test periods were seen in earlier EDA. Internal silhouette scores do not measure action effects, future performance or market representativeness.

**Next improvement.** Obtain recent transactions with verified customer linkage, apply the frozen grouping to complete comparable months and review profiles with a commercial stakeholder before considering an intervention. Reliable linking of the unidentified bucket would expand coverage; a campaign's effect would require separate evaluation.''')
md('''## 9. Contributions, AI use and references

**Contribution note:** Moisés provided our project context, source data/previous deliveries, updated course brief and W2 feedback. **Assigned defense preparation:** for our final review, Moisés will check preparation, fitting and validation; Ignacia will check profiles, the reference comparison and business interpretation. These are planned review responsibilities. Both of us will review the interpretation and prepare to explain the whole submitted route.

**AI assistance:** OpenAI Codex assisted with code, notebook/brief/presentation drafts and automated consistency checks. Verification includes input hashing, W2 result reproduction, source/partition conservation, identical comparison records, training-only fit invariance and a complete fresh-kernel run. These are automated checks, not an assertion that a particular student personally performed them. The team remains responsible for reviewing the interpretation and defending each decision. No instructor feedback or completed individual contribution is invented.

**References**
1. Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5BW33. CC BY 4.0. Source/dictionary: https://archive.ics.uci.edu/dataset/352/online-retail.
2. scikit-learn 1.5.2. [KMeans](https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.KMeans.html), [StandardScaler](https://scikit-learn.org/1.5/modules/generated/sklearn.preprocessing.StandardScaler.html), [silhouette_score](https://scikit-learn.org/1.5/modules/generated/sklearn.metrics.silhouette_score.html).
3. Fontecilla, T. (2026). *C2: Train and explain your first model*, updated IIB423T-1 brief supplied by the team. Course notebooks *Class 04: EDA to Supervised/Unsupervised* and *Validation, Leakage and Reproducible Pipelines* informed the method and train-only preparation. Teacher materials are not included in the ZIP.

The following cell exports the same numerical evidence used in the brief and presentation. Generated CSV/JSON/image files are development outputs and are **not** included in the submission ZIP.''')
code('''all_metrics=pd.concat([validation_metrics,test_metrics],ignore_index=True)
tables={'quality':quality,'row_flow':row_flow,'source_partitions':source_partitions,'model_partitions':model_partitions,
        'validation_profiles':validation_profiles,'test_profiles':test_profiles,'metrics':all_metrics,
        'validation_gate':gate,'test_cross':test_cross.reset_index(),'stability':stability,'value_bridge':value_bridge}
for name,table in tables.items():table.to_csv(OUT/f'{name}.csv',index=False)
results={'annual_W2_reproduction':annual,'frozen_model':frozen,'metrics':all_metrics.to_dict(orient='records'),
         'source_partitions':source_partitions.to_dict(orient='records'),'model_partitions':model_partitions.to_dict(orient='records'),
         'test_profiles':test_profiles.to_dict(orient='records'),'test_cross':test_cross.reset_index().to_dict(orient='records'),
         'stability':stability.to_dict(orient='records'),'value_bridge':value_bridge.to_dict(orient='records'),
         'validation_gate':gate.to_dict(orient='records'),'source':source_info,'customer_overlap':overlap_rows}
(OUT/'C2_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+chr(10),encoding='utf-8')
print('Final results exported. Notebook code and saved outputs are the primary executable evidence.')''')
md('''## 10. Individual defense checkpoints

These prompts support preparation; each student should answer independently in their own words. No live AI assistance is allowed in the defense.

1. **What is a modeling row?** An active identified customer-month. A source line is an invoice item entry, and multiple lines/invoices aggregate into that monthly row. The 3,021 test rows represent 2,405 distinct active IDs.
2. **Why frequency and average invoice value?** Their product is monthly value. The two inputs distinguish more invoices from larger invoices without adding a redundant total-value feature. Neither includes future purchases.
3. **What does KMeans learn?** Three centers in the standardized log-feature space. It iteratively assigns each record to the nearest center and updates centers to reduce within-group squared distance. Labels are arbitrary; our profile numbering uses only training medians. Three is a manageable first choice, not a demonstrated optimum.
4. **Why log1p and StandardScaler?** Logarithms reduce large ranges. Standardization puts two different units on a comparable scale. Both affect the meaning of similarity. Only training records determine the means, scales and centers; later transforms do not refit them.
5. **How is the reference fair?** It uses training monthly-value percentiles and assigns every validation/test record with fixed cutoffs. The model and reference compare on identical rows. A later higher-value share of 12.6% is compatible with a training 90th percentile cutoff.
6. **What does silhouette 0.464 mean?** It is the average of (b − a) / max(a, b), where a is a record's mean distance to its own group and b is its nearest other group's mean distance. It describes internal separation in these features. It is not 46.4% accuracy, a probability, external label validation or proof of better actions.
7. **What did the model add?** The 380 higher-value test ID-months split between 124 in Profile 2 and 256 in Profile 3. A similar value tier can contain different frequency/invoice-size patterns. Profile 3 contributes 55.0% of identified test value, with a different denominator from all eligible value.
8. **What remains uncertain?** Missing IDs exclude some value from profiling, recurrent IDs create dependence, KMeans/feature choices impose structure, and the period is historical with prior full-case exposure. An absent purchase is not proven churn. Reviewing accounts and ID capture is supported; profit, loyalty or campaign effects are not established. Recent linked transactions and stakeholder review are the next improvement.
''')

nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12.5'}})
path=HERE/'01_C2_Customer_Profiles.ipynb'
nbf.write(nb,path);print(path)
