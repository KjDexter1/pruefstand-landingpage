# ops — Betriebssystem

Ein Python-Skript ohne externe Abhängigkeiten (`pruefstand.py`), zwei JSONL-Dateien
und drei GitHub Actions. Mehr braucht ein Ein-Personen-Betrieb nicht.

## Befehle

```bash
# Vertrieb
./ops/pruefstand.py lead add --betrieb "Elektro Voss" --gewerk Elektro --quelle Kaltakquise
./ops/pruefstand.py lead status L-001 demo_gehalten --notiz "Büro war dabei"
./ops/pruefstand.py lead liste --status pilot
./ops/pruefstand.py lead faellig --tage 7        # wer wurde zu lange nicht angefasst

# Bearbeitete Belege (die Lernschleife)
./ops/pruefstand.py fall add --kunde "Elektro Voss" --lieferant "Nordmann" \
    --ergebnis korrigiert --regel "IBAN fehlt" --minuten-manuell 9 --minuten-system 1

# Auswertung
./ops/pruefstand.py kpi --tage 30
./ops/pruefstand.py regeln                        # wiederkehrende Fehler je Lieferant
./ops/pruefstand.py bericht --woche --stdout
```

Statuswerte: `neu, kontaktiert, demo_geplant, demo_gehalten, pilot, kunde, verloren`
Ergebniswerte: `ok, korrigiert, eskaliert, fehler`

## Wiederkehrende Läufe

| Workflow | Zeitplan (UTC) | Ergebnis |
|---|---|---|
| `wochenlauf.yml` | Mo 04:00 | Bericht committet + Issue mit Wochen-Checkliste |
| `monatslauf.yml` | 1. um 05:00 | Monatsbericht + Issue mit Preis-/Compliance-/Abbruchprüfung |
| `seitencheck.yml` | täglich 06:30 + bei HTML-Push | Pflichtseiten, tote Verweise, Kontaktadresse |

Alle drei sind zusätzlich über *Actions → Run workflow* manuell auslösbar.

Voraussetzung: Settings → Actions → General → Workflow permissions auf
**Read and write** stellen, sonst schlägt der Commit der Berichte fehl.

## Zielwerte

Stehen als `ZIELE` oben in `pruefstand.py` und stammen aus
`strategie/02-geschaeftskonzept.md`. Wenn sich die Strategie ändert, dort anpassen —
die Berichte ziehen sie automatisch.
