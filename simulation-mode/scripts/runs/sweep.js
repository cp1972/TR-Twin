const fs=require('fs'); const {JSDOM}=require('jsdom');
const DIR='/home/claude/TR-Twin-extract/simulation-mode';
const html=fs.readFileSync('/home/claude/TR-Twin-extract/tr-twin.html','utf8');
const ctxStub=new Proxy({},{get:()=>(()=>ctxStub),set:()=>true});
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext=()=>ctxStub; w.requestAnimationFrame=()=>0; w.cancelAnimationFrame=()=>{};
  if(!w.matchMedia)w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}});
function rip(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}
rip(`window.__sweep=function(csv,migVal,n){
  const dt=1/60*0.68;
  const r=parseCursorCSV(csv); if(!r) return null;
  applyDefaults();
  for(const cid in r.keys){const p=r.keys[cid];const el=document.getElementById(cid);if(el){el.value=p[p.length-1].val;el.dispatchEvent(new Event('input'));}}
  const em=document.getElementById('mig'); em.value=migVal; em.dispatchEvent(new Event('input'));
  if(r.chains&&Object.keys(r.chains).length){loadedChains=r.chains;for(const sx in r.chains)setChain(+sx,r.chains[sx]);}
  else{loadedChains=null;resetChains();}
  satS=[0,0,0,0]; rulerHold=[0,0,0,0];   // WICHTIG: reset() setzt satS NICHT zurueck
  reset(); for(let i=0;i<n;i++)step(dt);
  return {G:+gini().toFixed(4), R:+reciprocity().toFixed(4), S:S.map(v=>+v.toFixed(4)), sat:Math.max(...satS)};
};`);
const MIGS=[0.5,0.7,0.8,1.1,1.4,1.7];
const ORIG={White:{0.5:0.394,0.8:0.354,1.1:0.000,1.4:0.011,1.7:0.011}, Tilly:{0.5:0.405,0.8:0.197,1.1:0.072,1.4:0.094,1.7:0.105}};
for(const name of ['White','Tilly']){
  const csv=fs.readFileSync(`${DIR}/profil_${name}.csv`,'utf8');
  console.log(`\n=== ${name} ===`);
  console.log(' mig   GINI(headless)  GINI(Original)  Größen K/P/W/M %');
  for(const m of MIGS){
    const r=dom.window.__sweep(csv,m,5000);
    const o=ORIG[name][m]!==undefined?ORIG[name][m].toFixed(3):'  —  ';
    console.log(` ${m.toFixed(2)}     ${r.G.toFixed(3)}          ${o}       ${r.S.map(v=>(v*100).toFixed(1)).join('/')}`);
  }
}
