// Author native editable evidence in the live Artifact Session presentation.
export async function buildDeck(presentation, R) {
  const C={navy:'#082230',teal:'#087F85',orange:'#ED8957',paper:'#F5F7F5',white:'#FFFFFF',muted:'#586974',rule:'#CED8DD'};
  presentation.slides.keep([]);
  presentation.theme.defaultFont='Arial';
  const slides=[];
  const fmt=(n,d=0)=>Number(n).toLocaleString('en-GB',{minimumFractionDigits:d,maximumFractionDigits:d});
  const gbp=n=>'£'+fmt(n,2);
  // Excel workbooks preserve at most 15 significant digits. Ten decimal places
  // in fractions are far more precise than displayed percentages and portable.
  const fraction=n=>Number((Number(n)/100).toFixed(10));
  const profiles=R.test_profiles.filter(x=>x.method==='KMeans');
  const vm=R.metrics.filter(x=>x.partition==='validation');
  const tm=R.metrics.filter(x=>x.partition==='test');
  const source='Sources: UCI Online Retail, Chen (2015), https://doi.org/10.24432/C5BW33. Numerical evidence: submitted 01_C2_Customer_Profiles.ipynb and its saved results.';
  const method='Method: scikit-learn 1.5.2 KMeans, StandardScaler and silhouette_score official documentation.';
  function text(s,body,x,y,w,h,size=26,color=C.navy,bold=false){
    const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    shape.text=body;shape.text.style={fontSize:size,color,bold,fontFamily:'Arial'};
    return shape;
  }
  function base(title,dark=false){
    const s=presentation.slides.add();s.setViewportSize(1280,720);s.background.fill=dark?C.navy:C.paper;
    text(s,title,64,42,1152,100,44,dark?C.white:C.navy,true);
    text(s,String(slides.length+1).padStart(2,'0'),1180,666,48,28,17,dark?C.white:C.muted);
    slides.push(s);return s;
  }
  function note(s,seconds,speech,extra=''){
    s.speakerNotes.text=`Speaking guide: approximately ${seconds} seconds including pauses.\n\n${speech}\n\n${source}\n${extra}`;
  }
  function table(s,values,x,y,w,h,widths=null,size=24){
    const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,
      ...(widths?{columnWidths:widths}:{})});
    t.borders.assign({fill:C.rule,width:1,style:'solid'});
    for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
      const cell=t.getCell(r,c);cell.fill=r===0?C.navy:(r%2?C.white:'#E4F0EE');
      cell.text.style={fontSize:size,color:r===0?C.white:C.navy,bold:r===0,fontFamily:'Arial'};
    }
    return t;
  }
  function lineChart(s,series,x=82,y=170,w=1100,h=360){
    return s.charts.add('line',{position:{left:x,top:y,width:w,height:h},categories:['October','November'],series,
      hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:21,fill:C.navy}},
      chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',
      xAxis:{textStyle:{fontSize:22,fill:C.navy}},
      yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:21,fill:C.navy},majorGridlines:{fill:C.rule,width:1}},
      dataLabels:{showValue:true,position:'top',numberFormatCode:'0.0%',textStyle:{fontSize:20,fill:C.navy}},
      lineOptions:{smooth:false}});
  }
  let s=base('Monthly customer\npurchase profiles',true);
  text(s,'Can frequency and invoice size improve a value-only account review?',68,257,1020,125,36,'#9DD8D0');
  text(s,'Moisés Medina and Ignacia Castillo',68,468,1000,52,28,C.white);
  text(s,'Business Intelligence IIB423T-1\nC2 · 10 November 2026',68,543,980,85,24,C.white);
  note(s,30,'Our project studies customer concentration in a historical online retailer. Today we extend that work with one clustering model. We ask whether monthly invoice frequency and invoice size give a more useful account description than a value-only rule. We will explain the unit of analysis, the training comparison and what the results can support.');

  s=base('The retailer and the review question');
  text(s,'UCI Online Retail',68,168,1110,55,34,C.teal,true);
  text(s,'A UK gift retailer with many wholesale customers\nDecember 2010 to November 2011\n516,384 invoice lines in the preserved W2 extract',68,240,1120,155,30);
  text(s,'W2: the top 10% of identified accounts contributed 60.5% of identified annual value.',68,426,1100,90,30,C.navy,true);
  text(s,'C2 asks how purchase frequency and invoice size differ within that activity.',68,550,1100,75,28,C.teal);
  note(s,65,'The source is a public UCI dataset from a UK retailer selling gifts. Many customers are wholesalers, so large accounts are plausible. We use the same twelve complete months and eligibility rules as W2. One source line is an item entry on an invoice. Several lines can form an invoice, and several invoices can share a customer ID. Our earlier finding was a concentration of recorded value. That does not tell us whether an account contributes through frequent purchases or larger invoices. We now study that distinction.');

  s=base('One active account in one month');
  table(s,[['Feature','Definition','Business meaning'],['Frequency F','Distinct eligible invoices','How often the account bought'],['Invoice size A','Monthly value ÷ invoice count','GBP per eligible invoice']],68,172,1144,220,[250,440,454],27);
  text(s,'Example: two eligible invoices totalling £100 give F = 2 and A = £50.',68,431,1115,80,29,C.teal,true);
  text(s,'Only active identified ID-months enter either grouping. Purchases without an ID remain in value coverage.',68,553,1100,83,27);
  note(s,65,'Our model row is one active identified customer in one calendar month. Frequency counts distinct eligible invoices. Invoice size is monthly eligible value divided by that count. The example here explains the calculation and is not a claimed dataset record. Monthly value is their product, so we do not add it again as a third model input. We do not create zeros for months with no observed purchase. Missing customer IDs cannot receive a profile. Their eligible value remains visible in coverage and in the separate value table later.');

  s=base('The same W2 time boundaries');
  table(s,[['Partition','Source lines','Active ID-months','Unique active IDs'],
    ['Train: Dec–Jul','285,421','7,195','3,145'],['Validation: Aug–Sep','85,510','2,192','1,769'],['Test: Oct–Nov','145,453','3,021','2,405']],68,167,1144,300,[338,264,275,267],25);
  text(s,'Fit the scaler and model on training only. Validation precedes test.',68,500,1120,65,29,C.teal,true);
  text(s,'Recurring IDs are intentional. Earlier EDA already exposed the test months.',68,594,1120,58,25);
  note(s,60,'We reserve October and November as test and take validation from the earlier development period. The actual training fit uses December through July. The raw-line counts exactly reproduce W2. Customer-month counts are smaller because we aggregate and require an eligible identified purchase. No invoice or ID-month is shared across partitions. The same customer may recur later, which fits a same-account review but prevents a claim about independent new customers. All periods appeared in earlier EDA, so this is a retrospective check rather than a pristine prospective test.');

  s=base('KMeans and the value reference',true);
  text(s,'KMeans',68,169,490,60,35,'#9DD8D0',true);
  text(s,'log1p(F), log1p(A)\nTraining-only StandardScaler\nThree profiles\n20 initializations, seed 4232026',68,250,510,245,29,C.white);
  text(s,'Simple reference',687,169,500,60,35,'#9DD8D0',true);
  text(s,'Training monthly-value cutoffs\nLower: up to £329.65\nMiddle: up to £1,036.768\nHigher: above that cutoff',687,250,520,245,29,C.white);
  text(s,'Both methods keep their learned rules fixed for later records.',68,562,1115,73,29,C.white,true);
  note(s,90,'KMeans assigns each point to the nearest center and updates centers to reduce squared distances. We choose three profiles in advance to keep the first description manageable. We do not claim three is optimal. Logarithms reduce the effect of large ranges. StandardScaler then prevents the GBP dimension from dominating invoice counts. Both are positive inputs and we retain large accounts. Our reference is simpler: two monthly-value percentiles estimated from training. We freeze those exact cutoffs for validation and test, so the later high-value fraction need not be exactly ten percent. Neither grouping has true class labels. They answer related descriptive questions.',method);

  s=base('Validation precedes the final comparison');
  table(s,[['Same 2,192 validation ID-months','KMeans','Value rule'],['Silhouette',fmt(vm.find(x=>x.method==='KMeans').silhouette,3),fmt(vm.find(x=>x.method==='Value rule').silhouette,3)]],68,168,1144,170,[644,250,250],29);
  text(s,'Every record receives both assignments.\nAll three groups are populated.\nScaler parameters and cluster centers remain unchanged.',68,388,1110,150,28);
  text(s,'We retain the fixed first model without tuning on test.',68,574,1110,60,31,C.teal,true);
  note(s,65,'Before evaluating test, we inspect validation. The code requires finite positive features, complete assignments, three populated profiles and unchanged fitted parameters. A structural failure stops execution before test. We also inspect group sizes and silhouette. Silhouette compares distances within a group with the nearest other group. Larger values indicate clearer separation in this specific feature space. We retain the prespecified first model rather than trying many settings. We have no known labels and therefore do not report classification accuracy. This validation table does not replace the final test comparison.',method);

  s=base('Test profiles differ in purchase pattern');
  table(s,[['Profile','ID-months','Record share','Median F','Median A'],...profiles.map(p=>[p.group,fmt(p.records),fmt(p.record_share_pct,1)+'%',fmt(p.median_invoices),gbp(p.median_invoice_value_gbp)])],68,170,1144,280,[254,205,235,205,245],27);
  text(s,'Profile 1: smaller invoices\nProfile 2: larger single-invoice months\nProfile 3: more frequent purchase months',68,486,1100,140,29,C.teal,true);
  note(s,85,'These are the frozen model assignments for the test records. Profile one contains 864 customer-months and has a median invoice size of about 152 pounds. Profile two contains 1,352 records, with a median of one invoice and an invoice size of about 416 pounds. Profile three contains 805 records, a median of two invoices and an invoice size of about 313 pounds. It contributes 55 percent of identified test value. A person may have a different profile in another month. These are descriptive labels, not evidence of loyalty, profitability or permanent customer types.');

  s=base('The value reference mixes purchase patterns');
  table(s,[['Same test records','Lower value','Middle value','Higher value'],...R.test_cross.map(p=>[p.cluster,fmt(p['Lower value']),fmt(p['Middle value']),fmt(p['Higher value'])])],68,168,1144,260,[344,265,265,270],27);
  text(s,`Test silhouette: KMeans ${fmt(tm.find(x=>x.method==='KMeans').silhouette,3)} / value rule ${fmt(tm.find(x=>x.method==='Value rule').silhouette,3)}`,68,470,1130,62,32,C.teal,true);
  text(s,'Of 380 higher-value ID-months, 124 belong to Profile 2 and 256 to Profile 3.',68,555,1110,73,28);
  note(s,80,'This is a cross-table of two partitions of exactly the same 3,021 test records. It is not a confusion matrix because the reference does not supply true labels. The higher-value rule includes 380 records. Of these, 124 are in the larger single-invoice profile and 256 in the more frequent profile. That is the additional distinction the model provides. The test silhouette is 0.464 for KMeans and 0.289 for the rule. Both use the same scaled inputs. KMeans optimizes a related distance objective, so stronger geometric separation is not proof of more profitable commercial actions.',method);

  s=base('Earlier major accounts still contribute');
  text(s,'Share of identified eligible purchase value',78,135,1100,42,24,C.muted);
  lineChart(s,[{name:'Earlier fixed group',values:R.stability.map(x=>fraction(x.frozen_group_known_value_pct)),line:{fill:C.navy,width:3},marker:{symbol:'circle',size:8},dataLabels:{showValue:true,position:'bottom',numberFormatCode:'0.0%',textStyle:{fontSize:21,fill:C.navy}}},
    {name:'Monthly top 10%',values:R.stability.map(x=>fraction(x.reranked_K10_pct)),line:{fill:C.teal,width:3},marker:{symbol:'circle',size:8},dataLabels:{showValue:true,position:'top',numberFormatCode:'0.0%',textStyle:{fontSize:21,fill:C.teal}}}],86,180,1090,337);
  text(s,'Freeze 362 accounts using December–September. Active later: 218 in October and 265 in November.',68,548,1110,90,28,C.teal,true);
  note(s,65,'The instructor asked whether concentration persists in a later period. We freeze a review group using only records through September and follow the same 362 accounts later. Their share of identified value is about 48.2 percent in October and 46.1 percent in November. The number active changes from 218 to 265. We also show each month’s re-ranked top decile for context. The group sizes differ, so this is a persistence diagnostic, not a like-sized model competition. No purchase in one month is not proof of churn. These later historical months had already been explored.');

  s=base('Unidentified value remains outside profiling');
  text(s,'Share of all eligible positive purchase value',78,135,1100,42,24,C.muted);
  const series=[['Known top-decile purchases','Known top 10%',C.teal],['Other identified purchases','Other identified',C.navy],['Unidentified purchases','Unidentified',C.orange]].map(([sourceName,name,color])=>({name,values:R.value_bridge.map(x=>fraction(x[sourceName])).reverse(),fill:color}));
  s.charts.add('bar',{position:{left:78,top:183,width:1120,height:325},categories:['November','October'],series,
    barOptions:{direction:'bar',grouping:'stacked',overlap:100,gapWidth:65},hasLegend:true,
    legend:{position:'bottom',overlay:false,textStyle:{fontSize:20,fill:C.navy}},
    xAxis:{textStyle:{fontSize:22,fill:C.navy}},
    yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:20,fill:C.navy}},
    dataLabels:{showValue:true,position:'center',numberFormatCode:'0.0%',textStyle:{fontSize:22,fill:C.white}},
    chartFill:'none',plotAreaFill:'none',chartLine:{fill:'none',width:0}});
  text(s,'21.45% of November eligible value has no CustomerID.',68,535,1110,70,34,C.teal,true);
  text(s,'That bucket can contain many people. It never becomes one artificial customer.',68,615,1100,52,25);
  note(s,60,'This chart uses all eligible purchase value as its denominator. Each month has identified purchases from the current top group, other identified purchases and unidentified purchases. In November, 21.45 percent is unidentified. That value remains part of the business context even though we cannot give it a customer profile. The bucket can contain many real people, including people who also appear with an ID elsewhere. We therefore cannot claim our known-ID top group is the top group of all real customers. Reviewing identifiable accounts and investigating ID capture are both defensible.');

  s=base('A bounded account-review recommendation',true);
  text(s,'Use profiles to distinguish frequency from invoice size during manual account review.',68,176,1110,124,36,'#9DD8D0',true);
  text(s,'The value-only rule remains simpler when contribution alone is the question.',68,339,1100,93,30,C.white);
  text(s,'Next: recent transactions, verified customer linkage and a stakeholder review of profile usefulness.',68,478,1110,117,30,C.white);
  note(s,55,'Our supported conclusion is limited but useful. The model describes different purchasing patterns that a total-value rule mixes together. We can use that distinction to structure manual account review. If contribution alone is the question, the simple value rule may be enough. We have not estimated profit, future churn or campaign effects. The next improvement is recent data with verified identity links, comparable complete months and stakeholder review. Each member should be able to explain the model, reference and these limits in their own words.');

  s=base('Sources and defense checkpoints');
  text(s,'Source: UCI Online Retail, Chen (2015)\nDOI 10.24432/C5BW33, CC BY 4.0',68,166,1120,90,27);
  text(s,'Method: scikit-learn 1.5.2\nKMeans, StandardScaler and silhouette_score',68,288,1120,90,27);
  text(s,'Why this unit and these two features?\nWhat does silhouette measure?\nWhich conclusions survive missing customer IDs?',68,430,1120,148,31,C.teal,true);
  text(s,'Full code, contributions, AI disclosure and references are inside the submitted notebook.',68,614,1100,48,22,C.muted);
  s.speakerNotes.text='Backup slide. Defense prompts: explain eligible purchase rules and why source rows are retained; distinguish invoice lines, invoices and active ID-months; explain log1p and training-only scaling; explain KMeans nearest centers and fixed k=3; explain the training-value reference and changed test group shares; explain why the cross-table is not a confusion matrix; distinguish silhouette from accuracy and commercial impact; explain prior exposure, recurring customers and unidentified value.\n\n'+source+'\n'+method+'\nOfficial documentation: https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.KMeans.html; https://scikit-learn.org/1.5/modules/generated/sklearn.metrics.silhouette_score.html. Brief: updated C2 IIB423T-1 supplied by the team. AI support and planned member review responsibilities appear in notebook section 9.';
  return {slideCount:slides.length,mainSlides:11,targetMinutes:12,nativeTables:[3,4,6,7,8],nativeCharts:[9,10]};
}
