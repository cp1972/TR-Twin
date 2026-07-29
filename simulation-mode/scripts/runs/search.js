// Parametersuche: App einmal laden, viele Konfigurationen rechnen, beste Treffer melden.
const fs = require('fs');
const { JSDOM } = require('jsdom');
const APP = '/home/claude/TR-Twin-extract/tr-twin.html';
const html = fs.readFileSync(APP, 'utf8');
const ctxStub = new Proxy({}, { get: () => (() => ctxStub), set: () => true });
const dom = new JSDOM(html, { runScripts:'dangerously', pretendToBeVisual:true, beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext=()=>ctxStub; w.requestAnimationFrame=()=>0; w.cancelAnimationFrame=()=>{};
  if(!w.matchMedia) w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
}});
function runInPage(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}

// Einen Lauf im Seiten-Kontext ausführen: Regler setzen, Ketten, reset, N Schritte, Kennzahlen zurück.
runInPage(`window.__once = function(cfg){
  const dt=1/60*0.68;
  for(const cid in cfg.cursors){ const el=document.getElementById(cid); if(el){ el.value=cfg.cursors[cid]; el.dispatchEvent(new Event('input')); } }
  if(cfg.chains){ loadedChains=cfg.chains; for(const sx in cfg.chains) setChain(+sx, cfg.chains[sx]); }
  else { loadedChains=null; resetChains(); }
  reset();
  for(let i=0;i<cfg.n;i++) step(dt);
  return { R:+reciprocity().toFixed(4), G:+gini().toFixed(4), sat:satS.map(v=>+v.toFixed(3)), S:S.map(v=>+v.toFixed(4)) };
};`);

// Parsons-Ketten (aus profil_Parsons.csv): A->D,B,C · D->A,B,C · B->D,A,C · C->B,A,D
const CH = { 0:[3,1,2], 3:[0,1,2], 1:[3,0,2], 2:[1,0,3] };
const TARGET = { R:0.51, G:0.22, sat:0 };

const grid = {
  rate:  [1.8, 2.0, 2.2],
  back:  [1.0, 1.2],
  over:  [1.0, 1.7],
  mig:   [0.50, 0.55, 0.60, 0.65, 0.70],
  decl:  [0.50, 0.65],
};
const fixed = { alpha:1.0, anchor:0.6, cap:0.6, rho:1.0, peak:0.5, plast:0.25, dynam:0.2 };

const keys = Object.keys(grid);
const results = [];
function rec(i, acc){
  if(i===keys.length){
    for(const chains of [CH, null]){
      const cursors = Object.assign({}, fixed, acc);
      const r = dom.window.__once({ cursors, chains, n:1819 });
      const satMax = Math.max(...r.sat);
      const err = Math.abs(r.R-TARGET.R) + Math.abs(r.G-TARGET.G) + satMax*0.3;
      results.push({ err, R:r.R, G:r.G, satMax, chains: !!chains, cfg: Object.assign({}, acc) });
    }
    return;
  }
  for(const v of grid[keys[i]]){ acc[keys[i]]=v; rec(i+1, acc); }
}
rec(0, {});
results.sort((a,b)=>a.err-b.err);
console.log(`${results.length} Konfigurationen gerechnet · Ziel: R=0.51 GINI=0.22 sat=0\n`);
console.log('  R     GINI   satMax  Ketten  Regler');
for(const r of results.slice(0,10)){
  const c = Object.entries(r.cfg).map(([k,v])=>`${k}=${v}`).join(' ');
  console.log(`  ${r.R.toFixed(3)} ${r.G.toFixed(3)}  ${r.satMax.toFixed(2)}    ${r.chains?'ja ':'nein'}    ${c}`);
}
