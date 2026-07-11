# -*- coding: utf-8 -*-
import csv, statistics
from collections import Counter

GENERIC_DROP = {'manager','agent','proprietor','clerk','shopkeeper','assistant'}
# concepts kept WITH documented compromise:
COMPROMISE = {'secretary','union_official','lecturer','engineer','bookseller','publisher','warehouseman','salesman'}

S=list(csv.DictReader(open('out/stages_long_coded.csv',encoding='utf-8-sig')))
L=list(csv.DictReader(open('out/occupation_lexicon.csv',encoding='utf-8-sig')))

# map each stage to its lexicon line (by recomputing key is complex) -> instead use method:
# Rule: keep a stage's code iff (it had a code) AND (its code came from a 'synonym' concept that is NOT generic-dropped).
#  -> term/keyword/rescue codes are dropped (precision-first); generic concepts dropped.
# We identify concept of each coded stage via its code_method: synonym=concept; others dropped.
# But we also need the concept name; reconstruct from a concept->code map.
import importlib.util
# Rebuild concept->hisco from the lexicon 'concept' lines:
concept_code={r['concept_or_term']:r['hisco'] for r in L if r['kind']=='concept' and r['hisco']}
code_concept={}
for c,h in concept_code.items(): code_concept.setdefault(h,set()).add(c)

kept=0; dropped_generic=0; dropped_termnoise=0
for st in S:
    keep=False
    if st['hisco_code'] and st['code_method']=='synonym':
        # which concept? a synonym stage's code maps to a concept; if that concept is generic-dropped, drop
        cons=code_concept.get(st['hisco_code'],set())
        if cons & GENERIC_DROP and not (cons - GENERIC_DROP):
            dropped_generic+=1
        else:
            keep=True
    if not keep and st['hisco_code']:
        if st['code_method']=='synonym': pass
        else: dropped_termnoise+=1
    if keep: kept+=1
    else:
        st['hisco_code']=st['hisclass']=st['hiscam']=''
        st['code_method']=st['code_review']=''

# ---------- TR category rule (PROPOSAL): HISCAM level + trajectory direction ----------
cams=[float(s['hiscam']) for s in S if s['hiscam']]
HIGH=round(statistics.quantiles(cams,n=3)[1],1)   # top tercile
LOW =round(statistics.quantiles(cams,n=3)[0],1)   # bottom tercile
DELTA=3.0
TRLABEL={3:'Etablierte',2:'Anwaerter',1:'Bewahrende',0:'Enttaeuschte'}

# group by actor, in stage order, track previous coded HISCAM
from collections import defaultdict
byact=defaultdict(list)
for s in S: byact[s['entry_id']].append(s)
for eid,sts in byact.items():
    prev=None
    for s in sorted(sts,key=lambda x:int(x['stage_index'])):
        if not s['hiscam']:
            s['tr_category']=''; continue
        h=float(s['hiscam']); d=(h-prev) if prev is not None else 0.0
        if h>=HIGH: cat=3
        elif (prev is not None and d<=-DELTA) or h<=LOW: cat=0
        elif prev is not None and d>=DELTA: cat=2
        else: cat=1
        s['tr_category']=TRLABEL[cat]
        prev=h

with open('out/stages_long_final.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=S[0].keys()); w.writeheader(); w.writerows(S)

N=len(S); coded=sum(1 for s in S if s['hisco_code'])
print(f"Seuils HISCAM cohorte : LOW(P33)={LOW}  HIGH(P67)={HIGH}  (δ={DELTA})")
print(f"étapes codées après nettoyage : {coded}/{N} ({100*coded/N:.0f}%)")
print(f"  dropés (génériques)         : {dropped_generic}")
print(f"  dropés (term/noise/rescue)  : {dropped_termnoise}")
print("\nrépartition catégories TR (proposition) sur étapes codées :")
c=Counter(s['tr_category'] for s in S if s['tr_category'])
for k in ['Etablierte','Anwaerter','Bewahrende','Enttaeuschte']:
    print(f"  {k:<13}: {c.get(k,0):>3} ({100*c.get(k,0)/coded:.0f}%)")
