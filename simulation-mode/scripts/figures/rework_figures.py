#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figuren_ueberarbeiten.py — überarbeitet die älteren SVG-Abbildungen der
Kapitel 2 bis 10.

Diese Abbildungen liegen als fertige SVG-Dateien im Repository; ihre
Erzeugerskripte sind nur teilweise erhalten. Das Skript arbeitet deshalb
unmittelbar auf den Dateien und nimmt dieselben Änderungen vor, die
figuren_kap11.py für Kapitel 11 im Code vornimmt:

  1. Titelzeile oben (grau, klein) entfernen — der Titel steht in der Legende
  2. lange Erläuterungszeile am unteren Rand entfernen — sie wiederholt den
     Kapiteltext; kurze technische Zusätze bleiben, rücken aber ab
  3. Schriftgrade um Faktor 1,45 anheben, Mindestwert 14 Einheiten
     (im 15-cm-Satz rund 8 pt)
  4. verbliebene graue Beschriftung auf Schwarz setzen
  5. Legenden auf halbe Höhe an den rechten Rand, weiß hinterlegt
  6. übereinanderliegende Beschriftungen auseinanderrücken, Zeichenfläche
     bei Bedarf vergrößern

    python3 figuren_ueberarbeiten.py <figures-Verzeichnis>
    python3 figuren_ueberarbeiten.py <figures-Verzeichnis> --probe
