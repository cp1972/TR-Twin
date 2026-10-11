# -*- coding: utf-8 -*-
"""Nachgebesserte Topic-Vertragstabellen.
N3  Berufsetappen, überarbeitete Zuordnung (gemischte Topics per Untermodell getrennt), echte Jahre
N4  N3 + datierte Nebentätigkeiten als außerberufliche Schicht (nach Jahr eingeordnet)
Kategorien jeweils nach der Zirkulationsregel, berechnet auf der vollständigen Folge der Positionen.
"""
from pfade import *
import csv, pickle
from collections import defaultdict, Counter
from common import STG, ACT
from l_dates import stage_years

YEARS, _ = stage_years()
D = pickle.load(open(arbeit('two_stage.pkl'), 'rb')); s1, REST, idx, det, U = D['s1'], D['REST'], D['idx'], D['det'], D['U']
SPL = pickle.load(open(arbeit('splits.pkl'), 'rb'))
AV = pickle.load(open(arbeit('avoc_rows.pkl'), 'rb'))
d1 = s1['documents']; d2 = det[6]['documents']; sub = dict(zip(idx, range(len(idx))))

# Unterthemen der gemischten Topics (K = 2, Konsens): Dokumentindex -> (Unterthema, stabil)
def split_map(name, K=2):
    ix, dt = SPL[name]; r = dt[K]['documents']
    return {j: (int(t.split('_')[1]) if t else None, bool(st)) for j, t, st in zip(ix, r['Consensus topic'], r['Stable'])}
SP_T1, SP_T2, SP_S5 = split_map('T1 Lehre/Druck'), split_map('T2 Presse'), split_map('S5 Dozent/Propagandist')

POS = {  # überarbeitete Zuordnung
    'T0': ('C', 'D'),                      # Laufjunge, Laden, Botengänge
    'T1-0': ('C', 'C'), 'T1-1': ('A', 'C'),  # Handwerkslehre | Druck- und Buchgewerbe
    'T2-0': ('D', 'A'), 'T2-1': ('A', 'A'),  # Journalismus | Autorschaft
    'S0': ('D', 'D'), 'S1': ('A', 'A'), 'S2': ('C', 'D'), 'S3': ('C', 'C'), 'S4': ('B', 'D'),
    'S5-0': ('B', 'D'), 'S5-1': ('A', 'A'),  # Propaganda | Universität
}
AVPOS = {0: ('A', 'A'), 1: ('B', 'B'), 2: ('A', 'A'), 3: ('B', 'D'), 4: ('A', 'B')}
AVNAME = {0: 'Vereine, Selbstbildung', 1: 'Parteien', 2: 'Dichtung', 3: 'Gewerkschaft, Verbandsamt', 4: 'Sonntagsschule, Predigt'}

OCC, OCCLAB = {}, {}
for j, (e, i, _) in enumerate(U):
    k = (e, i); OCC[k] = ('', ''); OCCLAB[k] = ''
    ct = d1['Consensus topic'][j]
    if not ct or not d1['Stable'][j]: continue
    t = int(ct.split('_')[1])
    if t == 0: lab = 'T0'
    elif t in (1, 2):
        u, st = (SP_T1 if t == 1 else SP_T2)[j]
        if u is None or not st: continue
        lab = f'T{t}-{u}'
    else:
        r = d2.iloc[sub[j]]
        if not r['Consensus topic'] or not r['Stable']: continue
        s = int(r['Consensus topic'].split('_')[1])
        if s == 5:
            u, st = SP_S5[j]
            if u is None or not st: continue
            lab = f'S5-{u}'
        else:
            lab = f'S{s}'
    OCC[k] = POS[lab]; OCCLAB[k] = lab

CATS = ['Etablierte', 'Anwaerter', 'Bewahrende', 'Enttaeuschte']
CATFR = {'Etablierte': 'etabli', 'Anwaerter': 'aspirant', 'Bewahrende': 'conservateur', 'Enttaeuschte': 'decu'}


def sequences(with_avoc):
    """je Akteur: Liste (jahr, art, schlüssel, position) in zeitlicher Folge"""
    seq = defaultdict(list)
    for (e, i), p in OCC.items():
        if p[0]: seq[e].append((YEARS[(e, i)][0], 0, i, p, 'Beruf'))
    if with_avoc:
        for r in AV:
            if r['year'] and r['stable'] and r['topic']:
                a = int(r['topic'].split('_')[1])
                seq[r['e']].append((r['year'], 1, 1000 + r['j'], AVPOS[a], 'Nebentätigkeit'))
    for e in seq: seq[e].sort()
    return seq


def categories(seq):
    inn, out = Counter(), Counter()
    for e, v in seq.items():
        path = [''.join(x[3]) for x in v]
        path = [p for j, p in enumerate(path) if j == 0 or p != path[j - 1]]
        for a, b in zip(path, path[1:]): out[a] += 1; inn[b] += 1
    val = {p: (inn[p] - out[p]) / (inn[p] + out[p]) for p in set(inn) | set(out)}
    cats = {}
    for e, v in seq.items():
        if len(v) < 2: continue
        prev = None
        for j, x in enumerate(v):
            c = x[3]
            if j + 1 < len(v):
                n = v[j + 1][3]
                cat = (CATS[2] if n == c else CATS[1] if n[0] == c[0]
                       else CATS[0] if val.get(''.join(n), 0) >= val.get(''.join(c), 0) else CATS[3])
            else:
                cat = CATS[0] if prev == CATS[0] else CATS[2]
            cats[(e, x[2])] = cat; prev = cat
    return cats, val


def write(seq, cats, path):
    rows = [[e, x[0], x[3][0], CATFR.get(cats.get((e, x[2]), ''), ''), x[3][1]] for e, v in seq.items() for x in v]
    rows.sort(key=lambda r: (int(r[0]), r[1]))
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(['aid', 'year', 'structure', 'category', 'sequence']); w.writerows(rows)
    c = Counter(r[2] for r in rows)
    return len(rows), len({r[0] for r in rows}), {k: round(c[k] / len(rows), 3) for k in 'ABCD'}


if __name__ == '__main__':
    S3 = sequences(False); C3, V3 = categories(S3)
    S4 = sequences(True); C4, V4 = categories(S4)
    print('N3', write(S3, C3, vertrag('N3_topics_ueberarbeitet_echte_jahre.csv')))
    print('N4', write(S4, C4, vertrag('N4_topics_ueberarbeitet_mit_nebentaetigkeiten.csv')))
    print('Etappen je Label', Counter(v for v in OCCLAB.values() if v))
    print('Attraktivität N3', {k: round(v, 2) for k, v in sorted(V3.items())})
    print('Attraktivität N4', {k: round(v, 2) for k, v in sorted(V4.items())})
    pickle.dump(dict(OCC=OCC, OCCLAB=OCCLAB, C3=C3, C4=C4, V3=V3, V4=V4), open(arbeit('codings_v2.pkl'), 'wb'))
