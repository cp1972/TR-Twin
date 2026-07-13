#!/usr/bin/env python3
"""
Pedagogical example: "Auktion" art-market control.

Builds two CSVs that a student loads into the TR digital twin to run FICTITIOUS,
heuristic scenarios about how auction houses (control instances spanning
A-Culture and D-Media) regulate the circulation of artists in A.

  1) auktion_artists_cohort.csv   -> load as "cohort / contract table"
        columns: aid,annee,structure,categorie,sequence
        A STIPULATED population of artists, built as four ideal-types. It is a
        probe, not a census; it carries the demography only (no governing force).

  2) auktion_control_parc.csv     -> load as "instance parc"
        columns: aid,annee,structure,categorie,sequence,poids
        The EMPIRICAL layer that a 5-7 interview study can actually profile:
        the "way of working" of the auction houses, written as control instances
        (categorie=controle) with a force curve (poids) over time, plus a couple
        of mediation instances (galleries / critics) that carry the crossing.

The numbers are illustrative type-ideals, NOT measurements. Their role is to let
students state a mechanistic hypothesis ("if the Auktion works like THIS, then for
THIS population the circulation reconfigures like THAT") and test its sensitivity.
"""
import csv, os

OUT = "examples/auktion-art-market/data"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1) ARTIST POPULATION  (four ideal-types; concentrated in A, a thin crossing to D)
#    categories: etabli (established) / conservateur (canonised) / aspirant /
#                decu (disappointed).  sequence = sub-stake within the structure.
# ---------------------------------------------------------------------------
# each artist: (aid, [(year, structure, categorie, sequence), ...])
artists = []

# T1 — contemporary renowned, living blue-chip: solidly A-etabli; two of them
#      also reach D (media visibility) from the late 2000s.
for i in range(1, 5):
    rows = [(1988, "A", "aspirant", "A"), (1998, "A", "etabli", "A"), (2015, "A", "etabli", "A"), (2025, "A", "conservateur", "A")]
    if i <= 2:
        rows += [(2010, "D", "etabli", "A"), (2025, "D", "etabli", "A")]
    artists.append((f"t1_renowned_{i}", rows))

# T2 — deceased former-established (historical blue-chip): A-etabli/conservateur,
#      active mid-century, then closure (death) ~1985.
for i in range(1, 4):
    artists.append((f"t2_classic_{i}", [(1948, "A", "etabli", "A"), (1965, "A", "conservateur", "A"), (1984, "A", "conservateur", "A")]))

# T3 — deceased risen in prestige (rediscovered): aspirant -> dip -> posthumous
#      canonisation (stylised as etabli/conservateur into the present); one crosses to D.
for i in range(1, 5):
    rows = [(1958, "A", "aspirant", "A"), (1974, "A", "decu", "B"), (2002, "A", "etabli", "A"), (2022, "A", "conservateur", "A")]
    if i == 1:
        rows += [(2012, "D", "etabli", "A")]
    artists.append((f"t3_rediscovered_{i}", rows))

# T4 — aspiring regional (the REGULATED): A-aspirant (some decu), recent, mostly
#      no crossing — their circulation is exactly what the Auktion gates.
t4 = [("A", "aspirant", "A"), ("A", "aspirant", "B"), ("A", "decu", "A"),
      ("A", "aspirant", "A"), ("A", "decu", "B"), ("A", "aspirant", "C"), ("A", "aspirant", "A")]
for i, (st, cat, sq) in enumerate(t4, 1):
    artists.append((f"t4_regional_{i}", [(2001, st, "aspirant", sq), (2013, st, cat, sq), (2025, st, cat, sq)]))

with open(f"{OUT}/auktion_artists_cohort.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["aid", "annee", "structure", "categorie", "sequence"])
    for aid, rows in artists:
        for (yr, st, cat, sq) in sorted(rows):
            w.writerow([aid, yr, st, cat, sq])

# ---------------------------------------------------------------------------
# 2) AUKTION CONTROL PARC  (the empirically-profilable "way of working")
# ---------------------------------------------------------------------------
# IMPORTANT — what the "categorie" column means in an INSTANCE file (not a cohort):
#   It is NOT "the actor category the instance socialises preferentially" — the model
#   never reads it that way. For an instance it has only two roles:
#     (a) TYPE FLAG (load-bearing): a value containing "controle"/"control"/"kontrolle"
#         marks a CONTROL instance (joins the control parc, feeds control capacity);
#         any other value marks a MEDIATION instance. So "controle" is REQUIRED on
#         control rows, but it is a routing keyword, not an actor category.
#     (b) DISPLAY LABEL only: on mediation rows the value just tints the probe dot.
#   An instance is actually targeted by  structure x sequence x poids  (see docs/07).
#   The mediation labels below (etabli / conservateur) are mnemonic tints, nothing more.
#
# each instance: (aid, structure, categorie, sequence, [(year, poids), ...])
instances = [
    # --- CONTROL: the auction houses ---
    # Leipzig (East): a regional house, moderate and slowly consolidating.
    ("auktion_leipzig",     "A", "controle", "A", [(1985, 0.20), (2005, 0.34), (2025, 0.52)]),
    # Rhineland / Dortmund (West): stronger, more selective gatekeeping in A.
    ("auktion_rheinland",   "A", "controle", "A", [(1985, 0.26), (2005, 0.52), (2025, 0.76)]),
    # A media-side control house: gates the crossing into D (visibility / blue-chip).
    ("auktion_media_house", "D", "controle", "A", [(1992, 0.18), (2008, 0.40), (2025, 0.62)]),
    # --- MEDIATION: the carriers of the crossing ---
    # Galleries that represent and circulate artists inside A.
    ("galleries",           "A", "etabli",      "A", [(1985, 0.30), (2005, 0.46), (2025, 0.60)]),
    # Critics / press channelling toward media prestige (target sequence D).
    ("critics_press",       "A", "conservateur", "D", [(1990, 0.20), (2008, 0.38), (2025, 0.52)]),
]

with open(f"{OUT}/auktion_control_parc.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["aid", "annee", "structure", "categorie", "sequence", "poids"])
    for aid, st, cat, sq, curve in instances:
        for (yr, pw) in curve:
            w.writerow([aid, yr, st, cat, sq, pw])

n_art = len(artists)
n_ctrl = sum(1 for x in instances if x[2] == "controle")
n_med = len(instances) - n_ctrl
print(f"\u2713 Auktion example written to {OUT}/")
print(f"  artists_cohort: {n_art} artists")
print(f"  control_parc: {n_ctrl} control instances + {n_med} mediation instances")
