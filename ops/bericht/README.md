# Berichtsgenerator

Erzeugt den fertigen Prüfbericht als Word-Datei. Du trägst die Funde in eine
Tabelle ein, das Skript rechnet und schreibt das Dokument. Damit stehen im
Bericht, mit dem du Geld verlangst, keine Rechen- oder Tippfehler.

## Wo die Daten liegen

**Nicht im Projektordner.** Die Arbeitsdateien enthalten Rechnungsnummern,
Lieferanten und Beträge echter Betriebe. Kämen sie in die Versionsverwaltung,
blieben sie dort dauerhaft — auch nach dem Löschen. Das widerspräche der
Zusage aus der Vertraulichkeitserklärung, digitale Kopien nach acht Wochen
zu löschen.

Standardordner ist deshalb **`~/pruefstand-daten`**. Beim ersten Aufruf legt
das Skript ihn an und kopiert die Vorlagen hinein:

```
Arbeitsordner angelegt: /Users/faruk/pruefstand-daten
Hineinkopiert: funde.csv, bericht.json
```

Für mehrere Betriebe parallel: `--daten ~/kunden/voss`. Die Word-Datei
entsteht im selben Ordner wie die Daten.

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
npm install                          # einmalig

node erzeuge-bericht.js              # aus ~/pruefstand-daten
node erzeuge-bericht.js --daten ~/kunden/voss
node erzeuge-bericht.js --beispiel   # mit den Beispieldaten des Projekts
node erzeuge-bericht.js --muster     # gekennzeichnete Musterfassung
```

Voraussetzung ist Node.js.

## Der GitHub-Weg erzeugt nur noch den Musterbericht

Früher ließ sich der Bericht ohne lokale Installation über *Actions* bauen.
Das geht für **echte** Berichte nicht mehr, und zwar aus gutem Grund: Dafür
müssten die Kundendaten ins Repository, und genau das soll nicht passieren.

Der Workflow *Musterbericht erzeugen* baut weiterhin die gekennzeichnete
Musterfassung aus den Beispieldaten — brauchbar, um jemandem zu zeigen, wie
ein Bericht aussieht. Echte Berichte entstehen lokal.

## Danach

Word öffnen, überfliegen, als PDF exportieren, verschicken. Alles
**orange** Geschriebene stammt aus deinen beiden Dateien — wenn dort etwas
falsch aussieht, korrigierst du es in `funde.csv` oder `bericht.json` und
erzeugst neu, statt im Word-Dokument herumzuschreiben.

Die erzeugten `.docx` werden nicht ins Repository aufgenommen: Sie enthalten
echte Kundendaten und gehören nicht in ein Code-Verzeichnis.
