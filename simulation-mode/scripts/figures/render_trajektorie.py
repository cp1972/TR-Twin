#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rendert eine Struktur-Trajektorie (Schritt-Lauf) als SVG im Report-Stil."""
import json, sys

def render_trajektorie(data, untertitel="Neutrales Szenario, Seed 1, 1819 Schritte; Anteil am Feld in Prozent",
                       out="trajektorie.svg"):
    S = data["S"]; n = len(S)
    W, H = 780, 430
    L, R, TOP, BOT = 72, 724, 54, 372
    COLORS = ["#E8B14C", "#46CDB8", "#E36F9E", "#8C92EC"]   # Kultur, Politik, Wirtschaft, Medien
    NAMES  = ["Kultur", "Politik", "Wirtschaft", "Medien"]

    def x(i): return L + i/(n-1)*(R-L)
    def y(pct): return BOT - pct/100*(BOT-TOP)

    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">']
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
    s.append(f'<text x="40" y="47" font-size="11" fill="#777">{untertitel}</text>')

    # horizontale Gitter + %-Beschriftung
    for pct in (0, 25, 50, 75, 100):
        yy = y(pct)
        s.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{R}" y2="{yy:.1f}" stroke="#e7e7e7" stroke-width="1"/>')
        s.append(f'<text x="{L-8}" y="{yy+3:.1f}" font-size="10" fill="#9a9a9a" text-anchor="end">{pct}</text>')
    # vertikale Gitter + Schritt-Beschriftung
    for st in (0, 500, 1000, 1500, n-1):
        xx = x(st)
        s.append(f'<line x1="{xx:.1f}" y1="{TOP}" x2="{xx:.1f}" y2="{BOT}" stroke="#e7e7e7" stroke-width="1"/>')
        s.append(f'<text x="{xx:.1f}" y="388" font-size="10" fill="#9a9a9a" text-anchor="middle">{st if st!=n-1 else n}</text>')
    s.append(f'<text x="398" y="404" font-size="11" fill="#555" text-anchor="middle">Simulationsschritt</text>')

    # Marker: wo überschreitet die dominante Struktur 50 % / 75 %?
    last = S[-1]; dom = last.index(max(last))
    def cross(p):
        for i in range(n):
            if S[i][dom] >= p: return i
        return -1
    for p, side in ((0.50, "end"), (0.75, "start")):
        ci = cross(p)
        if ci >= 0:
            xx = x(ci)
            s.append(f'<line x1="{xx:.1f}" y1="{TOP}" x2="{xx:.1f}" y2="{BOT}" stroke="#bbb" stroke-width="1" stroke-dasharray="3 3"/>')
            dx = -4 if side == "end" else 4
            yy = 66 if p == 0.50 else 81
            s.append(f'<text x="{xx+dx:.1f}" y="{yy}" font-size="9" fill="#999" text-anchor="{side}">{NAMES[dom]} {int(p*100)} % (Schritt {ci})</text>')

    # Polylinien der vier Strukturen
    step = max(1, n//360)   # leichte Ausdünnung wie im Original
    for k in range(4):
        pts = " ".join(f"{x(i):.1f},{y(S[i][k]*100):.1f}" for i in range(0, n, step))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{COLORS[k]}" stroke-width="2.2"/>')

    # Legende oben rechts
    ly = 51
    for k in range(4):
        s.append(f'<rect x="574" y="{ly}" width="11" height="11" fill="{COLORS[k]}"/>')
        s.append(f'<text x="590" y="{ly+9}" font-size="11" fill="#2b2b2b">{NAMES[k]}</text>')
        ly += 16

    s.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(s))
    return out

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/tr-headless/out/traj_emirbayer.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/tr-headless/out/trajektorie_report.svg"
    data = json.load(open(inp, encoding="utf-8"))
    print("gerendert:", render_trajektorie(data, out=out))
