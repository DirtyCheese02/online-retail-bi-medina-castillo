"""Audit C2 delivery and cross-artifact numerical evidence without awarding a grade."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,math,re
import unicodedata
import xml.etree.ElementTree as E
import numpy as np
import pandas as pd
import nbformat
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
OUT=HERE/'outputs';DELIVERY=HERE/'delivery'
R=json.loads((OUT/'C2_results.json').read_text(encoding='utf-8'))
checks=[]
def check(label,condition):
    assert condition,label
    checks.append({'check':label,'result':'PASS'})
nb=nbformat.read(DELIVERY/'01_C2_Customer_Profiles.ipynb',4)
codes=[c for c in nb.cells if c.cell_type=='code']
code='\n'.join(c.source for c in codes);text='\n'.join(c.source for c in nb.cells if c.cell_type=='markdown')
check('All notebook code cells executed sequentially',[c.execution_count for c in codes]==list(range(1,len(codes)+1)))
check('No notebook execution error',not any(o.output_type=='error' for c in codes for o in c.outputs))
check('Code and outputs include all project logic inline',all(f'def {n}(' in code for n in ['load_source','check_preparation','monthly_records','fit_first_model','assess','validation_gate','concentration_followup']) and not re.search(r'from (c2_analysis|w2_analysis|feedback_delivery) import',code))
check('At least three saved plot outputs',sum('image/png' in o.get('data',{}) for c in codes for o in c.outputs)>=3)
check('Group, source, contribution and AI notes present',all(x in text for x in ['Moisés Medina','Ignacia Castillo','UCI Online Retail','Assigned defense preparation','AI assistance']))
check('Descriptive clustering route and no accuracy claim','Route: descriptive clustering' in text and 'not accuracy' in text)
check('Unchanged W2 baseline reproduced',R['annual_W2_reproduction']['known_ids']==4293 and np.isclose(R['annual_W2_reproduction']['K10_pct'],60.50013933127034))
check('W2 source split counts retained',[x['source_rows'] for x in R['source_partitions']]==[285421,85510,145453])
check('Active ID-month partition counts explicit',[x['active_ID_months'] for x in R['model_partitions']]==[7195,2192,3021])
check('One frozen training-only model',R['frozen_model']['fit_records']==7195 and R['frozen_model']['k']==3 and R['frozen_model']['seed']==4232026 and not R['frozen_model']['test_used_for_model_choice'])
check('Validation gate completed before test',all(x['passed'] for x in R['validation_gate']) and code.index('gate=validation_gate(')<code.index("test,test_profiles,test_metrics,test_cross=assess("))
check('ID-month keys do not overlap',all(x['shared_ID_months']==0 for x in R['customer_overlap']))
m=pd.DataFrame(R['metrics'])
check('Both methods compare on identical held record counts',m.groupby('partition').records.nunique().eq(1).all() and m.groupby('partition').method.nunique().eq(2).all())
check('All three profiles populated and record counts conserved',all(m.populated_groups.eq(3)) and sum(x['records'] for x in R['test_profiles'] if x['method']=='KMeans')==3021)
cross=pd.DataFrame(R['test_cross'])
check('Reference cross-table conserves all 3021 records',int(cross.iloc[:,1:].to_numpy().sum())==3021)
bridge=pd.DataFrame(R['value_bridge'])
check('Unidentified category conserves all eligible value',np.allclose(bridge.iloc[:,1:].sum(axis=1),100) and np.isclose(bridge.iloc[1]['Unidentified purchases'],21.44882712054614))
check('W2 fixed earlier group followed in later months',all(x['frozen_review_ids']==362 for x in R['stability']) and [x['frozen_ids_active'] for x in R['stability']]==[218,265])
reader=PdfReader(DELIVERY/'GROUP_Medina_Castillo_C2_Brief.pdf');pdftext='\n'.join(p.extract_text() or '' for p in reader.pages)
check('PDF brief at most three pages including references',len(reader.pages)<=3 and 'References and submitted evidence' in pdftext)
check('Brief contains actual held comparison metrics',all(f'{v:.3f}' in pdftext for v in m.silhouette))
check('Brief includes group sizes and missing-ID limit',all(str(v) in pdftext.replace(',','') for v in [3021,2405,864,1352,805]) and '21.45%' in pdftext)
plain_pdf=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',pdftext))
check('Brief clearly distinguishes grouping from prediction','This is grouping, not a forecast' in plain_pdf and 'not classification accuracy' in plain_pdf)
check('Notebook and brief state a scoped model verdict','Model verdict: retain this first model for descriptive profiling' in text and 'Model verdict.' in plain_pdf and 'commercial usefulness remains unvalidated' in plain_pdf)
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with ZipFile(DELIVERY/'GROUP_Medina_Castillo_C2_Presentation.pptx') as z:
    slidefiles=[p for p in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',p)]
    notes=[p for p in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',p)]
    check('Presentation has 14 slides and 14 speaking-note parts',len(slidefiles)==14 and len(notes)==14)
    slides={int(re.search(r'slide(\d+)',p).group(1)):E.fromstring(z.read(p)) for p in slidefiles}
    recap=' '.join(t.text or '' for t in slides[2].findall('.//a:t',ns))
    check('Opening C1 recap states method, scoped findings and conclusion',all(x in recap for x in ['C1 recap','audited UCI Online Retail','60.5%','85.7%','14.3%','430 of 4,293','Review major accounts and improve ID capture together','C2 explores']))
    check('Backup slide has an editable exact cross-table',slides[14].find('.//a:tbl',ns) is not None)
    charts=[p for p in z.namelist() if re.search(r'/charts/chart\d+\.xml$',p)]
    check('Ten native charts have ten embedded data workbooks',len(charts)==10 and len([p for p in z.namelist() if p.endswith('.xlsx') and 'embeddings/' in p])==10)
    for n,count in {5:1,7:1,8:2,9:3,10:1,11:1,12:1}.items():
        check(f'Slide {n} has the expected editable charts',len(slides[n].findall('.//c:chart',ns))==count)
    profiles=[x for x in R['test_profiles'] if x['method']=='KMeans']
    vc=m.loc[m.partition.eq('validation')].set_index('method')
    # Recompute coordinates/assignments from saved monthly records and frozen training
    # parameters independently of the presentation manifest. No model is refitted.
    held=pd.read_csv(OUT/'monthly_records.csv').query("split == 'test'").copy()
    frozen=R['frozen_model']
    xy=(np.log1p(held[frozen['feature_names']].to_numpy())-frozen['scaler_mean'])/frozen['scaler_scale']
    centers=np.array(frozen['cluster_centers'])
    nearest=np.argmin(((xy[:,None,:]-centers[None,:,:])**2).sum(axis=2),axis=1)
    held['cluster']=[frozen['cluster_names'][str(int(i))] for i in nearest]
    held['reference']=np.select([held.monthly_value_gbp.le(frozen['reference_p50_gbp']),held.monthly_value_gbp.le(frozen['reference_p90_gbp'])],['Lower value','Middle value'],default='Higher value')
    expected_scatter={}
    for index,column,groups in [(2,'reference',['Lower value','Middle value','Higher value']),(3,'cluster',['Profile 1','Profile 2','Profile 3'])]:
        expected_scatter[index]=[(xy[held[column].eq(g),0],xy[held[column].eq(g),1]) for g in groups]
    counts=cross.iloc[:,1:].to_numpy()
    expected={0:[[3021,2192,7195]],1:[[vc.loc['KMeans','silhouette'],vc.loc['Value rule','silhouette']]],
              4:[[x['records'] for x in profiles]],5:[[x['median_invoices'] for x in profiles]],
              6:[[x['median_invoice_value_gbp'] for x in profiles]],7:(counts/counts.sum(axis=0)).tolist(),
              8:[[x['frozen_group_known_value_pct']/100 for x in R['stability']],[x['reranked_K10_pct']/100 for x in R['stability']]],
              9:[[x[col]/100 for x in reversed(R['value_bridge'])] for col in ['Known top-decile purchases','Other identified purchases','Unidentified purchases']]}
    for i,p in enumerate(sorted(charts,key=lambda p:int(re.search(r'chart(\d+)\.xml',p).group(1)))):
        chart=E.fromstring(z.read(p))
        series=chart.findall('.//c:ser',ns)
        if i in expected_scatter:
            point_count=0
            for s,(xs,ys) in zip(series,expected_scatter[i],strict=True):
                actualx=[float(v.text) for v in s.findall('.//c:xVal//c:numCache/c:pt/c:v',ns)]
                actualy=[float(v.text) for v in s.findall('.//c:yVal//c:numCache/c:pt/c:v',ns)]
                check(f'Native scatter {i+1} preserves a complete frozen group',np.allclose(actualx,xs,atol=5.01e-7,rtol=0) and np.allclose(actualy,ys,atol=5.01e-7,rtol=0))
                point_count+=len(actualx)
            check(f'Native scatter {i+1} includes all 3021 held records',point_count==3021)
        else:
            values=[[float(v.text) for v in s.findall('.//c:val//c:numCache/c:pt/c:v',ns)] for s in series]
            check(f'Native chart {i+1} agrees with notebook values',np.allclose(values,expected[i],atol=.00501 if i==6 else 1e-9,rtol=0))
    table=slides[14].find('.//a:tbl',ns)
    actualcounts=[[int(''.join(t.text or '' for t in cell.findall('.//a:t',ns)).replace(',','')) for cell in row.findall('a:tc',ns)[1:]] for row in table.findall('a:tr',ns)[1:]]
    check('Presentation backup preserves all exact reference counts',np.array_equal(actualcounts,counts) and sum(map(sum,actualcounts))==3021)
    slide9=' '.join(t.text or '' for t in slides[10].findall('.//a:t',ns))
    check('Presentation test metrics agree with notebook','0.464' in slide9 and '0.289' in slide9 and '380' in slide9)
    verdict=re.sub(r'\s+',' ',' '.join(t.text or '' for t in slides[13].findall('.//a:t',ns)))
    check('Presentation distinguishes descriptive result from business validation','Keep the model for describing purchase patterns.' in verdict and 'Commercial usefulness still needs validation.' in verdict and all(x in verdict for x in ['0.472','0.464','0.289']))
with ZipFile(DELIVERY/'GROUP_Medina_Castillo_C2.zip') as z:
    expectednames={'01_C2_Customer_Profiles.ipynb','GROUP_Medina_Castillo_C2_Brief.pdf','GROUP_Medina_Castillo_C2_Presentation.pptx'}
    check('ZIP contains only the three permitted deliverables',set(z.namelist())==expectednames and z.testzip() is None)
    check('ZIP bytes match the verified individual files',all(z.read(n)==(DELIVERY/n).read_bytes() for n in expectednames))
check('Contributions distinguish documented inputs from planned reviews','planned review responsibilities' in text and 'Moisés will check' in text and 'Ignacia will check' in text)
latex=json.loads((HERE/'qa/latex_export.json').read_text(encoding='utf-8-sig'))
check('LaTeX export succeeded without overflowing content',latex['exitCode']==0 and 'Overfull' not in latex['log'])
record={'status':'PASS','checks':checks,'check_count':len(checks),'notebook_code_cells':len(codes),'brief_pages':len(reader.pages),
        'route':'clustering','grade_awarded':None,'Canvas_receipt':'Not verified; user upload required',
        'individual_defense':'Prepared questions/notes, not a verified oral performance'}
(OUT/'C2_verification.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print(json.dumps({k:v for k,v in record.items() if k!='checks'},indent=2))
