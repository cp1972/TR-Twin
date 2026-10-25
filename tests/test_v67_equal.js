// v68 must compute exactly what v67 computes on its deterministic paths.
//   node tests/test_v67_equal.js <v67.html> [v68.html]
// (1) steps: the pipeline's way (__setze + N steps) for every profile, seeds 1–2
// (2) years: run.js's way (profile over its years, runSeries) for three profiles
// (3) data: the import field "actor cohort" + runSeries (chapter 12), with and without the instance table
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const REPO = path.resolve(__dirname, '..');
const V67 = process.argv[2], V68 = process.argv[3] || path.join(REPO, 'tr-twin.html');
const ctx = new Proxy({}, { get: (o, p) => { if (p === 'createRadialGradient' || p === 'createLinearGradient') return () => ({ addColorStop() {} });
  if (p === 'measureText') return () => ({ width: 10 }); return typeof p === 'string' ? (() => {}) : undefined; } });
function open(file) { const dom = new JSDOM(fs.readFileSync(file, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true,
  beforeParse(w) { w.HTMLCanvasElement.prototype.getContext = () => ctx; w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }); } });
  const w = dom.window; w.__run = c => { const s = w.document.createElement('script'); s.textContent = 'window.__o=(function(){' + c + '})();'; w.document.body.appendChild(s); s.remove(); return w.__o; };
  return w; }
const prof = d => fs.readdirSync(d).filter(f => f.endsWith('.csv')).sort().map(f => path.join(d, f));
const PROFILES = prof(path.join(REPO, 'simulation-mode', 'profiles'));
const CONTRACTS = path.join(REPO, 'data-mode', 'topic-models', 'contracts');
const INST = path.join(REPO, 'data-mode', 'data', 'instances', 'instances_full_empirical.csv');
let bad = 0, n = 0;
function same(a, b, what) { n++; const ja = JSON.stringify(a), jb = JSON.stringify(b); if (ja !== jb) { bad++; console.log('DIFF', what, ja.slice(0, 160), '|', jb.slice(0, 160)); } }
const pick = r => ({ S: r.S, gini: r.gini, recip: r.recip, ruler: r.ruler, sat: r.sat, rGini: r.rGini, vGini: r.vGini, rRecip: r.rRecip });

// (1) steps
for (const p of (process.env.QUICK ? [] : PROFILES.concat([null]))) for (const sd of [1, 2]) {
  const csv = p ? fs.readFileSync(p, 'utf8') : null;
  const w7 = open(V67);
  const ref = w7.__run(`seed=${sd};applyDefaults();let ch=null;const csv=${JSON.stringify(csv)};
    if(csv){const r=parseCursorCSV(csv);for(const cid in r.keys){const p=r.keys[cid];const el=document.getElementById(cid);if(el){el.value=p[p.length-1].val;el.dispatchEvent(new Event('input'));}}
      if(r.chains&&Object.keys(r.chains).length)ch=r.chains;profilMech(r);}
    if(ch){loadedChains=ch;for(const sx in ch)setChain(+sx,ch[sx]);}else{loadedChains=null;resetChains();}
    satS=[0,0,0,0];rulerHold=[0,0,0,0];boost=-1;reset();for(let i=0;i<1819;i++)step(1/60*0.68);
    return {S:S.slice(),gini:gini(),recip:reciprocity(),ruler:ruler.slice(),sat:satS.slice()};`);
  const w8 = open(V68);
  const got = w8.__run(`const files={};const csv=${JSON.stringify(csv)};if(csv)files['p.csv']=csv;
    const spec=parseRunFile('mode,simulation\\n'+(csv?'profile,p.csv\\n':'')+'steps,1819\\nseeds,${sd}\\nthresholds,no\\nprobe,no').spec;
    const res=r68Run(spec,files);const run=res.runs[res.runs.length-1];const r=run.rows[run.rows.length-1];
    return {S:r.S,gini:r.gini,recip:r.recip,ruler:r.ruler,sat:r.sat};`);
  same(ref, got, 'steps ' + (p ? path.basename(p) : 'TR') + ' seed ' + sd);
}
// (2) years
for (const p of PROFILES.slice(0, 3)) {
  const csv = fs.readFileSync(p, 'utf8');
  const ref = open(V67).__run(`const r=parseCursorCSV(${JSON.stringify(csv)});tl.cursorKeys=r.keys;
    if(r.chains&&Object.keys(r.chains).length){loadedChains=r.chains;for(const sx in r.chains)setChain(+sx,r.chains[sx]);}profilMech(r);
    const ys=r.years.filter(y=>!isNaN(y));tl.start=Math.min(...ys);tl.end=Math.max(...ys);return runSeries();`);
  const ys = csv.split(/\r?\n/)[0].split(',').slice(1).map(Number).filter(v => !isNaN(v));
  const got = open(V68).__run(`const spec=parseRunFile('mode,simulation\\nprofile,p.csv\\nseeds,1\\nstart,${Math.min(...ys)}\\nend,${Math.max(...ys)}\\nthresholds,no\\nprobe,no').spec;
    const res=r68Run(spec,{'p.csv':${JSON.stringify(csv)}});return res.runs[1].rows;`);
  same(ref.map(pick), got.map(pick), 'years ' + path.basename(p));
}
// (3) data
async function data() {
  const COH = path.join(REPO, 'data-mode', 'data', 'actors', 'cohorte_contrat.csv'), PROBE = path.join(REPO, 'data-mode', 'data', 'instances', 'instances_probe_demo.csv');
  for (const [f, inst] of [['N1_lexikon_hiscam_echte_jahre.csv', false], ['N5B_topics_dichtung_regelB.csv', false], ['N1_lexikon_hiscam_echte_jahre.csv', true], [COH, false], [COH, 'probe']]) {
    const text = fs.readFileSync(path.isAbsolute(f) ? f : path.join(CONTRACTS, f), 'utf8'), itext = fs.readFileSync(inst === 'probe' ? PROBE : INST, 'utf8');
    const w7 = open(V67);
    const load = (id, t) => { const input = w7.document.getElementById(id); const file = new w7.File([t], 'x.csv', { type: 'text/csv' });
      Object.defineProperty(input, 'files', { value: [file], configurable: true }); input.dispatchEvent(new w7.Event('change')); };
    load('contractfile', text); await new Promise(r => setTimeout(r, 300));
    if (inst) { load(inst === 'probe' ? 'probefile' : 'instcohortfile', itext); await new Promise(r => setTimeout(r, 300)); }
    const ref = w7.__run('return runSeries();');
    const got = open(V68).__run(`const spec=parseRunFile('mode,data\\ncontracts,c.csv${inst === 'probe' ? '\\nprobes,i.csv' : (inst ? '\\ninstances,i.csv' : '')}').spec;
      return r68Run(spec,{'c.csv':${JSON.stringify(text)},'i.csv':${JSON.stringify(itext)}}).runs[0].rows;`);
    same(ref.map(pick), got.map(pick), 'data ' + path.basename(f) + (inst === 'probe' ? ' + probes' : (inst ? ' + instances' : '')));
  }
  console.log(`${n - bad}/${n} identical`); process.exit(bad ? 1 : 0);
}
data();
