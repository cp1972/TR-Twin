# -*- coding: utf-8 -*-
"""Rangordnung aus der Zirkulation und statische vertikale Ungleichheit (Kapitel 12, Abschnitt 12.7).

1  Netto-Attraktivität jeder Position (Struktur.Sequenz) der Lexikon-Kodierung,
   (Zuflüsse − Abflüsse) / (Zuflüsse + Abflüsse), gegen ihren mittleren HISCAM-Wert;
   Spearmans ρ über die Positionen mit mindestens drei HISCAM-Werten und drei Wechseln (Abbildung 7).
2  Statische vertikale Ungleichheit je Relationsstruktur (alle Jahre zusammengefasst, nur Etappen mit
   Kategorie; Formeln des Zwillings) für die HISCAM-Regel (N1), die Zirkulationsregel A (E1) und
   die Zirkulationsregel B (E1B) bei gleicher Lexikon-Zuordnung (Abbildung 9).
3  Übereinstimmung der Regeln A und B mit der HISCAM-Regel je Berufsetappe (Cohens κ).

Läuft nach m_contracts.py, r_ruleB.py und t_ergaenzungen.py. Ausgabe: results/rangordnung.json
"""
from pfade import *
import csv, json, statistics
from collections import defaultdict
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
import m_contracts as M

VAL = [3, 2, 1, 0]
CI = {'etabli': 0, 'aspirant': 1, 'conservateur': 2, 'decu': 3}
SI = {c: i for i, c in enumerate('ABCD')}


def vertikal(path):
    """Vertikaler Gini je Struktur: Gini der Kategorien je Sequenz, gewichtet mit dem Anteil der Sequenz."""
    cnt = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['structure'] and r['sequence'] and r['category']:
            cnt[SI[r['structure']]][SI[r['sequence']]][CI[r['category']]] += 1
    out = []
    for x in range(4):
        tot = sum(map(sum, cnt[x])); num = den = 0.0
        for s in range(4):
            n = sum(cnt[x][s])
            if not n: continue
            m = n / tot; a = [v / n for v in cnt[x][s]]; mean = sum(a[c] * VAL[c] for c in range(4)); den += m
            if mean < 1e-9: continue
            num += m * sum(a[c] * a[d] * abs(VAL[c] - VAL[d]) for c in range(4) for d in range(4)) / (2 * mean)
        out.append(round(num / den, 3) if den else 0.0)
    return dict(zip('ABCD', out))


if __name__ == '__main__':
    R = {}
    # 1 Rangordnung
    val, inn, out = M.circulation_values(M.LEX)
    cam = defaultdict(list)
    for s in M.STG:
        p = ''.join(M.LEX[(s['entry_id'], int(s['stage_index']))])
        if p and s['hiscam']: cam[p].append(float(s['hiscam']))
    P = sorted(p for p in val if len(cam[p]) >= 3 and inn[p] + out[p] >= 3)
    rho, pv = spearmanr([val[p] for p in P], [statistics.mean(cam[p]) for p in P])
    R['positionen'] = {p: {'attraktivitaet': round(val[p], 2), 'zufluesse': inn[p], 'abfluesse': out[p],
                           'hiscam_mittel': round(statistics.mean(cam[p]), 1) if cam[p] else None,
                           'im_vergleich': p in P} for p in sorted(val)}
    R['spearman'] = {'rho': round(rho, 3), 'p': round(pv, 4), 'n': len(P)}
    print(f'Spearman ρ = {rho:.3f} (p = {pv:.4f}, n = {len(P)})')

    # 2 statische vertikale Ungleichheit
    R['vertikal_statisch'] = {
        'HISCAM-Regel (N1)': vertikal(vertrag('N1_lexikon_hiscam_echte_jahre.csv')),
        'Regel A (E1)': vertikal(vertrag('E1_lexikon_zirkulation_echte_jahre.csv')),
        'Regel B (E1B)': vertikal(vertrag('E1B_lexikon_regelB.csv'))}
    for k, v in R['vertikal_statisch'].items(): print(f'{k:<18}', v)

    # 3 κ je Etappe gegen die HISCAM-Regel (gleiche Lexikon-Zuordnung, gleiche Etappen)
    from r_ruleB import categories_B
    seq = {e: [(M.YEARS[(e, int(s['stage_index']))][0], 0, int(s['stage_index']), M.LEX[(e, int(s['stage_index']))], 'Beruf')
               for s in M.stages_by[e] if M.LEX[(e, int(s['stage_index']))][0]] for e in M.ids}
    CB, _ = categories_B(seq)
    CA = M.circulation_cats(M.LEX)
    R['kappa'] = {}
    for name, C in (('Regel A', CA), ('Regel B', CB)):
        ks = [k for k in C if M.HCAT.get(k) and C[k]]
        R['kappa'][name] = {'kappa': round(cohen_kappa_score([M.HCAT[k] for k in ks], [C[k] for k in ks]), 3),
                            'uebereinstimmung': round(sum(M.HCAT[k] == C[k] for k in ks) / len(ks), 3), 'n': len(ks)}
        print(name, 'gegen HISCAM-Regel', R['kappa'][name])
    json.dump(R, open(ergeb('rangordnung.json'), 'w'), ensure_ascii=False, indent=1)
