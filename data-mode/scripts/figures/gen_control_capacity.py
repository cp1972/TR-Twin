#!/usr/bin/env python3
"""
Abgeleitete Kontrollkapazität je Struktur (die Untergrenze von Ictrl), berechnet aus
einem Bestand von Kontrollinstanzen. Die Abstufung ist hergeleitet, nicht gesetzt.
Helles Thema, satzfertig.
"""
import csv, math, sys
KCAP,S0,LAM=1.0,0.5,0.8
THEME=sys.argv[1] if len(sys.argv)>1 else 'light'
OUT=sys.argv[2] if len(sys.argv)>2 else 'data-mode/figures/control_capacity.svg'
YEAR=int(sys.argv[4]) if len(sys.argv)>4 else 1900
rows=list(csv.DictReader(open(sys.argv[3] if len(sys.argv)>3 else 'data-mode/data/instances/control_parc_demo.csv')))
byA={}
for r in rows: byA.setdefault(r['aid'],[]).append(r)
SX={'A':0,'B':1,'C':2,'D':3}
wByX={0:[],1:[],2:[],3:[]}
for a,rs in byA.items():
    rs=sorted(rs,key=lambda r:int(r['year']))
    ys=[int(r['year']) for r in rs]
    if YEAR<ys[0] or YEAR>ys[-1]: continue
    # Gewichte interpolieren
    lo=rs[0]; hi=rs[-1]
    for r in rs:
        if int(r['year'])<=YEAR: lo=r
    for r in reversed(rs):
        if int(r['year'])>=YEAR: hi=r
    wl,wh=float(lo['weight']),float(hi['weight'])
    yl,yh=int(lo['year']),int(hi['year'])
    wv=wl if yh==yl else wl+(wh-wl)*(YEAR-yl)/(yh-yl)
    wByX[SX[rs[0]['structure']]].append(wv)
def gini(a):
    n=len(a)
    if n<2: return 0.0
    s=sum(a)
    if s<=0: return 0.0
    b=sorted(a); acc=sum((i+1)*b[i] for i in range(n))
    return max(0.0,min(1.0,(2*acc)/(n*s)-(n+1)/n))
cap=[1,1,1,1]; info=[]
for x in range(4):
    ws=wByX[x]; n=len(ws); W=sum(ws)
    strat=gini(ws)*(1-1/n) if n>1 else 0.0
    sat=1-math.exp(-LAM*W)
    cap[x]=1+KCAP*sat*(S0+(1-S0)*strat)
    info.append((n,W,strat))
PAL={'light':dict(bg='#ffffff',title='#1b1f2a',sub='#5b6472',tick='#8a92a0',axis='rgba(0,0,0,0.25)',grid='rgba(0,0,0,0.06)',foot='#9aa1ad'),
     'dark':dict(bg='#0d1018',title='#e9eaf2',sub='#9aa3b8',tick='#9aa3b8',axis='rgba(255,255,255,0.3)',grid='rgba(255,255,255,0.07)',foot='#5f677d')}[THEME]
COL=['#2E6DA4','#6C5BA0','#4E9A4E','#C76A2A']
NM=['A · Culture','B · Politics','C · Economy','D · Media']
W,H=760,420; L=70; R=40; T=96; B=92
bw=(W-L-R)/4*0.56; gap=(W-L-R)/4
ymax=max(1.6,max(cap)+0.08)
def ys(v): return T+(H-T-B)-(v-1.0)/(ymax-1.0)*(H-T-B)
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,sans-serif">']
S.append(f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>')
S.append(f'<text x="{L}" y="38" fill="{PAL["title"]}" font-size="19" font-weight="600">Control capacity by structure \u2014 derived, not decreed</text>')
S.append(f'<text x="{L}" y="59" fill="{PAL["sub"]}" font-size="12">Ictrl floor = 1 + K\u00b7sat(\u03a3 weights)\u00b7(S\u2080+(1\u2212S\u2080)\u00b7stratification), stratification = Gini\u00b7(1\u22121/n). Control parc at {YEAR}.</text>')
# axe y
for gv in (1.0,1.2,1.4,1.6):
    yy=ys(gv); S.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="{PAL["grid"]}" stroke-width="1"/>')
    S.append(f'<text x="{L-8}" y="{yy+4:.1f}" fill="{PAL["tick"]}" font-size="10" text-anchor="end" font-family="ui-monospace,monospace">{gv:.1f}</text>')
S.append(f'<line x1="{L}" y1="{ys(1.0):.1f}" x2="{W-R}" y2="{ys(1.0):.1f}" stroke="{PAL["axis"]}" stroke-width="1.2"/>')
S.append(f'<text x="{L-8}" y="{ys(1.0)+18:.1f}" fill="{PAL["tick"]}" font-size="8.5" text-anchor="end">baseline</text>')
for x in range(4):
    cx=L+gap*x+gap/2; bx=cx-bw/2; top=ys(cap[x]); base=ys(1.0)
    S.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{base-top:.1f}" rx="3" fill="{COL[x]}" fill-opacity="0.85"/>')
    S.append(f'<text x="{cx:.1f}" y="{top-8:.1f}" fill="{PAL["title"]}" font-size="13" font-weight="600" text-anchor="middle" font-family="ui-monospace,monospace">{cap[x]:.3f}</text>')
    S.append(f'<text x="{cx:.1f}" y="{H-B+20:.1f}" fill="{COL[x]}" font-size="12.5" font-weight="600" text-anchor="middle">{NM[x]}</text>')
    n,Wt,st=info[x]
    S.append(f'<text x="{cx:.1f}" y="{H-B+38:.1f}" fill="{PAL["sub"]}" font-size="9.5" text-anchor="middle" font-family="ui-monospace,monospace">n={n} \u00b7 \u03a3w={Wt:.2f}</text>')
    S.append(f'<text x="{cx:.1f}" y="{H-B+52:.1f}" fill="{PAL["sub"]}" font-size="9.5" text-anchor="middle" font-family="ui-monospace,monospace">strat={st:.3f}</text>')
S.append(f'<text x="{L}" y="{H-12}" fill="{PAL["foot"]}" font-size="9.5">More numerous, stronger and better-stratified control instances \u2192 higher capacity \u2014 derived from the parc, not decreed. Theory of Relation \u00b7 digital twin.</text>')
S.append('</svg>')
open(OUT,'w').write('\n'.join(S))
print('\u2713',THEME,'->',OUT,'· cap =',[round(c,3) for c in cap])
