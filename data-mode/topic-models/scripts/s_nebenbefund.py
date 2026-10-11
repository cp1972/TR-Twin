# -*- coding: utf-8 -*-
"""Nebenbefund zerlegen: statische Ablesung vs. laufender Zwilling (N0, veröffentlichte Daten).
Stufe 1  statisch, alle Jahre gepoolt, je Struktur x Sequenz (wie Skript 08)
Stufe 2  statisch, Zeitschnitt: nur Akteure, die im Jahr Y aktiv sind (Regel des Zwillings), je Struktur x Sequenz
Stufe 3  Eingabe des Zwillings im Jahr Y: Kategorienanteile je Struktur (Sequenz-Detail fällt weg)
Stufe 4  Ausgabe des laufenden Zwillings im Jahr Y
"""
from pfade import *
import csv, json
from collections import defaultdict

VAL = [3, 2, 1, 0]
CI = {'etabli': 0, 'aspirant': 1, 'conservateur': 2, 'decu': 3}
L = 'ABCD'
rows = list(csv.DictReader(open(vertrag('N0_lexikon_hiscam_alte_jahre.csv'), encoding='utf-8')))
rec = [dict(aid=r['aid'], y=int(r['year']), s=L.index(r['structure']), q=L.index(r['sequence']) if r['sequence'] in L else L.index(r['structure']),
            c=CI.get(r['category'], 2), coded=r['category'] in CI) for r in rows]


def gdist(a):
    m = sum(a[c] * VAL[c] for c in range(4))
    if m < 1e-9: return 0.0
    return sum(a[c] * a[d] * abs(VAL[c] - VAL[d]) for c in range(4) for d in range(4)) / (2 * m)


def vert_xs(items):
    """items: Liste (s, q, c) -> vertikaler Gini je Struktur, Formel des Simulators (g-gewichtet über Sequenzen)"""
    cnt = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    for s, q, c in items: cnt[s][q][c] += 1
    out = []
    for x in range(4):
        sx = sum(sum(cnt[x][q]) for q in range(4)); num = den = 0.0
        for q in range(4):
            m = sum(cnt[x][q])
            if not m: continue
            a = [v / m for v in cnt[x][q]]; w = m / sx
            num += w * gdist(a); den += w
        out.append(num / den if den else 0.0)
    return out, [sum(sum(cnt[x][q]) for q in range(4)) for x in range(4)]


def vert_struct(items):
    cnt = [[0] * 4 for _ in range(4)]
    for s, q, c in items: cnt[s][c] += 1
    return [gdist([v / sum(cnt[x]) for v in cnt[x]]) if sum(cnt[x]) else 0.0 for x in range(4)]


byA = defaultdict(list)
for r in rec: byA[r['aid']].append(r)
for a in byA: byA[a].sort(key=lambda r: r['y'])


def active(Y):
    res = []
    for a, st in byA.items():
        if Y < st[0]['y'] or Y > st[-1]['y']: continue
        pos = st[0]
        for s in st:
            if s['y'] <= Y: pos = s
            else: break
        res.append((pos['s'], pos['q'], pos['c']))
    return res


tw = json.load(open(ergeb('zwilling_laeufe.json')))['N0_lexikon_hiscam_alte_jahre.csv']
out = {}
pooled_all, n_all = vert_xs([(r['s'], r['q'], r['c']) for r in rec])
pooled_cod, n_cod = vert_xs([(r['s'], r['q'], r['c']) for r in rec if r['coded']])
out['statisch_gepoolt'] = dict(alle=pooled_all, nur_kodiert=pooled_cod, n=n_cod)
for lab, Y in (('1850', 1850), ('1900', 1900), ('Ende', tw['end']['year'])):
    items = active(Y)
    v2, n2 = vert_xs(items)
    v3 = vert_struct(items)
    key = {'1850': 'y1850', '1900': 'y1900', 'Ende': 'end'}[lab]
    out[lab] = dict(jahr=Y, n_aktiv=len(items), n_je_struktur=n2, zeitschnitt=v2, eingabe_zwilling=v3, zwilling=tw[key]['vGini'])
# Zeitfenster um 1900 (± 10 Jahre, alle Etappen im Fenster), robuster als ein Stichjahr
win = [(r['s'], r['q'], r['c']) for r in rec if 1890 <= r['y'] <= 1910]
out['fenster_1890_1910'] = dict(n=len(win), zeitschnitt=vert_xs(win)[0], n_je_struktur=vert_xs(win)[1])
json.dump(out, open(ergeb('nebenbefund.json'), 'w'), indent=1)
f = lambda v: ' '.join(f'{x:.2f}' for x in v)
print('gepoolt (alle Zeilen)   ', f(pooled_all), n_all)
print('gepoolt (nur kodierte)  ', f(pooled_cod), n_cod)
for lab in ('1850', '1900', 'Ende'):
    o = out[lab]
    print(f"{lab} ({o['jahr']}) n={o['n_aktiv']} {o['n_je_struktur']}")
    print('   Zeitschnitt x Sequenz ', f(o['zeitschnitt']))
    print('   Eingabe Zwilling      ', f(o['eingabe_zwilling']))
    print('   Zwilling              ', f(o['zwilling']))
print('Fenster 1890-1910', out['fenster_1890_1910']['n'], f(out['fenster_1890_1910']['zeitschnitt']), out['fenster_1890_1910']['n_je_struktur'])
