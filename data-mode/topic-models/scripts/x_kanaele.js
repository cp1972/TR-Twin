// x_kanaele.js — transversale Kanäle (Kapitel 11, Abschnitt 11.4.4; Kapitel 12, Abschnitt 12.10.2, Abbildung 13).
// Lädt eine Vertragstabelle zusammen mit den Vermittlungs- und Kontrollinstanzen
// (data-mode/data/instances/instances_full_empirical.csv) in den Zwilling und schreibt die Jahresreihen
// Präsenz / Vermittlung / Kontrolle / Reziprozität / Sättigung je Relationsstruktur.
// Präsenz = Zahl der Akteure, die ihre Laufbahn bis zum Jahr begonnen haben und deren letzte Etappe
// bis dahin in der Struktur liegt. Korrelationen über die Jahre mit Präsenz > 0, für die Niveaus und
// für die Zehnjahresänderungen (Kopplung jenseits des gemeinsamen Zeittrends).
//
//   NODE_PATH=<jsdom>/node_modules node x_kanaele.js [N1_lexikon_hiscam_echte_jahre.csv N0_lexikon_hiscam_alte_jahre.csv]
//
// Ausgabe: results/course_<tabelle>.json (Format wie daten/course.json des Buches; mit N0 ergibt sich
// daten/course.json, mit N1 daten/course_echte_jahre.json) und results/kanaele.json.
const fs = require('fs'), path = require('path');
const Z = require('./zwilling');
(async () => {
  const args = process.argv.slice(2);
  const files = Z.tabellen(args.length ? args : ['N0_lexikon_hiscam_alte_jahre.csv', 'N1_lexikon_hiscam_echte_jahre.csv']);
  const ziel = path.join(Z.ERGEB, 'kanaele.json');
  const out = fs.existsSync(ziel) ? JSON.parse(fs.readFileSync(ziel, 'utf8')) : {};
  for (const f of files) {
    const { w, text } = await Z.zwillingMit(f, true);
    const rows = w.runSeries(); const years = rows.map(r => r.year);
    const aby = w.buildCohortByActor(w.parseContractCSV(text));
    const presAt = Y => { const c = [0, 0, 0, 0]; for (const a in aby) { const st = aby[a]; if (Y < st[0].year) continue;
      let s = st[0].s; for (const r of st) { if (r.year <= Y) s = r.s; else break; } c[s]++; } return c; };
    const full = fs.readFileSync(path.join(Z.REPO, 'data-mode', 'data', 'instances', 'instances_full_empirical.csv'), 'utf8');
    const iby = w.buildCohortByActor(w.parseContractCSV(full));
    const medAt = Y => { const m = [0, 0, 0, 0]; for (const a in iby) { const st = iby[a]; if (st[0].ctrl) continue;
      const wv = w.probeWeightAt(st, Y); if (wv == null) continue; const s = st[0].s; if (wv > m[s]) m[s] = wv; } return m; };
    const CRS = { years, struct: {} };
    for (const x of [0, 1, 2, 3]) CRS.struct[x] = { presence: [], med: [], ctrl: [], recip: [], sat: [] };
    rows.forEach(r => { const Y = r.year, pr = presAt(Y), md = medAt(Y), cc = w.controlCapacity(Y).floor;
      for (let x = 0; x < 4; x++) { const s = CRS.struct[x]; s.presence.push(pr[x]); s.med.push(md[x]); s.ctrl.push(cc[x]); s.recip.push(r.rRecip[x]); s.sat.push(r.sat[x]); } });
    const name = path.basename(f).replace('.csv', '');
    fs.writeFileSync(path.join(Z.ERGEB, 'course_' + name + '.json'), JSON.stringify(CRS));
    const res = { years: [years[0], years[years.length - 1]] };
    const d10 = a => a.slice(10).map((v, i) => v - a[i]);
    for (const x of [0, 3]) {
      const s = CRS.struct[x]; const idx = s.presence.map((v, i) => v > 0 ? i : -1).filter(i => i >= 0);
      const P = idx.map(i => s.presence[i]), M = idx.map(i => s.med[i]), C = idx.map(i => s.ctrl[i]);
      const pmax = Math.max(...s.presence);
      res['ABCD'[x]] = { r_med: Z.r3(Z.pearson(P, M)), r_ctrl: Z.r3(Z.pearson(P, C)),
        r_med_10j: Z.r3(Z.pearson(d10(P), d10(M))), r_ctrl_10j: Z.r3(Z.pearson(d10(P), d10(C))),
        n_jahre: idx.length, erste_praesenz: years[idx[0]], hoehepunkt: years[s.presence.indexOf(pmax)], pmax };
    }
    out[path.basename(f)] = res;
    console.log(path.basename(f), 'A', JSON.stringify(res.A), '\n   D', JSON.stringify(res.D));
    w.close();
  }
  fs.writeFileSync(ziel, JSON.stringify(out, null, 1));
})();
