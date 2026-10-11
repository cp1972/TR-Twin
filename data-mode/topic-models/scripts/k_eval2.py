from pfade import *
import pickle
from g_crossing import *
D=pickle.load(open(arbeit('two_stage.pkl'),'rb'))
s1,REST,idx,det,U=D['s1'],D['REST'],D['idx'],D['det'],D['U']
BASE4={0:'M',1:'M',2:'N',3:'N'}
SUBS={6:{0:'N',1:'N',2:'N',3:'M',4:'N',5:'N'}, 8:{0:'N',1:'N',2:'N',3:'M',4:'N',5:'N',6:'X',7:'N'}}
Hc=hisclass_cross()
HCL={(s['entry_id'],int(s['stage_index'])):('N' if int(s['hisclass'])<=5 else 'M') for s in STG if s['hisclass']}
txt={(s['entry_id'],int(s['stage_index'])):s['occupation_raw'] for s in STG}
d1=s1['documents']
def build(K2,stable_only):
    lab={}; d2=det[K2]['documents']; sub=dict(zip(idx,range(len(idx))))
    for j,(e,i,_) in enumerate(U):
        ct=d1['Consensus topic'][j]
        if not ct: lab[(e,i)]='X'; continue
        if stable_only and not d1['Stable'][j]: lab[(e,i)]='X'; continue
        t=int(ct.split('_')[1])
        if t!=REST: lab[(e,i)]=BASE4[t]; continue
        r=d2.iloc[sub[j]]
        if not r['Consensus topic'] or (stable_only and not r['Stable']): lab[(e,i)]='X'; continue
        lab[(e,i)]=SUBS[K2][int(r['Consensus topic'].split('_')[1])]
    return lab
def cross(lab):
    by=defaultdict(list)
    for (e,i),l in lab.items():
        if l!='X': by[e].append((i,l))
    T={}
    for e,v in by.items():
        if len(v)<2: continue
        q=[l for _,l in sorted(v)]; T[e]=any(q[k]=='M' and 'N' in q[k+1:] for k in range(len(q)))
    return T
rows=[]
for K2 in (6,8):
    for so in (False,True):
        lab=build(K2,so); T=cross(lab); both=[e for e in Hc if e in T]
        st=[(HCL[k],l) for k,l in lab.items() if k in HCL and l!='X']
        c=Counter((Hc[e],T[e]) for e in both)
        one=[e for e in both if T[e] and not Hc[e]]
        unc=sum(1 for e in one if any(lab[(a,i)]=='M' and (a,i) not in HCL for (a,i) in lab if a==e))
        det_n=sum(1 for l in lab.values() if l!='X')
        print(f"K2={K2} {'nur stabile' if so else 'alle      '}: bestimmt {det_n}/996 ({det_n/996:.0%}), Etappen-Widerspruch {np.mean([a!=b for a,b in st]):.0%}, Übergang {sum(T.values())}/{len(T)} ({sum(T.values())/len(T):.0%}), kappa {KAPPA([Hc[e] for e in both],[T[e] for e in both]):.2f} (n={len(both)}), Topics ja/HC nein {c[(False,True)]} (davon ohne HISCO-Code {unc}), HC ja/Topics nein {c[(True,False)]}")
        rows.append((K2,so,lab,T))
# Liste für Durchsicht: Hauptvariante K2=6, nur stabile
K2,so,lab,T=rows[1]
one=sorted([e for e in Hc if e in T and T[e] and not Hc[e]],key=int)
other=sorted([e for e in Hc if e in T and not T[e] and Hc[e]],key=int)
import csv
with open(ergeb('konsens_abweichungen.csv'),'w',encoding='utf-8-sig',newline='') as fh:
    w=csv.writer(fh); w.writerow(['richtung','entry_id','name','etappe','taetigkeit','hisclass','topics (M/N/X)','ihr_urteil'])
    for tag,L in (('Topics sehen Übergang, HISCLASS nicht',one),('HISCLASS sieht Übergang, Topics nicht',other)):
        for e in L:
            for i in sorted(i for (a,i) in lab if a==e):
                w.writerow([tag,e,ACT[e]['surname'],i,txt[(e,i)],{'M':'manuell','N':'nicht-manuell'}.get(HCL.get((e,i)),''),lab[(e,i)],''])
print(len(one),len(other))
pickle.dump(rows,open(arbeit('two_stage_eval.pkl'),'wb'))
