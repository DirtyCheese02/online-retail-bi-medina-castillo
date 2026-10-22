"""Check the evidence contracts that materially affect the W2 submission."""
from pathlib import Path
import hashlib,json,math
import nbformat
import numpy as np
import pandas as pd
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition,evidence):
    assert condition,name
    checks.append({'check':name,'status':'PASS','evidence':evidence})

metrics=json.loads((ROOT/'data/processed/w2_metrics.json').read_text())
b=metrics['baseline']
check('C1 baseline independently regenerated',b['known_customers']==4293 and abs(b['K10_pct']-60.50013933127034)<1e-9 and abs(b['ID_coverage_pct']-85.66276814655409)<1e-9,'w2_metrics.json')
nb=nbformat.read(ROOT/'notebooks/W2_project.ipynb',as_version=4)
code=[c for c in nb.cells if c.cell_type=='code']
check('Notebook execution counts are complete and sequential',[c.execution_count for c in code]==list(range(1,len(code)+1)),'notebooks/W2_project.ipynb')
check('No notebook error outputs',all(o.output_type!='error' for c in code for o in c.outputs),'saved notebook outputs')
check('At least three saved figures',sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)>=3,'saved notebook image outputs')
summary=(ROOT/'evidence/management_summary.txt').read_text()
check('Management summary is 120–180 words',120<=len(summary.split())<=180,'management_summary.txt')
last_output=' '.join(o.get('data',{}).get('text/markdown','') for o in nb.cells[-1].get('outputs',[]))
check('Notebook closes with the management summary',nb.cells[-1].cell_type=='code' and summary.strip() in last_output,'last notebook cell and saved Markdown output')
manifest=json.loads((ROOT/'evidence/artifact_manifest.json').read_text())
check('Generated data and figure SHA-256 hashes match',all(hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in manifest),'artifact_manifest.json')
full=pd.read_csv(ROOT/'data/processed/validated_lines.csv.gz',dtype={'InvoiceNo':'string','CustomerID':'Int64'})
check('No source rows silently lost',len(full)==516384 and full.source_row.is_unique,'validated_lines.csv.gz')
groups=full.row_group.value_counts().to_dict()
check('Row-group conservation',groups=={'priced_purchase':500531,'priced_C_record':8351,'other_retained':7502},'row_flow.csv')
parts={k:pd.read_csv(ROOT/f'data/splits/{k}.csv.gz',dtype={'InvoiceNo':'string'}) for k in ['train','validation','test']}
check('Actual split files partition all source rows',set().union(*(set(p.source_row) for p in parts.values()))==set(full.source_row) and sum(map(len,parts.values()))==len(full),'data/splits/*.csv.gz')
dev_rows=set(full.loc[pd.to_datetime(full.InvoiceDate).lt('2011-10-01'),'source_row'])
hierarchy=pd.read_csv(ROOT/'data/processed/split_hierarchy.csv')
check('Validation is carved entirely from earlier development pool',dev_rows==set(parts['train'].source_row)|set(parts['validation'].source_row) and not(dev_rows&set(parts['test'].source_row)) and int(hierarchy.iloc[0].rows)==len(dev_rows),'split_hierarchy.csv; actual split files')
protocol=json.loads((ROOT/'evidence/protocol.json').read_text())
for key,frame in parts.items():
    dates=pd.to_datetime(frame.InvoiceDate)
    start,end=protocol['split_dates'][key]
    check(f'Chronological bounds: {key}',dates.ge(start).all() and dates.lt(end).all(),'protocol.json; actual split timestamps')
for a,bname in [('train','validation'),('train','test'),('validation','test')]:
    check(f'No row or invoice overlap: {a}/{bname}',not(set(parts[a].source_row)&set(parts[bname].source_row)) and not(set(parts[a].InvoiceNo)&set(parts[bname].InvoiceNo)), 'split_overlap.csv')
