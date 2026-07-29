# -*- coding: utf-8 -*-
import csv, gzip, re
from collections import Counter, defaultdict

rows=list(csv.DictReader(gzip.open('hisco_repo/data-raw/hisco-ses.csv.gz',mode='rt',encoding='utf-8')))
base=[r for r in rows if not r['STATUS'] and not r['RELATION'] and not r['PRODUCT'] and r['HISCAM_U1']]
REF={r['HISCO']:{'hisco':r['HISCO'],'en':r['EN_HISCO_TEXT'].strip(),'hisclass':r['HISCLASS'],
                 'hisclass_5':r['HISCLASS_5'],'socpo':r['SOCPO'],'hiscam':r['HISCAM_U1']} for r in base}
BAD=('unknown','other','specialisation','elsewhere','related')
def find_code(*kws):
    cs=[e for e in REF.values() if all(re.search(r'\b'+k,e['en'].lower()) for k in kws)]
    if not cs: return None
    cs.sort(key=lambda e:(sum(b in e['en'].lower() for b in BAD), len(e['en'])))
    return cs[0]

# geprüfte Festcodes für häufige, eindeutige Begriffe (aus Stichproben im Crosswalk)
OVERRIDE={'teacher':'13000','journalist':'15915','editor':'15920','author':'15120',
 'printer':'92110','compositor':'92120','minister_religion':'14120','missionary':'14130',
 'messenger':'37040','legislator':'20110','musician':'17100','actor':'17320',
 'painter_artist':'16130','carpenter':'95410','joiner':'95420','blacksmith':'83110',
 'tailor':'79100','fitter':'84100','seaman':'98140','labourer':'99910'}

CONCEPTS={
 'minister_religion':(['minister','clergyman','clergy','pastor','preacher','parson','curate','vicar','priest','rector'],None,False),
 'missionary':(['missionary','missioner'],None,False),
 'teacher':(['teacher','schoolteacher','schoolmaster','tutor','governess','pupil-teacher'],None,False),
 'lecturer':(['lecturer','professor'],['teacher','level'],True),
 'journalist':(['journalist','correspondent','reporter','contributor','contributed','contributing'],None,False),
 'editor':(['editor','sub-editor','subeditor'],None,False),
 'author':(['author','writer','novelist','poet','essayist'],None,False),
 'printer':(['printer','printing'],None,False),
 'compositor':(['compositor','typesetter','type-setter'],None,False),
 'publisher':(['publisher'],['publish'],True),
 'bookseller':(['bookseller'],['booksell'],True),
 'weaver':(['weaver','weaving'],['weaver'],False),
 'spinner':(['spinner','spinning'],['spinner'],False),
 'shoemaker':(['shoemaker','cobbler','bootmaker','shoemaking','bootmaking'],['shoemaker'],False),
 'tailor':(['tailor','draper'],None,False),
 'carpenter':(['carpenter'],None,False),
 'joiner':(['joiner'],None,False),
 'blacksmith':(['blacksmith','smith','whitesmith'],None,False),
 'mason':(['mason','stonemason','bricklayer'],['bricklayer'],False),
 'fitter':(['fitter','turner','mechanic','machinist'],None,False),
 'engineer':(['engineer','engineering'],['fitter','machine'],True),
 'miner':(['miner','collier','pitman','mine','mines','pit','colliery'],['coal','miner'],False),
 'labourer':(['labourer','navvy'],None,False),
 'farm_labourer':(['ploughboy','farm-boy','farmboy','agricultural','herdboy','herd','cowherd','shepherd','drover','ploughman'],['agricultural','labourer'],False),
 'farmer':(['farmer','husbandman','crofter'],['farmer'],True),
 'messenger':(['messenger','errand-boy','errandboy','office-boy','officeboy','van-boy','reading-boy','shop-boy','lobby-boy'],None,False),
 'news_vendor':(['newspaper boy','newsboy','news-boy','newsvendor','vendor'],['news','vendor'],False),
 'clerk':(['clerk'],['clerk','general'],True),
 'shopkeeper':(['shopkeeper','grocer','draper','dealer'],['proprietor','retail'],True),
 'salesman':(['salesman','traveller','commercial'],['salesman'],True),
 'manager':(['manager'],['manager','general'],True),
 'agent':(['agent'],['canvasser'],True),
 'proprietor':(['proprietor','proprietress'],['proprietor'],True),
 'seaman':(['sailor','seaman','mariner','sea'],None,False),
 'assistant':(['assistant'],None,True),
 'soldier':(['soldier','enlisted','army','regiment'],['armed'],True),
 'musician':(['musician','composer','singer'],None,False),
 'actor':(['actor','comedian'],None,False),
 'painter_artist':(['artist','painter'],None,False),
 'legislator':(['mp','parliament','legislator','councillor','alderman','mayor'],None,False),
 'union_official':(['union','organiser','organizer','agitator','propagandist'],['labour'],True),
 'secretary':(['secretary'],['secretary'],True),
 'servant':(['servant','footman','valet','maid'],['servant','domestic'],False),
 'gardener':(['gardener'],['gardener'],False),
 'baker':(['baker'],['baker'],False),
 'butcher':(['butcher'],['butcher'],False),
 'warehouseman':(['warehouseman','warehouse'],['warehouse'],True),
 'porter':(['porter'],['porter'],True),
 'policeman':(['policeman','constable','police'],['police'],False),
 'soldier':(['soldier','enlisted','army','regiment','sergeant'],['armed'],True),
}
CODE={}
for c,(vars_,kws,amb) in CONCEPTS.items():
    e = REF.get(OVERRIDE[c]) if c in OVERRIDE else (find_code(*kws) if kws else None)
    CODE[c]=(e,amb)
