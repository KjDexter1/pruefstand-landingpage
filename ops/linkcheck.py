#!/usr/bin/env python3
"""Prueft, ob alle internen HTML-Verweise der Landingpage aufloesbar sind."""

import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PFLICHT = ["index.html", "impressum.html", "datenschutz.html", "funktionsweise.html"]


def main():
    fehler = []

    for datei in PFLICHT:
        if not os.path.exists(os.path.join(WURZEL, datei)):
            fehler.append("Pflichtseite fehlt: %s" % datei)

    for datei in sorted(os.listdir(WURZEL)):
        if not datei.endswith(".html"):
            continue
        text = open(os.path.join(WURZEL, datei), encoding="utf-8").read()
        for ziel in re.findall(r'href="([^"#?:]+\.html)[^"]*"', text):
            if not os.path.exists(os.path.join(WURZEL, ziel)):
                fehler.append("toter Verweis: %s -> %s" % (datei, ziel))

    index = open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
    if "farukpolat@mail.de" not in index:
        fehler.append("Kontaktadresse im Demo-Formular fehlt")

    if fehler:
        print("\n".join(fehler))
        return 1
    print("Seitencheck ok: Pflichtseiten, interne Verweise und Kontaktadresse vorhanden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
