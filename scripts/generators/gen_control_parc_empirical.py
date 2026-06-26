#!/usr/bin/env python3
"""Parc de controle EMPIRIQUE, derive du catalogue instances_extract_contract.csv
selon l'etiquetage valide (structure, sequence-cible, poids). B = illustratif (contraste)."""
import csv
# annees de fondation depuis le catalogue
found={}
for r in csv.DictReader(open('examples/working-class-authors/data/instances/instances_extract_contract.csv')):
    a=r['aid']; y=int(r['annee'])
    if a not in found or y<found[a]: found[a]=y
# (aid, structure, sequence-cible, poids) — REEL (catalogue)
REAL=[
 # A · seqA : certification / examen
 ('cambridge_university','A','A',0.60),('st_andrews_university','A','A',0.60),
 ('university_of_london','A','A',0.60),('harvard_university','A','A',0.60),
 ('university_college','A','A',0.45),('reading_university_college','A','A',0.45),
 ('city_of_london_college','A','A',0.45),('anderson_s_college_and_museu','A','A',0.45),
 ('bible_training_college','A','A',0.45),('aberdeen_grammar_school','A','A',0.35),
 ('shrewsbury_school','A','A',0.35),
 # A · seqD : critique / consecration / moralisation
 ('secular_review','A','D',0.42),('elizabethan_literary_society','A','D',0.40),
 ('manchester_literary_club','A','D',0.40),('victoria_and_albert_museum','A','D',0.45),
 ('national_secular_society','A','D',0.35),('leicester_secular_society','A','D',0.35),
 ('oddfellows_sunday_school','A','D',0.30),('sunday_school_times','A','D',0.30),
 # C · seqD : regulation actuarielle
 ('temperance_and_general_provi','C','D',0.35),
 # D · seqC : evaluation economique
 ('financial_times','D','C',0.45),
 # D · seqD : gatekeeping
 ('reuters','D','D',0.60),
]
# B illustratif (pas d'instance reelle de controle dans le corpus) — fondation fixee
ILLUS=[
 ('parliamentary_oversight_illus','B','B',0.45,1870),
 ('royal_commission_illus','B','D',0.40,1860),
]
END=1966
out=[('aid','annee','structure','categorie','sequence','poids')]
for aid,s,q,w in REAL:
    f=found.get(aid)
    if f is None: print('!! manquant:',aid); continue
    out.append((aid,f,s,'controle',q,w)); out.append((aid,END,s,'controle',q,w))
for aid,s,q,w,f in ILLUS:
    out.append((aid,f,s,'controle',q,w)); out.append((aid,END,s,'controle',q,w))
with open('examples/working-class-authors/data/instances/control_parc_empirical.csv','w',newline='') as fo:
    csv.writer(fo).writerows(out)
nre=len(REAL); print(f"\u2713 parc empirique : {nre} instances reelles + {len(ILLUS)} illustratives (B) · {len(out)-1} lignes")
