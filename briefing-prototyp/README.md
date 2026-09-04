# Pre-Call-Briefing — Prototyp

Nimmt eine Firmen-Domain und gibt ein belegtes Kurzbriefing als Markdown aus.
Zweck dieses Prototyps ist **nicht**, ein Produkt zu sein, sondern eine einzige
Frage zu beantworten:

> Liefert das etwas, das ein Profi nicht in zwei Minuten selbst sieht —
> oder ist es generischer KI-Text?

## Benutzung

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...

python3 recherche.py econsor.de
python3 recherche.py econsor.de --protokoll   # zeigt, was recherchiert wurde
python3 recherche.py econsor.de --roh         # zusaetzlich das JSON vor der Pruefung
```

Kosten pro Briefing: wenige Cent.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `recherche.py` | Steuerung: ruft das Modell mit Websuche und Seitenabruf auf |
| `schema.py` | Ausgabeschema mit Beleg- und Zitatpflicht |
| `pruefung.py` | **Deterministischer Filter — hier faellt raus, was nicht traegt** |
| `ausgabe.py` | Rendert das Markdown-Briefing |
| `beispiel-econsor.md` | Ein echter Durchlauf, von Hand recherchiert |

## Warum die Trennung wichtig ist

Das Sprachmodell recherchiert und formuliert. **Was durchgeht, entscheidet
Python** — nicht das Modell. Genau wie beim Rechnungspruefer: Extraktion darf
raten, die Bewertung nicht.

`pruefung.py` wirft heraus:

- jede Aussage ohne Quell-URL,
- jede Aussage ohne woertliches Zitat von mindestens 25 Zeichen,
- jede Aussage mit einer Floskel aus der Sperrliste
  („fuehrender Anbieter“, „innovativ“, „gut aufgestellt“, …),
- jede Einstiegsfrage, die auf jede beliebige Firma passt
  („Wo drueckt der Schuh?“).

Bleibt danach weniger als zwei belegte Signale uebrig, wird das Briefing
**automatisch als nicht tragfaehig markiert**. Ein ehrliches „nichts gefunden“
ist brauchbar; ein aufgeblasenes Briefing ist es nicht — es gibt falsche
Sicherheit ins Gespraech hinein.

## Bewusste Beschraenkung: keine Personendaten

Stufe 1 recherchiert ausschliesslich **Unternehmen**: Website, Impressum,
Stellenanzeigen, Presse. Keine LinkedIn-Profile, keine Gespraechspartner,
keine Personensuche.

Das ist keine technische Luecke, sondern eine Entscheidung. Ein Dossier ueber
eine benannte natuerliche Person, kommerziell an einen Dritten geliefert, ist
DSGVO-Kernbereich (Informationspflicht nach Art. 14) und zusaetzlich ein
Verstoss gegen die Nutzungsbedingungen der Netzwerke. Das braucht anwaltliche
Klaerung, bevor es in ein Produkt geht — nicht danach.

Fuer die Produktfrage ist das ohne Belang: ob der Output taugt, zeigt sich an
den Firmendaten genauso.

## Naechster Schritt: der Kenner-Test

Fuenf Firmen nehmen, **die man selbst gut kennt**, und durchlaufen lassen.

- Sagt das Briefing ueber eine bekannte Firma nichts Neues, wird es ueber eine
  fremde erst recht nichts Brauchbares sagen. Dann ist die Idee tot, und zwar
  fuer 20 Minuten Aufwand statt fuer drei Monate.
- Sagt es etwas Nicht-Offensichtliches, geht es weiter: fuenf echte Agenturen,
  je ein fertiges Briefing unaufgefordert per Mail, und die Antwortquote
  entscheidet.

Erst danach lohnt sich ueberhaupt ein Gedanke an Kalender-Anbindung, Abo oder
Weboberflaeche.
