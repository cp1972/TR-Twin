from pfade import *
import pickle, json
from collections import Counter, defaultdict
from common import STG, ACT
from m_contracts import circulation_values, stages_by, ids
C = pickle.load(open(arbeit('codings.pkl'),'rb'))
CAM = {(s['entry_id'], int(s['stage_index'])): (float(s['hiscam']) if s['hiscam'] else None) for s in STG}
def transitions(codes):
    val,_,_ = circulation_values(codes)
    out=[]
    for e in ids:
        seq=[(int(s['stage_index']),codes[(e,int(s['stage_index']))]) for s in stages_by[e]]
        seq=[(i,c) for i,c in seq if c[0]]
        for (i1,c1),(i2,c2) in zip(seq,seq[1:]):
            typ='Strukturwechsel' if c1[0]!=c2[0] else 'Sequenzwechsel' if c1!=c2 else 'gleiche Position'
            h1,h2=CAM[(e,i1)],CAM[(e,i2)]
            hd=None if h1 is None or h2 is None else ('auf' if h2-h1>=3 else 'ab' if h2-h1<=-3 else 'gleich')
            v1,v2=val.get(''.join(c1)),val.get(''.join(c2))
            idir=None if typ=='gleiche Position' else ('auf' if v2-v1>=0.05 else 'ab' if v2-v1<=-0.05 else 'gleich')
            out.append(dict(e=e,typ=typ,hiscam=hd,intern=idir))
    return out
res={}
for name,codes in (('Topics',C['TOP']),('Lexikon',C['LEX'])):
    T=transitions(codes)
    tab=Counter((t['typ'],t['hiscam']) for t in T)
    n_typ=Counter(t['typ'] for t in T)
    agree=Counter((t['intern'],t['hiscam']) for t in T if t['typ']=='Strukturwechsel' and t['hiscam'])
    print('==',name,'Übergänge',len(T),dict(n_typ))
    for typ in ('Strukturwechsel','Sequenzwechsel','gleiche Position'):
        d={h:tab[(typ,h)] for h in ('auf','gleich','ab')}; m=sum(d.values())
        print(f'  {typ:<17} mit HISCAM beidseitig {m}:',{k:f'{v} ({v/m:.0%})' for k,v in d.items()} if m else '')
    print('  Strukturwechsel intern x HISCAM:',dict(agree))
    res[name]=dict(n=len(T),n_typ=dict(n_typ),tab={f'{a}|{b}':v for (a,b),v in tab.items()},agree={f'{a}|{b}':v for (a,b),v in agree.items()})
json.dump(res,open(ergeb('circ_mob.json'),'w'),ensure_ascii=False,indent=1)
