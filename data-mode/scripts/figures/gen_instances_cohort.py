#!/usr/bin/env python3
"""
Vollständige Instanzenkohorte für den Erhebungsmodus: übernimmt die 60 Instanzen des
Verzeichnisses (Gründung, Struktur, Sequenz, Kategorie) und legt eine GENERISCHE
Gewichtskurve darüber (Gründung -> Höhepunkt -> Rückgang) über eine geschätzte
Lebensdauer. Die Gewichte sind illustrativ.
"""
import csv
rows=list(csv.DictReader(open('data-mode/data/instances/instances_extract_contract.csv')))
by={}
for r in rows:
    a=r['aid']; by.setdefault(a,[]).append(r)
out=[('aid','year','structure','category','sequence','weight')]
CAP=1966
for a,rs in by.items():
    rs=sorted(rs,key=lambda r:int(r['year']))
    f=int(rs[0]['year']); base=rs[0]
    yrs=[int(r['year']) for r in rs]; ymax=max(yrs)
    h=0
    for ch in a: h=(h*31+ord(ch))&0x7fffffff
    span=35+(h%26)                 # 35..60 ans
    close=min(CAP,max(f+span,ymax))
    if close<=f: close=f+30
    peakh=0.40+(h%5)*0.05          # 0.40..0.60
    pky=f+round(0.40*(close-f))
    s=base['structure']; q=base['sequence']; c=base['category'] or 'aspirant'
    pts=[(f,0.12),(pky,round(peakh,2)),(close,0.08)]
    # doppelte Jahreseinträge entfernen
    seen=set(); cpts=[]
    for (yy,ww) in pts:
        if yy in seen: continue
        seen.add(yy); cpts.append((yy,ww))
    for (yy,ww) in cpts:
        out.append((a,yy,s,c,q,ww))
with open('data-mode/data/instances/instances_cohort_demo.csv','w',newline='') as fo:
    w=csv.writer(fo); w.writerows(out)
print(f"\u2713 cohorte d'instances : {len(by)} instances, {len(out)-1} lignes")
