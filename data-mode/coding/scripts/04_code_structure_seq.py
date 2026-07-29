# -*- coding: utf-8 -*-
# Structure (domaine) + Séquence (mode) par étape, couche occupationnelle + avocationnelle.
# Structures : A=Kultur B=Politik C=Wirtschaft D=Medien
# Séquences (mode dans la structure hôte) : A=noyau/relation B=représentation C=production D=diffusion/contrôle
import csv, re, statistics
from collections import defaultdict, Counter

# concept -> (structure, séquence, à_valider) ; ancres de l'utilisateur en dur
SS = {
 # --- Kultur (A) ---
 'author':('A','A',False),'painter_artist':('A','A',False),'musician':('A','A',False),'actor':('A','A',False),
 'teacher':('A','A',True),'lecturer':('A','A',False),                      # ancre A.A
 'minister_religion':('A','B',False),'missionary':('A','B',False),          # ancre A.B
 'printer':('A','C',False),'compositor':('A','C',False),                    # ancre A.C
 'publisher':('A','D',True),'bookseller':('A','D',True),
 # --- Politik (B) ---
 'legislator':('B','B',True),'union_official':('B','D',True),'secretary':('B','B',True),
 # --- Wirtschaft (C) ---
 'labourer':('C','C',False),'weaver':('C','C',False),'spinner':('C','C',False),'shoemaker':('C','C',False),
 'tailor':('C','C',False),'carpenter':('C','C',False),'joiner':('C','C',False),'blacksmith':('C','C',False),
 'mason':('C','C',False),'fitter':('C','C',False),'engineer':('C','C',True),'miner':('C','C',False),
 'farm_labourer':('C','C',False),'farmer':('C','A',True),'seaman':('C','C',True),'messenger':('C','D',True),
 'warehouseman':('C','C',True),'gardener':('C','C',True),'servant':('C','C',True),'baker':('C','C',False),
 'butcher':('C','C',False),'porter':('C','C',True),'policeman':('B','C',False),'soldier':('B','C',False),
 'salesman':('C','C',False),'manager':('C','A',True),'agent':('C','D',True),'proprietor':('C','A',True),
 'clerk':('C','C',True),'shopkeeper':('C','D',True),'assistant':('C','C',True),
 # --- Medien (D) ---
 'journalist':('D','A',True),'editor':('D','D',True),'news_vendor':('D','C',True),
}
VAR = {
 'journalist':['journalist','correspondent','reporter','contributor'],'editor':['editor','sub-editor'],
 'author':['author','writer','novelist','poet','essayist'],'printer':['printer','printing'],
 'compositor':['compositor','typesetter'],'publisher':['publisher'],'news_vendor':['newsboy','news-boy','newsvendor'],
 'painter_artist':['artist','painter','sculptor'],'musician':['musician','composer','singer'],'actor':['actor','comedian'],
 'teacher':['teacher','schoolteacher','schoolmaster','tutor','governess'],'lecturer':['lecturer','professor'],
 'legislator':['mp','parliament','legislator','councillor','alderman','mayor','candidate'],
 'union_official':['union','organiser','organizer','agitator','propagandist'],'secretary':['secretary'],
 'minister_religion':['minister','clergyman','preacher','pastor','curate','vicar','priest','rector'],'missionary':['missionary'],
 'labourer':['labourer','navvy'],'weaver':['weaver','weaving'],'spinner':['spinner','spinning'],
 'shoemaker':['shoemaker','cobbler','bootmaker'],'tailor':['tailor','draper'],'carpenter':['carpenter'],'joiner':['joiner'],
 'blacksmith':['blacksmith','smith'],'mason':['mason','bricklayer'],'fitter':['fitter','turner','mechanic'],
 'engineer':['engineer'],'seaman':['sailor','seaman','mariner'],'farm_labourer':['ploughboy','farm-boy','agricultural','cowherd','shepherd'],
 'farmer':['farmer','husbandman','crofter'],'messenger':['messenger','errand-boy','office-boy','van-boy'],
 'warehouseman':['warehouse'],'gardener':['gardener'],'servant':['servant','footman'],'baker':['baker'],'butcher':['butcher'],
 'porter':['porter'],'policeman':['policeman','constable','police'],'soldier':['soldier','enlisted','regiment'],
 'salesman':['salesman','traveller','commercial'],'bookseller':['bookseller'],'manager':['manager'],'agent':['agent'],
 'proprietor':['proprietor'],'clerk':['clerk'],'shopkeeper':['shopkeeper','grocer','dealer'],'assistant':['assistant'],
 'miner':['miner','collier','pitman','colliery'],
}
# avocational lexicon (affiliations + publications) -> (structure, séquence)
AVOC = [
 # religion -> A.B
 (['church','chapel','methodist','baptist','congregational','wesleyan','quaker','catholic','dissenting',
   'lay preacher','sunday school','nonconformist','unitarian','salvation army'],'A','B'),
 # culture proper -> A.A
 (['poet','poetry','poems','novel','novelist','hymn','playwright','painting','choir','literary society',
   'self-education','self-taught','botanist','naturalist'],'A','A'),
 # politics -> B (représentation)
 (['labour party','independent labour','ilp','socialist','social democratic','chartist','fabian',
   'trade union','miners federation','co-operative','co-op','guild','radical','liberal','political',
   'councillor','alderman','parliamentary','candidate'],'B','B'),
 # media -> D
 (['journal','newspaper','periodical','magazine','edited','editor','press','published in','contributor to'],'D','A'),
]
def norm(s):
    s=(s or '').lower(); s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r'[^a-z\'\- ]',' ',s)
    return ' '+re.sub(r'\s+',' ',s).strip()+' '
