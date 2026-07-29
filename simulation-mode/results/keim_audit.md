# Keim-Prüfung (Seed-Audit) aller Apex-Befunde — 5000 Schritte, Keime 1–8

Kriterium: GINI > 0,05 = Herrschaft. Bei GINI ≤ 0,05 ist der Argmax bedeutungslos
(symmetrisches Feld), deshalb "keine Herrschaft".

| Konfiguration              | Ergebnis über 8 Keime                                    | Status    |
|----------------------------|----------------------------------------------------------|-----------|
| Parsons (Kap. 3)           | Politik 8/8 — 77,5 %                                     | robust    |
| Luhmann (Kap. 4)           | keine Herrschaft 8/8 — 25,1 %                            | robust    |
| Habermas Ketten auf B (5)  | Politik 8/8 — 60,4–60,5 %                                | robust    |
| Habermas Ketten auf C (5)  | Wirtschaft 4/8 (49,1–49,4 %) · Politik 4/8 (61,8 %)      | BISTABIL  |
| White Basis (Kap. 6)       | Politik 8/8 — 62,2 %                                     | robust    |
| White hub=K (6)            | keine Herrschaft 6/8 (27,0 %) · Politik 2/8 (61,2 %)     | BISTABIL  |
| White hub=P (6)            | Politik 8/8 — 60,2 %                                     | robust    |
| White hub=W (6)            | Wirtschaft 4/8 (49,6 %) · Politik 4/8 (62,0 %)           | BISTABIL  |
| White hub=M (6)            | Wirtschaft 4/8 (36,2–53,9 %) · Politik 4/8 (62,0 %)      | BISTABIL  |
| Tilly (Kap. 7)             | Wirtschaft 6/8 (49,4 %) · Politik 2/8 (62,1 %)           | BISTABIL  |
| Bourdieu dialektisiert (8) | Politik 8/8 — 63,4–65,4 %                                | robust    |
| Bourdieu nicht-dial. (8)   | Politik 8/8 — 62,2 %                                     | robust    |
| Intersektionalität (9)     | Politik 8/8 — 70,7 %                                     | robust    |
| Fuhse Sinn→W (10)          | Wirtschaft 8/8 — 49,5–49,6 %                             | robust    |
| Fuhse Sinn→P (10)          | Politik 8/8 — 59,7–59,8 %                                | robust    |

Tragfähigkeits-Maxima (Kap. 10, emirbayer_substanz), je Keim das Maximum über alle α:

| hub        | Maximum je Keim 1–8                     | Status |
|------------|-----------------------------------------|--------|
| Kultur     | 27,4 (achtmal identisch)                | robust |
| Politik    | 60,7 (achtmal identisch)                | robust |
| Wirtschaft | 49,2–49,6 (Median 49,4)                 | robust |
| Medien     | 27,4 (achtmal identisch)                | robust |

## Befund

Es gibt stets **genau zwei Attraktoren**; der Keim wählt nur das Becken. Der Politik-Attraktor
ist der stärkere: Er setzt sich auch dort durch, wo alle Ketten auf eine andere Struktur
zeigen. Bistabilität tritt nur bei hoher Konzentration auf (alpha 1,6); bei alpha 1,4
(Fuhse) ist derselbe Aufbau keimstabil.

## Reproduktion

    node metrics.js ./tr-twin.html ./spec.json ./out/audit.json

mit `"seed": N` je Eintrag der spec.json.
