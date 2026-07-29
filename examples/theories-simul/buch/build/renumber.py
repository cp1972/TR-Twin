#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
renumber.py — nummeriert Abbildungen und Tabellen in den Org-Quelldateien.

Je Kapitel wird getrennt gezählt, jeweils ab 1, in der Reihenfolge des
Auftretens. Aus

    #+NAME: fig:white-rewire
    #+CAPTION: Bei Veränderung der netzwerkartigen Struktur …

wird

    #+NAME: fig:white-rewire
    #+CAPTION: *Abbildung 3.* Bei Veränderung der netzwerkartigen Struktur …

Ein bereits vorhandenes Präfix wird ersetzt, das Skript lässt sich also
beliebig oft laufen — etwa nachdem eine Abbildung eingefügt oder verschoben
wurde. Die Verweise im Text bleiben symbolisch ([[fig:white-rewire]]);
build.py setzt beim Export die passende Zahl ein und liest sie dafür aus
genau diesem Präfix, so dass Legende und Verweis nicht auseinanderlaufen
können.

    python3 build/renumber.py                 # buch/ neben build/
    python3 build/renumber.py --quelle ../buch
    python3 build/renumber.py --pruefen       # nur berichten, nichts ändern
"""
import argparse, glob, os, re, sys

HIER = os.path.dirname(os.path.abspath(__file__))

PRAEFIX = re.compile(r'^\*(Abbildung|Tabelle) \d+\.\*\s*')
WORT = {'fig': 'Abbildung', 'tab': 'Tabelle'}


def bloecke(zeilen):
    """Liefert (start, ende, name, caption_index, typ) für jeden Legendenblock."""
    i, out = 0, []
    while i < len(zeilen):
        if zeilen[i].startswith(('#+NAME:', '#+CAPTION:')):
            j = i
            while j < len(zeilen) and zeilen[j].startswith('#+'):
                j += 1
            name = cap = None
            for k in range(i, j):
                if zeilen[k].startswith('#+NAME:'):
                    name = zeilen[k][len('#+NAME:'):].strip()
                elif zeilen[k].startswith('#+CAPTION:'):
                    cap = k
            folgt = zeilen[j] if j < len(zeilen) else ''
            if folgt.lstrip().startswith('|'):
                typ = 'tab'
            elif 'file:' in folgt:
                typ = 'fig'
            elif name and ':' in name:
                typ = name.split(':', 1)[0]
            else:
                typ = None
            if cap is not None and typ in WORT:
                out.append((i, j, name, cap, typ))
            i = j
        else:
            i += 1
    return out


def datei(pfad, schreiben=True):
    zeilen = open(pfad, encoding='utf-8').read().split('\n')
    zaehler = {'fig': 0, 'tab': 0}
    aenderungen = []
    for _s, _e, name, cap, typ in bloecke(zeilen):
        zaehler[typ] += 1
        n = zaehler[typ]
        text = zeilen[cap][len('#+CAPTION:'):].strip()
        alt = text
        text = PRAEFIX.sub('', text)
        neu = f'#+CAPTION: *{WORT[typ]} {n}.* {text}'
        if zeilen[cap] != neu:
            aenderungen.append((name or '—', alt[:48], f'{WORT[typ]} {n}'))
        zeilen[cap] = neu
    if schreiben and aenderungen:
        open(pfad, 'w', encoding='utf-8').write('\n'.join(zeilen))
    return zaehler, aenderungen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quelle', default=os.path.join(HIER, '..', 'buch'))
    ap.add_argument('--pruefen', action='store_true', help='nichts schreiben')
    a = ap.parse_args()
    quelle = os.path.abspath(a.quelle)
    if not os.path.isdir(quelle):
        sys.exit(f'Quellverzeichnis fehlt: {quelle}')

    gesamt = 0
    for pfad in sorted(glob.glob(os.path.join(quelle, '*.org'))):
        z, ae = datei(pfad, schreiben=not a.pruefen)
        if z['fig'] or z['tab']:
            print(f"{os.path.basename(pfad):38s} "
                  f"Abbildungen: {z['fig']:2d}   Tabellen: {z['tab']:2d}"
                  + (f"   ({len(ae)} geändert)" if ae else ''))
            gesamt += len(ae)
    print(f"\n{'Zu ändern' if a.pruefen else 'Geändert'}: {gesamt} Legenden")


if __name__ == '__main__':
    main()
