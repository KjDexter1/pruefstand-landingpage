"""
Deterministische Nachkontrolle des Briefings.

Das Sprachmodell recherchiert und formuliert. Was durchgeht, entscheidet
dieser Code -- nicht das Modell. Gleiches Prinzip wie beim Rechnungspruefer:
Extraktion darf raten, die Bewertung nicht.
"""

import re
from urllib.parse import urlparse

# Formulierungen, die nichts aussagen. Wer eine davon benutzt, hat nichts
# gefunden und fuellt die Luecke mit Klang. Kommt eine vor, faellt die
# Aussage raus -- unabhaengig davon, wie plausibel sie klingt.
FLOSKELN = [
    "führender anbieter", "fuehrender anbieter", "marktführer", "marktfuehrer",
    "innovativ", "ganzheitlich", "maßgeschneidert", "massgeschneidert",
    "lösungsorientiert", "loesungsorientiert", "zukunftsorientiert",
    "breites portfolio", "langjährige erfahrung", "langjaehrige erfahrung",
    "hohe qualität", "hohe qualitaet", "kundenorientiert", "dynamisches umfeld",
    "scheint zu wachsen", "setzt auf wachstum", "gut aufgestellt",
    "spannende herausforderung", "am puls der zeit",
]

# Fragen, die man jeder beliebigen Firma stellen koennte.
GENERISCHE_FRAGEN = [
    "wo sehen sie sich", "was sind ihre größten herausforderungen",
    "was sind ihre groessten herausforderungen", "wie läuft das geschäft",
    "wie laeuft das geschaeft", "wo drückt der schuh", "wo drueckt der schuh",
    "was beschäftigt sie gerade", "was beschaeftigt sie gerade",
    "wie sind sie aufgestellt", "welche ziele haben sie",
]

MIN_ZITAT_ZEICHEN = 25


def _floskel_treffer(text):
    klein = text.lower()
    return [f for f in FLOSKELN if f in klein]


def _url_brauchbar(url):
    try:
        teile = urlparse(url)
    except ValueError:
        return False
    return teile.scheme in ("http", "https") and bool(teile.netloc)


def _zitat_belastbar(zitat):
    """Ein Zitat muss lang genug sein, um etwas zu tragen, und Inhalt haben."""
    sauber = re.sub(r"\s+", " ", zitat).strip()
    if len(sauber) < MIN_ZITAT_ZEICHEN:
        return False, f"Zitat zu kurz ({len(sauber)} Zeichen, Minimum {MIN_ZITAT_ZEICHEN})"
    if len(sauber.split()) < 4:
        return False, "Zitat hat weniger als vier Woerter"
    return True, ""


def pruefe(briefing):
    """
    Nimmt das Roh-Briefing des Modells und gibt zurueck:
      (bereinigtes_briefing, liste_der_verworfenen_punkte)
    """
    verworfen = []
    sauber = dict(briefing)

    # --- Signale: Beleg- und Floskelpflicht -----------------------------
    gepruefte_signale = []
    for s in briefing.get("signale", []):
        grund = None

        if not _url_brauchbar(s.get("quelle_url", "")):
            grund = "keine brauchbare Quell-URL"
        else:
            ok, warum = _zitat_belastbar(s.get("zitat", ""))
            if not ok:
                grund = warum

        if grund is None:
            treffer = _floskel_treffer(s.get("beobachtung", "") + " " + s.get("bedeutung", ""))
            if treffer:
                grund = "Floskel ohne Aussage: " + ", ".join(treffer)

        if grund:
            verworfen.append({
                "art": "Signal",
                "inhalt": s.get("beobachtung", "")[:120],
                "grund": grund,
            })
        else:
            gepruefte_signale.append(s)
    sauber["signale"] = gepruefte_signale

    # --- Stellenanzeigen: brauchen mindestens eine Quelle ----------------
    gepruefte_stellen = []
    for st in briefing.get("stellenanzeigen", []):
        if not _url_brauchbar(st.get("quelle_url", "")):
            verworfen.append({
                "art": "Stellenanzeige",
                "inhalt": st.get("titel", "")[:120],
                "grund": "keine brauchbare Quell-URL",
            })
        else:
            gepruefte_stellen.append(st)
    sauber["stellenanzeigen"] = gepruefte_stellen

    # --- Einstiegsfragen: duerfen nicht auf jede Firma passen ------------
    gepruefte_fragen = []
    for f in briefing.get("einstiegsfragen", []):
        frage = f.get("frage", "")
        klein = frage.lower()
        treffer = [g for g in GENERISCHE_FRAGEN if g in klein]
        if treffer:
            verworfen.append({
                "art": "Einstiegsfrage",
                "inhalt": frage[:120],
                "grund": "passt auf jede beliebige Firma",
            })
        else:
            gepruefte_fragen.append(f)
    sauber["einstiegsfragen"] = gepruefte_fragen[:3]

    # --- Gesamturteil ----------------------------------------------------
    # Ein Briefing ist nur dann etwas wert, wenn nach der Bereinigung noch
    # etwas uebrig ist, das die Startseite nicht auch hergegeben haette.
    substanz = len(sauber["signale"]) + len(sauber["stellenanzeigen"])
    if substanz == 0:
        sauber["tragfaehig"] = False
        sauber["tragfaehig_begruendung"] = (
            "Nach der Belegpruefung blieb kein einziges belegtes Signal uebrig. "
            "Das Briefing gibt nicht mehr her als ein Blick auf die Startseite."
        )
    elif substanz < 2:
        sauber["tragfaehig"] = False
        sauber["tragfaehig_begruendung"] = (
            f"Nur {substanz} belegtes Signal nach der Pruefung. Zu duenn fuer ein "
            "Gespraech, das ohne dieses Briefing anders verlaufen waere."
        )

    return sauber, verworfen
