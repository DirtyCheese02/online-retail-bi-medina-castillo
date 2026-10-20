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
manifest=json.loads((ROOT/'evidence/artifact_manifest.json').read_text())
check('Generated data and figure SHA-256 hashes match',all(hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in manifest),'artifact_manifest.json')
full=pd.read_csv(ROOT/'data/processed/validated_lines.csv.gz',dtype={'InvoiceNo':'string','CustomerID':'Int64'})
check('No source rows silently lost',len(full)==516384 and full.source_row.is_unique,'validated_lines.csv.gz')
groups=full.row_group.value_counts().to_dict()
check('Row-group conservation',groups=={'priced_purchase':500531,'priced_C_record':8351,'other_retained':7502},'row_flow.csv')
parts={k:pd.read_csv(ROOT/f'data/splits/{k}.csv.gz',dtype={'InvoiceNo':'string'}) for k in ['train','validation','test']}
check('Actual split files partition all source rows',set().union(*(set(p.source_row) for p in parts.values()))==set(full.source_row) and sum(map(len,parts.values()))==len(full),'data/splits/*.csv.gz')
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
features=pd.read_csv(ROOT/'data/processed/invoice_preprocessing.csv')
params=json.loads((ROOT/'evidence/preprocessing_parameters.json').read_text())
train=features.loc[features.split.eq('train'),'log_invoice_value']
check('Fitted mean and scale use train invoices only',len(train)==params['fitted_invoice_count'] and np.isclose(train.mean(),params['mean']) and np.isclose(train.std(ddof=0),params['scale']), 'preprocessing_parameters.json; invoice_preprocessing.csv')
check('Frozen training rule applied to every partition',np.allclose((features.log_invoice_value-params['mean'])/params['scale'],features.scaled_log_value),'invoice_preprocessing.csv')
check('Four or more contextual leakage risks',len(pd.read_csv(ROOT/'data/processed/leakage_audit.csv'))>=4,'leakage_audit.csv')
check('Three or more grounded feedback entries',len(pd.read_csv(ROOT/'data/processed/feedback_to_action.csv'))>=3,'feedback_to_action.csv')
check('Dictionary and quality checks supplied',len(pd.read_csv(ROOT/'data/processed/data_dictionary.csv'))>=8 and len(pd.read_csv(ROOT/'data/processed/quality_checks.csv'))>=8,'data_dictionary.csv; quality_checks.csv')
pdf=ROOT/'report/GROUP_Medina_Castillo_W2_Report.pdf'
reader=PdfReader(pdf);text='\n'.join(page.extract_text() or '' for page in reader.pages)
check('Supplemental PDF readable with all major sections',all(s in text for s in ['Management summary','Process record','Sampling','leakage']),str(pdf.relative_to(ROOT)))
check('No broken font-command text in PDF','ootnotesize' not in text,str(pdf.relative_to(ROOT)))
check('Final C1 presentation snapshot preserved',len(PdfReader(ROOT/'assessments/C1/presentation/GROUP_Medina_Castillo_C1_Slides.pdf').pages)==15,'assessments/C1/presentation/')
check('No tracked candidate exceeds GitHub 100 MiB file limit',all(p.stat().st_size<100*1024**2 for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','.venv','qa'])),'project file sizes')
out={'result':'PASS','checks':checks,'pdf_pages':len(reader.pages),'summary_words':len(summary.split())}
(ROOT/'evidence/verification.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'result':out['result'],'checks':len(checks),'pdf_pages':len(reader.pages),'summary_words':len(summary.split())},indent=2))
