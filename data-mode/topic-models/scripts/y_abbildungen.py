# -*- coding: utf-8 -*-
"""Abbildungen 1 bis 12 von Kapitel 12 (PNG, 300 dpi) in figures/ als rk_abb<N>_<name>.png.
Die Nummern der Dateien folgen dem Prüfbericht; im Buch sind rk_abb10 = Abb. 8, rk_abb8 = Abb. 9,
rk_abb9 = Abb. 10, sonst stimmen die Nummern überein.

Abb. 1 bis 6 sind Schemata und Zusammenfassungen; ihre Zahlen stammen aus j_two_stage.py und k_eval2.py
(Konsens über 50 Läufe, Übergänge und κ gegen HISCLASS) und sind hier eingetragen.
rk_abb7 bis rk_abb12 lesen die Ergebnisse aus results/:
  rk_abb7, rk_abb8   rangordnung.json        (u_rangordnung.py)
  rk_abb9            date_diffs.json         (t_ergaenzungen.py)
  rk_abb10           circ_mob_v2.json        (t_ergaenzungen.py)
  rk_abb11           nebenbefund.json, leer_kontrolle.json  (s_nebenbefund.py, w_luecken.js)
  rk_abb12           leer_kontrolle.json     (w_luecken.js)
Abb. 13 (Kanäle mit den Jahren aus den Notizen) zeichnet das Buch mit build/figuren_kap11.py --abb08
aus results/course_N1_lexikon_hiscam_echte_jahre.json (x_kanaele.js).

Im Buch tragen die Abbildungen keine Titel (die Bildunterschrift übernimmt das); TITEL=1 setzt sie.
"""
from pfade import *
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e4e2dc", "#b8b6ae"
BLUE, ORANGE, SURF = "#2a78d6", "#eb6834", "#ffffff"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
})
import os
OUT = os.path.join(FIG, "rk_")
NOTITLE = not os.environ.get("TITEL")
from matplotlib.ticker import FuncFormatter
COMMA = FuncFormatter(lambda v, _: (f"{v:.1f}" if abs(v - round(v)) > 1e-9 else f"{v:.0f}").replace(".", ",").replace("-", "−"))


def save(fig, name):
    fig.savefig(OUT + name, dpi=300, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)


def title(ax, t, sub=None):
    if NOTITLE:
        return
    ax.set_title(t, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")


def box(ax, x, y, w, h, text, fc="#f4f3ef", ec=GRID, color=INK, bold=False, fs=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.2))


# ---------------------------------------------------------------- Abb. 1 Pipeline
fig, ax = plt.subplots(figsize=(8.2, 3.6)); ax.axis("off"); ax.set_xlim(-0.03, 1.03); ax.set_ylim(0, 1)
box(ax, 0.00, 0.40, 0.21, 0.22, "996 Berufs-\netappen aus\n163 Notizen", bold=True)
box(ax, 0.30, 0.72, 0.30, 0.20, "Stichwortlexikon\n(49 Begriffe)")
box(ax, 0.30, 0.40, 0.30, 0.20, "HISCO-Code → HISCAM-Wert\n+ Schwellen 67,6 / 82,4", fc="#eaf2fc", ec=BLUE)
box(ax, 0.30, 0.08, 0.30, 0.20, "Geburtsjahr + 15\n+ 4 × Etappennummer")
box(ax, 0.70, 0.72, 0.30, 0.20, "structure, sequence\n(60 % der Etappen)")
box(ax, 0.70, 0.40, 0.30, 0.20, "category\n(46 % der Etappen)", fc="#eaf2fc", ec=BLUE, bold=True)
box(ax, 0.70, 0.08, 0.30, 0.20, "year")
for y in (0.82, 0.50, 0.18):
    arrow(ax, 0.21, 0.51, 0.30, y); arrow(ax, 0.60, y, 0.70, y)
ax.text(0.85, 0.99, "Spalten der Vertragstabelle", ha="center", fontsize=9, color=INK2)
ax.text(0.45, 0.99, "Verfahren", ha="center", fontsize=9, color=INK2)
title(ax, "HISCO bestimmt nur die Akteurkategorie, nicht die Relationsstruktur")
save(fig, "abb1_pipeline.png")

