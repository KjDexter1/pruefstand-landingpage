# Berichtsgenerator

Erzeugt den fertigen Prüfbericht als Word-Datei. Du trägst die Funde in eine
Tabelle ein, das Skript rechnet und schreibt das Dokument. Damit stehen im
Bericht, mit dem du Geld verlangst, keine Rechen- oder Tippfehler.

## Zwei Dateien füllst du aus

**`funde.csv`** — eine Zeile je Fund. Öffnet sich in Excel per Doppelklick
(Semikolon-getrennt, wie in Deutschland üblich).

| Spalte | Beispiel | Hinweis |
|---|---|---|
| Lieferant | Nordmann Baustoffe | |
| Rechnung | RE-08214 | ohne sie kann der Betrieb nicht reklamieren |
| Datum | 18.08.2026 | |
| Pruefpunkt | Preis still erhöht | Kurzname aus der Prüf-Checkliste |
| Soll | 6,20 € | was vereinbart war |
| Ist | 6,45 € | was berechnet wurde |
| Differenz | 30,00 | nur die Zahl, kein Euro-Zeichen nötig |
| Status | sicher | `sicher` oder `zu klären` — sonst bricht das Skript ab |

**`bericht.json`** — Betrieb, Zeitraum, Lieferanten mit Prüftiefe, die
Muster-Sätze, was nicht geprüft werden konnte, die Empfehlungen.

## Was das Skript selbst rechnet

Diese Zahlen trägst du **nicht** ein, sie entstehen aus den beiden Dateien:

- Summe der belegbaren Funde — nur Zeilen mit Status `sicher`
- Anzahl der Funde
- Geprüfte Rechnungen und Einkaufsvolumen (Summe über die Lieferanten)
- Hochrechnung aufs Jahr (Quartalssumme × 4)

Genau hier entstehen von Hand die Fehler, und genau die sind in einem
Dokument peinlich, das einen Betrag gegenüber einem Lieferanten begründet.

## Erzeugen

```bash
cd ops/bericht
npm install          # einmalig
npm run bericht      # -> Pruefbericht_<Betrieb>.docx
npm run muster       # -> Musterbericht_Pruefstand.docx, gekennzeichnet
```

Voraussetzung ist Node.js. Wer nichts installieren will, nutzt den Weg über
GitHub (siehe unten).

## Ohne Installation, über GitHub

1. `ops/bericht/funde.csv` und `ops/bericht/bericht.json` direkt auf
   github.com bearbeiten und speichern.
2. Reiter **Actions** → **Prüfbericht erzeugen** → *Run workflow*.
3. Nach etwa einer Minute liegt die Word-Datei unter dem Lauf als
   herunterladbares Ergebnis (*Artifacts*).

## Danach

Word öffnen, überfliegen, als PDF exportieren, verschicken. Alles
**orange** Geschriebene stammt aus deinen beiden Dateien — wenn dort etwas
falsch aussieht, korrigierst du es in `funde.csv` oder `bericht.json` und
erzeugst neu, statt im Word-Dokument herumzuschreiben.

Die erzeugten `.docx` werden nicht ins Repository aufgenommen: Sie enthalten
echte Kundendaten und gehören nicht in ein Code-Verzeichnis.
