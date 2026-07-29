#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schritt 1 der Instanzenseite: die Vermittlungsinstanzen einsammeln, die jeder Akteur
berührt hat, aus den Rohtexten der Biographien.
"""
import csv, re, collections

# ---- Einordnung nach der TR (vorläufig) ------------------------------------
NEWSPAPER = ("Times","News","Mail","Guardian","Citizen","Express","Herald","Star","Gazette",
             "Chronicle","Mercury","Advertiser","Observer","Mirror","Telegraph","Courier",
             "Standard","Operative","Syndicalist","Reporter","Echo","Post","Dispatch","Clarion",
             "Reasoner","Vindicator","Commonwealth","Reynolds","Reuters","Newspaper")
LITERARY  = ("Review","Magazine","Journal","Cornhill","Athenaeum","Anthology","Quarterly")
PUBLISH   = ("Press","Publishing","Printing","Printer","Library","Bookshop","Books")
CULTURE_S = ("Mechanics","Institute","Institution","Lyceum","Athenaeum","College","School",
             "Reading","Improvement","Secular","Academy","University","Museum","Sunday")
POLITICAL = ("Party","Union","League","Federation","Association","Charter","International",
             "Commission","Council","Committee","Brotherhood","Fund","Movement","Chartist",
             "Labour","Socialist","Co-operative","Cooperative","Guild","ILP","SDF")
COMPANY   = ("Company","Works","Mills","Factory","Firm","Manufactory","Brothers")

def classify(name):
    toks = re.findall(r"[A-Za-z'’\-]+", name)
    last = toks[-1] if toks else ""
    has = lambda S: any(t in S for t in toks)
    if has(NEWSPAPER) or last in NEWSPAPER:                 return ("press·newspaper","D","sequence/fragment")
    if has(LITERARY):                                        return ("press·review","A","sequence")
    if has(PUBLISH):                                         return ("publishing/print","A","fragment (gatekeeping)")
    if has(POLITICAL):                                       return ("political body","B","sequence")
    if has(CULTURE_S):                                       return ("cultural formation","A","relation/sequence")
    if has(COMPANY):                                         return ("firm","C","fragment")
    return ("other","?","?")

ALL_KW = NEWSPAPER+LITERARY+PUBLISH+CULTURE_S+POLITICAL+COMPANY

# ---- Namens- und Signalmuster ----------------------------------------------
TOK  = r"[A-Z][A-Za-z0-9'’.\-&]+"
CONN = r"(?:of|the|and|for|&|in|on|de|du|to)"
NAME = r"(?:the\s+|of\s+)?(" + TOK + r"(?:\s+(?:" + CONN + r"\s+)?" + TOK + r"){0,5})"
CUE  = (r"(?:editor and proprietor of|proprietor and editor of|joint editor of|sub-editor of|"
        r"editor of|proprietor of|correspondent for|correspondent of|reporter on|reporter for|"
        r"contributor to|writer for|wrote for|manager of|founder-member of|founder of|co-founder of|"
        r"president of|vice-president of|secretary of|treasurer of|chairman of|member of|"
        r"joined|edited|established|founded|started)")
CUE_RE  = re.compile(CUE + r"\s+" + NAME)
SUF_RE  = re.compile(r"\b(" + TOK + r"(?:\s+(?:" + CONN + r"\s+)?" + TOK + r"){0,5})\b")
YEAR_RE = re.compile(r"\(?\b(1[789]\d{2})\b")

STOP = {"He","She","Started","Worked","Went","Published","Author","Poet","Interested","Active",
        "Supported","Inherited","Joined","Member","Signed","Perhaps","See","God","English","British",
        "South","African","War","World","Royal"}  # crude false-positive guard for bare starts

def clean(name):
    name = name.strip().strip(".,;:")
    name = re.sub(r"^(the|of|a)\s+","",name, flags=re.I)
    return name.strip()

def has_kw(name):
    return any(t in ALL_KW for t in re.findall(r"[A-Za-z'’\-]+", name))

def nearby_year(text, end):
    m = YEAR_RE.search(text, end, min(end+14, len(text)))
    return m.group(1) if m else ""

def extract(text):
    found = {}   # norm_name -> (display, cue, year)
    # (a) über Signalwörter
    for m in CUE_RE.finditer(text):
        nm = clean(m.group(1))
        if len(nm) < 3 or nm.split()[0] in STOP: continue
        yr = nearby_year(text, m.end())
        found.setdefault(nm.lower(), (nm, m.group(0).split()[0]+"…", yr))
    # (b) über die Endung (Namen, die ein Institutionswort enthalten)
    for m in SUF_RE.finditer(text):
        nm = clean(m.group(1))
        if has_kw(nm) and len(nm.split()) >= 2 and nm.split()[0] not in STOP:
            yr = nearby_year(text, m.end())
            found.setdefault(nm.lower(), (nm, "suffix", yr))
    return list(found.values())

def main():
    rows = []
    perType = collections.Counter()
    recur = collections.Counter()
    with open("out/actors.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            eid, sur = r["entry_id"], r["surname"]
            for field in ("career_raw","affiliations_raw"):
                txt = r.get(field) or ""
                for (nm, cue, yr) in extract(txt):
                    typ, struct, lvl = classify(nm)
                    rows.append({"entry_id":eid,"surname":sur,"instance":nm,"type":typ,
                                 "struct_guess":struct,"level_guess":lvl,"year":yr,
                                 "cue":cue,"field":field})
                    perType[typ]+=1
                    recur[nm]+=1
    with open("instances_extracted.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["entry_id","surname","instance","type","struct_guess","level_guess","year","cue","field"])
        w.writeheader(); w.writerows(rows)
    # Zusammenfassung
    print("TOTAL mentions extracted:", len(rows),
          "across", len({r['entry_id'] for r in rows}), "actors\n")
    print("=== by type (provisional TR structure) ===")
    for typ,n in perType.most_common():
        st={'press·newspaper':'D','press·review':'A','publishing/print':'A','political body':'B',
            'cultural formation':'A','firm':'C','other':'?'}[typ]
        print(f"  {n:4}  {typ:20} → {st}")
    print("\n=== most recurrent instances (≥3 actors) ===")
    for nm,n in recur.most_common(30):
        if n>=3: print(f"  {n:3}×  {nm}")

if __name__=="__main__":
    main()
