# Preisverlauf-Prüfer

Findet stille Preiserhöhungen in elektronischen Eingangsrechnungen — der
Prüfpunkt, der erfahrungsgemäß am häufigsten etwas findet, und der einzige,
der ganz ohne Preisliste auskommt.

Das Vorgehen ist dasselbe wie von Hand: Einzelpreise desselben Artikels über
mehrere Rechnungen untereinanderschreiben und schauen, wo sich etwas ändert.
Nur eben in Sekunden statt in Stunden.

## Aufrufen

```bash
./ops/preise/preisverlauf.py --ordner ops/preise/beispiel
./ops/preise/preisverlauf.py --ordner ~/rechnungen/voss --csv vorschlag.csv
```

Ohne `--csv` nur die Bildschirmausgabe. Mit `--csv` entsteht zusätzlich eine
Datei im Format von `ops/bericht/funde.csv` — Zeilen daraus kopierst du
direkt in die Fundtabelle des Berichts.

## Welche Rechnungen gelesen werden

| Format | Erkennung |
|---|---|
| XRechnung, UBL-Syntax | `.xml` mit Wurzelelement `Invoice` |
| XRechnung / ZUGFeRD, CII-Syntax | `.xml` mit Wurzelelement `CrossIndustryInvoice` |
| ZUGFeRD / Factur-X | `.pdf` mit eingebettetem XML — braucht `pip install pypdf` |
| Papier, Scan, normales PDF | **nicht lesbar** — diese Positionen bleiben Handarbeit |

Was nicht gelesen werden kann, wird einzeln mit Grund gemeldet und
übersprungen. Der Lauf bricht deswegen nicht ab.

## Was gemeldet wird

Eine Preiserhöhung ab 1 Cent **und** ab 0,5 % — darunter ist es Rundung.
Preissenkungen werden nicht gemeldet.

Wichtig: Gezählt wird nicht nur die erste Rechnung mit dem höheren Preis,
sondern **jede folgende, solange der Preis oben bleibt**. Wer nur die erste
zählt, unterschätzt den Schaden erheblich — genau das ist der Punkt, den ein
Betrieb selbst nie bemerkt.

## Warum alles als „zu klären" herauskommt

Jeder gefundene Anstieg wird mit Status `zu klären` ausgegeben, nie als
`sicher`. Eine Preiserhöhung kann angekündigt und vereinbart worden sein —
das weiß nur, wer die Konditionsvereinbarung kennt.

**Der Ablauf ist also:** Skript findet die Kandidaten → du prüfst gegen die
Vereinbarung → du setzt die bestätigten Zeilen von Hand auf `sicher` → erst
dann zählen sie im Bericht in die Summe.

Solange nichts umgestellt ist, weist der Bericht korrekt `0,00 € belegbar`
aus. Das ist keine Fehlfunktion, sondern die Trennung zwischen Fund und
Nachweis.

## Beispiel ausprobieren

`beispiel/` enthält acht erfundene Rechnungen von zwei Lieferanten, vier in
UBL- und vier in CII-Syntax, mit zwei eingebauten Preiserhöhungen. Damit
lässt sich der Ablauf durchspielen, bevor echte Rechnungen da sind.

## Echte Rechnungen

Gehören **nicht** ins Repository. Lege sie außerhalb ab, oder in
`ops/preise/rechnungen/` — dieser Ordner ist von der Versionierung
ausgenommen.
