import sys, csv, re, os
from pfade import *
M=mta_core()
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
DIR=os.environ.get('NOTIZEN_DIR','')  # nur für Analysen ganzer Notizen; für Kapitel 12 nicht nötig
# generic stopwords + notice boilerplate (not substantive)
EXTRA="""born died aged age year years pp index portrait ltd london co press published publ also see
account life autobiography autobiographical memoir memoirs reminiscences book volume vol edition
ed introduction foreword preface written writes wrote describes description includes including
little great good long early later many much well one two three four first second times
went became become began left took worked working work job jobs time mr mrs sir
chapter chapters section sections pages page detail details details number""".split()
STOP=sorted(set(ENGLISH_STOP_WORDS)|set(EXTRA))
def read(p):
    raw=open(p,'rb').read()
    try: return raw.decode('utf-8-sig')
    except: return raw.decode('latin-1')
def paras(t): return [p.strip() for p in re.split(r'\n\s*\n',t) if p.strip()]
def load_notices():
    out=[]
    for f in sorted(os.listdir(DIR)):
        if not f.endswith('.txt'): continue
        eid=re.match(r'(\d+)',f).group(1)
        out.append((eid,f,read(os.path.join(DIR,f))))
    return out
ACT={r['entry_id']:r for r in csv.DictReader(open(os.path.join(DATEN,'actors.csv'),encoding='utf-8-sig'))}
STG=list(csv.DictReader(open(os.path.join(DATEN,'stages_long_final.csv'),encoding='utf-8-sig')))

def strip_proper(t):
    # drop capitalised tokens that are not sentence-initial (place/person/organisation names)
    toks=re.findall(r"\S+",t); out=[]; start=True
    for w in toks:
        core=re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$","",w)
        if core and core[0].isupper() and not start and not core.isupper():
            pass
        else: out.append(w)
        start = bool(re.search(r"[.;:!?]$",w))
    return ' '.join(out)
def activity_text(eid, proper=False):
    a=ACT[eid]; t=a['career_raw']+' '+a['affiliations_raw']
    return t if proper else strip_proper(t)
