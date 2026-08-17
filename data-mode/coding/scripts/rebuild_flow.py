#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rekonstruiere_flow.py — baut flow.json (transversale Übergänge) neu auf.

Die Datei lag ursprünglich in einem out/-Ordner, der nicht im Repository ist.
Sie lässt sich aber vollständig aus stages_long_final.csv wiederherstellen:
die Struktur- und Sequenzcodierung wird mit demselben Lexikon vorgenommen wie
in coding/scripts/04_code_structure_seq.py, danach werden je Akteur die Wechsel
zwischen aufeinanderfolgenden Etappen gezählt.

Gegenprobe: die daraus abgeleiteten Größen S, g und act müssen mit
data/derived/tr_measures.json übereinstimmen. Das Skript prüft das und bricht
ab, wenn es nicht stimmt.

    python3 rekonstruiere_flow.py <repo>/data-mode
"""
import csv, json, os, sys
from collections import defaultdict

STR = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
CAT = {'Etablierte': 0, 'Anwaerter': 1, 'Bewahrende': 2, 'Enttaeuschte': 3}


def lexikon(pfad_skript):
    """SS, VAR und head_concept aus code_structure_seq.py übernehmen, damit die
    Codierung mit dem Original identisch bleibt."""
    src = open(pfad_skript, encoding='utf-8').read()
    kopf = src.split("A={r['entry_id']")[0]
    ns = {}
    exec(compile(kopf, 'code_structure_seq', 'exec'), ns)
    return ns['SS'], ns['head_concept']


def codiere(stages, SS, head_concept):
    for s in stages:
        con = head_concept(s['occupation_raw'])
        if con and con in SS:
            s['structure'], s['sequence'], _ = SS[con]
        else:
            s['structure'] = s['sequence'] = ''
    return stages


def masse(stages):
    cnt = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    n = 0
    for r in stages:
        st, sq, c = r['structure'], r['sequence'], r.get('tr_absolute', '')
        if st in STR and sq in STR and c in CAT:
            cnt[STR[st]][STR[sq]][CAT[c]] += 1
            n += 1
    gr = [sum(sum(cnt[x][s]) for s in range(4)) for x in range(4)]
    tot = sum(gr) or 1
    S = [v / tot for v in gr]
    g = [[0.0] * 4 for _ in range(4)]
    act = [[[0.25] * 4 for _ in range(4)] for _ in range(4)]
    for x in range(4):
        sx = gr[x]
        for s in range(4):
            m = sum(cnt[x][s])
            g[x][s] = (m / sx) if sx else 0.0
            if m:
                act[x][s] = [cnt[x][s][c] / m for c in range(4)]
    return n, S, g, act


def fluss(stages):
    """4x4-Matrix der Strukturwechsel: Zeile = von, Spalte = nach."""
    F = [[0] * 4 for _ in range(4)]
    je_akteur = defaultdict(list)
    for s in stages:
        if s['structure']:
            je_akteur[s['entry_id']].append(s)
    for eid, rs in je_akteur.items():
        rs.sort(key=lambda r: int(r['stage_index']))
        folge = [r['structure'] for r in rs]
        for a, b in zip(folge, folge[1:]):
            if a != b:
                F[STR[a]][STR[b]] += 1
    return F


def main():
    basis = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    anhang = os.path.join(basis, 'coding')
    stages_pfad = os.path.join(basis, 'coding', 'results', 'stages_long_final.csv')
    ziel = os.path.join(basis, 'data', 'derived', 'flow.json')

    SS, head_concept = lexikon(os.path.join(basis, 'coding', 'scripts', '04_code_structure_seq.py'))
    stages = list(csv.DictReader(open(stages_pfad, encoding='utf-8-sig')))
    # BOM-Spalte vereinheitlichen
    for s in stages:
        if 'entry_id' not in s:
            for k in list(s):
                if k.endswith('entry_id'):
                    s['entry_id'] = s[k]
    codiere(stages, SS, head_concept)

    n, S, g, act = masse(stages)
    ref = json.load(open(os.path.join(basis, 'data', 'derived', 'tr_measures.json'), encoding='utf-8'))
    def gleich(a, b, eps=1e-9):
        if isinstance(a, list):
            return len(a) == len(b) and all(gleich(x, y, eps) for x, y in zip(a, b))
        return abs(a - b) < eps
    assert n == ref['n_stages'], f"n_stages {n} != {ref['n_stages']}"
    assert gleich(S, ref['S']), 'S weicht ab'
    assert gleich(g, ref['g']), 'g weicht ab'
    assert gleich(act, ref['act']), 'act weicht ab'
    print(f'Gegenprobe bestanden: {n} Etappen, S/g/act identisch mit tr_measures.json')

    F = fluss(stages)
    json.dump(F, open(ziel, 'w', encoding='utf-8'), indent=1)
    NAMEN = ['A·Kultur', 'B·Politik', 'C·Wirtschaft', 'D·Medien']
    print(f'\nTransversale Übergänge (Zeile = von, Spalte = nach)  ->  {ziel}')
    print(f"{'':14s}" + ''.join(f'{n_:>14s}' for n_ in NAMEN))
    for i in range(4):
        print(f'{NAMEN[i]:14s}' + ''.join(f'{F[i][j]:>14d}' for j in range(4)))
    print(f'\nSumme der Wechsel: {sum(map(sum, F))}')


if __name__ == '__main__':
    main()
