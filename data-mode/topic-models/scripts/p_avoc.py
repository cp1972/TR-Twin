from pfade import *
import importlib.util, pickle, re
M5=mta_core()
from f_separate import units
from common import STOP, ACT
from l_dates import raw_year
UA=units('avoc'); cw,_=M5.preprocess_corpus([u[2] for u in UA],STOP,3); mx=M5.build_matrices(cw,STOP,2,0.95)
r=M5.topic_stability(mx['tf_matrix'],5,n_runs=50,doc_labels=[f'{e}_{j}' for e,j,_ in UA])
H=r['reference']['topicwords']; names=mx['tf_names']
for k in range(5): print('A%d'%k,' '.join(names[i] for i in H[k].argsort()[::-1][:8]))
dated=0; rows=[]
for (e,j,t),(_,d) in zip(UA,r['documents'].iterrows()):
    try: b=int(ACT[e]['birth_year'])
    except ValueError: b=None
    y,src=raw_year(t,b)
    if y is not None and b and not (b+4<=y<=b+90): y=None
    rows.append(dict(e=e,j=j,text=t,topic=d['Consensus topic'],stable=bool(d['Stable']),year=y))
    dated+= y is not None
print('Nebentätigkeitszeilen',len(rows),'datiert',dated,'stabil+datiert',sum(1 for x in rows if x['year'] and x['stable'] and x['topic']))
print('Akteure mit datierter Nebentätigkeit',len({x['e'] for x in rows if x['year'] and x['stable'] and x['topic']}))
pickle.dump(rows,open(arbeit('avoc_rows.pkl'),'wb'))
