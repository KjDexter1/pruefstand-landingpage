# Testlauf 01 — 04.09.2026

Fuenf Firmen aus dem eigenen Umfeld, ausgewaehlt fuer den Kenner-Test.
Ergebnis: **Der Test konnte bei vier von fuenf gar nicht stattfinden**, weil
es nichts zu recherchieren gab.

| Firma | Eigene Website | Eigene Karriereseite | Briefing moeglich |
|---|---|---|---|
| Lufthansa LEOS GmbH | ja, aber ohne abrufbaren Inhalt | nein, Konzernportal | nein |
| FES Frankfurt | ja | ja, 37 Stellen | ja |
| Alois Dallmayr Automaten-Service GmbH, Langen | nein, unter dallmayr.com | nein, Konzernportal | nein |
| Deutsche Bahn, Kleyerstrasse Frankfurt | nein, Betriebsstaette | nein | nein |
| DHL Oberursel | nein, Zustellbasis | nein | nein |

## Was konkret passiert ist

- `lufthansa-leos.com` liefert beim Abruf nur die Ueberschrift, sonst nichts —
  die Seite baut ihren Inhalt im Browser zusammen. Ein Abrufwerkzeug bekommt
  eine leere Seite.
- Die einzige auffindbare LEOS-Stellenanzeige lag im Lufthansa-Konzernportal
  und antwortete mit **HTTP 410 Gone** — die Anzeige ist abgelaufen, die
  Suchmaschine kannte sie noch.
- Dallmayr Langen ist eine **eigene GmbH** (Alois Dallmayr Automaten-Service
  GmbH, Pittlerstr. 65, HRB 31682 Amtsgericht Offenbach), hat aber keinen
  eigenen Webauftritt und keine eigene Karriereseite.
- DB Kleyerstrasse und DHL Oberursel sind Betriebsstaetten, keine
  Rechtstraeger mit Aussendarstellung. Beide habe ich nicht einzeln abgerufen —
  es gibt nichts, das man abrufen koennte.

## Die Grenze des Produkts

Das Werkzeug braucht drei Dinge, sonst liefert es nichts:

1. eine **eigene Domain** mit serverseitig ausgeliefertem Inhalt,
2. eine **eigene Karriereseite** — das ist die ergiebigste Quelle,
3. eine Groesse, bei der die Firma **als Ganzes** die Einheit des Gespraechs ist.

Punkt 3 ist der eigentliche Befund. Ein Briefing ueber „Deutsche Bahn" ist fuer
ein Gespraech an der Kleyerstrasse wertlos: Die recherchierbare Einheit ist der
Konzern, die verkaufsrelevante Einheit ist der Betriebshof. Zwischen beiden
liegt alles, worauf es ankaeme — und darueber steht oeffentlich nichts.

Bei ECONSOR (siehe `beispiel-econsor.md`) fielen alle drei Bedingungen
zusammen, und es kamen drei belastbare Signale heraus.

## Was damit noch offen ist

Die Kernfrage — **sagt das Briefing einem Kenner etwas, das er nicht wusste** —
ist unbeantwortet. Bei vier von fuenf gab es keinen Output zu beurteilen, bei
FES steht der Durchlauf noch aus.

Der Test muss mit Firmen wiederholt werden, die dem ECONSOR-Muster entsprechen:
inhabergefuehrt, 10 bis 200 Leute, eigene Website, eigene Karriereseite.

---

## Abbruch — 04.09.2026

Das Projekt wird nicht weiterverfolgt. Grund ist **nicht** die Qualitaet des
Werkzeugs: Der ECONSOR-Durchlauf hat drei belastbare, nicht offensichtliche
Signale geliefert. Das Produkt funktioniert.

Es fehlt der Zugang zur Zielgruppe. Auf die Frage, ob Agenturinhaber und
Vertriebsleiter erreichbar sind, lautet die Antwort nein — und es liess sich
keine einzige Firma aus dem Muster benennen, an die man sich wenden koennte.

Ein Produkt ohne Zugang zum Kaeufer ist kein Geschaeft, egal wie gut es ist.

## Das Muster ueber beide Projekte

| | Zielgruppe | Zugang | Bedarf |
|---|---|---|---|
| Pruefstand | Handwerksbetriebe | **ja** — 7 Anrufe gefuehrt | nein — pruefen selbst |
| Pre-Call-Briefing | Digitalagenturen | **nein** | vermutlich ja |

Zweimal fehlte eine der beiden Haelften. Beide Male wurde zuerst das Produkt
gewaehlt und danach gefragt, wer es kaufen soll.

Die naechste Idee faengt an der anderen Seite an: **Wozu gibt es Zugang, und
was wird dort heute schon bezahlt?** Vorhandener Zugang laut Testlauf 01:
Luftfahrt-Bodendienste, Entsorgung, Bahnbetrieb, Paketlogistik, Automaten-
service — Industrie- und Logistikbetriebe, von innen gekannt.

Der Code bleibt erhalten und ist lauffaehig.
