// TR-Twin headless: lädt die Web-App in jsdom, wendet ein Profil an, spielt den Lauf durch.
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const APP = process.argv[2] || '/home/claude/TR-Twin-extract/tr-twin.html';
const PROFILE = process.argv[3] || '/home/claude/TR-Twin-extract/examples/theories-simul/profil_Emirbayer.csv';

const html = fs.readFileSync(APP, 'utf8');
const profileCsv = fs.readFileSync(PROFILE, 'utf8');

// --- Canvas-Stub: jede Methode ist ein No-op, verkettbar ---
const ctxStub = new Proxy({}, { get: () => (() => ctxStub), set: () => true });

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(window) {
    window.HTMLCanvasElement.prototype.getContext = () => ctxStub;
    window.requestAnimationFrame = () => 0;   // Loop nicht starten
    window.cancelAnimationFrame = () => {};
    if (!window.matchMedia) window.matchMedia = () => ({ matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
  }
});

// Code im Seiten-Kontext ausführen (Zugriff auf let-Globals wie tl, runSeries, parseCursorCSV)
function runInPage(code) {
  const s = dom.window.document.createElement('script');
  s.textContent = code;
  dom.window.document.body.appendChild(s);
  s.remove();
}

runInPage(`window.__result = (function(){
  try {
    const r = parseCursorCSV(${JSON.stringify(profileCsv)});
    if(!r) return {ok:false, err:'Profil nicht geparst'};
    tl.cursorKeys = r.keys;
    if(r.chains && Object.keys(r.chains).length){ loadedChains=r.chains; for(const sx in r.chains) setChain(+sx, r.chains[sx]); }
    const ys = r.years.filter(y=>!isNaN(y));
    tl.start = Math.min(...ys); tl.end = Math.max(...ys);
    const rows = runSeries();
    return {ok:true, cursors:Object.keys(r.keys), start:tl.start, end:tl.end, n:rows.length, rows:rows};
  } catch(e){ return {ok:false, err:String((e&&e.stack)||e)}; }
})();`);

const res = dom.window.__result;
if (!res || !res.ok) { console.error('ERROR:', res && res.err); process.exit(1); }

console.log('Profile:', path.basename(PROFILE));
console.log('Cursors loaded:', res.cursors.join(', '));
console.log('Period:', res.start, '→', res.end, '·', res.n, 'years');
const f = res.rows[0], l = res.rows[res.rows.length-1];
const fmt = r => `  year ${r.year}: sizes A/B/C/D=${r.S.map(v=>v.toFixed(2)).join('/')}  gini=${r.gini.toFixed(3)}  reciprocity=${r.recip.toFixed(3)}  ruler=${r.ruler.join('')}  satS=${r.sat.map(v=>v.toFixed(2)).join('/')}`;
console.log('start:'); console.log(fmt(f));
console.log('end:  '); console.log(fmt(l));

// Vollständige Zeitreihe als JSON ablegen (für das Python-Rendering)
const outDir = process.argv[4] || './out';
fs.mkdirSync(outDir, { recursive: true });
const base = path.basename(PROFILE).replace(/^profil_/, '').replace(/\.csv$/, '');
fs.writeFileSync(path.join(outDir, base + '.json'), JSON.stringify(res.rows));
console.log('→ series written:', path.join(outDir, base + '.json'));
