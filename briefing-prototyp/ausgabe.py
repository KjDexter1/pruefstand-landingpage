"""Rendert das geprueefte Briefing als Markdown -- eine Seite, zwei Minuten Lesezeit."""

from datetime import date


def als_markdown(b, verworfen, domain):
    z = []
    a = z.append

    a(f"# {b.get('firmenname') or domain}")
    a("")
    a(f"*Briefing vom {date.today().strftime('%d.%m.%Y')} · Quelle: {domain} · "
      "ausschliesslich Unternehmensdaten, keine Personenrecherche*")
    a("")

    if not b.get("tragfaehig", False):
        a("> **Kein tragfaehiges Briefing.**")
        a(f"> {b.get('tragfaehig_begruendung', '')}")
        a("> Geh ohne vor -- ein duennes Briefing ist schlechter als keins, weil es")
        a("> falsche Sicherheit gibt.")
        a("")

    a("## Was die Firma macht")
    a("")
    a(b.get("geschaeftsmodell", "-"))
    beleg = b.get("geschaeftsmodell_beleg")
    if beleg:
        a("")
        a(f"<{beleg}>")
    a("")

    if b.get("signale"):
        a("## Was auffaellt")
        a("")
        for s in b["signale"]:
            a(f"**{s['beobachtung']}**")
            a("")
            a(f"{s['bedeutung']}")
            a("")
            a(f"> „{s['zitat'].strip()}“")
            a(f"> — <{s['quelle_url']}>")
            a("")

    if b.get("stellenanzeigen"):
        a("## Offene Stellen")
        a("")
        a("*Wofuer eine Firma gerade Geld ausgibt, verraet, wo es klemmt.*")
        a("")
        for st in b["stellenanzeigen"]:
            a(f"- **{st['titel']}** — {st['verraet']}  ")
            a(f"  <{st['quelle_url']}>")
        a("")

    if b.get("einstiegsfragen"):
        a("## Einstiegsfragen")
        a("")
        for i, f in enumerate(b["einstiegsfragen"], 1):
            a(f"{i}. „{f['frage']}“  ")
            a(f"   *stuetzt sich auf: {f['stuetzt_sich_auf']}*")
        a("")

    if b.get("nicht_gefunden"):
        a("## Nicht gefunden")
        a("")
        for n in b["nicht_gefunden"]:
            a(f"- {n}")
        a("")

    if verworfen:
        a("---")
        a("")
        a(f"<details><summary>{len(verworfen)} Punkte in der Pruefung verworfen</summary>")
        a("")
        for v in verworfen:
            a(f"- *{v['art']}*: {v['inhalt']} — **{v['grund']}**")
        a("")
        a("</details>")

    return "\n".join(z)
