// zwilling.js — lädt den digitalen Zwilling (tr-twin.html im Wurzelordner des Repositoriums)
// ohne Browser (jsdom) und liest Vertragstabellen ein. Gemeinsame Hilfsfunktionen für
// v_zwilling.js, w_luecken.js und x_kanaele.js.
//
// jsdom muss installiert sein (npm install jsdom); liegt es außerhalb dieses Ordners,
// übergibt man seinen Ort mit NODE_PATH=<ordner>/node_modules.
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const BASIS = path.resolve(__dirname, '..');            // data-mode/topic-models
const REPO = path.resolve(BASIS, '..', '..');           // Wurzel des Repositoriums
const TWIN = path.join(REPO, 'tr-twin.html');
const INSTANZEN = path.join(REPO, 'data-mode', 'data', 'instances', 'instances_full_empirical.csv');
const VERTRAG = path.join(BASIS, 'contracts');
const ERGEB = path.join(BASIS, 'results');
fs.mkdirSync(ERGEB, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));
const ctxProxy = new Proxy({}, { get: (o, p) => {
  if (p === 'createRadialGradient' || p === 'createLinearGradient') return () => ({ addColorStop() {} });
  if (p === 'measureText') return () => ({ width: 10 });
  return typeof p === 'string' ? (() => {}) : undefined; } });

async function oeffne() {
  const vc = new VirtualConsole(); const fehler = [];
  vc.on('jsdomError', e => fehler.push(String(e && e.message || e)));
  const dom = new JSDOM(fs.readFileSync(TWIN, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.HTMLCanvasElement.prototype.getContext = () => ctxProxy;
      w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
      w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
    } });
  const w = dom.window; await sleep(150);
  w.__fehler = fehler;
  return w;
}

async function lade(w, id, text, name) {
  const input = w.document.getElementById(id);
  const file = new w.File([text], name, { type: 'text/csv' });
  Object.defineProperty(input, 'files', { value: [file], configurable: true });
  input.dispatchEvent(new w.Event('change'));
  await sleep(120);
}

// Vertragstabelle als Akteurskohorte laden; mitInstanzen: zusätzlich die Vermittlungs- und Kontrollinstanzen
async function zwillingMit(datei, mitInstanzen = false) {
  const w = await oeffne();
  const text = fs.readFileSync(datei, 'utf8');
  await lade(w, 'contractfile', text, 'c.csv');
  if (mitInstanzen) await lade(w, 'instcohortfile', fs.readFileSync(INSTANZEN, 'utf8'), 'i.csv');
  const status = (w.document.getElementById('contractstatus').textContent || '').trim();
  return { w, text, status };
}

const NM = 'ABCD';
const r3 = v => +v.toFixed(3);
const pick = r => ({ year: r.year, S: r.S.map(r3), gini: r3(r.gini), recip: r3(r.recip), vGini: r.vGini.map(r3),
  rRecip: r.rRecip.map(r3), ruler: r.ruler.map(i => NM[i]), sat: r.sat.map(r3) });
function zusammenfassung(rows) {
  const at = y => rows.reduce((b, r) => Math.abs(r.year - y) < Math.abs(b.year - y) ? r : b);
  const mean = k => rows.reduce((s, r) => s + r[k], 0) / rows.length;
  return { years: [rows[0].year, rows[rows.length - 1].year], mean_gini: r3(mean('gini')), mean_recip: r3(mean('recip')),
    y1850: pick(at(1850)), y1900: pick(at(1900)), end: pick(rows[rows.length - 1]) };
}
const pearson = (a, c) => { const n = a.length, ma = a.reduce((s, v) => s + v, 0) / n, mc = c.reduce((s, v) => s + v, 0) / n;
  let num = 0, da = 0, dc = 0; for (let i = 0; i < n; i++) { num += (a[i] - ma) * (c[i] - mc); da += (a[i] - ma) ** 2; dc += (c[i] - mc) ** 2; }
  return da * dc > 0 ? num / Math.sqrt(da * dc) : 0; };

function tabellen(args) {
  if (args.length) return args.map(a => path.isAbsolute(a) || fs.existsSync(a) ? path.resolve(a) : path.join(VERTRAG, a));
  return fs.readdirSync(VERTRAG).filter(f => f.endsWith('.csv')).sort().map(f => path.join(VERTRAG, f));
}

module.exports = { BASIS, REPO, VERTRAG, ERGEB, zwillingMit, zusammenfassung, pearson, tabellen, r3, NM };
