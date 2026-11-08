"""C2 clustering analysis. These functions are embedded in full in the submitted notebook."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import math
import urllib.request

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from threadpoolctl import threadpool_limits

SEED = 4232026
RAW_SHA = '8f6d42748e36cf41008f411307fe77e03b2001d25eb445dcfab5aa70186fdb4f'
RAW_URL = ('https://raw.githubusercontent.com/DirtyCheese02/online-retail-bi-medina-castillo/'
           'e19b529d84144f2089d43fceede8aba73e2fc315/data/raw/online_retail_2010dec_2011nov_input.csv')
FEATURES = ['invoices', 'mean_invoice_value_gbp']
SPLITS = {'train': ('2010-12-01', '2011-08-01'),
          'validation': ('2011-08-01', '2011-10-01'),
          'test': ('2011-10-01', '2011-12-01')}


def load_source(force_download=False):
    candidates = [p / 'data/raw/online_retail_2010dec_2011nov_input.csv'
                  for p in [Path.cwd(), *Path.cwd().parents]]
    local = next((p for p in candidates if p.is_file()), None)
    if local is not None and not force_download:
        payload = local.read_bytes(); origin = 'Preserved local W2 extract'
    else:
        with urllib.request.urlopen(RAW_URL, timeout=60) as response:
            payload = response.read()
        origin = 'Pinned public W2 extract downloaded; no dataset included in ZIP'
    assert hashlib.sha256(payload).hexdigest() == RAW_SHA
    raw = pd.read_csv(BytesIO(payload), dtype={'InvoiceNo': 'string', 'StockCode': 'string',
            'CustomerID': 'Int64', 'Description': 'string', 'Country': 'string'}, parse_dates=['InvoiceDate'])
    assert len(raw) == 516384 and len(raw.columns) == 8
    d = raw.copy(); d.insert(0, 'source_row', np.arange(1, len(d) + 1))
    d['month'] = d.InvoiceDate.dt.strftime('%Y-%m')
    d['c_record'] = d.InvoiceNo.str.startswith('C')
    d['merchandise'] = d.StockCode.str.fullmatch('[0-9]{5}[A-Z]?')
    d['eligible'] = d.merchandise & ~d.c_record & d.Quantity.gt(0) & d.UnitPrice.gt(0)
    d['eligible_c'] = d.merchandise & d.c_record & d.Quantity.lt(0) & d.UnitPrice.gt(0)
    d['row_group'] = np.select([d.eligible, d.eligible_c], ['purchase', 'C_record'], default='other_retained')
    d['value_gbp'] = np.where(d.eligible, d.Quantity * d.UnitPrice, np.nan)
    d['split'] = ''
    for name, (start, end) in SPLITS.items():
        d.loc[d.InvoiceDate.ge(start) & d.InvoiceDate.lt(end), 'split'] = name
    return d, {'origin': origin, 'input_sha256': RAW_SHA, 'source_rows': len(raw), 'source_columns': 8}


def check_preparation(d):
    checks = []
    def record(name, n, treatment, structural=False):
        if structural: assert n == 0, name
        checks.append({'check': name, 'affected': int(n), 'status': 'PASS' if n == 0 else 'FLAG', 'treatment': treatment})
    record('Missing/outside-window timestamps', (d.InvoiceDate.isna() | d.split.eq('')).sum(), 'Stop on invalid partition date', True)
    record('Missing invoice/item keys', (d.InvoiceNo.isna() | d.StockCode.isna()).sum(), 'Stop; grouping requires keys', True)
    record('Missing customer IDs', d.CustomerID.isna().sum(), 'Keep eligible value; exclude both customer grouping methods')
    record('Nonpositive prices', d.UnitPrice.le(0).sum(), 'Keep source; exclude purchase measure; no imputation')
    record('Negative quantity without C', (d.Quantity.lt(0) & ~d.c_record).sum(), 'Keep outside purchase and eligible cancellation measures')
    record('Outside provisional item pattern', (~d.merchandise).sum(), 'Keep source; exclude scoped measure; pattern is not verified category')
    record('Missing descriptions', d.Description.isna().sum(), 'Do not remove solely for description; use StockCode')
    original = ['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
    record('Exact repeats beyond first copy', d.duplicated(original).sum(), 'Retain W2 baseline; no unique line ID proves error')
    record('Invoices crossing partitions', d.groupby('InvoiceNo').split.nunique().gt(1).sum(), 'Stop to avoid sibling-line leakage', True)
    record('Known IDs shared within one eligible invoice', d.loc[d.eligible].groupby('InvoiceNo').CustomerID.nunique().gt(1).sum(), 'Stop before customer aggregate', True)
    record('Source-row loss or repeated source position', int(len(d) != 516384 or not d.source_row.is_unique), 'Conserve every original row', True)
    assert int(d.eligible.sum()) == 500531 and int(d.eligible_c.sum()) == 8351
    counts = d.row_group.value_counts().rename_axis('group').reset_index(name='source_rows')
    summary = d.groupby('split', sort=False).agg(source_rows=('source_row','size'), invoices=('InvoiceNo','nunique'), known_ids_raw=('CustomerID','nunique'))
    summary = summary.reindex(['train','validation','test']).reset_index()
    assert summary.source_rows.tolist() == [285421,85510,145453]
    return pd.DataFrame(checks), counts, summary


def monthly_records(d):
    p = d.loc[d.eligible & d.CustomerID.notna()].copy()
    invoice = p.groupby(['split','month','CustomerID','InvoiceNo'], observed=True).agg(
        invoice_value_gbp=('value_gbp','sum'), first=('InvoiceDate','min'), last=('InvoiceDate','max')).reset_index()
    m = invoice.groupby(['split','month','CustomerID'], observed=True).agg(
        invoices=('InvoiceNo','nunique'), monthly_value_gbp=('invoice_value_gbp','sum'),
        first_invoice=('first','min'), last_invoice=('last','max')).reset_index()
    m['mean_invoice_value_gbp'] = m.monthly_value_gbp / m.invoices
    assert not m.duplicated(['month','CustomerID']).any()
    assert m[FEATURES].gt(0).all().all() and np.isfinite(m[FEATURES].to_numpy()).all()
    assert np.allclose(m.monthly_value_gbp, m.invoices * m.mean_invoice_value_gbp)
    parts = {name: m.loc[m.split.eq(name)].copy().reset_index(drop=True) for name in SPLITS}
    for name, (start,end) in SPLITS.items():
        assert parts[name].first_invoice.ge(start).all() and parts[name].last_invoice.lt(end).all()
    return m, parts


def fit_first_model(training):
    xlog = np.log1p(training[FEATURES].to_numpy(dtype=float))
    scaler = StandardScaler().fit(xlog)
    with threadpool_limits(limits=1):
        model = KMeans(n_clusters=3, n_init=20, max_iter=300, random_state=SEED, algorithm='lloyd').fit(scaler.transform(xlog))
    # Name only by training profiles, so a test result cannot choose label order.
    labelled = training.assign(raw_cluster=model.labels_)
    order = labelled.groupby('raw_cluster').monthly_value_gbp.median().sort_values().index.tolist()
    names = {int(raw): f'Profile {i+1}' for i,raw in enumerate(order)}
    cuts = np.quantile(training.monthly_value_gbp, [.5,.9])
    assert cuts[0] < cuts[1]
    frozen = {'feature_names': FEATURES, 'k':3, 'n_init':20, 'max_iter':300, 'seed':SEED,
              'fit_records':len(training), 'fit_months':sorted(training.month.unique().tolist()),
              'scaler_mean':scaler.mean_.tolist(), 'scaler_scale':scaler.scale_.tolist(),
              'cluster_centers':model.cluster_centers_.tolist(), 'cluster_names':names,
              'reference_p50_gbp':float(cuts[0]), 'reference_p90_gbp':float(cuts[1]),
              'test_used_for_model_choice':False, 'prior_full_case_exposure':True}
    return scaler, model, names, cuts, frozen


def parameters_unchanged(scaler, model, frozen):
    assert int(scaler.n_samples_seen_) == frozen['fit_records']
    assert np.array_equal(scaler.mean_, frozen['scaler_mean'])
    assert np.array_equal(scaler.scale_, frozen['scaler_scale'])
    assert np.array_equal(model.cluster_centers_, frozen['cluster_centers'])


def assess(frame, scaler, model, names, cuts, frozen, partition):
    x = scaler.transform(np.log1p(frame[FEATURES].to_numpy(dtype=float)))
    parameters_unchanged(scaler,model,frozen)
    with threadpool_limits(limits=1):
        labels = model.predict(x)
    grouped = frame.copy()
    grouped['cluster'] = [names[int(i)] for i in labels]
    grouped['reference'] = np.select([frame.monthly_value_gbp.le(cuts[0]), frame.monthly_value_gbp.le(cuts[1])],
                                     ['Lower value','Middle value'], default='Higher value')
    assert len(grouped) == len(frame) and not grouped[['cluster','reference']].isna().any().any()
    def profiles(col):
        g = grouped.groupby(col).agg(records=('CustomerID','size'), unique_ids=('CustomerID','nunique'),
            median_invoices=('invoices','median'), median_invoice_value_gbp=('mean_invoice_value_gbp','median'),
            median_monthly_value_gbp=('monthly_value_gbp','median'), eligible_value_gbp=('monthly_value_gbp','sum')).reset_index()
        g['record_share_pct'] = 100*g.records/len(frame)
        g['known_value_share_pct'] = 100*g.eligible_value_gbp/g.eligible_value_gbp.sum()
        g.insert(0,'partition',partition); g.insert(1,'method','KMeans' if col=='cluster' else 'Value rule')
        return g.rename(columns={col:'group'})
    metric_rows=[]
    for method,col in [('KMeans','cluster'),('Value rule','reference')]:
        with threadpool_limits(limits=1):
            score = float(silhouette_score(x,grouped[col])) if grouped[col].nunique()>1 else float('nan')
        metric_rows.append({'partition':partition,'method':method,'records':len(frame),'silhouette':score,
                            'populated_groups':grouped[col].nunique()})
    comparison = pd.crosstab(grouped.cluster,grouped.reference).reindex(
        index=['Profile 1','Profile 2','Profile 3'],columns=['Lower value','Middle value','Higher value'],fill_value=0)
    parameters_unchanged(scaler,model,frozen)
    return grouped, pd.concat([profiles('cluster'),profiles('reference')],ignore_index=True), pd.DataFrame(metric_rows), comparison


def validation_gate(validation_grouped, scaler, model, frozen):
    checks = {'finite_positive_features': bool(np.isfinite(validation_grouped[FEATURES]).all().all() and validation_grouped[FEATURES].gt(0).all().all()),
              'exactly_three_profiles_assigned': validation_grouped.cluster.nunique()==3,
              'all_records_have_both_groups': not validation_grouped[['cluster','reference']].isna().any().any(),
              'no_test_months_in_fit': max(frozen['fit_months']) < '2011-08',
              'validation_months_only': set(validation_grouped.month)=={'2011-08','2011-09'}}
    parameters_unchanged(scaler,model,frozen)
    checks['learned_parameters_unchanged'] = True
    assert all(checks.values()), checks
    return pd.DataFrame([{'validation_check':name,'passed':bool(value)} for name,value in checks.items()])


def concentration_followup(d):
    p = d.loc[d.eligible].copy()
    identified = p.dropna(subset=['CustomerID'])
    prior = identified.loc[identified.InvoiceDate.lt('2011-10-01')].groupby('CustomerID').value_gbp.sum().sort_values(ascending=False)
    frozen_ids = set(prior.head(math.ceil(.1*len(prior))).index)
    rows=[]; bridges=[]
    for month in ['2011-10','2011-11']:
        all_month = p.loc[p.month.eq(month)]
        known = all_month.dropna(subset=['CustomerID']).groupby('CustomerID').value_gbp.sum().sort_values(ascending=False)
        current_top = known.head(math.ceil(.1*len(known)))
        all_value=float(all_month.value_gbp.sum()); known_value=float(known.sum())
        frozen_value=float(known.loc[known.index.isin(frozen_ids)].sum())
        rows.append({'month':month,'active_known_ids':len(known),'reference_ids':len(prior),
            'frozen_review_ids':len(frozen_ids),'frozen_ids_active':int(known.index.isin(frozen_ids).sum()),
            'reranked_K10_pct':100*float(current_top.sum())/known_value,
            'frozen_group_known_value_pct':100*frozen_value/known_value,
            'frozen_group_all_value_pct':100*frozen_value/all_value,
            'ID_coverage_pct':100*known_value/all_value})
        bridges.append({'month':month,'Known top-decile purchases':100*float(current_top.sum())/all_value,
                        'Other identified purchases':100*(known_value-float(current_top.sum()))/all_value,
                        'Unidentified purchases':100*(all_value-known_value)/all_value})
    bridge=pd.DataFrame(bridges)
    assert np.allclose(bridge.iloc[:,1:].sum(axis=1),100)
    all_known=identified.groupby('CustomerID').value_gbp.sum().sort_values(ascending=False)
    annual={'known_ids':len(all_known),'K10_pct':100*all_known.head(math.ceil(.1*len(all_known))).sum()/all_known.sum(),
            'ID_coverage_pct':100*all_known.sum()/p.value_gbp.sum()}
    assert len(all_known)==4293 and np.isclose(annual['K10_pct'],60.50013933127034)
    return pd.DataFrame(rows),bridge,annual


def make_figures(test, profiles, stability, bridge, output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':170})
    palette={'Profile 1':'#087F85','Profile 2':'#ED8957','Profile 3':'#173E56',
             'Lower value':'#90C5BD','Middle value':'#39718A','Higher value':'#ED8957'}
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),sharex=True,sharey=True)
    for ax,col,title in zip(axes,['reference','cluster'],['Reference: training value cutoffs','KMeans: frozen training profiles']):
        for group,g in test.groupby(col):
            ax.scatter(g.invoices,g.mean_invoice_value_gbp,s=13,alpha=.35,label=group,color=palette[group])
        ax.set(xscale='log',yscale='log',xlabel='Eligible invoices per active ID-month',title=title)
        ax.legend(fontsize=8);ax.grid(alpha=.15)
    axes[0].set_ylabel('Mean eligible invoice value (GBP; log scale)')
    fig.tight_layout();fig.savefig(output/'reference_vs_profiles.png',bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.3))
    g=profiles.loc[profiles.method.eq('KMeans')]
    axes[0].bar(g['group'],g.records,color=[palette[x] for x in g['group']])
    for i,v in enumerate(g.records):axes[0].text(i,v+15,str(v),ha='center')
    axes[0].set(ylabel='Active customer-month records',title='Test profile sizes')
    axes[1].plot(stability.month,stability.frozen_group_known_value_pct,marker='o',label='Earlier fixed review group',color='#173E56')
    axes[1].plot(stability.month,stability.reranked_K10_pct,marker='o',label='Monthly re-ranked top 10%',color='#087F85')
    axes[1].set(ylim=(0,100),ylabel='Share of identified value (%)',title='Later historical account contribution')
    axes[1].legend(fontsize=8);fig.tight_layout();fig.savefig(output/'sizes_and_stability.png',bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,2.7));bottom=np.zeros(len(bridge))
    for column,color in zip(bridge.columns[1:],['#087F85','#173E56','#ED8957']):
        vals=bridge[column].to_numpy();ax.barh(bridge.month,vals,left=bottom,color=color,label=column)
        for i,(v,left) in enumerate(zip(vals,bottom)):ax.text(left+v/2,i,f'{v:.1f}%',ha='center',va='center',color='white',fontsize=10)
        bottom+=vals
    ax.set(xlim=(0,100),xlabel='All eligible positive purchase value (%)');ax.legend(loc='upper center',bbox_to_anchor=(.5,-.25),ncol=1,fontsize=9)
    fig.tight_layout();fig.savefig(output/'identified_and_unidentified_value.png',bbox_inches='tight');plt.close(fig)
    return [output/name for name in ['reference_vs_profiles.png','sizes_and_stability.png','identified_and_unidentified_value.png']]


def run_analysis(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    d,source=load_source();quality,flow,counts=check_preparation(d);monthly,parts=monthly_records(d)
    scaler,model,names,cuts,frozen=fit_first_model(parts['train'])
    train,train_profiles,_,_=assess(parts['train'],scaler,model,names,cuts,frozen,'train')
    val,val_profiles,val_metrics,val_cross=assess(parts['validation'],scaler,model,names,cuts,frozen,'validation')
    gate=validation_gate(val,scaler,model,frozen)
    # Test is assigned and scored only after the fixed validation gate passes.
    test,test_profiles,test_metrics,test_cross=assess(parts['test'],scaler,model,names,cuts,frozen,'test')
    stability,bridge,annual=concentration_followup(d)
    metrics=pd.concat([val_metrics,test_metrics],ignore_index=True)
    tables={'quality':quality,'row_flow':flow,'source_partitions':counts,'monthly_records':monthly,
            'train_profiles':train_profiles,'validation_profiles':val_profiles,'test_profiles':test_profiles,
            'metrics':metrics,'validation_gate':gate,'test_cross':test_cross.reset_index(),
            'stability':stability,'value_bridge':bridge}
    for name,frame in tables.items():frame.to_csv(output/f'{name}.csv',index=False)
    split_summary=pd.DataFrame([{'split':k,'monthly_records':len(v),'unique_active_ids':v.CustomerID.nunique(),
                'months':v.month.nunique()} for k,v in parts.items()])
    split_summary.to_csv(output/'model_partitions.csv',index=False)
    overlap=[]
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        overlap.append({'left':a,'right':b,'shared_customer_ids':len(set(parts[a].CustomerID)&set(parts[b].CustomerID)),
                        'shared_id_month_keys':len(set(zip(parts[a].month,parts[a].CustomerID))&set(zip(parts[b].month,parts[b].CustomerID)))})
    pd.DataFrame(overlap).to_csv(output/'customer_overlap.csv',index=False)
    images=make_figures(test,test_profiles,stability,bridge,output)
    result={'source':source,'annual_W2_reproduction':annual,'frozen_model':frozen,
            'source_partitions':counts.to_dict(orient='records'),'model_partitions':split_summary.to_dict(orient='records'),
            'metrics':metrics.to_dict(orient='records'),'test_profiles':test_profiles.to_dict(orient='records'),
            'test_cross':test_cross.reset_index().to_dict(orient='records'),'stability':stability.to_dict(orient='records'),
            'value_bridge':bridge.to_dict(orient='records'),'validation_gate':gate.to_dict(orient='records'),
            'customer_overlap':overlap,'figures':[p.name for p in images]}
    (output/'C2_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result,tables


if __name__=='__main__':
    result,_=run_analysis(Path(__file__).resolve().parent/'outputs')
    print(json.dumps(result,indent=2,ensure_ascii=False))