# ---------------------------------------------------------------- Abb. 2 Vorgehen
fig, ax = plt.subplots(figsize=(8.2, 3.9)); ax.axis("off"); ax.set_xlim(-0.03, 1.03); ax.set_ylim(0, 1)
box(ax, 0.00, 0.62, 0.22, 0.26, "Ein Dokument je\nTätigkeits-\nwechsel: 996\nBerufsetappen", bold=True)
box(ax, 0.29, 0.62, 0.22, 0.26, "Topic-Modell\nK = 4\n50 Läufe → Konsens")
box(ax, 0.58, 0.74, 0.42, 0.14, "3 klare Topics: Laufjunge/Laden ·\nLehre/Druck · Journalist", fc="#eaf2fc", ec=BLUE)
box(ax, 0.58, 0.55, 0.42, 0.14, "Resttopic: 610 Etappen\n(editor, clerk, employed …)")
box(ax, 0.58, 0.20, 0.42, 0.24, "Untermodell nur im Resttopic\nK2 = 6, 50 Läufe → Konsens\n6 Unterthemen, u. a. Fabrik,\nBüro, Gewerkschaft")
box(ax, 0.00, 0.10, 0.48, 0.30, "Jedes Topic als manuell oder\nnicht-manuell gelesen\n→ Übergang je Akteur\n→ Vergleich mit HISCLASS (κ)", fc="#fdf0ea", ec=ORANGE)
arrow(ax, 0.22, 0.75, 0.29, 0.75); arrow(ax, 0.51, 0.75, 0.58, 0.81); arrow(ax, 0.51, 0.75, 0.58, 0.62)
arrow(ax, 0.79, 0.55, 0.79, 0.44); arrow(ax, 0.58, 0.32, 0.48, 0.28)
box(ax, 0.00, 0.47, 0.22, 0.10, "getrennt: 1.097 Neben-\ntätigkeiten, eigenes Modell", fs=8)
title(ax, "Das Vorgehen: zwei Stufen, jede mit 50 Läufen")
save(fig, "abb2_vorgehen.png")

# ---------------------------------------------------------------- Abb. 3 Topics bei K = 4, 5, 6
data = {
    "K = 4": [("Laufjunge", 129, BLUE), ("Lehre/Druck", 145, BLUE), ("Presse", 74, BLUE), ("Resttopic", 610, MUTED)],
    "K = 5": [("Laufjunge", 111, BLUE), ("Lehre/Druck", 119, BLUE), ("Presse", 71, BLUE), ("Redakteur", 97, BLUE), ("Resttopic", 560, MUTED)],
    "K = 6": [("Laufjunge", 109, BLUE), ("Lehre/Druck", 118, BLUE), ("Presse", 65, BLUE), ("Redakteur", 98, BLUE), ("Lehrer", 59, BLUE), ("Resttopic", 509, MUTED)],
}
fig, ax = plt.subplots(figsize=(8.2, 2.9))
for row, (k, segs) in enumerate(reversed(list(data.items()))):
    left = 0
    for i, (lab, n, c) in enumerate(segs):
        ax.barh(row, n, left=left, color=c, height=0.62, edgecolor=SURF, linewidth=2)
        ax.text(left + n / 2, row, f"{lab}\n{n}", ha="center", va="center", fontsize=7 if n < 80 else 7.5,
                color=INK if c == MUTED else "white")
        left += n
ax.set_yticks(range(3)); ax.set_yticklabels(list(reversed(list(data))))
ax.set_xlim(0, 960); ax.set_xlabel("Berufsetappen (Konsens über 50 Läufe)")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
title(ax, "Mehr als die Hälfte der Etappen landet in einem Resttopic",
      "Blau: Topics mit eindeutigen Wörtern. Grau: Resttopic mit gemischten Tätigkeiten.")
save(fig, "abb3_topics_k.png")

# ---------------------------------------------------------------- Abb. 4 Übergang manuell → nicht-manuell
rows = [("HISCLASS (Referenz)", 64, None, ORANGE),
        ("K = 4, ein Lauf", 71, 0.28, BLUE), ("K = 5, ein Lauf", 63, 0.27, BLUE),
        ("K = 6, ein Lauf", 66, 0.32, BLUE), ("K = 4, Konsens", 72, 0.30, BLUE),
        ("K = 4 + Resttopic-Modell, Konsens", 75, 0.30, BLUE)]
