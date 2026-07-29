#!/usr/bin/env python3
"""
Vergleich der vier Signale — Zirkulation, Stärke der Instanzen, Ungleichheit,
Reziprozität — je Struktur A/B/C/D und für das Ganze. Helles Thema, satzfertig.
"""
import json, sys
d=json.load(open('/tmp/signals.json'))
THEME=sys.argv[1] if len(sys.argv)>1 else 'light'
OUT=sys.argv[2] if len(sys.argv)>2 else 'data-mode/figures/signals_comparison.svg'
PAL={'light':dict(bg='#ffffff',title='#1b1f2a',sub='#5b6472',tick='#8a92a0',frame='rgba(0,0,0,0.16)',grid='rgba(0,0,0,0.06)',foot='#9aa1ad'),
     'dark':dict(bg='#0d1018',title='#e9eaf2',sub='#9aa3b8',tick='#9aa3b8',frame='rgba(255,255,255,0.16)',grid='rgba(255,255,255,0.06)',foot='#5f677d')}[THEME]
SIG=[('circ','#D98A2B','circulation'),('force','#6B4F9E','instance force'),('gini','#C0392B','inequality (Gini)'),('recip','#2E6DA4','reciprocity')]
years=d['years']; Y0,Y1=years[0],years[-1]
panels=[('0','A \u00b7 Culture'),('1','B \u00b7 Politics'),('2','C \u00b7 Economy'),('3','D \u00b7 Media'),('overall','Overall')]
def series(key,sig): return d['overall'][sig] if key=='overall' else d['struct'][key][sig]
# Zirkulation normieren: Strukturen untereinander vergleichbar; das Ganze auf sein eigenes Maximum
smax=max([max(d['struct'][str(x)]['circ']) for x in range(4)]+[1])
omax=max(d['overall']['circ']+[1])
def cnorm(key,v): return v/(omax if key=='overall' else smax)
def val(key,sig,v): return cnorm(key,v) if sig=='circ' else v   # GINI, Reziprozität und Stärke liegen schon zwischen 0 und 1

W=1180; L=44; R=18; GAP=20; N=5
pw=(W-L-R-(N-1)*GAP)/N; ph=232; TOP=92; BOT=40
H=TOP+ph+BOT
def xs(px,yr): return px+(yr-Y0)/((Y1-Y0)or 1)*pw
def ys(v): return TOP+ph-v*ph   # v in [0,1]
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,sans-serif">']
S.append(f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>')
S.append(f'<text x="{L}" y="34" fill="{PAL["title"]}" font-size="20" font-weight="600">Four signals compared \u2014 by relational structure and overall</text>')
S.append(f'<text x="{L}" y="55" fill="{PAL["sub"]}" font-size="12">Circulation (total movement, normalised to its max) \u00b7 instance force (weight) \u00b7 inequality (Gini) \u00b7 reciprocity. Cohort {Y0}\u2013{Y1}; instances active where present.</text>')
# legende
lx=L
for key,col,lab in SIG:
    S.append(f'<line x1="{lx}" y1="72" x2="{lx+22}" y2="72" stroke="{col}" stroke-width="2.6"/>')
    S.append(f'<text x="{lx+28}" y="76" fill="{PAL["sub"]}" font-size="11.5">{lab}</text>')
    lx+=28+len(lab)*6.6+22
# aggregierte Kennzahl (rechts)
S.append(f'<text x="{W-R}" y="76" fill="{PAL["sub"]}" font-size="10" text-anchor="end">overall: total circ \u00b7 size-weighted force \u00b7 global Gini \u00b7 size-weighted recip</text>')
for pi,(key,lab) in enumerate(panels):
    px=L+pi*(pw+GAP)
    # Rahmen und Raster
    S.append(f'<rect x="{px:.1f}" y="{TOP}" width="{pw:.1f}" height="{ph}" fill="none" stroke="{PAL["frame"]}" stroke-width="1"/>')
    for gy in (0.5,1.0):
        S.append(f'<line x1="{px:.1f}" y1="{ys(gy):.1f}" x2="{px+pw:.1f}" y2="{ys(gy):.1f}" stroke="{PAL["grid"]}" stroke-width="1"/>')
    S.append(f'<text x="{px+pw/2:.1f}" y="{TOP-6}" fill="{PAL["title"]}" font-size="12.5" font-weight="600" text-anchor="middle">{lab}</text>')
    # Achsenbeschriftung
    S.append(f'<text x="{px-4:.1f}" y="{ys(1.0)+4:.1f}" fill="{PAL["tick"]}" font-size="8.5" text-anchor="end" font-family="ui-monospace,monospace">1</text>')
    S.append(f'<text x="{px-4:.1f}" y="{ys(0.0)+2:.1f}" fill="{PAL["tick"]}" font-size="8.5" text-anchor="end" font-family="ui-monospace,monospace">0</text>')
    for yr in (1800,1850,1900,1950):
        if Y0<=yr<=Y1:
            xx=xs(px,yr); S.append(f'<line x1="{xx:.1f}" y1="{TOP+ph:.1f}" x2="{xx:.1f}" y2="{TOP+ph+4:.1f}" stroke="{PAL["tick"]}" stroke-width="1"/>')
            S.append(f'<text x="{xx:.1f}" y="{TOP+ph+15:.1f}" fill="{PAL["tick"]}" font-size="8.5" text-anchor="middle" font-family="ui-monospace,monospace">{yr}</text>')
    # courbes
    for sig,col,lab in SIG:
        arr=series(key,sig)
        pts=' '.join(f'{xs(px,years[i]):.1f},{ys(val(key,sig,arr[i])):.1f}' for i in range(len(years)))
        S.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.5" stroke-linejoin="round" opacity="0.92"/>')
S.append(f'<text x="{L}" y="{H-10}" fill="{PAL["foot"]}" font-size="9.5">Deterministic replay of the digital twin \u00b7 Theory of Relation. Signals normalised to [0,1] for shape comparison.</text>')
S.append('</svg>')
open(OUT,'w').write('\n'.join(S))
print(f"\u2713 {THEME} -> {OUT} ({W}x{H})")
