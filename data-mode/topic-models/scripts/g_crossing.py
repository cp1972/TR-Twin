from f_separate import *
from collections import defaultdict, Counter
from sklearn.metrics import cohen_kappa_score as KAPPA
# Lesung der 15 Berufstopics: M = manuell, N = nicht-manuell, X = gemischt/unbestimmt
MN15={0:'M',1:'M',2:'N',3:'N',4:'X',5:'N',6:'X',7:'N',8:'N',9:'X',10:'X',11:'X',12:'X',13:'M',14:'N'}
def hisclass_cross():
    by=defaultdict(list)
    for s in STG:
        if s['hisclass']: by[s['entry_id']].append((int(s['stage_index']),int(s['hisclass'])))
    out={}
    for e,v in by.items():
        if len(v)<2: continue
        seq=['N' if h<=5 else 'M' for _,h in sorted(v)]
        out[e]=any(seq[i]=='M' and 'N' in seq[i+1:] for i in range(len(seq)))
    return out
def topic_cross(U,W,MN):
    by=defaultdict(list)
    for (e,i,_),w in zip(U,W):
        if w.sum()==0: continue
        c=MN[int(w.argmax())]
        if c!='X': by[e].append((i,c))
    out={}
    for e,v in by.items():
        if len(v)<2: continue
        seq=[c for _,c in sorted(v)]
        out[e]=any(seq[i]=='M' and 'N' in seq[i+1:] for i in range(len(seq)))
    return out
if __name__=='__main__':
    H=hisclass_cross(); print('HISCLASS: Akteure',len(H),'Kreuzung',sum(H.values()),f'{sum(H.values())/len(H):.0%}')
    U,W,Hm,mx=fit('occ',15)
    dom=W.argmax(1); share=Counter(MN15[int(d)] for d,w in zip(dom,W) if w.sum()>0); print('Etappen je Topic-Typ',share)
    T=topic_cross(U,W,MN15); print('Topics: Akteure',len(T),'Kreuzung',sum(T.values()),f'{sum(T.values())/len(T):.0%}')
    both=[e for e in H if e in T]
    print('beide bestimmbar',len(both),'Übereinstimmung',f"{np.mean([H[e]==T[e] for e in both]):.0%}",'kappa',round(KAPPA([H[e] for e in both],[T[e] for e in both]),3))
    print('Kreuztabelle H x T', Counter((H[e],T[e]) for e in both))
