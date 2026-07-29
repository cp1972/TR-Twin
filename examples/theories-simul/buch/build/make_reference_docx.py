#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_reference_docx.py — erzeugt die Formatvorlage reference.docx für Pandoc.

Layout:
  * Times New Roman 11 pt, Zeilenabstand 1,5, Blocksatz
  * A4, Ränder 2,5 cm
  * Abbildungen und Tabellen zentriert
  * Tabellen im Booktabs-Stil (Linie oben, unter der Kopfzeile, unten;
    keine Senkrechten, keine Schattierung) — der übliche Satz bei Springer VS
  * Bildunterschriften 10 pt, einzeilig, linksbündig
  * Literaturverzeichnis mit hängendem Einzug

Aufruf:  python3 make_reference_docx.py [ziel.docx]
"""
import os, re, shutil, subprocess, sys, tempfile, zipfile

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'reference.docx')

# ------------------------------------------------------------------ Stellschrauben
FONT       = 'Times New Roman'
SIZE       = 22    # halbe Punkt: 22 = 11 pt
SIZE_SMALL = 20    # 10 pt — Tabellen, Bildunterschriften, Blockzitate
LINE       = 360   # 240 = einzeilig, 360 = 1,5-zeilig
LANG       = 'de-DE'

RF   = (f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" '
        f'w:eastAsia="{FONT}" w:cs="{FONT}"/>')
SZ   = f'<w:sz w:val="{SIZE}"/><w:szCs w:val="{SIZE}"/>'
SZS  = f'<w:sz w:val="{SIZE_SMALL}"/><w:szCs w:val="{SIZE_SMALL}"/>'
LN   = f'<w:spacing w:line="{LINE}" w:lineRule="auto"/>'


def style(sid, name, custom=False, based=None, nxt=None, ppr='', rpr='', extra=''):
    c = ' w:customStyle="1"' if custom else ''
    s = [f'<w:style w:type="paragraph"{c} w:styleId="{sid}">',
         f'<w:name w:val="{name}"/>']
    if based: s.append(f'<w:basedOn w:val="{based}"/>')
    if nxt:   s.append(f'<w:next w:val="{nxt}"/>')
    s.append('<w:qFormat/>')
    if ppr: s.append(f'<w:pPr>{ppr}</w:pPr>')
    if rpr: s.append(f'<w:rPr>{rpr}</w:rPr>')
    s.append(extra)
    s.append('</w:style>')
    return ''.join(s)


def heading(sid, name, lvl, size, bold=True, italic=False, before=360, after=120):
    rpr = RF + f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:color w:val="000000"/>'
    if bold:   rpr += '<w:b/><w:bCs/>'
    if italic: rpr += '<w:i/><w:iCs/>'
    ppr = ('<w:keepNext/><w:keepLines/>'
           f'<w:spacing w:before="{before}" w:after="{after}" w:line="{LINE}" w:lineRule="auto"/>'
           '<w:jc w:val="left"/>'
           f'<w:outlineLvl w:val="{lvl}"/>')
    return style(sid, name, based='Normal', nxt='BodyText', ppr=ppr, rpr=rpr)


# ------------------------------------------------------------------ Absatzformate
STYLES = {

  'Normal': style('Normal', 'Normal', ppr=f'<w:jc w:val="both"/>{LN}'
                  '<w:spacing w:before="0" w:after="0" '
                  f'w:line="{LINE}" w:lineRule="auto"/>',
                  rpr=RF + SZ + f'<w:lang w:val="{LANG}"/>')
             .replace('<w:style w:type="paragraph"',
                      '<w:style w:type="paragraph" w:default="1"'),

  'BodyText': style('BodyText', 'Body Text', based='Normal',
                    ppr=f'<w:spacing w:before="0" w:after="160" w:line="{LINE}" w:lineRule="auto"/>'
                        '<w:jc w:val="both"/>',
                    extra='<w:link w:val="BodyTextChar"/>'),

  'FirstParagraph': style('FirstParagraph', 'First Paragraph', custom=True,
                          based='BodyText', nxt='BodyText'),

  'Compact': style('Compact', 'Compact', custom=True, based='BodyText',
                   ppr='<w:spacing w:before="0" w:after="60" '
                       f'w:line="{LINE}" w:lineRule="auto"/>'),

  'Heading1': heading('Heading1', 'heading 1', 0, 32, before=0,   after=240),
  'Heading2': heading('Heading2', 'heading 2', 1, 26, before=400, after=140),
  'Heading3': heading('Heading3', 'heading 3', 2, 24, before=320, after=120),
  'Heading4': heading('Heading4', 'heading 4', 3, 22, before=280, after=100,
                      bold=False, italic=True),
  'Heading5': heading('Heading5', 'heading 5', 4, 22, before=240, after=80,
                      bold=False, italic=True),

  # Abbildung: zentriert, etwas Luft darüber/darunter
  'Figure': style('Figure', 'Figure', custom=True, based='Normal',
                  ppr='<w:jc w:val="center"/>'
                      '<w:spacing w:before="0" w:after="240" '
                      'w:line="240" w:lineRule="auto"/>'),

  'CaptionedFigure': style('CaptionedFigure', 'Captioned Figure', custom=True,
                           based='Normal',
                           ppr='<w:jc w:val="center"/>'
                               '<w:spacing w:before="0" w:after="240" '
                               'w:line="240" w:lineRule="auto"/>'),

  # Legenden: 10 pt, einzeilig, linksbündig
  'Caption': style('Caption', 'caption', based='Normal',
                   ppr='<w:jc w:val="left"/><w:spacing w:before="0" w:after="240" '
                       'w:line="240" w:lineRule="auto"/>',
                   rpr=RF + SZS),

  'ImageCaption': style('ImageCaption', 'Image Caption', custom=True, based='Caption',
                        ppr='<w:keepNext/><w:jc w:val="left"/>'
                            '<w:spacing w:before="240" w:after="80" '
                            'w:line="240" w:lineRule="auto"/>'),

  'TableCaption': style('TableCaption', 'Table Caption', custom=True, based='Caption',
                        ppr='<w:keepNext/><w:jc w:val="left"/>'
                            '<w:spacing w:before="240" w:after="80" '
                            'w:line="240" w:lineRule="auto"/>'),

  # Blockzitat: eingerückt, 10 pt, einzeilig
  'BlockText': style('BlockText', 'Block Text', based='BodyText', nxt='BodyText',
                     ppr='<w:spacing w:before="160" w:after="160" '
                         'w:line="240" w:lineRule="auto"/>'
                         '<w:ind w:left="567" w:right="567" w:firstLine="0"/>'
                         '<w:jc w:val="both"/>',
                     rpr=RF + SZS),

  # Literaturverzeichnis: hängender Einzug
  'Bibliography': style('Bibliography', 'Bibliography', based='Normal',
                        nxt='Bibliography',
                        ppr=f'<w:spacing w:before="0" w:after="120" w:line="{LINE}" w:lineRule="auto"/>'
                            '<w:ind w:left="567" w:hanging="567"/>'
                            '<w:jc w:val="left"/>'),

  'FootnoteText': style('FootnoteText', 'footnote text', based='Normal',
                        ppr='<w:spacing w:before="0" w:after="0" '
                            'w:line="240" w:lineRule="auto"/><w:jc w:val="both"/>',
                        rpr=RF + SZS),

  # Text in Tabellenzellen: 10 pt, einzeilig, kein Abstand nach dem Absatz.
  # Eigenes Format, weil Absatzformate in der OOXML-Rangfolge über dem
  # Tabellenformat stehen — die rPr des Tabellenformats greift sonst nicht.
  'TabellenText': style('TabellenText', 'Tabellentext', custom=True, based='Normal',
                        ppr='<w:spacing w:before="0" w:after="0" '
                            'w:line="240" w:lineRule="auto"/><w:jc w:val="left"/>',
                        rpr=RF + SZS),

  # Leerzeile, die nach jeder Tabelle eingefügt wird
  'Leerzeile': style('Leerzeile', 'Leerzeile', custom=True, based='Normal',
                     ppr='<w:spacing w:before="0" w:after="0" '
                         'w:line="240" w:lineRule="auto"/>',
                     rpr=RF + SZ),

  'Title': style('Title', 'Title', based='Normal', nxt='BodyText',
                 ppr='<w:jc w:val="center"/><w:spacing w:before="0" w:after="240"/>',
                 rpr=RF + '<w:b/><w:sz w:val="40"/><w:szCs w:val="40"/>'),

  'Subtitle': style('Subtitle', 'Subtitle', based='Normal', nxt='BodyText',
                    ppr='<w:jc w:val="center"/><w:spacing w:before="0" w:after="240"/>',
                    rpr=RF + '<w:sz w:val="28"/><w:szCs w:val="28"/>'),

  'Author': style('Author', 'Author', based='Normal', nxt='BodyText',
                  ppr='<w:jc w:val="center"/><w:spacing w:before="0" w:after="120"/>',
                  rpr=RF + SZ),
}

# ------------------------------------------------------------------ Tabellenformat
TABLE_STYLE = f'''<w:style w:type="table" w:default="1" w:styleId="Table">
<w:name w:val="Table"/>
<w:basedOn w:val="TableNormal"/>
<w:qFormat/>
<w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/>
<w:jc w:val="left"/></w:pPr>
<w:rPr>{RF}{SZS}</w:rPr>
<w:tblPr>
<w:jc w:val="center"/>
<w:tblInd w:w="0" w:type="dxa"/>
<w:tblBorders>
<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>
<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>
<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>
<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
</w:tblBorders>
<w:tblCellMar>
<w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>
<w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/>
</w:tblCellMar>
</w:tblPr>
<w:trPr><w:jc w:val="center"/></w:trPr>
<w:tblStylePr w:type="firstRow">
<w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>
<w:rPr><w:b/><w:bCs/></w:rPr>
<w:tcPr><w:vAlign w:val="bottom"/>
<w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders>
</w:tcPr>
</w:tblStylePr>
</w:style>'''

# ------------------------------------------------------------------ Seiteneinrichtung
SECTPR = ('<w:sectPr>'
          '<w:pgSz w:w="11906" w:h="16838"/>'                      # A4
          '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" '  # 2,5 cm
          'w:left="1418" w:header="708" w:footer="708" w:gutter="0"/>'
          '<w:docGrid w:linePitch="360"/>'
          '</w:sectPr>')


def main():
    tmp = tempfile.mkdtemp()
    base = os.path.join(tmp, 'base.docx')
    with open(base, 'wb') as fh:
        subprocess.run(['pandoc', '--print-default-data-file', 'reference.docx'],
                       stdout=fh, check=True)
    work = os.path.join(tmp, 'ref')
    with zipfile.ZipFile(base) as z:
        z.extractall(work)

    p = os.path.join(work, 'word', 'styles.xml')
    xml = open(p, encoding='utf-8').read()

    # Dokument-Grundeinstellung
    xml = re.sub(r'<w:rPrDefault>.*?</w:rPrDefault>',
                 f'<w:rPrDefault><w:rPr>{RF}{SZ}'
                 f'<w:lang w:val="{LANG}" w:eastAsia="{LANG}" w:bidi="ar-SA"/>'
                 '</w:rPr></w:rPrDefault>', xml, flags=re.S)
    xml = re.sub(r'<w:pPrDefault>.*?</w:pPrDefault>',
                 f'<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="{LINE}" '
                 'w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault>',
                 xml, flags=re.S)

    # Absatzformate ersetzen bzw. ergänzen
    for sid, new in STYLES.items():
        pat = re.compile(r'<w:style w:type="paragraph"[^>]*w:styleId="' + sid + r'">.*?</w:style>',
                         re.S)
        xml, n = pat.subn(lambda _m: new, xml, count=1)
        if not n:
            xml = xml.replace('</w:styles>', new + '</w:styles>')

    # Tabellenformat ersetzen
    xml = re.sub(r'<w:style w:type="table"[^>]*w:styleId="Table">.*?</w:style>',
                 lambda _m: TABLE_STYLE, xml, flags=re.S, count=1)

    open(p, 'w', encoding='utf-8').write(xml)

    # Seitenformat
    d = os.path.join(work, 'word', 'document.xml')
    doc = open(d, encoding='utf-8').read().replace('<w:sectPr />', SECTPR)
    open(d, 'w', encoding='utf-8').write(doc)

    # Sprache der Rechtschreibprüfung
    s = os.path.join(work, 'word', 'settings.xml')
    st = open(s, encoding='utf-8').read().replace('w:val="en-US"', f'w:val="{LANG}"')
    open(s, 'w', encoding='utf-8').write(st)

    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(work):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, work))
    shutil.rmtree(tmp)
    print(f'Formatvorlage geschrieben: {OUT}')


if __name__ == '__main__':
    main()
