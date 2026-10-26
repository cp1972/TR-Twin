#!/usr/bin/env node
// run.js — computes a run file of the TR digital twin without a browser, exactly as the interface does.
//
//   node run.js <run file> [--lang de|en|fr] [--out <folder>]
//
// The run file names the mode, the theory profiles or the contract table, the time axis and the seeds (see
// runs/ for examples, document 4 for the keys). Paths in the run file are relative to the run file. The results
// go to the folder named by the key "output" or by --out, by default results/<name of the run file>/:
//   report.html  — the run file, all tables and all figures in one file
//   tables.csv   — all tables; tables/<table>.csv one per table
//   series.csv   — the yearly (or stepwise) series of every run, to compute your own trends
//   figures/*.svg
// Installation once, in this folder: npm install   (needs Node.js, https://nodejs.org)
const fs = require('fs');
const path = require('path');
let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch (e) { console.error('jsdom is missing. In this folder, run once:  npm install'); process.exit(1); }

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const LANG = (opt('--lang', 'en') || 'en').toLowerCase();
const OUTARG = opt('--out', null);
const RUN = args[0];
if (!RUN || args.length > 1 || /\.html?$/i.test(RUN)) {
  console.error('usage: node run.js <run file> [--lang de|en|fr] [--out <folder>]');
  if (/\.html?$/i.test(RUN || '')) console.error('(the scripts of v67 — run.js <app.html> <profile.csv> — are in simulation-mode/scripts/runs/)');
  process.exit(1); }
if (!fs.existsSync(RUN)) { console.error('run file not found: ' + RUN); process.exit(1); }
const runPath = path.resolve(RUN), runDir = path.dirname(runPath), runText = fs.readFileSync(runPath, 'utf8');
const TWIN = path.join(__dirname, 'tr-twin.html');

const ctx = new Proxy({}, { get: (o, p) => { if (p === 'createRadialGradient' || p === 'createLinearGradient') return () => ({ addColorStop() {} });
  if (p === 'measureText') return () => ({ width: 10 }); return typeof p === 'string' ? (() => {}) : undefined; } });
const dom = new JSDOM(fs.readFileSync(TWIN, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true,
  beforeParse(w) { w.HTMLCanvasElement.prototype.getContext = () => ctx; w.requestAnimationFrame = () => 0; w.cancelAnimationFrame = () => {};
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }); } });
const w = dom.window;
// runs code in the page; an error inside the page stops with its message (not with a later, unrelated one)
const inPage = (code, data) => { w.__in = data; w.__out = undefined; const s = w.document.createElement('script');
  s.textContent = 'window.__out=(function(D){try{' + code + '}catch(e){return {__error:String(e&&e.message||e)};}})(window.__in);';
  w.document.body.appendChild(s); s.remove();
  const r = w.__out; if (r === undefined) { console.error('error: the twin could not run the code (see above)'); process.exit(1); }
  if (r && r.__error) { console.error('error: ' + r.__error); process.exit(1); } return r; };

const parsed = inPage('setLang(D.lang);return parseRunFile(D.text);', { lang: LANG, text: runText });
for (const m of parsed.warnings) console.log('note:', m);
if (parsed.errors.length) { for (const m of parsed.errors) console.error('error:', m); process.exit(1); }
const names = inPage('return runFileNames(D);', parsed.spec), files = {};
for (const n of names) { const p = path.resolve(runDir, n);
  if (!fs.existsSync(p)) { console.error('file not found: ' + n + '  (looked for ' + p + ')'); process.exit(1); }
  files[n] = fs.readFileSync(p, 'utf8'); }
const spec = parsed.spec;
for (const m of inPage('return r68ProfileWarnings(D.spec,D.files);', { spec: parsed.spec, files })) console.log('note:', m);
console.log(`run file: ${path.basename(runPath)} · ${spec.mode === 'data' ? 'data · ' + spec.contracts : 'simulation · TR + ' + spec.profiles.length + ' theor' + (spec.profiles.length === 1 ? 'y' : 'ies')} · seeds ${spec.seeds.join(',')}`);
const t0 = Date.now();
const out = inPage(`const res=r68Run(D.spec,D.files,(i,n)=>{window.__prog&&window.__prog(i,n);});const sm=r68Summary(res);const figs=r68Figures(res,sm);
  return {tables:sm.tables.map(tb=>({id:tb.id,title:tb.title,csv:r68CSV(tb)})),all:r68AllCSV(sm),series:r68SeriesCSV(res),
    figs:figs.map(f=>({name:f.name,svg:f.svg})),report:r68Report(res,sm,figs,D.name,D.text)};`,
  { spec, files, name: path.basename(runPath), text: runText });
const dir = path.resolve(OUTARG ? OUTARG : (spec.output ? path.resolve(runDir, spec.output) : path.join('results', path.basename(runPath).replace(/\.[^.]*$/, ''))));
fs.mkdirSync(path.join(dir, 'tables'), { recursive: true }); fs.mkdirSync(path.join(dir, 'figures'), { recursive: true });
const bom = '﻿';
fs.writeFileSync(path.join(dir, 'report.html'), out.report);
fs.writeFileSync(path.join(dir, 'tables.csv'), bom + out.all);
fs.writeFileSync(path.join(dir, 'series.csv'), bom + out.series);
for (const tb of out.tables) fs.writeFileSync(path.join(dir, 'tables', tb.id + '.csv'), bom + tb.csv);
for (const f of out.figs) fs.writeFileSync(path.join(dir, 'figures', f.name + '.svg'), f.svg);
console.log(`computed in ${((Date.now() - t0) / 1000).toFixed(1)} s → ${dir}`);
console.log('  report.html · tables.csv · series.csv · tables/ (' + out.tables.length + ') · figures/ (' + out.figs.length + ')');
