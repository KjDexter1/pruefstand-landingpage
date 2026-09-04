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
