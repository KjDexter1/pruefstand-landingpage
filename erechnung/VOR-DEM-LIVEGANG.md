# Vor dem Livegang — Restliste

Vier Dinge, bevor die Seite oeffentlich erreichbar sein darf.

## 1. Platzhalter ersetzen

| Datei | Wo |
|---|---|
| `leser.html` | Abschnitt `KONTAKT` im Skript: Name, Firma, Telefon, E-Mail |
| `impressum.html` | 7 rot markierte Stellen |
| `datenschutz.html` | 8 rot markierte Stellen, dazu Hosting und Aufsichtsbehoerde |

Die roten Warnkaesten in allen drei Dateien danach loeschen.

## 2. Schriftarten lokal einbinden

Die Seiten laden IBM Plex derzeit von `fonts.googleapis.com`. Dabei geht die
IP-Adresse des Besuchers an Google. In Deutschland ist genau das abgemahnt
worden (LG Muenchen I, 3 O 17493/20), und es gab eine ganze Abmahnwelle dazu.

**Loesung:** IBM Plex ist frei lizenziert (SIL Open Font License). Schriftdateien
herunterladen, neben die HTML-Dateien legen, den `<link>` auf Google entfernen und
durch eigene `@font-face`-Regeln ersetzen. Danach faellt Abschnitt 7 der
Datenschutzerklaerung fast weg.

Solange das nicht gemacht ist: nicht oeffentlich stellen.

## 3. Gewerbe anmelden

Ein Impressum mit Namen und Anschrift, ein Angebot mit Festpreisen und eine
Rechnung setzen eine Gewerbeanmeldung voraus. Das ist der Schritt, der vor dem
ersten Kunden kommt, nicht danach.

## 4. AGB vom Anwalt

Drei Punkte muessen darin stehen:

1. Gegenstand ist die technische Einrichtung vorhandener Software, keine
   Steuerberatung.
2. Keine Zusicherung, dass ein bestimmter Empfaenger eine Rechnung annimmt.
   Keine Haftung fuer Zahlungseingaenge oder Zahlungsverzug.
3. Die steuerliche Richtigkeit verantwortet der Kunde beziehungsweise sein
   Steuerberater.

Das schreibt ein Anwalt, nicht ich. Bei Auftraegen, an denen Zahlungen ueber
zehntausende Euro haengen, ist das keine Vorsicht, sondern Grundausstattung.

---

## Was schon erledigt ist

- Impressum nennt **§ 5 DDG**, nicht mehr das abgeloeste TMG.
- **Kein Hinweis auf die EU-Streitschlichtungsplattform.** Die wurde am
  20.07.2025 eingestellt; der frueher pflichtige Hinweis ist heute selbst
  abmahnfaehig. Im alten Pruefstand-Impressum stand er noch drin.
- Abschnitt "Art der Taetigkeit" grenzt gegen Steuerberatungsgesetz und
  Rechtsdienstleistungsgesetz ab.
- Die Datenschutzerklaerung sagt in Abschnitt 4 und 5 zu, dass Rechnungsdateien
  und Formularangaben den Rechner nicht verlassen. Das stimmt technisch — die
  Seite hat keinen Server, an den sie etwas senden koennte. Diese Zusage darf
  beim Nachruesten eines echten Kontaktformulars nicht stillschweigend gebrochen
  werden.
- Impressum- und Datenschutzlink stehen immer im Fuss, unabhaengig davon, ob die
  Kontaktdaten schon eingetragen sind.
