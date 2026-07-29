#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maschinelle Sichtkontrolle: Rand, Überlappung, Schriftgrad."""
import glob, os, sys, xml.etree.ElementTree as ET

def breite(s, size):
    schmal = set("iljtfrI.,:;'| ")
    return sum(size * (0.34 if c in schmal else 0.56) for c in str(s))

def pruefe(pfad, min_pt=7.4, druckbreite_cm=15.0):
    root = ET.fromstring(open(pfad, encoding='utf-8').read())
    vb = [float(v) for v in root.get('viewBox').split()]
    W, H = vb[2], vb[3]
    pt_je_einheit = druckbreite_cm / 2.54 * 72 / W
    probleme = []
    kaesten = []
    for e in root.iter():
        tag = e.tag.split('}')[-1]
        if tag == 'text' and e.text and 'rotate' not in (e.get('transform') or ''):
            x, y = float(e.get('x', 0)), float(e.get('y', 0))
            sz = float(e.get('font-size', 16))
            an = e.get('text-anchor', 'start')
            w = breite(e.text, sz)
            x0 = x if an == 'start' else (x - w / 2 if an == 'middle' else x - w)
            if x0 < -0.5 or x0 + w > W + 0.5:
                probleme.append(f"RAND  '{e.text[:42]}'  [{x0:.0f}..{x0+w:.0f}] / {W:.0f}")
            if y - sz * 0.8 < 0 or y > H:
                probleme.append(f"HÖHE  '{e.text[:42]}'  y={y:.0f} / {H:.0f}")
            if sz * pt_je_einheit < min_pt:
                probleme.append(f"KLEIN '{e.text[:42]}'  {sz*pt_je_einheit:.1f} pt")
            kaesten.append((x0, y - sz * 0.8, x0 + w, y + sz * 0.22, e.text))
        elif tag == 'rect':
            x, y = float(e.get('x', 0)), float(e.get('y', 0))
            w, h = float(e.get('width', 0)), float(e.get('height', 0))
            if x < -0.5 or y < -0.5 or x + w > W + 0.5 or y + h > H + 0.5:
                probleme.append(f"RAND  Fläche [{x:.0f},{y:.0f} {w:.0f}x{h:.0f}]")
    for i in range(len(kaesten)):
        for j in range(i + 1, len(kaesten)):
            a, c = kaesten[i], kaesten[j]
            if min(a[2], c[2]) - max(a[0], c[0]) > 2 and min(a[3], c[3]) - max(a[1], c[1]) > 2:
                probleme.append(f"ÜBERLAPPUNG '{a[4][:26]}' / '{c[4][:26]}'")
    kleinste = min((float(e.get('font-size', 16)) for e in root.iter()
                    if e.tag.endswith('text')), default=0)
    return probleme, W, H, kleinste * pt_je_einheit

if __name__ == '__main__':
    muster = sys.argv[1] if len(sys.argv) > 1 else '*.svg'
    gesamt = 0
    for f in sorted(glob.glob(muster)):
        p, W, H, klein = pruefe(f)
        gesamt += len(p)
        print(f"{os.path.basename(f):36s} {int(W)}x{int(H)}  kleinste Schrift {klein:.1f} pt"
              + (f"   {len(p)} Problem(e)" if p else "   ok"))
        for x in p[:6]:
            print('     !', x)
    print(f"\nProbleme gesamt: {gesamt}")
