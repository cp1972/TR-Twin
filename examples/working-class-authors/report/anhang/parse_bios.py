# -*- coding: utf-8 -*-
import os, re, csv, json, statistics
from collections import Counter

ROOT = b'/home/claude/data'
def find_dir(name):
    for dp,dirs,fs in os.walk(ROOT):
        if os.path.basename(dp)==name: return dp
    return None
DIR_MASTER = find_dir(b'Akteure_KunstMedien')
DIR_ART    = find_dir(b'Akteure_Kunst')
DIR_MEDIA  = find_dir(b'Akteure_Medien')

def ids_in(d):
    s=set()
    for f in os.listdir(d):
        if f.endswith(b'.txt'):
            m=re.match(rb'(\d+)',f)
            if m: s.add(m.group(1).decode())
    return s
ART_IDS, MEDIA_IDS = ids_in(DIR_ART), ids_in(DIR_MEDIA)

def read_text(p):
    raw=open(p,'rb').read()
    try: return raw.decode('utf-8-sig')
    except: return raw.decode('latin-1')
def paras(t): return [p.strip() for p in re.split(r'\n\s*\n',t) if p.strip()]

def parse_header(h):
    m=re.match(r'^\s*(\d+)\s+([^,]+),\s*([^,]+),\s*(.*)$',h,re.S)
    if not m:
        m2=re.match(r'^\s*(\d+)\s+(.*)$',h,re.S)
        eid0=m2.group(1) if m2 else ''
        title0=(m2.group(2).split(' (')[0].strip() if m2 else h.strip())
        return eid0,'','',title0,''
    eid,surname,forename,rest=m.groups(); rest=' '.join(rest.split())
    surname=surname.strip(" []")
    title=rest.split(' (')[0].strip()
    yrs=re.findall(r'(1[6-9]\d{2}|20\d{2})',rest)
    return eid.strip(),surname,' '.join(forename.split()).strip(" []"),title,(yrs[-1] if yrs else '')

def find_bio_idx(ps):
    for i,p in enumerate(ps):
        if re.search(r'\bBorn\b',p): return i
    return 1 if len(ps)>1 else 0

TERM=r'(?=[.,;(]| and\b| who\b| whose\b| died\b| in\b|$)'
OCC=r"([a-z][a-z\-' ]+?)"
FATHER_PATS=[
    r'father\s*\(\s*'+OCC+r'\s*\)',                                            # Father (dramatic writer)
    r'father,?\s+(?:a|an)\s+'+OCC+TERM,                                        # Father, a joiner,
    r'father\b[^.(]*?\bwas\b\s+(?:a|an)?\s*'+OCC+TERM,                         # Father was a joiner
    r'father\b[^.(]*?\b(?:employed|worked)\b[^.(]*?\b(?:as|at)\s+(?:a|an)?\s*'+OCC+TERM,
    r'\b(?:son|daughter|child|orphan)\b[^.(]*?\bof\b\s+(?:a|an|the)?\s*'+OCC+TERM,  # Son of / child...of a weaver
    r'children\s+of\s+(?:a|an|the)?\s*'+OCC+TERM,
    r'\bof\s+(?:a|an)\s+'+OCC+r'\s+and\b',
    r'parents?\s+(?:were|was)\s+(?:both\s+)?'+OCC+TERM,
]
BAD_PREFIX=('whom','which','them','age','his','her','the','one','both','poor','humble',
            'small','working','raised','brought','born','left','only','deserted','unknown')

def parse_bio(b):
    o={'birth_year':'','birth_place':'','father_occupation':'','father_raw':'','married':'','residences':''}
    my=re.search(r'Born[^.]*?(1[6-9]\d{2}|20\d{2})',b)
    if my: o['birth_year']=my.group(1)
    mp=re.search(r'Born[^.]*?\bin\b\s+([A-Z][^.,;(]+)',b)
    if mp: o['birth_place']=mp.group(1).strip()
    for pat in FATHER_PATS:
        m=re.search(pat,b,re.I)
        if m:
            occ=re.sub(r'\s+',' ',m.group(1)).strip(" .,'-")
            low=occ.lower()
            if 3<=len(occ)<=50 and not low.startswith(BAD_PREFIX) and 'children' not in low:
                o['father_occupation']=occ
                ms=re.search(r'[^.]*'+re.escape(m.group(1))+r'[^.]*\.',b)
                o['father_raw']=ms.group(0).strip() if ms else ''
                break
    o['married']='yes' if re.search(r'\bMarried\b',b) else ''
    mr=re.search(r'Lived (?:in|at)\s+([^.]+)\.',b)
    if mr: o['residences']=' '.join(mr.group(1).split())
    return o

