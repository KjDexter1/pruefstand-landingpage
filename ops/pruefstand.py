#!/usr/bin/env python3
"""Betriebssystem fuer den Ein-Mann-Betrieb Pruefstand.

Kein externes Paket noetig. Daten liegen als JSONL neben diesem Skript und
sind damit versionierbar, diffbar und ohne Datenbank sicherungsfaehig.

  ./ops/pruefstand.py lead add --betrieb "Elektro Voss" --gewerk Elektro --quelle Kaltakquise
  ./ops/pruefstand.py lead status <id> demo_gehalten --notiz "Buero war dabei"
  ./ops/pruefstand.py fall add --kunde "Elektro Voss" --lieferant "Nordmann" \
      --ergebnis ok --minuten-manuell 9 --minuten-system 1
  ./ops/pruefstand.py kpi
  ./ops/pruefstand.py regeln
  ./ops/pruefstand.py bericht --woche
"""

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter, defaultdict

BASIS = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(BASIS, "data")
BERICHTE = os.path.join(BASIS, "berichte")

LEADS = os.path.join(DATEN, "leads.jsonl")
FAELLE = os.path.join(DATEN, "faelle.jsonl")

# Stundensatz Buerokraft, identisch zur Rechnung auf der Landingpage.
STUNDENSATZ = 35.0

STATUS = [
    "neu",
    "kontaktiert",
    "demo_geplant",
    "demo_gehalten",
    "pilot",
    "kunde",
    "verloren",
]
ERGEBNIS = ["ok", "korrigiert", "eskaliert", "fehler"]

# Zielwerte aus strategie/02-geschaeftskonzept.md, Tag 90.
ZIELE = {
    "gespraeche": 30,
    "piloten": 3,
    "minuten_gespart": 6.0,
    "zahlende": 1,
}


# --------------------------------------------------------------------------- io

def _lies(pfad):
    if not os.path.exists(pfad):
        return []
    eintraege = []
    with open(pfad, encoding="utf-8") as fh:
        for zeile in fh:
            zeile = zeile.strip()
            if zeile:
                eintraege.append(json.loads(zeile))
    return eintraege


def _schreib(pfad, eintraege):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as fh:
        for e in eintraege:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")


def _anhaenge(pfad, eintrag):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(eintrag, ensure_ascii=False, sort_keys=True) + "\n")


def _jetzt():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _id(praefix, vorhandene):
    return "%s-%03d" % (praefix, len(vorhandene) + 1)


def _datum(eintrag):
    return dt.datetime.fromisoformat(eintrag["ts"]).date()


def _zeitraum(tage):
    heute = dt.date.today()
    return heute - dt.timedelta(days=tage), heute


def _im_zeitraum(eintraege, tage):
    if tage is None:
        return eintraege
    von, _ = _zeitraum(tage)
    return [e for e in eintraege if _datum(e) >= von]


# ------------------------------------------------------------------------ leads

def lead_add(args):
    leads = _lies(LEADS)
    eintrag = {
        "id": _id("L", leads),
        "ts": _jetzt(),
        "betrieb": args.betrieb,
        "gewerk": args.gewerk or "",
        "kontakt": args.kontakt or "",
        "quelle": args.quelle or "unbekannt",
        "status": "neu",
        "notiz": args.notiz or "",
        "verlauf": [],
    }
    _anhaenge(LEADS, eintrag)
    print("angelegt: %s  %s" % (eintrag["id"], eintrag["betrieb"]))


def lead_status(args):
    if args.status not in STATUS:
        sys.exit("unbekannter Status. Erlaubt: %s" % ", ".join(STATUS))
    leads = _lies(LEADS)
    treffer = [l for l in leads if l["id"] == args.id]
    if not treffer:
        sys.exit("kein Lead mit id %s" % args.id)
    lead = treffer[0]
    lead.setdefault("verlauf", []).append(
        {"ts": _jetzt(), "von": lead["status"], "nach": args.status, "notiz": args.notiz or ""}
    )
    lead["status"] = args.status
    _schreib(LEADS, leads)
    print("%s -> %s" % (lead["id"], args.status))


