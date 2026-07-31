#!/usr/bin/env python3
"""
Lebenslinien der Vermittlungsinstanzen: Entstehung -> Stärke (Gewicht) -> Ende.
Aufruf: python3 gen_lifelines.py [light|dark] [ausgabe.svg]
Das helle Thema hat weißen Grund und ist satzfertig.
"""
import csv, sys
THEME = sys.argv[1] if len(sys.argv) > 1 else 'light'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data-mode/figures/instances_lifelines.svg'
PAL = {
 'light': dict(bg='#ffffff', title='#1b1f2a', sub='#5b6472', tick='#8a92a0',
               grid_major='rgba(0,0,0,0.13)', grid_minor='rgba(0,0,0,0.06)',
               base='rgba(0,0,0,0.22)', span='#7a8290', foot='#9aa1ad', peaktxt='#6b7280',
               lane=dict(culture='#B07A12', bridge='#9A4E86', media='#256AA0'), fill=0.18),
 'dark':  dict(bg='#0d1018', title='#e9eaf2', sub='#9aa3b8', tick='#9aa3b8',
               grid_major='rgba(255,255,255,0.10)', grid_minor='rgba(255,255,255,0.045)',
               base='rgba(255,255,255,0.16)', span='#7f87a0', foot='#5f677d', peaktxt='#9aa3b8',
               lane=dict(culture='#E9D8A6', bridge='#D6A2C4', media='#6FA8C7'), fill=0.20),
}[THEME]
COL = PAL['lane']
rows = list(csv.DictReader(open('data-mode/data/instances/instances_probe_demo.csv')))
inst = {}
for r in rows:
    inst.setdefault(r['aid'], []).append((int(r['year']), float(r['weight']), r['structure'], r['sequence']))
for a in inst: inst[a].sort()
def lane(s, q):
    return 'culture' if (s=='A' and q=='A') else ('bridge' if (s=='A' and q=='D') else ('media' if s=='D' else 'other'))
LANE = {a: lane(v[0][2], v[0][3]) for a, v in inst.items()}
NAME = {'mechanics_magazine':"Mechanics' Magazine",'secular_review':"Secular Review",'bakunin_press':"Bakunin Press",
        'cotton_factory_times':"Cotton Factory Times",'reuters':"Reuters",'daily_herald':"Daily Herald"}
CONT = {'reuters': True}
LANELAB = {'culture':'CULTURE CORE \u00b7 A\u00b7seqA','bridge':'PUBLISHING BRIDGE \u00b7 A\u00b7seqD','media':'MEDIA \u00b7 D\u00b7seqD'}
order = ['culture','bridge','media']
groups = {l: sorted([a for a in inst if LANE[a]==l], key=lambda a: inst[a][0][0]) for l in order}
W,LM,RM = 1060,210,46
TM,RH,BH = 104,82,46
Y0,Y1 = 1815,1998
rowlist = [(l,a) for l in order for a in groups[l]]
H = TM + len(rowlist)*RH + 34
def xs(y): return LM + (y-Y0)/(Y1-Y0)*(W-RM-LM)
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace("'",'&#39;')
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,sans-serif">']
S.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAL["bg"]}"/>')
S.append(f'<text x="{LM}" y="40" fill="{PAL["title"]}" font-size="21" font-weight="600">Mediation instances \u2014 lifelines, force and fate</text>')
S.append(f'<text x="{LM}" y="62" fill="{PAL["sub"]}" font-size="12.5">Existence span (birth \u2192 closure); filled height = weight (force as target share, 0\u20131). Demo extract, milestone-anchored.</text>')
for y in range(1825,1991,25):
    x=xs(y); major=(y%50==0)
    S.append(f'<line x1="{x:.1f}" y1="{TM-8}" x2="{x:.1f}" y2="{H-22}" stroke="{PAL["grid_major"] if major else PAL["grid_minor"]}" stroke-width="1"/>')
    if major: S.append(f'<text x="{x:.1f}" y="{TM-14}" fill="{PAL["tick"]}" font-size="11.5" text-anchor="middle" font-family="ui-monospace,monospace">{y}</text>')
