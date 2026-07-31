#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figuren_kap11.py — zeichnet die zehn Abbildungen des Kapitels 11 im Raster der
Kapitel 2 bis 9 neu: weißer Grund, Helvetica, Palette der Relationsstrukturen,
deutschsprachig.

Gestaltungsregeln (zweite Fassung):
  * kein Titel im Bild — der steht in der Legende des Dokuments
  * eine Randnotiz nur dort, wo die Abbildung ohne sie unverständlich bliebe,
    und dann schwarz statt grau
  * Legende auf halber Höhe am rechten Rand, weiß hinterlegt, damit keine
    Datenlinie sie kreuzt
  * Schriftgrade so, dass im 15-cm-Satz nichts unter 7,5 pt fällt
  * die Achsenbeschriftung am unteren Rand mit deutlichem Abstand zum Bild

    python3 figuren_kap11.py <repo>/data-mode <ziel>

Ersetzt die früheren PNG-Dateien (matplotlib/Solarized bzw. Inter/Monospace),
die drei verschiedene Bildsprachen und Deutsch, Englisch und Französisch
mischten.

Datengrundlage
  data/derived/tr_measures.json              Abb. 1–4
  data/derived/flow.json                     Abb. 5   (coding/scripts/rebuild_flow.py)
  data/instances/control_parc_empirical.csv  Abb. 6–7
  data/derived/course.json                   Abb. 8   (scripts/runs/course_analysis.js)
  fest verdrahtet in diesem Skript           Abb. 9–10
"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_style import (Bild, STRUKTUR, S_NAMEN, S_KURZ, EBENEN, KATEGORIE, K_NAMEN,
                    C_TICK, C_VALUE, C_LABEL, C_REF, C_MARK, C_GRID,
                    RAMPE_ANTEIL, RAMPE_ANZAHL, RAMPE_KONTROLLE,
                    SZ_TICK, SZ_LABEL, SZ_VALUE, SZ_LEG, SZ_PANEL, de, misch, breite)

W, H = 780, 430


# =============================================================== Abbildung 1
def abb01_kaskade(M, ziel):
    b = Bild(W, 440)
    c = M['cascade']
    werte = [c['transversal'], c['horizontal'], c['vertical']]
    ref = [0.0, 0.0, c['vertical_baseline']]
    namen = ['transversal', 'horizontal', 'vertikal']
    unter = ['zwischen Strukturen', 'zwischen Sequenzen', 'zwischen Kategorien']

    L, R, TOP, BOT = 92, 512, 56, 318
    ys = lambda v: BOT - v / 0.6 * (BOT - TOP)
    b.yraster(L, R, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], ys, 1)

    gruppe = (R - L) / 3
    bw = 50
    for i in range(3):
        cx = L + gruppe * (i + 0.5)
        x1 = cx - bw - 4
        b.rechteck(x1, ys(werte[i]), bw, BOT - ys(werte[i]), EBENEN[i])
        b.text(x1 + bw / 2, ys(werte[i]) - 8, de(werte[i]), size=SZ_VALUE,
               fill=C_VALUE, weight='bold')
        x2 = cx + 4
        if ref[i] > 0:
            b.rechteck(x2, ys(ref[i]), bw, BOT - ys(ref[i]), C_REF)
            b.text(x2 + bw / 2, ys(ref[i]) - 8, de(ref[i]), size=SZ_LABEL, fill=C_LABEL)
        else:
            b.linie(x2, BOT, x2 + bw, BOT, C_REF, 3)
            b.text(x2 + bw / 2, BOT - 8, '0,00', size=SZ_LABEL, fill=C_LABEL)
        b.text(cx, BOT + 28, namen[i], size=SZ_LABEL, fill=C_VALUE)
        b.text(cx, BOT + 48, unter[i], size=SZ_TICK, fill=C_LABEL)

    b.legende_rechts(W - 22, (TOP + BOT) / 2,
                     [(EBENEN[0], 'Kohorte (empirisch)'),
                      (C_REF, 'symmetrische Referenz')])
    b.fuss((L + R) / 2, BOT + 90, 'Ebene der Ungleichheit (GINI)')
    return b.speichern(ziel)


