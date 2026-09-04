# -*- coding: utf-8 -*-
"""Arbeitsmappe fuer die E-Rechnungs-Dienstleistung."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

GRUEN  = "0E5B50"
ROST   = "A93C1B"
SAND   = "F2F1EC"
GELB   = "FFF6D6"
GRAU   = "8A938D"
LINIE  = "D4D2C9"

def f(size=10, bold=False, color="1A1D1B", italic=False):
    return Font(name="Arial", size=size, bold=bold, color=color, italic=italic)

kante = Side(style="thin", color=LINIE)
rahmen = Border(left=kante, right=kante, top=kante, bottom=kante)
oben = Alignment(vertical="top", wrap_text=True)
oben_links = Alignment(vertical="top", horizontal="left", wrap_text=True)

def kopfzeile(ws, zeile, ueberschriften, breiten):
    for i, (text, breite) in enumerate(zip(ueberschriften, breiten), start=1):
        c = ws.cell(row=zeile, column=i, value=text)
        c.font = f(9, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=GRUEN)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = rahmen
        ws.column_dimensions[get_column_letter(i)].width = breite
    ws.row_dimensions[zeile].height = 34

def titel(ws, text, unterzeile, spannweite):
    ws["A1"] = text
    ws["A1"].font = f(15, bold=True, color=GRUEN)
    ws["A2"] = unterzeile
    ws["A2"].font = f(9, color=GRAU, italic=True)
    ws.merge_cells(f"A1:{get_column_letter(spannweite)}1")
    ws.merge_cells(f"A2:{get_column_letter(spannweite)}2")
    ws.row_dimensions[1].height = 22

wb = Workbook()

# ===================================================================
# 1  SYSTEME
# ===================================================================
ws = wb.active
ws.title = "1 Systeme"

titel(ws, "Rechnungsprogramme — Rechercheblatt",
      "Gelbe Felder selbst ausfuellen. Das ist der Wissensvorsprung, den kein Wettbewerber hat.", 15)

ws["A4"] = ("LEGENDE   Gelb hinterlegt = von dir zu recherchieren.   "
            "Weiss = bereits eingetragen.   "
            "Zeile 6 ist ein Beispiel und zeigt, wie ausgefuellt aussehen soll — spaeter loeschen.")
ws["A4"].font = f(9, italic=True, color=ROST)
ws.merge_cells("A4:O4")
ws.row_dimensions[4].height = 26

spalten = ["Produkt", "Hersteller", "Einstufung", "Geprueft am", "Ab Version",
           "Versand moeglich?", "Formate", "Menuepfad zum Schalter",
           "Pflicht-Stammdaten", "§ 13b abbildbar? Wie?", "Leitweg-ID: welches Feld?",
           "Empfang eingebaut?", "Bekannte Stolpersteine", "Aufwand Std.", "Quelle (URL)"]
breiten = [20, 16, 12, 11, 12, 15, 16, 30, 26, 28, 22, 14, 30, 9, 26]
kopfzeile(ws, 5, spalten, breiten)

beispiel = ["BEISPIEL: Muster Faktura", "Muster GmbH", "Kern", "01.10.2026", "ab 2025.2",
            "ja", "XRechnung + ZUGFeRD",
            "Einstellungen > Rechnungen > E-Rechnung aktivieren",
            "USt-IdNr., vollstaendige Anschrift, IBAN",
            "ja — Steuerschluessel „AE“ anlegen, Begruendungstext im Textbaustein",
            "Kundenstamm > Feld „Bestellreferenz“", "ja",
            "Rundet Positionssummen kaufmaennisch, Kopfsumme weicht ab 3 Nachkommastellen ab",
            2.0, "https://..."]

kern = [
    ("lexoffice / Lexware Office", "Haufe-Lexware"),
    ("sevdesk", "sevdesk GmbH"),
    ("WISO Mein Buero", "Buhl Data"),
    ("easybill", "easybill GmbH"),
    ("FastBill", "FastBill GmbH"),
    ("Billomat", "Billomat GmbH"),
    ("Papierkram", "Papierkram GmbH"),
    ("SumUp Rechnungen", "SumUp"),
    ("Collmex", "Collmex GmbH"),
]
pruefen = [
    ("pds Handwerkersoftware", "pds GmbH"),
    ("Label Software", "Label Software GmbH"),
    ("Streit V.1", "Streit Datentechnik"),
    ("TopKontor Handwerk", "blue:solution"),
    ("TAIFUN Handwerk", "TAIFUN Software"),
    ("M-SOFT Handwerk", "M-SOFT"),
]
aus = [
    ("SAP (alle Varianten)", "SAP SE"),
    ("Microsoft Dynamics / BC", "Microsoft"),
    ("Sage 100 / X3", "Sage"),
    ("DATEV Mittelstand", "DATEV eG"),
    ("Individualsoftware", "—"),
]

zeile = 6
for wert in beispiel:
    ws.cell(row=zeile, column=beispiel.index(wert) + 1)
for i, wert in enumerate(beispiel, start=1):
    c = ws.cell(row=zeile, column=i, value=wert)
    c.font = f(9, italic=True, color=GRAU)
    c.alignment = oben
    c.border = rahmen
ws.row_dimensions[zeile].height = 40

zeile = 7
for gruppe, einstufung in ((kern, "Kern"), (pruefen, "Pruefen"), (aus, "Ausschluss")):
    for produkt, hersteller in gruppe:
        ws.cell(row=zeile, column=1, value=produkt).font = f(10, bold=(einstufung == "Kern"))
        ws.cell(row=zeile, column=2, value=hersteller).font = f(9)
        c = ws.cell(row=zeile, column=3, value=einstufung)
        c.font = f(9, bold=True,
                   color={"Kern": GRUEN, "Pruefen": "8A6D1F", "Ausschluss": ROST}[einstufung])
        for spalte in range(1, 16):
            zelle = ws.cell(row=zeile, column=spalte)
            zelle.alignment = oben
            zelle.border = rahmen
            if einstufung == "Ausschluss" and spalte >= 4:
                zelle.fill = PatternFill("solid", fgColor=SAND)
            elif spalte >= 4:
                zelle.fill = PatternFill("solid", fgColor=GELB)
        if einstufung == "Ausschluss":
            ws.cell(row=zeile, column=13,
                    value="Nicht anbieten — siehe Blatt 4").font = f(9, italic=True, color=GRAU)
        ws.row_dimensions[zeile].height = 30
        zeile += 1

letzte = zeile - 1
pruef = DataValidation(type="list", formula1='"Kern,Pruefen,Ausschluss"', allow_blank=True)
ws.add_data_validation(pruef)
pruef.add(f"C6:C{letzte}")

ja_nein = DataValidation(type="list",
                         formula1='"ja,nein,nur Zusatzmodul,unklar"', allow_blank=True)
ws.add_data_validation(ja_nein)
ja_nein.add(f"F6:F{letzte}")
ja_nein.add(f"L6:L{letzte}")

ws.freeze_panes = "C6"

# ===================================================================
# 2  KUNDENCHECKLISTE
# ===================================================================
ws2 = wb.create_sheet("2 Kundencheckliste")
titel(ws2, "Ablauf je Kunde",
      "Ausdrucken oder kopieren. Reihenfolge einhalten — Schritt 3 entscheidet ueber den Preis.", 5)

kopfzeile(ws2, 4, ["#", "Schritt", "Was genau", "Erledigt", "Notiz"], [5, 30, 62, 10, 34])

schritte = [
    ("Vor dem Termin", [
        "Rechnungsprogramm auf Blatt 1 nachschlagen — Menuepfad und Stammdaten notieren",
        "Pruefen: faellt der Kunde unter 2027 (ueber 800.000 €) oder 2028?",
        "Kleinunternehmer nach § 19 UStG? Dann nur Empfang, kein Versand — kleineres Paket",
    ]),
    ("Bestandsaufnahme", [
        "Rechnungsprogramm und Version am Bildschirm bestaetigen lassen",
        "Rechnet der Betrieb nach § 13b ab (Bauleistungen)? Wenn ja: hoechste Fehlerquelle",
        "Behoerden oder oeffentliche Auftraggeber unter den Kunden? Dann Leitweg-ID noetig",
        "Eingehende E-Rechnungen: wo landen die heute? (Empfangspflicht gilt seit 2025)",
    ]),
    ("Einrichtung Empfang", [
        "Eigene Adresse fuer eingehende E-Rechnungen einrichten",
        "Ablage festlegen — wohin gehoert die XML-Datei, wie lange aufbewahren",
        "Leseweg zeigen: wie macht das Buero eine XML-Datei lesbar",
    ]),
    ("Einrichtung Versand", [
        "E-Rechnung im Programm aktivieren (Menuepfad von Blatt 1)",
        "Stammdaten pruefen: USt-IdNr., vollstaendige Anschrift, IBAN, Steuernummer",
        "Steuerschluessel pruefen — besonders § 13b und § 19 (Blatt 3)",
        "Leitweg-ID im Kundenstamm hinterlegen, wo noetig",
        "Einheiten pruefen: Codes statt Freitext",
    ]),
    ("Test", [
        "Testrechnung erzeugen — mit einer Position § 13b, wenn zutreffend",
        "Gegen den Validator pruefen (KoSIT / Validierungsdienst)",
        "Fehler beheben, bis sie sauber durchlaeuft — alle Befunde in Blatt 3 nachtragen",
        "Testrechnung an eine echte Kundenadresse senden und Empfang bestaetigen lassen",
    ]),
    ("Abschluss", [
        "Eine Seite Anleitung fuer das Buero uebergeben",
        "Abnahme durch den Kunden bestaetigen lassen (schriftlich, kurz)",
        "Rechnung stellen",
        "Blatt 1 ergaenzen: was war neu an diesem System?",
    ]),
]

r = 5
nr = 1
for abschnitt, punkte in schritte:
    c = ws2.cell(row=r, column=1, value=abschnitt)
    c.font = f(10, bold=True, color="FFFFFF")
    for s in range(1, 6):
        ws2.cell(row=r, column=s).fill = PatternFill("solid", fgColor=GRUEN)
        ws2.cell(row=r, column=s).border = rahmen
    ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    r += 1
    for punkt in punkte:
        ws2.cell(row=r, column=1, value=nr).font = f(9, color=GRAU)
        ws2.cell(row=r, column=3, value=punkt).font = f(10)
        ws2.cell(row=r, column=4).fill = PatternFill("solid", fgColor=GELB)
        ws2.cell(row=r, column=5).fill = PatternFill("solid", fgColor=GELB)
        for s in range(1, 6):
            ws2.cell(row=r, column=s).alignment = oben_links
            ws2.cell(row=r, column=s).border = rahmen
        ws2.row_dimensions[r].height = 26
        nr += 1
        r += 1
ws2.freeze_panes = "A5"

# ===================================================================
# 3  FEHLERKATALOG
# ===================================================================
ws3 = wb.create_sheet("3 Fehlerkatalog")
titel(ws3, "Warum E-Rechnungen abgelehnt werden",
      "Vorausgefuellt. Nach jedem Kunden ergaenzen — das ist das wertvollste Blatt der Mappe.", 5)

kopfzeile(ws3, 4, ["Rang", "Fehler", "Woran man ihn erkennt", "Was zu tun ist", "Eigene Notizen"],
          [7, 30, 44, 46, 30])

fehler = [
    ("1", "Rundungsdifferenz",
     "Summe der Positionsbetraege weicht von der Kopfsumme ab — oft nur ein Cent.",
     "Positionssummen gegen die Netto-Kopfsumme rechnen. Haeufigster Ablehnungsgrund ueberhaupt; die Rechenregeln der Norm lassen keine Abweichung zu."),
    ("2", "§ 13b Bauleistungen ohne Begruendung",
     "Steuersatz 0 %, aber Steuerkategorie steht auf „S“, oder der Hinweistext auf die Steuerschuldnerschaft des Leistungsempfaengers fehlt.",
     "Kategorie „AE“ setzen und Befreiungsgrund als Text hinterlegen. Bei Baubetrieben der mit Abstand haeufigste Fehler — hier zuerst hinsehen. Ob § 13b gilt, entscheidet der Steuerberater, nicht du."),
    ("3", "Steuerkategorie passt nicht zum Steuersatz",
     "Kategorie „S“ mit 0 %, oder Kategorie „Z“ mit 19 %.",
     "Steuerschluessel im Programm durchgehen. Jede Kategorie hat einen zulaessigen Satzbereich."),
    ("4", "Leitweg-ID fehlt",
     "Empfaenger ist eine Behoerde oder ein oeffentlicher Auftraggeber, das Feld Bestellreferenz ist leer.",
     "Leitweg-ID beim Kunden erfragen und im Kundenstamm hinterlegen. Ohne sie weist jedes Behoerdenportal die Rechnung ab."),
    ("5", "Kleinunternehmer ohne Hinweis",
     "Keine Umsatzsteuer ausgewiesen, aber kein Hinweis auf § 19 UStG.",
     "Kategorie „E“ setzen und Begruendungstext hinterlegen."),
    ("6", "USt-IdNr. fehlt oder hat falsches Format",
     "Feld leer, Leerzeichen enthalten, oder Steuernummer statt USt-IdNr. eingetragen.",
     "Im Firmenprofil pruefen. Beides ist nicht dasselbe — wird oft verwechselt."),
    ("7", "Einheit als Freitext statt als Code",
     "In der Position steht „Stk“ oder „Stunden“ statt eines Codes.",
     "Einheiten im Artikelstamm auf Codes umstellen (C62 und H87 fuer Stueck sind beide zulaessig, KGM fuer kg, HUR fuer Stunden, MTR fuer Meter)."),
    ("8", "Innergemeinschaftliche Lieferung ohne Begruendung",
     "Auslandskunde in der EU, 0 % Steuer, keine Begruendung hinterlegt.",
     "Kategorie „K“ plus Begruendungstext, USt-IdNr. beider Seiten pflicht."),
    ("9", "Zahlungsangaben unvollstaendig",
     "IBAN oder Zahlungsziel fehlen.",
     "Im Firmenprofil nachtragen. Faellt oft erst beim Empfaenger auf."),
    ("10", "Datei ist gar keine E-Rechnung",
     "PDF ohne eingebettete XML-Datei — sieht aus wie eine Rechnung, ist aber keine.",
     "Mit dem Leser pruefen. Ein PDF allein erfuellt die Pflicht nicht, auch nicht als Scan oder Ausdruck."),
]

r = 5
for rang, name, erkennen, tun in fehler:
    ws3.cell(row=r, column=1, value=rang).font = f(11, bold=True, color=ROST)
    ws3.cell(row=r, column=2, value=name).font = f(10, bold=True)
    ws3.cell(row=r, column=3, value=erkennen).font = f(9)
    ws3.cell(row=r, column=4, value=tun).font = f(9)
    ws3.cell(row=r, column=5).fill = PatternFill("solid", fgColor=GELB)
    for s in range(1, 6):
        ws3.cell(row=r, column=s).alignment = oben
        ws3.cell(row=r, column=s).border = rahmen
    ws3.row_dimensions[r].height = 52
    r += 1
ws3.freeze_panes = "A5"

# ===================================================================
# 4  ANGEBOT UND REGELN
# ===================================================================
ws4 = wb.create_sheet("4 Angebot & Regeln")
titel(ws4, "Pakete, Preise, Abgrenzung",
      "Die Entscheidungsregeln fuers Telefonat. Preise sind Festpreise, keine Stundensaetze.", 4)

kopfzeile(ws4, 4, ["Paket", "Fuer wen", "Was drin ist", "Festpreis"], [26, 34, 56, 16])

pakete = [
    ("Einrichtung Standard", "Betrieb mit einem System von der Kernliste",
     "Bestandsaufnahme, Empfang einrichten, Versand aktivieren, Stammdaten pruefen, Testrechnung gegen den Validator, eine Seite Anleitung",
     "450 – 650 €"),
    ("Umstieg von Word/Excel", "Betrieb ohne Rechnungsprogramm",
     "Wie oben, zusaetzlich Auswahl des Programms, Uebernahme von Kunden- und Artikelstamm ueber die CSV-Vorlage, Einweisung",
     "900 – 1.400 €"),
    ("Nur Empfang", "Kleinunternehmer nach § 19 UStG",
     "Empfangsweg, Ablage, Leseweg. Kein Versand — davon sind sie dauerhaft befreit",
     "190 – 290 €"),
    ("Datenbereinigung", "Zusatz zum Umstiegspaket",
     "Wenn der Kunde die CSV-Vorlage nicht selbst befuellen kann. Immer vorher schriftlich vereinbaren, nie im Festpreis",
     "nach Aufwand"),
]
r = 5
for name, fuer, drin, preis in pakete:
    ws4.cell(row=r, column=1, value=name).font = f(10, bold=True, color=GRUEN)
    ws4.cell(row=r, column=2, value=fuer).font = f(9)
    ws4.cell(row=r, column=3, value=drin).font = f(9)
    ws4.cell(row=r, column=4, value=preis).font = f(10, bold=True)
    for s in range(1, 5):
        ws4.cell(row=r, column=s).alignment = oben
        ws4.cell(row=r, column=s).border = rahmen
    ws4.row_dimensions[r].height = 46
    r += 1

r += 1
ws4.cell(row=r, column=1, value="Die Entscheidung am Telefon").font = f(12, bold=True, color=GRUEN)
r += 1
ws4.cell(row=r, column=1,
         value="Eine Frage: „Womit schreiben Sie heute Ihre Rechnungen?“").font = f(10, italic=True)
r += 2

kopfzeile(ws4, r, ["Antwort", "Deine Reaktion", "Warum", ""], [26, 34, 56, 16])
r += 1
regeln = [
    ("Name von der Kernliste", "Festpreis nennen, Termin machen",
     "Du kennst das System, der Aufwand ist kalkulierbar."),
    ("Word, Excel, gar nichts", "Umstiegspaket nennen, CSV-Vorlage ankuendigen",
     "Groesster Auftrag und der Kunde ist nicht austauschbar — aber Datenbereinigung separat."),
    ("„Ich nutze DATEV“", "Nachfragen: schreiben Sie selbst, oder macht das die Kanzlei?",
     "Meist nutzen sie nur DATEV Unternehmen online zum Belege-Hochladen und schreiben in Wahrheit mit Word. Dann ist es doch dein Kunde."),
    ("Branchensoftware", "„Das schaue ich mir an, ich melde mich morgen“",
     "Erst annehmen ab der dritten Anfrage zum selben Produkt. Vorher zahlst du die Einarbeitung selbst."),
    ("SAP, Dynamics, Sage", "Ehrlich absagen: „Da sind Sie bei mir falsch“",
     "Kostet nichts und bringt Glaubwuerdigkeit. Frag nach einer Empfehlung im Bekanntenkreis."),
]
for antwort, reaktion, warum in regeln:
    ws4.cell(row=r, column=1, value=antwort).font = f(10, bold=True)
    ws4.cell(row=r, column=2, value=reaktion).font = f(9)
    ws4.cell(row=r, column=3, value=warum).font = f(9)
    for s in range(1, 5):
        ws4.cell(row=r, column=s).alignment = oben
        ws4.cell(row=r, column=s).border = rahmen
    ws4.row_dimensions[r].height = 40
    r += 1

r += 1
ws4.cell(row=r, column=1, value="Grenzen — gilt immer").font = f(12, bold=True, color=ROST)
r += 1
for satz in [
    "Technische Einrichtung, keine Steuerberatung. Ob § 13b oder § 19 gilt, entscheidet der Steuerberater des Kunden.",
    "Keine Zusicherung, dass ein bestimmter Empfaenger eine Rechnung annimmt. Keine Haftung fuer Zahlungseingaenge oder Zahlungsverzug.",
    "Steuerliche Richtigkeit verantwortet der Kunde. Das gehoert in die AGB — vom Anwalt, vor dem ersten Auftrag.",
    "Fristen: Empfang seit 2025 Pflicht fuer alle. Versand ab 2027 ueber 800.000 € Umsatz, ab 2028 fuer alle uebrigen. Kleinunternehmer nach § 19 UStG: dauerhaft nur Empfang.",
]:
    c = ws4.cell(row=r, column=1, value="•  " + satz)
    c.font = f(9)
    c.alignment = oben_links
    ws4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    ws4.row_dimensions[r].height = 30
    r += 1

for blatt in wb.worksheets:
    blatt.sheet_view.showGridLines = False

wb.save("E-Rechnung_Arbeitsmappe.xlsx")
print("gespeichert")