lab={'culture':'culture core','bridge':'publishing bridge','media':'media'}
for i,(l,a) in enumerate(rowlist):
    yb=TM+i*RH+RH-22; col=COL[l]; pts=inst[a]
    b,d=pts[0][0],pts[-1][0]; xb,xd=xs(b),xs(d)
    if i==0 or rowlist[i-1][0]!=l:
        S.append(f'<line x1="{LM}" y1="{TM+i*RH-2}" x2="{W-RM}" y2="{TM+i*RH-2}" stroke="{PAL["grid_minor"]}" stroke-width="1"/>')
        S.append(f'<text x="{LM}" y="{TM+i*RH+13}" fill="{col}" font-size="10" font-weight="600" letter-spacing="0.5" font-family="ui-monospace,monospace">{LANELAB[l]}</text>')
    S.append(f'<line x1="{xb:.1f}" y1="{yb}" x2="{xd:.1f}" y2="{yb}" stroke="{PAL["base"]}" stroke-width="1"/>')
    poly=[f'{xb:.1f},{yb}']+[f'{xs(yr):.1f},{yb-w*BH:.1f}' for (yr,w,_,_) in pts]+[f'{xd:.1f},{yb}']
    S.append(f'<polygon points="{" ".join(poly)}" fill="{col}" fill-opacity="{PAL["fill"]}"/>')
    edge=' '.join(f'{xs(yr):.1f},{yb-w*BH:.1f}' for (yr,w,_,_) in pts)
    S.append(f'<polyline points="{edge}" fill="none" stroke="{col}" stroke-width="1.8" stroke-linejoin="round"/>')
    S.append(f'<circle cx="{xb:.1f}" cy="{yb}" r="4" fill="{col}"/>')
    if CONT.get(a):
        S.append(f'<path d="M {xd-2:.1f} {yb-5} L {xd+7:.1f} {yb} L {xd-2:.1f} {yb+5} Z" fill="{col}"/>')
    else:
        S.append(f'<line x1="{xd:.1f}" y1="{yb-7}" x2="{xd:.1f}" y2="{yb+7}" stroke="{col}" stroke-width="2.2"/>')
    pk=max(pts,key=lambda t:t[1]); pkx=xs(pk[0]); pky=yb-pk[1]*BH
    S.append(f'<circle cx="{pkx:.1f}" cy="{pky:.1f}" r="2.6" fill="{PAL["bg"]}" stroke="{col}" stroke-width="1.4"/>')
    S.append(f'<text x="{pkx:.1f}" y="{pky-6:.1f}" fill="{PAL["peaktxt"]}" font-size="9.5" text-anchor="middle" font-family="ui-monospace,monospace">{pk[0]} \u00b7 {pk[1]:.2f}</text>')
    S.append(f'<text x="{LM-12}" y="{yb-4}" fill="{col}" font-size="13" text-anchor="end" font-weight="600">{esc(NAME[a])}</text>')
    tail=' \u2192' if CONT.get(a) else ''
    S.append(f'<text x="{LM-12}" y="{yb+12}" fill="{PAL["span"]}" font-size="10" text-anchor="end" font-family="ui-monospace,monospace">{b}\u2013{d}{tail}</text>')
S.append(f'<text x="{LM}" y="{H-8}" fill="{PAL["foot"]}" font-size="9.5">\u25cf birth   \u2502 closure   \u25b6 continues   \u25cb peak (year \u00b7 weight) \u2014 Theory of Relation \u00b7 digital twin</text>')
S.append('</svg>')
open(OUT,'w').write('\n'.join(S))
print(f"\u2713 {THEME} -> {OUT} ({H}px)")
