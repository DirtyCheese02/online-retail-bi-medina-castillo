"""Prepare chart literals from the unchanged C2 results; no model is retrained."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
R=json.loads((HERE.parent/'outputs/C2_results.json').read_text(encoding='utf-8'))
m=pd.read_csv(HERE.parent/'outputs/monthly_records.csv')
t=m.loc[m.split.eq('test')].copy()
f=R['frozen_model']
z=(np.log1p(t[f['feature_names']].to_numpy())-np.array(f['scaler_mean']))/np.array(f['scaler_scale'])
centers=np.array(f['cluster_centers'])
labels=np.argmin(((z[:,None,:]-centers[None,:,:])**2).sum(axis=2),axis=1)
t['cluster']=[f['cluster_names'][str(int(i))] for i in labels]
t['reference']=np.select([t.monthly_value_gbp.le(f['reference_p50_gbp']),t.monthly_value_gbp.le(f['reference_p90_gbp'])],['Lower value','Middle value'],default='Higher value')
actual=t.cluster.value_counts().to_dict()
assert actual=={r['group']:r['records'] for r in R['test_profiles'] if r['method']=='KMeans'}
cross=pd.crosstab(t.cluster,t.reference).reindex(index=['Profile 1','Profile 2','Profile 3'],columns=['Lower value','Middle value','Higher value'],fill_value=0)
assert cross.reset_index().to_dict(orient='records')==R['test_cross']
scatter={}
for column,groups in [('reference',['Lower value','Middle value','Higher value']),('cluster',['Profile 1','Profile 2','Profile 3'])]:
    scatter[column]=[{'name':g,'x':np.round(z[t[column].eq(g),0],6).tolist(),'y':np.round(z[t[column].eq(g),1],6).tolist()} for g in groups]
composition=[]
for group in cross.index:
    composition.append({'name':group,'values':np.round(cross.loc[group].to_numpy()/cross.sum(axis=0).to_numpy(),10).tolist()})
data={'results':R,'scatter':scatter,'reference_composition':composition,
      'scatter_bounds':{'xmin':float(np.floor(z[:,0].min())),'xmax':float(np.ceil(z[:,0].max())),
                        'ymin':float(np.floor(z[:,1].min())),'ymax':float(np.ceil(z[:,1].max()))},
      'reference_tier_counts':cross.sum(axis=0).to_dict(),
      'model_record_count':sum(r['active_ID_months'] for r in R['model_partitions']),
      'test_record_count':len(t),'rounding':'Scatter coordinates: 6 decimals; percentage fractions: 10 decimals for Excel portability'}
(HERE/'visual_data.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Unchanged held records:',len(t),'Native scatter points:',sum(len(x['x']) for x in scatter['cluster']))
print('Bounds:',data['scatter_bounds'])
