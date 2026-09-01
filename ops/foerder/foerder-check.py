#!/usr/bin/env python3
"""Fördermittel-Check: erkennt förderfähige Investitionen in Eingangsrechnungen.

Liest dieselben Rechnungen wie der Preisverlauf-Prüfer (XRechnung UBL/CII,
ZUGFeRD-PDF) oder eine CSV, ordnet Positionen anhand von Stichworten einer
Kategorie zu und gleicht sie gegen ops/foerder/foerdermittel.json ab.

  ./ops/foerder/foerder-check.py --ordner ops/preise/beispiel
  ./ops/foerder/foerder-check.py --csv positionen.csv --mappe mappe.html

Was dieses Skript ausdrücklich NICHT tut:
  - Es entscheidet nicht über Förderfähigkeit. Das tut allein der Träger.
  - Es reicht nichts ein. Ämter haben keine Schnittstellen dafür.
  - Es ersetzt keine Rechtsberatung.
Es erzeugt einen Hinweis und eine Vorbereitungsmappe. Mehr nicht.
"""

import argparse
import csv
import datetime as dt
import html
import json
import os
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(HIER))
KATALOG = os.path.join(HIER, "foerdermittel.json")
PROTOKOLL = os.path.join(HIER, "fristen-protokoll.csv")

WARNUNG_TAGE = [14, 28]  # aufsteigend, damit immer die schaerfste Stufe greift


# --------------------------------------------------------------- Rechnungen

