# Das Betriebssystem für eine Person

Der wiederkehrende Ablauf, der aus dem Konzept tatsächlich Betrieb macht.
Alles hiervon läuft ohne fremden Dienst, ohne Abo und ohne Server.

## Warum überhaupt Automatisierung an dieser Stelle

Beide PDFs empfehlen im Kern dasselbe: Ergebnisse messen, Korrekturen sammeln,
daraus Regeln machen. Der Grund, warum das in Ein-Personen-Betrieben fast nie
passiert, ist nicht fehlendes Wissen, sondern fehlende Erinnerung. Deshalb ist die
Automatisierung hier bewusst nicht die Rechnungsprüfung selbst — die ist das Produkt —
sondern **die Disziplin drumherum**.

## Der Takt

| Rhythmus | Auslöser | Was passiert | Dein Aufwand |
|---|---|---|---|
| täglich | GitHub Action `Seitencheck` | Pflichtseiten, interne Verweise, Kontaktadresse | 0 min, nur bei Fehler eine Mail |
| pro Gespräch | du, sofort danach | `lead add` / `lead status` | 15 Sek |
| pro Beleg im Piloten | du oder später das Produkt | `fall add` mit Ergebnis und Korrektur | 20 Sek |
| montags 06:00 | GitHub Action `Wochenlauf` | Bericht + Issue mit Kennzahlen, überfälligen Leads, Regel-Backlog, Checkliste | 20 min lesen und abhaken |
| 1. des Monats | GitHub Action `Monatslauf` | Preis, Wettbewerb, Löschkonzept, AI-Act, Abbruchkriterium | 45 min |

Die beiden Berichtsläufe committen ihr Ergebnis nach `ops/berichte/`. Damit entsteht
nebenbei eine lückenlose Historie: nach sechs Monaten liegen 26 Wochenberichte vor,
aus denen der tatsächliche Verlauf ablesbar ist statt einer Erinnerung daran.

## Die einzige Regel, die du einhalten musst

**Jede Korrektur wird erfasst, bevor du sie vergisst.**

```
./ops/pruefstand.py fall add --kunde "Elektro Voss" --lieferant "Nordmann" \
    --ergebnis korrigiert --regel "IBAN fehlt" \
    --minuten-manuell 9 --minuten-system 1
```

Ab dem zweiten identischen `regel_kandidat` erscheint das Muster im Wochenbericht mit
der Markierung `AUTOMATISIEREN`. Das ist der komplette Lernmechanismus — kein Training,
kein Modell, keine Pipeline. Genau das, was bei 50 Fällen pro Woche angemessen ist.

## Was daraus über die Zeit entsteht

Nach ein paar Monaten beantwortet `pruefstand.py regeln` eine Frage, die sonst niemand
in der Branche beantworten kann: **Welcher Lieferant baut welchen Fehler wie oft ein?**

Das ist der Moat aus den beiden PDFs, übersetzt in etwas, das eine Person tatsächlich
aufbauen kann. Es ist kein Datenberg. Es ist eine Liste, die stimmt.

Verkaufsseitig wird daraus ein Satz, den kein Wettbewerber sagen kann:
*„Bei eurem Hauptlieferanten fehlt in jeder dritten Rechnung die Skontofrist — wir
fangen das ab, bevor es euch Geld kostet."*

## Einrichtung

Einmalig, danach läuft es:

1. Repository auf GitHub, Actions aktiviert (Settings → Actions → Allow all).
2. Settings → Actions → General → Workflow permissions: **Read and write**.
   Ohne das können Wochen- und Monatslauf ihren Bericht nicht committen.
3. Optional Labels `wochenlauf` und `monatslauf` anlegen — fehlen sie, legt der
   Lauf das Issue ohne Label an.
4. Ersten Lauf manuell testen: Actions → Wochenlauf → Run workflow.

Cron-Zeiten in UTC: Wochenlauf Mo 04:00 (06:00 Berlin Sommerzeit),
Monatslauf am 1. um 05:00, Seitencheck täglich 06:30.

## Was bewusst nicht automatisiert ist

- **Akquise.** 10 Anrufe pro Woche macht kein Skript. Der Wochenlauf erinnert nur daran.
- **Die Bewertung der Zahlen.** Der Bericht rechnet; entscheiden musst du.
- **Der Abbruch.** Steht als Punkt in der Monats-Checkliste, damit er nicht still
  übergangen wird. Das ist der Zweck der ganzen Konstruktion.
