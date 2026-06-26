#!/usr/bin/env python3
"""Cohorte d'instances complete pour le mode recensement : reprend les 60 instances du
catalogue (fondation, structure, sequence, categorie) et ajoute une courbe de poids
GENERIQUE (fondation -> apogee -> declin) sur une duree de vie estimee. Poids illustratifs."""
import csv
rows=list(csv.DictReader(open('examples/working-class-authors/data/instances/instances_extract_contract.csv')))
by={}
for r in rows:
    a=r['aid']; by.setdefault(a,[]).append(r)
out=[('aid','annee','structure','categorie','sequence','poids')]
CAP=1966
for a,rs in by.items():
    rs=sorted(rs,key=lambda r:int(r['annee']))
    f=int(rs[0]['annee']); base=rs[0]
    yrs=[int(r['annee']) for r in rs]; ymax=max(yrs)
    h=0
    for ch in a: h=(h*31+ord(ch))&0x7fffffff
    span=35+(h%26)                 # 35..60 ans
    close=min(CAP,max(f+span,ymax))
    if close<=f: close=f+30
    peakh=0.40+(h%5)*0.05          # 0.40..0.60
    pky=f+round(0.40*(close-f))
    s=base['structure']; q=base['sequence']; c=base['categorie'] or 'aspirant'
    pts=[(f,0.12),(pky,round(peakh,2)),(close,0.08)]
    # dedoublonnage annees
    seen=set(); cpts=[]
    for (yy,ww) in pts:
        if yy in seen: continue
        seen.add(yy); cpts.append((yy,ww))
    for (yy,ww) in cpts:
        out.append((a,yy,s,c,q,ww))
with open('examples/working-class-authors/data/instances/instances_cohort_demo.csv','w',newline='') as fo:
    w=csv.writer(fo); w.writerows(out)
print(f"\u2713 cohorte d'instances : {len(by)} instances, {len(out)-1} lignes")
