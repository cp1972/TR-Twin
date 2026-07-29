// Kennzahlen des Endzustands für eine Liste von Konfigurationen (Profil und abweichende Regler).
// Aufruf: node metrics.js <app.html> <spec.json> [aus.json]
// spec.json: [{ "label":"TR", "profile":null, "cursors":{} }, { "label":"Parsons", "profile":"./simulation-mode/profiles/profil_Parsons.csv" }, ...]
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const APP  = process.argv[2] || './tr-twin.html';
const SPEC = process.argv[3];
const OUT  = process.argv[4] || './out/metrics.json';
if (!SPEC) { console.error('Usage: node metrics.js <app.html> <spec.json> [out.json]'); process.exit(2); }

const html = fs.readFileSync(APP, 'utf8');
const ctxStub = new Proxy({}, { get: () => (() => ctxStub), set: () => true });
const dom = new JSDOM(html, { runScripts:'dangerously', pretendToBeVisual:true, beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext = () => ctxStub;
  w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
  if (!w.matchMedia) w.matchMedia = () => ({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
}});
function rip(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}

rip(`window.__one = function(csv, overrides, n, sd){
  const dt = 1/60*0.68;
  if (sd != null) seed = sd;                          // optional: change the RNG seed
  applyDefaults();                                    // all cursors -> TR reference values
  let chains = null;
  if (csv) {
    const r = parseCursorCSV(csv);
    if (r) {
      for (const cid in r.keys){ const p=r.keys[cid]; const el=document.getElementById(cid);
        if (el){ el.value=p[p.length-1].val; el.dispatchEvent(new Event('input')); } }
      if (r.chains && Object.keys(r.chains).length) chains = r.chains;
    }
  }
  for (const cid in (overrides||{})) {                // explicit overrides win
    const el = document.getElementById(cid);
    if (el){ el.value = overrides[cid]; el.dispatchEvent(new Event('input')); }
  }
  if (chains){ loadedChains=chains; for(const sx in chains) setChain(+sx, chains[sx]); }
  else { loadedChains=null; resetChains(); }
  satS=[0,0,0,0]; rulerHold=[0,0,0,0];                // reset() clears neither
  reset();
  for (let i=0;i<n;i++) step(dt);
  let crossOff=0; for(let x=0;x<4;x++) for(let y=0;y<4;y++) if(x!==y) crossOff+=crossViz[x][y];
  return {
    S: S.map(v=>+v.toFixed(5)),
    gini: +gini().toFixed(5),
    recip: +reciprocity().toFixed(5),
    crossOff: +crossOff.toFixed(5),          // volume of inter-structural circulation
    sat: satS.map(v=>+v.toFixed(3)),
    ruler: ruler.slice(),
    resid: +meanResid.toFixed(5),
    structRecip: [0,1,2,3].map(structRecip).map(v=>+v.toFixed(4)),
    structGini:  [0,1,2,3].map(structGini).map(v=>+v.toFixed(4)),
    vertGini:    [0,1,2,3].map(vertGiniX).map(v=>+v.toFixed(4))
  };
};`);

const spec = JSON.parse(fs.readFileSync(SPEC, 'utf8'));
const rows = [];
console.log(`${spec.length} configurations\n`);
console.log('label                          K     P     W     M    | GINI   R      crossOff');
console.log('-'.repeat(80));
for (const c of spec) {
  const csv = c.profile ? fs.readFileSync(c.profile, 'utf8') : null;
  const n = c.steps || 1819;
  const r = dom.window.__one(csv, c.cursors || {}, n, c.seed != null ? c.seed : null);
  rows.push(Object.assign({ label:c.label }, r));
  console.log(`${c.label.padEnd(28)} ${r.S.map(v=>(v*100).toFixed(1).padStart(5)).join(' ')} | ${r.gini.toFixed(3)} ${r.recip.toFixed(3)}  ${r.crossOff.toFixed(3)}`);
}
fs.mkdirSync(path.dirname(OUT), { recursive:true });
fs.writeFileSync(OUT, JSON.stringify(rows));
console.log('\n→', OUT);
