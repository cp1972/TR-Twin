# Konvertierung der Buchkapitel nach DOCX / ODT

## Aufbau

```
buch/          die .org-Dateien, Bericht.bib, die .csl-Dateien, figures/
build/         make_reference_docx.py, build.py, reference.docx, README.md
ausgabe/       Ergebnis (wird angelegt)
```

`build.py` erwartet diese Nachbarschaft. Andere Pfade lassen sich über
`--quelle` und `--ziel` setzen.

## Aufruf

```bash
python3 build/renumber.py              # Abbildungen und Tabellen nummerieren
python3 build/build.py                 # ein DOCX je Kapitel
python3 build/build.py --book          # zusätzlich ein Gesamtdokument mit Inhaltsverzeichnis
python3 build/build.py --odt           # zusätzlich ODT
python3 build/build.py --pdf           # zusätzlich PDF (Kontrollansicht)
python3 build/build.py --only kapitel-05
```

Das ODT wird aus dem fertig formatierten DOCX abgeleitet, nicht direkt von
Pandoc erzeugt — eine `reference.docx` wirkt nämlich nicht auf Pandocs
ODT-Ausgabe, und der Umweg über LibreOffice erhält das Layout eins zu eins.

## Voraussetzungen

| Programm | wofür | nötig? |
|---|---|---|
| `pandoc` ≥ 3.0 | Konvertierung | ja |
| `rsvg-convert` *oder* `cairosvg` *oder* `inkscape` *oder* `soffice` | SVG → PNG | ja, sobald SVG-Abbildungen vorkommen |
| `soffice` (LibreOffice) | ODT und PDF | nur für `--odt` / `--pdf` |
| Python-Paket `Pillow` | physische Bildbreite setzen | empfohlen |

Unter Debian/Ubuntu:

```bash
sudo apt install pandoc librsvg2-bin libreoffice python3-pil
```

## Was das Skript macht

1. **Abbildungen** — jede SVG-Datei aus `figures/` wird nach PNG gerendert
   (Zielbreite 15 cm bei 300 dpi); vorhandene PNG-Dateien bekommen dieselbe
   physische Breite über ihre DPI-Angabe. Ergebnis liegt im Cache
   `buch/_build/media/`; die Originale bleiben unberührt. Der Cache kann
   jederzeit gelöscht werden und wird neu aufgebaut.
2. **Org-Vorverarbeitung** — `#+STARTUP:` und `#+CITE_EXPORT:` werden entfernt,
   weil Pandoc sie sonst als Rohtext ins Dokument schreibt. Die Bildpfade
   werden auf den Cache umgebogen. Im Gesamtdokument entfallen zusätzlich die
   kapitelweisen `** Literatur`-Abschnitte, damit nur ein Verzeichnis am Ende
   steht.
3. **Unterstriche** — `#+OPTIONS: ^:nil` wird vorangestellt, sonst liest
   Pandoc den Unterstrich in Dateinamen als Tiefstellung und macht aus
   `stages_long_final.csv` ein `stages_(longfinal).csv`.
4. **Querverweise** — `[[fig:white-rewire]]` im Fließtext wird durch die
   Nummer ersetzt, die im zugehörigen `#+CAPTION`-Präfix steht. Beide stammen
   damit aus derselben Quelle und können nicht auseinanderlaufen. Ein Verweis
   auf einen unbekannten Namen wird gemeldet und unverändert gelassen.
5. **Pandoc** mit `--citeproc`, `Bericht.bib` und
   `chicago-author-date-de-ibid.csl`, dazu `reference.docx` als Formatvorlage.
6. **Nachbearbeitung der Tabellen** — drei Dinge schreibt Pandoc fest ins
   Dokument, sie lassen sich deshalb nicht über die Formatvorlage steuern:
   die Tabellen werden zentriert (Pandoc setzt `jc="start"`), die
   Zellenabsätze bekommen das Format *Tabellentext* statt *Compact*
   (10 pt, einzeilig, kein Abstand nach dem Absatz), und nach jeder Tabelle
   wird eine Leerzeile eingefügt.

## Abbildungen

Zwei Skripte, weil die Abbildungen aus zwei Quellen stammen:

* `figuren_kap11.py` zeichnet die zehn Abbildungen des Kapitels 11 aus den
  Daten neu (zusammen mit `tr_svg.py`, das das Raster der Kapitel 2 bis 9
  bereitstellt). Änderungen an Schriftgraden, Farben und Legendenlage gehören
  in `tr_svg.py`.
