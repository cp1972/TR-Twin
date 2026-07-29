#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figuren_kap11.py — zeichnet die zehn Abbildungen des Kapitels 11 im Raster der
Kapitel 2 bis 9 neu: weißer Grund, Helvetica, Palette der Relationsstrukturen,
deutschsprachig, ohne Titel im Bild (der steht in der Legende).

    python3 figuren_kap11.py <repo>/examples/working-class-authors <ziel>

Ersetzt die früheren PNG-Dateien (matplotlib/Solarized bzw. Inter/Monospace),
die drei verschiedene Bildsprachen und Deutsch, Englisch und Französisch
mischten.

Datengrundlage
  report/anhang/tr_measures.json          Abb. 1–4   (mitgeliefert)
  report/anhang/flow.json                 Abb. 5     (rekonstruiere_flow.py)
  data/instances/control_parc_empirical.csv  Abb. 6–7
  course.json                             Abb. 8     (course_analysis.js)
  fest verdrahtet in report/anhang/figures.py  Abb. 9–10
"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tr_svg import (Bild, STRUKTUR, S_NAMEN, S_KURZ, EBENEN, KATEGORIE, K_NAMEN,
                    C_TICK, C_VALUE, C_LABEL, C_REF, C_MARK, C_GRID,
                    RAMPE_ANTEIL, RAMPE_ANZAHL, RAMPE_KONTROLLE, de, misch)

W, H = 780, 430


# =============================================================== Abbildung 1
def abb01_kaskade(M, ziel):
    b = Bild(W, 430)
    b.notiz('Gini-Ungleichheit auf den drei Ebenen der Kaskade. Farbige Balken: '
            'Kohorte (empirisch). Grau: symmetrischer Referenzzustand der TR.')
    c = M['cascade']
    werte = [c['transversal'], c['horizontal'], c['vertical']]
    ref = [0.0, 0.0, c['vertical_baseline']]
    namen = ['transversal', 'horizontal', 'vertikal']
    unter = ['zwischen Strukturen', 'zwischen Sequenzen', 'zwischen Kategorien']

    L, R, TOP, BOT = 80, 700, 85, 330
    ys = lambda v: BOT - v / 0.6 * (BOT - TOP)
    b.yraster(L, R, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], ys, 1)

    gruppe = (R - L) / 3
    bw = 62
    for i in range(3):
        cx = L + gruppe * (i + 0.5)
        # empirisch
        x1 = cx - bw - 5
        b.rechteck(x1, ys(werte[i]), bw, BOT - ys(werte[i]), EBENEN[i])
        b.text(x1 + bw / 2, ys(werte[i]) - 6, de(werte[i]), size=10.5,
               fill=C_VALUE, weight='bold')
        # Referenz
        x2 = cx + 5
        if ref[i] > 0:
            b.rechteck(x2, ys(ref[i]), bw, BOT - ys(ref[i]), C_REF)
            b.text(x2 + bw / 2, ys(ref[i]) - 6, de(ref[i]), size=10, fill=C_LABEL)
        else:
            b.linie(x2, BOT, x2 + bw, BOT, C_REF, 2.5)
            b.text(x2 + bw / 2, BOT - 6, '0,00', size=10, fill=C_LABEL)
        b.text(cx, BOT + 20, namen[i], size=11, fill=C_VALUE)
        b.text(cx, BOT + 35, f'({unter[i]})', size=9.5, fill=C_LABEL)

    b.fuss((L + R) / 2, BOT + 62, 'Ebene der Ungleichheit')
    return b.speichern(ziel)


