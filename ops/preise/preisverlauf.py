#!/usr/bin/env python3
"""Findet stille Preiserhoehungen in elektronischen Eingangsrechnungen.

Liest XRechnung (UBL und CII) sowie ZUGFeRD/Factur-X (XML im PDF),
gruppiert alle Positionen je Lieferant und Artikel, sortiert sie nach
Datum und meldet jede Preisaenderung nach oben.

  ./ops/preise/preisverlauf.py --ordner ops/preise/beispiel
  ./ops/preise/preisverlauf.py --ordner ~/rechnungen --csv funde-vorschlag.csv

Die erzeugte CSV hat genau das Format von ops/bericht/funde.csv und kann
dort hineinkopiert werden.

Wichtig: Jeder Fund wird als "zu klaeren" ausgegeben, nicht als "sicher".
Eine Preiserhoehung kann angekuendigt und vereinbart gewesen sein. Ob sie
berechtigt war, entscheidet ein Mensch anhand der Konditionsvereinbarung.
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

# Preisaenderungen unterhalb dieser Schwellen gelten als Rundung.
MIN_ABWEICHUNG_EUR = 0.01
MIN_ABWEICHUNG_PROZENT = 0.5


# --------------------------------------------------------------- XML-Zugriff
# Die Formate unterscheiden sich in den Namensraeumen, nicht in den Namen.
# Deshalb wird durchgaengig ueber den lokalen Namen gesucht; das haelt auch
# ueber ZUGFeRD-Versionen hinweg.

def lokal(element):
    return element.tag.rsplit("}", 1)[-1] if "}" in element.tag else element.tag


def finde_alle(wurzel, pfad):
    """Sucht einen Pfad lokaler Namen, z. B. ['Item', 'Name']."""
    aktuell = [wurzel]
    for name in pfad:
        naechste = []
        for el in aktuell:
            naechste.extend(k for k in el if lokal(k) == name)
        aktuell = naechste
    return aktuell


def finde(wurzel, pfad, standard=None):
    treffer = finde_alle(wurzel, pfad)
    return treffer[0] if treffer else standard


def text_von(wurzel, pfad, standard=""):
    el = finde(wurzel, pfad)
    return (el.text or "").strip() if el is not None else standard


def tief_suchen(wurzel, name):
    """Erster Nachfahre mit diesem lokalen Namen, egal wie tief."""
    for el in wurzel.iter():
        if lokal(el) == name:
            return el
    return None


def zahl(text):
    if not text:
        return None
    t = text.strip().replace(" ", "")
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def datum_von(text):
    t = (text or "").strip()
    for form in ("%Y-%m-%d", "%Y%m%d", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(t[:10] if form == "%Y-%m-%d" else t[:8] if form == "%Y%m%d" else t[:10], form).date()
        except ValueError:
            continue
    return None


# ------------------------------------------------------------------- Formate

def lies_ubl(wurzel):
    """XRechnung in UBL-Syntax."""
    lieferant = ""
    partei = finde(wurzel, ["AccountingSupplierParty", "Party"])
    if partei is not None:
        lieferant = (text_von(partei, ["PartyName", "Name"])
                     or text_von(partei, ["PartyLegalEntity", "RegistrationName"]))

    rechnung = text_von(wurzel, ["ID"])
    datum = datum_von(text_von(wurzel, ["IssueDate"]))

    positionen = []
    for zeile in finde_alle(wurzel, ["InvoiceLine"]):
        artikel = finde(zeile, ["Item"])
        if artikel is None:
            continue
        name = text_von(artikel, ["Name"])
        nummer = (text_von(artikel, ["SellersItemIdentification", "ID"])
                  or text_von(artikel, ["StandardItemIdentification", "ID"]))
        menge = zahl(text_von(zeile, ["InvoicedQuantity"]))
        preis = zahl(text_von(zeile, ["Price", "PriceAmount"]))
        if preis is None or not (name or nummer):
            continue
        positionen.append({"artikel": name, "nummer": nummer,
                           "menge": menge or 0.0, "preis": preis})
    return lieferant, rechnung, datum, positionen


def lies_cii(wurzel):
    """ZUGFeRD / Factur-X / XRechnung in CII-Syntax."""
    dok = tief_suchen(wurzel, "ExchangedDocument")
    rechnung = text_von(dok, ["ID"]) if dok is not None else ""
    datum = None
    if dok is not None:
        zeit = finde(dok, ["IssueDateTime"])
        if zeit is not None:
            datum = datum_von(text_von(zeit, ["DateTimeString"]))

    lieferant = ""
    verkaeufer = tief_suchen(wurzel, "SellerTradeParty")
    if verkaeufer is not None:
        lieferant = text_von(verkaeufer, ["Name"])

    positionen = []
    for zeile in wurzel.iter():
        if lokal(zeile) != "IncludedSupplyChainTradeLineItem":
            continue
        produkt = finde(zeile, ["SpecifiedTradeProduct"])
        if produkt is None:
            continue
        name = text_von(produkt, ["Name"])
        nummer = (text_von(produkt, ["SellerAssignedID"])
                  or text_von(produkt, ["GlobalID"]))

        preis = None
        vereinbarung = finde(zeile, ["SpecifiedLineTradeAgreement"])
        if vereinbarung is not None:
            for feld in ("NetPriceProductTradePrice", "GrossPriceProductTradePrice"):
                knoten = finde(vereinbarung, [feld])
                if knoten is not None:
                    preis = zahl(text_von(knoten, ["ChargeAmount"]))
                    if preis is not None:
                        break

        menge = None
        lieferung = finde(zeile, ["SpecifiedLineTradeDelivery"])
        if lieferung is not None:
            menge = zahl(text_von(lieferung, ["BilledQuantity"]))

        if preis is None or not (name or nummer):
            continue
        positionen.append({"artikel": name, "nummer": nummer,
                           "menge": menge or 0.0, "preis": preis})
    return lieferant, rechnung, datum, positionen


def lies_xml_text(inhalt, quelle):
    try:
        wurzel = ET.fromstring(inhalt)
    except ET.ParseError as fehler:
        return None, "kein lesbares XML (%s)" % fehler
    name = lokal(wurzel)
    if name == "Invoice":
        daten = lies_ubl(wurzel)
    elif name == "CrossIndustryInvoice":
        daten = lies_cii(wurzel)
    else:
        return None, "unbekanntes Wurzelelement <%s>" % name
    lieferant, rechnung, datum, positionen = daten
    if not positionen:
        return None, "keine Positionen mit Einzelpreis gefunden"
    return {"quelle": quelle, "lieferant": lieferant or "unbekannter Lieferant",
            "rechnung": rechnung or os.path.basename(quelle),
            "datum": datum, "positionen": positionen}, None


def lies_pdf(pfad):
    """ZUGFeRD: XML steckt als Anhang im PDF."""
    try:
        import logging
        logging.getLogger("pypdf").setLevel(logging.ERROR)  # eigene Meldungen unterdruecken
        from pypdf import PdfReader
    except ImportError:
        return None, "PDF uebersprungen — 'pip install pypdf' fuer ZUGFeRD-PDFs"
    try:
        leser = PdfReader(pfad)
        anhaenge = leser.attachments
    except Exception as fehler:
        return None, "PDF nicht lesbar (%s)" % fehler
    for name, inhalte in (anhaenge or {}).items():
        if not name.lower().endswith(".xml"):
            continue
        for inhalt in inhalte:
            daten, fehler = lies_xml_text(inhalt, pfad)
            if daten:
                return daten, None
    return None, "kein XML-Anhang im PDF (vermutlich keine ZUGFeRD-Rechnung)"


def lies_datei(pfad):
    if pfad.lower().endswith(".pdf"):
        return lies_pdf(pfad)
    try:
        with open(pfad, "rb") as fh:
            return lies_xml_text(fh.read(), pfad)
    except OSError as fehler:
        return None, "nicht lesbar (%s)" % fehler


# ------------------------------------------------------------------- Auswerten

def schluessel(position):
    """Artikelnummer ist stabiler als der Name; sonst normalisierter Name."""
    if position["nummer"]:
        return position["nummer"].strip().lower()
    return re.sub(r"\s+", " ", position["artikel"]).strip().lower()


def sammle(rechnungen):
    reihen = defaultdict(list)
    for r in rechnungen:
        for pos in r["positionen"]:
            reihen[(r["lieferant"], schluessel(pos))].append({
                "datum": r["datum"], "rechnung": r["rechnung"],
                "artikel": pos["artikel"] or pos["nummer"],
                "menge": pos["menge"], "preis": pos["preis"],
            })
    for eintraege in reihen.values():
        eintraege.sort(key=lambda e: (e["datum"] or dt.date.min, e["rechnung"]))
    return reihen


def finde_erhoehungen(reihen):
    """Je Preiserhoehung ein Fund - mit allen Rechnungen, die danach noch
    zum erhoehten Preis abgerechnet wurden.

    Wer den Anstieg nur auf der ersten Rechnung zaehlt, unterschaetzt den
    Schaden: Der Betrieb zahlt bei jeder weiteren Lieferung erneut drauf,
    bis der Preis sich wieder aendert."""
    funde = []
    for (lieferant, _), eintraege in reihen.items():
        if len(eintraege) < 2:
            continue
        i = 1
        while i < len(eintraege):
            vorher, nachher = eintraege[i - 1], eintraege[i]
            diff = nachher["preis"] - vorher["preis"]
            if diff <= 0 or vorher["preis"] <= 0:
                i += 1
                continue
            prozent = diff / vorher["preis"] * 100
            if diff < MIN_ABWEICHUNG_EUR or prozent < MIN_ABWEICHUNG_PROZENT:
                i += 1
                continue

            # Alle folgenden Rechnungen mitnehmen, solange der Preis
            # auf dem erhoehten Stand bleibt.
            betroffen, j = [nachher], i + 1
            while j < len(eintraege) and abs(eintraege[j]["preis"] - nachher["preis"]) < MIN_ABWEICHUNG_EUR:
                betroffen.append(eintraege[j])
                j += 1

            funde.append({
                "lieferant": lieferant,
                "artikel": nachher["artikel"],
                "alt": vorher["preis"], "neu": nachher["preis"],
                "prozent": prozent,
                "seit_rechnung": vorher["rechnung"],
                "betroffen": [{
                    "rechnung": e["rechnung"], "datum": e["datum"],
                    "menge": e["menge"],
                    "differenz": diff * (e["menge"] or 0.0),
                } for e in betroffen],
                "differenz": sum(diff * (e["menge"] or 0.0) for e in betroffen),
            })
            i = j if j > i else i + 1
    funde.sort(key=lambda f: -f["differenz"])
    return funde


# -------------------------------------------------------------------- Ausgabe

def euro(wert):
    return ("%.2f" % wert).replace(".", ",") + " €"


def datum_text(d):
    return d.strftime("%d.%m.%Y") if d else ""


def main():
    ap = argparse.ArgumentParser(description="Stille Preiserhoehungen in E-Rechnungen finden")
    ap.add_argument("--ordner", required=True, help="Ordner mit XML- oder PDF-Rechnungen")
    ap.add_argument("--csv", help="Ergebnis zusaetzlich als CSV im Format von funde.csv")
    args = ap.parse_args()

    if not os.path.isdir(args.ordner):
        sys.exit("Ordner nicht gefunden: %s" % args.ordner)

    dateien = sorted(
        os.path.join(args.ordner, n) for n in os.listdir(args.ordner)
        if n.lower().endswith((".xml", ".pdf"))
    )
    if not dateien:
        sys.exit("Keine .xml- oder .pdf-Dateien in %s" % args.ordner)

    rechnungen, uebersprungen = [], []
    for pfad in dateien:
        daten, fehler = lies_datei(pfad)
        if daten:
            rechnungen.append(daten)
        else:
            uebersprungen.append((os.path.basename(pfad), fehler))

    print("Gelesen: %d von %d Dateien" % (len(rechnungen), len(dateien)))
    for name, grund in uebersprungen:
        print("  uebersprungen: %-28s %s" % (name, grund))
    if not rechnungen:
        sys.exit("Keine auswertbare Rechnung gefunden.")

    ohne_datum = [r["rechnung"] for r in rechnungen if not r["datum"]]
    if ohne_datum:
        print("  Hinweis: ohne Rechnungsdatum, Reihenfolge unsicher: %s"
              % ", ".join(ohne_datum[:5]))

    reihen = sammle(rechnungen)
    positionen = sum(len(e) for e in reihen.values())
    mehrfach = sum(1 for e in reihen.values() if len(e) > 1)
    print("\n%d Positionen, %d Artikel, davon %d mehrfach geliefert (nur diese sind vergleichbar)\n"
          % (positionen, len(reihen), mehrfach))

    funde = finde_erhoehungen(reihen)
    if not funde:
        print("Keine Preiserhoehung oberhalb der Schwelle gefunden.")
        print("Das ist ein Ergebnis, kein Fehler — es gehoert so in den Bericht.")
        return

    print("Preiserhoehungen, groesster Betrag zuerst\n")
    zeilen_gesamt = 0
    for f in funde:
        print("  %-26s %s" % (f["lieferant"][:26], f["artikel"][:44]))
        print("    %s -> %s  (+%.1f %%)  ab %s, zuletzt %s vor der Erhoehung"
              % (euro(f["alt"]), euro(f["neu"]), f["prozent"],
                 f["betroffen"][0]["rechnung"], f["seit_rechnung"]))
        for b in f["betroffen"]:
            print("      %-16s %-11s Menge %-7g Mehrkosten %s"
                  % (b["rechnung"], datum_text(b["datum"]), b["menge"], euro(b["differenz"])))
            zeilen_gesamt += 1
        if len(f["betroffen"]) > 1:
            print("      %-16s %-11s %-13s %s"
                  % ("", "", "zusammen", euro(f["differenz"])))
        print()
    print("  Summe der Mehrkosten ueber alle betroffenen Rechnungen: %s"
          % euro(sum(f["differenz"] for f in funde)))
    print("\n  Alle Funde sind als \"zu klaeren\" einzustufen, bis die")
    print("  Konditionsvereinbarung geprueft ist. Erst dann werden sie \"sicher\".")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            s = csv.writer(fh, delimiter=";")
            s.writerow(["Lieferant", "Rechnung", "Datum", "Pruefpunkt",
                        "Soll", "Ist", "Differenz", "Status"])
            geschrieben = 0
            for f in funde:
                for b in f["betroffen"]:
                    s.writerow([f["lieferant"], b["rechnung"], datum_text(b["datum"]),
                                "Preis still erhöht (%s)" % f["artikel"][:40],
                                euro(f["alt"]), euro(f["neu"]),
                                ("%.2f" % b["differenz"]).replace(".", ","),
                                "zu klären"])
                    geschrieben += 1
        print("\n  geschrieben: %s  (%d Zeilen fuer ops/bericht/funde.csv)"
              % (args.csv, geschrieben))


if __name__ == "__main__":
    main()
