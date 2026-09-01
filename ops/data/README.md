# Daten

Zwei append-only Dateien im JSONL-Format. Eine Zeile = ein Eintrag.
Bewusst keine Datenbank: versionierbar, diffbar, ohne Server sicherbar.

## leads.jsonl

Vertriebskontakte. Statusfolge:
`neu -> kontaktiert -> demo_geplant -> demo_gehalten -> pilot -> kunde` (oder `verloren`).
Jeder Statuswechsel landet mit Zeitstempel in `verlauf` — dadurch ist im Nachhinein
messbar, wo im Trichter Kontakte haengenbleiben.

## faelle.jsonl

Ein Eintrag je bearbeitetem Beleg. Das ist die Lernschleife aus der Gegenrecherche,
auf vier Felder reduziert:

| Feld | Entspricht | Warum |
|---|---|---|
| `kunde`, `lieferant`, `belegtyp` | Kontext | ohne Kontext ist eine Korrektur nicht uebertragbar |
| `ergebnis` | Ergebnis | `ok`, `korrigiert`, `eskaliert`, `fehler` |
| `korrektur`, `regel_kandidat` | Korrektur | der einzige wirklich wertvolle Datensatz |
| `minuten_manuell`, `minuten_system` | Outcome | belegt den ROI gegenueber dem Kunden |

`regel_kandidat` ist ein kurzer, wiederverwendbarer Name des Musters
(z. B. `IBAN fehlt`, `Skontofrist fehlt`, `Summe weicht ab`). Nur weil dieses Feld
gleich geschrieben wird, kann `pruefstand.py regeln` Wiederholungen erkennen.

## Datenschutz

Hier gehoeren keine personenbezogenen Daten von Mietern, Mitarbeitern oder
Rechnungsempfaengern hinein — nur Betriebsnamen, Lieferantennamen und
Prozesskennzahlen. Bei echten Kundendaten gilt Zweckbindung und Loeschkonzept
(siehe Monatslauf-Checkliste).
