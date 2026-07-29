#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schema-Renderer im Report-Stil (ohne eingebrannten 'Abbildung'-Titel)."""

COLORS = ["#E8B14C", "#46CDB8", "#E36F9E", "#8C92EC"]   # K, P, W, M
KPWM = ["K", "P", "W", "M"]

def _hdr(W, H, untertitel):
    return [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">',
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>',
            f'<text x="40" y="47" font-size="11" fill="#777">{untertitel}</text>']

def render_endzustand(theory, sizes_pct, R, GINI, untertitel, out):
    """Zwei Panels: links TR-Referenz (25/25/25/25), rechts Theorie."""
    W, H = 780, 430
    s = _hdr(W, H, untertitel)
    def panel(x0, x1, header, vals, r, gini, hx):
        BOT, TOP = 360.0, 80.0                      # 0% .. 100%
        out = [f'<text x="{hx}" y="70" font-size="12.5" font-family="Georgia,serif" fill="#2b2b2b" text-anchor="middle">{header}</text>']
        for pct in (0, 25, 50, 75, 100):
            yy = BOT - pct/100*(BOT-TOP)
            out.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="#e7e7e7"/>')
            out.append(f'<text x="{x0-6}" y="{yy+3:.1f}" font-size="9" fill="#9a9a9a" text-anchor="end">{pct}</text>')
        bx = x0 + 12
        for k in range(4):
            h = vals[k]/100*(BOT-TOP); y = BOT - h
            out.append(f'<rect x="{bx:.1f}" y="{y:.1f}" width="42" height="{h:.1f}" fill="{COLORS[k]}" rx="2"/>')
            out.append(f'<text x="{bx+21:.1f}" y="{y-5:.1f}" font-size="10" fill="#2b2b2b" text-anchor="middle">{round(vals[k])}</text>')
            out.append(f'<text x="{bx+21:.1f}" y="375.0" font-size="9.5" fill="#555" text-anchor="middle">{KPWM[k]}</text>')
            bx += 62
        out.append(f'<text x="{hx}" y="392" font-size="11" fill="#444" text-anchor="middle">R = {r:.2f}   ·   GINI = {gini:.2f}</text>')
        return out
    s += panel(58, 306, "Theorie der Relation (Referenz)", [25,25,25,25], 1.00, 0.00, 190)
    s += panel(428, 676, theory, sizes_pct, R, GINI, 560)
    s.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(s))
    return out

def render_reziprozitaet(bars, untertitel, out):
    """N Balken (0..1): jeweils {value, l1, l2, color}."""
    W, H = 780, 410
    s = _hdr(W, H, untertitel)
    BOT, TOP = 330.0, 90.0
    for i, g in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
        yy = BOT - g*(BOT-TOP)
        s.append(f'<line x1="110" y1="{yy:.1f}" x2="750" y2="{yy:.1f}" stroke="#e7e7e7"/>')
        s.append(f'<text x="104" y="{yy+3:.1f}" font-size="10" fill="#9a9a9a" text-anchor="end">{g:.2f}</text>')
    xs = [120, 330, 540]
    for b, x0 in zip(bars, xs):
        h = b["value"]*(BOT-TOP); y = BOT - h; cx = x0 + 60
        s.append(f'<rect x="{x0}.0" y="{y:.1f}" width="120" height="{h:.1f}" fill="{b["color"]}" rx="3"/>')
        s.append(f'<text x="{cx}.0" y="{y-7:.1f}" font-size="13" fill="#2b2b2b" text-anchor="middle" font-family="Georgia,serif">{b["value"]:.2f}</text>')
        s.append(f'<text x="{cx}.0" y="348.0" font-size="10.5" fill="#555" text-anchor="middle">{b["l1"]}</text>')
        s.append(f'<text x="{cx}.0" y="362.0" font-size="10.5" fill="#555" text-anchor="middle">{b["l2"]}</text>')
    s.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(s))
    return out
