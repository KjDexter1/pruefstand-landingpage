# Risiko-Notiz Fördermittel-Check

**Zweck:** Vorlage für die anwaltliche Prüfung, bevor das Modul einem Kunden
angeboten wird. Kein Rechtsrat, sondern eine Zusammenstellung der Punkte, die
geprüft werden müssen, und der Formulierungen, die derzeit verwendet werden.

Stand: 2026-09-01 · zu prüfen von: _________________ · geprüft am: __________

---

## 1. Rechtsdienstleistungsgesetz (RDG)

**Die Kernfrage an die Anwältin:** Ist das Zusammenstellen von Unterlagen,
das Vorbereiten von Antragsformularen und das Erinnern an Fristen eine
erlaubnispflichtige Rechtsdienstleistung nach § 2 RDG — oder eine bloße
Schreib- und Organisationsleistung?

**Unsere Selbsteinschätzung, die zu bestätigen oder zu verwerfen ist:**
Wir prüfen keinen Einzelfall rechtlich. Wir ordnen Rechnungspositionen
anhand von Stichworten Kategorien zu und zeigen, welche Programme zu einer
Kategorie gehören. Die Beurteilung, ob ein Programm einschlägig ist, findet
bei Träger und Betrieb statt.

**Wo die Grenze reißen könnte:**
- Sobald wir sagen „dafür bekommt ihr X Prozent" statt „dafür könnte
  Programm Y in Frage kommen, prüft das beim Träger".
- Sobald wir zur Antragsgestaltung raten („formulieren Sie es besser so").
- Sobald wir gegenüber dem Träger auftreten oder korrespondieren.

**Derzeit verwendete Formulierungen** (auf `foerdermittel-check.html`, in der
Vorbereitungsmappe und in der Skriptausgabe):

> Wir erbringen eine Schreib- und Organisationsleistung: Unterlagen
> zusammenstellen, Formulare vorbereiten, an Fristen erinnern. Die
> rechtliche Beurteilung eines Programms gehört zu einer Rechtsanwältin,
> einem Steuerberater oder der Beratung des Trägers.

> Ob gefördert wird, entscheidet ausschließlich der Träger. Kein Betrag auf
> unserer Seite ist ein Anspruch.

**Zu klären:** Reicht diese Abgrenzung? Muss sie in die Vertragsunterlage,
nicht nur auf die Website?

## 2. Keine Erfolgsgarantie

Es wird an keiner Stelle ein Bewilligungsergebnis versprochen. Die
Formulierung „Ob gefördert wird, entscheidet ausschließlich der Träger"
steht auf der Seite, in der Mappe und in der Konsolenausgabe des Skripts.

**Zu klären:** Ist die geplante Erfolgsvergütung (Anteil an der ausgezahlten
Förderung) in diesem Zusammenhang zulässig und sinnvoll — oder erzeugt sie
den Anschein einer Beratungsleistung? Alternative wäre eine Pauschale je
vorbereitetem Antrag.

## 3. Haftung für Fristen

Das größte praktische Risiko. Wenn ein Betrieb eine Förderung verliert, weil
eine Frist verstrichen ist, wird die Frage nach der Verantwortung gestellt.

**Was technisch umgesetzt ist:**
- Warnungen zu zwei Zeitpunkten (28 und 14 Tage vor Ablauf)
- Jede Warnung wird mit Zeitstempel in `fristen-protokoll.csv` festgehalten
- Abgelaufene Fristen werden ebenfalls protokolliert

**Was ausdrücklich nicht zugesagt wird:** Vollständigkeit des Katalogs. Das
Skript kennt nur Programme, die jemand eingetragen hat. Ein nicht
eingetragenes Programm erzeugt keine Warnung.

**Zu klären:** Genügt der Protokollnachweis? Muss die Warnung nachweislich
zugestellt sein (E-Mail mit Empfangsbestätigung) statt nur erzeugt?

## 4. Richtigkeit der Programmangaben

Quoten, Fristen und Voraussetzungen ändern sich mehrmals jährlich. Ein
veralteter Katalogeintrag, auf den sich ein Betrieb verlässt, ist ein
Haftungsfall.

**Was technisch umgesetzt ist:** Jeder Katalogeintrag hat die Felder
`geprueft_am` und `geprueft_von`. Solange sie leer sind, weist das Skript
bei jedem Lauf aus, dass der Eintrag nicht verifiziert ist, und die
Vorbereitungsmappe trägt einen entsprechenden Warnkasten.

**Derzeit sind alle Einträge unverifiziert.** Vor der ersten Nutzung mit
einem Kunden muss jeder Eintrag beim Träger gegengeprüft werden.

## 5. Datenschutz

Für dieses Modul werden dieselben Eingangsrechnungen verwendet wie für die
Erstprüfung. Es entstehen keine zusätzlichen Datenkategorien.

**Zu klären:** Deckt die vorhandene Vertraulichkeitserklärung (Zweck:
Prüfung von Eingangsrechnungen) auch die Verwendung für die
Förderrecherche ab, oder ist der Zweck zu erweitern? Die Antwort dürfte
lauten: erweitern, weil Zweckbindung.

Ebenso zu prüfen: Abschnitt 5 der Datenschutzerklärung nennt bisher nur die
Prüfung als Zweck.

## 6. Werbliche Aussagen

Die Value Proposition „Prüfstand holt zu viel gezahltes Geld vom Lieferanten
zurück, der Fördermittel-Check holt staatliches Geld in den Betrieb" ist im
Vertrieb wirksam, aber in dieser Zuspitzung nicht auf die Seite übernommen
worden.

**Grund:** „holt Geld" klingt nach Zusage. Auf der Seite steht stattdessen
„Ihr habt investiert. Für einen Teil davon gibt es Geld vom Staat" — mit dem
Zusatz, dass wir weder beraten noch einreichen.

**Zu klären:** Ist auch diese Formulierung noch zu weit?

---

## Offene Punkte in Kurzform

| Nr. | Frage | Betrifft |
|---|---|---|
| 1 | Ist die Leistung eine Rechtsdienstleistung nach § 2 RDG? | ganzes Modul |
| 2 | Ist die Erfolgsvergütung zulässig und sinnvoll? | Preismodell |
| 3 | Genügt das Fristenprotokoll als Nachweis? | Haftung |
| 4 | Muss die Warnung zugestellt oder nur erzeugt sein? | Haftung |
| 5 | Zweckerweiterung in Vertraulichkeitserklärung nötig? | Datenschutz |
| 6 | Datenschutzerklärung um den Förderzweck ergänzen? | Datenschutz |
| 7 | Sind die Website-Formulierungen ausreichend zurückhaltend? | Werbung |

**Bis diese Punkte geklärt sind, wird das Modul keinem Kunden angeboten.**
Die Seite ist erreichbar, aber im „Danach"-Abschnitt verlinkt und nicht Teil
des Kern-Funnels der Erstprüfung.
