"""Workshop 2: auditable descriptive validation, sampling, and temporal holdout.

All numerical outputs are regenerated from the preserved case input. No model is fit.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/online_retail_2010dec_2011nov_input.csv'
OUT = ROOT / 'data/processed'
FIG = ROOT / 'analysis/figures'
SEED = 4232026
COLS = ['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
SPLITS = {'train': ('2010-12-01','2011-08-01'),
          'validation': ('2011-08-01','2011-10-01'),
          'test': ('2011-10-01','2011-12-01')}
PROTOCOL = {
    'recorded_on':'2026-10-20', 'seed':SEED, 'case_start':'2010-12-01',
    'case_end_exclusive':'2011-12-01', 'merchandise_regex':'[0-9]{5}[A-Z]?',
    'purchase_rule':'merchandise pattern; not C; Quantity > 0; UnitPrice > 0',
    'c_record_rule':'merchandise pattern; C prefix; Quantity < 0; UnitPrice > 0',
    'duplicates':'retain baseline; deduplicate only sensitivity',
    'sampling':'25% of distinct invoices within earliest-invoice-month; rounded nearest integer; all invoice lines retained',
    'split_dates':SPLITS, 'preprocessing':'log1p eligible invoice value, StandardScaler fit on train invoices only',
    'intended_use':'retrospective monthly review of existing customer accounts; no predictive accuracy claim',
    'prior_exposure':'W1/C1 inspected the entire case; this is not a virgin or prospective test set',
    'test_policy':'rules fixed from C1 and agreed W2 plan; no threshold, feature or model selection from test',
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_csv(df: pd.DataFrame, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / name, index=False)


def export_gzip(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path,index=False,compression={'method':'gzip','mtime':0})


def freeze_protocol() -> dict:
    """Write the prespecified protocol before generating W2 result tables."""
    path=ROOT/'evidence/protocol.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(PROTOCOL,indent=2,ensure_ascii=False)+'\n'
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise RuntimeError('Protocol changed: document the amendment before continuing.')
    path.write_text(content,encoding='utf-8')
    return {'protocol_sha256':digest(path),**PROTOCOL}


def load_and_prepare() -> tuple[pd.DataFrame,pd.DataFrame]:
    expected=json.loads((ROOT/'data/raw/source_manifest.json').read_text())['extract_sha256']
    assert digest(RAW)==expected, 'Source input changed'
    raw=pd.read_csv(RAW,dtype={'InvoiceNo':'string','StockCode':'string','CustomerID':'Int64',
                             'Country':'string','Description':'string'},parse_dates=['InvoiceDate'])
    assert list(raw.columns)==COLS
    assert len(raw)==516384
    d=raw.copy()
    d.insert(0,'source_row',np.arange(1,len(d)+1))
    d['month']=d.InvoiceDate.dt.strftime('%Y-%m')
    d['is_c_invoice']=d.InvoiceNo.str.startswith('C')
    d['merchandise_rule']=d.StockCode.str.fullmatch(PROTOCOL['merchandise_regex'])
    d['missing_customer_id']=d.CustomerID.isna()
    d['missing_description']=d.Description.isna()
    d['exact_duplicate']=raw.duplicated(keep='first')
    d['eligible_purchase']=d.merchandise_rule & ~d.is_c_invoice & d.Quantity.gt(0) & d.UnitPrice.gt(0)
    d['eligible_c_record']=d.merchandise_rule & d.is_c_invoice & d.Quantity.lt(0) & d.UnitPrice.gt(0)
    d['row_group']=np.select([d.eligible_purchase,d.eligible_c_record],['priced_purchase','priced_C_record'],default='other_retained')
    d['line_value_gbp']=np.where(d.eligible_purchase,d.Quantity*d.UnitPrice,np.nan)
    d['split']=''
    for key,(start,end) in SPLITS.items():
        d.loc[d.InvoiceDate.ge(start)&d.InvoiceDate.lt(end),'split']=key
    assert d.split.ne('').all()
    export_gzip(d,OUT/'validated_lines.csv.gz')
    return raw,d


def purchases(d: pd.DataFrame) -> pd.DataFrame:
    return d.loc[d.eligible_purchase].copy()


def portfolio(d: pd.DataFrame) -> pd.DataFrame:
    k=purchases(d).dropna(subset=['CustomerID'])
    c=k.groupby('CustomerID',observed=True).agg(value_gbp=('line_value_gbp','sum'),
          invoices=('InvoiceNo','nunique'),lines=('source_row','size')).reset_index()
    return c.sort_values(['value_gbp','CustomerID'],ascending=[False,True]).reset_index(drop=True)


def kpis(d: pd.DataFrame) -> dict:
    p=purchases(d); c=portfolio(d); n=len(c); top=math.ceil(.1*n)
    total=float(p.line_value_gbp.sum()); known=float(c.value_gbp.sum())
    return {'source_lines':len(d),'purchase_lines':len(p),'known_customers':n,'top_ids':top,
            'eligible_value_gbp':total,'known_value_gbp':known,
            'K10_pct':100*float(c.head(top).value_gbp.sum())/known if known else np.nan,
            'ID_coverage_pct':100*known/total if total else np.nan,
            'UK_value_share_pct':100*float(p.loc[p.Country.eq('United Kingdom'),'line_value_gbp'].sum())/total if total else np.nan}


def dictionary() -> pd.DataFrame:
    rows=[
      ('InvoiceNo','Invoice identifier; C prefix marks a cancellation record','string','Nonblank; repeats across item lines','Not expected; cannot identify invoice if absent'),
      ('StockCode','Source item/special-code identifier, not commercial category','string','Nonblank; merchandise-pattern rule is provisional','Not expected; flag rather than invent item'),
      ('Description','Recorded item description','nullable string','Free text; not a key','Unknown/unrecorded description; not proof of zero activity'),
      ('Quantity','Signed units on an invoice line','integer','Positive purchase; negative C record; other signs flagged','Not expected; cannot calculate line value'),
      ('InvoiceDate','Recorded invoice-line timestamp','datetime','2010-12-01 <= date < 2011-12-01','Not expected; cannot assign period'),
      ('UnitPrice','Recorded unit price in GBP','numeric','Positive for value measure; zero/negative retained outside it','Not expected; no price imputation'),
      ('CustomerID','Identifier linking recorded lines to a customer account','nullable integer','Positive identifier; not a continuous measurement','Unidentified purchase; no ID imputation'),
      ('Country','Customer country recorded on this line','string','Source labels; UK share uses row label','Meaning unknown if absent; not delivery destination'),
      ('source_row','Stable position in unchanged case CSV, starting at 1','integer','Unique, 1..516384','Not permitted; not a source transaction ID'),
      ('eligible_purchase','Matches all baseline purchase conditions','boolean','True/False','Not permitted'),
      ('row_group','Mutually exclusive analytical classification','category','priced_purchase; priced_C_record; other_retained','Not permitted'),
      ('line_value_gbp','Quantity times UnitPrice for eligible purchase lines','nullable numeric','Strictly positive when eligible','Undefined outside purchase scope; not recorded zero'),
      ('split','Prespecified chronological partition','category','train; validation; test','Not permitted'),
      ('value_gbp','Sum of eligible purchase value by known ID within stated window','numeric','Positive; GBP, not net revenue or profit','No customer aggregate for missing ID'),
      ('K10_pct','Value of top ceil(0.10*N) IDs / value of all known IDs * 100','numeric','0..100; stated window and known-ID denominator','Undefined when no known-ID value'),
      ('ID_coverage_pct','Known-ID eligible value / all eligible purchase value * 100','numeric','0..100; value-weighted, not fraction of rows','Undefined when no eligible value'),
      ('invoice_value_gbp','Sum of eligible positive purchase lines within one invoice; GBP','numeric','Strictly positive; not net invoice settlement','No aggregate for an invoice without eligible purchases'),
      ('log_invoice_value','Natural log of 1 + invoice_value_gbp expressed numerically in GBP','numeric','Finite and positive; descriptive preprocessing only','Not permitted for an eligible invoice'),
      ('scaled_log_value','(log_invoice_value - training mean) / training population SD; dimensionless','numeric','Finite real number; may be negative; parameters fixed from train','Not permitted; never a replacement for monetary value'),
    ]
    result=pd.DataFrame(rows,columns=['variable','meaning_and_unit','expected_type','acceptable_values','missing_meaning'])
    export_csv(result,'data_dictionary.csv'); return result


def validate(raw: pd.DataFrame,d: pd.DataFrame) -> tuple[pd.DataFrame,dict]:
    inv=d.groupby('InvoiceNo').agg(first=('InvoiceDate','min'),last=('InvoiceDate','max'),
          timestamps=('InvoiceDate','nunique'),lines=('source_row','size'),partitions=('split','nunique'))
    mult=inv.loc[inv.timestamps.gt(1)].copy(); mult['span_minutes']=(mult['last']-mult['first']).dt.total_seconds()/60
    export_csv(mult.reset_index(),'invoice_timestamp_exceptions.csv')
    country=d.dropna(subset=['CustomerID']).groupby('CustomerID').agg(
        countries=('Country',lambda x:'; '.join(sorted(x.dropna().unique()))),
        n_countries=('Country','nunique'),lines=('source_row','size'))
    country=country.loc[country.n_countries.gt(1)]
    export_csv(country.reset_index(),'customer_country_exceptions.csv')
    p=purchases(d)
    idcounts=p.dropna(subset=['CustomerID']).groupby('InvoiceNo').CustomerID.nunique()
    mixed=p.groupby('InvoiceNo').missing_customer_id.agg(['any','all'])
    rows=[]
    def add(code,check,n,action,reason,structural=False):
        if structural: assert n==0, f'{code}: {n} invalid observations'
        rows.append((code,check,'PASS' if n==0 else 'FLAG',int(n),action,reason))
    add('Q01','Schema and numeric/time types',int(not(list(raw.columns)==COLS and pd.api.types.is_integer_dtype(raw.Quantity) and pd.api.types.is_numeric_dtype(raw.UnitPrice) and pd.api.types.is_datetime64_any_dtype(raw.InvoiceDate))),'retain','Required fields and physical types verified',True)
    add('Q02','Invalid/missing timestamps or outside case bounds',int((d.InvoiceDate.isna()|d.InvoiceDate.lt('2010-12-01')|d.InvoiceDate.ge('2011-12-01')).sum()),'retain','Case is twelve complete calendar months',True)
    add('Q03','Missing invoice or item identifier',int((d.InvoiceNo.isna()|d.StockCode.isna()).sum()),'retain','Invoice and source-code grouping require recorded keys',True)
    add('Q04','Nonpositive unit prices',int(d.UnitPrice.le(0).sum()),'retain source; exclude from positive-value measures','Do not guess discount reason or substitute another price')
    add('Q05','Nonpositive quantities',int(d.Quantity.le(0).sum()),'retain; separate eligible negative C records','Signed record meaning differs from a positive purchase')
    add('Q06','Missing CustomerID',int(d.CustomerID.isna().sum()),'retain eligible value; exclude from customer rank','Coverage includes unidentified value; identity cannot be invented')
    add('Q07','Missing description',int(d.Description.isna().sum()),'retain if otherwise eligible','StockCode, not description, supplies the item key')
    add('Q08','Exact repeated rows beyond first copy',int(raw.duplicated().sum()),'retain baseline; compare deduplicated sensitivity','No line ID proves repeated rows erroneous')
    add('Q09','Outside provisional merchandise-code pattern',int((~d.merchandise_rule).sum()),'retain source; exclude baseline; test alternative patterns','Pattern is a scope assumption, not verified item classification')
    add('Q10','Negative quantity without C prefix',int((d.Quantity.lt(0)&~d.is_c_invoice).sum()),'retain outside both eligible measures','Cannot safely classify as an eligible purchase or C cancellation')
    add('Q11','Source-row conservation and disjoint partition violations',int(len(d)!=len(raw) or not d.source_row.is_unique or (d.eligible_purchase&d.eligible_c_record).any()),'retain','One prepared record per source line; flags may overlap but row groups do not',True)
    add('Q12','Eligible purchase invoices with multiple known IDs',int(idcounts.gt(1).sum()),'retain','Invoice-level aggregation must not merge distinct known customers',True)
    add('Q13','Invoice numbers with multiple timestamps',len(mult),'retain; use min/max interval and check split boundaries','One InvoiceNo is not necessarily one timestamp; no silent timestamp replacement')
    add('Q14','Customer IDs with multiple country labels',len(country),'retain country at line level; flag identity consistency','Do not assert a single residence or overwrite historical country labels')
    add('Q15','Invoices crossing chronological partition boundaries',int(inv.partitions.gt(1).sum()),'retain','All lines of a source invoice remain in one partition',True)
    add('Q16','Missing quantities or prices',int((d.Quantity.isna()|d.UnitPrice.isna()).sum()),'retain','No numeric imputation required',True)
    add('Q17','Purchase invoices mixing identified and unidentified lines',int((mixed['any']&~mixed['all']).sum()),'retain','No ambiguous invoice-level ID assignment found',True)
    q=pd.DataFrame(rows,columns=['check_id','check','status','affected_count','treatment','justification'])
    export_csv(q,'quality_checks.csv')
    counts=d.groupby('row_group',observed=True).agg(rows=('source_row','size')).reset_index()
    counts['source_rows_before']=len(raw); counts['source_rows_after']=len(d)
    export_csv(counts,'row_flow.csv')
    details={'invoice_multiple_timestamps':len(mult),'invoice_timestamp_span_max_minutes':float(mult.span_minutes.max()),
             'invoice_timestamp_exceptions_cross_day':int(mult['first'].dt.date.ne(mult['last'].dt.date).sum()),
             'customer_multiple_countries':len(country),'purchase_invoice_mixed_id':int((mixed['any']&~mixed['all']).sum())}
    assert len(mult)==43 and len(country)==8
    return q,details


def feedback_table(details: dict) -> pd.DataFrame:
    rows=[
      ('Self-audit of C1','A provisional product-code scope could be mistaken for a verified category','Keep the rule explicit and repeat narrow/broad code sensitivities','Clarification; baseline retained','data/processed/sensitivity.csv; notebook 3 and 4','K10 is conditional on the stated merchandise rule'),
      ('Self-audit of source','43 invoices have multiple timestamps','Inspect first/last timestamps and assert no invoice crosses split boundaries','New check; not proof of wrong invoices','data/processed/invoice_timestamp_exceptions.csv; notebook 3','Retain invoice lines; do not assign future lines to an earlier partition'),
      ('Self-audit of source','8 CustomerIDs have multiple country labels','Keep source country per line; use line-value country proportions; do not force one country per ID','New check; country stability qualified','data/processed/customer_country_exceptions.csv; notebook 3','Country comparisons do not establish fixed residence or stable identity'),
      ('Self-audit of monthly interpretation','K10 monthly ranking changes with observed IDs and coverage','Show monthly N and ID-value coverage alongside K10','Clarification; no causal missing-ID claim','data/processed/monthly_kpi.csv; notebook 4','A lower K10 alone does not establish diversification'),
      ('W2 extension / self-audit','Entire source period was explored in W1/C1','Freeze W2 rules and use chronological held periods with prior-exposure disclosure','New validation scope; no retrospective untouched-test claim','evidence/protocol.json; notebook 6 and 7','No predictive-accuracy or virgin-holdout conclusion'),
    ]
    result=pd.DataFrame(rows,columns=['source','issue','action_and_reason','change_type','evidence','effect_on_conclusion'])
    export_csv(result,'feedback_to_action.csv'); return result


def analyze(d: pd.DataFrame) -> tuple[dict,pd.DataFrame,pd.DataFrame]:
    base=kpis(d); c=portfolio(d); p=purchases(d)
    prior=json.loads((ROOT/'assessments/C1/data/report_metrics.json').read_text())
    assert base['known_customers']==4293
    assert abs(base['K10_pct']-prior['baseline']['top_decile_share_pct'])<1e-9
    assert abs(base['ID_coverage_pct']-prior['baseline']['known_id_value_coverage_pct'])<1e-9
    monthly=pd.DataFrame([{'month':m,**kpis(g)} for m,g in d.groupby('month',sort=True)])
    export_csv(monthly,'monthly_kpi.csv'); export_csv(c,'customer_portfolio.csv')
    stats={'baseline':base,'median_customer_value':float(c.value_gbp.median()),'mean_customer_value':float(c.value_gbp.mean()),
           'max_customer_value':float(c.value_gbp.max()),'spearman_frequency_value':float(c.invoices.corr(c.value_gbp,method='spearman')),
           'pearson_frequency_value':float(c.invoices.corr(c.value_gbp,method='pearson'))}
    scenarios=[('Baseline',d),('Drop exact repeated rows',d.loc[~d.exact_duplicate]),
               ('Five digits only',d.loc[d.StockCode.str.fullmatch('[0-9]{5}')]),
               ('Remove largest known ID',d.loc[d.CustomerID.ne(c.iloc[0].CustomerID).fillna(True)])]
    sensitivity=pd.DataFrame([{'rule':name,**kpis(frame)} for name,frame in scenarios])
    broad=d.copy(); broad['eligible_purchase']=~d.is_c_invoice&d.Quantity.gt(0)&d.UnitPrice.gt(0)
    broad['line_value_gbp']=np.where(broad.eligible_purchase,broad.Quantity*broad.UnitPrice,np.nan)
    sensitivity=pd.concat([sensitivity,pd.DataFrame([{'rule':'All positive-priced codes',**kpis(broad)}])],ignore_index=True)
    export_csv(sensitivity,'sensitivity.csv')
    stats['sensitivity_min_K10']=float(sensitivity.K10_pct.min());stats['sensitivity_max_K10']=float(sensitivity.K10_pct.max())
    return stats,monthly,sensitivity


def figures(d: pd.DataFrame,monthly: pd.DataFrame) -> list[Path]:
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':150})
    c=portfolio(d); teal='#087F85'; navy='#173E56'; orange='#D57E4E'
    paths=[]
    def save(fig,name):
        path=FIG/name;fig.tight_layout();fig.savefig(path,bbox_inches='tight');plt.close(fig);paths.append(path)
    fig,ax=plt.subplots(figsize=(7.5,3.4));ax.hist(c.value_gbp,bins=np.geomspace(c.value_gbp.min(),c.value_gbp.max(),40),color=teal)
    ax.set(xscale='log',xlabel='Eligible recorded purchase value per known ID (GBP; log scale)',ylabel='Customer IDs')
    save(fig,'customer_value_distribution.png')
    fig,ax=plt.subplots(figsize=(7.5,3.4));ax.scatter(c.invoices,c.value_gbp,s=9,alpha=.35,color=teal)
    ax.set(xscale='log',yscale='log',xlabel='Distinct eligible purchase invoices per known ID (log scale)',ylabel='Eligible value per ID (GBP; log scale)')
    save(fig,'frequency_value_relationship.png')
    fig,ax=plt.subplots(figsize=(7.5,3.4));x=np.r_[0,np.arange(1,len(c)+1)/len(c)*100];y=np.r_[0,c.value_gbp.cumsum()/c.value_gbp.sum()*100]
    ax.plot(x,y,color=teal,lw=2);ax.plot([0,100],[0,100],ls='--',color='gray',label='Equal-value reference')
    top=math.ceil(.1*len(c));value=100*c.head(top).value_gbp.sum()/c.value_gbp.sum()
    ax.scatter([100*top/len(c)],[value],color=orange,zorder=3);ax.annotate(f'Top {top:,} IDs: {value:.1f}%',(100*top/len(c),value),xytext=(25,35),textcoords='offset points')
    ax.set(xlim=(0,100),ylim=(0,100),xlabel='Known IDs ranked from highest value (%)',ylabel='Cumulative known-ID value (%)');ax.legend(loc='lower right')
    save(fig,'concentration_curve.png')
    fig,(ax,bx)=plt.subplots(2,1,figsize=(8.5,5),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    x=np.arange(len(monthly));ax.plot(x,monthly.K10_pct,marker='o',color=teal,label='Monthly K10');ax.plot(x,monthly.ID_coverage_pct,marker='o',color=orange,label='ID-value coverage')
    ax.set(ylim=(0,105),ylabel='Share (%)');ax.legend(ncol=2,loc='lower left');ax.grid(axis='y',alpha=.2)
    bx.bar(x,monthly.known_customers,color=navy);bx.set(ylabel='Known IDs (N)',xticks=x,xticklabels=['Dec 10','Jan 11','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov 11'])
    bx.tick_params(axis='x',labelsize=8)
    save(fig,'monthly_kpi_coverage_population.png')
    return paths


def sample_invoices(d: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    rng=np.random.default_rng(SEED)
    inv=d.groupby('InvoiceNo',sort=True).agg(start=('InvoiceDate','min'),end=('InvoiceDate','max'),rows=('source_row','size'))
    inv['stratum']=inv.start.dt.strftime('%Y-%m')
    selection=[]; strata=[]
    for m,g in inv.groupby('stratum',sort=True):
        count=round(.25*len(g)); ids=rng.choice(g.index.to_numpy(),size=count,replace=False)
        selection.extend(ids.tolist());strata.append((m,len(g),count))
    s=d.loc[d.InvoiceNo.isin(selection)].copy()
    assert s.InvoiceNo.nunique()==len(selection)
    assert s.groupby('InvoiceNo').size().equals(d.loc[d.InvoiceNo.isin(selection)].groupby('InvoiceNo').size())
    export_gzip(s,OUT/'invoice_sample_25pct.csv.gz')
    export_csv(pd.DataFrame({'InvoiceNo':sorted(selection)}),'sample_invoice_ids.csv')
    st=pd.DataFrame(strata,columns=['month','available_invoices','sampled_invoices']);st['invoice_fraction_pct']=100*st.sampled_invoices/st.available_invoices
    st['available_rows']=d.groupby('month').size().reindex(st.month).to_numpy();st['sample_rows']=s.groupby('month').size().reindex(st.month,fill_value=0).to_numpy()
    export_csv(st,'sample_strata.csv')
    comp=pd.DataFrame([{'dataset':'Complete available case',**kpis(d)},{'dataset':'Month-stratified invoice sample',**kpis(s)}])
    for metric in ['K10_pct','ID_coverage_pct','UK_value_share_pct']:
        comp[metric+'_difference_pp']=comp[metric]-comp.iloc[0][metric]
    comp['fraction_source_rows_pct']=100*comp.source_lines/len(d)
    export_csv(comp,'sample_comparison.csv');return s,st,comp


def make_splits(d: pd.DataFrame) -> tuple[dict,pd.DataFrame,pd.DataFrame]:
    # First reserve test; validation is then carved out of the earlier development pool.
    development=d.loc[d.InvoiceDate.lt(SPLITS['test'][0])].copy()
    test=d.loc[d.InvoiceDate.ge(SPLITS['test'][0])].copy()
    splits={'train':development.loc[development.InvoiceDate.lt(SPLITS['validation'][0])].copy(),
            'validation':development.loc[development.InvoiceDate.ge(SPLITS['validation'][0])].copy(),
            'test':test}
    assert set(splits['train'].source_row).isdisjoint(splits['validation'].source_row)
    assert set(development.source_row)==set(splits['train'].source_row)|set(splits['validation'].source_row)
    assert set(development.source_row).isdisjoint(test.source_row)
    hierarchy=pd.DataFrame([
        ('1: reserve test','development',len(development),len(d),'Earlier pool available for training/validation; not the scaler fit set'),
        ('1: reserve test','test',len(test),len(d),'Later assessment period; excluded from development'),
        ('2: carve validation from development','train',len(splits['train']),len(development),'Fit preprocessing only here'),
        ('2: carve validation from development','validation',len(splits['validation']),len(development),'Check the fixed procedure before test transformation'),
    ],columns=['stage','subset','rows','parent_rows','role'])
    hierarchy['parent_fraction_pct']=100*hierarchy.rows/hierarchy.parent_rows
    export_csv(hierarchy,'split_hierarchy.csv')
    summary=[]
    for key,frame in splits.items():
        export_gzip(frame,ROOT/f'data/splits/{key}.csv.gz')
        summary.append({'split':key,'first':str(frame.InvoiceDate.min()),'last':str(frame.InvoiceDate.max()),
                        'rows':len(frame),'row_fraction_pct':100*len(frame)/len(d),'invoices':frame.InvoiceNo.nunique(),
                        'known_ids_raw':frame.CustomerID.nunique(),'eligible_purchase_lines':int(frame.eligible_purchase.sum()),
                        'eligible_known_ids':portfolio(frame).CustomerID.nunique()})
    export_csv(d[['source_row','InvoiceNo','split']],'split_membership.csv')
    checks=[]
    for left,right in [('train','validation'),('train','test'),('validation','test')]:
        a,b=splits[left],splits[right]
        for label,col in [('source_rows','source_row'),('invoices','InvoiceNo'),('known_customer_ids','CustomerID')]:
            overlap=len(set(a[col].dropna())&set(b[col].dropna()))
            checks.append((left,right,label,overlap,'Allowed: same-account later-period scope' if col=='CustomerID' else 'Must be zero'))
            if col!='CustomerID':assert overlap==0
        ha=set(pd.util.hash_pandas_object(a[COLS],index=False));hb=set(pd.util.hash_pandas_object(b[COLS],index=False))
        overlap=len(ha&hb);assert overlap==0
        checks.append((left,right,'exact_source_record_hashes',overlap,'Must be zero; duplicates include invoice and timestamp'))
    assert sum(map(len,splits.values()))==len(d)
    assert d.groupby('InvoiceNo').split.nunique().eq(1).all()
    table=pd.DataFrame(summary);overlap=pd.DataFrame(checks,columns=['left','right','unit','overlap_count','interpretation'])
    export_csv(table,'split_summary.csv');export_csv(overlap,'split_overlap.csv')
    return splits,table,overlap


def preprocess(splits: dict) -> tuple[pd.DataFrame,dict]:
    frames={}
    for key,d in splits.items():
        inv=purchases(d).groupby('InvoiceNo').agg(invoice_value_gbp=('line_value_gbp','sum'),first=('InvoiceDate','min'),last=('InvoiceDate','max')).reset_index()
        inv['log_invoice_value']=np.log1p(inv.invoice_value_gbp)
        inv['split']=key;frames[key]=inv
    scaler=StandardScaler().fit(frames['train'][['log_invoice_value']])
    params_before=(scaler.mean_.copy(),scaler.scale_.copy(),int(scaler.n_samples_seen_))
    rows=[]; events=[]
    events.append({'step':1,'event':'fit train','partition':'train','passed':True,'fitted_count':params_before[2]})
    for key in ['train','validation','test']:
        if key=='test':
            assert len(events)==2 and events[-1]['passed']
        f=frames[key];f['scaled_log_value']=scaler.transform(f[['log_invoice_value']]).ravel()
        assert np.array_equal(params_before[0],scaler.mean_) and np.array_equal(params_before[1],scaler.scale_)
        assert int(scaler.n_samples_seen_)==params_before[2]
        assert np.isfinite(f[['invoice_value_gbp','log_invoice_value','scaled_log_value']].to_numpy()).all()
        assert f.invoice_value_gbp.gt(0).all() and f.InvoiceNo.is_unique
        if key=='validation':
            # Structural applicability is the validation criterion; no distribution-based tuning.
            events.append({'step':2,'event':'validation gate: finite values, positive invoices, unique invoice keys, frozen parameters',
                           'partition':key,'passed':True,'fitted_count':int(scaler.n_samples_seen_)})
        if key=='test':
            events.append({'step':3,'event':'test transformed after validation gate; no refit',
                           'partition':key,'passed':True,'fitted_count':int(scaler.n_samples_seen_)})
        rows.append((key,len(f),float(f.log_invoice_value.mean()),float(f.scaled_log_value.mean()),float(f.scaled_log_value.std(ddof=0))))
    assert abs(frames['train'].scaled_log_value.mean())<1e-10
    assert abs(frames['train'].scaled_log_value.std(ddof=0)-1)<1e-10
    table=pd.DataFrame(rows,columns=['split','invoices','mean_log_value','mean_scaled_value','sd_scaled_value_ddof0'])
    all_inv=pd.concat(frames.values(),ignore_index=True);export_csv(all_inv,'invoice_preprocessing.csv');export_csv(table,'preprocessing_by_split.csv')
    export_csv(pd.DataFrame(events),'validation_execution.csv')
    params={'feature':'log1p(invoice_value_gbp)','fit_partition':'train','fitted_invoice_count':params_before[2],
            'mean':float(scaler.mean_[0]),'scale':float(scaler.scale_[0]),'refit_on_validation_or_test':False,
            'parameter_invariance_verified':True,'K10_uses_original_GBP':True}
    (ROOT/'evidence/preprocessing_parameters.json').write_text(json.dumps(params,indent=2)+'\n')
    return table,params


def holdout_robustness(splits: dict) -> pd.DataFrame:
    """Compare month-level descriptions after the validation gate; never tune a rule."""
    execution=pd.read_csv(OUT/'validation_execution.csv')
    assert execution.step.tolist()==[1,2,3] and execution.passed.all()
    rows=[]
    for key in ['train','validation','test']:
        for month,frame in splits[key].groupby('month',sort=True):
            rows.append({'split':key,'month':month,**kpis(frame)})
    monthly=pd.DataFrame(rows)
    export_csv(monthly,'holdout_monthly_kpi.csv')
    summary=monthly.groupby('split',sort=False).agg(
        months=('month','size'),mean_monthly_K10_pct=('K10_pct','mean'),
        min_monthly_K10_pct=('K10_pct','min'),max_monthly_K10_pct=('K10_pct','max'),
        mean_monthly_ID_coverage_pct=('ID_coverage_pct','mean'),
        min_known_ids=('known_customers','min'),max_known_ids=('known_customers','max')).reset_index()
    reference=float(summary.loc[summary.split.eq('train'),'mean_monthly_K10_pct'].iloc[0])
    summary['mean_K10_difference_from_train_pp']=summary.mean_monthly_K10_pct-reference
    export_csv(summary,'holdout_robustness.csv')
    return summary


def leakage_audit(d: pd.DataFrame,overlap: pd.DataFrame,params: dict) -> pd.DataFrame:
    count=int(overlap.loc[(overlap.left=='train')&(overlap.right=='test')&(overlap.unit=='known_customer_ids'),'overlap_count'].iloc[0])
    rows=[
      ('Future full-case customer totals/rank','present in prior artifacts','C1 aggregates span Dec 2010–Nov 2011; not W2 pre-cutoff features','Would reveal later purchases before review date','Rebuild invoice/period aggregates from rows available at that cut-off; exclude full-year rank from features'),
      ('Repeated customer accounts','present',f'{count} known IDs occur in both train and test','Invalid new-customer independence claim; global customer aggregation could leak future history','Allow repeated IDs for same-account time review; disclose dependence; no full-case profile reuse'),
      ('Duplicated event lines across partitions','absent across chosen partitions',f'{int(d.exact_duplicate.sum())} extra exact repeats within source; zero record-hash and invoice overlap across partitions','Random line splitting could put copies or sibling invoice lines on both sides','Partition by recorded time and verify invoice/record-hash boundaries; retain baseline repeats with sensitivity'),
      ('Preprocessing learned on validation/test','absent in W2',f'Scaler fit on {params["fitted_invoice_count"]} train invoices; parameters unchanged after transformations','Full-data mean/scale would let held data influence fitted rule','Fit once on train; transform validation/test; export fit parameters and invariance checks'),
      ('Target-derived variables in hypothetical prediction','uncertain for future use; no target/model in W2','Invoice value, period value and K10 use completed purchases','Predicting the same purchase value from its total/rank would be circular','Define any future outcome and horizon first; use only prior-cutoff information; no accuracy claim here'),
      ('Prior full-case exploration / analyst leakage','present','W1/C1 inspected all twelve months, including Oct–Nov; source snapshots retained','Current test cannot be described as untouched prospective evidence','Prespecify W2 transformations; treat as descriptive robustness; collect a genuinely later period before prospective evaluation'),
      ('Linked external tables','absent / not applicable','Single UCI source; W2 performs no external join','Future joins could leak later customer states or create duplicate rows','No forced join; require as-of keys, cardinality and match checks before future integration'),
    ]
    table=pd.DataFrame(rows,columns=['risk','status','dataset_evidence','potential_consequence','mitigation'])
    export_csv(table,'leakage_audit.csv');return table


def management_summary(stats: dict,comp: pd.DataFrame,details: dict) -> str:
    b=stats['baseline'];s=comp.iloc[1]
    text=(f'Our historical account-review question and K10 definition remain unchanged from C1. '
          f'The complete case still contains {b["known_customers"]:,} identifiable customers: the highest-value 10% account for {b["K10_pct"]:.1f}% of known purchase value, while IDs cover {b["ID_coverage_pct"]:.1f}% of eligible value. '
          f'W2 adds explicit validation, a month-stratified invoice sample and chronological training, validation and test partitions. '
          f'We retained {details["invoice_multiple_timestamps"]} invoices with multiple timestamps and {details["customer_multiple_countries"]} IDs with multiple country labels, documenting their interpretation rather than overwriting records. '
          f'The sample contains {100*s.source_lines/b["source_lines"]:.1f}% of source lines and yields K10 of {s.K10_pct:.1f}%, illustrating the effect of observing fewer invoices per customer. '
          f'Train-only preprocessing prevents held periods from determining the fitted scale. '
          f'However, missing IDs, provisional product codes and prior exploration of all periods still limit generalization. '
          f'We recommend reviewing major accounts and ID capture together, then obtaining recent transactions and verified identity/code definitions before operational use or prospective evaluation.')
    assert 120<=len(text.split())<=180, len(text.split())
    return text


def finalize(stats,details,comparison,params,quality,split_summary) -> dict:
    result={**stats,'quality_details':details,'sampling':comparison.to_dict(orient='records'),
            'preprocessing':params,'split_counts':split_summary.to_dict(orient='records'),
            'protocol_sha256':digest(ROOT/'evidence/protocol.json'),'input_sha256':digest(RAW),
            'source_rows_before':516384,'source_rows_after':516384,
            'quality_check_count':len(quality),'seed':SEED}
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'w2_metrics.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    summary=management_summary(stats,comparison,details)
    (ROOT/'evidence/management_summary.txt').write_text(summary+'\n',encoding='utf-8')
    artifacts=[RAW,*sorted(OUT.glob('*')),*sorted((ROOT/'data/splits').glob('*')),*sorted(FIG.glob('*.png'))]
    manifest=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in artifacts]
    (ROOT/'evidence/artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return result


def run() -> dict:
    freeze_protocol();raw,d=load_and_prepare();dictionary();q,detail=validate(raw,d);feedback_table(detail)
    stats,monthly,_=analyze(d);figures(d,monthly);_,_,comp=sample_invoices(d)
    splits,summary,overlap=make_splits(d);_,params=preprocess(splits);holdout_robustness(splits);leakage_audit(d,overlap,params)
    return finalize(stats,detail,comp,params,q,summary)


if __name__=='__main__':
    result=run()
    print(json.dumps({'baseline':result['baseline'],'sample':result['sampling'][1],
                      'checks':result['quality_check_count'],'split_rows':{x['split']:x['rows'] for x in result['split_counts']}},indent=2))
