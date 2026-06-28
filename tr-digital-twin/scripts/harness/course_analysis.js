const fs=require("fs");const {JSDOM,VirtualConsole}=require("jsdom");
const ctxProxy=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return ()=>({addColorStop(){}});if(p==='measureText')return ()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const vc=new VirtualConsole();const errors=[];vc.on("jsdomError",e=>errors.push(e&&e.message?e.message:String(e)));
const dom=new JSDOM(fs.readFileSync("tr-twin.html","utf8"),{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,
  beforeParse(window){window.HTMLCanvasElement.prototype.getContext=()=>ctxProxy;window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};if(!window.performance)window.performance={now:()=>0};}});
const w=dom.window;
function load(id,text,name){return new Promise(res=>{const input=w.document.getElementById(id);const file=new w.File([text],name,{type:'text/csv'});Object.defineProperty(input,'files',{value:[file],configurable:true});input.dispatchEvent(new w.Event('change'));setTimeout(res,90);});}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  await sleep(150);
  const cohort=fs.readFileSync('examples/working-class-authors/data/actors/cohorte_contrat.csv','utf8');
  const full=fs.readFileSync('examples/working-class-authors/data/instances/instances_full_empirical.csv','utf8');
  await load('contractfile',cohort,'cohorte.csv');
  await load('instcohortfile',full,'instances_full.csv');
  const rows=w.runSeries();
  const years=rows.map(r=>r.year);
  // présence des acteurs par structure (la circulation transversale matérialisée)
  const arec=w.parseContractCSV(cohort);const aby=w.buildCohortByActor(arec);
  const presAt=(Y)=>{const c=[0,0,0,0];for(const a in aby){const st=aby[a];if(Y<st[0].year)continue;let s=st[0].s;for(const r of st){if(r.year<=Y)s=r.s;else break;}c[s]++;}return c;};
  // force de médiation par structure (max poids des instances NON-contrôle)
  const irec=w.parseContractCSV(full);const iby=w.buildCohortByActor(irec);
  const medAt=(Y)=>{const f=[0,0,0,0];for(const a in iby){const st=iby[a];if(st[0].ctrl)continue;const wv=w.probeWeightAt(st,Y);if(wv==null)continue;const s=st[0].s;if(wv>f[s])f[s]=wv;}return f;};
  const struct={0:{},1:{},2:{},3:{}};
  for(const x of [0,1,2,3])for(const k of ['presence','med','ctrl','recip','sat'])struct[x][k]=[];
  for(const r of rows){const Y=r.year;const pr=presAt(Y),md=medAt(Y),cc=w.controlCapacity(Y).floor;
    for(let x=0;x<4;x++){struct[x].presence.push(pr[x]);struct[x].med.push(md[x]);struct[x].ctrl.push(cc[x]);struct[x].recip.push(r.rRecip[x]);struct[x].sat.push(r.sat[x]);}}
  fs.writeFileSync('/tmp/course.json',JSON.stringify({years,struct}));
  // petit résumé : pic de présence A et D, et corrélation présence~(med+ctrl)
  const NM=['A','B','C','D'];
  for(const x of [0,3]){const P=struct[x].presence,M=struct[x].med,C=struct[x].ctrl;
    const pmax=Math.max(...P),pyr=years[P.indexOf(pmax)];
    console.log(NM[x]+': présence max '+pmax+' en '+pyr+' · force médiation max '+Math.max(...M).toFixed(2)+' · capacité contrôle max '+Math.max(...C).toFixed(3));}
  console.log('✓ /tmp/course.json écrit ·',years.length,'années');
})();
