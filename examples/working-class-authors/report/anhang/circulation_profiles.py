# -*- coding: utf-8 -*-
# Profils d'intensité de circulation par acteur, axe VERTICAL (HISCAM).
import csv, statistics
from collections import defaultdict

DELTA=3.0  # seuil pour qu'un pas compte comme montée/descente (sinon "plat")

A={r['entry_id']:r for r in csv.DictReader(open('out/actors.csv',encoding='utf-8-sig'))}
S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))
byact=defaultdict(list)
for s in S: byact[s['entry_id']].append(s)

rows=[]
for eid,sts in byact.items():
    meta=A.get(eid,{})
    coded=[s for s in sorted(sts,key=lambda x:int(x['stage_index'])) if s['hiscam']]
    cams=[float(s['hiscam']) for s in coded]
    n_total=int(meta.get('n_stages',len(sts)) or len(sts))
    n_coded=len(cams)
    prof={'entry_id':eid,'surname':meta.get('surname',''),'forename':meta.get('forename',''),
          'destinations':meta.get('destinations',''),'birth_year':meta.get('birth_year',''),
          'n_stages_total':n_total,'n_stages_coded':n_coded}
    if n_coded==0:
        prof.update({k:'' for k in ['cam_first','cam_last','cam_min','cam_max','range',
            'amplitude','net','mean_step','n_reversals','volatility','n_distinct_occ','n_distinct_hisclass']})
        rows.append(prof); continue
    steps=[cams[i+1]-cams[i] for i in range(len(cams)-1)]
    amplitude=sum(abs(d) for d in steps)
    rng=max(cams)-min(cams)
    # reversals: sign changes among non-flat steps
    signs=[(1 if d>=DELTA else (-1 if d<=-DELTA else 0)) for d in steps]
    nz=[s for s in signs if s!=0]
    reversals=sum(1 for i in range(len(nz)-1) if nz[i]!=nz[i+1])
    prof.update({
        'cam_first':round(cams[0],1),'cam_last':round(cams[-1],1),
        'cam_min':round(min(cams),1),'cam_max':round(max(cams),1),
        'range':round(rng,1),'amplitude':round(amplitude,1),
        'net':round(cams[-1]-cams[0],1),
        'mean_step':round(amplitude/(n_coded-1),1) if n_coded>1 else 0,
        'n_reversals':reversals,
        'volatility':round(amplitude/rng,2) if rng>0 else '',
        'n_distinct_occ':len({s['hisco_code'] for s in coded}),
        'n_distinct_hisclass':len({s['hisclass'] for s in coded if s['hisclass']}),
    })
    rows.append(prof)

rows.sort(key=lambda r:int(r['entry_id']))
cols=['entry_id','surname','forename','destinations','birth_year','n_stages_total','n_stages_coded',
      'cam_first','cam_last','cam_min','cam_max','range','amplitude','net','mean_step',
      'n_reversals','volatility','n_distinct_occ','n_distinct_hisclass']
with open('out/circulation_profiles.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)

# ---- résumé sur les acteurs avec ≥2 étapes codées (où l'amplitude a un sens) ----
M=[r for r in rows if isinstance(r['n_stages_coded'],int) and r['n_stages_coded']>=2]
def stat(key):
    v=[r[key] for r in M if r[key]!='']
    v=[float(x) for x in v]
    return f"méd {statistics.median(v):.1f} | moy {statistics.mean(v):.1f} | max {max(v):.1f}"
print(f"acteurs analysables (≥2 étapes codées) : {len(M)}/163")
print(f"  amplitude verticale totale  : {stat('amplitude')}")
print(f"  étendue (range)             : {stat('range')}")
print(f"  déplacement net             : {stat('net')}")
print(f"  renversements de direction  : {stat('n_reversals')}")
print(f"  volatilité (ampl/étendue)   : {stat('volatility')}")
rev=[r['n_reversals'] for r in M]
print(f"\n  acteurs avec ≥1 renversement : {sum(1 for x in rev if x>=1)}/{len(M)} ({100*sum(1 for x in rev if x>=1)/len(M):.0f}%)")
print(f"  acteurs avec ≥2 renversements: {sum(1 for x in rev if x>=2)}/{len(M)} ({100*sum(1 for x in rev if x>=2)/len(M):.0f}%)")
# top circulateurs
print("\n--- top 8 « circulateurs » (amplitude verticale) ---")
for r in sorted(M,key=lambda r:-r['amplitude'])[:8]:
    print(f"  {r['surname']:<14} ampl={r['amplitude']:>5} étendue={r['range']:>4} renvers.={r['n_reversals']} net={r['net']:>5} ({r['n_stages_coded']} ét. codées)")
