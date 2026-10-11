# -*- coding: utf-8 -*-
"""Pfade der Prüfung mit Topic-Modellen (Kapitel 12). Alle Pfade sind relativ zu diesem Ordner.

    data-mode/topic-models/
        scripts/    die Skripte (dieser Ordner)
        data/       Eingaben: actors.csv, stages_long_final.csv (aus data-mode/coding)
        work/       Zwischenstände (Pickle-Dateien), werden neu erzeugt
        contracts/  Vertragstabellen für den Zwilling
        results/    Ergebnisse (JSON, CSV)
        figures/    Abbildungen von Kapitel 12

MTA 3.5 wird gebraucht (Konsens über viele Läufe). Den Ordner code/ von MTA übergibt man über
die Umgebungsvariable MTA_CODE, z. B.  export MTA_CODE=~/mta-app/MTA-for-Master/code
"""
import os, sys, importlib.util

HIER = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.dirname(HIER)
REPO = os.path.dirname(os.path.dirname(BASIS))
DATEN = os.path.join(BASIS, 'data')
ARBEIT = os.path.join(BASIS, 'work')
VERTRAG = os.path.join(BASIS, 'contracts')
ERGEB = os.path.join(BASIS, 'results')
FIG = os.path.join(BASIS, 'figures')
LEXIKON_SKRIPT = os.path.join(REPO, 'data-mode', 'coding', 'scripts', '04_code_structure_seq.py')
for _d in (ARBEIT, VERTRAG, ERGEB, FIG):
    os.makedirs(_d, exist_ok=True)


def mta_core():
    """Lädt mta_core.py aus MTA 3.5 (Ordner in MTA_CODE)."""
    code = os.environ.get('MTA_CODE')
    if not code or not os.path.exists(os.path.join(code, 'mta_core.py')):
        sys.exit('MTA_CODE muss auf den Ordner code/ von MTA 3.5 zeigen (dort liegt mta_core.py).')
    spec = importlib.util.spec_from_file_location('mta_core', os.path.join(code, 'mta_core.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if not hasattr(m, 'topic_stability'):
        sys.exit('Diese MTA-Fassung kennt topic_stability nicht; gebraucht wird MTA 3.5 oder neuer.')
    return m


def arbeit(name): return os.path.join(ARBEIT, name)
def vertrag(name): return os.path.join(VERTRAG, name)
def ergeb(name): return os.path.join(ERGEB, name)
