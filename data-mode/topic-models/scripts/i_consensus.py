from pfade import *
import sys, importlib.util
M5=mta_core()
from g_crossing import *
from h_refine import BASE, RESID
U=units('occ'); cw,_=M5.preprocess_corpus([u[2] for u in U],STOP,3); mx=M5.build_matrices(cw,STOP,2,0.95)
labels=[f'{e}_{i}' for e,i,_ in U]
table,det=M5.stability_over_k(mx['tf_matrix'],[4,5,6],method='nmf',n_runs=50,doc_labels=labels)
pd.set_option('display.width',200)
print(table.round(3).to_string(index=False))
Hc=hisclass_cross()
for K in (4,5,6):
    r=det[K]; t=r['topics']; names=mx['tf_names']; H=r['reference']['topicwords']
    print(f'\n== K={K}')
    for k in range(K):
        row=t.iloc[k]
        print(f"  T{k} sim {row['Mean similarity']:.2f} (min {row['Min similarity']:.2f}), reproduziert {row['Reproduced (share of runs, sim >= 0.8)']:.0%}, Dok {row['Documents (consensus)']}, stabil {row['Stable documents']} | {' '.join(names[i] for i in H[k].argsort()[::-1][:6])}")
    d=r['documents']
    for mode in ('alle','nur stabile'):
        lab={}
        for (e,i,_),(_,row) in zip(U,d.iterrows()):
            ct=row['Consensus topic']
            if not ct or (mode=='nur stabile' and not row['Stable']): continue
            lab[(e,i)]=BASE[K][int(ct.split('_')[1])]
        # cross
        by=defaultdict(list)
        for (e,i),l in lab.items(): by[e].append((i,l))
        T={}
        for e,v in by.items():
            if len(v)<2: continue
            q=[l for _,l in sorted(v)]; T[e]=any(q[j]=='M' and 'N' in q[j+1:] for j in range(len(q)))
        both=[e for e in Hc if e in T]
        print(f"  Konsens ({mode}): Etappen {len(lab)}, Übergang {sum(T.values())}/{len(T)} ({sum(T.values())/len(T):.0%}), kappa {KAPPA([Hc[e] for e in both],[T[e] for e in both]):.2f} (n={len(both)})")
det_out={K:det[K]['documents'] for K in det}
import pickle; pickle.dump((table,{K:(det[K]['documents'],det[K]['topics'],det[K]['runs']) for K in det}),open(arbeit('consensus_4_6.pkl'),'wb'))
