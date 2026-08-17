const fs=require("fs");
const {JSDOM,VirtualConsole}=require("jsdom");
const ctxProxy=new Proxy({},{get:(o,p)=>{
  if(p==='createRadialGradient'||p==='createLinearGradient')return ()=>({addColorStop(){}});
  if(p==='measureText')return ()=>({width:10});
  return typeof p==='string'?(()=>{}):undefined;}});
const vc=new VirtualConsole();const errors=[];vc.on("jsdomError",e=>errors.push(e&&e.message?e.message:String(e)));
const html=fs.readFileSync("tr-twin.html","utf8");
const dom=new JSDOM(html,{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,
  beforeParse(window){
    window.HTMLCanvasElement.prototype.getContext=()=>ctxProxy;
    window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};
    if(!window.performance)window.performance={now:()=>0};
  }});
const w=dom.window;
function loadFile(id,text,name){return new Promise(res=>{
  const input=w.document.getElementById(id);
  const file=new w.File([text],name,{type:'text/csv'});
  Object.defineProperty(input,'files',{value:[file],configurable:true});
  input.dispatchEvent(new w.Event('change'));
  setTimeout(res,80);});}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const COH=fs.existsSync('data-mode/data/actors/cohorte_contrat.csv')?'data-mode/data/actors/cohorte_contrat.csv':'cohorte_contrat.csv';
  await sleep(150);
  if(errors.length){console.log("✗ erreurs chargement:",errors[0]);process.exit(1);}
  const cohort=fs.readFileSync(COH,'utf8');
  const insts=fs.readFileSync('data-mode/data/instances/instances_probe_demo.csv','utf8');
  await loadFile('contractfile',cohort,'cohorte_contrat.csv');
  const tlstart=w.document.getElementById('tlstart').value, tlend=w.document.getElementById('tlend').value;
  console.log('cohorte chargée · timeline',tlstart,'→',tlend,'· statut:',(w.document.getElementById('contractstatus').textContent||'').slice(0,60));
  // Lauf ohne Instanzen
  const rowsA=w.runSeries();
  await loadFile('probefile',insts,'data-mode/data/instances/instances_probe_demo.csv');
  console.log('instances · prismPick items:',w.document.getElementById('prismPick').children.length);
  const rowsB=w.runSeries();
  let dmax=0;for(let i=0;i<Math.min(rowsA.length,rowsB.length);i++)dmax=Math.max(dmax,Math.abs(rowsA[i].gini-rowsB[i].gini));
  let dRG=0;for(let i=0;i<Math.min(rowsA.length,rowsB.length);i++)for(let x=0;x<4;x++)dRG=Math.max(dRG,Math.abs(rowsA[i].rGini[x]-rowsB[i].rGini[x]));
  console.log('Δgini global:',dmax.toFixed(4),'· Δgini interne max (par structure):',dRG.toFixed(4),dRG>0.003?'→ weightDrive ACTIF ✓':'');
  // ---- Zirkulation (aus den Übergängen der Kohorte) ----
  const rec=w.parseContractCSV(fs.readFileSync(COH,'utf8'));
  const tr=w.buildFullTransitions(rec); const FLUXW=40;
  function circAt(Y){const c=[0,0,0,0];let tot=0;for(const e of tr){if(e.year>Y-FLUXW&&e.year<=Y){if(e.sf===e.st)continue;c[e.sf]++;c[e.st]++;tot++;}}return {c,tot};}
  // ---- Stärke der Instanzen (aus den Gewichten) ----
  const byI=w.buildCohortByActor(w.parseContractCSV(insts));
  const istruct={}; for(const a in byI) istruct[a]=byI[a][0].s;
  function forceAt(Y){const f=[null,null,null,null];for(const a in byI){const wv=w.probeWeightAt(byI[a],Y);if(wv==null)continue;const x=istruct[a];f[x]=(f[x]==null)?wv:Math.max(f[x],wv);}return f.map(v=>v==null?0:v);}
  // ---- Zusammenführung ----
  const years=rowsB.map(r=>r.year);
  const struct={0:{circ:[],force:[],gini:[],recip:[]},1:{circ:[],force:[],gini:[],recip:[]},2:{circ:[],force:[],gini:[],recip:[]},3:{circ:[],force:[],gini:[],recip:[]}};
  const overall={circ:[],force:[],gini:[],recip:[]};
  for(const r of rowsB){const Y=r.year;const cc=circAt(Y),ff=forceAt(Y);
    let sw=0,fw=0;for(let x=0;x<4;x++){sw+=r.S[x];fw+=r.S[x]*ff[x];}
    for(let x=0;x<4;x++){struct[x].circ.push(cc.c[x]);struct[x].force.push(ff[x]);struct[x].gini.push(r.rGini[x]);struct[x].recip.push(r.rRecip[x]);}
    overall.circ.push(cc.tot);overall.force.push(sw>0?fw/sw:0);overall.gini.push(r.gini);overall.recip.push(r.recip);}
  fs.writeFileSync('/tmp/signals.json',JSON.stringify({years,struct,overall}));
  console.log('✓ signaux écrits /tmp/signals.json ·',years.length,'années ·',years[0],'→',years[years.length-1]);
})();
