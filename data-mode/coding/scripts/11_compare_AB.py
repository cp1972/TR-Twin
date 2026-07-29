# -*- coding: utf-8 -*-
# Vergleich A (Zieldimension, zwei Punkte) und B (Intensität bei angeglichener Auflösung) gegen die Referenztabelle.
import csv, math, statistics
from collections import defaultdict

A={r['entry_id']:r for r in csv.DictReader(open('out/actors.csv',encoding='utf-8-sig'))}
S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))

def band5(h):  # HISCLASS -> Klasse nach Miles (I bis V); None, wenn leer
    try:h=int(h)
    except:return None
    if h<=2:return 'I'      # Professional
    if h<=5:return 'II'     # Intermediate (unteres nicht-manuelles Segment)
    if h in(6,7):return 'III'  # Skilled
    if h==8:return 'F'      # Farmer
    if h in(9,10):return 'IV'  # Semi
    return 'V'              # Unskilled
NONMAN={'I','II'}; MANUAL={'III','IV','V'}

# ---- Wilson-Konfidenzintervall, 95 % ----
def wilson(k,n,z=1.96):
    if n==0:return (0,0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))

# ===== A: Zieldimension (zwei Punkte: Vater -> Höhepunkt des Sohnes) =====
# HISCLASS am HISCAM-Höhepunkt
byA=defaultdict(list)
for r in S:
    if r['hiscam'] and r['hisclass']:
        byA[r['entry_id']].append((float(r['hiscam']),r['hisclass']))
peak_band={eid:band5(sorted(v)[-1][1]) for eid,v in byA.items()}

# Väter in manuellen Berufen (nutzt die Codierung aus 10_father_coding)
import importlib.util
spec=importlib.util.spec_from_file_location("fc","10_father_coding.py")
# 10_father_coding gibt nur aus; das Nötigste wird hier nachgebaut, um die Liste zu erhalten
import re
L={r['concept_or_term']:r for r in csv.DictReader(open('out/occupation_lexicon.csv',encoding='utf-8-sig'))}
src=open('04_code_structure_seq.py').read(); ns={}; exec(src[src.index('VAR = {'):src.index('# avocational')],ns); VAR=ns['VAR']
CC={c:(L[c]['hisclass'],L[c]['hiscam']) for c in L if L.get(c,{}).get('kind')=='concept' and L[c]['hisco']}
for g,v in {'manager':('3','84.88'),'clerk':('5','69.59'),'shopkeeper':('3','81.33'),'proprietor':('3','81.33'),'agent':('11','51.9'),'salesman':('4','73.55')}.items(): CC.setdefault(g,v)
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

sons_manual=[]
for eid,r in A.items():
    fc=code_father(r.get('father_occupation','') or r.get('father_raw',''))
    if not fc: continue
    fb=band5(CC[fc][0])
    if fb in MANUAL and peak_band.get(eid): sons_manual.append((eid,fb,peak_band[eid]))
n=len(sons_manual)
elite=sum(1 for _,_,d in sons_manual if d=='I')
nonman=sum(1 for _,_,d in sons_manual if d in NONMAN)
print("===== VERGLEICH A — Zieldimension (Vater manuell -> Gipfel des Sohns) =====")
print(f"n (Söhne manueller Väter mit kodiertem Ziel) = {n}")
ce=wilson(elite,n); cn=wilson(nonman,n)
print(f"  -> Professional (Miles I): {elite}/{n} = {100*elite/n:.0f}%  [95%-KI {100*ce[0]:.0f}–{100*ce[1]:.0f}%]   Referenz ~0,2%  => RR ~{(elite/n)/0.002:.0f}×")
print(f"  -> nicht-manuell (I–II)  : {nonman}/{n} = {100*nonman/n:.0f}%  [95%-KI {100*cn[0]:.0f}–{100*cn[1]:.0f}%]   Referenz ~5%   => RR ~{(nonman/n)/0.05:.0f}×")
print(f"  konservativ (untere KI-Grenze Elite {100*ce[0]:.0f}% vs 0,2%) => RR ~{ce[0]/0.002:.0f}×")

