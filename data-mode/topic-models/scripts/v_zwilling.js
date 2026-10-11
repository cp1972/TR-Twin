// v_zwilling.js — lädt Vertragstabellen in den digitalen Zwilling und fasst den deterministischen Lauf zusammen
// (Abschnitt 12.8, Tabelle der Läufe). Ohne Argumente: alle Tabellen in contracts/.
//
//   NODE_PATH=<jsdom>/node_modules node v_zwilling.js [N0_lexikon_hiscam_alte_jahre.csv ...]
//
// Ausgabe: results/zwilling_laeufe.json (je Tabelle: Status der Einlesung, mittlerer Gini und mittlere
// Reziprozität über den Lauf, Zustand 1850, 1900 und am Ende).
const fs = require('fs'), path = require('path');
const Z = require('./zwilling');
(async () => {
  const ziel = path.join(Z.ERGEB, 'zwilling_laeufe.json');
  const out = fs.existsSync(ziel) ? JSON.parse(fs.readFileSync(ziel, 'utf8')) : {};
  for (const f of Z.tabellen(process.argv.slice(2))) {
    const { w, status } = await Z.zwillingMit(f);
    const rows = w.runSeries();
    out[path.basename(f)] = { status, errors: w.__fehler.slice(0, 2), ...Z.zusammenfassung(rows) };
    const o = out[path.basename(f)];
    console.log(path.basename(f).padEnd(48), 'Reziprozität', o.mean_recip, 'Gini', o.mean_gini, '| 1900 S', o.y1900.S.join(' '), '| Ende S', o.end.S.join(' '));
    w.close();
  }
  fs.writeFileSync(ziel, JSON.stringify(out, null, 1));
})();
