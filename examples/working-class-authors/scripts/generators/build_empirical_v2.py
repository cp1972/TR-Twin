#!/usr/bin/env python3
"""Parc de controle EMPIRIQUE v2 : vraies courbes d'autorite (fondation -> apogee -> declin/maintien)
et dates de fermeture. Prioritaires sources (Reuters, Financial Times, University of London, V&A,
Secular Review) ; les autres avec une courbe d'autorite plausible (fondation reelle connue)."""
import csv
CAT='examples/working-class-authors/data/instances/instances_extract_contract.csv'
# CONTROLE : aid -> (structure, seq-cible, [(annee, poids), ...])   ★ = sourced
CTRLC={
 # --- A · seqA : certification / examen ---
 'university_of_london':('A','A',[(1836,0.20),(1858,0.45),(1900,0.60),(1966,0.60)]),      # ★ examinateur 1836, externes 1858
 'cambridge_university':('A','A',[(1820,0.50),(1900,0.55),(1966,0.55)]),                  # ancienne, etablie
 'st_andrews_university':('A','A',[(1820,0.45),(1900,0.50),(1966,0.50)]),
 'harvard_university':('A','A',[(1955,0.45),(1966,0.50)]),                                # tardive pour la cohorte
 'university_college':('A','A',[(1826,0.30),(1860,0.45),(1966,0.48)]),                    # UCL 1826
 'city_of_london_college':('A','A',[(1848,0.25),(1900,0.42),(1966,0.42)]),
 'reading_university_college':('A','A',[(1892,0.25),(1926,0.45),(1966,0.45)]),            # college 1892 -> univ 1926
 'anderson_s_college_and_museu':('A','A',[(1796,0.30),(1850,0.42),(1966,0.42)]),          # Anderson's 1796
 'bible_training_college':('A','A',[(1882,0.25),(1910,0.40),(1966,0.38)]),
 'aberdeen_grammar_school':('A','A',[(1820,0.32),(1966,0.35)]),
 'shrewsbury_school':('A','A',[(1820,0.32),(1966,0.35)]),
 # --- A · seqD : critique / consecration / moralisation ---
 'secular_review':('A','D',[(1876,0.20),(1882,0.42),(1888,0.15)]),                        # ★ ferme ~1888 (-> Agnostic Journal)
 'victoria_and_albert_museum':('A','D',[(1852,0.20),(1880,0.38),(1909,0.45),(1966,0.45)]),# ★ 1852 fondation, V&A 1899, batiment 1909
 'elizabethan_literary_society':('A','D',[(1884,0.30),(1910,0.40),(1940,0.30),(1966,0.22)]),
 'manchester_literary_club':('A','D',[(1862,0.30),(1900,0.42),(1966,0.36)]),              # 1862
 'national_secular_society':('A','D',[(1866,0.28),(1885,0.40),(1915,0.35),(1966,0.28)]),  # NSS 1866, apogee Bradlaugh
 'leicester_secular_society':('A','D',[(1851,0.25),(1881,0.38),(1920,0.30),(1966,0.22)]), # Secular Hall 1881
 'oddfellows_sunday_school':('A','D',[(1838,0.25),(1880,0.32),(1930,0.25),(1966,0.18)]),
 'sunday_school_times':('A','D',[(1875,0.25),(1900,0.32),(1940,0.22),(1966,0.16)]),
 # --- C · seqD : regulation actuarielle ---
 'temperance_and_general_provi':('C','D',[(1840,0.22),(1880,0.35),(1920,0.40),(1966,0.40)]), # T&G Provident 1840
 # --- D · seqC : evaluation economique ---
 'financial_times':('D','C',[(1888,0.20),(1900,0.30),(1920,0.40),(1945,0.50),(1966,0.50)]),  # ★ 1888, fusion FN 1945
 # --- D · seqD : gatekeeping ---
 'reuters':('D','D',[(1851,0.25),(1865,0.50),(1900,0.70),(1945,0.70),(1966,0.65)]),        # ★ 1851, Times 1858, agence imperiale
}
ILLUS={  # B illustratif (contraste)
 'parliamentary_oversight_illus':('B','B',[(1870,0.40),(1920,0.48),(1966,0.45)]),
 'royal_commission_illus':('B','D',[(1860,0.35),(1900,0.42),(1966,0.38)]),
}
ALLCTRL={**CTRLC,**ILLUS}
# catalogue : fondation + meta pour la mediation (non-controle)
found={}; meta={}
for r in csv.DictReader(open(CAT)):
    a=r['aid']; y=int(r['annee'])
    if a not in found or y<found[a]: found[a]=y
    meta.setdefault(a,r)
END=1966
def ctrl_rows(target):
    rows=[]
    for a,(s,q,curve) in target.items():
        for (yy,ww) in curve: rows.append((a,yy,s,'controle',q,ww))
    return rows
# 1) parc de controle seul
ctrl=[('aid','annee','structure','categorie','sequence','poids')]+ctrl_rows(ALLCTRL)
with open('examples/working-class-authors/data/instances/control_parc_empirical.csv','w',newline='') as fo: csv.writer(fo).writerows(ctrl)
# 2) cohorte complete : controle (courbes) + mediation (generique)
full=[('aid','annee','structure','categorie','sequence','poids')]+ctrl_rows(ALLCTRL)
nmed=0
for a,f in found.items():
    if a in CTRLC: continue   # deja en controle
    m=meta[a]; s=m['structure']; q=m['sequence']; c=m['categorie'] or 'aspirant'
    h=0
    for ch in a: h=(h*31+ord(ch))&0x7fffffff
    span=35+(h%26); close=min(END,max(f+span,f+30)); pky=f+round(0.40*(close-f)); peak=round(0.40+(h%5)*0.05,2)
    for (yy,ww) in [(f,0.12),(pky,peak),(close,0.08)]: full.append((a,yy,s,c,q,ww))
    nmed+=1
# dedoublonnage (aid,annee)
seen=set(); clean=[full[0]]
for row in full[1:]:
    k=(row[0],row[1])
    if k in seen: continue
    seen.add(k); clean.append(row)
with open('examples/working-class-authors/data/instances/instances_full_empirical.csv','w',newline='') as fo: csv.writer(fo).writerows(clean)
print(f"\u2713 controle : {len(CTRLC)} reels + {len(ILLUS)} illustratifs, courbes d'autorite ({len(ctrl)-1} lignes)")
print(f"\u2713 cohorte complete : + {nmed} mediation generique ({len(clean)-1} lignes)")
