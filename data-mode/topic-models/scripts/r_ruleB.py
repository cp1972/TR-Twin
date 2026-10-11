"""Zirkulationsregel B: Eroberung oder Enttäuschung entscheidet sich an der Stärke der AUSGANGSposition
(Netto-Attraktivität >= 0 -> Etablierte; < 0 -> Enttäuschte), nicht am Ziel."""
from pfade import *
import csv
from collections import Counter
import q_contracts as Q
CATS=Q.CATS
def categories_B(seq):
    inn,out=Counter(),Counter()
    for e,v in seq.items():
        path=[''.join(x[3]) for x in v]; path=[p for j,p in enumerate(path) if j==0 or p!=path[j-1]]
        for a,b in zip(path,path[1:]): out[a]+=1; inn[b]+=1
    val={p:(inn[p]-out[p])/(inn[p]+out[p]) for p in set(inn)|set(out)}
    cats={}
    for e,v in seq.items():
        if len(v)<2: continue
        prev=None
        for j,x in enumerate(v):
            c=x[3]
            if j+1<len(v):
                n=v[j+1][3]
                cat=CATS[2] if n==c else CATS[1] if n[0]==c[0] else (CATS[0] if val.get(''.join(c),0)>=0 else CATS[3])
            else:
                cat=CATS[0] if (prev==CATS[0] or val.get(''.join(c),0)>=0) else CATS[2]
            cats[(e,x[2])]=cat; prev=cat
    return cats,val
if __name__=='__main__':
    S3=Q.sequences(False); C3,_=categories_B(S3); print('N3B',Q.write(S3,C3,vertrag('N3B_topics_regelB.csv')))
    S4=Q.sequences(True); C4,_=categories_B(S4); print('N4B',Q.write(S4,C4,vertrag('N4B_topics_nebentaetigkeiten_regelB.csv')))
    # Lexikon mit Regel B
    import m_contracts as M
    seq={}
    for e in M.ids:
        seq[e]=[(M.YEARS[(e,int(s['stage_index']))][0],0,int(s['stage_index']),M.LEX[(e,int(s['stage_index']))],'Beruf') for s in M.stages_by[e] if M.LEX[(e,int(s['stage_index']))][0]]
    CL,_=categories_B(seq); print('E1B',Q.write(seq,CL,vertrag('E1B_lexikon_regelB.csv')))
    for nm,C in (('N3B',C3),('N4B',C4),('E1B',CL)): print(nm,Counter(C.values()))
