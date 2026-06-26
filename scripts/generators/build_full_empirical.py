#!/usr/bin/env python3
"""Cohorte d'instances COMPLETE (mediation + controle) pour la config cours, derivee du catalogue.
Les lignes de controle (categorie=controle) sont auto-routees vers la capacite par le twin ;
les autres pilotent g (mediation, courbe generique montee-apogee-declin)."""
import csv
found={}; meta={}
for r in csv.DictReader(open('examples/working-class-authors/data/instances/instances_extract_contract.csv')):
    a=r['aid']; y=int(r['annee'])
    if a not in found or y<found[a]: found[a]=y
    meta.setdefault(a,r)  # structure/seq/categorie d'origine
# CONTROLE : aid -> (structure, seq-cible, poids)
CTRL={
 'cambridge_university':('A','A',0.60),'st_andrews_university':('A','A',0.60),
 'university_of_london':('A','A',0.60),'harvard_university':('A','A',0.60),
 'university_college':('A','A',0.45),'reading_university_college':('A','A',0.45),
 'city_of_london_college':('A','A',0.45),'anderson_s_college_and_museu':('A','A',0.45),
 'bible_training_college':('A','A',0.45),'aberdeen_grammar_school':('A','A',0.35),
 'shrewsbury_school':('A','A',0.35),
 'secular_review':('A','D',0.42),'elizabethan_literary_society':('A','D',0.40),
 'manchester_literary_club':('A','D',0.40),'victoria_and_albert_museum':('A','D',0.45),
 'national_secular_society':('A','D',0.35),'leicester_secular_society':('A','D',0.35),
 'oddfellows_sunday_school':('A','D',0.30),'sunday_school_times':('A','D',0.30),
 'temperance_and_general_provi':('C','D',0.35),
 'financial_times':('D','C',0.45),'reuters':('D','D',0.60),
}
END=1966
out=[('aid','annee','structure','categorie','sequence','poids')]
nmed=nctrl=0
for a,f in found.items():
    if a in CTRL:
        s,q,w=CTRL[a]; out.append((a,f,s,'controle',q,w)); out.append((a,END,s,'controle',q,w)); nctrl+=1
    else:
        m=meta[a]; s=m['structure']; q=m['sequence']; c=m['categorie'] or 'aspirant'
        h=0
        for ch in a: h=(h*31+ord(ch))&0x7fffffff
        span=35+(h%26); close=min(END,max(f+span,f+30)); pky=f+round(0.40*(close-f)); peak=round(0.40+(h%5)*0.05,2)
        for (yy,ww) in [(f,0.12),(pky,peak),(close,0.08)]:
            out.append((a,yy,s,c,q,ww))
        nmed+=1
# B illustratif (controle) pour le contraste
for a,s,q,w,f in [('parliamentary_oversight_illus','B','B',0.45,1870),('royal_commission_illus','B','D',0.40,1860)]:
    out.append((a,f,s,'controle',q,w)); out.append((a,END,s,'controle',q,w))
# dédoublonnage années identiques par aid
seen=set(); clean=[out[0]]
for row in out[1:]:
    k=(row[0],row[1])
    if k in seen: continue
    seen.add(k); clean.append(row)
with open('examples/working-class-authors/data/instances/instances_full_empirical.csv','w',newline='') as fo:
    csv.writer(fo).writerows(clean)
print(f"\u2713 cohorte complete : {nmed} mediation + {nctrl} controle reels + 2 B illustratifs · {len(clean)-1} lignes")
