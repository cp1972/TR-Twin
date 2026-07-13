#!/usr/bin/env python3
"""Figure d'approfondissement : circulation transversale atypique (presence des auteurs ouvriers
en A et D) et ses mediations (instances de mediation + capacite de controle), + reciprocite.
Theme clair (publication)."""
import json, math, sys
d=json.load(open('/tmp/course.json'))
THEME=sys.argv[1] if len(sys.argv)>1 else 'light'
OUT=sys.argv[2] if len(sys.argv)>2 else 'examples/working-class-authors/figures/course_transversal.svg'
years=d['years']; Y0,Y1=years[0],years[-1]
PAL={'light':dict(bg='#ffffff',title='#1b1f2a',sub='#5b6472',tick='#8a92a0',frame='rgba(0,0,0,0.16)',grid='rgba(0,0,0,0.06)',foot='#9aa1ad'),
     'dark':dict(bg='#0d1018',title='#e9eaf2',sub='#9aa3b8',tick='#9aa3b8',frame='rgba(255,255,255,0.16)',grid='rgba(255,255,255,0.06)',foot='#5f677d')}[THEME]
SIG=[('presence','#C0392B','working-class presence (crossing in)'),('med','#6B4F9E','mediation instance force'),
     ('ctrl','#1F7A5A','control capacity'),('recip','#2E6DA4','reciprocity of the destination')]
def norm(a):
    mx=max(a) if a else 1
    return [v/mx if mx>0 else 0 for v in a]
def normctrl(a):
    mx=max(a); return [ (v-1)/(mx-1) if mx>1 else 0 for v in a]
def pearson(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    num=sum((a[i]-ma)*(b[i]-mb) for i in range(n)); da=math.sqrt(sum((x-ma)**2 for x in a)); db=math.sqrt(sum((x-mb)**2 for x in b))
    return num/(da*db) if da*db>0 else 0
panels=[('0','A · Culture'),('3','D · Media')]
W=1080; L=52; R=22; GAP=46; N=2
pw=(W-L-R-(N-1)*GAP)/N; ph=300; TOP=132; BOT=46
H=TOP+ph+BOT
def xs(px,yr): return px+(yr-Y0)/((Y1-Y0)or 1)*pw
def ys(v): return TOP+ph-v*ph
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,sans-serif">']
S.append(f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>')
S.append(f'<text x="{L}" y="36" fill="{PAL["title"]}" font-size="20" font-weight="600">Atypical transversal circulation and its mediations</text>')
S.append(f'<text x="{L}" y="58" fill="{PAL["sub"]}" font-size="12.5">Working-class autobiographers reaching Culture (A) and Media (D), with the instances that channel the crossing. Series normalised to [0,1].</text>')
lx=L
for key,col,lab in SIG:
    S.append(f'<line x1="{lx}" y1="78" x2="{lx+22}" y2="78" stroke="{col}" stroke-width="2.6"/>')
    S.append(f'<text x="{lx+28}" y="82" fill="{PAL["sub"]}" font-size="11.5">{lab}</text>')
    lx+=28+len(lab)*6.5+24
for pi,(key,lab) in enumerate(panels):
    px=L+pi*(pw+GAP); st=d['struct'][key]
    series={'presence':norm(st['presence']),'med':norm(st['med']),'ctrl':normctrl(st['ctrl']),'recip':st['recip']}
    S.append(f'<rect x="{px:.1f}" y="{TOP}" width="{pw:.1f}" height="{ph}" fill="none" stroke="{PAL["frame"]}" stroke-width="1"/>')
    for gy in (0.5,1.0): S.append(f'<line x1="{px:.1f}" y1="{ys(gy):.1f}" x2="{px+pw:.1f}" y2="{ys(gy):.1f}" stroke="{PAL["grid"]}" stroke-width="1"/>')
    S.append(f'<text x="{px+pw/2:.1f}" y="{TOP-10}" fill="{PAL["title"]}" font-size="14" font-weight="600" text-anchor="middle">{lab}</text>')
    # corrélations présence~médiation, présence~contrôle (sur la fenêtre où présence>0)
    idx=[i for i in range(len(years)) if st['presence'][i]>0]
    if len(idx)>5:
        P=[st['presence'][i] for i in idx]; M=[st['med'][i] for i in idx]; C=[st['ctrl'][i] for i in idx]
        rM=pearson(P,M); rC=pearson(P,C)
        S.append(f'<rect x="{px+pw/2-150:.1f}" y="{TOP+ph-22}" width="300" height="17" fill="{PAL["bg"]}" opacity="0.82"/>');S.append(f'<text x="{px+pw/2:.1f}" y="{TOP+ph-9}" fill="{PAL["sub"]}" font-size="10.5" text-anchor="middle" font-weight="600">corr(presence, mediation)={rM:.2f} \u00b7 corr(presence, control)={rC:.2f}</text>')
    for yr in (1800,1850,1900,1950):
        if Y0<=yr<=Y1:
            xx=xs(px,yr); S.append(f'<line x1="{xx:.1f}" y1="{TOP+ph:.1f}" x2="{xx:.1f}" y2="{TOP+ph+4:.1f}" stroke="{PAL["tick"]}" stroke-width="1"/>')
            S.append(f'<text x="{xx:.1f}" y="{TOP+ph+16:.1f}" fill="{PAL["tick"]}" font-size="9" text-anchor="middle" font-family="ui-monospace,monospace">{yr}</text>')
    for sig,col,lab in SIG:
        arr=series[sig]; pts=' '.join(f'{xs(px,years[i]):.1f},{ys(arr[i]):.1f}' for i in range(len(years)))
        S.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.7" stroke-linejoin="round" opacity="0.92"/>')
    # marqueur du pic de présence
    P=st['presence']; pmax=max(P); pi2=P.index(pmax); xx=xs(px,years[pi2])
    S.append(f'<line x1="{xx:.1f}" y1="{TOP}" x2="{xx:.1f}" y2="{TOP+ph}" stroke="#C0392B" stroke-width="0.8" stroke-dasharray="3 3" opacity="0.5"/>')
    S.append(f'<text x="{xx:.1f}" y="{TOP-26}" fill="#C0392B" font-size="9.5" text-anchor="middle">peak {years[pi2]}: {pmax}</text>')
S.append(f'<text x="{L}" y="{H-12}" fill="{PAL["foot"]}" font-size="9.5">Deterministic replay (actors + mediation + control). The crossing into A and D builds together with the instances that channel it. Theory of Relation \u00b7 digital twin.</text>')
S.append('</svg>')
open(OUT,'w').write('\n'.join(S))
print('\u2713',THEME,'->',OUT)