# gezielte Korrekturen fehlgehender automatischer Zuordnungen
CODE['lecturer']=(REF.get('13000'),True)                                   # als Lehrkraft (generisch) behandeln, markieren
_uo=find_code('labour','organ') or find_code('official','labour') or find_code('trade','union')
CODE['union_official']=(_uo,True)
_fl=find_code('agricultural','labourer') or find_code('field','crop') or find_code('agricultural')
CODE['farm_labourer']=(_fl,False)
_sol=find_code('armed','forces') or find_code('soldier')
CODE['soldier']=(_sol,True)
# Sammelkorrektur häufiger mehrdeutiger Begriffe (vertretbare Näherungen, zur Prüfung markiert)
CODE['salesman']=(REF.get('43220'),False)          # Commercial Traveller 73.55
CODE['manager']=(REF.get('21110'),True)            # General Manager 84.88
CODE['agent']=(REF.get('45230'),True)              # Canvasser 51.9 (insurance/society agents)
CODE['clerk']=(REF.get('39310'),True)              # Office Clerk, General 69.59
CODE['secretary']=(REF.get('21110'),True)          # überwiegend Gewerkschafts- und Verbandssekretäre, als Leitung genähert
CODE['union_official']=(REF.get('21110'),True)
CODE['shopkeeper']=(REF.get('41020'),True)         # Working Proprietor 81.33
CODE['publisher']=(REF.get('41020'),True)
CODE['bookseller']=(REF.get('41020'),True)
CODE['news_vendor']=(REF.get('45240'),False)       # News Vendor 56.72
CODE['warehouseman']=(REF.get('97145') or find_code('warehouse'),True)
CODE['proprietor']=(REF.get('41020'),True)
TERM2CON={v:c for c,(vars_,kws,amb) in CONCEPTS.items() for v in vars_}

FILLER=set(('a an the and or of to in for with at on by his her their as from into out also '
 'employed worked work working started start became become appointed entered enter went being '
 'joined join engaged engage returned return spent spend held hold set sets setting served job '
 'serve serving took take taken made make making trained train apprenticed rising rose risen was '
 'elected promoted eventually subsequently later then briefly various first second third left '
 'early late fulltime parttime full part time age aged years year own new old chief senior school '
 'junior active regular leading principal up down off about over many several including this that '
 'these those who which whom when while during after before until native local small large great '
 'good well long short high low career life').split())
NOISE=set(('was job left chairman half-timer enlisted apprentice apprenticed journeyman various '
 'unspecified misc - vide').split())
def norm_stage(s):
    s=s.lower(); s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r'\b1[6-9]\d{2}\b',' ',s)
    s=re.sub(r"[^a-z'\- ]",' ',s)
    toks=[t for t in s.split() if t]
    while toks and toks[0] in FILLER: toks=toks[1:]
    cut=[]
    for t in toks:
        if t in ('in','at','for','of','to','on','with','and','from'): break
        if t in FILLER: continue
        cut.append(t)
        if len(cut)>=3: break
    return ' '.join(cut).strip()

def resolve(term):
    cands=[term, term.replace('-',''), term.replace('-',' ')] + re.split(r'[ \-]', term)
    for t in cands:
        c = TERM2CON.get(t) or (TERM2CON.get(t[:-1]) if t.endswith('s') else None)
        if c:
            e,amb=CODE[c]
            if e: return c,e,'synonym',amb
            if amb: return c,None,'ambiguous',True   # zugeordnet, aber bewusst nicht codiert, zur Prüfung
    simp=re.sub(r'[^a-z ]','',term)
    for e in REF.values():
        if simp and re.sub(r'[^a-z ]','',e['en'].lower())==simp: return term,e,'exact',False
    BLACK=set('local small large general various regular active leading chief senior junior own works business member full'.split())
    for t in term.split():
        if t in BLACK or len(t)<4: continue
        e=find_code(t)
        if e: return term,e,'keyword',True
    return term,None,'none',True

