// C1-inspired editorial design. Every quantitative graphic remains a native chart.
export async function buildVisualDeck(presentation,D,cover,fade,oldNotes=[]) {
  const R=D.results;
  const C={navy:'#071D2B',ink:'#102A38',teal:'#0B7F83',orange:'#E58B5B',mint:'#9FD8CF',paper:'#F4F7F6',rule:'#CEDDDC',muted:'#637781',white:'#FFFFFF'};
  const PROFILE=[C.teal,C.orange,C.navy];
  const fr=v=>Number((Number(v)/100).toFixed(10));
  const num=(v,d=0)=>Number(v).toLocaleString('en-GB',{minimumFractionDigits:d,maximumFractionDigits:d});
  const profiles=R.test_profiles.filter(x=>x.method==='KMeans');
  const validation=R.metrics.filter(x=>x.partition==='validation');
  presentation.slides.keep([]);presentation.theme.defaultFont='Arial';
  const slides=[],manifest=[];
  function text(s,body,x,y,w,h,size=26,color=C.ink,bold=false,font='Arial'){
    const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    sh.text=body;sh.text.style={fontSize:size,color,bold,typeface:font};sh.text.insets=0;return sh;
  }
  function number(s,value,x,y,w,color=C.teal,size=85){return text(s,value,x,y,w,110,size,color,true,'Consolas');}
  function base(title,dark=false){
    const s=presentation.slides.add();s.setViewportSize(1280,720);s.background.fill=dark?C.navy:C.paper;
    if(title)text(s,title,48,42,1184,110,42,dark?C.white:C.ink,true,'Montserrat');
    text(s,'UCI ONLINE RETAIL  /  C2',48,681,520,20,13,dark?C.mint:C.muted,false,'Consolas');
    text(s,String(slides.length+1).padStart(2,'0'),1190,681,45,20,14,dark?C.mint:C.muted,false,'Consolas');
    slides.push(s);return s;
  }
  function notes(s,oldIndex,extra=''){
    const logicalSlide=slides.length>2?slides.length-1:slides.length;
    const seconds=[25,65,55,55,85,65,80,75,65,60,60,55,0][logicalSlide-1];
    let speech=(oldNotes[oldIndex]??'').replace(/Speaking guide: approximately \d+ seconds including pauses\./,'Speaking guide: approximately '+seconds+' seconds including pauses.');
    if(logicalSlide===6)speech=speech.replace('validation table','validation comparison');
    if(logicalSlide===7)speech='Speaking guide: approximately 80 seconds including pauses.\n\nEach dot is one of the same 3,021 held customer-months. The charts have identical coordinates and scales. Further right means more invoices and higher up means larger average invoices, after the training-only log/scaling transformation. The left chart colors records by the simple value rule. The right chart colors them by the frozen KMeans model. The vertical bands reflect discrete invoice counts. This makes the difference between grouping by total value and grouping by purchase pattern visible. The axes are unitless standardized values, not raw invoice counts or pounds.';
    if(logicalSlide===9)speech='Speaking guide: approximately 65 seconds including pauses.\n\nThese bars show percentages within each reference value tier. They are derived from the exact cross-table in the notebook and backup slide. Of the 380 higher-value customer-months, 124 fall in Profile 2 and 256 in Profile 3. Similar total contribution can come from different purchase patterns. The test silhouette is 0.464 for KMeans and 0.289 for the value rule on identical records and inputs. The improvement describes this feature-space geometry. It does not establish more profitable actions or classification accuracy.';
    s.speakerNotes.text=speech+'\n\n'+extra+'\nSource: submitted 01_C2_Customer_Profiles.ipynb; Chen (2015), UCI Online Retail, doi:10.24432/C5BW33. Method: scikit-learn 1.5.2 KMeans, StandardScaler and silhouette_score documentation. Design reference: team-provided GROUP_Medina_Castillo_C1_Slides.pdf.';
  }
  function fonts(chart){
    for(const st of [chart.titleTextStyle,chart.legend?.textStyle,chart.dataLabels?.textStyle,chart.xAxis?.textStyle,chart.yAxis?.textStyle])if(st)st.typeface='Arial';
    return chart;
  }
  function chart(s,type,config,sourceKey){
    const titles={model_partitions:'Active customer-months',reference_composition:'Composition within each value tier',stability:'Share of identified value',value_bridge:'Share of all eligible value'};
    if(!config.title)config={...config,title:titles[sourceKey]??sourceKey,titleTextStyle:{fontSize:23,bold:true,fill:C.ink}};
    const c=fonts(s.charts.add(type,{chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0},...config}));
    manifest.push({slide:slides.length,type,sourceKey,series:config.series.map(x=>({name:x.name,values:x.values,xValues:x.xValues})),categories:config.categories??null});
    return c;
  }
  function col(s,values,categories,title,x,y,w,h,format='0',max=null,colors=PROFILE){
    return chart(s,'bar',{position:{left:x,top:y,width:w,height:h},title,titleTextStyle:{fontSize:23,bold:true,fill:C.ink},categories,
      series:[{name:title,values,fill:C.teal,points:values.map((_,i)=>({idx:i,fill:colors[i%colors.length]}))}],hasLegend:false,
      barOptions:{direction:'column',grouping:'clustered',gapWidth:75},
      xAxis:{textStyle:{fontSize:20,fill:C.ink}},yAxis:{min:0,...(max!==null?{max}:{}),...(max===3?{majorUnit:1}:{}),numberFormatCode:format,textStyle:{fontSize:18,fill:C.muted},majorGridlines:{fill:C.rule,width:1}},
      dataLabels:{showValue:true,position:'outEnd',numberFormatCode:format,textStyle:{fontSize:23,bold:true,fill:C.ink}}},title);
  }
  function scatter(s,column,title,x){
    const bounds=D.scatter_bounds;
    return chart(s,'scatter',{position:{left:x,top:190,width:564,height:355},title,titleTextStyle:{fontSize:25,bold:true,fill:C.ink},
      scatterOptions:{style:'marker'},series:D.scatter[column].map((a,i)=>({name:a.name,xValues:a.x,values:a.y,fill:PROFILE[i],line:{fill:'none',width:0},marker:{symbol:'circle',size:3,fill:PROFILE[i]}})),
      hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:17,fill:C.ink}},
      xAxis:{min:bounds.xmin,max:bounds.xmax,majorUnit:2,crossesAt:bounds.xmin,tickLabelPosition:'low',numberFormatCode:'0',textStyle:{fontSize:17,fill:C.muted},title:{text:'Frequency: training-scaled log',textStyle:{fontSize:18,fill:C.ink}},majorGridlines:{fill:C.rule,width:.5}},
      yAxis:{min:bounds.ymin,max:bounds.ymax,majorUnit:2,crossesAt:bounds.ymin,tickLabelPosition:'low',numberFormatCode:'0',textStyle:{fontSize:17,fill:C.muted},title:{text:'Invoice size: training-scaled log',textStyle:{fontSize:18,fill:C.ink}},majorGridlines:{fill:C.rule,width:.5}}},'scatter_'+column);
  }
  let s=base('',true);
  s.images.add({dataUrl:cover,contentType:'image/png',alt:'Decorative purchase-value artwork reused from our C1 cover',fit:'cover',position:{left:773,top:0,width:507,height:720}});
  s.images.add({dataUrl:fade,contentType:'image/png',alt:'Original C1 cover edge blend',fit:'cover',position:{left:690,top:0,width:180,height:720}});
  text(s,'BUSINESS INTELLIGENCE  /  C2',68,95,650,35,15,C.mint,true,'Consolas');
  text(s,'How do customers\nbuild recorded\npurchase value?',68,166,708,220,54,C.white,true,'Montserrat');
  text(s,'Monthly purchase profiles in UCI Online Retail',68,435,660,80,27,C.mint);
  text(s,'Moisés Medina  ×  Ignacia Castillo\n10 November 2026',68,600,650,60,19,C.white);
  notes(s,0,'Cover artwork is a decorative image extracted intact from our supplied C1 reference, not a data chart.');

  s=base('C1 recap: customer concentration');
  text(s,'We audited UCI Online Retail and measured how much eligible purchase value came from the highest-value customers.',70,143,1140,95,27,C.muted);
  number(s,num(R.annual_W2_reproduction.K10_pct,1)+'%',70,254,510,C.teal,88);
  text(s,'K10: share from the top 10% of IDs',75,365,525,41,25,C.ink,true);
  text(s,'Of identified purchase value, 60.5%\ncame from 430 of 4,293 customer IDs.',75,413,525,84,26);
  number(s,num(R.annual_W2_reproduction.ID_coverage_pct,1)+'%',713,254,500,C.orange,88);
  text(s,'ID coverage: value linked to an ID',718,365,510,41,25,C.ink,true);
  text(s,'We could rank 85.7% of eligible value.\nThe remaining 14.3% had no customer ID.',718,413,510,84,26);
  text(s,'C1 CONCLUSION',75,523,1100,28,15,C.teal,true,'Consolas');
  text(s,'Review major accounts and improve ID capture together.',75,559,1125,52,30,C.ink,true);
  text(s,'C2 explores how purchase frequency and invoice size distinguish customer activity.',75,627,1130,45,24,C.teal);
  s.speakerNotes.text='Speaking guide: approximately 50 seconds including pauses.\n\nIn C1 we checked the quality of the Online Retail data, defined eligible positive purchases and examined how recorded purchase value was distributed across customer IDs. The top 10 percent, 430 of 4,293 identified customers, contributed 60.5 percent of identified value. ID-value coverage was 85.7 percent, which left 14.3 percent outside the ranking. Our conclusion was to review major accounts while investigating ID capture. C2 extends that descriptive question by separating purchase frequency from average invoice size. These are historical positive recorded purchases, not profit or evidence of loyalty.\n\nSource: team-provided GROUP_Medina_Castillo_C1_Slides.pdf, slide 11. The same baseline is reproduced in the submitted C2 notebook. C1 uses customer IDs across the full analysis period. C2 models active customer-months, so their population counts differ.';

  s=base('The Online Retail case');
  text(s,'A UK gift retailer with many wholesale customers. December 2010–November 2011.',48,133,1180,65,26,C.muted);
  number(s,'516,384',70,220,570,C.teal,84);text(s,'source invoice lines retained from W2',75,322,520,55,25);
  number(s,num(D.model_record_count),710,220,520,C.orange,84);text(s,'active identified customer-month records',715,322,500,60,25);
  const nodes=[['INVOICE LINE',C.teal,C.white,70],['INVOICE',C.navy,C.white,490],['CUSTOMER-MONTH',C.orange,C.navy,910]];
  for(const [label,fill,ink,x] of nodes){
    const box=s.shapes.add({geometry:'roundRect',position:{left:x,top:438,width:300,height:76},fill,line:{fill:'none',width:0},borderRadius:10});
    box.text=label;box.text.style={fontSize:21,typeface:'Consolas',bold:true,color:ink,alignment:'center',verticalAlignment:'middle'};
  }
  for(const x of [399,819])s.shapes.add({geometry:'rightArrow',position:{left:x,top:466,width:62,height:16},fill:C.mint,line:{fill:'none',width:0}});
  text(s,'Many item lines form an invoice. Eligible identified invoices form each monthly record.',70,557,1140,70,27,C.ink,true);
  text(s,'All original lines remain auditable. Missing-ID value stays visible outside the customer profiles.',70,630,1140,40,21,C.muted);
  notes(s,1,'There are 12,408 active ID-months across 7,195 training, 2,192 validation and 3,021 test records. They are not 12,408 distinct customers. Original W2 eligibility remains positive Quantity/UnitPrice, non-C and the provisional merchandise-code rule. The source-line diagram restates the unit distinction from C1.');

  s=base('What we group, and why');
  number(s,'F',80,170,420,C.teal,112);text(s,'Purchase frequency',80,305,510,50,32,C.ink,true,'Montserrat');
  text(s,'Distinct eligible invoices\nfor one active ID-month',80,375,510,95,30);
  number(s,'A',714,170,420,C.orange,112);text(s,'Average invoice value',714,305,510,60,31,C.ink,true,'Montserrat');
  text(s,'Monthly eligible value ÷ F\nGBP per eligible invoice',714,375,500,95,30);
  text(s,'W2: the top 10% held 60.5% of identified value. C2 explores their purchase patterns.',80,493,1120,40,23,C.muted);
  text(s,'EXAMPLE',80,540,150,25,15,C.teal,true,'Consolas');
  text(s,'Two invoices totalling £100 give F = 2 and A = £50.',80,578,1120,55,29,C.ink,true);
  notes(s,2,'Business continuity: W2 annual K10 is 60.5% among known IDs, with ID-value coverage 85.7%. C2 distinguishes purchase patterns within recorded activity. F×A equals monthly value for each record. We omit total value as a redundant third clustering input. The example is illustrative, not an asserted source record.');

  s=base('Past months define the later evaluation');
  text(s,'Monthly modeling records',70,152,1100,45,25,C.muted);
  chart(s,'bar',{position:{left:70,top:215,width:1140,height:315},categories:['Test  Oct–Nov','Validation  Aug–Sep','Training  Dec–Jul'],
    series:[{name:'Active ID-months',values:[3021,2192,7195],fill:C.teal,points:[{idx:0,fill:C.orange},{idx:1,fill:C.navy},{idx:2,fill:C.teal}]}],hasLegend:false,
    barOptions:{direction:'bar',grouping:'clustered',gapWidth:70},xAxis:{textStyle:{fontSize:24,fill:C.ink}},yAxis:{min:0,max:8000,majorUnit:2000,textStyle:{fontSize:19,fill:C.muted},majorGridlines:{fill:C.rule,width:1}},
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'#,##0',textStyle:{fontSize:27,bold:true,fill:C.ink}}},'model_partitions');
  text(s,'Training alone determines the scaler, centers and reference cutoffs.',70,564,1120,60,29,C.teal,true);
  text(s,'No shared invoice or ID-month. Recurring accounts and prior full-period EDA remain disclosed.',70,632,1120,43,21,C.muted);
  notes(s,3,'Source row counts remain 285,421 / 85,510 / 145,453. The graphic reports customer-month counts, a different unit. Validation is carved from the earlier development pool and test stays outside fitting.');

  s=base('One model and one simple reference',true);
  text(s,'MODEL',70,173,460,30,16,C.mint,true,'Consolas');text(s,'KMeans',70,218,500,62,40,C.white,true,'Montserrat');
  text(s,'log1p(F) and log1p(A)\nTraining-only StandardScaler\nThree profiles, fixed in advance',70,323,500,165,30,C.white);
  text(s,'20 initializations · seed 4232026',70,548,510,58,23,C.mint,false,'Consolas');
  text(s,'REFERENCE',713,173,490,30,16,C.orange,true,'Consolas');text(s,'Monthly value rule',713,218,510,100,35,C.white,true,'Montserrat');
  text(s,'Lower: up to £329.65\nMiddle: up to £1,036.768\nHigher: above that cutoff',713,344,510,157,29,C.white);
  text(s,'Training percentiles stay fixed later',713,548,510,62,23,C.mint);
  notes(s,4,'Additional exact setting: Lloyd algorithm and max_iter=300. KMeans groups by Euclidean distance in standardized log-feature space. Three is a manageable first description, not an optimal k claim. The value rule learns p50 and p90 from those same training records. No test score chooses either rule.');

  s=base('Validation checks before the test');
  number(s,'2,192',70,203,480,C.teal,90);text(s,'validation ID-months',75,310,440,60,28);
  text(s,'All records assigned\nThree profiles populated\nFitted parameters unchanged',75,413,440,150,27,C.ink,true);
  col(s,[Number(validation.find(x=>x.method==='KMeans').silhouette.toFixed(10)),Number(validation.find(x=>x.method==='Value rule').silhouette.toFixed(10))],['KMeans','Value rule'],'Silhouette',570,179,640,368,'0.000',1,[C.teal,C.orange]);
  text(s,'Higher silhouette means clearer separation in this input space.',570,557,640,49,22,C.muted);
  text(s,'We retain the prespecified first model before assigning the test records.',70,610,1130,60,28,C.teal,true);
  notes(s,5,'Silhouette ranges approximately from -1 to 1. These two positive results use a 0–1 display scale. It is an internal separation diagnostic on the same transformed inputs, not classification accuracy or evidence of business impact. Structural validation completes before the test transform.');

  s=base('The same records, two ways to group');
  text(s,'3,021 test ID-months. Identical coordinates and ranges in both charts.',48,137,1160,46,25,C.muted);
  scatter(s,'reference','Value reference',48);scatter(s,'cluster','KMeans profiles',668);
  text(s,'A similar monthly total can come from larger invoices or more frequent purchases.',70,604,1130,65,27,C.teal,true);
  notes(s,7,'Both native scatter charts include all 3,021 held ID-month records without sampling or clipping. Coordinates are training-standardized log1p frequency and invoice size. The first chart colors the fixed value tiers; the second colors the frozen KMeans assignments. Color correspondence follows each legend. No new fitting or target labels are introduced.');

  s=base('Three profiles describe different purchase patterns');
  col(s,profiles.map(x=>x.records),['P1','P2','P3'],'ID-month records',48,174,365,335,'#,##0',1600);
  col(s,profiles.map(x=>x.median_invoices),['P1','P2','P3'],'Median invoice count',458,174,365,335,'0',3);
  col(s,profiles.map(x=>Number(x.median_invoice_value_gbp.toFixed(2))),['P1','P2','P3'],'Median avg invoice (GBP)',868,174,365,335,'0.00',500);
  text(s,'P1  Smaller invoices',58,539,370,47,24,C.teal,true);
  text(s,'P2  Larger invoice months',455,539,395,47,24,C.orange,true);
  text(s,'P3  More frequent months',866,539,370,65,24,C.navy,true);
  text(s,'P3 holds 26.6% of test ID-months and contributes 55.0% of identified test value.',70,623,1140,48,25,C.ink,true);
  notes(s,6,'The plotted original-unit medians are frequency 1/1/2 and mean invoice value £152.48/£416.19/£313.225. The GBP column is the median of each record’s average invoice value. Records are 864/1,352/805. A customer can move between profiles across months. These descriptions do not establish loyalty or profit.');

  s=base('A value tier can contain different purchase patterns');
  number(s,'380',65,194,390,C.teal,103);text(s,'higher-value ID-months',72,311,410,65,28,C.ink,true);
  text(s,'124 in Profile 2\n256 in Profile 3',72,430,400,105,30);
  chart(s,'bar',{position:{left:506,top:188,width:708,height:337},categories:['Lower value','Middle value','Higher value'],
    series:D.reference_composition.map((a,i)=>({name:'P'+(i+1),values:a.values,fill:PROFILE[i],dataLabelOverrides:a.values.flatMap((v,j)=>v===0?[{idx:j,showValue:false}]:v<.1?[{idx:j,textStyle:{fontSize:16,bold:true,fill:C.white}}]:[])})),
    barOptions:{direction:'bar',grouping:'stacked',overlap:100,gapWidth:75},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:20,fill:C.ink}},
    xAxis:{textStyle:{fontSize:22,fill:C.ink}},yAxis:{min:0,max:1,majorUnit:.5,numberFormatCode:'0%',textStyle:{fontSize:19,fill:C.muted}},
    dataLabels:{showValue:true,position:'center',numberFormatCode:'0.0%',textStyle:{fontSize:21,bold:true,fill:C.white}}},'reference_composition');
  text(s,'Each reference tier totals 100% of its records',535,548,650,50,23,C.muted);
  text(s,'Test silhouette   KMeans 0.464   /   value rule 0.289',70,621,1140,52,29,C.teal,true,'Consolas');
  notes(s,7,'The stacked chart shows conditional percentages within each reference tier, derived from the unchanged 3×3 cross-table. It is not a confusion matrix. The higher tier has 380 records, of which 32.6% map to P2 and 67.4% to P3. Silhouette is measured on identical standardized inputs and favors separation in that geometry, not necessarily better actions.');

  s=base('Earlier major accounts keep contributing');
  number(s,'362',65,189,405,C.teal,98);text(s,'accounts fixed at September close',70,300,410,91,29,C.ink,true);
  text(s,'Active in October: 218\nActive in November: 265',70,452,420,101,28);
  chart(s,'bar',{position:{left:525,top:178,width:685,height:360},categories:['October','November'],
    series:[{name:'Fixed group',values:R.stability.map(x=>fr(x.frozen_group_known_value_pct)),fill:C.teal},{name:'Monthly top 10%',values:R.stability.map(x=>fr(x.reranked_K10_pct)),fill:C.orange}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:100},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:20,fill:C.ink}},
    xAxis:{textStyle:{fontSize:22,fill:C.ink}},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:19,fill:C.muted},majorGridlines:{fill:C.rule,width:1}},
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:21,bold:true,fill:C.ink}}},'stability');
  text(s,'Both groups use identified value as denominator',568,552,630,46,23,C.muted);
  text(s,'The earlier group contributes 46–48% later. Group sizes differ from the monthly top decile.',70,622,1140,50,25,C.ink,true);
  notes(s,8,'The fixed group comes from December–September: 362 of 3,613 known IDs. It contributes 48.161% of known value in October and 46.125% in November. The re-ranked monthly decile is a context comparison with a different group size, not a like-sized model contest. Inactive in one month does not establish churn.');

  s=base('Missing IDs change the scope of the findings');
  number(s,'21.45%',65,205,455,C.orange,87);text(s,'of November eligible value\nhas no CustomerID',70,321,440,105,29,C.ink,true);
  const bridgeCols=[['Known top-decile purchases','Known top 10%',C.teal],['Other identified purchases','Other identified',C.navy],['Unidentified purchases','Unidentified',C.orange]];
  chart(s,'bar',{position:{left:523,top:181,width:690,height:349},categories:['November','October'],
    series:bridgeCols.map(([key,name,fill])=>({name,values:R.value_bridge.map(x=>fr(x[key])).reverse(),fill})),
    barOptions:{direction:'bar',grouping:'stacked',overlap:100,gapWidth:85},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:17,fill:C.ink}},
    xAxis:{textStyle:{fontSize:22,fill:C.ink}},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:18,fill:C.muted}},
    dataLabels:{showValue:true,position:'center',numberFormatCode:'0.0%',textStyle:{fontSize:20,bold:true,fill:C.white}}},'value_bridge');
  text(s,'Identified and unidentified value total 100%',569,547,630,44,23,C.muted);
  text(s,'Review identifiable accounts and investigate ID capture together.',70,621,1140,51,29,C.teal,true);
  notes(s,9,'The unknown bucket may include many people. It is not one artificial customer or cluster. Both displayed months sum to 100% before rounding. The unidentified share is 8.9367% in October and 21.4488% in November. Customer-specific profile claims cannot extend to that whole bucket without verified linkage.');

  s=base('What the model supports',true);
  text(s,'EVIDENCE',70,174,490,30,16,C.mint,true,'Consolas');
  text(s,'Frequency and invoice size\ndescribe different\npurchase patterns.',70,234,510,210,38,C.white,true,'Montserrat');
  text(s,'The simple value rule remains useful\nwhen contribution alone is the question.',70,477,510,105,27,C.mint);
  text(s,'PROPOSED REVIEW',722,174,490,30,16,C.orange,true,'Consolas');
  text(s,'Review accounts with\nprofiles and value\ncoverage together.',722,234,500,210,36,C.white,true,'Montserrat');
  text(s,'Next: recent linked transactions\nand a stakeholder review of usefulness.',722,477,500,105,27,C.mint);
  text(s,'Historical, purchase-active identified records. Profit, loyalty and campaign effects remain unmeasured.',70,627,1140,48,22,C.white);
  notes(s,10,'The supported conclusion is descriptive. All periods were exposed in earlier EDA; recurring IDs are not independent new-customer samples. KMeans imposes three groups and depends on variables/scaling. Recent linked data and stakeholder review are the proposed improvement, not claims that an action will work.');

  s=base('Reference comparison and sources');
  const vals=[['Same 3,021 test records','Lower value','Middle value','Higher value'],...R.test_cross.map(x=>[x.cluster,num(x['Lower value']),num(x['Middle value']),num(x['Higher value'])])];
  const tb=s.tables.add({rows:4,columns:4,left:70,top:171,width:1140,height:240,values:vals,columnWidths:[390,250,250,250]});
  tb.borders.assign({fill:C.rule,width:1});
  for(let r=0;r<4;r++)for(let c=0;c<4;c++){const a=tb.getCell(r,c);a.fill=r===0?C.navy:(r%2?C.white:'#E3EFED');a.text.style={fontSize:25,color:r===0?C.white:C.ink,bold:r===0,typeface:'Arial'};}
  text(s,'Source: Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33. CC BY 4.0.',70,459,1140,57,23,C.muted);
  text(s,'Method: scikit-learn 1.5.2 KMeans, StandardScaler and silhouette_score.',70,525,1140,55,23,C.muted);
  text(s,'Counts refer to customer-months, not distinct customers or true outcome labels.',70,608,1140,58,27,C.teal,true);
  notes(s,11,'Backup only. Full code, provenance, contribution/AI notes and eight defense checkpoints remain inside the unchanged executed notebook. This table preserves exact cross-counts behind the percentage graphic. Official method references: https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.KMeans.html and https://scikit-learn.org/1.5/modules/generated/sklearn.metrics.silhouette_score.html.');
  return {slides:14,mainSlides:13,nativeCharts:manifest.length,nativeChartOwnerSlides:[5,7,8,9,10,11,12],nativeTableOwnerSlides:[14],manifest};
}
