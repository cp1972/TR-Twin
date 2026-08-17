# Coding — how 390 autobiographies became data

This folder documents and reproduces the step from a corpus of texts to the
tables the twin reads. Nothing here is needed to *run* the twin; it is here so
that the empirical claims can be checked, criticised and repeated.

Four folders, four questions:

| Folder | Answers |
|---|---|
| `scripts/` | **How** was it done? The eleven steps, in order. |
| `lookup/` | **With what** was it coded? Crosswalk, lexicon, reference rates. |
| `results/` | **What** came out? The coded corpus and the validation sheet. |
| `reports/` | **Why** that way? Five reports on the decisions and their limits. |

## Start here

If you only want to read: go to `reports/`. The five reports are in reading
order and stand on their own.

If you want to recompute: the corpus itself (the 390 biography text files from
the Burnett–Vincent–Mayall bibliography) is **not** in this repository for
rights reasons. Steps 1–3 therefore cannot be re-run without it. Everything
from step 4 on works from `results/stages_long_final.csv`, which is included.

## The pipeline (`scripts/`)

Requirements: Python 3, standard library only. Each step reads and writes in an
`out/` working directory; adjust the paths at the top of a script if your
layout differs.

| Step | Script | In → out |
|---|---|---|
| 1 | `01_parse_bios.py` | 390 text files → `actors.csv`, `stages_long.csv` (163 persons, 996 stages) |
| 2 | `02_code_occupations.py` | occupations → HISCO / HISCLASS / HISCAM; writes `hisco_crosswalk.csv`, `occupation_lexicon.csv` |
| 3 | `03_finalize_coding.py` | cleaning rules, precision first |
| 4 | `04_code_structure_seq.py` | stages → structure + sequence (and the avocational layer) |
| 5 | `05_densify_tr.py` | TR actor categories, absolute and relative → `tr_absolute`, `tr_relative` |
| 6 | `06_circulation_profiles.py` | vertical profile per actor |
| 7 | `07_circulation_index.py` | the composite three-axis index → `circulation_index.csv` |
| 8 | `08_tr_measures.py` | empirical state (S, g, act) and the inequality cascade → `tr_measures.json` |
| 9 | `09_make_contract.py` | the twin's native contract table → `cohorte_contrat.csv`, and `flow.json` |
| 10 | `10_father_coding.py` | fathers' occupations → HISCLASS / HISCAM; origin vs destination |
| 11 | `11_compare_AB.py` | comparisons A (destination) and B (intensity at matched resolution) against the reference table |

`rebuild_flow.py` is not a pipeline step but a recovery tool: it rebuilds
`flow.json` from `results/stages_long_final.csv` using the same lexicon as step
4, and verifies the result against `tr_measures.json` before writing. Use it if
`flow.json` is lost or if you want to check that the coding still reproduces
the published measures.

Two steps load their neighbours by filename: `11_compare_AB.py` reads
`10_father_coding.py` and `04_code_structure_seq.py`. Renaming a script means
adjusting those two lines.

## What is *not* here any more

`figures.py` used to be step 10 and produced the chapter figures with
matplotlib. It has been replaced by `../scripts/figures/chapter_figures.py`,
which draws the same figures as SVG in the visual language used throughout the
project. The old script remains in the Git history.

## Lookup tables (`lookup/`)

- `hisco_crosswalk.csv` — HISCO → HISCLASS/HISCAM, after CEDAR
  (<https://github.com/cedarfoundation/hisco>)
- `occupation_lexicon.csv` — the occupational descriptions found in the corpus
  and their coding
- `referenztabelle_mobilitaet.csv` — published outflow and persistence rates
  for the English working class 1839–1914, each cell with its source

## Results (`results/`)

- `stages_long_final.csv` — the coded corpus: 996 stages with structure,
  sequence and TR category
- `circulation_index.csv` — the composite index per actor
- `Validation_structure_sequence.xlsx` — the manual validation of the
  structure/sequence coding

## Reports (`reports/`)

1. `01-Kodierbericht_HISCO.org` — how occupations were coded, and the residue
2. `02-Protokoll_Referenzvergleich.org` — the comparison protocol, fixed in advance
3. `03-Bericht_Referenztabelle.org` — the reference table and its sources
4. `04-Bericht_Zirkulationsanalyse.org` — the circulation analysis
5. `05-Bericht_Atypizitaet.org` — atypicality: comparisons A and B

`references.bib` holds the bibliography cited in report 3.
