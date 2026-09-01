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

## Der Katalog: zwei Stufen

`foerdermittel.json` wird von Hand gepflegt und kennt zwei Zustände:

| Feld | Bedeutung |
|---|---|
| `recherchiert_am` + `quelle` + `quelle_typ` | Die Angabe stammt aus dieser Quelle von diesem Tag. `quelle_typ` ist `offiziell` (Trägerseite) oder `sekundaer` (Fachportal, Blog). |
| `freigegeben_am` + `freigegeben_von` | Ein Mensch hat die Angabe beim Träger bestätigt. **Erst jetzt darf sie einem Betrieb vorgelegt werden.** |

Der Unterschied ist nicht formal. Recherche sagt, was auf einer Seite stand.
Freigabe sagt, dass jemand dafür geradesteht. Förderprogramme ändern sich
mehrmals im Jahr, und eine falsche Quote in einer Kundenmappe ist ein
Haftungsfall.

Das Skript weist bei jedem Lauf aus, welche Einträge nicht freigegeben sind,
welche ganz ohne Recherche dastehen und welche Freigabe älter als sechs
Monate ist. Die Vorbereitungsmappe trägt pro nicht freigegebenem Programm
einen Warnkasten.

**Derzeit ist kein Eintrag freigegeben.** Alle fünf sind recherchiert.

### Vor der Freigabe abgleichen

1. `quelle` aufrufen und die Angaben Zeile für Zeile vergleichen
2. Besonders: **Antrag vor Vorhabenbeginn?** Trifft das zu, ist eine bereits
   bezahlte Rechnung nicht mehr förderfähig — dann bringt der Fund nichts
   und darf im Kundengespräch nicht als Chance dargestellt werden.
3. Bei `quelle_typ: sekundaer` zusätzlich beim Träger selbst nachfragen
4. `freigegeben_am` und `freigegeben_von` setzen

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
