#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prototyp des Prismenmodus — Seite der Akteure.
Liest ein bis fünf Laufbahnen der Kohorte als SONDEN (Testteilchen im relationalen Feld).
"""
import csv, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# --- Sonden (entry_id): ein Bogen über beide Regime -------------------------
PROBES = ["735", "430", "235", "108", "481"]   # Watson, Leno, Farish, Burgess, Mann

# --- Statusskala (entspricht der vertikalen GINI-Reihung im Simulator) ------
STATUS = {"established": 3, "aspirant": 2, "conservative": 1, "excluded": 0,
          "possedant": 3, "exclu": 0}            # tolerate synonyms
STATUS_LABEL = {3: "established", 2: "aspirant", 1: "conservative", 0: "disappointed"}
STRUCT_NAME = {"A": "Culture", "B": "Politics", "C": "Economy", "D": "Media"}

# Solarized
SOL = {"base03": "#002b36", "base01": "#586e75", "base1": "#93a1a1",
       "base2": "#eee8d5", "base3": "#fdf6e3",
       "blue": "#268bd2", "cyan": "#2aa198", "yellow": "#b58900",
       "red": "#dc322f", "green": "#859900", "violet": "#6c71c5"}
CAT_COLOR = {3: SOL["green"], 2: SOL["cyan"], 1: SOL["yellow"], 0: SOL["red"]}
LANE = {"A": 3, "B": 2, "C": 1, "D": 0}          # vertical lanes in the figure


def load():
    traj = {}
    with open("out/cohorte_contrat.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["aid"] in PROBES:
                traj.setdefault(r["aid"], []).append(
                    (int(r["year"]), r["structure"], (r["category"] or "").strip(), r["sequence"]))
    for a in traj:
        traj[a].sort()
    meta = {}
    with open("out/circulation_profiles.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["entry_id"] in PROBES:
                meta[r["entry_id"]] = {"name": (r["forename"] + " " + r["surname"]).strip(),
                                       "birth": r["birth_year"]}
    with open("out/actors.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["entry_id"] in PROBES:
                meta.setdefault(r["entry_id"], {})
                meta[r["entry_id"]]["father"] = r["father_occupation"]
                meta[r["entry_id"]]["title"] = r["title"]
    return traj, meta


def crossings(path):
    """Structure->structure transitions the actor actually traverses (channels proven open)."""
    out = []
    for (y0, s0, *_), (y1, s1, *_) in zip(path, path[1:]):
        if s0 != s1:
            out.append((s0, s1))
    return out


def reading(aid, path, meta):
    structs = [s for _, s, _, _ in path]
    cats = [STATUS[c] for _, _, c, _ in path if c in STATUS]
    span = (path[0][0], path[-1][0])
    # vertikaler Werdegang
    net = (cats[-1] - cats[0]) if cats else None
    nrev = sum(1 for a, b, c in zip(cats, cats[1:], cats[2:])
               if (b - a) * (c - b) < 0) if len(cats) >= 3 else 0
    # Heuristiken zum Ablesen des Feldes
    cr = crossings(path)
    ends_B = structs[-1] == "B"
    a_to_c = any(s0 == "A" and s1 == "C" for s0, s1 in cr)
    late = span[1] >= 1900
    notes = []
    if a_to_c and not late:
        notes.append("A pulled into C (culture satellised by the economy)")
    if ends_B or structs[-3:].count("B") >= 2:
        notes.append("carried into Politics (B) — the 20th-c. rise of B")
    if "D" in structs and ("B" in structs[structs.index("D"):] if "D" in structs else False):
        notes.append("Media (D) used as a ramp toward Politics (B)")
    dom = max(set(structs), key=structs.count)
    return {
        "aid": aid, "name": meta.get(aid, {}).get("name", "?"),
        "birth": meta.get(aid, {}).get("birth", "") or "?",
        "father": meta.get(aid, {}).get("father", "") or "?",
        "span": f"{span[0]}-{span[1]}",
        "n_stages": len(path),
        "structs_touched": "".join(sorted(set(structs))),
        "dominant_struct": dom,
        "crossings": " ".join(f"{a}>{b}" for a, b in cr) or "—",
        "n_crossings": len(cr),
        "status_path": "".join(str(c) for c in cats),
        "status_first": STATUS_LABEL.get(cats[0], "?") if cats else "?",
        "status_last": STATUS_LABEL.get(cats[-1], "?") if cats else "?",
        "vertical_net": net,
        "n_reversals": nrev,
        "field_reading": "; ".join(notes) or "stays within its core structure",
    }


def sheet(rd, path):
    print("═" * 92)
    print(f"PROBE #{rd['aid']}  {rd['name']}   (b.{rd['birth']}, father: {rd['father']})   {rd['span']}")
    print("  path:", " → ".join(f"{y}:{s}/{seq}[{c[:5] or '·'}]" for y, s, c, seq in path))
    print(f"  structures touched : {rd['structs_touched']}   dominant: {rd['dominant_struct']} ({STRUCT_NAME[rd['dominant_struct']]})")
    print(f"  channels proven open (crossings): {rd['crossings']}   [{rd['n_crossings']}]")
    print(f"  vertical fate (status 3>2>1>0): {rd['status_path']}   "
          f"{rd['status_first']} → {rd['status_last']}   net {rd['vertical_net']:+d}   reversals {rd['n_reversals']}")
    print(f"  ▶ FIELD READING: {rd['field_reading']}")


def figure(traj, meta, readings):
    n = len(PROBES)
    fig, axes = plt.subplots(n, 1, figsize=(11, 1.7 * n + 1), sharex=True)
    fig.patch.set_facecolor(SOL["base3"])
    if n == 1:
        axes = [axes]
    for ax, aid in zip(axes, PROBES):
        ax.set_facecolor(SOL["base3"])
        path = traj[aid]
        xs = [y for y, _, _, _ in path]
        ys = [LANE[s] for _, s, _, _ in path]
        ax.plot(xs, ys, "-", color=SOL["base1"], lw=1.4, zorder=1)
        for (y, s, c, seq) in path:
            col = CAT_COLOR.get(STATUS.get(c, -1), SOL["base01"])
            ax.scatter(y, LANE[s], s=120, color=col, edgecolor=SOL["base03"],
                       lw=0.6, zorder=3)
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(["D Media", "C Econ.", "B Polit.", "A Cult."],
                           fontsize=8, color=SOL["base01"])
        ax.set_ylim(-0.6, 3.6)
        rd = next(r for r in readings if r["aid"] == aid)
        ax.set_title(f"{rd['name']}  ({rd['span']}) — {rd['field_reading']}",
                     fontsize=9, color=SOL["base03"], loc="left", pad=3)
        for sp in ax.spines.values():
            sp.set_color(SOL["base1"])
        ax.tick_params(colors=SOL["base01"])
        ax.grid(axis="x", color=SOL["base2"], lw=0.6)
    axes[-1].set_xlabel("year", color=SOL["base01"])
    legend = [Line2D([0], [0], marker="o", color="w", markerfacecolor=CAT_COLOR[k],
                     markeredgecolor=SOL["base03"], markersize=9, label=STATUS_LABEL[k])
              for k in (3, 2, 1, 0)]
    fig.legend(handles=legend, loc="upper center", ncol=4, frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("Prism mode — actor probes: each biography as a test particle in the relational field",
                 fontsize=11, color=SOL["base03"], y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig("fig_prism_acteurs.png", dpi=150, bbox_inches="tight",
                facecolor=SOL["base3"])
    print("\n[figure] fig_prism_acteurs.png written")


def main():
    traj, meta = load()
    readings = [reading(a, traj[a], meta) for a in PROBES]
    for rd in readings:
        sheet(rd, traj[rd["aid"]])
    with open("prism_readings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(readings[0].keys()))
        w.writeheader()
        w.writerows(readings)
    print("\n[table] prism_readings.csv written")
    figure(traj, meta, readings)


if __name__ == "__main__":
    main()