# =============================================================== Abbildung 2
def abb02_vertikal(M, ziel):
    b = Bild(W, 430)
    b.notiz('Vertikale Ungleichheit (Gini über die Akteurkategorien) je Relationsstruktur')
    v = M['vertGiniX']
    basis = M['cascade']['vertical_baseline']

    L, R, TOP, BOT = 90, 690, 90, 330
    ys = lambda x: BOT - x / 0.8 * (BOT - TOP)
    b.yraster(L, R, [0, 0.2, 0.4, 0.6, 0.8], ys, 1)

    gruppe = (R - L) / 4
    bw = 74
    for i in range(4):
        cx = L + gruppe * (i + 0.5)
        b.rechteck(cx - bw / 2, ys(v[i]), bw, BOT - ys(v[i]), STRUKTUR[i])
        b.text(cx, ys(v[i]) - 6, de(v[i]), size=10.5, fill=C_VALUE, weight='bold')
        b.text(cx, BOT + 20, S_KURZ[i], size=10.5, fill=C_LABEL)

    b.linie(L, ys(basis), R, ys(basis), C_MARK, 1.4, strich='4 3')
    b.text(R, ys(basis) - 6, f'symmetrische Referenz {de(basis)}', size=9,
           fill=C_TICK, anchor='end')

    # zwei Befunde annotieren
    cx_p = L + gruppe * 1.5
    b.text(cx_p, ys(v[1]) - 46, 'Apex homogenisiert', size=9.5, fill=C_LABEL)
    b.text(cx_p, ys(v[1]) - 34, '(nur Etablierte)', size=9.5, fill=C_LABEL)
    b.linie(cx_p, ys(v[1]) - 28, cx_p, ys(v[1]) - 10, C_MARK, 1)

    cx_w = L + gruppe * 2.5
    b.text(cx_w, ys(v[2]) - 40, 'Beherrschte stratifiziert', size=9.5, fill=C_LABEL)
    b.text(cx_w, ys(v[2]) - 28, '(Etablierte und Enttäuschte)', size=9.5, fill=C_LABEL)
    b.linie(cx_w, ys(v[2]) - 22, cx_w, ys(v[2]) - 8, C_MARK, 1)

    b.fuss((L + R) / 2, BOT + 46, 'Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 3
def abb03_sequenzen(M, ziel):
    b = Bild(W, 400)
    b.notiz('Anteil der Sequenzen an der jeweiligen Relationsstruktur (g), '
            'in Prozent; S = Größe der Struktur am gesamten Feld')
    g, S = M['g'], M['S']
    L, T = 250, 96
    zeilen = [f'{S_KURZ[x]}  (S = {S[x]*100:.0f} %)' for x in range(4)]
    spalten = ['Sequenz A', 'Sequenz B', 'Sequenz C', 'Sequenz D']
    b.heatmap(L, T, spalten, zeilen, g, RAMPE_ANTEIL, zellw=112, zellh=58,
              fmt=lambda v: f'{v*100:.0f}', schwelle=0.55, leer=0.0)
    b.skala(L + 112, T + 4 * 58 + 24, 224, RAMPE_ANTEIL, '0 %', '100 %')
    b.fuss(L + 2 * 112, T + 4 * 58 + 60, 'Sequenz innerhalb der Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 4
def abb04_kategorien(M, ziel):
    b = Bild(W, 430)
    b.notiz('Zusammensetzung der Akteurkategorien je Relationsstruktur, '
            'gewichtet nach den Sequenzgrößen')
    g, act = M['g'], M['act']
    comp = []
    for x in range(4):
        v = [0.0] * 4
        for s in range(4):
            for c in range(4):
                v[c] += g[x][s] * act[x][s][c]
        t = sum(v) or 1
        comp.append([q / t for q in v])

    L, R, TOP, BOT = 100, 660, 90, 320
    ys = lambda v: BOT - v * (BOT - TOP)
    b.yraster(L, R, [0, 0.25, 0.5, 0.75, 1.0], ys, 2)

    gruppe = (R - L) / 4
    bw = 76
    for x in range(4):
        cx = L + gruppe * (x + 0.5)
        unten = 0.0
        for c in range(4):
            hoehe = comp[x][c]
            if hoehe <= 0.001:
                unten += hoehe
                continue
            y0, y1 = ys(unten + hoehe), ys(unten)
            b.rechteck(cx - bw / 2, y0, bw, y1 - y0, KATEGORIE[c], rx=0)
            if hoehe > 0.09:
                b.text(cx, (y0 + y1) / 2 + 4, f'{hoehe*100:.0f} %', size=10,
                       fill='#ffffff' if c in (0, 3) else C_VALUE)
            unten += hoehe
        b.text(cx, BOT + 20, S_KURZ[x], size=10.5, fill=C_LABEL)

    b.legende(L, 55, list(zip(KATEGORIE, K_NAMEN)), waagerecht=True, size=10.5)
    b.fuss((L + R) / 2, BOT + 46, 'Anteil an der Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 5
def abb05_uebergaenge(F, ziel):
    b = Bild(W, 400)
    gesamt = sum(map(sum, F))
    b.notiz(f'Wechsel zwischen Relationsstrukturen über aufeinanderfolgende '
            f'Etappen; {gesamt} Übergänge insgesamt')
    L, T = 236, 100
    zeilen = ['von ' + n for n in S_KURZ]
    spalten = ['nach ' + n.split('·')[1] for n in S_KURZ]
    b.heatmap(L, T, spalten, zeilen, [[float(v) for v in r] for r in F],
              RAMPE_ANZAHL, zellw=118, zellh=54,
              fmt=lambda v: f'{int(v)}', schwelle=0.55, leer=0.0)
    b.skala(L + 118, T + 4 * 54 + 24, 236, RAMPE_ANZAHL, '0', str(max(map(max, F))))
    b.fuss(L + 2 * 118, T + 4 * 54 + 60, 'Zielstruktur')
    return b.speichern(ziel)


# ------------------------------------------------- Kontrollkapazität (6 und 7)
KCAP, S0, LAM = 1.0, 0.5, 0.8
SX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}


def gini(a):
    n = len(a)
    if n < 2:
        return 0.0
    s = sum(a)
    if s <= 0:
        return 0.0
    b = sorted(a)
    acc = sum((i + 1) * b[i] for i in range(n))
    return max(0.0, min(1.0, (2 * acc) / (n * s) - (n + 1) / n))


def kap_von(ws):
    n = len(ws)
    if n == 0:
        return 1.0
    W_ = sum(ws)
    strat = gini(ws) * (1 - 1 / n) if n > 1 else 0.0
    sat = 1 - math.exp(-LAM * W_)
    return 1 + KCAP * sat * (S0 + (1 - S0) * strat)


def parc_gewichte(pfad, jahr):
    """Gewicht jeder Kontrollinstanz zum Stichjahr, interpoliert."""
    rows = list(csv.DictReader(open(pfad, encoding='utf-8-sig')))
    je = {}
    for r in rows:
        je.setdefault(r['aid'], []).append(r)
    proX = {x: [] for x in range(4)}
    proZelle = {x: {q: [] for q in range(4)} for x in range(4)}
    for aid, rs in je.items():
        rs.sort(key=lambda r: int(r['annee']))
        ys = [int(r['annee']) for r in rs]
        if jahr < ys[0] or jahr > ys[-1]:
            continue
        lo = hi = rs[0]
        for r in rs:
            if int(r['annee']) <= jahr:
                lo = r
        for r in reversed(rs):
            if int(r['annee']) >= jahr:
                hi = r
        wl, wh = float(lo['poids']), float(hi['poids'])
        yl, yh = int(lo['annee']), int(hi['annee'])
        wv = wl if yh == yl else wl + (wh - wl) * (jahr - yl) / (yh - yl)
        x = SX[rs[0]['structure']]
        proX[x].append(wv)
        proZelle[x][SX[rs[0]['sequence']]].append(wv)
    return proX, proZelle


# =============================================================== Abbildung 6
def abb06_kontrollkapazitaet(parc, jahr, ziel):
    proX, _ = parc
    b = Bild(W, 430)
    b.notiz(f'Aus dem Bestand der Kontrollinstanzen abgeleitete Kapazität '
            f'(Stand {jahr}); 1,00 = keine Kontrolle')
    cap = [kap_von(proX[x]) for x in range(4)]

    L, R, TOP, BOT = 90, 690, 92, 318
    obergrenze = max(1.6, max(cap) + 0.06)
    ys = lambda v: BOT - (v - 1.0) / (obergrenze - 1.0) * (BOT - TOP)
    marken = [1.0, 1.2, 1.4, 1.6]
    b.yraster(L, R, marken, ys, 2)

    gruppe = (R - L) / 4
    bw = 74
    for x in range(4):
        cx = L + gruppe * (x + 0.5)
        b.rechteck(cx - bw / 2, ys(cap[x]), bw, BOT - ys(cap[x]), STRUKTUR[x])
        b.text(cx, ys(cap[x]) - 6, de(cap[x], 3), size=10.5, fill=C_VALUE, weight='bold')
        n = len(proX[x])
        strat = gini(proX[x]) * (1 - 1 / n) if n > 1 else 0.0
        b.text(cx, BOT + 20, S_KURZ[x], size=10.5, fill=C_LABEL)
        b.text(cx, BOT + 36, f'n = {n} · Σw = {de(sum(proX[x]))}', size=9, fill=C_TICK)
        b.text(cx, BOT + 49, f'Konzentration {de(strat, 3)}', size=9, fill=C_TICK)

    b.linie(L, ys(1.0), R, ys(1.0), C_MARK, 1.4, strich='4 3')
    b.fuss((L + R) / 2, BOT + 76, 'Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 7
def abb07_kontrollprofil(parc, jahr, ziel):
    _, proZelle = parc
    b = Bild(W, 400)
    b.notiz(f'Kontrollkapazität je Zelle (Struktur × Sequenz), Stand {jahr}; '
            f'graue Zelle = keine Kontrollinstanz')
    cap = [[kap_von(proZelle[x][q]) for q in range(4)] for x in range(4)]
    L, T = 250, 96
    spalten = ['Sequenz A', 'Sequenz B', 'Sequenz C', 'Sequenz D']
    werte = [[v - 1.0 for v in r] for r in cap]     # 0 = keine Kontrolle
    b.heatmap(L, T, spalten, S_KURZ, werte, RAMPE_KONTROLLE, zellw=112, zellh=58,
              fmt=lambda v: de(v + 1.0, 3), schwelle=0.55, leer=0.0)
    mx = max(max(r) for r in werte)
    b.skala(L + 112, T + 4 * 58 + 24, 224, RAMPE_KONTROLLE, '1,00', de(mx + 1.0, 2))
    b.fuss(L + 2 * 112, T + 4 * 58 + 60, 'regulierte Sequenz')
    return b.speichern(ziel)


# =============================================================== Abbildung 8
def abb08_kanaele(course, ziel):
    b = Bild(W, 430)
    b.notiz('Auf 0 bis 1 normierte Reihen; senkrechte Marke = Höhepunkt der Präsenz')
    jahre = course['years']
    Y0, Y1 = jahre[0], jahre[-1]
    reihen = [('presence', '#C0392B', 'Präsenz der Arbeiterautoren'),
              ('med', '#8C92EC', 'Stärke der Vermittlungsinstanzen'),
              ('ctrl', '#46CDB8', 'Kontrollkapazität'),
              ('recip', '#E8B14C', 'Reziprozität der Zielstruktur')]

    def norm(a):
        mx = max(a) if a else 1
        return [v / mx if mx > 0 else 0 for v in a]

    def normctrl(a):
        mx = max(a)
        return [(v - 1) / (mx - 1) if mx > 1 else 0 for v in a]

    def pearson(a, c):
        n = len(a)
        ma, mc = sum(a) / n, sum(c) / n
        num = sum((a[i] - ma) * (c[i] - mc) for i in range(n))
        da = math.sqrt(sum((x - ma) ** 2 for x in a))
        dc = math.sqrt(sum((x - mc) ** 2 for x in c))
        return num / (da * dc) if da * dc > 0 else 0.0

    # Legende zweizeilig, sonst läuft sie über den rechten Rand
    b.linienlegende(60, 58, [(f, l) for _, f, l in reihen[:2]], size=10.5)
    b.linienlegende(60, 76, [(f, l) for _, f, l in reihen[2:]], size=10.5)

    panels = [('0', 'A · Kultur'), ('3', 'D · Medien')]
    L, TOP, PH, GAP = 60, 108, 210, 56
    PW = (W - 2 * L - GAP) / 2
    for pi, (schl, lab) in enumerate(panels):
        px = L + pi * (PW + GAP)
        st = course['struct'][schl]
        werte = {'presence': norm(st['presence']), 'med': norm(st['med']),
                 'ctrl': normctrl(st['ctrl']), 'recip': st['recip']}
        xs = lambda yr: px + (yr - Y0) / ((Y1 - Y0) or 1) * PW
        ys = lambda v: TOP + PH - v * PH
        b.panel(px + PW / 2, TOP - 14, lab)
        for gv in (0.0, 0.5, 1.0):
            b.linie(px, ys(gv), px + PW, ys(gv), C_GRID)
        b.text(px - 8, ys(0.0) + 3, '0', size=9, fill=C_TICK, anchor='end')
        b.text(px - 8, ys(1.0) + 3, '1', size=9, fill=C_TICK, anchor='end')
        for yr in (1750, 1800, 1850, 1900, 1950):
            if Y0 <= yr <= Y1:
                xx = xs(yr)
                b.linie(xx, TOP + PH, xx, TOP + PH + 4, C_TICK)
                b.text(xx, TOP + PH + 17, str(yr), size=9, fill=C_TICK)
        P = st['presence']
        pmax = max(P)
        xx = xs(jahre[P.index(pmax)])
        b.linie(xx, TOP, xx, TOP + PH, C_MARK, 1, strich='3 3')
        b.text(xx, TOP - 1, f'Höhepunkt {jahre[P.index(pmax)]}: {pmax}',
               size=9, fill=C_LABEL)
        for schluessel, farbe, _ in reihen:
            a = werte[schluessel]
            b.polylinie([(xs(jahre[i]), ys(a[i])) for i in range(len(jahre))],
                        farbe, 1.8, opacity=0.92)
        idx = [i for i in range(len(jahre)) if st['presence'][i] > 0]
        if len(idx) > 5:
            Pv = [st['presence'][i] for i in idx]
            Mv = [st['med'][i] for i in idx]
            Cv = [st['ctrl'][i] for i in idx]
            b.text(px + PW / 2, TOP + PH + 36,
                   f'r(Präsenz, Vermittlung) = {de(pearson(Pv, Mv))}', size=9.5,
                   fill=C_LABEL)
            b.text(px + PW / 2, TOP + PH + 50,
                   f'r(Präsenz, Kontrolle) = {de(pearson(Pv, Cv))}', size=9.5,
                   fill=C_LABEL)
    b.fuss(W / 2, TOP + PH + 76, 'Jahr')
    return b.speichern(ziel)


# =============================================================== Abbildung 9
def abb09_atypizitaet(ziel):
    b = Bild(W, 430)
    b.notiz('Anteil der Männer aus Arbeiterfamilien, die die Arbeiterklasse verlassen')
    kats = [('erreicht den Angestelltenstand', '(HISCLASS I–V)'),
            ('erreicht die berufliche Elite', '(HISCLASS I–II)')]
    kohorte = [79, 62]
    referenz = [8, 0.2]

    L, R, TOP, BOT = 90, 690, 96, 322
    ys = lambda v: BOT - v / 90 * (BOT - TOP)
    b.yraster(L, R, [0, 20, 40, 60, 80], ys, 0)

    gruppe = (R - L) / 2
    bw = 88
    for i in range(2):
        cx = L + gruppe * (i + 0.5)
        x1 = cx - bw - 6
        b.rechteck(x1, ys(kohorte[i]), bw, BOT - ys(kohorte[i]), '#E36F9E')
        b.text(x1 + bw / 2, ys(kohorte[i]) - 6, f'{kohorte[i]} %', size=11,
               fill=C_VALUE, weight='bold')
        x2 = cx + 6
        hoehe = max(BOT - ys(referenz[i]), 1.2)
        b.rechteck(x2, BOT - hoehe, bw, hoehe, C_REF)
        lab = de(referenz[i], 1) + ' %' if referenz[i] < 1 else f'rund {referenz[i]} %'
        b.text(x2 + bw / 2, BOT - hoehe - 6, lab, size=10, fill=C_LABEL)
        b.text(cx, BOT + 22, kats[i][0], size=10.5, fill=C_VALUE)
        b.text(cx, BOT + 37, kats[i][1], size=9.5, fill=C_LABEL)

    b.legende(L, 58,
              [('#E36F9E', 'Kohorte (Söhne von Arbeitern, n = 29)'),
               (C_REF, 'englische Arbeiterklasse 1839–1914 (Miles 1999)')],
              waagerecht=True, size=10.5)
    b.fuss((L + R) / 2, BOT + 64, 'Anteil in Prozent')
    return b.speichern(ziel)


# ============================================================== Abbildung 10
def abb10_vergleich(ziel):
    b = Bild(W, 430)
    b.notiz('Vergleich B: Intensität bei angeglichener zeitlicher Auflösung')
    kats = [('Übertritt manuell → nicht-manuell', '(innerhalb eines Lebens)'),
            ('Aufstieg ungelernt → gelernt', '(gewöhnliche Fluidität)')]
    kohorte = [52, 29]
    referenz = [5, 40]
    randnotiz = ['distinktiv (Grenzüberschreitung)', 'unauffällig — die Stufe wird übersprungen']

    L, R, TOP, BOT = 90, 690, 128, 306
    ys = lambda v: BOT - v / 60 * (BOT - TOP)
    b.yraster(L, R, [0, 20, 40, 60], ys, 0)

    gruppe = (R - L) / 2
    bw = 88
    for i in range(2):
        cx = L + gruppe * (i + 0.5)
        x1 = cx - bw - 6
        b.rechteck(x1, ys(kohorte[i]), bw, BOT - ys(kohorte[i]), '#E36F9E')
        b.text(x1 + bw / 2, ys(kohorte[i]) - 6, f'{kohorte[i]} %', size=11,
               fill=C_VALUE, weight='bold')
        x2 = cx + 6
        b.rechteck(x2, ys(referenz[i]), bw, BOT - ys(referenz[i]), C_REF)
        b.text(x2 + bw / 2, ys(referenz[i]) - 6, f'rund {referenz[i]} %', size=10,
               fill=C_LABEL)
        b.text(cx, BOT + 22, kats[i][0], size=10.5, fill=C_VALUE)
        b.text(cx, BOT + 37, kats[i][1], size=9.5, fill=C_LABEL)
        b.text(cx, BOT + 54, randnotiz[i], size=9.5,
               fill='#E36F9E' if i == 0 else C_LABEL, style='italic')

    b.legende(L, 58, [('#E36F9E', 'Kohorte'), (C_REF, 'Referenz (Miles 1999 / Long 2013)')],
              waagerecht=True, size=10.5)
    b.rechteck(L + 4, 80, R - L - 8, 30, '#f4f4f4', rx=3)
    b.text((L + R) / 2, 93, 'Kohortenintern verbleibt ein Residuum: Richtungsumkehrungen',
           size=9.5, fill=C_LABEL)
    b.text((L + R) / 2, 105, '37 % → 11 % bei dekadischer Auflösung — vom Zensus nicht erfassbar',
           size=9.5, fill=C_LABEL)
    b.fuss((L + R) / 2, BOT + 78, 'Anteil der Akteure in Prozent')
    return b.speichern(ziel)


# ------------------------------------------------------------------ Hauptlauf
def main():
    basis = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    ziel = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'figures')
    course_pfad = sys.argv[3] if len(sys.argv) > 3 else os.path.join(basis, 'course.json')
    os.makedirs(ziel, exist_ok=True)
    anhang = os.path.join(basis, 'report', 'anhang')

    M = json.load(open(os.path.join(anhang, 'tr_measures.json'), encoding='utf-8'))
    F = json.load(open(os.path.join(anhang, 'flow.json'), encoding='utf-8'))
    parc = parc_gewichte(os.path.join(basis, 'data', 'instances',
                                      'control_parc_empirical.csv'), 1950)
    course = json.load(open(course_pfad, encoding='utf-8'))

    p = lambda n: os.path.join(ziel, n)
    aus = [
        abb01_kaskade(M, p('wk_abb01_kaskade.svg')),
        abb02_vertikal(M, p('wk_abb02_vertikal.svg')),
        abb03_sequenzen(M, p('wk_abb03_sequenzen.svg')),
        abb04_kategorien(M, p('wk_abb04_kategorien.svg')),
        abb05_uebergaenge(F, p('wk_abb05_uebergaenge.svg')),
        abb06_kontrollkapazitaet(parc, 1950, p('wk_abb06_kontrollkapazitaet.svg')),
        abb07_kontrollprofil(parc, 1950, p('wk_abb07_kontrollprofil.svg')),
        abb08_kanaele(course, p('wk_abb08_kanaele.svg')),
        abb09_atypizitaet(p('wk_abb09_atypizitaet.svg')),
        abb10_vergleich(p('wk_abb10_vergleich.svg')),
    ]
    for a in aus:
        print('  ✓', os.path.basename(a))
    print(f'\n{len(aus)} Abbildungen in {ziel}')


if __name__ == '__main__':
    main()
