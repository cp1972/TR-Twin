# -*- coding: utf-8 -*-
"""Ergänzende Vertragstabellen und Kennzahlen für Kapitel 12.
E1   Lexikon-Positionen, Kategorien nach Zirkulationsregel A, echte Jahre
E2   Topic-Tabelle N3 ohne Kategorien (der Zwilling liest alle Etappen als Bewahrende)
E3   Lexikon-Tabelle N1 ohne Kategorien
N5B  Topic-Positionen + Nebentätigkeit Dichtung als außerberufliche Schicht, Regel B (empfohlene Topic-Tabelle)
circ_mob_v2.json  Zirkulation vs. Mobilität für die überarbeitete Topic-Klassifikation (Abschnitt 12.7.2)
date_diffs.json   echtes Jahr minus bisher geschätztes Jahr für alle datierten Etappen (Abschnitt 12.8.1)
Läuft nach m_contracts.py, q_contracts.py und r_ruleB.py.
"""
from pfade import *
import csv, json, pickle
from collections import Counter
import m_contracts as M
import q_contracts as Q
from r_ruleB import categories_B
from l_dates import stage_years


def ohne_kategorien(src, dst):
    rows = list(csv.reader(open(src, encoding='utf-8')))
    for r in rows[1:]:
        r[3] = ''
    with open(dst, 'w', encoding='utf-8', newline='') as fh:
        csv.writer(fh).writerows(rows)
    return len(rows) - 1


if __name__ == '__main__':
    real = lambda k: M.YEARS[k][0]
    print('E1', M.write(M.LEX, M.circulation_cats(M.LEX), real, vertrag('E1_lexikon_zirkulation_echte_jahre.csv')))
    print('E2', ohne_kategorien(vertrag('N3_topics_ueberarbeitet_echte_jahre.csv'), vertrag('E2_N3_ohne_kategorien.csv')))
    print('E3', ohne_kategorien(vertrag('N1_lexikon_hiscam_echte_jahre.csv'), vertrag('E3_N1_ohne_kategorien.csv')))

    # N5B: Berufe + nur die Dichtung (Topic 2 der Nebentätigkeiten) als außerberufliche Schicht
    dichtung = {(r['e'], 1000 + r['j']) for r in Q.AV if r['topic'] == 'Topic_2'}
    seq = Q.sequences(True)
    for e in seq:
        seq[e] = [x for x in seq[e] if x[4] == 'Beruf' or (e, x[2]) in dichtung]
    seq = {e: v for e, v in seq.items() if v}
    C5, _ = categories_B(seq)
    print('N5B', Q.write(seq, C5, vertrag('N5B_topics_dichtung_regelB.csv')))

    # Zirkulation vs. Mobilität, überarbeitete Topic-Klassifikation
    import n_circ_mob as N
    V2 = pickle.load(open(arbeit('codings_v2.pkl'), 'rb'))
    T = N.transitions(V2['OCC'])
    tab = Counter((t['typ'], t['hiscam']) for t in T)
    agree = Counter((t['intern'], t['hiscam']) for t in T if t['typ'] == 'Strukturwechsel' and t['hiscam'])
    res = {'Topics': dict(n=len(T), n_typ=dict(Counter(t['typ'] for t in T)),
                          tab={f'{a}|{b}': v for (a, b), v in tab.items()},
                          agree={f'{a}|{b}': v for (a, b), v in agree.items()})}
    json.dump(res, open(ergeb('circ_mob_v2.json'), 'w'), ensure_ascii=False, indent=1)
    print('circ_mob_v2', res['Topics']['n_typ'])

    # Abweichung der bisherigen Schätzung
    Y, _ = stage_years()
    d = [Y[k][0] - M.old_year(k) for k in sorted(Y, key=lambda k: (int(k[0]), k[1])) if Y[k][1] in ('text', 'alter')]
    json.dump(d, open(ergeb('date_diffs.json'), 'w'))
    print('date_diffs', len(d), 'davon > 10 Jahre:', round(sum(abs(x) > 10 for x in d) / len(d), 2))