fig, ax = plt.subplots(figsize=(8.2, 3.3))
for i, (lab, v, k, c) in enumerate(reversed(rows)):
    ax.barh(i, v, color=c, height=0.6)
    ax.text(v + 1.8, i, f"{v} %" + (f"   κ = {k:.2f}".replace(".", ",") if k is not None else ""),
            va="center", fontsize=9, color=INK)
ax.axvline(64, color=ORANGE, lw=1, ls=(0, (3, 3)))
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in reversed(rows)])
ax.set_xlim(0, 100); ax.set_xlabel("Anteil der Akteure mit Übergang von manueller zu nicht-manueller Tätigkeit (%)")
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
title(ax, "Für die Kohorte dasselbe Bild wie HISCLASS – je Akteur nur mäßige Übereinstimmung",
      "κ = Übereinstimmung mit HISCLASS je Akteur, bereinigt um Zufall (0 = Zufall, 1 = vollständig)")
save(fig, "abb4_uebergang.png")

# ---------------------------------------------------------------- Abb. 5 Stabilität
panels = [("Berufe", [4, 5, 6], [97, 52, 94], 4),
          ("Nebentätigkeiten", [4, 5, 6], [62, 93, 91], 5),
          ("Resttopic (Untermodell)", [3, 4, 5, 6, 7, 8], [99, 67, 95, 94, 83, 94], 6)]
fig, axs = plt.subplots(1, 3, figsize=(8.2, 3.0), gridspec_kw={"width_ratios": [3, 3, 6]}, sharey=True)
for ax, (name, ks, vals, chosen) in zip(axs, panels):
    cols = [BLUE if k == chosen else MUTED for k in ks]
    ax.bar([str(k) for k in ks], vals, color=cols, width=0.6)
    for x, v in zip([str(k) for k in ks], vals):
        ax.text(x, v + 2, f"{v}", ha="center", fontsize=8.5, color=INK)
    ax.set_title(name, fontsize=10, color=INK, loc="left")
    ax.set_xlabel("Anzahl Topics"); ax.set_ylim(0, 110)
    ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
axs[0].set_ylabel("Stabile Etappen (%)")
if not NOTITLE: fig.suptitle("Wie stabil ist das Modell? Anteil der Etappen, die in ≥ 2/3 der 50 Läufe ihr Topic behalten",
             x=0.01, ha="left", fontsize=11, fontweight="bold", y=1.06)
if not NOTITLE: fig.text(0.01, 0.975, "Blau: gewähltes Modell. K = 3 im Resttopic ist stabil, bildet aber wieder ein Sammeltopic.",
         fontsize=9, color=INK2)
fig.tight_layout(rect=(0, 0, 1, 0.93))
save(fig, "abb5_stabilitaet.png")

# ---------------------------------------------------------------- Abb. 6 Abweichungen
fig, ax = plt.subplots(figsize=(8.2, 2.6))
segs = [("klarer Übergang, den HISCLASS verfehlt", 16, BLUE, 1.0),
        ("echter Übergang über falsch gelesene Etappe", 2, BLUE, 0.55),
        ("unklar", 9, MUTED, 1.0), ("Fehler der Topics", 1, ORANGE, 1.0)]
left = 0
for lab, n, c, a in segs:
    ax.barh(1, n, left=left, color=c, alpha=a, height=0.55, edgecolor=SURF, linewidth=2)
    ax.text(left + n / 2, 1, str(n), ha="center", va="center", fontsize=9,
            color="white" if c != MUTED else INK)
    left += n
ax.barh(0, 4, color=ORANGE, height=0.55)
ax.text(4.4, 0, "4", va="center", fontsize=9)
ax.set_yticks([0, 1]); ax.set_yticklabels(["HISCLASS sieht Übergang,\nTopics nicht",
                                           "Topics sehen Übergang,\nHISCLASS nicht (28)"])
ax.set_xlim(0, 30); ax.set_xlabel("Akteure"); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=a) for _, _, c, a in segs]
ax.legend(handles, [s[0] for s in segs], loc="lower right", fontsize=8, frameon=False)
title(ax, "Die Abweichungen gehen fast nur in eine Richtung",
      "Zweistufiger Konsens gegen HISCLASS, 113 Akteure. Bei 25 der 28 hat die manuelle Etappe keinen HISCO-Code.")
