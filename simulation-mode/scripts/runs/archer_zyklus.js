// Archer: morphogenetischer Zyklus (Kapitel 9, Abbildung 3).
// Drei Läufe im Schritt-Modus mit dem Profil profil_Archer.csv (Zirkulation 1,8), Keim 1:
//   Morphostase        Konzentration zum Pol (alpha) 1,0 über den ganzen Lauf
//   Morphogenese       alpha 1,8 über den ganzen Lauf
//   Elaboration verriegelt  alpha 1,8 bis zum dritten Messpunkt, danach 1,2 (ohne Rücksetzen)
// Gemessen wird der transversale Gini an fünf Punkten: Schritt 0, 1250, 2500, 3750, 5000.
//
//   node simulation-mode/scripts/runs/archer_zyklus.js [aus.json]
//   python3 simulation-mode/scripts/figures/render_archer.py aus.json simulation-mode/figures/archer_morphogenese.svg
const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const REPO = path.resolve(__dirname, '..', '..', '..');
const OUT = process.argv[2] || './out/archer_zyklus.json';
const PUNKTE = [0, 1250, 2500, 3750, 5000], WECHSEL = 2500;
const html = fs.readFileSync(path.join(REPO, 'tr-twin.html'), 'utf8');
const csv = fs.readFileSync(path.join(REPO, 'simulation-mode', 'profiles', 'profil_Archer.csv'), 'utf8');
const ctxStub = new Proxy({}, { get: () => (() => ctxStub), set: () => true });
function lauf(a1, a2) {
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, beforeParse(w) {
    w.HTMLCanvasElement.prototype.getContext = () => ctxStub; w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
    if (!w.matchMedia) w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
  } });
  const s = dom.window.document.createElement('script');
  s.textContent = `window.__lauf = function(csv, a1, a2, punkte, wechsel){
    const dt = 1/60*0.68;
    const setC = (id,v)=>{const el=document.getElementById(id); if(el){el.value=v; el.dispatchEvent(new Event('input'));}};
    applyDefaults();
    const r = parseCursorCSV(csv);
    for (const c in r.keys){ const p=r.keys[c]; setC(c, p[p.length-1].val); }
    if (r.chains && Object.keys(r.chains).length){ loadedChains=r.chains; for(const sx in r.chains) setChain(+sx, r.chains[sx]); } else { loadedChains=null; resetChains(); }
    setC('alpha', a1); satS=[0,0,0,0]; rulerHold=[0,0,0,0]; reset();
    const g = []; let t = 0;
    for (const p of punkte){ while (t < p){ if (t === wechsel) setC('alpha', a2); step(dt); t++; } g.push(+gini().toFixed(4)); }
    return g; };`;
  dom.window.document.body.appendChild(s);
  const g = dom.window.__lauf(csv, a1, a2, PUNKTE, WECHSEL); dom.window.close(); return g;
}
const res = { punkte: PUNKTE, wechsel: WECHSEL,
  morphogenese: lauf(1.8, 1.8), verriegelt: lauf(1.8, 1.2), morphostase: lauf(1.0, 1.0) };
for (const k of ['morphogenese', 'verriegelt', 'morphostase']) console.log(k.padEnd(13), res[k].map(v => v.toFixed(3)).join('  '));
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(res, null, 1));
console.log('→', OUT);