def head_concept(raw):
    t=norm(raw); best=None; pos=10**9
    for con,vs in VAR.items():
        for v in vs:
            m=re.search(r'[ \-]'+re.escape(v)+r'(s|es|ing)?[ \-]',t)
            if m and m.start()<pos: pos=m.start(); best=con
    return best
def avoc_touches(text):
    t=norm(text); out=set()
    for kws,st,sq in AVOC:
        for kw in kws:
            if (' '+kw+' ') in t: out.add((st,sq))
    return out

A={r['entry_id']:r for r in csv.DictReader(open('out/actors.csv',encoding='utf-8-sig'))}
S=list(csv.DictReader(open('out/stages_long_final.csv',encoding='utf-8-sig')))

occ_tagged=0
for s in S:
    con=head_concept(s['occupation_raw'])
    if con and con in SS:
        st,sq,rev=SS[con]
        s['structure']=st; s['sequence']=sq; s['struct_concept']=con
        s['struct_review']='yes' if rev else ''
        occ_tagged+=1
    else:
        s['structure']=s['sequence']=s['struct_concept']=''; s['struct_review']=''
cols=list(S[0].keys())
with open('out/stages_long_final.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(S)

# ---- per actor ----
byact=defaultdict(list)
for s in S: byact[s['entry_id']].append(s)
prof=[]
for eid in sorted(byact,key=lambda x:int(x)):
    sts=sorted(byact[eid],key=lambda x:int(x['stage_index']))
    occ=[(s['structure'],s['sequence']) for s in sts if s['structure']]
    meta=A.get(eid,{})
    avoc=avoc_touches((meta.get('affiliations_raw','') or '')+' '+(meta.get('content_tone','') or ''))
    touched_struct=set(x[0] for x in occ) | set(x[0] for x in avoc)
    touched_ss=set(occ) | avoc
    # crossings on occupational order
    trans=sum(1 for i in range(len(occ)-1) if occ[i][0]!=occ[i+1][0])
    horiz=sum(1 for i in range(len(occ)-1) if occ[i][0]==occ[i+1][0] and occ[i][1]!=occ[i+1][1])
    path='-'.join([occ[0][0]+'.'+occ[0][1]]+[occ[i][0]+'.'+occ[i][1] for i in range(1,len(occ)) if occ[i]!=occ[i-1]]) if occ else ''
    prof.append({'entry_id':eid,'surname':meta.get('surname',''),'destinations':meta.get('destinations',''),
        'ss_path':path,'n_struct_occ':len(set(x[0] for x in occ)),'n_struct_total':len(touched_struct),
        'n_seq_total':len(touched_ss),'transversal_cross':trans,'horizontal_cross':horiz,
        'avoc_touches':' '.join(sorted(a[0]+'.'+a[1] for a in avoc)),'n_occ_stages':len(occ)})

with open('out/structure_profiles.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(prof[0].keys())); w.writeheader(); w.writerows(prof)

# ---- report ----
print(f"étapes occupationnelles taguées (struct+seq) : {occ_tagged}/{len(S)} ({100*occ_tagged/len(S):.0f}%)")
byst=Counter(s['structure'] for s in S if s['structure'])
DOM=dict(A='Kultur',B='Politik',C='Wirtschaft',D='Medien')
print("structures (étapes occ.) :", ' | '.join(f"{k}/{DOM[k]} {byst.get(k,0)}" for k in 'ABCD'))
# QA avec couche avocationnelle
ok=tot=0
for p in prof:
    d=p['destinations']; 
    if not d: continue
    need={'Art':{'A'},'Media':{'D'},'Art+Media':{'A','D'}}.get(d)
    if not need: continue
    touched=set(x.split('.')[0] for x in (p['ss_path'].split('-')+p['avoc_touches'].split()) if x)
    tot+=1
    if need<=touched: ok+=1
print(f"\nQA destination atteinte (occ+avoc) : {ok}/{tot} ({100*ok/tot:.0f}%)  [était 46% en occ. seul]")
acts=[p for p in prof if p['n_occ_stages']>=2]
print(f"\nacteurs avec ≥2 étapes occ. : {len(acts)}")
print(f"  franchissements TRANSVERSAUX (structure) : méd {statistics.median([p['transversal_cross'] for p in acts]):.0f} | moy {statistics.mean([p['transversal_cross'] for p in acts]):.1f} | max {max(p['transversal_cross'] for p in acts)}")
print(f"  franchissements HORIZONTAUX (séquence)   : méd {statistics.median([p['horizontal_cross'] for p in acts]):.0f} | moy {statistics.mean([p['horizontal_cross'] for p in acts]):.1f} | max {max(p['horizontal_cross'] for p in acts)}")
ts=[p['n_struct_total'] for p in prof if p['n_struct_total']]
print(f"  structures distinctes touchées (occ+avoc): moy {statistics.mean(ts):.1f} ; ≥2 : {sum(1 for x in ts if x>=2)}/{len(ts)} ({100*sum(1 for x in ts if x>=2)/len(ts):.0f}%) ; ≥3 : {sum(1 for x in ts if x>=3)} ({100*sum(1 for x in ts if x>=3)/len(ts):.0f}%)")
print("\n--- chemins (structure.séquence) les plus fréquents ---")
for path,c in Counter(p['ss_path'] for p in acts if p['ss_path']).most_common(12):
    print(f"  {c:>3}×  {path}")
