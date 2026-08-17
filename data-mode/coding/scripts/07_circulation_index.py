# -*- coding: utf-8 -*-
# Zusammengesetzter Zirkulationsindex aus drei Achsen: vertikal (HISCAM), horizontal (Sequenz), transversal (Struktur)
import csv, statistics
from collections import defaultdict

W=(1/3,1/3,1/3)  # Gewichtung (vertikal, horizontal, transversal) — änderbar

V={r['entry_id']:r for r in csv.DictReader(open('out/circulation_profiles.csv',encoding='utf-8-sig'))}
T={r['entry_id']:r for r in csv.DictReader(open('out/structure_profiles.csv',encoding='utf-8-sig'))}

def num(x):
    try: return float(x)
    except: return None

# auswertbare Akteure sammeln: mindestens zwei HISCAM-codierte UND zwei strukturierte Etappen
rows=[]
for eid in V:
    v=V[eid]; t=T.get(eid,{})
    n_cam=int(v['n_stages_coded']) if v['n_stages_coded'] else 0
    n_occ=int(t.get('n_occ_stages',0) or 0)
    if n_cam<2 or n_occ<2: continue
    rows.append({
        'entry_id':eid,'surname':v['surname'],'destinations':v['destinations'],
        'amplitude':num(v['amplitude']),'n_reversals':int(v['n_reversals']) if v['n_reversals'] else 0,
        'horizontal_cross':int(t.get('horizontal_cross',0) or 0),
        'transversal_cross':int(t.get('transversal_cross',0) or 0),
        'n_struct_total':int(t.get('n_struct_total',0) or 0),
        'n_cam':n_cam,'n_occ':n_occ,
    })

def pctile(vals):
    # Perzentilrang: Anteil der Akteure mit Wert <= x, bei Gleichstand der mittlere Rang
    s=sorted(vals); n=len(vals)
    out=[]
    for x in vals:
        # mittlere Position
        lo=sum(1 for y in s if y<x); eq=sum(1 for y in s if y==x)
        out.append((lo+ (eq+1)/2)/n)
    return out

pV=pctile([r['amplitude'] for r in rows])
pH=pctile([r['horizontal_cross'] for r in rows])
pT=pctile([r['transversal_cross'] for r in rows])
for i,r in enumerate(rows):
    r['pV']=round(pV[i],3); r['pH']=round(pH[i],3); r['pT']=round(pT[i],3)
    r['index']=round(100*(W[0]*pV[i]+W[1]*pH[i]+W[2]*pT[i]),1)
    r['confiance']='faible' if min(r['n_cam'],r['n_occ'])<3 else ('moyenne' if min(r['n_cam'],r['n_occ'])<4 else 'bonne')

rows.sort(key=lambda r:-r['index'])
cols=['entry_id','surname','destinations','amplitude','n_reversals','horizontal_cross','transversal_cross',
      'n_struct_total','pV','pH','pT','index','confiance','n_cam','n_occ']
with open('out/circulation_index.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)

idx=[r['index'] for r in rows]
print(f"acteurs avec indice (≥2 ét. codées + ≥2 ét. structurées) : {len(rows)}/163")
print(f"indice : méd {statistics.median(idx):.1f} | moy {statistics.mean(idx):.1f} | min {min(idx)} | max {max(idx)}")
conf=defaultdict(int)
for r in rows: conf[r['confiance']]+=1
print("confiance :", dict(conf))
# Korrelation mit dem Zielzustand
print("\nindice moyen par destination :")
byd=defaultdict(list)
for r in rows: byd[r['destinations']].append(r['index'])
for d in ['Art','Media','Art+Media']:
    if byd[d]: print(f"  {d:<10}: {statistics.mean(byd[d]):.1f}  (n={len(byd[d])})")
print("\n--- top 10 circulateurs (indice composite) ---")
for r in rows[:10]:
    print(f"  {r['surname']:<14} idx={r['index']:>5}  V={r['pV']:.2f} H={r['pH']:.2f} T={r['pT']:.2f}  (ampl={r['amplitude']:.0f} renv={r['n_reversals']} trans={r['transversal_cross']} struct={r['n_struct_total']}) [{r['confiance']}]")
print("\n--- bottom 5 (circulation faible) ---")
for r in rows[-5:]:
    print(f"  {r['surname']:<14} idx={r['index']:>5}  V={r['pV']:.2f} H={r['pH']:.2f} T={r['pT']:.2f}")
