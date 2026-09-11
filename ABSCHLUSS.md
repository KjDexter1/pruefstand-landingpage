# Prüfstand — eingestellt am 04.09.2026

Das Projekt wird nicht weiterverfolgt. Kein Betrieb angemeldet, keine Kunden,
keine Verträge, keine Zahlungen. Der Ausstieg ist vollständig und sauber.

## Die Geschäftsidee

Handwerksbetriebe zahlen ihren Baustoff-Großhändlern zu viel, weil stille
Preiserhöhungen in den Eingangsrechnungen untergehen. Prüfstand sollte die
Rechnungen der letzten Monate automatisiert auf Preissprünge, Mengenabweichungen
und Rechenfehler prüfen und die Funde in einem Bericht ausweisen.

## Warum eingestellt

Am 04.09.2026 wurden sieben Kaltakquise-Anrufe geführt, verteilt auf vier
Gewerke: Bau, Elektro, Sanitär, Heizung.

**Ergebnis: 0 von 7.** Alle sieben Betriebe gaben unabhängig voneinander
dieselbe Antwort — sie prüfen ihre Einkaufspreise selbst, weil das ihr
Kerngeschäft ist und sie sich nicht übervorteilen lassen wollen.

Die vorab festgelegte Entscheidungsregel lautete: 3+ Zusagen = weitermachen,
1–2 = Zielgruppe verengen, 0 = einstellen.

## Was daraus zu lernen ist

1. **Es war die falsche Art von Nein.** „Zu teuer" oder „gerade keine Zeit"
   sind Einwände, gegen die man antesten kann. „Das ist unser Geschäft" ist
   ein struktureller Einwand: die Leistung ist beim Kunden bereits eine
   besetzte interne Funktion. Dagegen hilft keine Positionierung.

2. **Der Rettungsversuch trägt nicht.** Vermutlich prüfen die Betriebe nur
   oberflächlich und übersehen schleichende Erhöhungen tatsächlich. Das
   ändert kommerziell nichts: Man kann niemandem etwas verkaufen, von dem
   er überzeugt ist, dass er es bereits tut. Man müsste ihm erst beweisen,
   dass er seinen eigenen Job nicht richtig macht — kostenlos, bei jedem
   Kunden neu, gegen seinen Widerstand.

3. **Die tragende Annahme war nie belegt.** Ein Preisanstieg ist kein
   Schaden. Baustoffpreise steigen legitim. Ein belegbarer Fehler entsteht
   erst gegen ein schriftliches Referenzdokument (Konditionsvereinbarung,
   Rahmenvertrag). Ob Handwerksbetriebe so etwas überhaupt haben, wurde nie
   geklärt — das hätte vor jeder Zeile Code passieren müssen.

4. **Der Test hat funktioniert.** Zwei Stunden Telefon statt zwei Monaten
   Entwicklung. Das ist das eigentliche Ergebnis: erst sieben Gespräche,
   dann bauen.

## Was erhalten bleibt

- `ops/preise/preisverlauf.py` — funktionierender Parser für XRechnung (UBL
  und CII) sowie ZUGFeRD-PDFs, mit Preisverlaufsanalyse. Unabhängig vom
  Geschäftsmodell wiederverwendbar.
- `ops/bericht/` — Berichtsgenerator (CSV + JSON → Word).
- `archiv/website/` — die komplette ehemalige Website inklusive Impressum,
  Datenschutzerklärung und Funktionsbeschreibung.
- `strategie/` — Marktvergleich, Geschäftskonzept, Betriebssystem.
- `.github/workflows-deaktiviert/` — die vier Automatiken. Wieder aktiv,
  sobald der Ordner zurück nach `.github/workflows/` verschoben wird.

## Offene Frage für später

Die Gespräche haben gezeigt: Handwerksbetriebe sind telefonisch erreichbar
und gesprächsbereit. Sie kaufen nur nichts, was ihre eigene Kernkompetenz
verdoppelt. Die interessante Frage ist damit nicht mehr „was können wir für
Handwerker prüfen", sondern „was nervt Handwerker, das *nicht* ihr Geschäft
ist" — Bürokratie, Dokumentation, Nachweise, Behördenkram.
