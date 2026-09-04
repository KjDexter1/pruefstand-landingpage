#!/usr/bin/env python3
"""
Pre-Call-Briefing: nimmt eine Firmen-Domain und gibt ein belegtes
Kurzbriefing als Markdown aus.

    python3 recherche.py beispiel-agentur.de
    python3 recherche.py beispiel-agentur.de --roh   # zusaetzlich das JSON

Stufe 1 bewusst OHNE Personendaten: recherchiert werden ausschliesslich
Angaben ueber das Unternehmen (Website, Impressum, Stellenanzeigen, Presse).
Keine LinkedIn-Profile, keine Gespraechspartner, keine Personensuche.
Das ist keine technische Beschraenkung, sondern eine Entscheidung --
Profile ueber benannte Personen sind DSGVO-Kernbereich (Art. 14) und
brauchen anwaltliche Klaerung, bevor sie in ein Produkt gehen.

Voraussetzungen:
    pip install anthropic
    export ANTHROPIC_API_KEY=...
"""

import argparse
import json
import sys

import anthropic

from schema import BRIEFING_TOOL
from pruefung import pruefe
from ausgabe import als_markdown

MODELL = "claude-opus-5"

SYSTEM = """\
Du recherchierst ein Unternehmen fuer ein Vertriebsgespraech. Der Leser ist \
Vertriebler, hat zwei Minuten Zeit und geht danach in den Termin.

Dein Wert liegt ausschliesslich in dem, was er NICHT schon weiss, wenn er die \
Startseite ueberfliegt. Eine Zusammenfassung der Selbstdarstellung ist wertlos.

Vorgehen:
1. Sieh dir die Website an: Startseite, Leistungen, Referenzen, Impressum.
2. Sieh dir die Karriereseite an. Offene Stellen sind die ergiebigste Quelle -- \
   wofuer eine Firma gerade Geld ausgibt, verraet mehr ueber ihre Lage als jeder \
   Marketingtext. Achte auf: welche Rollen, welche Technologien im Anforderungsprofil, \
   welche Abteilung waechst, wie lange die Stelle schon offen ist.
3. Suche nach aktuellen Meldungen, Fachbeitraegen, Vortraegen, Auszeichnungen.
4. Achte auf Widersprueche: Aussendarstellung gegen Stellenprofil, alte Referenzen \
   gegen neue Positionierung, angekuendigte Produkte ohne Spuren.

Harte Regeln:
- Jede Aussage braucht eine Quell-URL UND ein woertliches Zitat von dieser Seite. \
  Zitate werden Wort fuer Wort abgeschrieben, nie sinngemaess wiedergegeben.
- Findest du zu einem Punkt nichts Belastbares, laesst du ihn weg und traegst ihn \
  unter "nicht_gefunden" ein. Rate nichts. Fuelle keine Luecken mit Plausiblem.
- Keine Werbesprache. Nicht "fuehrender Anbieter", "innovativ", "ganzheitlich", \
  "gut aufgestellt". Wenn du eine solche Formulierung schreiben willst, hast du \
  nichts gefunden -- dann schreib das.
- Deutungen als Vermutung kennzeichnen, nicht als Feststellung.
- Keine Personen recherchieren. Keine Namen von Mitarbeitenden, keine Lebenslaeufe, \
  keine Profile in sozialen Netzwerken. Ausschliesslich das Unternehmen. \
  Geschaeftsfuehrernamen aus dem Impressum nur, wenn sie fuer die Firmierung noetig \
  sind -- keine Recherche ueber diese Personen.
- Lieber ein ehrliches "nichts Tragfaehiges gefunden" als ein volles Briefing \
  ohne Substanz. Setze dann tragfaehig=false.

Wenn du fertig recherchiert hast, rufe genau einmal briefing_abgeben auf."""


def hole_briefing(domain, protokoll=False):
    client = anthropic.Anthropic()

    auftrag = (
        f"Recherchiere das Unternehmen hinter der Domain {domain}.\n"
        f"Startpunkt: https://{domain}\n\n"
        "Sieh dir die Website und die Karriereseite an und suche nach aktuellen "
        "Meldungen. Rufe danach briefing_abgeben auf."
    )

    with client.messages.stream(
        model=MODELL,
        max_tokens=32000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
            BRIEFING_TOOL,
        ],
        messages=[{"role": "user", "content": auftrag}],
    ) as stream:
        antwort = stream.get_final_message()

    if antwort.stop_reason == "refusal":
        raise SystemExit(
            "Das Modell hat die Anfrage abgelehnt: "
            f"{getattr(antwort.stop_details, 'explanation', 'kein Grund angegeben')}"
        )

    if protokoll:
        for block in antwort.content:
            if block.type == "server_tool_use":
                print(f"  [{block.name}] {json.dumps(block.input, ensure_ascii=False)[:110]}",
                      file=sys.stderr)

    for block in antwort.content:
        if block.type == "tool_use" and block.name == "briefing_abgeben":
            return block.input

    raise SystemExit(
        "Das Modell hat kein Briefing abgegeben. Meist heisst das, dass die Website "
        "nicht erreichbar war. Antwort war:\n"
        + "\n".join(b.text for b in antwort.content if b.type == "text")[:800]
    )


def main():
    p = argparse.ArgumentParser(description="Firmenbriefing aus einer Domain erzeugen.")
    p.add_argument("domain", help="z. B. beispiel-agentur.de")
    p.add_argument("--roh", action="store_true", help="zusaetzlich das JSON ausgeben")
    p.add_argument("--protokoll", action="store_true", help="zeigt, was recherchiert wurde")
    args = p.parse_args()

    domain = args.domain.replace("https://", "").replace("http://", "").strip("/")

    print(f"Recherchiere {domain} ...", file=sys.stderr)
    roh = hole_briefing(domain, protokoll=args.protokoll)
    briefing, verworfen = pruefe(roh)

    print(als_markdown(briefing, verworfen, domain))

    if args.roh:
        print("\n\n<!-- Rohdaten des Modells vor der Pruefung\n", file=sys.stderr)
        print(json.dumps(roh, ensure_ascii=False, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
