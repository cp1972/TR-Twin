const fs=require("fs");const {JSDOM,VirtualConsole}=require("jsdom");
const ctxProxy=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return ()=>({addColorStop(){}});if(p==='measureText')return ()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const errors=[];const vc=new VirtualConsole();vc.on("jsdomError",e=>errors.push(e&&e.message?e.message:String(e)));
const html=fs.readFileSync("tr-twin.html","utf8");let nextCSV="";
const dom=new JSDOM(html,{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,beforeParse(window){
  window.HTMLCanvasElement.prototype.getContext=()=>ctxProxy;window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
  window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};if(!window.performance)window.performance={now:()=>0};
  window.FileReader=function(){this.readAsText=()=>{this.result=nextCSV;this.onload&&this.onload();};};}});
const w=dom.window,D=w.document;const feed=(id,csv)=>{nextCSV=csv;D.getElementById(id).onchange({target:{files:[{name:'x.csv'}]}});};
const setSel=(id,v)=>{D.getElementById(id).value=String(v);};const val=id=>D.getElementById(id).value;
setTimeout(()=>{
  let ok=true;const fail=m=>{ok=false;console.log("X "+m);};
  if(errors.length){fail("erreurs chargement");errors.forEach(e=>console.log("  ",String(e).split("\n")[0]));}else console.log("ok page chargee");
  feed('contractfile',fs.readFileSync('data-mode/data/actors/cohorte_contrat.csv','utf8'));
  feed('instcohortfile',fs.readFileSync('data-mode/data/instances/instances_full_empirical.csv','utf8'));
  D.getElementById('scnDetect').click();
  const opts=[...D.getElementById('scnTrend').options];
  console.log("ok detect:",opts.length,"tendances");
  const histEnd=+val('tlend');console.log("   fin historique (tlend):",histEnd);
  const presIdx=opts.findIndex(o=>/presence|présence/i.test(o.textContent));
  const ctrlIdx=opts.findIndex(o=>/control|contrôle/i.test(o.textContent));
  // Hilfsfunktion: fährt ein Szenario, liefert [readHTML, tlend]
  function run(idx,verb,mag,hor,toX){setSel('scnTrend',idx);setSel('scnVerb',verb);D.getElementById('scnToWrap').style.display=(verb==='umlenken')?'flex':'none';if(verb==='umlenken')setSel('scnTo',toX);setSel('scnMag',mag);D.getElementById('scnHor').value=String(hor);
    D.getElementById('scnRun').click();return [D.getElementById('scnRead').innerHTML,+val('tlend')];}
  // 1) der Zeitstrahl verlängert sich
  const [r1,end1]=run(presIdx,'beschleunigen',0.8,30);
  console.log((end1===histEnd+30?"ok":"X")+" frise prolongee: tlend "+histEnd+" -> "+end1+" (attendu "+(histEnd+30)+")");if(end1!==histEnd+30)ok=false;
  console.log((r1.includes('<table')?"ok":"X")+" lecture rendue");if(!r1.includes('<table'))ok=false;
  // 2) die AMPLITUDE ändert das Ergebnis
  const [rA]=run(presIdx,'beschleunigen',0.1,30);const [rB]=run(presIdx,'beschleunigen',1.0,30);
  console.log((rA!==rB?"ok":"X")+" l'ampleur change la projection");if(rA===rB)ok=false;
  // 3) der HORIZONT ändert das Ergebnis UND den Zeitstrahl
  const [rC,endC]=run(presIdx,'beschleunigen',0.5,10);const [rD,endD]=run(presIdx,'beschleunigen',0.5,50);
  console.log((rC!==rD&&endC!==endD?"ok":"X")+" l'horizon change projection+frise ("+endC+" vs "+endD+")");if(rC===rD||endC===endD)ok=false;
  // 4) die Kontrolle wirkt ebenfalls (Kontrolltendenz)
  if(ctrlIdx>=0){const [rE,endE]=run(ctrlIdx,'beschleunigen',0.8,30);console.log((rE.includes('<table')&&endE===histEnd+30?"ok":"X")+" scenario de controle: lecture+frise");if(!rE.includes('<table')||endE!==histEnd+30)ok=false;}
  // 5) Determinismus (dieselben Parameter zweimal)
  const [d1]=run(presIdx,'beschleunigen',0.6,20);const [d2]=run(presIdx,'beschleunigen',0.6,20);
  console.log((d1===d2?"ok":"X")+" deterministe");if(d1!==d2)ok=false;
  // 6) RESET stellt den historischen Zeitstrahl wieder her
  D.getElementById('scnClear').click();
  console.log((+val('tlend')===histEnd?"ok":"X")+" reset: frise revenue a "+val('tlend'));if(+val('tlend')!==histEnd)ok=false;
  // 7) Karte und Wiedergabe (Neustart, Zeitstrahl erneut verlängert)
  run(presIdx,'beschleunigen',0.7,25);D.getElementById('scnSave').click();
  D.getElementById('scnClear').click();
  const rep=D.getElementById('scnCards').querySelector('button');rep&&rep.click();
  console.log(((+val('tlend')>histEnd)&&D.getElementById('scnRead').innerHTML.includes('<table')?"ok":"X")+" replay carte: frise re-prolongee + lecture");if(!(+val('tlend')>histEnd))ok=false;
  // 8) Dreisprachigkeit
  w.setLang('de');w.refreshScnLang();const de=[...D.getElementById('scnVerb').options].map(o=>o.textContent).join(',');w.setLang('en');
  console.log("ok verbes DE:",de);
  console.log(ok?"\nSCENARIO SMOKE TEST OK":"\nECHEC");
},220);
