from g_crossing import *
from sklearn import decomposition
RESID={4:3,5:4,6:4}
BASE={4:{0:'M',1:'M',2:'N',3:'N'},5:{0:'M',1:'M',2:'N',3:'N',4:'N'},6:{0:'M',1:'M',2:'N',3:'N',4:'N',5:'N'}}
def submodel(K,K2,seed=None):
    U,W,H,mx=fit('occ',K,seed=seed)
    idx=[i for i,w in enumerate(W) if w.sum()>0 and int(w.argmax())==RESID[K]]
    X=mx['tf_matrix'][idx]
    if seed is None: m=decomposition.NMF(n_components=K2,random_state=1,init='nndsvd',max_iter=800)
    else: m=decomposition.NMF(n_components=K2,random_state=seed,init='random',max_iter=800)
    W2=m.fit_transform(X); return U,W,H,mx,idx,W2,m.components_
if __name__=='__main__':
    import sys
    K=int(sys.argv[1])
    for K2 in (4,6,8):
        U,W,H,mx,idx,W2,H2=submodel(K,K2); names=mx['tf_names']; d=W2.argmax(1)
        print(f'== K={K}, Resttopic {len(idx)} Etappen, Untermodell K2={K2}')
        for k in range(K2): print(f'  S{k} n={int(((d==k)&(W2.sum(1)>0)).sum()):3d}',' '.join(names[i] for i in H2[k].argsort()[::-1][:12]))
