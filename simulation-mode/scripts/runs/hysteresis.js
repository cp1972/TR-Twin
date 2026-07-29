// Hysterese: erste Phase mit einem Reglerwert fahren, dann OHNE Rücksetzen mit einem anderen weiter.
// Aufruf: node hysteresis.js <app.html> <Profil.csv> <ReglerId> <v1> <n1> <v2> <n2> [aus.json]
const fs = require('fs');
const { JSDOM } = require('jsdom');

const APP = process.argv[2] || './tr-twin.html';
const PROFILE = process.argv[3];
const CURSOR = process.argv[4];
const V1 = +process.argv[5], N1 = +process.argv[6];
const V2 = +process.argv[7], N2 = +process.argv[8];
const OUT = process.argv[9] || './out/hysteresis.json';
if (!PROFILE || !CURSOR || isNaN(V1) || isNaN(V2)) {
  console.error('Usage: node hysteresis.js <app.html> <profile.csv> <cursorId> <v1> <n1> <v2> <n2> [out.json]');
  process.exit(2);
}
const html = fs.readFileSync(APP, 'utf8');
const ctxStub = new Proxy({}, { get: () => (() => ctxStub), set: () => true });
const dom = new JSDOM(html, { runScripts:'dangerously', pretendToBeVisual:true, beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext = () => ctxStub;
  w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
  if (!w.matchMedia) w.matchMedia = () => ({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
}});
function rip(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}

rip(`window.__hyst = function(csv, cid, v1, n1, v2, n2){
  const dt = 1/60*0.68;
  const setC = (id,v)=>{const el=document.getElementById(id); if(el){el.value=v; el.dispatchEvent(new Event('input'));}};
  applyDefaults();
  let chains=null;
  const r = parseCursorCSV(csv);
  if (r) {
    for (const c in r.keys){ const p=r.keys[c]; setC(c, p[p.length-1].val); }
    if (r.chains && Object.keys(r.chains).length) chains = r.chains;
  }
  if (chains){ loadedChains=chains; for(const sx in chains) setChain(+sx, chains[sx]); }
  else { loadedChains=null; resetChains(); }
  setC(cid, v1);
  satS=[0,0,0,0]; rulerHold=[0,0,0,0];
  reset();
  for (let i=0;i<n1;i++) step(dt);                 // phase 1: the past
  const after1 = { S:S.map(v=>+v.toFixed(5)), gini:+gini().toFixed(5) };
  setC(cid, v2);                                   // phase 2: pressure released, NO reset
  for (let i=0;i<n2;i++) step(dt);
  return { after1, S:S.map(v=>+v.toFixed(5)), gini:+gini().toFixed(5), recip:+reciprocity().toFixed(5),
           sat:satS.map(v=>+v.toFixed(3)) };
};`);

const csv = fs.readFileSync(PROFILE, 'utf8');
const r = dom.window.__hyst(csv, CURSOR, V1, N1, V2, N2);
const NM = ['K','P','W','M'];
const pct = a => a.map(v=>(v*100).toFixed(1)).join('/');
console.log(`profile: ${require('path').basename(PROFILE)} · ${CURSOR}: ${V1} (${N1} steps) → ${V2} (${N2} steps, no reset)\n`);
console.log(`  after phase 1 : ${pct(r.after1.S)}  GINI=${r.after1.gini.toFixed(3)}`);
console.log(`  after phase 2 : ${pct(r.S)}  GINI=${r.gini.toFixed(3)}  R=${r.recip.toFixed(3)}`);
const ap = r.S.indexOf(Math.max(...r.S));
console.log(`  apex          : ${NM[ap]} at ${(r.S[ap]*100).toFixed(1)} %`);
fs.mkdirSync(require('path').dirname(OUT), { recursive:true });
fs.writeFileSync(OUT, JSON.stringify(r));
console.log('\n→', OUT);