save(fig, "abb6_abweichungen.png")

# ---------------------------------------------------------------- Abb. 7 Rangordnung
RG = json.load(open(ergeb("rangordnung.json"), encoding="utf-8"))
P = {p: {"attraction": v["attraktivitaet"], "mean_hiscam": v["hiscam_mittel"]} for p, v in RG["positionen"].items()}
NAMES = {"AA": "A.A Autor, Dozent", "AB": "A.B Religion", "AC": "A.C Druckgewerbe",
         "AD": "A.D Verlag, Buchhandel", "BB": "B.B Politik", "BD": "B.D Gewerkschaft",
         "CA": "C.A Leitung, Landwirt", "CC": "C.C Handarbeit", "CD": "C.D Bote, Handel",
         "DA": "D.A Journalismus", "DC": "D.C Zeitungsverkauf", "DD": "D.D Redaktion"}
fig, ax = plt.subplots(figsize=(8.2, 4.6))
LPOS = {"AB": (0.33, 90.5), "DA": (0.02, 89.5), "BB": (0.43, 87.6), "BD": (0.30, 86.0),
        "CA": (-0.20, 84.5), "AD": (-0.20, 79.0), "AA": (0.30, 78.0), "DD": (0.33, 82.0),
        "AC": (-0.05, 69.0), "CC": (-0.48, 64.5), "CD": (-0.22, 58.5), "DC": (-0.45, 55.0)}
for p, lab in NAMES.items():
    x, y = P[p]["attraction"], P[p]["mean_hiscam"]
    ax.scatter(x, y, s=46, color=BLUE, zorder=3, edgecolor=SURF, linewidth=1.5)
    lx, ly = LPOS[p]
    ax.annotate(lab, xy=(x, y), xytext=(lx, ly), fontsize=8, color=INK2, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, shrinkA=0, shrinkB=4))
ax.axvline(0, color=GRID, lw=1)
ax.set_xlabel("Netto-Attraktivität in der Kohorte  (Zuflüsse − Abflüsse) / (Zuflüsse + Abflüsse)")
ax.set_ylabel("Mittlerer HISCAM-Wert")
ax.xaxis.set_major_formatter(COMMA); ax.set_xlim(-0.62, 0.62); ax.set_ylim(53, 93); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.text(-0.6, 74, "← Position wird verlassen", fontsize=8.5, color=INK2)
ax.text(0.53, 74, "Position wird aufgesucht →", fontsize=8.5, color=INK2, ha="right")
title(ax, f"Die Bewegungen der Akteure ordnen die Positionen fast wie HISCAM (ρ = {RG['spearman']['rho']:.2f})".replace(".", ","),
      "12 Positionen (Struktur.Sequenz) der Lexikon-Kodierung; ρ = Spearmans Rangkorrelation")
save(fig, "abb7_rangordnung.png")

# ---------------------------------------------------------------- Abb. 8 Vertikale Ungleichheit
AQUA = "#1baf7a"
VS = RG["vertikal_statisch"]
rows = [(lab, VS["HISCAM-Regel (N1)"][x], VS["Regel A (E1)"][x], VS["Regel B (E1B)"][x])
        for lab, x in (("A · Kultur", "A"), ("B · Politik", "B"), ("C · Wirtschaft", "C"), ("D · Medien", "D"))]
fig, ax = plt.subplots(figsize=(8.2, 3.6))
for i, (lab, h, a, b) in enumerate(reversed(rows)):
    vals = [h, a, b]
    ax.plot([min(vals), max(vals)], [i, i], color=GRID, lw=2.5, zorder=1)
    for v, col, dy in ((h, MUTED, 0.24), (a, BLUE, 0.24), (b, AQUA, -0.34)):
        ax.scatter(v, i, s=80, color=col, zorder=3, edgecolor=SURF, linewidth=1.5)
        ax.text(v, i + dy, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8.5,
                color=INK2 if col == MUTED else col)