"""
import glob, os, re, sys

FAKTOR   = 1.45
MINDEST  = 15
GRAUTOENE = {'#777', '#777777', '#9a9a9a', '#999', '#888'}


def breite(s, size):
    schmal = set("iljtfrI.,:;'| ")
    return sum(size * (0.34 if c in schmal else 0.56) for c in str(s))


# ---------------------------------------------------------------- Zerlegung
TEXT = re.compile(r'<text([^>]*)>(.*?)</text>', re.S)


def attr(s, name, standard=None):
    m = re.search(name + r'="([^"]*)"', s)
    return m.group(1) if m else standard


def setz(s, name, wert):
    if re.search(name + r'="[^"]*"', s):
        return re.sub(name + r'="[^"]*"', f'{name}="{wert}"', s)
    return s + f' {name}="{wert}"'


def masse(svg):
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1).split()
    return float(vb[2]), float(vb[3])


def setze_masse(svg, W, H):
    svg = re.sub(r'viewBox="[^"]+"', f'viewBox="0 0 {W:.0f} {H:.0f}"', svg)
    svg = re.sub(r'(<rect[^>]*width=")\d+(\"[^>]*height=")\d+(\"[^>]*fill="#(?:fff|ffffff)"[^>]*/>)',
                 lambda m: f'{m.group(1)}{W:.0f}{m.group(2)}{H:.0f}{m.group(3)}', svg, count=1)
    return svg


# ------------------------------------------------------------------ Schritte
def titelzeile_weg(svg):
    """Die graue Zeile ganz oben (y zwischen 40 und 56) ist der Titel."""
    def raus(m):
        a, inhalt = m.group(1), m.group(2)
        y = float(attr(a, 'y', 0))
        fill = (attr(a, 'fill', '') or '').lower()
        if y <= 58 and fill in GRAUTOENE and len(inhalt) > 25:
            return ''
        return m.group(0)
    return TEXT.sub(raus, svg)


def fusszeile_weg(svg):
    """Lange Erläuterungszeile am unteren Rand entfernen."""
    W, H = masse(svg)
    def raus(m):
        a, inhalt = m.group(1), m.group(2)
        y = float(attr(a, 'y', 0))
        if y > H - 45 and len(inhalt) > 55:
            return ''
        return m.group(0)
    return TEXT.sub(raus, svg)


def schrift_anheben(svg):
    def gross(m):
        alt = float(m.group(1))
        return f'font-size="{max(MINDEST, round(alt * FAKTOR, 1))}"'
    return re.sub(r'font-size="([\d.]+)"', gross, svg)


def grau_zu_schwarz(svg):
    """Beschriftung, die stehen bleibt, muss lesbar sein."""
    def dunkler(m):
        a, inhalt = m.group(1), m.group(2)
        fill = (attr(a, 'fill', '') or '').lower()
        if fill in ('#777', '#777777', '#888'):
            a = setz(a, 'fill', '#2b2b2b')
        elif fill in ('#999', '#9a9a9a'):
            a = setz(a, 'fill', '#666')          # Achsenzahlen bleiben zurückhaltend
        return f'<text{a}>{inhalt}</text>'
    return TEXT.sub(dunkler, svg)


def kaesten(svg):
    """Bounding-Boxen aller Texte."""
    out = []
    for m in TEXT.finditer(svg):
        a, inhalt = m.group(1), m.group(2)
        if not inhalt.strip() or 'rotate' in (attr(a, 'transform', '') or ''):
            continue
        x, y = float(attr(a, 'x', 0)), float(attr(a, 'y', 0))
        sz = float(attr(a, 'font-size', 16))
        an = attr(a, 'text-anchor', 'start')
        w = breite(inhalt, sz)
        x0 = x if an == 'start' else (x - w / 2 if an == 'middle' else x - w)
        out.append(dict(span=m.span(), x=x, y=y, sz=sz, w=w,
                        x0=x0, x1=x0 + w, y0=y - sz * 0.8, y1=y + sz * 0.22,
                        text=inhalt))
    return out


def auseinander(svg, runden=8):
    """Übereinanderliegende Beschriftungen nach unten schieben."""
    for _ in range(runden):
        ks = kaesten(svg)
        verschiebung = {}
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, c = ks[i], ks[j]
                ux = min(a['x1'], c['x1']) - max(a['x0'], c['x0'])
                uy = min(a['y1'], c['y1']) - max(a['y0'], c['y0'])
                if ux > 2 and uy > 2:
                    unten = c if c['y'] >= a['y'] else a
                    verschiebung[unten['span']] = max(
                        verschiebung.get(unten['span'], 0), uy + 3)
        if not verschiebung:
            break
        neu, letzte = [], 0
        for k in sorted(ks, key=lambda z: z['span'][0]):
            s0, s1 = k['span']
            neu.append(svg[letzte:s0])
            stueck = svg[s0:s1]
            if k['span'] in verschiebung:
                stueck = re.sub(r'y="[\d.]+"',
                                f'y="{k["y"] + verschiebung[k["span"]]:.1f}"',
                                stueck, count=1)
            neu.append(stueck)
            letzte = s1
        neu.append(svg[letzte:])
        svg = ''.join(neu)
    return svg


def umbrechen(svg, rand=16):
    """Zeilen, die nicht auf die Fläche passen, auf zwei bis drei Zeilen
    verteilen — besser als die Zeichenfläche zu verbreitern, weil die Schrift
    sonst im Verhältnis wieder schrumpft."""
    W, H = masse(svg)
    for _ in range(6):
        ks = kaesten(svg)
        ziel = None
        for k in ks:
            if k['w'] > W - 2 * rand and ' ' in k['text'].strip():
                ziel = k
                break
        if not ziel:
            break
        worte = ziel['text'].split()
        teile = max(2, int(ziel['w'] // (W - 2 * rand)) + 1)
        pro = len(worte) / teile
        zeilen, i = [], 0
        for n in range(teile):
            j = len(worte) if n == teile - 1 else round(pro * (n + 1))
            zeilen.append(' '.join(worte[i:j]))
            i = j
        zeilen = [z for z in zeilen if z]
        s0, s1 = ziel['span']
        roh = svg[s0:s1]
        a = re.match(r'<text([^>]*)>', roh).group(1)
        neu = []
        for n, z in enumerate(zeilen):
            aa = re.sub(r'y="[\d.-]+"', f'y="{ziel["y"] + n * ziel["sz"] * 1.25:.1f}"',
                        a, count=1)
            neu.append(f'<text{aa}>{z}</text>')
        svg = svg[:s0] + '\n'.join(neu) + svg[s1:]
    return svg


def flaeche_anpassen(svg):
    """Zeichenfläche vergrößern, wenn Text über den Rand ragt."""
    W, H = masse(svg)
    ks = kaesten(svg)
    if not ks:
        return svg
    rechts = max(k['x1'] for k in ks)
    unten = max(k['y1'] for k in ks)
    links = min(k['x0'] for k in ks)
    nW = min(max(W, rechts + 12), W * 1.06)     # Fläche nur behutsam verbreitern
    nH = max(H, unten + 14)
    if links < 0:                       # nach rechts einrücken
        svg = re.sub(r'(<text[^>]*\bx=")(-?[\d.]+)',
                     lambda m: m.group(1) + f'{float(m.group(2)) - links + 8:.1f}', svg)
        nW += -links + 8
    if (nW, nH) != (W, H):
        svg = setze_masse(svg, nW, nH)
    return svg


def legende_nach_rechts(svg):
    """Legendenmarken (kleine Quadrate mit Text daneben) auf halbe Höhe an den
    rechten Rand versetzen und weiß hinterlegen."""
    W, H = masse(svg)
    marken = [m for m in re.finditer(
        r'<rect x="([\d.]+)" y="([\d.]+)" width="(1[0-2](?:\.0)?)" height="\3"[^>]*/>', svg)]
    if len(marken) < 2:
        return svg
    xs = [float(m.group(1)) for m in marken]
    ys = [float(m.group(2)) for m in marken]
    if max(xs) - min(xs) > 4:            # waagerechte Legende: in Ruhe lassen
        return svg
    if min(ys) > H * 0.45:               # steht schon nicht mehr oben
        return svg
    ks = kaesten(svg)
    beschriftung = [k for k in ks
                    if abs(k['x0'] - (min(xs) + 16)) < 26 and min(ys) - 6 <= k['y'] <= max(ys) + 22]
    if len(beschriftung) < len(marken):
        return svg
    bb_breite = max(k['x1'] for k in beschriftung) - min(xs) + 16
    bb_hoehe = max(ys) - min(ys) + 26
    dx = (W - 16 - bb_breite) - min(xs)
    dy = (H * 0.5 - bb_hoehe / 2) - min(ys)
    if abs(dx) < 2 and abs(dy) < 2:
        return svg
    for m in reversed(marken):
        alt = m.group(0)
        neu = alt.replace(f'x="{m.group(1)}"', f'x="{float(m.group(1))+dx:.1f}"')
        neu = neu.replace(f'y="{m.group(2)}"', f'y="{float(m.group(2))+dy:.1f}"', 1)
        svg = svg[:m.start()] + neu + svg[m.end():]
    for k in sorted(beschriftung, key=lambda z: -z['span'][0]):
        s0, s1 = k['span']
        stueck = svg[s0:s1]
        stueck = re.sub(r'x="[\d.-]+"', f'x="{k["x"]+dx:.1f}"', stueck, count=1)
        stueck = re.sub(r'y="[\d.-]+"', f'y="{k["y"]+dy:.1f}"', stueck, count=1)
        svg = svg[:s0] + stueck + svg[s1:]
    kasten = (f'<rect x="{min(xs)+dx-9:.1f}" y="{min(ys)+dy-9:.1f}" '
              f'width="{bb_breite+14:.1f}" height="{bb_hoehe+4:.1f}" '
              f'fill="#ffffff" stroke="#e7e7e7" rx="3"/>')
    erste = min(m.start() for m in marken) if dx == 0 else svg.find('<rect x="%.1f"' % (min(xs)+dx))
    svg = svg[:erste] + kasten + svg[erste:]
    return svg


def synthese_drei_neu():
    """Ohne die Pfeile trägt das alte Gerüst nicht mehr; die Abbildung wird
    deshalb als schlichtes Schema neu gesetzt: oben die beiden stabilen
    Regime, darunter die drei Übergänge als Liste."""
    W, H = 780, 430
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="Helvetica,Arial,sans-serif">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>']

    kaesten = [
        (40, '#46CDB8', '#2f9e8c', 'Symmetrische Reziprozität', 'das gemeinsame Ideal',
         ['Theorie der Relation (Ideal)', 'Habermas — kommunikatives Ideal',
          'Luhmann — das Darstellbare', 'Autonomie, keine Hierarchie']),
        (400, '#E36F9E', '#c45680', 'Einziger Apex', 'Satellisierung',
         ['Parsons — kybernetische Hierarchie', 'Habermas — Kolonialisierung',
          'ein Pol dominiert,', 'drei Satelliten']),
    ]
    for x, farbe, titel_farbe, titel, unter, zeilen in kaesten:
        s.append(f'<rect x="{x}" y="34" width="340" height="196" rx="12" '
                 f'fill="{farbe}" opacity="0.10" stroke="{farbe}"/>')
        cx = x + 170
        s.append(f'<text x="{cx}" y="66" font-size="19" font-family="Georgia,serif" '
                 f'fill="{titel_farbe}" text-anchor="middle">{titel}</text>')
        s.append(f'<text x="{cx}" y="88" font-size="15" fill="#2b2b2b" '
                 f'text-anchor="middle">{unter}</text>')
        y = 126
        for z in zeilen:
            s.append(f'<text x="{cx}" y="{y}" font-size="16" fill="#2b2b2b" '
                     f'text-anchor="middle">{z}</text>')
            y += 26

    s.append('<line x1="40" y1="264" x2="740" y2="264" stroke="#e7e7e7"/>')
    s.append('<text x="40" y="292" font-size="16" fill="#2b2b2b">'
             'Die drei Übergänge zwischen den beiden Regimen</text>')
    uebergaenge = [
        ('Parsons', '#2b2b2b', 'Hierarchie führt zum Apex — darstellbar, mit innerer Spannung'),
        ('Luhmann', '#8C92EC', 'operative Schließung fällt in die Symmetrie zurück — nicht darstellbar'),
        ('Habermas', '#E36F9E', 'die Bipolarität von System und Lebenswelt kippt in den Apex — nicht darstellbar'),
    ]
    y = 322
    for name, farbe, text in uebergaenge:
        s.append(f'<rect x="40" y="{y-13}" width="6" height="16" fill="{farbe}" rx="2"/>')
        s.append(f'<text x="56" y="{y}" font-size="16" font-family="Georgia,serif" '
                 f'fill="#2b2b2b">{name}</text>')
        s.append(f'<text x="152" y="{y}" font-size="15" fill="#2b2b2b">{text}</text>')
        y += 30
    s.append('</svg>')
    return '\n'.join(s)



# ------------------------------------------------------------- Sonderfälle
# Was die allgemeine Behandlung nicht auflösen kann, steht hier je Datei.
# Die Koordinaten beziehen sich auf den Stand nach dem Anheben der Schrift.

def _setz_y(svg, inhalt_muster, y):
    m = re.search(r'<text[^>]*>' + inhalt_muster + r'</text>', svg)
    if not m:
        raise SystemExit('Sonderfall greift nicht mehr: ' + inhalt_muster)
    return svg[:m.start()] + re.sub(r'y="[\d.]+"', f'y="{y}"', m.group(0), count=1) + svg[m.end():]


def sf_donati(svg):
    """Die Kennzahl zur gestrichelten Linie lag über der Säule M."""
    svg = re.sub(r'<text[^>]*>R\(System\)=0\.32</text>\n?', '', svg)
    return svg.replace('</svg>',
        '<line x1="155" y1="60" x2="187" y2="60" stroke="#c0392b" '
        'stroke-width="1" stroke-dasharray="4,3"/>\n'
        '<text x="195" y="65" font-size="15" fill="#c0392b">R(System) = 0.32</text>\n'
        '</svg>')


def sf_fuhse(svg):
    """Kennzahlen von der Säulenspitze abrücken, Fußbeschriftung zweizeilig."""
    spitzen = {'187': 263.3, '291': 129.4, '395': 168.8, '499': 258.4}
    def r_hoch(m):
        x = m.group(1).split('.')[0]
        return re.sub(r'y="[\d.]+"', f'y="{spitzen[x] - 13:.1f}"', m.group(0), count=1)
    svg = re.sub(r'<text x="(187|291|395|499)(?:\.0)?" y="[\d.]+"[^>]*>R=[\d.]+</text>',
                 r_hoch, svg)
    def p_hoch(m):
        x = m.group(1).split('.')[0]
        return re.sub(r'y="[\d.]+"', f'y="{spitzen[x] - 36:.1f}"', m.group(0), count=1)
    svg = re.sub(r'<text x="(187|291|395|499)\.0" y="[\d.]+"[^>]*>\d+%</text>', p_hoch, svg)
    for x, unten in (('291.0', 'Politik'), ('395.0', 'Wirtschaft'), ('499.0', 'Kultur')):
        muster = re.compile(r'<text x="' + re.escape(x) + r'" y="376\.0"([^>]*)>Sinn → '
                            + unten + r'</text>')
        m = muster.search(svg)
        if not m:
            raise SystemExit('Sonderfall greift nicht mehr: fuhse ' + unten)
        a = m.group(1)
        svg = svg[:m.start()] + (
            f'<text x="{x}" y="376.0"{a}>Sinn →</text>\n'
            f'<text x="{x}" y="394.3"{a}>{unten}</text>') + svg[m.end():]
    return svg


def sf_habermas_bifurkation(svg):
    """Die rechte Beschriftung lag auf der Kurve; beide stehen jetzt auf
    gleicher Höhe über ihrem Feld."""
    svg = _setz_y(svg, r'einziger Apex \(Satellisierung\)', 64)
    return _setz_y(svg, r'symmetrische Reziprozität', 64)


def sf_habermas_ideal(svg):
    """Panelüberschriften kleiner und zweizeilig."""
    titel = [(r'Habermas — kommunikatives Ideal', 'Habermas —', 'kommunikatives Ideal'),
             (r'Kolonialisierung — Ketten auf B \(Macht\)', 'Kolonialisierung',
              'Ketten auf B (Macht)'),
             (r'Kolonialisierung — Ketten auf C \(Geld\)', 'Kolonialisierung',
              'Ketten auf C (Geld)')]
    for muster, oben, unten in titel:
        m = re.search(r'<text([^>]*)>' + muster + r'</text>', svg)
        if not m:
            raise SystemExit('Sonderfall greift nicht mehr: ' + oben)
        a = re.sub(r'font-size="[\d.]+"', 'font-size="16"', m.group(1))
        svg = svg[:m.start()] + (
            f'<text{re.sub(chr(121)+chr(61)+chr(34)+r"[0-9.]+"+chr(34), chr(121)+chr(61)+chr(34)+"50"+chr(34), a, count=1)}>{oben}</text>\n'
            f'<text{re.sub(chr(121)+chr(61)+chr(34)+r"[0-9.]+"+chr(34), chr(121)+chr(61)+chr(34)+"70"+chr(34), a, count=1)}>{unten}</text>'
        ) + svg[m.end():]
    return svg


def sf_parsons_trajektorie(svg):
    """Die beiden Schwellenmarken standen auf verschiedener Höhe."""
    return _setz_y(svg, r'Politik 75 % \(Schritt 655\)', 66)


def sf_kaskade(svg):
    """Die schwarze Marke steht bei allen sechs Rahmen; die Legende erklärt sie
    bereits. Die beiden vereinzelten Jahreszahlen entfallen."""
    return re.sub(r'<text[^>]*>1819</text>\n?', '', svg)


def sf_tilly(svg):
    """Lesbarkeit der Kopfzeile, freistehende Beschriftung, erklärte Migration."""
    # Der Kasten war schmaler als seine Beschriftung.
    svg = svg.replace(
        '<rect x="270" y="80" width="180" height="64" rx="6" fill="#E36F9E" opacity="0.92"/>',
        '<rect x="240" y="80" width="240" height="64" rx="6" fill="#E36F9E" '
        'opacity="0.16" stroke="#E36F9E"/>')
    svg = svg.replace('fill="#fff"', 'fill="#2b2b2b"')
    # Die Beschriftung lag unter drei Pfeilen; sie rückt über die Grenzlinie.
    m = re.search(r'<text([^>]*)>Ausbeutung: Wert fließt nach oben ↑</text>', svg)
    if not m:
        raise SystemExit('Sonderfall greift nicht mehr: Ausbeutung')
    a = re.sub(r'x="[\d.]+"', 'x="20"', m.group(1), count=1)
    a = re.sub(r'fill="#\w+"', 'fill="#2b2b2b"', a)
    zeilen = ['Ausbeutung:', 'Wert fließt', 'nach oben ↑']
    gestapelt = '\n'.join(
        f'<text{re.sub(chr(121)+chr(61)+chr(34)+r"[0-9.]+"+chr(34), chr(121)+chr(61)+chr(34)+str(196+18*i)+chr(34), a, count=1)}>{z}</text>'
        for i, z in enumerate(zeilen))
    svg = svg[:m.start()] + gestapelt + svg[m.end():]
    # Der gebogene Pfeil wird gerade gezogen.
    svg = re.sub(r'<path d="M180,330 q40,40 360,0"', '<path d="M180,340 L540,340"', svg)
    # Die gestrichelte Kurve war unbeschriftet, die Fußzeile zu lang.
    m = re.search(r'<text([^>]*)>Individuen migrieren \(graue Punkte\)[^<]*</text>', svg)
    if not m:
        raise SystemExit('Sonderfall greift nicht mehr: Migration')
    a = re.sub(r'fill="#\w+"', 'fill="#2b2b2b"', m.group(1))
    svg = svg[:m.start()] + (
        f'<text{re.sub(chr(121)+chr(61)+chr(34)+r"[0-9.]+"+chr(34), chr(121)+chr(61)+chr(34)+"370"+chr(34), a, count=1)}>'
        'einzelne Individuen (graue Punkte) wechseln die Kategorie</text>\n'
        f'<text{re.sub(chr(121)+chr(61)+chr(34)+r"[0-9.]+"+chr(34), chr(121)+chr(61)+chr(34)+"404"+chr(34), a, count=1)}>'
        'Die Grenze bleibt und füllt die begünstigte Kategorie immer wieder auf.</text>'
    ) + svg[m.end():]
    return svg


SONDERFAELLE = {
    'donati_emergenz.svg': sf_donati,
    'fuhse_sinn.svg': sf_fuhse,
    'habermas_bifurkation.svg': sf_habermas_bifurkation,
    'habermas_ideal_kolonisierung.svg': sf_habermas_ideal,
    'kaskade_typologie.svg': sf_kaskade,
    'parsons_trajektorie.svg': sf_parsons_trajektorie,
    'tilly_mechanismus.svg': sf_tilly,
}


# ------------------------------------------------------------------ Hauptlauf
def ueberarbeiten(pfad, probe=False):
    svg = open(pfad, encoding='utf-8').read()
    name = os.path.basename(pfad)
    if name == 'synthese_drei.svg':
        open(pfad, 'w', encoding='utf-8').write(synthese_drei_neu())
        return synthese_drei_neu()
    svg = titelzeile_weg(svg)
    svg = fusszeile_weg(svg)
    svg = schrift_anheben(svg)
    svg = grau_zu_schwarz(svg)
    if name in SONDERFAELLE:
        svg = SONDERFAELLE[name](svg)
    svg = legende_nach_rechts(svg)
    svg = umbrechen(svg)
    svg = auseinander(svg)
    svg = flaeche_anpassen(svg)
    svg = auseinander(svg)
    svg = re.sub(r'\n{2,}', '\n', svg)
    if not probe:
        open(pfad, 'w', encoding='utf-8').write(svg)
    return svg


def main():
    verz = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'figures')
    probe = '--probe' in sys.argv
    dateien = [f for f in sorted(glob.glob(os.path.join(verz, '*.svg')))
               if not os.path.basename(f).startswith('wk_abb')]
    for f in dateien:
        ueberarbeiten(f, probe)
        print('  ✓', os.path.basename(f))
    print(f"\n{len(dateien)} Abbildungen überarbeitet"
          + (' (Probelauf, nichts geschrieben)' if probe else ''))


if __name__ == '__main__':
    main()
