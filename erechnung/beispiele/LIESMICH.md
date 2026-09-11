# Zwei Beispielrechnungen — derselbe Vorgang, zweimal

Beide Dateien beschreiben **dieselbe Rechnung**: Maurerarbeiten pauschal,
dazu 18,5 Regiestunden, zusammen 4.260,85 Euro netto, Bauleistung nach
§ 13 b ohne Umsatzsteuer.

Der Betrieb hat in seinem Programm in beiden Fällen **genau dasselbe getippt**.
Der Unterschied sind ausschließlich Einstellungen.

| Datei | Zustand |
|---|---|
| `13b-falsch.xml` | Programm nie eingerichtet |
| `13b-richtig.xml` | Programm eingerichtet |

## So siehst du den Unterschied

1. Öffne den Leser auf deiner Seite.
2. Lade `13b-falsch.xml` hoch, sieh sie dir an.
3. Lade `13b-richtig.xml` hoch und vergleiche.
4. Öffne beide zusätzlich in einem Texteditor. Die Kommentare im Text zeigen
   Zeile für Zeile, was verstellt war.

## Die drei Unterschiede

**Steuerschlüssel.** Falsch steht `S` mit 0 Prozent — Kategorie S heißt
„normal steuerpflichtig", und 0 Prozent ergibt dazu keinen Sinn. Richtig ist
`AE` mit dem Befreiungsgrund `VATEX-EU-AE` und dem Klartext
„Steuerschuldnerschaft des Leistungsempfängers". Im Programm des Kunden ist
das ein Steuerschlüssel im Stammdatensatz, oft selbst angelegt als „0 % Bau".

**Rundung.** Falsch stehen unten 4.260,83 Euro, die Positionen ergeben aber
4.260,85. Zwei Cent, weil das Programm je Position rundet und danach addiert.
Im Programm ist das eine Einstellung zur Rundung.

**Mengeneinheiten.** Falsch stehen `psch` und `Std` als frei getippter Text.
Gültig sind nur Codes: `C62` für die Einheit eins, `HUR` für die Stunde.
Im Programm hängen die am Artikelstamm.

## Warum das keiner von allein merkt

Beide Rechnungen sehen als PDF ausgedruckt **völlig gleich aus**. Der
Unterschied steckt nur in der Datei dahinter. Deshalb fällt es erst auf,
wenn der Kunde die Rechnung ablehnt — und dann in der Regel im Januar.