* `figuren_ueberarbeiten.py` arbeitet auf den fertigen SVG-Dateien der
  Kapitel 2 bis 10. Deren Erzeugerskripte sind nur teilweise erhalten, deshalb
  wird dort unmittelbar an der Datei gearbeitet. **Das Skript ist nicht
  wiederholbar** — ein zweiter Lauf würde die Schrift ein zweites Mal
  vergrößern. Vor einem erneuten Lauf die Originale aus dem Repository
  zurückholen.

Beide setzen dieselben Regeln um: kein Titel im Bild, Randnotizen nur wo
nötig und dann schwarz, Legende auf halber Höhe rechts mit weißer
Hinterlegung, kleinste Schrift im 15-cm-Satz nicht unter 7,5 pt, deutlicher
Abstand zwischen Bild und Achsenbeschriftung.

`pruefe_svg.py` prüft eine Abbildung maschinell: Text über dem Rand,
übereinanderliegende Beschriftungen, zu kleine Schrift.

## Nummerierung von Abbildungen und Tabellen

`renumber.py` zählt je Kapitel getrennt und jeweils ab 1, in der Reihenfolge
des Auftretens, und schreibt das Ergebnis in die Legende:

```org
#+NAME: fig:white-rewire
#+CAPTION: *Abbildung 3.* Bei Veränderung der netzwerkartigen Struktur …
```

Der fette Teil entsteht aus dem `*…*` und wird von Pandoc übernommen.
Ein bereits vorhandenes Präfix wird ersetzt — das Skript lässt sich also nach
jeder Einfügung oder Umstellung erneut laufen. Die Verweise im Fließtext
bleiben dabei symbolisch (`[[fig:white-rewire]]`) und müssen nie von Hand
angefasst werden.

`python3 build/renumber.py --pruefen` zeigt nur an, was sich ändern würde.

Ob eine Legende zu einer Tabelle oder zu einer Abbildung gehört, entscheidet
das Skript daran, was auf den Block folgt (`|` oder `[[file:…]]`), nicht am
Namenspräfix — ein falsch benanntes `#+NAME:` fällt also nicht ins Gewicht.

## Formatvorlage

`reference.docx` entsteht aus `make_reference_docx.py`. Fehlt sie, erzeugt
`build.py` sie beim ersten Lauf selbst. Sie setzt:

* Times New Roman 11 pt, Zeilenabstand 1,5, Blocksatz, A4, Ränder 2,5 cm
* Überschriften schwarz, Times New Roman, linksbündig (H1 16 pt, H2 13 pt,
  H3 12 pt, H4/H5 11 pt kursiv)
* Abbildungen und Tabellen zentriert
* Tabellen im Booktabs-Satz: Linie oben, Linie unter der Kopfzeile, Linie
  unten, keine Senkrechten, keine Schattierung, Kopfzeile fett, 10 pt —
  der bei Springer VS übliche Satz
* Tabellenüberschriften über, Abbildungsunterschriften unter dem Objekt,
  10 pt, einzeilig, linksbündig; die Marke („Tabelle 1.“, „Abbildung 3.“)
  fett
* eigenes Absatzformat *Tabellentext* für den Inhalt der Zellen — es lässt
  sich in Word direkt anpassen und gilt dann für alle Tabellen
* Literaturverzeichnis mit hängendem Einzug
* Blockzitate eingerückt, 10 pt, einzeilig
* Dokumentsprache `de-DE`

Die Stellschrauben stehen oben in `make_reference_docx.py` (`FONT`, `SIZE`,
`SIZE_SMALL`, `LINE`, `LANG`, `BILDBREITE_CM`). Nach einer Änderung:

```bash
rm build/reference.docx && python3 build/build.py
```

Wollen Sie Tabellen und Legenden ebenfalls 1,5-zeilig, ersetzen Sie in
`make_reference_docx.py` die betreffenden `w:line="240"` durch `w:line="360"`.
Für die Tabellen genügt es auch, in Word das Format *Tabellentext* zu ändern.

## Hinweise

* Das Inhaltsverzeichnis im Gesamtdokument ist ein Word-Feld. Word füllt die
  Seitenzahlen beim Öffnen bzw. nach `Strg+A` und `F9`; LibreOffice zeigt es
  zunächst ohne Zahlen an.
* `--pdf` dient nur der Sichtkontrolle. Für den Druck ist der Weg über die
  Satzvorlage des Verlags gedacht.
