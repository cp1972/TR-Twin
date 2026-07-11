# README — Reproduzierbares Pipeline (empirischer Teil der Theorie der Relation)

Voraussetzungen: Python 3, `matplotlib` (für die Figuren). Keine weiteren Pflichtpakete.
Eingangsdaten: die 390 Autobiographie-Textdateien (Korpus Burnett-Vincent-Mayall) sowie der HISCO-Crosswalk
(CEDAR, https://github.com/cedarfoundation/hisco). Zwischen- und Enddateien liegen im Ordner `out/`.

Ausführungsreihenfolge (jedes Skript schreibt nach `out/`):

1.  `parse_bios.py`            Textdateien -> `actors.csv`, `stages_long.csv` (163 Personen, 996 Etappen).
2.  `code_occupations.py`      Berufe -> HISCO/HISCLASS/HISCAM; erzeugt `hisco_crosswalk.csv`,
                               `occupation_lexicon.csv`, `stages_long_coded.csv`.
3.  `finalize_coding.py`       Bereinigungsregeln (Präzision zuerst) -> bereinigte Kodierung.
4.  `code_structure_seq.py`    Etappen -> Struktur/Sequenz (+ avokationale Schicht); schreibt Struktur in
                               `stages_long_final.csv`, erzeugt `structure_profiles.csv`,
                               `mapping_structure_sequence.csv`.
5.  `densify_tr.py`            TR-Akteurkategorien (absolut/relativ), Verdichtung über generische Proxys
                               -> Spalten `tr_absolute`, `tr_relative` in `stages_long_final.csv`.
6.  `circulation_profiles.py`  vertikale Profile je Akteur -> `circulation_profiles.csv`.
7.  `circulation_index.py`     zusammengesetzter Drei-Achsen-Index -> `circulation_index.csv`.
8.  `tr_measures.py`           empirischer Zustand (S, g, act) und Ungleichheitskaskade (§5.17)
                               mit den Simulatorformeln -> `tr_measures.json`.
9.  `make_contract_and_figs.py` native Vertragstabelle für den Simulator -> `cohorte_contrat.csv`
                               und transversale Flussmatrix `flow.json`.
10. `figures.py`               Abbildungen 1–7 -> `fig1_kaskade.png` … `fig7_vergleich_AB.png`.
11. `father_coding.py`         Väterberufe -> HISCLASS/HISCAM; Vergleich Herkunft -> Ziel.
12. `compare_AB.py`            Vergleiche A (Zieldimension) und B (Intensität bei angeglichener
                               Auflösung) gegen die Referenztabelle.

Begleitdateien (keine Skripte): `referenztabelle_mobilitaet.csv` (publizierte Referenzraten mit Quellen),
`references.bib` (Bibliographie für die org-mode-Berichte und den Artikel).

Hinweis: Die Pfade in den Skripten erwarten Eingaben unter `out/` bzw. den Korpus im Arbeitsverzeichnis;
gegebenenfalls die obersten Pfadangaben je Skript anpassen.