def lade_leser():
    """Nutzt den Parser des Preisverlauf-Prüfers, statt ihn zu verdoppeln."""
    pfad = os.path.join(WURZEL, "ops", "preise")
    if pfad not in sys.path:
        sys.path.insert(0, pfad)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "preisverlauf", os.path.join(pfad, "preisverlauf.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def aus_ordner(ordner):
    pv = lade_leser()
    dateien = sorted(os.path.join(ordner, n) for n in os.listdir(ordner)
                     if n.lower().endswith((".xml", ".pdf")))
    positionen, uebersprungen = [], []
    for pfad in dateien:
        daten, fehler = pv.lies_datei(pfad)
        if not daten:
            uebersprungen.append((os.path.basename(pfad), fehler))
            continue
        for pos in daten["positionen"]:
            positionen.append({
                "lieferant": daten["lieferant"],
                "rechnung": daten["rechnung"],
                "datum": daten["datum"],
                "artikel": pos["artikel"] or pos["nummer"],
                "betrag": (pos["menge"] or 0.0) * pos["preis"],
            })
    return positionen, uebersprungen


def aus_csv(pfad):
    """Erwartet: Lieferant;Rechnung;Datum;Artikel;Betrag"""
    positionen = []
    with open(pfad, encoding="utf-8-sig", newline="") as fh:
        for i, zeile in enumerate(csv.DictReader(fh, delimiter=";"), start=2):
            schluessel = {k.lower().strip(): (v or "").strip() for k, v in zeile.items() if k}
            betrag = schluessel.get("betrag", "0").replace(".", "").replace(",", ".")
            try:
                betrag = float(betrag)
            except ValueError:
                sys.exit("%s Zeile %d: Betrag '%s' nicht lesbar" % (pfad, i, schluessel.get("betrag")))
            datum = None
            for form in ("%d.%m.%Y", "%Y-%m-%d"):
                try:
                    datum = dt.datetime.strptime(schluessel.get("datum", ""), form).date()
                    break
                except ValueError:
                    continue
            positionen.append({
                "lieferant": schluessel.get("lieferant", ""),
                "rechnung": schluessel.get("rechnung", ""),
                "datum": datum,
                "artikel": schluessel.get("artikel", ""),
                "betrag": betrag,
            })
    return positionen, []


# ---------------------------------------------------------------- Zuordnung

def kategorisiere(positionen, kategorien):
    treffer = defaultdict(list)
    ohne = []
    for pos in positionen:
        text = (pos["artikel"] or "").lower()
        zugeordnet = False
        for kuerzel, kat in kategorien.items():
            if any(w in text for w in kat["stichworte"]):
                treffer[kuerzel].append(pos)
                zugeordnet = True
                break
        if not zugeordnet:
            ohne.append(pos)
    return treffer, ohne


def tage_bis(frist):
    if not frist or frist == "laufend":
        return None
    try:
        ziel = dt.datetime.strptime(frist, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (ziel - dt.date.today()).days


def protokolliere(zeilen):
    neu = not os.path.exists(PROTOKOLL)
    with open(PROTOKOLL, "a", encoding="utf-8", newline="") as fh:
        s = csv.writer(fh, delimiter=";")
        if neu:
            s.writerow(["Zeitpunkt", "Programm", "Frist", "Tage_verbleibend", "Stufe"])
        for z in zeilen:
            s.writerow(z)


# ----------------------------------------------------------------- Ausgabe

def euro(w):
    return "{:,.2f}".format(w).replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def mappe_schreiben(pfad, betrieb, funde, katalog):
    """Vorbereitungsmappe als HTML - im Browser mit Strg+P als PDF speichern."""
    heute = dt.date.today().strftime("%d.%m.%Y")
    teile = ["""<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>Fördermittel-Vorbereitung</title><style>
body{font:14px/1.6 Arial,sans-serif;color:#1F2A28;max-width:820px;margin:0 auto;padding:32px}
h1{font-size:26px;margin:0 0 4px} h2{font-size:16px;margin:28px 0 10px;color:#0E5B50;
  border-bottom:2px solid #0E5B50;padding-bottom:5px;text-transform:uppercase;letter-spacing:.06em}
.kopf{border-bottom:3px solid #1F2A28;padding-bottom:14px;margin-bottom:22px;color:#5B6A67;font-size:13px}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
th,td{border:1px solid #D3DAD7;padding:8px 10px;text-align:left;vertical-align:top}
th{background:#F1F5F3;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#5B6A67}
.warn{background:#F5E3DC;border-left:4px solid #A9451B;padding:14px 16px;margin:16px 0;font-size:13px}
.warn b{color:#A9451B}
ul{margin:8px 0 8px 18px} li{margin-bottom:5px}
.fuss{margin-top:32px;border-top:1px solid #D3DAD7;padding-top:12px;font-size:11px;color:#8A9794}
@media print{body{padding:0}}
</style></head><body>""",
      "<h1>Fördermittel — Vorbereitung</h1>",
      '<div class="kopf">Betrieb: <b>%s</b> · Erstellt am %s · Prüfstand, Faruk Polat</div>'
      % (html.escape(betrieb), heute),
      '<div class="warn"><b>Kein Förderbescheid und keine Zusage.</b> Diese Mappe fasst zusammen, '
      'welche Investitionen in den Rechnungen aufgefallen sind und welche Programme dazu passen könnten. '
      'Ob ein Programm einschlägig ist und ob bewilligt wird, entscheidet ausschließlich der jeweilige Träger. '
      'Prüfstand erbringt eine Schreib- und Organisationsleistung, keine Rechts- oder Förderberatung. '
      'Der Antrag wird vom Betrieb selbst geprüft, unterschrieben und eingereicht.</div>']

    for f in funde:
        p = f["programm"]
        ungeprueft = not p.get("geprueft_am")
        teile.append("<h2>%s</h2>" % html.escape(p["name"]))
        if ungeprueft:
            teile.append('<div class="warn"><b>Katalogeintrag nicht verifiziert.</b> '
                         'Angaben zu diesem Programm wurden noch nicht beim Träger gegengeprüft '
                         'und dürfen so nicht an einen Betrieb weitergegeben werden.</div>')
        teile.append("<table><tr><th>Träger</th><td>%s</td></tr>"
                     "<tr><th>Kategorie</th><td>%s</td></tr>"
                     "<tr><th>Erkannte Investition</th><td>%s in %d Position(en)</td></tr>"
                     "<tr><th>Frist</th><td>%s</td></tr>"
                     "<tr><th>Antrag vor Investition</th><td>%s</td></tr>"
                     "<tr><th>Quelle</th><td>%s</td></tr></table>"
                     % (html.escape(p["traeger"]), html.escape(f["kategorie_name"]),
                        euro(f["summe"]), len(f["positionen"]),
                        html.escape(str(p.get("frist") or "unbekannt")),
                        "ja — bereits bezahlte Rechnungen sind dann nicht mehr förderfähig"
                        if p.get("antrag_vor_investition") else "unbekannt",
                        html.escape(p.get("quelle", ""))))
        if p.get("notiz"):
            teile.append("<p>%s</p>" % html.escape(p["notiz"]))
        teile.append("<table><tr><th>Rechnung</th><th>Datum</th><th>Position</th><th>Betrag</th></tr>")
        for pos in f["positionen"]:
            teile.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                         % (html.escape(pos["rechnung"]),
                            pos["datum"].strftime("%d.%m.%Y") if pos["datum"] else "",
                            html.escape(pos["artikel"][:60]), euro(pos["betrag"])))
        teile.append("</table>")
        teile.append("<p><b>Checkliste vor der Antragstellung</b></p><ul>"
                     "<li>Beim Träger prüfen, ob das Programm noch läuft und für den Betrieb offensteht</li>"
                     "<li>Klären, ob der Antrag vor Vorhabenbeginn nötig war — sonst ist die Investition raus</li>"
                     "<li>Rechnungen, Angebote und Zahlungsnachweise zusammenstellen</li>"
                     "<li>Betriebsgröße, Umsatz und Beschäftigtenzahl bereithalten</li>"
                     "<li>Bei energetischen Maßnahmen: ist ein Energieeffizienz-Experte einzubinden?</li>"
                     "<li>Antrag durch den Betrieb prüfen und unterschreiben lassen</li>"
                     "<li>Einreichung durch den Betrieb, nicht durch Prüfstand</li></ul>")

    teile.append('<div class="fuss">Prüfstand · Faruk Polat · In den Rübgärten 17 · 61476 Kronberg im Taunus '
                 '· 0152 28487769 · farukpolat@mail.de<br>'
                 'Diese Mappe ist eine Vorbereitungshilfe. Keine Rechtsdienstleistung, keine Förderberatung, '
                 'keine Gewähr für Vollständigkeit oder Bewilligung.</div></body></html>')
    with open(pfad, "w", encoding="utf-8") as fh:
        fh.write("\n".join(teile))


def main():
    ap = argparse.ArgumentParser(description="Förderfähige Investitionen in Rechnungen erkennen")
    quelle = ap.add_mutually_exclusive_group(required=True)
    quelle.add_argument("--ordner", help="Ordner mit XML-/PDF-Rechnungen")
    quelle.add_argument("--csv", help="CSV: Lieferant;Rechnung;Datum;Artikel;Betrag")
    ap.add_argument("--betrieb", default="", help="Name des Betriebs für die Mappe")
    ap.add_argument("--mappe", help="Vorbereitungsmappe als HTML schreiben")
    args = ap.parse_args()

    with open(KATALOG, encoding="utf-8") as fh:
        katalog = json.load(fh)

    if args.ordner:
        if not os.path.isdir(args.ordner):
            sys.exit("Ordner nicht gefunden: %s" % args.ordner)
        positionen, uebersprungen = aus_ordner(args.ordner)
    else:
        if not os.path.isfile(args.csv):
            sys.exit("Datei nicht gefunden: %s" % args.csv)
        positionen, uebersprungen = aus_csv(args.csv)

    for name, grund in uebersprungen:
        print("  uebersprungen: %-28s %s" % (name, grund))
    if not positionen:
        sys.exit("Keine auswertbaren Positionen gefunden.")

    ungeprueft = [p["id"] for p in katalog["programme"] if not p.get("geprueft_am")]
    if ungeprueft:
        print("\n  ACHTUNG: %d von %d Katalogeintraegen sind nicht verifiziert (%s)."
              % (len(ungeprueft), len(katalog["programme"]), ", ".join(ungeprueft)))
        print("  Diese Ergebnisse duerfen so keinem Betrieb vorgelegt werden.\n")

    treffer, ohne = kategorisiere(positionen, katalog["kategorien"])
    print("%d Positionen gelesen, %d einer Kategorie zugeordnet, %d ohne Zuordnung"
          % (len(positionen), len(positionen) - len(ohne), len(ohne)))

    if not treffer:
        print("\nKeine förderfähig aussehende Investition erkannt.")
        print("Das ist ein Ergebnis, kein Fehler — die meisten Eingangsrechnungen sind Material.")
        return

    funde, protokollzeilen = [], []
    jetzt = dt.datetime.now().replace(microsecond=0).isoformat()
    print("\nMögliche Programme\n")
    for kuerzel, posten in sorted(treffer.items(), key=lambda x: -sum(p["betrag"] for p in x[1])):
        summe = sum(p["betrag"] for p in posten)
        kat = katalog["kategorien"][kuerzel]
        passende = [p for p in katalog["programme"] if p["kategorie"] == kuerzel]
        if not passende:
            continue
        print("  %s — %s in %d Position(en)" % (kat["bezeichnung"], euro(summe), len(posten)))
        for prog in passende:
            tage = tage_bis(prog.get("frist"))
            if tage is None:
                hinweis = "laufend"
            elif tage <= 0:
                hinweis = "Frist abgelaufen"
            else:
                hinweis = "noch %d Tage" % tage
            marke = "" if prog.get("geprueft_am") else "   [NICHT VERIFIZIERT]"
            print("      %s  (%s)%s" % (prog["name"][:66], hinweis, marke))
            if tage is not None:
                for stufe in WARNUNG_TAGE:
                    if 0 < tage <= stufe:
                        print("        FRIST: nur noch %d Tage — Stufe T-%d" % (tage, stufe))
                        protokollzeilen.append([jetzt, prog["id"], prog["frist"], tage, "T-%d" % stufe])
                        break
                if tage <= 0:
                    print("        FRIST ABGELAUFEN")
                    protokollzeilen.append([jetzt, prog["id"], prog["frist"], tage, "abgelaufen"])
            funde.append({"programm": prog, "kategorie_name": kat["bezeichnung"],
                          "summe": summe, "positionen": posten})
        print()

    if protokollzeilen:
        protokolliere(protokollzeilen)
        print("  %d Fristwarnung(en) protokolliert in %s"
              % (len(protokollzeilen), os.path.relpath(PROTOKOLL, WURZEL)))

    print("  Kein Treffer ist eine Zusage. Ob ein Programm einschlaegig ist und ob")
    print("  bewilligt wird, entscheidet allein der Traeger. Eingereicht wird vom Betrieb.")

    if args.mappe:
        mappe_schreiben(args.mappe, args.betrieb or "Betrieb", funde, katalog)
        print("\n  geschrieben: %s  (im Browser oeffnen, Strg+P fuer PDF)" % args.mappe)


if __name__ == "__main__":
    main()