def full_scan(s):
    s=s.lower(); s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r'\b1[6-9]\d{2}\b',' ',s)
    s=re.sub(r"[^a-z'\- ]",' ',s)
    for t in re.split(r'[ \-]+', s):
        c = TERM2CON.get(t) or (TERM2CON.get(t[:-1]) if t.endswith('s') else None)
        if c and CODE[c][0]:
            return c, CODE[c][0], 'rescue', True
    return None,None,None,None

stages=list(csv.DictReader(open('out/stages_long.csv',encoding='utf-8-sig')))
# group by CONCEPT (if matched) else cleaned term
grp=defaultdict(lambda:{'freq':0,'actors':set(),'examples':Counter(),'ref':None,'method':'','review':False,'kind':'concept'})
for st in stages:
    term=norm_stage(st['occupation_raw'])
    if not term or term in NOISE: 
        key='(non classé)'; con,e,method,review=key,None,'none',True; kind='noise'
    else:
        con,e,method,review=resolve(term)
        key=con; kind='concept' if method=='synonym' else 'term'
    if not e:
        rc,re_,rm,rv=full_scan(st['occupation_raw'])
        if re_: con,e,method,review,key,kind=rc,re_,rm,rv,rc,'concept'
    if method=='rescue':
        grev = True
    elif method=='synonym':
        grev = CODE[con][1] if con in CODE else (not bool(e))
    elif method=='exact':
        grev = False
    else:
        grev = True
    st['code_method']=method if e else ''
    st['code_review']='yes' if (grev or not e) else ''
    G=grp[key]; G['freq']+=1; G['actors'].add(st['entry_id'])
    G['examples'][st['occupation_raw'][:45]]+=1
    G['ref'],G['method'],G['review'],G['kind']=e,method,grev,kind
    st['hisco_code']=e['hisco'] if e else ''
    st['hisclass']=e['hisclass'] if e else ''
    st['hiscam']=e['hiscam'] if e else ''

# write coded stages
with open('out/stages_long_coded.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=stages[0].keys()); w.writeheader(); w.writerows(stages)

# write compact lexicon (grouped)
lexrows=[]
for key,G in sorted(grp.items(), key=lambda kv:-kv[1]['freq']):
    e=G['ref']
    lexrows.append({'concept_or_term':key,'kind':G['kind'],'freq':G['freq'],'n_actors':len(G['actors']),
        'top_example':G['examples'].most_common(1)[0][0] if G['examples'] else '',
        'hisco':e['hisco'] if e else '','en_hisco':e['en'] if e else '',
        'hisclass':e['hisclass'] if e else '','hisclass_5':e['hisclass_5'] if e else '',
        'hiscam':e['hiscam'] if e else '','match':G['method'],
        'needs_review':'yes' if (G['review'] or not e) else ''})
with open('out/occupation_lexicon.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=['concept_or_term','kind','freq','n_actors','top_example',
        'hisco','en_hisco','hisclass','hisclass_5','hiscam','match','needs_review'])
    w.writeheader(); w.writerows(lexrows)

N=len(stages)
coded=sum(1 for st in stages if st['hisco_code'])
strong=sum(G['freq'] for G in grp.values() if G['ref'] and not G['review'])
print(f"étapes                  : {N}")
print(f"lignes de lexique       : {len(lexrows)}  (regroupées par concept/terme)")
print(f"étapes avec un code     : {coded} ({100*coded/N:.0f}%)")
print(f"  dont confiance forte  : {strong} ({100*strong/N:.0f}%)")
print(f"lignes à revoir         : {sum(1 for r in lexrows if r['needs_review']=='yes')} / {len(lexrows)}")
print(f"étapes encore sans code : {N-coded} ({100*(N-coded)/N:.0f}%)")
print("\n--- lexique, top 30 (✓=confiance forte, ⚠=à revoir) ---")
for r in lexrows[:30]:
    fl='✓' if r['needs_review']!='yes' and r['hisco'] else ('·' if r['hisco'] else '⚠')
    print(f" {fl} {r['freq']:>3}× {r['concept_or_term'][:20]:<20} {r['hisco']:>6} «{r['en_hisco'][:28]:<28}» CAM{r['hiscam']:<6} HC{r['hisclass']:<2} [{r['match']}]")
