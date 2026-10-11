// w_luecken.js — Kontrolle der Behandlung leerer Relationsstrukturen (Abschnitt 12.9, Abbildung 12).
// Der Zwilling füllt Jahre, in denen eine Relationsstruktur keine aktiven Akteure hat, mit einer
// gleichverteilten Kategorienzusammensetzung (je 25 %). Das Skript ersetzt diese Füllung im geladenen
// Zwilling (nicht in tr-twin.html) durch drei Varianten und vergleicht die vertikale Ungleichheit:
//   orig   unverändert (gleichverteilte Lückenfüllung)
//   fort   (a) letzte beobachtete Zusammensetzung der Struktur fortgeschrieben
//   pool   (b) Gesamtzusammensetzung der Struktur über alle Zeilen der Tabelle in den Lücken
//   konst  (c) Gesamtzusammensetzung in allen Jahren (nur die Mechanik des Zwillings wirkt)
// Fehlende Kategorie zählt wie im Zwilling als Bewahrende.
//
//   NODE_PATH=<jsdom>/node_modules node w_luecken.js [N0_lexikon_hiscam_alte_jahre.csv]
//
// Ausgabe: results/leer_kontrolle.json  (input = Mittel des vertikalen Gini der Eingabe, die in den Jahren
// des Laufs gilt; input_besetzt = dasselbe nur über die Jahre, in denen die Struktur aktive Akteure hat, twin = Mittel des vertikalen Gini im Lauf, dazu 1850, 1900, Ende) und
// results/luecken_reihen.json (Jahresreihen des vertikalen Gini je Variante).
const fs = require('fs'), path = require('path');
const Z = require('./zwilling');
const KAT = ['etabli', 'aspirant', 'conservateur', 'decu'];
const VAL = [3, 2, 1, 0];
const vgini = a => { const s = a.reduce((x, y) => x + y, 0); if (s <= 0) return 0; const p = a.map(v => v / s);
  const m = p.reduce((x, v, c) => x + v * VAL[c], 0); if (m <= 0) return 0; let g = 0;
  for (let c = 0; c < 4; c++) for (let d = 0; d < 4; d++) g += p[c] * p[d] * Math.abs(VAL[c] - VAL[d]); return g / (2 * m); };
function pool(text) {
  const L = text.trim().split(/\r?\n/); const h = L[0].split(',');
  const iS = h.indexOf('structure'), iC = h.indexOf('category'); const n = [0, 1, 2, 3].map(() => [0, 0, 0, 0]);
  for (const l of L.slice(1)) { const r = l.split(','); const x = 'ABCD'.indexOf(r[iS]); if (x < 0) continue;
    const c = KAT.indexOf(r[iC] || 'conservateur'); n[x][c < 0 ? 2 : c]++; }
  return n.map(v => { const s = v.reduce((a, b) => a + b, 0); return v.map(x => s ? x / s : 0.25); });
}
(async () => {
  const f = Z.tabellen(process.argv.slice(2).length ? process.argv.slice(2) : ['N0_lexikon_hiscam_alte_jahre.csv'])[0];
  const res = {}, reihen = {};
  for (const VAR of ['orig', 'fort', 'pool', 'konst']) {
    const { w, text } = await Z.zwillingMit(f);
    const P = pool(text);
    if (VAR !== 'orig') w.eval(`(function(V,P){const ks=tl.keys;for(let x=0;x<4;x++){let last=null;const first=ks.find(k=>k.w[x]>0);
      for(const k of ks){if(k.w[x]>0){last=k.comp[x].slice();continue;}
        if(V==='fort'){const src=last||(first?first.comp[x]:null);if(src)k.comp[x]=src.slice();}
        else if(V==='pool'){k.comp[x]=P[x].slice();}}
      if(V==='konst')for(const k of ks)k.comp[x]=P[x].slice();}})`)(VAR, P);
    const keys = w.eval('tl.keys');
    const rows = w.runSeries();
    const S = Z.zusammenfassung(rows);
    const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
    const kAt = y => { let b = keys[0]; for (const k of keys) { if (k.year <= y) b = k; else break; } return b; };
    res[VAR] = { input: [0, 1, 2, 3].map(x => Z.r3(mean(rows.map(r => vgini(kAt(r.year).comp[x]))))),
      input_besetzt: [0, 1, 2, 3].map(x => { const v = rows.map(r => kAt(r.year)).filter(k => k.w[x] > 0).map(k => vgini(k.comp[x])); return v.length ? Z.r3(mean(v)) : null; }),
      twin: [0, 1, 2, 3].map(x => Z.r3(mean(rows.map(r => r.vGini[x])))),
      y1850: S.y1850.vGini, y1900: S.y1900.vGini, end: S.end.vGini, mean_gini: S.mean_gini, mean_recip: S.mean_recip };
    reihen[VAR] = rows.map(r => ({ y: r.year, v: r.vGini.map(Z.r3) }));
    console.log(VAR.padEnd(6), 'Eingabe', res[VAR].input.join(' '), '| Lauf', res[VAR].twin.join(' '));
    w.close();
  }
  res.tabelle = path.basename(f);
  fs.writeFileSync(path.join(Z.ERGEB, 'leer_kontrolle.json'), JSON.stringify(res, null, 1));
  fs.writeFileSync(path.join(Z.ERGEB, 'luecken_reihen.json'), JSON.stringify(reihen));
})();
