# -*- coding: utf-8 -*-
# Code le métier du père -> HISCLASS/HISCAM, puis compare origine->destination de la cohorte aux bases publiées.
import csv, re
from collections import Counter, defaultdict

# concept -> (hisclass, hiscam) depuis le lexique ; variants depuis code_structure_seq
L={r['concept_or_term']:r for r in csv.DictReader(open('out/occupation_lexicon.csv',encoding='utf-8-sig'))}
src=open('code_structure_seq.py').read(); ns={}; exec(src[src.index('VAR = {'):src.index('# avocational')],ns); VAR=ns['VAR']
CC={c:(L[c]['hisclass'],L[c]['hiscam']) for c in L if L.get(c,{}).get('kind')=='concept' and L[c]['hisco']}
# add generic proxies for fathers (often shopkeeper/clerk etc.)
GEN={'manager':('3','84.88'),'clerk':('5','69.59'),'shopkeeper':('3','81.33'),'proprietor':('3','81.33'),
     'agent':('11','51.9'),'salesman':('4','73.55')}
for g,v in GEN.items(): CC.setdefault(g,v)

def norm(s):
    s=(s or '').lower(); s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r"[^a-z'\- ]",' ',s); return ' '+re.sub(r'\s+',' ',s).strip()+' '
def code_father(txt):
    t=norm(txt); best=None;pos=10**9
    for con,vs in VAR.items():
        if con not in CC: continue
        for v in vs:
            m=re.search(r'[ \-]'+re.escape(v)+r'(s|es|ing)?[ \-]',t)
            if m and m.start()<pos: pos=m.start();best=con
    return best

A=list(csv.DictReader(open('out/actors.csv',encoding='utf-8-sig')))
prof={r['entry_id']:r for r in csv.DictReader(open('out/circulation_profiles.csv',encoding='utf-8-sig'))}

def cls_band(hc):
    try:h=int(hc)
    except:return None
    if h<=2:return 'élite prof./entrepr. (I-II)'
    if h<=5:return 'col blanc inf. (III-V)'
    if h in (6,7):return 'manuel qualifié (VI-VII)'
    if h==8:return 'fermier (VIII)'
    return 'manuel peu/non qualifié (IX-XII)'
MANUAL={'manuel qualifié (VI-VII)','manuel peu/non qualifié (IX-XII)'}

n_father=0; orig=Counter(); pairs=[]
for r in A:
    fc=code_father(r.get('father_occupation','') or r.get('father_raw',''))
    if not fc: continue
    fhc=CC[fc][0]; band=cls_band(fhc)
    if band is None: continue
    n_father+=1; orig[band]+=1
    # destination du fils : HISCLASS de l'étape au HISCAM max (pic)
    p=prof.get(r['entry_id'],{})
    dest=None
    if p.get('cam_max'):
        # retrouver l'étape codée au pic
        dest_hc=None
        # approx : on relit stages
        pairs.append((r['entry_id'],band,fc,float(p['cam_max']) if p['cam_max'] else None))
print(f"pères codés : {n_father}/{len(A)}")
print("\nclasse d'origine (père) :")
for b,c in orig.most_common(): print(f"  {b:<32} {c:>3} ({100*c/n_father:.0f}%)")
father_manual=sum(orig[b] for b in MANUAL)
print(f"\npères manuels (classe ouvrière) : {father_manual}/{n_father} ({100*father_manual/n_father:.0f}%)")

# destination : reconstruire HISCLASS au pic depuis stages
S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))
byA=defaultdict(list)
for s in S:
    if s['hiscam']: byA[s['entry_id']].append((float(s['hiscam']),s['hisclass']))
dest_band={}
for eid,lst in byA.items():
    lst.sort(); dest_band[eid]=cls_band(lst[-1][1])  # au pic HISCAM
# parmi pères manuels, destination des fils
fm=[]
for r in A:
    fc=code_father(r.get('father_occupation','') or r.get('father_raw',''))
    if not fc: continue
    band=cls_band(CC[fc][0])
    if band in MANUAL: fm.append((r['entry_id'],band,fc))
reached={}
tot_fm=0; reached_elite=0; reached_nonman=0
for eid,band,fc in fm:
    db=dest_band.get(eid)
    if not db: continue
    tot_fm+=1
    if db=='élite prof./entrepr. (I-II)': reached_elite+=1
    if db in ('élite prof./entrepr. (I-II)','col blanc inf. (III-V)'): reached_nonman+=1
print(f"\n=== fils de pères MANUELS, destination au pic (n={tot_fm}) ===")
print(f"  atteignent l'élite prof. (HISCLASS I-II) : {reached_elite}/{tot_fm} ({100*reached_elite/tot_fm:.0f}%)")
print(f"  atteignent le col blanc (HISCLASS I-V)   : {reached_nonman}/{tot_fm} ({100*reached_nonman/tot_fm:.0f}%)")
print(f"\n  RÉFÉRENCE (Miles 1999, ouvriers anglais 1839-1914) :")
print(f"    ~90% restent ouvriers ; ~5% atteignent la classe moyenne ; ~0,2% le sommet professionnel.")