def split_stages(para):
    out=[]
    for c in [c.strip(' .') for c in para.split(';') if c.strip(' .')]:
        age=''
        ma=re.search(r'aged\s*(\d+)',c)
        if ma: age=ma.group(1)
        label=re.sub(r'\s*\(aged[^)]*\)','',c).strip(' .')
        out.append((label,age))
    return out

actors,stages=[],[]
master=sorted([f for f in os.listdir(DIR_MASTER) if f.endswith(b'.txt')])
for f in master:
    t=read_text(os.path.join(DIR_MASTER,f)); ps=paras(t)
    if not ps: continue
    eid,surname,forename,title,yr=parse_header(ps[0])
    if not eid:
        mfn=re.match(rb'(\d+)',f); eid=mfn.group(1).decode() if mfn else ('NOID_'+f.decode('latin-1'))
    bidx=find_bio_idx(ps); bio=parse_bio(ps[bidx]) if bidx<len(ps) else {}
    occ_idx=bidx+1; occ_para=ps[occ_idx] if occ_idx<len(ps) else ''
    affil=ps[occ_idx+1] if occ_idx+1<len(ps)-1 else ''
    content=ps[-1] if len(ps)>occ_idx+1 else ''
    st=split_stages(occ_para) if occ_para else []
    ra=eid in ART_IDS; rm=eid in MEDIA_IDS
    dest='Art+Media' if (ra and rm) else ('Art' if ra else ('Media' if rm else '?'))
    actors.append({'entry_id':eid,'surname':surname,'forename':forename,
        'reached_art':'yes' if ra else '','reached_media':'yes' if rm else '','destinations':dest,
        'birth_year':bio.get('birth_year',''),'birth_place':bio.get('birth_place',''),
        'father_occupation':bio.get('father_occupation',''),'father_raw':bio.get('father_raw',''),
        'married':bio.get('married',''),'residences':bio.get('residences',''),
        'n_stages':len(st),'career_raw':' '.join(occ_para.split()),
        'affiliations_raw':' '.join(affil.split()),'content_tone':' '.join(content.split()),
        'title':title,'year_pub':yr,'source_file':f.decode('latin-1')})
    for i,(label,age) in enumerate(st,1):
        stages.append({'entry_id':eid,'surname':surname,'forename':forename,'destinations':dest,
            'stage_index':i,'occupation_raw':label,'age':age,
            'hisco_code':'','hisclass':'','hiscam':'','tr_category':''})

def k(r):
    try: return int(r['entry_id'])
    except: return 10**9
actors.sort(key=k); stages.sort(key=lambda r:(k(r),r['stage_index']))

os.makedirs('/home/claude/out',exist_ok=True)
acols=['entry_id','surname','forename','reached_art','reached_media','destinations',
       'birth_year','birth_place','father_occupation','father_raw','married','residences',
       'n_stages','career_raw','affiliations_raw','content_tone','title','year_pub','source_file']
scols=['entry_id','surname','forename','destinations','stage_index','occupation_raw','age',
       'hisco_code','hisclass','hiscam','tr_category']
with open('/home/claude/out/actors.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=acols); w.writeheader(); w.writerows(actors)
with open('/home/claude/out/stages_long.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=scols); w.writeheader(); w.writerows(stages)

n=len(actors)
def pct(x): return f'{x} ({100*x/n:.0f}%)'
ns=sorted(a['n_stages'] for a in actors)
qa={'unique_actors':n,'stages_total':len(stages),'avg_stages':round(len(stages)/n,2),
    'stages_min_med_max':[ns[0],int(statistics.median(ns)),ns[-1]],
    'with_birth_year':pct(sum(1 for a in actors if a['birth_year'])),
    'with_father_occ':pct(sum(1 for a in actors if a['father_occupation'])),
    'with_residences':pct(sum(1 for a in actors if a['residences'])),
    'destinations':dict(Counter(a['destinations'] for a in actors)),
    'noid_or_q':[ (a['entry_id'],a['surname'],a['source_file']) for a in actors if a['destinations']=='?' or str(a['entry_id']).startswith('NOID')]}
print(json.dumps(qa,ensure_ascii=False,indent=2))
