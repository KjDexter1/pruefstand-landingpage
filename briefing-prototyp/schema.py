"""
Ausgabeschema fuer das Firmenbriefing.

Zentrale Regel: Jede Aussage braucht eine Quelle UND ein woertliches Zitat.
Ohne beides fliegt die Aussage in pruefung.py deterministisch raus.
Das ist der einzige Schutz gegen generischen KI-Text.
"""

BRIEFING_TOOL = {
    "name": "briefing_abgeben",
    "description": (
        "Gibt das fertige Firmenbriefing ab. Genau einmal aufrufen, "
        "nachdem die Recherche abgeschlossen ist."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "firmenname",
            "geschaeftsmodell",
            "geschaeftsmodell_beleg",
            "signale",
            "stellenanzeigen",
            "einstiegsfragen",
            "nicht_gefunden",
            "tragfaehig",
            "tragfaehig_begruendung",
        ],
        "properties": {
            "firmenname": {
                "type": "string",
                "description": "Firmierung laut Impressum, nicht laut Marketing.",
            },
            "geschaeftsmodell": {
                "type": "string",
                "description": (
                    "Was die Firma konkret verkauft, an wen, womit sie Geld verdient. "
                    "Hoechstens zwei Saetze. Keine Adjektive aus der Selbstdarstellung. "
                    "Nicht 'fuehrender Anbieter', sondern was tatsaechlich geliefert wird."
                ),
            },
            "geschaeftsmodell_beleg": {"type": "string", "description": "URL"},
            "signale": {
                "type": "array",
                "description": (
                    "Konkrete, nicht offensichtliche Beobachtungen. Jede muss aus einer "
                    "Quelle belegbar sein. Beispiele fuer brauchbare Signale: eine seit "
                    "Monaten offene Schluesselposition, ein Technologiewechsel, ein neuer "
                    "Standort, ein Widerspruch zwischen Aussendarstellung und Stellenprofil, "
                    "ein genannter Referenzkunde aus einer bestimmten Branche. "
                    "Leeres Array ist erlaubt und besser als Fuellmaterial."
                ),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["beobachtung", "bedeutung", "quelle_url", "zitat"],
                    "properties": {
                        "beobachtung": {
                            "type": "string",
                            "description": "Was steht da. Faktisch, ohne Deutung.",
                        },
                        "bedeutung": {
                            "type": "string",
                            "description": (
                                "Was das fuer ein Verkaufsgespraech bedeutet. "
                                "Als Vermutung formulieren, nicht als Tatsache."
                            ),
                        },
                        "quelle_url": {"type": "string"},
                        "zitat": {
                            "type": "string",
                            "description": (
                                "Woertliche Passage von der Quellseite, die die Beobachtung "
                                "traegt. Wort fuer Wort abgeschrieben, nicht paraphrasiert. "
                                "Wenn kein woertliches Zitat existiert: Signal weglassen."
                            ),
                        },
                    },
                },
            },
            "stellenanzeigen": {
                "type": "array",
                "description": (
                    "Offene Stellen. Das ist erfahrungsgemaess die ergiebigste Quelle: "
                    "wofuer eine Firma Geld ausgibt, verraet mehr als ihre Website."
                ),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["titel", "verraet", "quelle_url"],
                    "properties": {
                        "titel": {"type": "string"},
                        "verraet": {
                            "type": "string",
                            "description": "Welcher Engpass oder welches Vorhaben dahintersteckt.",
                        },
                        "quelle_url": {"type": "string"},
                    },
                },
            },
            "einstiegsfragen": {
                "type": "array",
                "description": (
                    "Hoechstens drei. Jede muss sich auf ein konkretes Signal stuetzen und "
                    "waere so nur bei dieser Firma stellbar. Eine Frage, die man jeder "
                    "beliebigen Firma stellen koennte, ist wertlos."
                ),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["frage", "stuetzt_sich_auf"],
                    "properties": {
                        "frage": {"type": "string"},
                        "stuetzt_sich_auf": {
                            "type": "string",
                            "description": "Auf welche Beobachtung sich die Frage bezieht.",
                        },
                    },
                },
            },
            "nicht_gefunden": {
                "type": "array",
                "description": (
                    "Was gesucht, aber nicht gefunden wurde. Ehrliche Luecken sind "
                    "wertvoller als geratene Fuellungen."
                ),
                "items": {"type": "string"},
            },
            "tragfaehig": {
                "type": "boolean",
                "description": (
                    "false, wenn die Recherche nichts hergegeben hat, das ueber eine "
                    "Zusammenfassung der Startseite hinausgeht. Im Zweifel false. "
                    "Ein ehrliches 'nichts gefunden' ist brauchbar, ein aufgeblasenes "
                    "Briefing ist es nicht."
                ),
            },
            "tragfaehig_begruendung": {"type": "string"},
        },
    },
}
