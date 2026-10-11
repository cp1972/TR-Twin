from common import *
import sys, re
from d2_units import FORM
from sklearn import decomposition
def units(kind):
    out=[]
    if kind=='occ':
        for s in STG: out.append((s['entry_id'],int(s['stage_index']),s['occupation_raw']))
    else:
        for e,a in ACT.items():
            for j,c in enumerate([c for c in a['affiliations_raw'].split(';') if c.strip()]): out.append((e,j,c))
    return out
def fit(kind,K,form=False,seed=None,min_df=2):
    U=units(kind); stop=STOP+(FORM if form else [])
    cw,_=M.preprocess_corpus([u[2] for u in U],stop,3); mx=M.build_matrices(cw,stop,min_df,0.95)
    if seed is None: r=M.run_nmf(mx['tf_matrix'],K); W,H=r['doctopic'],r['topicwords']
    else:
        m=decomposition.NMF(n_components=K,random_state=seed,init='random',max_iter=800); W=m.fit_transform(mx['tf_matrix']); H=m.components_
    return U,W,H,mx
if __name__=='__main__':
    kind=sys.argv[1]; K=int(sys.argv[2]); form=len(sys.argv)>3
    U,W,H,mx=fit(kind,K,form); names=mx['tf_names']; dom=W.argmax(1); empty=W.sum(1)==0
    print(kind,'docs',len(U),'vocab',len(names),'empty',empty.sum())
    for k in range(K):
        print(f'T{k:02d} n={int(((dom==k)&~empty).sum()):3d}',' '.join(names[i] for i in H[k].argsort()[::-1][:11]))