sample=pd.read_csv(ROOT/'data/processed/invoice_sample_25pct.csv.gz',dtype={'InvoiceNo':'string'})
counts=full.groupby('InvoiceNo').size().loc[sample.InvoiceNo.unique()].sort_index()
check('Sampling preserves all lines of each selected invoice',counts.equals(sample.groupby('InvoiceNo').size().sort_index()),'invoice_sample_25pct.csv.gz')
check('Sample approximately one quarter of source rows',.20<=len(sample)/len(full)<=.30,'sample_comparison.csv')
strata=pd.read_csv(ROOT/'data/processed/sample_strata.csv')
check('Invoice sample follows fixed monthly quarter counts',all(round(.25*r.available_invoices)==r.sampled_invoices for r in strata.itertuples()),'sample_strata.csv')
# Independently recalculate the nonlinear sample KPI from the saved sampled rows.
p=sample.loc[sample.eligible_purchase].copy()
p['recalculated_value']=p.Quantity*p.UnitPrice
values=p.dropna(subset=['CustomerID']).groupby('CustomerID').recalculated_value.sum().sort_values(ascending=False)
comparison=pd.read_csv(ROOT/'data/processed/sample_comparison.csv').iloc[1]
check('Sample KPI and country proportion match saved sample',np.isclose(100*values.head(math.ceil(.1*len(values))).sum()/values.sum(),comparison.K10_pct) and np.isclose(100*p.loc[p.Country.eq('United Kingdom'),'recalculated_value'].sum()/p.recalculated_value.sum(),comparison.UK_value_share_pct),'actual invoice sample; sample_comparison.csv')
features=pd.read_csv(ROOT/'data/processed/invoice_preprocessing.csv')
params=json.loads((ROOT/'evidence/preprocessing_parameters.json').read_text())
train=features.loc[features.split.eq('train'),'log_invoice_value']
check('Fitted mean and scale use train invoices only',len(train)==params['fitted_invoice_count'] and np.isclose(train.mean(),params['mean']) and np.isclose(train.std(ddof=0),params['scale']), 'preprocessing_parameters.json; invoice_preprocessing.csv')
check('Frozen training rule applied to every partition',np.allclose((features.log_invoice_value-params['mean'])/params['scale'],features.scaled_log_value),'invoice_preprocessing.csv')
execution=pd.read_csv(ROOT/'data/processed/validation_execution.csv')
check('Ordered validation gate before test with no refit',execution.step.tolist()==[1,2,3] and execution.partition.tolist()==['train','validation','test'] and execution.passed.all() and execution.fitted_count.eq(params['fitted_invoice_count']).all(),'validation_execution.csv; preprocess execution order')
held=pd.read_csv(ROOT/'data/processed/holdout_robustness.csv')
monthly=pd.read_csv(ROOT/'data/processed/holdout_monthly_kpi.csv')
check('Holdout compares monthly shares with explicit denominators',monthly.groupby('split').size().to_dict()=={'train':8,'validation':2,'test':2} and np.allclose(held.set_index('split').mean_monthly_K10_pct.sort_index(),monthly.groupby('split').K10_pct.mean().sort_index()) and monthly.known_customers.gt(0).all(),'holdout_monthly_kpi.csv; holdout_robustness.csv')
check('Four or more contextual leakage risks',len(pd.read_csv(ROOT/'data/processed/leakage_audit.csv'))>=4,'leakage_audit.csv')
check('Three or more grounded feedback entries',len(pd.read_csv(ROOT/'data/processed/feedback_to_action.csv'))>=3,'feedback_to_action.csv')
check('Dictionary and quality checks supplied',len(pd.read_csv(ROOT/'data/processed/data_dictionary.csv'))>=8 and len(pd.read_csv(ROOT/'data/processed/quality_checks.csv'))>=8,'data_dictionary.csv; quality_checks.csv')
pdf=ROOT/'report/GROUP_Medina_Castillo_W2_Report.pdf'
reader=PdfReader(pdf);text='\n'.join(page.extract_text() or '' for page in reader.pages)
check('Supplemental PDF readable with all major sections',all(s in text for s in ['Management summary','Process record','Sampling','leakage']),str(pdf.relative_to(ROOT)))
check('No broken font-command text in PDF','ootnotesize' not in text,str(pdf.relative_to(ROOT)))
check('PDF reports regenerated descriptive holdout findings',all(f'{x:.2f}%' in text for x in held.mean_monthly_K10_pct),'report PDF; holdout_robustness.csv')
check('Final C1 presentation snapshot preserved',len(PdfReader(ROOT/'assessments/C1/presentation/GROUP_Medina_Castillo_C1_Slides.pdf').pages)==15,'assessments/C1/presentation/')
check('No tracked candidate exceeds GitHub 100 MiB file limit',all(p.stat().st_size<100*1024**2 for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','.venv','qa'])),'project file sizes')
out={'result':'PASS','checks':checks,'pdf_pages':len(reader.pages),'summary_words':len(summary.split())}
(ROOT/'evidence/verification.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'result':out['result'],'checks':len(checks),'pdf_pages':len(reader.pages),'summary_words':len(summary.split())},indent=2))
