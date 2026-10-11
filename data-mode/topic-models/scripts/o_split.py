from pfade import *
import importlib.util, pickle, numpy as np
M5=mta_core()
from f_separate import units
from common import STOP
D=pickle.load(open(arbeit('two_stage.pkl'),'rb')); s1,REST,idx,det,U=D['s1'],D['REST'],D['idx'],D['det'],D['U']
cw,_=M5.preprocess_corpus([u[2] for u in U],STOP,3); mx=M5.build_matrices(cw,STOP,2,0.95); names=mx['tf_names']
d1=s1['documents']; d2=det[6]['documents']
groups={'T1 Lehre/Druck':[j for j,t in enumerate(d1['Consensus topic']) if t=='Topic_1'],
        'T2 Presse':[j for j,t in enumerate(d1['Consensus topic']) if t=='Topic_2'],
        'S5 Dozent/Propagandist':[idx[k] for k,t in enumerate(d2['Consensus topic']) if t=='Topic_5']}
out={}
for g,ix in groups.items():
    X=mx['tf_matrix'][ix]
    tab,dt=M5.stability_over_k(X,[2,3],n_runs=50,doc_labels=[str(j) for j in ix])
    print('==',g,len(ix)); print(tab[['K','Stable documents (share)','Min topic similarity']].round(2).to_string(index=False))
    for K,r in dt.items():
        H=r['reference']['topicwords']; t=r['topics']
        for k in range(K): print(f'   K{K} U{k} n={t.iloc[k]["Documents (consensus)"]} rep={t.iloc[k]["Reproduced (share of runs, sim >= 0.8)"]:.0%} |',' '.join(names[i] for i in H[k].argsort()[::-1][:10]))
        if K==2:
            for k in range(K):
                ex=[U[ix[m]][2][:60] for m,tt in enumerate(r['documents']['Consensus topic']) if tt==f'Topic_{k}'][:6]
                print('      z.B.',ex)
    out[g]=(ix,dt)
pickle.dump(out,open(arbeit('splits.pkl'),'wb'))
