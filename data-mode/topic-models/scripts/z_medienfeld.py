"""z_medienfeld.py — Eintritte in die Medien und in die Kultur über das Jahrhundert (Kapitel 12, Abschnitt 12.11).

Für jede Vertragstabelle und jeden Zeitraum: wie viele Wechsel der Relationsstruktur in die Medien (D) bzw. in die
Kultur (A) führen, gemessen an allen Wechseln, die nicht aus dieser Relationsstruktur kommen; mit welcher
Akteurkategorie, in welche Sequenz und aus welcher Relationsstruktur die Akteure eintreten. Für die Tabelle mit den
Jahren aus den Notizen (N1) zusätzlich je Jahrzehnt der Anteil der Wechsel neben den Vermittlungsinstanzen und der
Kontrollkapazität aus results/course_N1_lexikon_hiscam_echte_jahre.json (x_kanaele.js), mit den Korrelationen der
Niveaus und der Veränderungen von Jahrzehnt zu Jahrzehnt (nur Jahrzehnte mit mindestens drei Wechseln).

  python3 z_medienfeld.py            → results/medienfeld.json
"""
import csv
import json
from collections import Counter, defaultdict

import numpy as np

from pfade import *  # noqa: F401,F403  (BASIS, ergeb, …)

VERTRAG = BASIS + "/contracts/"
TABELLEN = ["N1_lexikon_hiscam_echte_jahre.csv", "N0_lexikon_hiscam_alte_jahre.csv", "N5B_topics_dichtung_regelB.csv"]
PER = [(0, 1850, "vor 1850"), (1850, 1880, "1850–1879"), (1880, 1910, "1880–1909"), (1910, 3000, "ab 1910")]


def per(y):
    return next(lab for a, b, lab in PER if a <= y < b)


def lade(datei):
    by = defaultdict(list)
    with open(VERTRAG + datei, encoding="utf-8") as f:
        for z in csv.DictReader(f):
            by[z["aid"]].append((int(float(z["year"])), z["structure"], z["category"] or "leer", z["sequence"]))
    for a in by:
        by[a].sort(key=lambda t: t[0])
    return by


def eintritte(by, ziel, zeit):
    """Eintritte in die Relationsstruktur ziel und alle Wechsel aus anderen Relationsstrukturen, je Zeitabschnitt."""
    r = {k: defaultdict(Counter) for k in ("kategorie", "sequenz", "herkunft")}
    ein, wechsel = Counter(), Counter()
    for st in by.values():
        for (y1, s1, k1, q1), (y2, s2, k2, q2) in zip(st, st[1:]):
            if s1 == s2:
                continue
            p = zeit(y2)
            if s1 != ziel:
                wechsel[p] += 1
            if s2 == ziel:
                ein[p] += 1
                r["kategorie"][p][k2] += 1
                r["sequenz"][p][ziel + "." + q2] += 1
                r["herkunft"][p][s1] += 1
    return ein, wechsel, r


def main():
    out = {"perioden": {}, "jahrzehnte": {}}
    for t in TABELLEN:
        by = lade(t)
        out["perioden"][t] = {}
        print("\n==", t)
        for z, name in (("D", "Medien"), ("A", "Kultur")):
            ein, w, r = eintritte(by, z, per)
            zeilen = []
            for _, _, p in PER:
                zeilen.append({"zeitraum": p, "eintritte": ein[p], "wechsel": w[p],
                               "anteil": round(ein[p] / w[p], 3) if w[p] else None,
                               "kategorie": dict(r["kategorie"][p]), "sequenz": dict(r["sequenz"][p]),
                               "herkunft": dict(r["herkunft"][p])})
                print(f"  {name:7} {p:10} {ein[p]:3} von {w[p]:3} Wechseln"
                      f" ({100 * ein[p] / w[p] if w[p] else 0:3.0f} %) · {dict(r['kategorie'][p])} · {dict(r['sequenz'][p])}"
                      f" · aus {dict(r['herkunft'][p])}")
            out["perioden"][t][z] = zeilen
    # Jahrzehnte gegen die Instanzen (N1)
    c = json.load(open(ergeb("course_N1_lexikon_hiscam_echte_jahre.json"), encoding="utf-8"))
    Y = np.array(c["years"])
    by = lade("N1_lexikon_hiscam_echte_jahre.csv")
    print("\n== Jahrzehnte (N1): Anteil der Wechsel, Vermittlung, Kontrolle")
    for z, k in (("D", "3"), ("A", "0")):
        ein, w, _ = eintritte(by, z, lambda y: y // 10 * 10)
        reihe = []
        for d in range(1780, 1960, 10):
            m = (Y >= d) & (Y < d + 10)
            reihe.append({"jahrzehnt": d, "eintritte": ein[d], "wechsel": w[d],
                          "anteil": ein[d] / w[d] if w[d] else None,
                          "med": float(np.mean(np.array(c["struct"][k]["med"])[m])),
                          "ctrl": float(np.mean(np.array(c["struct"][k]["ctrl"])[m]))})
        R = np.array([[x["anteil"], x["med"], x["ctrl"]] for x in reihe if x["wechsel"] >= 3], float)
        dR = np.diff(R, axis=0)
        kor = {"niveau_ctrl": float(np.corrcoef(R[:, 0], R[:, 2])[0, 1]), "niveau_med": float(np.corrcoef(R[:, 0], R[:, 1])[0, 1]),
               "aenderung_ctrl": float(np.corrcoef(dR[:, 0], dR[:, 2])[0, 1]), "aenderung_med": float(np.corrcoef(dR[:, 0], dR[:, 1])[0, 1]),
               "n_jahrzehnte": int(len(R))}
        out["jahrzehnte"][z] = {"reihe": reihe, "korrelation": kor}
        print(f"  {z}: Niveaus r(ctrl) {kor['niveau_ctrl']:.2f} r(med) {kor['niveau_med']:.2f} · "
              f"Veränderungen r(ctrl) {kor['aenderung_ctrl']:.2f} r(med) {kor['aenderung_med']:.2f} · {kor['n_jahrzehnte']} Jahrzehnte")
    json.dump(out, open(ergeb("medienfeld.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n→ results/medienfeld.json")


if __name__ == "__main__":
    main()
