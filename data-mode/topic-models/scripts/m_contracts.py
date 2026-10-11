# -*- coding: utf-8 -*-
"""Neue Vertragstabellen mit echten Jahren.
N0  Lexikon + HISCAM-Kategorien, bisherige geschätzte Jahre (= veröffentlichte Tabelle)
N1  Lexikon + HISCAM-Kategorien, echte Jahre
N2  zweistufige Topic-Klassifikation (Konsens, nur stabile Etappen) -> Struktur.Sequenz nach Vorschlag,
    Kategorien nach Zirkulationsregel, echte Jahre; jede Laufbahn beginnt bei der ersten erkennbaren Tätigkeit
"""
from pfade import *
import csv, pickle, os
from collections import defaultdict, Counter
from common import STG, ACT
from lexcode import lex
from l_dates import stage_years

YEARS, STEP = stage_years()
ids = sorted(ACT, key=int)
stages_by = defaultdict(list)
for s in STG: stages_by[s['entry_id']].append(s)
for e in stages_by: stages_by[e].sort(key=lambda s: int(s['stage_index']))
CATS = ['Etablierte', 'Anwaerter', 'Bewahrende', 'Enttaeuschte']
CATFR = {'Etablierte': 'etabli', 'Anwaerter': 'aspirant', 'Bewahrende': 'conservateur', 'Enttaeuschte': 'decu'}

# ---- Lexikon + HISCAM (wie veröffentlicht)
LEX = {}
for s in STG:
    st, sq, _ = lex(s['occupation_raw']); LEX[(s['entry_id'], int(s['stage_index']))] = (st, sq)
HCAT = {(s['entry_id'], int(s['stage_index'])): s['tr_absolute'] for s in STG}

# ---- zweistufige Topic-Klassifikation -> Struktur.Sequenz (Vorschlag aus dem Bericht, Tabelle 5)
D = pickle.load(open(arbeit('two_stage.pkl'), 'rb'))
s1, REST, idx, det, U = D['s1'], D['REST'], D['idx'], D['det'], D['U']
BASE_POS = {0: ('C', 'D'),   # Laufjunge, Laden, Botengänge
            1: ('C', 'C'),   # Lehre, Handwerk, Druck (gemischt; hier als Handwerk)
            2: ('D', 'A')}   # Presse, Journalismus
SUB_POS = {0: ('D', 'D'),    # Redakteur
           1: ('A', 'A'),    # Lehrer
           2: ('C', 'D'),    # Büro
           3: ('C', 'C'),    # Fabrikarbeit (employed ...)
           4: ('B', 'D'),    # Gewerkschaft, Sekretär
           5: ('B', 'D')}    # Dozent, Propagandist (gemischt; hier politisch)
d1 = s1['documents']; d2 = det[6]['documents']; sub = dict(zip(idx, range(len(idx))))
TOP = {}
for j, (e, i, _) in enumerate(U):
    ct = d1['Consensus topic'][j]
    if not ct or not d1['Stable'][j]: TOP[(e, i)] = ('', ''); continue
    t = int(ct.split('_')[1])
    if t != REST: TOP[(e, i)] = BASE_POS[t]; continue
    r = d2.iloc[sub[j]]
    if not r['Consensus topic'] or not r['Stable']: TOP[(e, i)] = ('', ''); continue
    TOP[(e, i)] = SUB_POS[int(r['Consensus topic'].split('_')[1])]


def circulation_values(codes):
    inn, out = Counter(), Counter()
    for e in ids:
        path = [''.join(codes[(e, int(s['stage_index']))]) for s in stages_by[e]]
        path = [p for p in path if p]
        path = [p for j, p in enumerate(path) if j == 0 or p != path[j - 1]]
        for a, b in zip(path, path[1:]): out[a] += 1; inn[b] += 1
    return {p: (inn[p] - out[p]) / (inn[p] + out[p]) for p in set(inn) | set(out)}, inn, out


def circulation_cats(codes):
    val, _, _ = circulation_values(codes)
    res = {}
    for e in ids:
        seq = [(int(s['stage_index']), codes[(e, int(s['stage_index']))]) for s in stages_by[e]]
        seq = [(i, c) for i, c in seq if c[0]]
        if len(seq) < 2: continue
        prev = None
        for j, (i, c) in enumerate(seq):
            if j + 1 < len(seq):
                n = seq[j + 1][1]
                cat = (CATS[2] if n == c else CATS[1] if n[0] == c[0]
                       else CATS[0] if val.get(''.join(n), 0) >= val.get(''.join(c), 0) else CATS[3])
            else:
                cat = CATS[0] if prev == CATS[0] else CATS[2]
            res[(e, i)] = cat; prev = cat
    return res


def write(codes, cats, years, path):
    rows = []
    for e in ids:
        for s in stages_by[e]:
            k = (e, int(s['stage_index'])); st, sq = codes[k]
            if not st: continue
            rows.append([e, years(k), st, CATFR.get(cats.get(k, ''), ''), sq])
    rows.sort(key=lambda r: (int(r[0]), r[1]))
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(['aid', 'year', 'structure', 'category', 'sequence']); w.writerows(rows)
    return len(rows), len({r[0] for r in rows})


def old_year(k):
    e, i = k
    try: b = int(ACT[e]['birth_year'])
    except ValueError: b = 1850
    return b + 15 + i * 4


if __name__ == '__main__':
    pass  # Ordner legt pfade.py an
    real = lambda k: YEARS[k][0]
    print('N0', write(LEX, HCAT, old_year, vertrag('N0_lexikon_hiscam_alte_jahre.csv')))
    print('N1', write(LEX, HCAT, real, vertrag('N1_lexikon_hiscam_echte_jahre.csv')))
    TC = circulation_cats(TOP)
    print('N2', write(TOP, TC, real, vertrag('N2_topics_zirkulation_echte_jahre.csv')))
    print('Etappen mit Position: Lexikon', sum(1 for v in LEX.values() if v[0]), '| Topics', sum(1 for v in TOP.values() if v[0]))
    # Etappentabelle mit Jahren
    with open(ergeb('etappen_jahre_positionen.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['entry_id', 'surname', 'stage_index', 'occupation_raw', 'jahr', 'jahr_quelle', 'jahr_bisher',
                    'lexikon_position', 'hiscam', 'kategorie_hiscam', 'topic_position', 'kategorie_zirkulation'])
        for e in ids:
            for s in stages_by[e]:
                k = (e, int(s['stage_index']))
                w.writerow([e, ACT[e]['surname'], k[1], s['occupation_raw'], YEARS[k][0], YEARS[k][1], old_year(k),
                            '.'.join(LEX[k]) if LEX[k][0] else '', s['hiscam'], HCAT[k],
                            '.'.join(TOP[k]) if TOP[k][0] else '', TC.get(k, '')])
    pickle.dump(dict(TOP=TOP, LEX=LEX, TC=TC, YEARS=YEARS), open(arbeit('codings.pkl'), 'wb'))
