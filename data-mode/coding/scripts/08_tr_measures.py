# -*- coding: utf-8 -*-
# Lecture des mesures de la TR (§5.17) sur l'état empirique (S, g, act), formules portées du simulateur.
import csv, json
from collections import defaultdict

STR={'A':0,'B':1,'C':2,'D':3}; SEQ={'A':0,'B':1,'C':2,'D':3}
CAT={'Etablierte':0,'Anwaerter':1,'Bewahrende':2,'Enttaeuschte':3}  # val=[3,2,1,0]
VAL=[3,2,1,0]; N=4

S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))
# jeu cohérent : étapes ayant structure + sequence + tr_absolute
cnt=[[[0]*4 for _ in range(4)] for _ in range(4)]
nused=0
for r in S:
    st=r.get('structure',''); sq=r.get('sequence',''); c=r.get('tr_absolute','')
    if st in STR and sq in SEQ and c in CAT:
        cnt[STR[st]][SEQ[sq]][CAT[c]]+=1; nused+=1

# S[x], g[x][s], act[x][s][c]
Ssz=[sum(sum(cnt[x][s]) for s in range(4)) for x in range(4)]
tot=sum(Ssz) or 1
Sn=[v/tot for v in Ssz]
g=[[0.0]*4 for _ in range(4)]; act=[[[0.25]*4 for _ in range(4)] for _ in range(4)]
for x in range(4):
    sx=sum(sum(cnt[x][s]) for s in range(4))
    for s in range(4):
        m=sum(cnt[x][s]); g[x][s]=(m/sx) if sx>0 else 0.0
        if m>0: act[x][s]=[cnt[x][s][c]/m for c in range(4)]

def gini(v):
    return sum(abs(v[i]-v[j]) for i in range(N) for j in range(N))/(2*N)
def structGini(x): return gini(g[x])
def vertGiniX(x):
    num=den=0.0
    for s in range(4):
        m=g[x][s]
        if m<1e-9: continue
        a=act[x][s]; mean=sum(a[c]*VAL[c] for c in range(4)); den+=m
        if mean<1e-9: continue
        mad=sum(a[c]*a[d]*abs(VAL[c]-VAL[d]) for c in range(4) for d in range(4))
        num+=m*(mad/(2*mean))
    return num/den if den>0 else 0.0

transv=gini(Sn)
horiz=sum(structGini(x) for x in range(4))/N
vert=sum(vertGiniX(x) for x in range(4))/N

# baseline symétrique (P0 = composition par défaut)
P0=[0.22,0.28,0.28,0.22]
mean0=sum(P0[c]*VAL[c] for c in range(4)); mad0=sum(P0[c]*P0[d]*abs(VAL[c]-VAL[d]) for c in range(4) for d in range(4))
vert_base=mad0/(2*mean0)

DOM=['A·Kultur','B·Politik','C·Wirtschaft','D·Medien']
print(f"étapes utilisées (structure+séquence+catégorie) : {nused}\n")
print("S (taille relationnelle des structures) :")
for x in range(4): print(f"  {DOM[x]:<14} {Sn[x]*100:5.1f}%  (séquences g: "+', '.join(f'{g[x][s]*100:.0f}' for s in range(4))+")")
print(f"\n=== CASCADE DES TROIS NIVEAUX (lecture §5.17) ===")
print(f"  transversal (entre structures)        : {transv:.3f}")
print(f"  horizontal  (entre séquences/struct.) : {horiz:.3f}")
print(f"  vertical    (entre catégories/séq.)   : {vert:.3f}")
print(f"\n  référence symétrique                  : transv 0.000 | horiz 0.000 | vert {vert_base:.3f}")
print(f"\n  vertical par structure (pv0..3) :")
for x in range(4): print(f"    {DOM[x]:<14} {vertGiniX(x):.3f}")

json.dump({'n_stages':nused,'S':Sn,'g':g,'act':act,
  'cascade':{'transversal':transv,'horizontal':horiz,'vertical':vert,'vertical_baseline':vert_base},
  'vertGiniX':[vertGiniX(x) for x in range(4)],
  'structGini':[structGini(x) for x in range(4)]},
  open('out/tr_measures.json','w'),indent=1)
print("\n-> out/tr_measures.json")
