#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg_style.py — das Raster der Abbildungen aus den Kapiteln 2 bis 9.

Abgelesen an den vorhandenen SVG-Dateien (parsons_endzustand.svg,
tilly_durabilitaet.svg, kaskade_typologie.svg, render_trajektorie.py):
weißer Grund, Helvetica, Georgia für Panelüberschriften, Raster #e7e7e7,
Achsenbeschriftung #9a9a9a, Werte #2b2b2b, Fußzeile #555.

Kein Titel im Bild — der steht in der Legende des Dokuments.
"""

# --------------------------------------------------------------- Schriftgrade
# Eine Abbildung von 780 Einheiten Breite wird 15 cm breit gesetzt, eine
# Einheit entspricht also rund 0,55 pt. Damit die kleinste Beschriftung im
# Druck nicht unter 7,5 pt fällt, liegt der Grundwert bei 14.
SZ_TICK   = 14      # Achsenbeschriftung        ~7,6 pt
SZ_LABEL  = 16      # Kategorien, Achsentitel   ~8,7 pt
SZ_VALUE  = 17      # Werte über den Balken     ~9,3 pt
SZ_LEG    = 16      # Legende                   ~8,7 pt
SZ_PANEL  = 19      # Panelüberschrift          ~10,4 pt
SZ_NOTE   = 15      # Randnotiz, nur wo nötig   ~8,2 pt


# ------------------------------------------------------------------ Palette
BG       = '#ffffff'
FONT     = 'Helvetica,Arial,sans-serif'
SERIF    = 'Georgia,serif'
C_NOTE   = '#2b2b2b'     # Randnotiz — schwarz, damit lesbar
C_GRID   = '#e7e7e7'
C_TICK   = '#9a9a9a'
C_VALUE  = '#2b2b2b'
C_LABEL  = '#555'
C_FOOT   = '#444'
C_REF    = '#b9b9b9'     # Referenz-/Vergleichsreihe
C_MARK   = '#bbb'        # gestrichelte Hilfslinien

# Relationsstrukturen — identisch mit render_trajektorie.py
STRUKTUR = ['#E8B14C', '#46CDB8', '#E36F9E', '#8C92EC']
S_NAMEN  = ['Kultur', 'Politik', 'Wirtschaft', 'Medien']
S_KURZ   = ['A·Kultur', 'B·Politik', 'C·Wirtschaft', 'D·Medien']

# Ungleichheitsebenen — identisch mit kaskade_typologie.svg
EBENEN   = ['#5B6CB8', '#E08A3C', '#7BB661']

# Akteurkategorien
KATEGORIE = ['#5B6CB8', '#46CDB8', '#E8B14C', '#E36F9E']
K_NAMEN   = ['Etablierte', 'Anwärter', 'Bewahrende', 'Enttäuschte']


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def de(v, n=2):
    """Deutsche Dezimalschreibung."""
    return f'{v:.{n}f}'.replace('.', ',')


class Bild:
    def __init__(self, w=780, h=430):
        self.w, self.h = w, h
        self.s = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
                  f'font-family="{FONT}">',
                  f'<rect x="0" y="0" width="{w}" height="{h}" fill="{BG}"/>']

    # -------------------------------------------------------------- Bausteine
    def notiz(self, text, y=32, x=40, size=SZ_NOTE):
        """Kurze technische Randnotiz — nur, wo die Abbildung ohne sie
        unverständlich bliebe. Schwarz, nicht grau."""
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{C_NOTE}">'
                      f'{esc(text)}</text>')

    def panel(self, x, y, text, size=SZ_PANEL):
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-family="{SERIF}" '
                      f'fill="{C_VALUE}" text-anchor="middle">{esc(text)}</text>')

    def text(self, x, y, t, size=SZ_LABEL, fill=C_LABEL, anchor='middle',
             weight=None, style=None, family=None):
        a = f' font-weight="{weight}"' if weight else ''
        b = f' font-style="{style}"' if style else ''
        c = f' font-family="{family}"' if family else ''
        self.s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                      f'text-anchor="{anchor}"{a}{b}{c}>{esc(t)}</text>')

    def linie(self, x1, y1, x2, y2, farbe=C_GRID, breite=1, strich=None):
        d = f' stroke-dasharray="{strich}"' if strich else ''
        self.s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{farbe}" stroke-width="{breite}"{d}/>')

    def rechteck(self, x, y, w, h, farbe, rx=2, opacity=None):
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                      f'fill="{farbe}" rx="{rx}"{o}/>')

    def polylinie(self, punkte, farbe, breite=2.2, opacity=None):
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in punkte)
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.s.append(f'<polyline points="{p}" fill="none" stroke="{farbe}" '
                      f'stroke-width="{breite}" stroke-linejoin="round"{o}/>')

    def punkt(self, x, y, farbe, r=3):
        self.s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{farbe}"/>')

    def yraster(self, L, R, werte, yfun, nachkomma=2, size=SZ_TICK):
        """Waagerechtes Raster mit Beschriftung links."""
        for v in werte:
            yy = yfun(v)
            self.linie(L, yy, R, yy)
            self.text(L - 10, yy + size * 0.35, de(v, nachkomma) if nachkomma else f'{v:g}',
                      size=size, fill=C_TICK, anchor='end')

    def legende(self, x, y, eintraege, size=SZ_LEG, schritt=22, waagerecht=False):
        """eintraege: [(farbe, beschriftung), …]"""
        if waagerecht:
            cx = x
            for farbe, lab in eintraege:
                self.rechteck(cx, y, size - 3, size - 3, farbe, rx=2)
                self.text(cx + size + 3, y + size - 4, lab, size=size,
                          fill=C_VALUE, anchor='start')
                cx += size + 3 + breite(lab, size) + 26
        else:
            cy = y
            for farbe, lab in eintraege:
                self.rechteck(x, cy, size - 3, size - 3, farbe, rx=2)
                self.text(x + size + 3, cy + size - 4, lab, size=size,
                          fill=C_VALUE, anchor='start')
                cy += schritt

    def linienlegende(self, x, y, eintraege, size=SZ_LEG):
        cx = x
        for farbe, lab in eintraege:
            self.linie(cx, y, cx + 24, y, farbe, 2.8)
            self.text(cx + 30, y + size * 0.35, lab, size=size,
                      fill=C_VALUE, anchor='start')
            cx += 30 + breite(lab, size) + 26

    def fuss(self, x, y, text, size=SZ_LABEL, anchor='middle'):
        self.text(x, y, text, size=size, fill=C_LABEL, anchor=anchor)

    def legende_rechts(self, rechts, mitte, eintraege, size=SZ_LEG, art='block'):
        """Legende auf halber Höhe am rechten Rand, mit weißer Hinterlegung —
        so kreuzt keine Datenlinie den Text. `rechts` ist die rechte Kante,
        `mitte` die senkrechte Mitte des Blocks."""
        schritt = size + 8
        bh = len(eintraege) * schritt + 8
        bb = max(breite(l, size) for _, l in eintraege) + size + 18
        x0 = rechts - bb
        y0 = mitte - bh / 2
        self.rechteck(x0, y0, bb, bh, '#ffffff', rx=3)
        self.s.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bb:.1f}" '
                      f'height="{bh:.1f}" fill="none" stroke="{C_GRID}" rx="3"/>')
        cy = y0 + 8
        for farbe, lab in eintraege:
            if art == 'linie':
                self.linie(x0 + 8, cy + size / 2 - 1, x0 + 8 + size, cy + size / 2 - 1,
                           farbe, 2.8)
            else:
                self.rechteck(x0 + 8, cy, size - 3, size - 3, farbe, rx=2)
            self.text(x0 + 8 + size + 6, cy + size - 4, lab, size=size,
                      fill=C_VALUE, anchor='start')
            cy += schritt
        return x0

    # -------------------------------------------------------------- Heatmap
    def heatmap(self, L, T, spalten, zeilen, werte, rampe, zellw=None, zellh=None,
                fmt=lambda v: de(v, 2), schwelle=0.55, leer=None):
        n_s, n_z = len(spalten), len(zeilen)
        cw = zellw or 92
        ch = zellh or 52
        mx = max(max(r) for r in werte) or 1.0
        for i in range(n_z):
            for j in range(n_s):
                v = werte[i][j]
                t = v / mx if mx else 0
                x, y = L + j * cw, T + i * ch
                if leer is not None and v <= leer:
                    self.rechteck(x, y, cw - 3, ch - 3, '#f4f4f4', rx=2)
                    self.text(x + (cw - 3) / 2, y + (ch - 3) / 2 + 6, '–',
                              size=SZ_LABEL, fill=C_TICK)
                    continue
                self.rechteck(x, y, cw - 3, ch - 3, misch(rampe[0], rampe[1], t), rx=2)
                self.text(x + (cw - 3) / 2, y + (ch - 3) / 2 + 6, fmt(v),
                          size=SZ_VALUE, fill='#ffffff' if t > schwelle else C_VALUE,
                          weight='bold' if t > schwelle else None)
        for j, sp in enumerate(spalten):
            self.text(L + j * cw + (cw - 3) / 2, T - 12, sp, size=SZ_LABEL, fill=C_LABEL)
        for i, ze in enumerate(zeilen):
            self.text(L - 12, T + i * ch + (ch - 3) / 2 + 6, ze, size=SZ_LABEL,
                      fill=C_VALUE, anchor='end')
        return L + n_s * cw, T + n_z * ch

    def skala(self, x, y, breite, rampe, links, rechts, hoehe=13):
        """Kleine Farbskala unter einer Heatmap."""
        n = 40
        for k in range(n):
            self.rechteck(x + k * breite / n, y, breite / n + 0.6, hoehe,
                          misch(rampe[0], rampe[1], k / (n - 1)), rx=0)
        self.text(x - 10, y + hoehe, links, size=SZ_TICK, fill=C_TICK, anchor='end')
        self.text(x + breite + 10, y + hoehe, rechts, size=SZ_TICK, fill=C_TICK,
                  anchor='start')

    def speichern(self, pfad):
        self.s.append('</svg>')
        open(pfad, 'w', encoding='utf-8').write('\n'.join(self.s))
        return pfad


def breite(s, size):
    """Näherung der Textbreite in SVG-Einheiten (Helvetica)."""
    schmal = set("iljtfrI.,:;'| ")
    return sum(size * (0.34 if c in schmal else 0.56) for c in str(s))


def misch(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    r = [round(a[i] + (b[i] - a[i]) * t) for i in range(3)]
    return '#%02x%02x%02x' % tuple(r)


# Farbverläufe für Heatmaps (weiß -> Palettenfarbe)
RAMPE_ANTEIL   = ('#ffffff', '#46CDB8')
RAMPE_ANZAHL   = ('#ffffff', '#5B6CB8')
RAMPE_KONTROLLE = ('#ffffff', '#E8B14C')