# =============================================================== Abbildung 2
def abb02_vertikal(M, ziel):
    b = Bild(W, 440)
    v = M['vertGiniX']
    basis = M['cascade']['vertical_baseline']

    L, R, TOP, BOT = 92, 540, 100, 326
    ys = lambda x: BOT - x / 0.8 * (BOT - TOP)
    b.yraster(L, R, [0, 0.2, 0.4, 0.6, 0.8], ys, 1)

    gruppe = (R - L) / 4
    bw = 58
    for i in range(4):
        cx = L + gruppe * (i + 0.5)
        b.rechteck(cx - bw / 2, ys(v[i]), bw, BOT - ys(v[i]), STRUKTUR[i])
        b.text(cx, ys(v[i]) - 8, de(v[i]), size=SZ_VALUE, fill=C_VALUE, weight='bold')
        b.text(cx, BOT + 28, S_KURZ[i], size=SZ_LABEL, fill=C_LABEL)

    b.linie(L, ys(basis), R, ys(basis), C_MARK, 1.6, strich='5 4')
    b.text(L + 4, ys(basis) - 9, f'symmetrische Referenz {de(basis)}',
           size=SZ_TICK, fill=C_LABEL, anchor='start')

    cx_p = L + gruppe * 1.5
    b.text(cx_p, ys(v[1]) - 48, 'Apex homogenisiert', size=SZ_TICK, fill=C_VALUE)
    b.text(cx_p, ys(v[1]) - 30, '(nur Etablierte)', size=SZ_TICK, fill=C_LABEL)
    b.linie(cx_p, ys(v[1]) - 24, cx_p, ys(v[1]) - 8, C_MARK, 1.2)

    cx_w = L + gruppe * 2.5
    b.text(cx_w, ys(v[2]) - 48, 'Beherrschte stratifiziert', size=SZ_TICK, fill=C_VALUE)
    b.text(cx_w, ys(v[2]) - 30, '(Etablierte, Enttäuschte)', size=SZ_TICK, fill=C_LABEL)
    b.linie(cx_w, ys(v[2]) - 24, cx_w, ys(v[2]) - 8, C_MARK, 1.2)

    b.legende_rechts(W - 22, (TOP + BOT) / 2,
                     [(STRUKTUR[i], S_KURZ[i]) for i in range(4)])
    b.fuss((L + R) / 2, BOT + 68, 'vertikale Ungleichheit (GINI) je Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 3
def abb03_sequenzen(M, ziel):
    b = Bild(W, 440)
    b.notiz('Anteile in Prozent; S = Größe der Struktur am gesamten Feld')
    g, S = M['g'], M['S']
    L, T = 268, 104
    zeilen = [f'{S_KURZ[x]} (S = {S[x]*100:.0f} %)' for x in range(4)]
    spalten = ['Sequenz A', 'Sequenz B', 'Sequenz C', 'Sequenz D']
    b.heatmap(L, T, spalten, zeilen, g, RAMPE_ANTEIL, zellw=118, zellh=56,
              fmt=lambda v: f'{v*100:.0f}', schwelle=0.55, leer=0.0)
    b.skala(L + 118, T + 4 * 56 + 34, 236, RAMPE_ANTEIL, '0 %', '100 %')
    b.fuss(L + 2 * 118, T + 4 * 56 + 84, 'Sequenz innerhalb der Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 4
def abb04_kategorien(M, ziel):
    b = Bild(W, 440)
    g, act = M['g'], M['act']
    comp = []
    for x in range(4):
        v = [0.0] * 4
        for s in range(4):
            for c in range(4):
                v[c] += g[x][s] * act[x][s][c]
        t = sum(v) or 1
        comp.append([q / t for q in v])

    L, R, TOP, BOT = 100, 500, 60, 326
    ys = lambda v: BOT - v * (BOT - TOP)
    b.yraster(L, R, [0, 0.25, 0.5, 0.75, 1.0], ys, 2)

    gruppe = (R - L) / 4
    bw = 62
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
            if hoehe > 0.12:
                b.text(cx, (y0 + y1) / 2 + 6, f'{hoehe*100:.0f} %', size=SZ_TICK,
                       fill='#ffffff' if c in (0, 3) else C_VALUE)
            unten += hoehe
        b.text(cx, BOT + 28, S_KURZ[x], size=SZ_LABEL, fill=C_LABEL)

    b.legende_rechts(W - 22, (TOP + BOT) / 2, list(zip(KATEGORIE, K_NAMEN)))
    b.fuss((L + R) / 2, BOT + 68, 'Anteil an der Relationsstruktur')
    return b.speichern(ziel)


# =============================================================== Abbildung 5
def abb05_uebergaenge(F, ziel):
    b = Bild(W, 440)
    gesamt = sum(map(sum, F))
    b.notiz(f'Anzahl der Wechsel über aufeinanderfolgende Etappen; '
            f'{gesamt} Übergänge insgesamt')
    L, T = 256, 104
    zeilen = ['von ' + n for n in S_KURZ]
    spalten = ['nach ' + n.split('·')[1] for n in S_KURZ]
    b.heatmap(L, T, spalten, zeilen, [[float(v) for v in r] for r in F],
              RAMPE_ANZAHL, zellw=120, zellh=56,
              fmt=lambda v: f'{int(v)}', schwelle=0.55, leer=0.0)
    b.skala(L + 120, T + 4 * 56 + 34, 240, RAMPE_ANZAHL, '0', str(max(map(max, F))))
    b.fuss(L + 2 * 120, T + 4 * 56 + 84, 'Zielstruktur')
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
        rs.sort(key=lambda r: int(r['year']))
        ys = [int(r['year']) for r in rs]
        if jahr < ys[0] or jahr > ys[-1]:
            continue
        lo = hi = rs[0]
        for r in rs:
            if int(r['year']) <= jahr:
                lo = r
        for r in reversed(rs):
            if int(r['year']) >= jahr:
                hi = r
        wl, wh = float(lo['weight']), float(hi['weight'])
        yl, yh = int(lo['year']), int(hi['year'])
        wv = wl if yh == yl else wl + (wh - wl) * (jahr - yl) / (yh - yl)
        x = SX[rs[0]['structure']]
        proX[x].append(wv)
        proZelle[x][SX[rs[0]['sequence']]].append(wv)
    return proX, proZelle


# =============================================================== Abbildung 6
def abb06_kontrollkapazitaet(parc, jahr, ziel):
    proX, _ = parc
    b = Bild(W, 500)
    b.notiz('1,00 = keine Kontrolle')
    cap = [kap_von(proX[x]) for x in range(4)]

    L, R, TOP, BOT = 92, 540, 78, 300
    obergrenze = max(1.6, max(cap) + 0.06)
    ys = lambda v: BOT - (v - 1.0) / (obergrenze - 1.0) * (BOT - TOP)
    b.yraster(L, R, [1.0, 1.2, 1.4, 1.6], ys, 2)

    gruppe = (R - L) / 4
    bw = 58
    for x in range(4):
        cx = L + gruppe * (x + 0.5)
        b.rechteck(cx - bw / 2, ys(cap[x]), bw, BOT - ys(cap[x]), STRUKTUR[x])
        b.text(cx, ys(cap[x]) - 8, de(cap[x], 3), size=SZ_VALUE, fill=C_VALUE,
               weight='bold')
        n = len(proX[x])
        strat = gini(proX[x]) * (1 - 1 / n) if n > 1 else 0.0
        b.text(cx, BOT + 28, S_KURZ[x], size=SZ_LABEL, fill=C_LABEL)
        b.text(cx, BOT + 50, f'n = {n}', size=SZ_TICK, fill=C_VALUE)
        b.text(cx, BOT + 68, f'Σw = {de(sum(proX[x]))}', size=SZ_TICK, fill=C_VALUE)
        b.text(cx, BOT + 86, f'Konz. = {de(strat, 2)}', size=SZ_TICK, fill=C_VALUE)

    b.linie(L, ys(1.0), R, ys(1.0), C_MARK, 1.6, strich='5 4')
    b.legende_rechts(W - 22, (TOP + BOT) / 2,
                     [(STRUKTUR[i], S_KURZ[i]) for i in range(4)])
    b.fuss((L + R) / 2, BOT + 126, 'abgeleitete Kontrollkapazität je Relationsstruktur')
    # Kurzerklärung der beiden Kennzahlen unter den Säulen
    b.text(W - 22, 452, 'n = Zahl der Kontrollinstanzen · Σw = Summe ihrer '
           'Autoritätsgewichte', size=SZ_TICK, fill=C_LABEL, anchor='end')
    b.text(W - 22, 472, 'Konz. = Konzentration dieser Gewichte (GINI, 0 = gleich '
           'verteilt)', size=SZ_TICK, fill=C_LABEL, anchor='end')
    return b.speichern(ziel)


# =============================================================== Abbildung 7
def abb07_kontrollprofil(parc, jahr, ziel):
    _, proZelle = parc
    b = Bild(W, 440)
    b.notiz('graue Zelle = keine Kontrollinstanz; 1,00 = keine Kontrolle')
    cap = [[kap_von(proZelle[x][q]) for q in range(4)] for x in range(4)]
    L, T = 252, 104
    spalten = ['Sequenz A', 'Sequenz B', 'Sequenz C', 'Sequenz D']
    werte = [[v - 1.0 for v in r] for r in cap]
    b.heatmap(L, T, spalten, S_KURZ, werte, RAMPE_KONTROLLE, zellw=122, zellh=56,
              fmt=lambda v: de(v + 1.0, 3), schwelle=0.55, leer=0.0)
    mx = max(max(r) for r in werte)
    b.skala(L + 122, T + 4 * 56 + 34, 244, RAMPE_KONTROLLE, '1,00', de(mx + 1.0, 2))
    b.fuss(L + 2 * 122, T + 4 * 56 + 84, 'regulierte Sequenz')
    return b.speichern(ziel)


# =============================================================== Abbildung 8
def abb08_kanaele(course, ziel):
    b = Bild(W, 480)
    b.notiz('Reihen auf 0 bis 1 normiert; gestrichelt = Höhepunkt der Präsenz')
    jahre = course['years']
    Y0, Y1 = jahre[0], jahre[-1]
    reihen = [('presence', '#C0392B', 'Präsenz der Arbeiterautoren'),
              ('med', '#8C92EC', 'Vermittlungsinstanzen'),
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

    panels = [('0', 'A · Kultur'), ('3', 'D · Medien')]
    L, TOP, PH, GAP, PW = 58, 116, 186, 38, 196
    for pi, (schl, lab) in enumerate(panels):
        px = L + pi * (PW + GAP)
        st = course['struct'][schl]
        werte = {'presence': norm(st['presence']), 'med': norm(st['med']),
                 'ctrl': normctrl(st['ctrl']), 'recip': st['recip']}
        xs = lambda yr: px + (yr - Y0) / ((Y1 - Y0) or 1) * PW
        ys = lambda v: TOP + PH - v * PH
        b.panel(px + PW / 2, TOP - 20, lab)
        for gv in (0.0, 0.5, 1.0):
            b.linie(px, ys(gv), px + PW, ys(gv), C_GRID)
        b.text(px - 10, ys(0.0) + 5, '0', size=SZ_TICK, fill=C_TICK, anchor='end')
        b.text(px - 10, ys(1.0) + 5, '1', size=SZ_TICK, fill=C_TICK, anchor='end')
        for yr in (1800, 1900):
            if Y0 <= yr <= Y1:
                xx = xs(yr)
                b.linie(xx, TOP + PH, xx, TOP + PH + 5, C_TICK)
                b.text(xx, TOP + PH + 24, str(yr), size=SZ_TICK, fill=C_TICK)
        P = st['presence']
        pmax = max(P)
        xx = xs(jahre[P.index(pmax)])
        b.linie(xx, TOP, xx, TOP + PH, C_MARK, 1.2, strich='4 3')
        for schluessel, farbe, _ in reihen:
            a = werte[schluessel]
            b.polylinie([(xs(jahre[i]), ys(a[i])) for i in range(len(jahre))],
                        farbe, 2.0, opacity=0.92)
        b.text(px + PW / 2, TOP + PH + 52,
               f'Höhepunkt {jahre[P.index(pmax)]}: {pmax} Akteure',
               size=SZ_TICK, fill=C_VALUE)
        idx = [i for i in range(len(jahre)) if st['presence'][i] > 0]
        if len(idx) > 5:
            Pv = [st['presence'][i] for i in idx]
            Mv = [st['med'][i] for i in idx]
            Cv = [st['ctrl'][i] for i in idx]
            b.text(px + PW / 2, TOP + PH + 72,
                   f'r(Präsenz, Vermittlung) = {de(pearson(Pv, Mv))}',
                   size=SZ_TICK, fill=C_LABEL)
            b.text(px + PW / 2, TOP + PH + 90,
                   f'r(Präsenz, Kontrolle) = {de(pearson(Pv, Cv))}',
                   size=SZ_TICK, fill=C_LABEL)
    b.legende_rechts(W - 18, TOP + PH / 2, [(f, l) for _, f, l in reihen], art='linie')
    b.fuss(L + PW + GAP / 2, TOP + PH + 128, 'Jahr')
    return b.speichern(ziel)


# =============================================================== Abbildung 9
def abb09_atypizitaet(ziel):
    b = Bild(W, 450)
    kats = [('Angestelltenstand', '(HISCLASS I–V)'),
            ('berufliche Elite', '(HISCLASS I–II)')]
    kohorte = [79, 62]
    referenz = [8, 0.2]

    L, R, TOP, BOT = 92, 452, 60, 318
    ys = lambda v: BOT - v / 90 * (BOT - TOP)
    b.yraster(L, R, [0, 20, 40, 60, 80], ys, 0)

    gruppe = (R - L) / 2
    bw = 62
    for i in range(2):
        cx = L + gruppe * (i + 0.5)
        x1 = cx - bw - 5
        b.rechteck(x1, ys(kohorte[i]), bw, BOT - ys(kohorte[i]), '#E36F9E')
        b.text(x1 + bw / 2, ys(kohorte[i]) - 8, f'{kohorte[i]} %', size=SZ_VALUE,
               fill=C_VALUE, weight='bold')
        x2 = cx + 5
        hoehe = max(BOT - ys(referenz[i]), 1.5)
        b.rechteck(x2, BOT - hoehe, bw, hoehe, C_REF)
        lab = de(referenz[i], 1) + ' %' if referenz[i] < 1 else f'rund {referenz[i]} %'
        b.text(x2 + bw / 2, BOT - hoehe - 8, lab, size=SZ_LABEL, fill=C_LABEL)
        b.text(cx, BOT + 28, kats[i][0], size=SZ_LABEL, fill=C_VALUE)
        b.text(cx, BOT + 48, kats[i][1], size=SZ_TICK, fill=C_LABEL)

    b.legende_rechts(W - 22, (TOP + BOT) / 2,
                     [('#E36F9E', 'Kohorte (n = 29)'),
                      (C_REF, 'englische Arbeiterklasse'),
                      (C_REF, '1839–1914 (Miles 1999)')])
    b.fuss((L + R) / 2, BOT + 92,
           'Anteil der Männer aus Arbeiterfamilien, die diese Position erreichen (%)')
    return b.speichern(ziel)


# ============================================================== Abbildung 10
def abb10_vergleich(ziel):
    b = Bild(W, 490)
    kats = [('Übertritt manuell →', 'nicht-manuell'),
            ('Aufstieg ungelernt →', 'gelernt')]
    unterzeile = ['(innerhalb eines Lebens)', '(gewöhnliche Fluidität)']
    kohorte = [52, 29]
    referenz = [5, 40]
    randnotiz = [('distinktiv:', 'Grenzüberschreitung'),
                 ('unauffällig:', 'die Stufe wird übersprungen')]

    L, R, TOP, BOT = 92, 452, 60, 296
    ys = lambda v: BOT - v / 60 * (BOT - TOP)
    b.yraster(L, R, [0, 20, 40, 60], ys, 0)

    gruppe = (R - L) / 2
    bw = 62
    for i in range(2):
        cx = L + gruppe * (i + 0.5)
        x1 = cx - bw - 5
        b.rechteck(x1, ys(kohorte[i]), bw, BOT - ys(kohorte[i]), '#E36F9E')
        b.text(x1 + bw / 2, ys(kohorte[i]) - 8, f'{kohorte[i]} %', size=SZ_VALUE,
               fill=C_VALUE, weight='bold')
        x2 = cx + 5
        b.rechteck(x2, ys(referenz[i]), bw, BOT - ys(referenz[i]), C_REF)
        b.text(x2 + bw / 2, ys(referenz[i]) - 8, f'rund {referenz[i]} %',
               size=SZ_LABEL, fill=C_LABEL)
        b.text(cx, BOT + 28, kats[i][0], size=SZ_LABEL, fill=C_VALUE)
        b.text(cx, BOT + 48, kats[i][1], size=SZ_LABEL, fill=C_VALUE)
        b.text(cx, BOT + 68, unterzeile[i], size=SZ_TICK, fill=C_LABEL)
        b.text(cx, BOT + 94, randnotiz[i][0], size=SZ_TICK,
               fill='#E36F9E' if i == 0 else C_LABEL, style='italic')
        b.text(cx, BOT + 112, randnotiz[i][1], size=SZ_TICK,
               fill='#E36F9E' if i == 0 else C_LABEL, style='italic')

    b.legende_rechts(W - 22, (TOP + BOT) / 2,
                     [('#E36F9E', 'Kohorte'),
                      (C_REF, 'Referenz (Miles 1999,'),
                      (C_REF, 'Long 2013)')])
    b.fuss((L + R) / 2, BOT + 142, 'Anteil der Akteure in Prozent')
    return b.speichern(ziel)


# ------------------------------------------------------------------ Hauptlauf
def main():
    basis = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    ziel = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'figures')
    abgeleitet = os.path.join(basis, 'data', 'derived')
    course_pfad = sys.argv[3] if len(sys.argv) > 3 else os.path.join(abgeleitet, 'course.json')
    os.makedirs(ziel, exist_ok=True)

    M = json.load(open(os.path.join(abgeleitet, 'tr_measures.json'), encoding='utf-8'))
    F = json.load(open(os.path.join(abgeleitet, 'flow.json'), encoding='utf-8'))
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
