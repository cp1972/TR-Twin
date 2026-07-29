#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — Stapelkonvertierung der Buchkapitel (Org) nach DOCX bzw. ODT.

    python3 build.py                    # ein DOCX je Kapitel  -> ausgabe/
    python3 build.py --book             # zusätzlich ein Gesamtdokument
    python3 build.py --odt              # zusätzlich ODT
    python3 build.py --pdf              # zusätzlich PDF (über LibreOffice)
    python3 build.py --only kapitel-05  # nur passende Dateien
    python3 build.py --quelle ../buch --ziel ../ausgabe

Der Aufruf erwartet im Quellverzeichnis: die .org-Dateien, Bericht.bib,
die .csl-Dateien und den Ordner figures/.
Die Formatvorlage reference.docx wird bei Bedarf automatisch erzeugt
(make_reference_docx.py muss daneben liegen).

Voraussetzungen: pandoc >= 3.0.
Optional:  rsvg-convert | cairosvg | inkscape | soffice   (für SVG-Abbildungen)
           soffice                                        (für ODT/PDF)
"""
import argparse, math, os, re, shutil, subprocess, sys

HIER = os.path.dirname(os.path.abspath(__file__))

# Zielbreite der Abbildungen im Satzspiegel (A4 minus 2×2,5 cm = 16,1 cm)
BILDBREITE_CM = 15.0
BILD_DPI      = 300

CSL = 'chicago-author-date-de-ibid.csl'
BIB = 'Bericht.bib'


# --------------------------------------------------------------- Hilfsfunktionen
def hat(prog):
    return shutil.which(prog) is not None


def lauf(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(f"\nFEHLER bei: {' '.join(cmd[:4])} …\n{r.stderr[:1500]}\n")
    return r.returncode == 0


def svg_nach_png(svg, png, breite_px):
    """Erste funktionierende Methode gewinnt."""
    if hat('rsvg-convert'):
        if lauf(['rsvg-convert', '-w', str(breite_px), '-o', png, svg]):
            return True
    try:
        import cairosvg
        cairosvg.svg2png(url=svg, write_to=png, output_width=breite_px)
        return True
    except Exception:
        pass
    if hat('inkscape'):
        if lauf(['inkscape', svg, '--export-type=png',
                 f'--export-width={breite_px}', f'--export-filename={png}']):
            return True
    if hat('soffice'):
        aus = os.path.dirname(png)
        if lauf(['soffice', '--headless', '--convert-to', 'png',
                 svg, '--outdir', aus]):
            erzeugt = os.path.join(aus, os.path.splitext(os.path.basename(svg))[0] + '.png')
            if os.path.exists(erzeugt):
                if erzeugt != png:
                    shutil.move(erzeugt, png)
                return True
    return False


def dpi_setzen(png, breite_cm):
    """Physische Breite über die DPI-Angabe des PNG festlegen."""
    try:
        from PIL import Image
    except ImportError:
        return
    with Image.open(png) as im:
        w = im.size[0]
        dpi = max(1, round(w / (breite_cm / 2.54)))
        im.save(png, dpi=(dpi, dpi))


def medien_aufbereiten(quelle, cache):
    """SVG -> PNG umwandeln, PNG auf Zielbreite bringen. Gibt {alt: neu} zurück."""
    figs = os.path.join(quelle, 'figures')
    if not os.path.isdir(figs):
        return {}
    os.makedirs(cache, exist_ok=True)
    px = round(BILDBREITE_CM / 2.54 * BILD_DPI)
    karte = {}
    for name in sorted(os.listdir(figs)):
        alt = os.path.join(figs, name)
        stamm, endung = os.path.splitext(name)
        endung = endung.lower()
        if endung == '.svg':
            neu = os.path.join(cache, stamm + '.png')
            if not os.path.exists(neu) or os.path.getmtime(alt) > os.path.getmtime(neu):
                if not svg_nach_png(alt, neu, px):
                    sys.stderr.write(f"  ! SVG nicht konvertierbar: {name}\n")
                    continue
                dpi_setzen(neu, BILDBREITE_CM)
            karte[f'figures/{name}'] = os.path.relpath(neu, quelle).replace(os.sep, '/')
        elif endung in ('.png', '.jpg', '.jpeg'):
            neu = os.path.join(cache, name)
            if not os.path.exists(neu) or os.path.getmtime(alt) > os.path.getmtime(neu):
                shutil.copy(alt, neu)
                if endung == '.png':
                    dpi_setzen(neu, BILDBREITE_CM)
            karte[f'figures/{name}'] = os.path.relpath(neu, quelle).replace(os.sep, '/')
    return karte


ORG_MUELL = re.compile(r'^#\+(STARTUP|CITE_EXPORT|LATEX_CLASS|LATEX_CLASS_OPTIONS|'
                       r'LATEX_HEADER|OPTIONS|BIBLIOGRAPHY|AUTHOR|DATE):.*$',
                       re.M | re.I)

CAP_NR = re.compile(r'^#\+CAPTION:\s*\*(?:Abbildung|Tabelle)\s+(\d+)\.\*')


def nummern(text):
    """{'fig:white-rewire': '3', …} — gelesen aus den Legenden-Präfixen,
    die renumber.py gesetzt hat. Legende und Verweis stammen damit aus
    derselben Quelle und können nicht auseinanderlaufen."""
    karte, zeilen = {}, text.split('\n')
    i = 0
    while i < len(zeilen):
        if zeilen[i].startswith(('#+NAME:', '#+CAPTION:')):
            j, name, nr = i, None, None
            while j < len(zeilen) and zeilen[j].startswith('#+'):
                if zeilen[j].startswith('#+NAME:'):
                    name = zeilen[j][len('#+NAME:'):].strip()
                m = CAP_NR.match(zeilen[j])
                if m:
                    nr = m.group(1)
                j += 1
            if name and nr:
                karte[name] = nr
            i = j
        else:
            i += 1
    return karte


def verweise_aufloesen(text, pfad):
    """[[fig:white-rewire]] -> 3   (als schlichter Text, ohne Hyperlink)"""
    karte = nummern(text)

    def ersetzen(m):
        ziel = m.group(1)
        if ziel in karte:
            return karte[ziel]
        sys.stderr.write(f'  ! unaufgelöster Verweis in {os.path.basename(pfad)}: '
                         f'[[{ziel}]]\n')
        return m.group(0)

    return re.sub(r'\[\[((?:fig|tab):[^\]\[]+)\]\](?:\[[^\]]*\])?', ersetzen, text)


def org_aufbereiten(pfad, karte, literatur_raus=False):
    t = open(pfad, encoding='utf-8').read()
    t = ORG_MUELL.sub('', t)                      # Schlüsselwörter, die Pandoc durchreicht
    # Ohne ^:nil liest Pandoc den Unterstrich in Dateinamen als Tiefstellung:
    # aus stages_long_final.csv wird sonst stages_(longfinal).csv
    t = '#+OPTIONS: ^:nil\n' + t
    t = verweise_aufloesen(t, pfad)               # [[fig:x]] -> Nummer
    for alt, neu in karte.items():                # Abbildungspfade umbiegen
        t = t.replace('file:' + alt, 'file:' + neu)
    if literatur_raus:                            # im Gesamtdokument nur ein Verzeichnis
        t = re.sub(r'^\*\* Literatur\s*\n+#\+print_bibliography:\s*$', '',
                   t, flags=re.M)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.lstrip('\n')


def legenden_nach_oben(doc):
    """Pandoc setzt die Bildlegende unter die Abbildung. Tabellenlegenden stehen
    darüber — hier wird beides angeglichen, indem das Legendenabsatz vor den
    Abbildungsabsatz gezogen wird."""
    muster = re.compile(
        r'(<w:p><w:pPr><w:pStyle w:val="CaptionedFigure" ?/></w:pPr>.*?</w:p>)'
        r'(<w:p><w:pPr><w:pStyle w:val="ImageCaption" ?/></w:pPr>.*?</w:p>)',
        re.S)
    return muster.subn(lambda m: m.group(2) + m.group(1), doc)


# Satzspiegel A4 mit 2,5 cm Rändern, in Twips
TEXTBREITE = 11906 - 2 * 1418
ZEICHEN    = 100    # Näherung: ein Zeichen in 10 pt Times ≈ 100 Twips
POLSTER    = 200    # Zellenrand links + rechts
SCHMAL     = 1500   # bis hierhin gilt eine Spalte als schmal und behält ihre Breite
MINDEST    = 700


def spaltenbreiten(tabelle_xml):
    """Spaltenbreiten aus dem Inhalt ableiten: schmale Spalten (Zahlen, kurze
    Wörter) behalten ihre natürliche Breite, die Textspalten teilen sich den
    Rest nach der Wurzel ihres Umfangs — so bekommt die Begründungsspalte den
    Platz, ohne dass die Zahlenspalten ihn verschwenden."""
    zeilen = re.findall(r'<w:tr>.*?</w:tr>', tabelle_xml, re.S)
    if not zeilen:
        return None
    natur = []
    for tr in zeilen:
        for i, tc in enumerate(re.findall(r'<w:tc>.*?</w:tc>', tr, re.S)):
            text = re.sub(r'<[^>]+>', '', tc)
            wort = max((len(w) for w in text.split()), default=1)
            breite = max(len(text), wort) * ZEICHEN + POLSTER
            if i < len(natur):
                natur[i] = max(natur[i], breite)
            else:
                natur.append(breite)
    if not natur:
        return None

    fest = {i: b for i, b in enumerate(natur) if b <= SCHMAL}
    frei = [i for i in range(len(natur)) if i not in fest]
    if not frei:                                   # alle Spalten schmal
        summe = sum(natur)
        if summe >= TEXTBREITE:
            return [max(MINDEST, round(b * TEXTBREITE / summe)) for b in natur]
        return natur

    rest = TEXTBREITE - sum(fest.values())
    gewicht = {i: math.sqrt(natur[i]) for i in frei}
    gsumme = sum(gewicht.values())
    breiten = []
    for i in range(len(natur)):
        if i in fest:
            breiten.append(fest[i])
        else:
            breiten.append(max(MINDEST, round(rest * gewicht[i] / gsumme)))
    # Rundungsrest auf die breiteste Spalte legen
    diff = TEXTBREITE - sum(breiten)
    breiten[breiten.index(max(breiten))] += diff
    return breiten


def tabellen_nachbearbeiten(docx):
    """Was Pandoc beim Schreiben der Tabellen fest verdrahtet und was sich
    deshalb nicht über die Formatvorlage steuern lässt:
      * <w:jc w:val="start"/>  ->  zentriert
      * Zellenabsätze auf das Format 'TabellenText' (10 pt, einzeilig,
        kein Abstand nach dem Absatz) statt 'Compact'
      * nach jeder Tabelle eine Leerzeile, damit der Text nicht anklebt
    """
    import zipfile
    with zipfile.ZipFile(docx) as z:
        namen = z.namelist()
        inhalt = {n: z.read(n) for n in namen}
    doc = inhalt['word/document.xml'].decode('utf-8')

    leerzeile = '<w:p><w:pPr><w:pStyle w:val="Leerzeile"/></w:pPr></w:p>'

    def eine_tabelle(m):
        t = m.group(0)
        t = t.replace('<w:jc w:val="start" />', '<w:jc w:val="center" />')
        t = t.replace('<w:jc w:val="start"/>', '<w:jc w:val="center"/>')
        t = t.replace('<w:pStyle w:val="Compact" />', '<w:pStyle w:val="TabellenText" />')
        t = t.replace('<w:pStyle w:val="Compact"/>', '<w:pStyle w:val="TabellenText"/>')
        br = spaltenbreiten(t)
        if br:
            raster = ''.join(f'<w:gridCol w:w="{b}" />' for b in br)
            t = re.sub(r'<w:tblGrid>.*?</w:tblGrid>',
                       f'<w:tblGrid>{raster}</w:tblGrid>', t, flags=re.S)
            t = t.replace('<w:tblW w:type="auto" w:w="0" />',
                          f'<w:tblW w:type="dxa" w:w="{sum(br)}" />')
            # Zellbreiten mitschreiben, sonst rechnet Word neu
            i = [0]
            def zelle(mm):
                b = br[i[0] % len(br)]; i[0] += 1
                s = mm.group(0)
                tcpr = f'<w:tcPr><w:tcW w:type="dxa" w:w="{b}" /></w:tcPr>'
                if '<w:tcPr />' in s:
                    return s.replace('<w:tcPr />', tcpr, 1)
                if '<w:tcPr/>' in s:
                    return s.replace('<w:tcPr/>', tcpr, 1)
                return s.replace('<w:tc>', '<w:tc>' + tcpr, 1)
            t = re.sub(r'<w:tc>.*?</w:tc>', zelle, t, flags=re.S)
        return t + leerzeile

    doc, anzahl = re.subn(r'<w:tbl>.*?</w:tbl>', eine_tabelle, doc, flags=re.S)
    doc, _ = legenden_nach_oben(doc)
    inhalt['word/document.xml'] = doc.encode('utf-8')

    with zipfile.ZipFile(docx, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in namen:
            z.writestr(n, inhalt[n])
    return anzahl


def nach_odt(docx, ziel_verz):
    """ODT aus dem bereits formatierten DOCX ableiten — so bleibt das Layout erhalten.
    (Eine reference.docx wirkt nicht auf Pandocs ODT-Ausgabe.)"""
    if not hat('soffice'):
        sys.stderr.write('soffice fehlt — ODT übersprungen.\n')
        return False
    return lauf(['soffice', '--headless', '--convert-to', 'odt',
                 docx, '--outdir', ziel_verz])


def pandoc_aufruf(eingaben, ziel, quelle, ref, extra=()):
    cmd = ['pandoc', *eingaben,
           '--from=org', '--citeproc',
           f'--bibliography={os.path.join(quelle, BIB)}',
           f'--csl={os.path.join(quelle, CSL)}',
           f'--resource-path={quelle}',
           '--metadata=lang:de-DE',
           '--dpi=300',
           *extra,
           '-o', ziel]
    if ziel.endswith('.docx'):
        cmd.insert(-2, f'--reference-doc={ref}')
    if not lauf(cmd):
        return False
    if ziel.endswith('.docx'):
        tabellen_nachbearbeiten(ziel)
    return True


# --------------------------------------------------------------------- Hauptlauf
def main():
    ap = argparse.ArgumentParser(description='Buchkapitel nach DOCX/ODT konvertieren')
    ap.add_argument('--quelle', default=os.path.join(HIER, '..', 'buch'))
    ap.add_argument('--ziel',   default=os.path.join(HIER, '..', 'ausgabe'))
    ap.add_argument('--referenz', default=os.path.join(HIER, 'reference.docx'))
    ap.add_argument('--only', default=None, help='nur Dateien, die diesen Text enthalten')
    ap.add_argument('--book', action='store_true', help='zusätzlich ein Gesamtdokument')
    ap.add_argument('--odt',  action='store_true', help='zusätzlich ODT erzeugen')
    ap.add_argument('--pdf',  action='store_true', help='zusätzlich PDF erzeugen')
    a = ap.parse_args()

    quelle = os.path.abspath(a.quelle)
    ziel   = os.path.abspath(a.ziel)
    ref    = os.path.abspath(a.referenz)

    if not hat('pandoc'):
        sys.exit('pandoc wurde nicht gefunden.')
    if not os.path.isdir(quelle):
        sys.exit(f'Quellverzeichnis fehlt: {quelle}')

    if not os.path.exists(ref):
        skript = os.path.join(HIER, 'make_reference_docx.py')
        if not os.path.exists(skript):
            sys.exit(f'Weder {ref} noch make_reference_docx.py vorhanden.')
        print('Formatvorlage wird erzeugt …')
        lauf([sys.executable, skript, ref])

    os.makedirs(ziel, exist_ok=True)
    cache = os.path.join(quelle, '_build', 'media')

    print('Abbildungen werden aufbereitet …')
    karte = medien_aufbereiten(quelle, cache)
    print(f'  {len(karte)} Abbildungen bereit')

    dateien = sorted(f for f in os.listdir(quelle) if f.endswith('.org'))
    if a.only:
        dateien = [f for f in dateien if a.only in f]
    if not dateien:
        sys.exit('Keine passenden .org-Dateien gefunden.')

    tmp = os.path.join(quelle, '_build', 'org')
    os.makedirs(tmp, exist_ok=True)

    print('Kapitel werden konvertiert …')
    ok = 0
    for f in dateien:
        vor = os.path.join(tmp, f)
        open(vor, 'w', encoding='utf-8').write(
            org_aufbereiten(os.path.join(quelle, f), karte))
        stamm = os.path.splitext(f)[0]
        aus = os.path.join(ziel, stamm + '.docx')
        if pandoc_aufruf([vor], aus, quelle, ref):
            print(f'  ✓ {stamm}.docx'); ok += 1
            if a.odt and nach_odt(aus, ziel):
                print(f'  ✓ {stamm}.odt')

    if a.book:
        print('Gesamtdokument …')
        teile = []
        for f in dateien:
            vor = os.path.join(tmp, '_buch_' + f)
            open(vor, 'w', encoding='utf-8').write(
                org_aufbereiten(os.path.join(quelle, f), karte, literatur_raus=True))
            teile.append(vor)
        aus = os.path.join(ziel, 'TR-Twin-Buch.docx')
        extra = ['--toc', '--toc-depth=3',
                 '--metadata=title:Der digitale Zwilling der Theorie der Relation',
                 '--metadata=author:Christian Papilloud']
        if pandoc_aufruf(teile, aus, quelle, ref, extra):
            print('  ✓ TR-Twin-Buch.docx')
            if a.odt and nach_odt(aus, ziel):
                print('  ✓ TR-Twin-Buch.odt')

    if a.pdf:
        if not hat('soffice'):
            sys.stderr.write('soffice fehlt — PDF übersprungen.\n')
        else:
            print('PDF …')
            for f in sorted(os.listdir(ziel)):
                if f.endswith('.docx'):
                    lauf(['soffice', '--headless', '--convert-to', 'pdf',
                          os.path.join(ziel, f), '--outdir', ziel])

    print(f'\nFertig: {ok}/{len(dateien)} Kapitel in {ziel}')


if __name__ == '__main__':
    main()
