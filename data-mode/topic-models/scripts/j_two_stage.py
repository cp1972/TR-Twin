from pfade import *
import importlib.util, pickle
M5=mta_core()
from g_crossing import *
U=units('occ'); cw,_=M5.preprocess_corpus([u[2] for u in U],STOP,3); mx=M5.build_matrices(cw,STOP,2,0.95)
labels=[f'{e}_{i}' for e,i,_ in U]; names=mx['tf_names']
# Stufe 1: K=4, 50 Läufe
s1=M5.topic_stability(mx['tf_matrix'],4,n_runs=50,doc_labels=labels)
d1=s1['documents']; H1=s1['reference']['topicwords']
for k in range(4): print('T%d'%k,' '.join(names[i] for i in H1[k].argsort()[::-1][:8]))
print(s1['summary'])
REST=int(np.argmax(np.bincount([int(t.split('_')[1]) for t in d1['Consensus topic'] if t],minlength=4)))
idx=[j for j,t in enumerate(d1['Consensus topic']) if t==f'Topic_{REST}']
print('Resttopic T%d:'%REST,len(idx),'Etappen')
X=mx['tf_matrix'][idx]; lab2=[labels[j] for j in idx]
keep=np.asarray(X.sum(1)).ravel()>0
# Stufe 2: Untermodell, K2 = 3..8, je 50 Läufe
tab,det=M5.stability_over_k(X,list(range(3,9)),n_runs=50,doc_labels=lab2)
pd.set_option('display.width',220); print(tab.round(3).to_string(index=False))
for K2,r in det.items():
    H2=r['reference']['topicwords']; t=r['topics']
    print(f'-- K2={K2}')
    for k in range(K2):
        print(f"   S{k} rep {t.iloc[k]['Reproduced (share of runs, sim >= 0.8)']:.0%} n={t.iloc[k]['Documents (consensus)']} stabil={t.iloc[k]['Stable documents']} |",' '.join(names[i] for i in H2[k].argsort()[::-1][:10]))
pickle.dump(dict(s1=s1,REST=REST,idx=idx,tab=tab,det=det,U=U,labels=labels),open(arbeit('two_stage.pkl'),'wb'))
