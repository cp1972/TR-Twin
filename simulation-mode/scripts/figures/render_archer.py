#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zeichnet Kapitel 9, Abbildung 3 (Archer, morphogenetischer Zyklus) aus der Ausgabe von
runs/archer_zyklus.js neu. Die bestehende SVG-Datei dient als Vorlage (Achsen, Legende, Stil);
ersetzt werden nur die drei Linien und ihre Punkte.

    python3 render_archer.py archer_zyklus.json ../../figures/archer_morphogenese.svg
"""
import json, re, sys

FARBE = {'morphogenese': '#46CDB8', 'verriegelt': '#8C92EC', 'morphostase': '#bbb'}
X = [120.0, 252.5, 385.0, 517.5, 650.0]
y = lambda v: 350.0 - v * 687.5            # Achse: 0 bei y=350, 0,4 bei y=75


def main(inp, svg_pfad):
    d = json.load(open(inp, encoding='utf-8'))
    svg = open(svg_pfad, encoding='utf-8').read()
    for k, farbe in FARBE.items():
        pts = [(x, y(v)) for x, v in zip(X, d[k])]
        poly = ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts)
        svg, n = re.subn(r'<polyline points="[^"]*"( fill="none" stroke="' + re.escape(farbe) + r'")',
                         f'<polyline points="{poly}"' + r'\1', svg)
        assert n == 1, (k, n)
        kreise = iter(pts)
        svg = re.sub(r'<circle cx="[\d.]+" cy="[\d.]+"( r="3" fill="' + re.escape(farbe) + r'"/>)',
                     lambda m: '<circle cx="%.1f" cy="%.1f"' % next(kreise) + m.group(1), svg)
    open(svg_pfad, 'w', encoding='utf-8').write(svg)
    print('gezeichnet:', svg_pfad)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