# ===== B: Intensität bei angeglichener Auflösung =====
def years(eid):
    by=A.get(eid,{}).get('birth_year','')
    try:base=int(by)
    except:base=1850
    return base
traj=defaultdict(list)  # eid -> [(year,hisclass_band)]
for r in S:
    if r['hisclass']:
        b=band5(r['hisclass'])
        if b and b!='F':
            traj[r['entry_id']].append((years(r['entry_id'])+15+int(r['stage_index'])*4,b))
ORD={'V':0,'IV':1,'III':2,'II':3,'I':4}
def decadal(seq):
    seq=sorted(seq); y0,y1=seq[0][0],seq[-1][0]
    out=[]
    for g in range((y0//10)*10,(y1//10)*10+1,10):
        vals=[b for (y,b) in seq if y<=g]
        if vals:out.append(vals[-1])
    return [out[0]]+[out[i] for i in range(1,len(out)) if out[i]!=out[i-1]] if out else []

cross_fine=cross_dec=0; nman_cross=0; tot=0; anychg_dec=0
unsk_start=0; unsk_to_skilled=0; unsk_to_nonman=0
fine_changes=[]; dec_changes=[]
analys_dec=0
for eid,seq in traj.items():
    if len({b for _,b in seq})<1: continue
    fine=[b for _,b in sorted(seq)]
    fc_seq=[fine[0]]+[fine[i] for i in range(1,len(fine)) if fine[i]!=fine[i-1]]
    dec=decadal(seq)
    if len(seq)<2: continue
    tot+=1
    fine_changes.append(len(fc_seq)-1)
    # manuell -> nicht-manuell (irgendwann), fein und dekadisch aufgelöst
    if any(b in NONMAN for b in fine) and fine[0] in MANUAL: cross_fine+=1
    if len(dec)>=2:
        analys_dec+=1
        dec_changes.append(len(dec)-1)
        if dec[0] in MANUAL and any(b in NONMAN for b in dec): cross_dec+=1
        if any(b in NONMAN for b in dec) and any(b in MANUAL for b in dec): nman_cross+=1
        anychg_dec+= 1 if len(set(dec))>1 else 0
    # parmi ceux qui DÉMARRENT non-qualifié (V)
    if fine[0]=='V':
        unsk_start+=1
        if any(b=='III' for b in fine): unsk_to_skilled+=1
        if any(b in NONMAN for b in fine): unsk_to_nonman+=1

print("\n===== VERGLEICH B — Intensität bei angeglichener Auflösung =====")
print(f"analysierbare Akteure (≥2 kodierte HISCLASS-Etappen) = {tot}")
print(f"  manuell -> nicht-manuell im Leben (fein)     : {cross_fine}/{tot} = {100*cross_fine/tot:.0f}%")
print(f"  davon dekadisch analysierbar (≥2 Dekadenpkt.): {analys_dec}")
print(f"  manuell -> nicht-manuell (dekadisch)         : {cross_dec}/{analys_dec} = {100*cross_dec/max(analys_dec,1):.0f}%")
print(f"  Referenz: Übertritt manuell->nicht-manuell intra-vital = 'sehr selten' (Miles); intergen. ~5% (Tab.-Ref.)")
print(f"\n  unter denen, die ungelernt (V) STARTEN (n={unsk_start}):")
if unsk_start:
    print(f"    -> erreichen gelernt (III)        : {unsk_to_skilled}/{unsk_start} = {100*unsk_to_skilled/unsk_start:.0f}%   (Referenz Long ~40%)")
    print(f"    -> erreichen nicht-manuell (I–II) : {unsk_to_nonman}/{unsk_start} = {100*unsk_to_nonman/unsk_start:.0f}%   (Referenz: verschwindend)")
print(f"\n  Klassenwechsel je Lebenslauf: fein {statistics.mean(fine_changes):.2f} vs dekadisch {statistics.mean(dec_changes) if dec_changes else 0:.2f}")
print(f"  (Erinnerung Residuum: Richtungsumkehrungen 37% -> 11% bei dekadischer Auflösung)")
