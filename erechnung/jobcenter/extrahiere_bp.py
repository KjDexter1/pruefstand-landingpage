# -*- coding: utf-8 -*-
"""Liest den Businessplan aus der Word-Datei und schreibt die Bloecke als JSON.

Aufruf: python3 extrahiere_bp.py <docx> <json>
Damit bleiben Word- und PDF-Fassung inhaltsgleich: die PDF wird nicht neu
geschrieben, sondern aus derselben Quelle erzeugt.
"""
import json, sys
from docx import Document
from docx.shared import Pt

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def absatz(p):
    text = p.text.strip()
    if not text:
        return None
    lauf = p.runs[0] if p.runs else None
    groesse = 10.5
    fett = False
    rot = False
    if lauf is not None:
        if lauf.font.size is not None:
            groesse = lauf.font.size / Pt(1)
        fett = bool(lauf.font.bold)
        farbe = lauf.font.color
        rot = bool(farbe and farbe.rgb and str(farbe.rgb).upper() == "A93C1B")
    # Aufzaehlungen stecken in der Nummerierung, nicht im Text
    pPr = p._p.find(W + "pPr")
    liste = pPr is not None and pPr.find(W + "numPr") is not None
    return {"art": "p", "text": text, "groesse": groesse,
            "fett": fett, "rot": rot, "liste": liste}

def tabelle(t):
    zeilen = [[z.text.strip() for z in r.cells] for r in t.rows]
    return {"art": "t", "zeilen": zeilen}

doc = Document(sys.argv[1])
bloecke = []
for kind in doc.element.body.iterchildren():
    if kind.tag == W + "p":
        from docx.text.paragraph import Paragraph
        b = absatz(Paragraph(kind, doc))
        if b:
            bloecke.append(b)
    elif kind.tag == W + "tbl":
        from docx.table import Table
        bloecke.append(tabelle(Table(kind, doc)))

json.dump(bloecke, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print("Bloecke:", len(bloecke))