def lead_liste(args):
    leads = _lies(LEADS)
    if args.status:
        leads = [l for l in leads if l["status"] == args.status]
    if not leads:
        print("keine Leads")
        return
    for l in leads:
        print("%-7s %-28s %-14s %-12s %s"
              % (l["id"], l["betrieb"][:28], l["status"], l["quelle"][:12], l.get("gewerk", "")))


def lead_faellig(args):
    """Leads, die seit N Tagen keinen Statuswechsel hatten und noch offen sind."""
    grenze = dt.date.today() - dt.timedelta(days=args.tage)
    offen = []
    for l in _lies(LEADS):
        if l["status"] in ("kunde", "verloren"):
            continue
        verlauf = l.get("verlauf") or []
        letzte = verlauf[-1]["ts"] if verlauf else l["ts"]
        if dt.datetime.fromisoformat(letzte).date() <= grenze:
            offen.append((letzte[:10], l))
    if not offen:
        print("nichts ueberfaellig")
        return
    for letzte, l in sorted(offen, key=lambda x: x[0]):
        print("%-7s %-28s %-14s letzte Aktivitaet %s" % (l["id"], l["betrieb"][:28], l["status"], letzte))


# ------------------------------------------------------------------------ faelle

def fall_add(args):
    if args.ergebnis not in ERGEBNIS:
        sys.exit("unbekanntes Ergebnis. Erlaubt: %s" % ", ".join(ERGEBNIS))
    faelle = _lies(FAELLE)
    eintrag = {
        "id": _id("F", faelle),
        "ts": _jetzt(),
        "kunde": args.kunde,
        "lieferant": args.lieferant or "",
        "belegtyp": args.belegtyp or "XRechnung",
        "ergebnis": args.ergebnis,
        "korrektur": args.korrektur or "",
        "regel_kandidat": args.regel or "",
        "minuten_manuell": args.minuten_manuell,
        "minuten_system": args.minuten_system,
        "notiz": args.notiz or "",
    }
    _anhaenge(FAELLE, eintrag)
    gespart = args.minuten_manuell - args.minuten_system
    print("erfasst: %s  gespart %.1f min" % (eintrag["id"], gespart))


def regeln(args):
    """Korrekturgruende, die sich wiederholen. Das ist das Lern-Backlog."""
    faelle = _im_zeitraum(_lies(FAELLE), args.tage)
    zaehler = Counter()
    je_lieferant = defaultdict(Counter)
    for f in faelle:
        kandidat = (f.get("regel_kandidat") or "").strip()
        if not kandidat:
            continue
        zaehler[kandidat] += 1
        if f.get("lieferant"):
            je_lieferant[f["lieferant"]][kandidat] += 1
    if not zaehler:
        print("noch keine Korrekturmuster erfasst")
        return
    print("Regel-Backlog (ab 2 Vorkommen automatisierungswuerdig)\n")
    for kandidat, n in zaehler.most_common():
        marke = "AUTOMATISIEREN" if n >= 2 else "beobachten"
        print("  %2dx  %-14s %s" % (n, marke, kandidat))
    print("\nWiederkehrende Fehler je Lieferant (der eigentliche Moat)\n")
    for lieferant, c in sorted(je_lieferant.items(), key=lambda x: -sum(x[1].values())):
        top = ", ".join("%s (%dx)" % (k, v) for k, v in c.most_common(3))
        print("  %-24s %s" % (lieferant[:24], top))


# --------------------------------------------------------------------------- kpi

