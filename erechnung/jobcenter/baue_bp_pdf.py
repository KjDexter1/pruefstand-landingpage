# -*- coding: utf-8 -*-
"""Erzeugt die PDF-Fassung des Businessplans aus denselben Inhalten wie die Word-Datei."""
import json, html, re

bloecke = json.load(open('/tmp/bp.json'))

KOPF = """<title>Businessplan</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@600;700&display=swap">
<style>
  @page { size:A4; margin:22mm 22mm 18mm; }
  :root {
    --ink:#161917; --ink-soft:#4E5854; --ink-faint:#87908B; --rule:#D2D0C7;
    --accent:#0E5B50; --accent-soft:#E7F0ED; --flag:#A93C1B; --surface:#F5F4EF;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:#fff; color:var(--ink);
    font-family:"IBM Plex Sans", Arial, sans-serif;
    font-size:10.3pt; line-height:1.52; -webkit-font-smoothing:antialiased;
  }
  h1 {
    font-family:"IBM Plex Serif", Georgia, serif; font-weight:700;
    font-size:15pt; color:var(--accent); margin:22px 0 9px;
    padding-bottom:4px; border-bottom:1.5px solid var(--accent);
    page-break-after:avoid;
  }
  h2 {
    font-size:11.4pt; font-weight:600; margin:15px 0 6px; page-break-after:avoid;
  }
  p { margin:0 0 8px; }
  .titel {
    font-family:"IBM Plex Serif", Georgia, serif; font-weight:700;
    font-size:30pt; color:var(--accent); margin:0 0 4px; line-height:1.1;
  }
  .untertitel { font-size:12pt; color:var(--ink-soft); margin:0 0 26px; }
  .kopfzeile { margin:0 0 5px; }
  .lueck { color:var(--flag); font-weight:600; }
  .vorwort {
    font-style:italic; color:var(--ink-soft); font-size:9.8pt;
    border-top:1.5px solid var(--accent); padding-top:12px; margin-top:18px;
  }
  ul.striche { margin:0 0 9px; padding-left:0; list-style:none; }
  ul.striche li {
    padding-left:14px; position:relative; margin-bottom:4px;
  }
  ul.striche li:before {
    content:"–"; position:absolute; left:0; color:var(--accent); font-weight:600;
  }
  table {
    width:100%; border-collapse:collapse; font-size:9.6pt;
    margin:6px 0 14px; page-break-inside:avoid;
  }
  th {
    background:var(--accent); color:#fff; font-weight:600; font-size:9pt;
    text-align:left; padding:6px 8px; border:1px solid var(--rule);
  }
  td {
    padding:5px 8px; border:1px solid var(--rule); vertical-align:top;
  }
  tr:last-child td { background:var(--surface); font-weight:600; }
  .zahl { text-align:right; white-space:nowrap; }
  .unterschrift { color:var(--ink-faint); font-style:italic; margin-top:34px; }
</style>
"""

def esc(t):
    t = html.escape(t)
    # Platzhalter in eckigen Klammern rot setzen
    return re.sub(r'(\[[^\]]+\])', r'<span class="lueck">\1</span>', t)

teile = [KOPF]
erste_ueberschrift = True
letzte_war_punkt = False

for i, b in enumerate(bloecke):
    if b['art'] == 't':
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        z = b['zeilen']
        spalten = len(z[0])
        # Spalten, die ueberwiegend Betraege enthalten, rechtsbuendig setzen
        rechts = [c for c in range(1, spalten)
                  if sum(1 for r in z[1:] if re.match(r'^[\d.,]+ ?(€|Aufträge)?$', r[c].strip())) > len(z)/2]
        kl = ' class="zahl"'
        kopf = ''.join('<th' + (kl if c in rechts else '') + '>' + esc(z[0][c]) + '</th>'
                       for c in range(spalten))
        koerper = ''.join(
            '<tr>' + ''.join('<td' + (kl if c in rechts else '') + '>' + esc(r[c]) + '</td>'
                             for c in range(spalten)) + '</tr>'
            for r in z[1:])
        teile.append(f'<table><thead><tr>{kopf}</tr></thead><tbody>{koerper}</tbody></table>')
        continue

    t, g, fett, rot = b['text'], b['groesse'], b['fett'], b['rot']

    if g >= 22:                                     # Haupttitel
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        teile.append(f'<div class="titel">{esc(t)}</div>')
    elif g >= 11.5 and not fett:                    # Untertitel
        teile.append(f'<div class="untertitel">{esc(t)}</div>')
    elif g >= 13.5 and fett:                        # Abschnittsueberschrift
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        teile.append(f'<h1>{esc(t)}</h1>')
    elif fett and g >= 11:                          # Zwischenueberschrift
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        teile.append(f'<h2>{esc(t)}</h2>')
    elif b.get('liste'):                            # Aufzaehlung
        if not letzte_war_punkt: teile.append('<ul class="striche">'); letzte_war_punkt = True
        teile.append(f'<li>{esc(t)}</li>')
    elif rot or '[' in t:                           # Kopfzeile mit Platzhalter
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        teile.append(f'<p class="kopfzeile">{esc(t)}</p>')
    elif t.startswith('Dieser Businessplan'):
        teile.append(f'<p class="vorwort">{esc(t)}</p>')
    elif t.startswith('Ort, Datum'):
        teile.append(f'<p class="unterschrift">{esc(t)}</p>')
    else:
        if letzte_war_punkt: teile.append('</ul>'); letzte_war_punkt = False
        teile.append(f'<p>{esc(t)}</p>')

if letzte_war_punkt: teile.append('</ul>')

open('businessplan.html', 'w', encoding='utf-8').write('\n'.join(teile))
print('HTML erzeugt')
