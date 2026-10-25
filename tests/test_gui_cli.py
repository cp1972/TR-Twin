"""The interface (Chromium) and the command line (node run.js) give the same results for the same run file.

    python3 tests/test_gui_cli.py [chromium executable]

For each example run file: the run is computed in the browser (button Compute), its series and tables are read
from the page, and compared with series.csv and tables.csv written by node run.js. Also checks that a replay of
seed 1 ends in the state of the computed run, and that the page logs no error.
"""
import os, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROME = sys.argv[1] if len(sys.argv) > 1 else "/opt/pw-browsers/chromium"
CASES = [("runs/compare_parsons_luhmann.csv", ["simulation-mode/profiles/profil_Parsons.csv", "simulation-mode/profiles/profil_Luhmann.csv"]),
         ("runs/arbeiter_N1.csv", ["data-mode/topic-models/contracts/N1_lexikon_hiscam_echte_jahre.csv"]),
         ("runs/ouvriers_N1_instances.csv", ["data-mode/topic-models/contracts/N1_lexikon_hiscam_echte_jahre.csv", "data-mode/data/instances/instances_full_empirical.csv"])]
bad = 0
with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
    b = p.chromium.launch(executable_path=CHROME)
    for run, files in CASES:
        out = os.path.join(tmp, os.path.basename(run))
        subprocess.run(["node", "run.js", run, "--lang", "en", "--out", out], cwd=REPO, check=True, capture_output=True)
        cli_series = open(os.path.join(out, "series.csv"), encoding="utf-8").read().lstrip("﻿")
        cli_tables = open(os.path.join(out, "tables.csv"), encoding="utf-8").read().lstrip("﻿")
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + os.path.join(REPO, "tr-twin.html")); pg.wait_for_timeout(1500)
        pg.evaluate("setLang('en')")
        pg.locator("#r68files").set_input_files([os.path.join(REPO, run)] + [os.path.join(REPO, f) for f in files])
        pg.wait_for_timeout(500)
        pg.click("#r68go")
        pg.wait_for_function("R68&&R68.sm&&!R68busy", timeout=3600000)
        gui_series = pg.evaluate("r68SeriesCSV(R68.res)")
        gui_tables = pg.evaluate("r68AllCSV(R68.sm)")
        # replay of the selected run (seed 1) to its end: the state equals the last computed row
        pg.evaluate("running=true")
        pg.wait_for_function("R68.runner.done", timeout=3600000)
        same_end = pg.evaluate("(()=>{const r=R68.res.runs[R68.selIdx],q=r.rows[r.rows.length-1];return JSON.stringify(q.S)===JSON.stringify(S)&&q.gini===gini()&&q.recip===reciprocity();})()")
        ok = gui_series == cli_series and gui_tables == cli_tables and same_end and not errs
        bad += not ok
        print(f"{run:40} series {'=' if gui_series == cli_series else '≠'} · tables {'=' if gui_tables == cli_tables else '≠'} · replay end {'=' if same_end else '≠'} · errors {len(errs)}")
        for e in errs: print("   ", e)
        pg.close()
    b.close()
print("✓ interface = command line" if not bad else f"✗ {bad} case(s) differ")
sys.exit(1 if bad else 0)