def _kennzahlen(tage=None):
    leads_alle = _lies(LEADS)
    faelle = _im_zeitraum(_lies(FAELLE), tage)

    def hatte_status(lead, status):
        if lead["status"] == status:
            return True
        return any(v.get("nach") == status for v in lead.get("verlauf") or [])

    gespraeche = [l for l in leads_alle if hatte_status(l, "demo_gehalten")]
    piloten = [l for l in leads_alle if hatte_status(l, "pilot")]
    kunden = [l for l in leads_alle if l["status"] == "kunde"]

    minuten = [f["minuten_manuell"] - f["minuten_system"] for f in faelle]
    gespart_gesamt = sum(minuten)
    korrigiert = [f for f in faelle if f["ergebnis"] in ("korrigiert", "eskaliert", "fehler")]
    eskaliert = [f for f in faelle if f["ergebnis"] == "eskaliert"]

    return {
        "leads_gesamt": len(leads_alle),
        "leads_offen": len([l for l in leads_alle if l["status"] not in ("kunde", "verloren")]),
        "gespraeche": len(gespraeche),
        "piloten": len(piloten),
        "zahlende": len(kunden),
        "faelle": len(faelle),
        "minuten_gespart_schnitt": (gespart_gesamt / len(minuten)) if minuten else 0.0,
        "stunden_gespart": gespart_gesamt / 60.0,
        "wert_euro": gespart_gesamt / 60.0 * STUNDENSATZ,
        "automationsquote": (1 - len(korrigiert) / len(faelle)) * 100 if faelle else 0.0,
        "eskalationsquote": (len(eskaliert) / len(faelle)) * 100 if faelle else 0.0,
    }


def _ampel(wert, ziel):
    if wert >= ziel:
        return "erreicht"
    if ziel and wert >= ziel * 0.5:
        return "auf Kurs"
    return "offen"


def kpi(args):
    k = _kennzahlen(args.tage)
    spanne = "letzte %d Tage" % args.tage if args.tage else "gesamt"
    print("Kennzahlen (%s)\n" % spanne)
    print("  Leads gesamt / offen        %d / %d" % (k["leads_gesamt"], k["leads_offen"]))
    print("  Erstgespraeche gefuehrt     %d   (Ziel 90 Tage: %d, %s)"
          % (k["gespraeche"], ZIELE["gespraeche"], _ampel(k["gespraeche"], ZIELE["gespraeche"])))
    print("  Betriebe im Piloten         %d   (Ziel: %d, %s)"
          % (k["piloten"], ZIELE["piloten"], _ampel(k["piloten"], ZIELE["piloten"])))
    print("  Zahlende Kunden             %d   (Ziel: %d, %s)"
          % (k["zahlende"], ZIELE["zahlende"], _ampel(k["zahlende"], ZIELE["zahlende"])))
    print()
    print("  Bearbeitete Belege          %d" % k["faelle"])
    print("  Gesparte Minuten je Beleg   %.1f (Ziel: %.1f, %s)"
          % (k["minuten_gespart_schnitt"], ZIELE["minuten_gespart"],
             _ampel(k["minuten_gespart_schnitt"], ZIELE["minuten_gespart"])))
    print("  Gesparte Bearbeitungszeit   %.1f Std  entspricht %.0f EUR bei %.0f EUR/Std"
          % (k["stunden_gespart"], k["wert_euro"], STUNDENSATZ))
    print("  Ohne Eingriff durchgelaufen %.0f %%" % k["automationsquote"])
    print("  Eskalationsquote            %.0f %%" % k["eskalationsquote"])


# ----------------------------------------------------------------------- bericht

CHECKLISTE_WOCHE = [
    "10 neue Betriebe kontaktiert (Telefon, nicht E-Mail)",
    "Alle Leads ohne Aktivitaet seit 7 Tagen nachgefasst (`lead faellig`)",
    "1 Steuerberater-Kanzlei angesprochen (Kanal mit dem besten Hebel)",
    "Alle Korrekturen der Woche als `regel_kandidat` erfasst",
    "Top-Regel aus dem Backlog umgesetzt oder verworfen",
    "ROI-Zahlen der Landingpage gegen echte Messwerte geprueft",
]

CHECKLISTE_MONAT = [
    "Preis-Hypothese gegen die tatsaechlich gesparte Zeit gehalten",
    "Wettbewerb geprueft: was koennen DATEV / sevDesk / lexoffice inzwischen",
    "Loeschkonzept angewendet: Belege ueber Aufbewahrungszweck hinaus entfernt",
    "AI-Act Art. 50: Kennzeichnung KI-gestuetzter Ausgaben noch korrekt",
    "Abbruchkriterium geprueft (Tag 90: mindestens 1 zahlender Kunde oder Kanzleivertrag)",
    "Entscheidung dokumentiert: weiter, verticalisieren oder stoppen",
]