ax.set_yticks(range(4)); ax.set_yticklabels([r[0] for r in reversed(rows)])
ax.set_xlim(-0.02, 0.8); ax.set_ylim(-0.7, 3.6); ax.xaxis.set_major_formatter(COMMA)
ax.set_xlabel("Vertikale Ungleichheit in der Struktur (Gini der Kategorien je Sequenz; 0 = alle gleich)")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.scatter([], [], s=60, color=MUTED, label="HISCAM-Regel (Statusstufen)")
ax.scatter([], [], s=60, color=BLUE, label="Zirkulationsregel A (Ziel entscheidet)")
ax.scatter([], [], s=60, color=AQUA, label="Zirkulationsregel B (Ausgangsposition entscheidet)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8, frameon=False)
title(ax, "Regel B findet ohne Statusskala den Kern des HISCAM-Befunds: die Wirtschaft ist am stärksten geschichtet",
      "Gleiche Zuordnung zu Strukturen und Sequenzen (Lexikon); nur die Regel für die Kategorien wechselt.")
save(fig, "abb8_vertikal.png")

# ---------------- Abb. 9: Abweichung bisher geschätzter Jahre
d = np.array(json.load(open(ergeb("date_diffs.json"))))
fig, ax = plt.subplots(figsize=(8.2, 3.2))
bins = np.arange(-50, 50, 5)
cnt, edges = np.histogram(d, bins=bins)
cols = [MUTED if abs(c) <= 10 else BLUE for c in (edges[:-1] + 2.5)]
ax.bar(edges[:-1] + 2.5, cnt, width=4.4, color=cols)
ax.axvline(0, color=INK2, lw=1)
ax.text(1, cnt.max() * 0.95, "bisherige Schätzung\nstimmt", fontsize=8.5, color=INK2)
ax.set_xlabel("Echtes Jahr minus bisher geschätztes Jahr (Jahre)")
ax.set_ylabel("Etappen")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
share = (np.abs(d) > 10).mean()
title(ax, f"Bei {share*100:.0f} % der datierten Etappen lag die bisherige Schätzung mehr als 10 Jahre daneben",
      f"{len(d)} Etappen mit Jahreszahl oder Altersangabe in der Notiz; blau: Abweichung über 10 Jahre")
save(fig, "abb9_jahre.png")

# ---------------- Abb. 10: Zirkulation gegen Mobilität
R = json.load(open(ergeb("circ_mob_v2.json"), encoding="utf-8"))["Topics"]
types = ["Strukturwechsel", "Sequenzwechsel", "gleiche Position"]
labels = {"Strukturwechsel": "Wechsel der Relationsstruktur", "Sequenzwechsel": "Wechsel der Sequenz\n(gleiche Struktur)",
          "gleiche Position": "gleiche Position"}
fig, ax = plt.subplots(figsize=(8.2, 3.3))
for row, t in enumerate(reversed(types)):
    v = [R["tab"].get(f"{t}|{h}", 0) for h in ("auf", "gleich", "ab")]
    n = sum(v); left = 0
    for val, col, h in zip(v, (BLUE, MUTED, ORANGE), ("aufwärts", "gleich", "abwärts")):
        w = val / n * 100
        ax.barh(row, w, left=left, color=col, height=0.6, edgecolor=SURF, linewidth=2)
        if w >= 8:
            ax.text(left + w / 2, row, f"{w:.0f} %", ha="center", va="center", fontsize=9,
                    color="white" if col != MUTED else INK)
        left += w
    ax.text(101.5, row, f"{R['n_typ'][t]} Übergänge,\n{n} mit HISCAM prüfbar", va="center", fontsize=8.5, color=INK2)
ax.set_yticks(range(3)); ax.set_yticklabels([labels[t] for t in reversed(types)])
ax.set_xlim(0, 100); ax.set_xlabel("Richtung der Statusänderung nach HISCAM (% der prüfbaren Übergänge)")
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (BLUE, MUTED, ORANGE)]
ax.legend(handles, ["aufwärts (≥ +3)", "gleich", "abwärts (≤ −3)"], loc="upper center",
          bbox_to_anchor=(0.45, -0.28), ncol=3, frameon=False, fontsize=8.5)
title(ax, "Nicht einmal die Hälfte der Wechsel zwischen Relationsstrukturen ist ein Aufstieg",
      "Übergänge zwischen aufeinanderfolgenden Etappen, überarbeitete Topic-Klassifikation")
