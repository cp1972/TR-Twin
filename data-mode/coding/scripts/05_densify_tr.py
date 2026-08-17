# -*- coding: utf-8 -*-
# Gezielte Verdichtung auf Laufbahnebene, danach beide TR-Regeln neu berechnet.
# Die Näherungscodes generischer Berufsbezeichnungen (als ungenau markiert) kommen wieder
# hinein, allein um die Laufbahnen zu verdichten; dann tr_absolute und tr_relative neu.
import csv, statistics, re
from collections import defaultdict, Counter

GENERIC_CODES = {  # Begriff -> (HISCO, Bezeichnung, HISCLASS, HISCAM)
 'manager':    ('21110','General Manager','3','84.88'),
 'agent':      ('45230','Canvasser','11','51.9'),
 'proprietor': ('41020','Working Proprietor (Wholesale/Retail)','3','81.33'),
 'clerk':      ('39310','Office Clerk, General','5','69.59'),
 'shopkeeper': ('41020','Working Proprietor (Wholesale/Retail)','3','81.33'),
}  # 'assistant' reste sans code
VARS = {'manager':['manager'],'agent':['agent'],'proprietor':['proprietor','proprietress'],
        'clerk':['clerk'],'shopkeeper':['shopkeeper','grocer','draper','dealer']}
def has(t,vs): return any(re.search(r'\b'+re.escape(v),t.lower()) for v in vs)

S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))
for s in S:
    if s['hisco_code']:
        s['code_tier']='statut'; continue
    for con,vs in VARS.items():
        if has(s['occupation_raw'],vs):
            h,en,hc,cam=GENERIC_CODES[con]
            s.update(hisco_code=h,hisclass=hc,hiscam=cam,code_method='generic',
                     code_review='yes',code_tier='trajectoire'); break
    else:
        s.setdefault('code_tier','')
for s in S: s.setdefault('code_tier','')

byact=defaultdict(list)
for s in S: byact[s['entry_id']].append(s)
cams=[float(s['hiscam']) for s in S if s['hiscam']]
HIGH=round(statistics.quantiles(cams,n=3)[1],1); LOW=round(statistics.quantiles(cams,n=3)[0],1)
DELTA=3.0; TR={3:'Etablierte',2:'Anwaerter',1:'Bewahrende',0:'Enttaeuschte'}
for eid,sts in byact.items():
    prev=None
    for s in sorted(sts,key=lambda x:int(x['stage_index'])):
        if not s['hiscam']: s['tr_absolute']=''; continue
        h=float(s['hiscam']); d=(h-prev) if prev is not None else 0.0
        s['tr_absolute']=TR[3 if h>=HIGH else (0 if ((prev is not None and d<=-DELTA) or h<=LOW) else (2 if (prev is not None and d>=DELTA) else 1))]; prev=h
TOP,BOT,DR=0.80,0.20,0.10
for eid,sts in byact.items():
    cs=[s for s in sorted(sts,key=lambda x:int(x['stage_index'])) if s['hiscam']]
    for s in sts:
        if not s['hiscam']: s['tr_relative']=''
    c2=[float(s['hiscam']) for s in cs]
    if len(cs)<2 or max(c2)==min(c2):
        for s in cs: s['tr_relative']='(indéterminé)'; 
        continue
    lo,hi=min(c2),max(c2); rng=hi-lo; prev=None
    for s in cs:
        pos=(float(s['hiscam'])-lo)/rng; d=(pos-prev) if prev is not None else 0.0
        s['tr_relative']=TR[3 if pos>=TOP else (0 if ((prev is not None and d<=-DR) or pos<=BOT) else (2 if (prev is not None and d>=DR) else 1))]; prev=pos

cols=list(S[0].keys())
with open('out/stages_long_final.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(S)
print('densification + TR recalculés ; colonnes:', cols)
