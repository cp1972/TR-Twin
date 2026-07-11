# -*- coding: utf-8 -*-
import csv, json
from collections import defaultdict

A={r['entry_id']:r for r in csv.DictReader(open('out/actors.csv',encoding='utf-8-sig'))}
S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))
CATFR={'Etablierte':'etabli','Anwaerter':'aspirant','Bewahrende':'conservateur','Enttaeuschte':'decu'}

# ---- 1) table-contrat CSV (format simulateur : aid,annee,structure,categorie,sequence) ----
rows=[]
for r in S:
    st=r.get('structure','')
    if st not in ('A','B','C','D'): continue
    eid=r['entry_id']; by=A.get(eid,{}).get('birth_year','')
    try: base=int(by)
    except: base=1850
    yr=base+15+int(r['stage_index'])*4
    cat=CATFR.get(r.get('tr_absolute',''),'')
    sq=r.get('sequence','') if r.get('sequence','') in ('A','B','C','D') else ''
    rows.append([eid,yr,st,cat,sq])
rows.sort(key=lambda x:(x[0],x[1]))
with open('out/cohorte_contrat.csv','w',encoding='utf-8',newline='') as fh:
    w=csv.writer(fh); w.writerow(['aid','annee','structure','categorie','sequence']); w.writerows(rows)
print(f"cohorte_contrat.csv : {len(rows)} lignes")

# ---- transition matrix (structure -> structure), per actor ordered ----
byA=defaultdict(list)
for r in S:
    if r.get('structure','') in ('A','B','C','D'):
        byA[r['entry_id']].append((int(r['stage_index']),r['structure']))
flow=[[0]*4 for _ in range(4)]; IDX={'A':0,'B':1,'C':2,'D':3}
for eid,sts in byA.items():
    seq=[s for _,s in sorted(sts)]
    path=[seq[0]]+[seq[i] for i in range(1,len(seq)) if seq[i]!=seq[i-1]]
    for i in range(len(path)-1):
        flow[IDX[path[i]]][IDX[path[i+1]]]+=1
json.dump(flow,open('out/flow.json','w'))
print("flow matrix:",flow)