save(fig, "abb10_zirkulation.png")

# ---------------- Abb. 11: Nebenbefund zerlegt
NB = json.load(open(ergeb("nebenbefund.json"), encoding="utf-8"))
LK = json.load(open(ergeb("leer_kontrolle.json"), encoding="utf-8"))
st = {"statisch, nur Etappen mit Kategorie\n(Bericht zur Atypizität)": (NB["statisch_gepoolt"]["nur_kodiert"], MUTED, "o"),
      "statisch, fehlende Kategorie\nals Bewahrende gelesen": (NB["statisch_gepoolt"]["alle"], INK2, "s"),
      "Eingabe des Zwillings\n(Mittel der Jahre mit Akteuren)": (LK["orig"]["input_besetzt"], BLUE, "D"),
      "laufender Zwilling\n(Mittel über den Lauf)": (LK["orig"]["twin"], ORANGE, "o")}
st = {k: ([round(x, 2) for x in v], c, m) for k, (v, c, m) in st.items()}  # wie im Buch auf zwei Stellen
names = ["A Kultur", "B Politik", "C Wirtschaft", "D Medien"]
fig, ax = plt.subplots(figsize=(8.2, 3.6))
for x in range(4):
    vals = [v[0][x] for v in st.values()]
    ax.plot([min(vals), max(vals)], [3 - x] * 2, color=GRID, lw=3, zorder=1)
for lab, (v, col, m) in st.items():
    ax.scatter(v, [3, 2, 1, 0], s=70, color=col, marker=m, zorder=3, label=lab, edgecolor="white", linewidth=0.8)
ax.axvline(0.40, color=INK2, lw=0.8, ls=":")
ax.text(0.405, 3.45, "symmetrischer\nAusgangswert 0,40", fontsize=8, color=INK2, va="center")
ax.set_yticks(range(4)); ax.set_yticklabels(list(reversed(names)))
ax.set_xlim(0, 0.8); ax.set_ylim(-0.5, 3.8)
ax.set_xlabel("Vertikale Ungleichheit (Gini) je Struktur")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v:.1f}".replace(".", ",")))
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, frameon=False, fontsize=8.5)
title(ax, "Die Daten bleiben bis zur Eingabe geschichtet wie gelesen; erst der Lauf kehrt das Bild um",
      "Veröffentlichte Vertragstabelle (N0); C bleibt in der Eingabe am stärksten, B am schwächsten geschichtet")
save(fig, "abb11_nebenbefund.png")

# ---------------- Abb. 12: Kontrolle leere Strukturen
var = [("orig", "gleichverteilte Lückenfüllung (bisher)", ORANGE, "o"),
       ("fort", "(a) letzte Beobachtung fortgeschrieben", INK2, "s"),
       ("pool", "(b) Gesamtzusammensetzung in den Lücken", BLUE, "D"),
       ("konst", "(c) Gesamtzusammensetzung in allen Jahren\n(nur die Mechanik wirkt)", AQUA, "^")]
fig, ax = plt.subplots(figsize=(8.2, 3.6))
for x in range(4):
    vals = [LK[v[0]]["twin"][x] for v in var]
    ax.plot([min(vals), max(vals)], [3 - x] * 2, color=GRID, lw=3, zorder=1)
for k, lab, col, m in var:
    ax.scatter(LK[k]["twin"], [3, 2, 1, 0], s=70, color=col, marker=m, zorder=3, label=lab, edgecolor="white", linewidth=0.8)
ax.set_yticks(range(4)); ax.set_yticklabels(list(reversed(names)))
ax.set_xlim(0, 0.8); ax.set_ylim(-0.5, 3.6)
ax.set_xlabel("Vertikale Ungleichheit (Gini) je Struktur, Mittel über den Lauf")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v:.1f}".replace(".", ",")))
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, frameon=False, fontsize=8.5)
title(ax, "Ohne gleichverteilte Lückenfüllung ist C wieder am stärksten geschichtet",
      "Laufender Zwilling mit N0; Behandlung von Strukturen ohne aktive Akteure")
save(fig, "abb12_leer.png")
print("Abbildungen in", FIG)
