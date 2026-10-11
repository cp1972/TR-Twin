from common import *
import sys, json
from sklearn import decomposition
FORM="""member members employed various variously joined active served elected founder founding started
subsequently eventually continued later period short spent became assistant general chief head
boy boys apprentice apprenticed journeyman master joint honorary vice president chairman secretary
committee executive branch national local district""".split()
def build(K,seed=1,form=True,min_df=3):
    units=[]
    for s in STG: units.append((s['entry_id'],'stage',int(s['stage_index']),s['occupation_raw']))
    for eid,a in ACT.items():
        for j,c in enumerate([c for c in a['affiliations_raw'].split(';') if c.strip()]):
            units.append((eid,'affil',j,c))
    stop=STOP+(FORM if form else [])
    cw,cr=M.preprocess_corpus([u[3] for u in units],stop,3)
    mx=M.build_matrices(cw,stop,min_df,0.5)
    nmf=decomposition.NMF(n_components=K,random_state=seed,init='nndsvd' if seed==1 else 'nndsvdar',max_iter=1000)
    W=nmf.fit_transform(mx['tf_matrix']); H=nmf.components_
    return units,W,H,mx['tf_names']
if __name__=='__main__':
    K=int(sys.argv[1])
    units,W,H,names=build(K)
    empty=W.sum(1)==0; dom=W.argmax(1)
    print('empty',empty.sum(),'of',len(units),' empty stages',sum(1 for i,u in enumerate(units) if empty[i] and u[1]=='stage'))
    for k in range(K):
        top=[names[i] for i in H[k].argsort()[::-1][:12]]
        ns=sum(1 for i,u in enumerate(units) if dom[i]==k and not empty[i] and u[1]=='stage')
        na=sum(1 for i,u in enumerate(units) if dom[i]==k and not empty[i] and u[1]=='affil')
        print(f'T{k:02d} st={ns:3d} af={na:3d}',' '.join(top))
