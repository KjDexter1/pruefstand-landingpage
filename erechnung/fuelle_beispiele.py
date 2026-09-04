# -*- coding: utf-8 -*-
"""Traegt die recherchierten Zeilen in die Arbeitsmappe ein."""
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

WEISS = "FFFFFF"; GELB = "FFF6D6"; ROST = "A93C1B"; GRUEN = "0E5B50"
def f(size=9, bold=False, color="1A1D1B"):
    return Font(name="Arial", size=size, bold=bold, color=color)

wb = load_workbook("E-Rechnung_Arbeitsmappe.xlsx")
ws = wb["1 Systeme"]

OFFEN = "— noch offen —"

daten = {
 7: {  # lexoffice / Lexware Office
  "D": "04.09.2026",
  "E": "ab Paket M",
  "F": "ja",
  "G": "XRechnung + ZUGFeRD",
  "H": "Einstellungen (Zahnrad) > E-Rechnung > „E-Rechnung erstellen“. Admin-Rechte noetig.",
  "I": "Kontakt muss als „Firma“ angelegt sein — an Privatpersonen ist keine E-Rechnung moeglich. Bei Behoerden zusaetzlich Leitweg-ID und Lieferantennummer.",
  "J": "NEIN — nur als PDF! Rechnungsart oben rechts „§13b – Bauleistung“, vorher im Kundenstamm > Steuerangaben Haekchen „Steuerfreie Rechnungen erlauben“. Lexware selbst: §13b wird aktuell NICHT im XRechnung- oder ZUGFeRD-Format unterstuetzt.",
  "K": "Kundenstamm, Pflichtfeld bei Behoerden",
  "L": "ja",
  "M": "GROESSTER PUNKT: Baubetriebe mit §13b koennen mit Lexware Office ab 2028 keine gueltige E-Rechnung stellen. Bis 2027/2028 ist PDF noch zulaessig, danach nicht mehr. Das ist kein Einrichtungsauftrag, sondern ein Gespraech ueber einen Systemwechsel.",
  "N": 2.0,
  "O": "help.lexware.de/de-form/articles/547939 und /547981",
 },
 8: {  # sevdesk
  "D": "04.09.2026",
  "E": OFFEN,
  "F": "ja",
  "G": "XRechnung (UBL) + ZUGFeRD 2.1 / 2.2",
  "H": "Einstellungen > Rechnungen: Standardformat auf XRechnung oder ZUGFeRD setzen. QUELLE DRITTANBIETER — in der sevdesk-Hilfe gegenpruefen.",
  "I": "USt-IdNr., Bankverbindung, Handelsregisternummer unter Einstellungen > Unternehmen",
  "J": OFFEN + " — unbedingt selbst pruefen, siehe Lexware-Zeile",
  "K": "im Kontaktdatensatz des Empfaengers",
  "L": OFFEN,
  "M": "Angaben stammen aus Drittquellen, nicht aus der Herstellerhilfe. Vor dem ersten Kunden verifizieren.",
  "N": None,
  "O": "sevdesk.de/funktion-e-rechnung (Herstellerhilfe noch pruefen)",
 },
 10: {  # easybill
  "D": "04.09.2026",
  "E": OFFEN,
  "F": "ja",
  "G": "XRechnung 3.0.2 + ZUGFeRD",
  "H": "Kunde oeffnen > Bearbeiten > Einstellungen > Dokumentformat fuer den Versand. Wird JE KUNDE eingestellt, nicht zentral.",
  "I": OFFEN,
  "J": OFFEN + " — unbedingt selbst pruefen",
  "K": OFFEN,
  "L": OFFEN,
  "M": "Format je Kunde statt global — bei vielen Bestandskunden entsteht Mehraufwand. Hersteller empfiehlt, ZUGFeRD als Standard fuer alle Vorlagen zu setzen.",
  "N": None,
  "O": "support.easybill.de/hc/de/articles/13571616499228 und /14557057264412",
 },
}

for zeile, felder in daten.items():
    for spalte, wert in felder.items():
        if wert is None:
            continue
        c = ws[f"{spalte}{zeile}"]
        c.value = wert
        offen = isinstance(wert, str) and OFFEN in wert
        c.fill = PatternFill("solid", fgColor=GELB if offen else WEISS)
        if spalte == "J" and zeile == 7:
            c.font = f(9, bold=True, color=ROST)
        elif spalte == "M" and zeile == 7:
            c.font = f(9, bold=True, color=ROST)
        else:
            c.font = f(9)
        c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[zeile].height = 86

# Hinweis oben ergaenzen
ws["A3"] = ("Drei Zeilen sind vorrecherchiert (04.09.2026). Weiss = belegt. "
            "Gelb = noch offen. Quellen stehen in Spalte O.")
ws["A3"].font = f(9, bold=True, color=GRUEN)
ws.merge_cells("A3:O3")

wb.save("E-Rechnung_Arbeitsmappe.xlsx")
print("eingetragen")