def _md_tabelle(kennzahlen):
    zeilen = [
        "| Kennzahl | Wert | Ziel |",
        "|---|---|---|",
        "| Erstgespraeche | %d | %d |" % (kennzahlen["gespraeche"], ZIELE["gespraeche"]),
        "| Betriebe im Piloten | %d | %d |" % (kennzahlen["piloten"], ZIELE["piloten"]),
        "| Zahlende Kunden | %d | %d |" % (kennzahlen["zahlende"], ZIELE["zahlende"]),
        "| Offene Leads | %d | – |" % kennzahlen["leads_offen"],
        "| Bearbeitete Belege | %d | – |" % kennzahlen["faelle"],
        "| Gesparte Minuten je Beleg | %.1f | %.1f |"
        % (kennzahlen["minuten_gespart_schnitt"], ZIELE["minuten_gespart"]),
        "| Gesparte Zeit | %.1f Std (%.0f EUR) | – |"
        % (kennzahlen["stunden_gespart"], kennzahlen["wert_euro"]),
        "| Ohne Eingriff durchgelaufen | %.0f %% | 80 %% |" % kennzahlen["automationsquote"],
        "| Eskalationsquote | %.0f %% | < 10 %% |" % kennzahlen["eskalationsquote"],
    ]
    return "\n".join(zeilen)


def _regel_backlog_md(tage):
    faelle = _im_zeitraum(_lies(FAELLE), tage)
    zaehler = Counter(
        (f.get("regel_kandidat") or "").strip() for f in faelle if (f.get("regel_kandidat") or "").strip()
    )
    if not zaehler:
        return "_Keine Korrekturmuster erfasst. Ohne Korrekturen kein Lernen — das ist die wichtigste Luecke._"
    zeilen = ["| Vorkommen | Muster | Aktion |", "|---|---|---|"]
    for kandidat, n in zaehler.most_common(10):
        aktion = "als Regel umsetzen" if n >= 2 else "beobachten"
        zeilen.append("| %dx | %s | %s |" % (n, kandidat, aktion))
    return "\n".join(zeilen)


def bericht(args):
    tage = 30 if args.monat else 7
    titel = "Monatslauf" if args.monat else "Wochenlauf"
    checkliste = CHECKLISTE_MONAT if args.monat else CHECKLISTE_WOCHE
    heute = dt.date.today()
    kw = heute.isocalendar()
    kennung = "%d-%02d" % (heute.year, heute.month) if args.monat else "%d-KW%02d" % (kw[0], kw[1])

    k_zeitraum = _kennzahlen(tage)
    k_gesamt = _kennzahlen(None)

    teile = [
        "# %s %s" % (titel, kennung),
        "",
        "Erzeugt am %s. Datenbasis: `ops/data/`." % heute.isoformat(),
        "",
        "## Kennzahlen — letzte %d Tage" % tage,
        "",
        _md_tabelle(k_zeitraum),
        "",
        "## Kennzahlen — gesamt",
        "",
        _md_tabelle(k_gesamt),
        "",
        "## Regel-Backlog (Lernschleife)",
        "",
        "Wiederkehrende Korrekturen sind der einzige Datensatz, der ueber die Zeit einen",
        "Vorsprung erzeugt. Alles ab 2 Vorkommen gehoert in eine feste Regel.",
        "",
        _regel_backlog_md(tage),
        "",
        "## Ueberfaellige Leads",
        "",
    ]

    grenze = heute - dt.timedelta(days=7)
    ueberfaellig = []
    for l in _lies(LEADS):
        if l["status"] in ("kunde", "verloren"):
            continue
        verlauf = l.get("verlauf") or []
        letzte = verlauf[-1]["ts"] if verlauf else l["ts"]
        if dt.datetime.fromisoformat(letzte).date() <= grenze:
            ueberfaellig.append("- `%s` %s — Status %s, letzte Aktivitaet %s"
                                % (l["id"], l["betrieb"], l["status"], letzte[:10]))
    teile.append("\n".join(ueberfaellig) if ueberfaellig
                 else "_Keine. Alle offenen Leads wurden in den letzten 7 Tagen bewegt._")

    teile += ["", "## Checkliste", ""]
    teile += ["- [ ] %s" % punkt for punkt in checkliste]

    if k_gesamt["gespraeche"] < ZIELE["gespraeche"] and k_gesamt["zahlende"] == 0:
        teile += [
            "",
            "## Hinweis",
            "",
            "Weniger als %d Erstgespraeche und kein zahlender Kunde. In dieser Phase ist"
            % ZIELE["gespraeche"],
            "jede Stunde Entwicklung eine Stunde zu wenig Vertrieb.",
        ]

    text = "\n".join(teile) + "\n"

    os.makedirs(BERICHTE, exist_ok=True)
    pfad = os.path.join(BERICHTE, "%s-%s.md" % ("monat" if args.monat else "woche", kennung))
    with open(pfad, "w", encoding="utf-8") as fh:
        fh.write(text)

    if args.stdout:
        sys.stdout.write(text)
    else:
        print("geschrieben: %s" % os.path.relpath(pfad, os.path.dirname(BASIS)))

    # Titel fuer die GitHub Action, damit sie ihn nicht selbst bauen muss.
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write("titel=%s %s\n" % (titel, kennung))
            fh.write("pfad=%s\n" % os.path.relpath(pfad, os.path.dirname(BASIS)))


