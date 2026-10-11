import re, csv
# re-use the user's lexicon from 04_code_structure_seq.py without running it
from pfade import LEXIKON_SKRIPT
src=open(LEXIKON_SKRIPT,encoding='utf-8').read()
ns={}; exec(src.split("A={r['entry_id']")[0], ns)
SS,VAR,head_concept,avoc_touches=ns['SS'],ns['VAR'],ns['head_concept'],ns['avoc_touches']
def lex(raw):
    c=head_concept(raw)
    if c and c in SS: return SS[c][0],SS[c][1],c
    return '','',c or ''
