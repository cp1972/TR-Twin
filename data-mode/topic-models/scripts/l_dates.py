# -*- coding: utf-8 -*-
"""Echte Jahre der Berufsetappen aus den Notizen.

Regeln (in dieser Reihenfolge):
  text   : erste Jahreszahl der Etappe = Beginn (bei Spannen wie 1893-5 der Anfang).
           Steht die Jahreszahl nur hinter 'to'/'until'/'till', ist sie ein Endjahr und wird nicht als Beginn genommen.
  alter  : 'aged 11', 'at age 9' -> Geburtsjahr + Alter.
  Plausibilität: Beginn zwischen Geburtsjahr + 4 und + 90; die Jahre eines Akteurs dürfen nicht
           rückwärts laufen (eine Jahreszahl vor der vorigen datierten Etappe gilt als Rückblick und wird verworfen).
  interpoliert : zwischen zwei datierten Etappen gleichmäßig verteilt.
  geschätzt    : vor der ersten bzw. nach der letzten datierten Etappe im Abstand der typischen
                 Etappendauer (Median der Kohorte); ohne jede Datierung wie bisher Geburtsjahr + 15 + 4 x Etappe.
"""
import re, statistics
from collections import defaultdict
from common import STG, ACT

YR = re.compile(r'\b(1[6-9]\d\d)\b')
END_ONLY = re.compile(r'\b(?:to|until|till)\s+(1[6-9]\d\d)\b', re.I)
AGE = re.compile(r'\b(?:aged?|at age|age of|from age)\s*(\d{1,2})\b', re.I)


def raw_year(text, birth):
    m = YR.search(text)
    if m:
        e = END_ONLY.search(text)
        if not (e and e.start(1) == m.start(1)):
            return int(m.group(1)), 'text'
    a = AGE.search(text)
    if a and birth:
        return birth + int(a.group(1)), 'alter'
    return None, None


def stage_years():
    by = defaultdict(list)
    for s in STG:
        by[s['entry_id']].append(s)
    raw = {}
    for e, v in by.items():
        v.sort(key=lambda s: int(s['stage_index']))
        try:
            birth = int(ACT[e]['birth_year'])
        except ValueError:
            birth = None
        prev = None
        for s in v:
            y, src = raw_year(s['occupation_raw'], birth)
            if y is not None and birth and not (birth + 4 <= y <= birth + 90):
                y, src = None, None
            if y is not None and prev is not None and y < prev:
                y, src = None, None
            if y is not None:
                prev = y
            raw[(e, int(s['stage_index']))] = (y, src)
    # typische Etappendauer
    gaps = []
    for e, v in by.items():
        ys = [raw[(e, int(s['stage_index']))][0] for s in v]
        ds = [(i, y) for i, y in enumerate(ys) if y is not None]
        for (i1, y1), (i2, y2) in zip(ds, ds[1:]):
            if y2 > y1:
                gaps.append((y2 - y1) / (i2 - i1))
    step = round(statistics.median(gaps), 1)
    out = {}
    for e, v in by.items():
        idx = [int(s['stage_index']) for s in v]
        ys = [raw[(e, i)][0] for i in idx]
        src = [raw[(e, i)][1] for i in idx]
        try:
            birth = int(ACT[e]['birth_year'])
        except ValueError:
            birth = None
        dated = [k for k, y in enumerate(ys) if y is not None]
        if not dated:
            base = birth or 1850
            for k, i in enumerate(idx):
                out[(e, i)] = (base + 15 + 4 * i, 'geschätzt')
            continue
        f, l = dated[0], dated[-1]
        for k in range(len(idx)):
            if ys[k] is not None:
                out[(e, idx[k])] = (ys[k], src[k]); continue
            if k < f:
                y = ys[f] - step * (f - k)
                if birth:
                    y = max(y, birth + 8 + k)          # nicht vor dem Kindesalter
                out[(e, idx[k])] = (int(round(min(y, ys[f]))), 'geschätzt')
            elif k > l:
                out[(e, idx[k])] = (int(round(ys[l] + step * (k - l))), 'geschätzt')
            else:
                a = max(d for d in dated if d < k); b = min(d for d in dated if d > k)
                out[(e, idx[k])] = (int(round(ys[a] + (ys[b] - ys[a]) * (k - a) / (b - a))), 'interpoliert')
    return out, step


if __name__ == '__main__':
    from collections import Counter
    Y, step = stage_years()
    print('typische Etappendauer (Median, Jahre):', step)
    print(Counter(s for _, s in Y.values()))
    old = {}
    for s in STG:
        e = s['entry_id']
        try: b = int(ACT[e]['birth_year'])
        except ValueError: b = 1850
        old[(e, int(s['stage_index']))] = b + 15 + int(s['stage_index']) * 4
    d = [Y[k][0] - old[k] for k in Y if Y[k][1] in ('text', 'alter')]
    print('Abweichung echtes Jahr - bisherige Schätzung: Median', statistics.median(d),
          '| Anteil |Abw.| > 10 Jahre:', round(sum(abs(x) > 10 for x in d) / len(d), 2))
