#!/usr/bin/env python3
"""Heatmap : capacite de controle PAR SEQUENCE (capCell[structure][sequence]) = regulation
differentielle. Recalcule depuis le parc. Theme clair (publication)."""
import csv, math, sys
KCAP,S0,LAM=1.0,0.5,0.8; YEAR=int(sys.argv[4]) if len(sys.argv)>4 else 1900
THEME=sys.argv[1] if len(sys.argv)>1 else 'light'
OUT=sys.argv[2] if len(sys.argv)>2 else 'data-mode/figures/control_profile.svg'
SX={'A':0,'B':1,'C':2,'D':3}
rows=list(csv.DictReader(open(sys.argv[3] if len(sys.argv)>3 else 'data-mode/data/instances/control_parc_demo.csv')))
byA={}
for r in rows: byA.setdefault(r['aid'],[]).append(r)
cellW={x:{q:[] for q in range(4)} for x in range(4)}
for a,rs in byA.items():
    rs=sorted(rs,key=lambda r:int(r['annee'])); ys=[int(r['annee']) for r in rs]
    if YEAR<ys[0] or YEAR>ys[-1]: continue
    lo=rs[0]; hi=rs[-1]
    for r in rs:
        if int(r['annee'])<=YEAR: lo=r
    for r in reversed(rs):
        if int(r['annee'])>=YEAR: hi=r
    wl,wh=float(lo['poids']),float(hi['poids']); yl,yh=int(lo['annee']),int(hi['annee'])
    wv=wl if yh==yl else wl+(wh-wl)*(YEAR-yl)/(yh-yl)
    cellW[SX[rs[0]['structure']]][SX[rs[0]['sequence']]].append(wv)
def gini(a):
    n=len(a)
    if n<2: return 0.0
    s=sum(a);
    if s<=0: return 0.0
    b=sorted(a); acc=sum((i+1)*b[i] for i in range(n))
    return max(0.0,min(1.0,(2*acc)/(n*s)-(n+1)/n))
def capOf(ws):
    n=len(ws)
    if n==0: return 1.0
    W=sum(ws); strat=gini(ws)*(1-1/n) if n>1 else 0.0; sat=1-math.exp(-LAM*W)
    return 1+KCAP*sat*(S0+(1-S0)*strat)
cap=[[capOf(cellW[x][q]) for q in range(4)] for x in range(4)]
mx=max(max(r) for r in cap); mx=max(mx,1.001)
PAL={'light':dict(bg='#ffffff',title='#1b1f2a',sub='#5b6472',lab='#3b4252',empty='#f1f3f6',grid='#ffffff',foot='#9aa1ad',hue=(38,110,164)),
     'dark':dict(bg='#0d1018',title='#e9eaf2',sub='#9aa3b8',lab='#c7ccda',empty='#161a25',grid='#0d1018',foot='#5f677d',hue=(111,168,199))}[THEME]
NMS=['A · Culture','B · Politics','C · Economy','D · Media']
SQ=['seq A','seq B','seq C','seq D']
W,H=720,575; L=150; T=120; cs=104
def col(v):
    t=(v-1.0)/(mx-1.0) if mx>1 else 0
    t=max(0,min(1,t)); r,g,b=PAL['hue']
    # mélange empty -> hue
    import re
    er,eg,eb=(int(PAL['empty'][1:3],16),int(PAL['empty'][3:5],16),int(PAL['empty'][5:7],16))
    R=int(er+(r-er)*t); G=int(eg+(g-eg)*t); B=int(eb+(b-eb)*t)
    return f'#{R:02x}{G:02x}{B:02x}'
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,sans-serif">']
S.append(f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>')
S.append(f'<text x="{L-110}" y="40" fill="{PAL["title"]}" font-size="19" font-weight="600">Control capacity by sequence \u2014 differential regulation</text>')
S.append(f'<text x="{L-110}" y="61" fill="{PAL["sub"]}" font-size="12">Each control instance regulates a target sequence; capCell[structure][sequence] amplifies that cell\u2019s reactivity. Parc at {YEAR}.</text>')
for q in range(4):
    S.append(f'<text x="{L+q*cs+cs/2:.0f}" y="{T-12}" fill="{PAL["lab"]}" font-size="12" text-anchor="middle" font-weight="600">{SQ[q]}</text>')
for x in range(4):
    cy=T+x*cs
    S.append(f'<text x="{L-12}" y="{cy+cs/2+4:.0f}" fill="{PAL["lab"]}" font-size="12.5" text-anchor="end" font-weight="600">{NMS[x]}</text>')
    for q in range(4):
        cx=L+q*cs; v=cap[x][q]
        S.append(f'<rect x="{cx}" y="{cy}" width="{cs-4}" height="{cs-4}" rx="5" fill="{col(v)}" stroke="{PAL["grid"]}" stroke-width="2"/>')
        if v>1.001:
            tcol='#ffffff' if (v-1)/(mx-1)>0.5 else PAL['lab']
            S.append(f'<text x="{cx+(cs-4)/2:.0f}" y="{cy+(cs-4)/2+5:.0f}" fill="{tcol}" font-size="14" font-weight="600" text-anchor="middle" font-family="ui-monospace,monospace">{v:.3f}</text>')
        else:
            S.append(f'<text x="{cx+(cs-4)/2:.0f}" y="{cy+(cs-4)/2+5:.0f}" fill="{PAL["sub"]}" font-size="11" text-anchor="middle" font-family="ui-monospace,monospace">\u2013</text>')
S.append(f'<text x="{L-110}" y="{H-14}" fill="{PAL["foot"]}" font-size="9.5">1.000 = no control on that sequence. Each control instance amplifies its target cell \u2014 derived from the parc. Theory of Relation \u00b7 digital twin.</text>')
S.append('</svg>')
open(OUT,'w').write('\n'.join(S))
print('\u2713',THEME,'->',OUT)