# -------------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Pruefstand Betriebssystem")
    sub = p.add_subparsers(dest="bereich", required=True)

    pl = sub.add_parser("lead", help="Vertriebskontakte").add_subparsers(dest="aktion", required=True)

    a = pl.add_parser("add")
    a.add_argument("--betrieb", required=True)
    a.add_argument("--gewerk")
    a.add_argument("--kontakt")
    a.add_argument("--quelle")
    a.add_argument("--notiz")
    a.set_defaults(fn=lead_add)

    a = pl.add_parser("status")
    a.add_argument("id")
    a.add_argument("status", choices=STATUS)
    a.add_argument("--notiz")
    a.set_defaults(fn=lead_status)

    a = pl.add_parser("liste")
    a.add_argument("--status", choices=STATUS)
    a.set_defaults(fn=lead_liste)

    a = pl.add_parser("faellig")
    a.add_argument("--tage", type=int, default=7)
    a.set_defaults(fn=lead_faellig)

    pf = sub.add_parser("fall", help="Bearbeitete Belege mit Ergebnis").add_subparsers(
        dest="aktion", required=True)

    a = pf.add_parser("add")
    a.add_argument("--kunde", required=True)
    a.add_argument("--lieferant")
    a.add_argument("--belegtyp")
    a.add_argument("--ergebnis", required=True, choices=ERGEBNIS)
    a.add_argument("--korrektur", help="Was musste ein Mensch aendern")
    a.add_argument("--regel", help="Kurzname des Musters, z.B. 'IBAN fehlt'")
    a.add_argument("--minuten-manuell", dest="minuten_manuell", type=float, default=9.0)
    a.add_argument("--minuten-system", dest="minuten_system", type=float, default=0.5)
    a.add_argument("--notiz")
    a.set_defaults(fn=fall_add)

    a = sub.add_parser("regeln", help="Wiederkehrende Korrekturen")
    a.add_argument("--tage", type=int, default=None)
    a.set_defaults(fn=regeln)

    a = sub.add_parser("kpi", help="Kennzahlen")
    a.add_argument("--tage", type=int, default=None)
    a.set_defaults(fn=kpi)

    a = sub.add_parser("bericht", help="Wochen- oder Monatsbericht schreiben")
    a.add_argument("--woche", action="store_true")
    a.add_argument("--monat", action="store_true")
    a.add_argument("--stdout", action="store_true")
    a.set_defaults(fn=bericht)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
