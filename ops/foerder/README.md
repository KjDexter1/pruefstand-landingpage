# Fördermittel-Check

Erkennt aus Eingangsrechnungen Investitionen, für die staatliche Zuschüsse
existieren könnten, und bereitet den Antrag vor. **Vor der ersten Nutzung mit
einem Kunden: `RISIKO-NOTIZ.md` anwaltlich prüfen lassen.**

## Aufrufen

```bash
./ops/foerder/foerder-check.py --ordner ops/foerder/beispiel \
    --betrieb "Elektro Voss GmbH" --mappe mappe.html
./ops/foerder/foerder-check.py --csv positionen.csv
```

Liest dieselben Rechnungsformate wie der Preisverlauf-Prüfer (XRechnung UBL
und CII, ZUGFeRD-PDF) oder eine CSV mit den Spalten
`Lieferant;Rechnung;Datum;Artikel;Betrag`.

Die Mappe entsteht als HTML — im Browser öffnen und mit Strg+P als PDF
speichern. Bewusst kein automatisches Einreichen: Ämter haben dafür keine
Schnittstellen, und die Verantwortung für den Antrag bleibt beim Betrieb.

## Der Katalog

`foerdermittel.json` wird von Hand gepflegt. Jeder Eintrag hat
`geprueft_am` und `geprueft_von`.

**Solange diese Felder leer sind, gilt der Eintrag als unverifiziert.** Das
Skript weist das bei jedem Lauf aus, und die Vorbereitungsmappe trägt einen
Warnkasten. Derzeit ist kein Eintrag verifiziert — die enthaltenen Programme
sind Startpunkte für die Recherche, keine belastbaren Angaben.

Beim Prüfen eines Eintrags: Seite des Trägers aufrufen, Quote, Frist,
Voraussetzungen und vor allem die Frage „Antrag vor Vorhabenbeginn?"
abgleichen, dann Datum und Namen eintragen.

## Fristen-Radar

Warnungen bei 28 und 14 Tagen vor Ablauf, dazu bei bereits abgelaufenen
Fristen. Jede Warnung wird mit Zeitstempel in `fristen-protokoll.csv`
festgehalten — diese Datei ist der Nachweis, wann informiert wurde, und
gehört zur Haftungsfrage in der Risiko-Notiz.

## Zuordnung

Positionen werden über Stichworte einer Kategorie zugeordnet
(`kategorien` in der JSON). Das ist bewusst grob: Es erzeugt einen Hinweis
zum Nachschauen, keine Feststellung. Fehlzuordnungen sind erwartbar und
werden beim Durchsehen der Mappe korrigiert.

Positionen ohne Treffer werden gezählt und nicht weiter behandelt. Die
meisten Eingangsrechnungen sind Material, kein Investitionsgut — wenn nichts
gefunden wird, ist das das normale Ergebnis.
