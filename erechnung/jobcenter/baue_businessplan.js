// Businessplan fuer den Antrag auf Einstiegsgeld nach § 16b SGB II.
// Alle personenbezogenen Angaben stehen als Platzhalter in eckigen Klammern.

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  PageBreak, LevelFormat, convertMillimetersToTwip,
} = require("docx");
const fs = require("fs");

const BREITE = 9070;          // Textbreite in DXA bei 2,5 cm Raendern
const GRUEN  = "0E5B50";
const ROST   = "A93C1B";
const HELL   = "EFEEE9";
const LINIE  = "C9C7BE";

const f = (text, opt = {}) => new TextRun({ text, font: "Arial", ...opt });

const p = (text, opt = {}) =>
  new Paragraph({
    spacing: { after: opt.after ?? 120, line: 276 },
    alignment: opt.align,
    children: [f(text, { size: opt.size ?? 21, bold: opt.bold, italics: opt.italics,
                         color: opt.color })],
  });

const platzhalter = (vorText, feld, nachText = "") =>
  new Paragraph({
    spacing: { after: 120, line: 276 },
    children: [
      f(vorText, { size: 21 }),
      f(feld, { size: 21, bold: true, color: ROST }),
      f(nachText, { size: 21 }),
    ],
  });

const h1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    children: [f(text, { size: 28, bold: true, color: GRUEN })],
  });

const h2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [f(text, { size: 23, bold: true })],
  });

const punkt = (text) =>
  new Paragraph({
    numbering: { reference: "striche", level: 0 },
    spacing: { after: 80, line: 276 },
    children: [f(text, { size: 21 })],
  });

const zelle = (text, opt = {}) =>
  new TableCell({
    width: { size: opt.breite, type: WidthType.DXA },
    shading: opt.fuell
      ? { type: ShadingType.CLEAR, color: "auto", fill: opt.fuell }
      : undefined,
    margins: { top: 80, bottom: 80, left: 110, right: 110 },
    children: [
      new Paragraph({
        alignment: opt.rechts ? AlignmentType.RIGHT : AlignmentType.LEFT,
        spacing: { after: 0, line: 260 },
        children: [f(String(text), {
          size: opt.size ?? 20,
          bold: opt.bold,
          color: opt.color,
        })],
      }),
    ],
  });

function tabelle(spaltenbreiten, kopfzeile, zeilen, opt = {}) {
  const reihen = [
    new TableRow({
      tableHeader: true,
      children: kopfzeile.map((t, i) =>
        zelle(t, {
          breite: spaltenbreiten[i],
          fuell: GRUEN,
          bold: true,
          color: "FFFFFF",
          size: 19,
          rechts: i > 0 && opt.rechtsAb !== false,
        })),
    }),
    ...zeilen.map((zl, zi) =>
      new TableRow({
        children: zl.map((t, i) =>
          zelle(t, {
            breite: spaltenbreiten[i],
            fuell: (opt.summeLetzte && zi === zeilen.length - 1) ? HELL : undefined,
            bold: (opt.summeLetzte && zi === zeilen.length - 1) || (i === 0 && opt.ersteFett),
            rechts: i > 0 && opt.rechtsAb !== false,
          })),
      })),
  ];
  return new Table({
    columnWidths: spaltenbreiten,
    width: { size: BREITE, type: WidthType.DXA },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 2, color: LINIE },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: LINIE },
      left:   { style: BorderStyle.SINGLE, size: 2, color: LINIE },
      right:  { style: BorderStyle.SINGLE, size: 2, color: LINIE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: LINIE },
      insideVertical:   { style: BorderStyle.SINGLE, size: 2, color: LINIE },
    },
    rows: reihen,
  });
}

const abstand = (h = 160) => new Paragraph({ spacing: { after: h }, children: [] });

// ---------------------------------------------------------------- Inhalt

// Aufruf mit "ihk" erzeugt die Fassung für die IHK-Durchsicht: ohne die
// Kundennummer des Jobcenters, sonst wortgleich.
const FUER_IHK = process.argv.includes("ihk");

const inhalt = [];

// Titel
inhalt.push(
  new Paragraph({
    spacing: { after: 80 },
    children: [f("Businessplan", { size: 48, bold: true, color: GRUEN })],
  }),
  new Paragraph({
    spacing: { after: 400 },
    children: [f("Technische Einrichtung der elektronischen Rechnung für Handwerksbetriebe",
                 { size: 24, color: "444444" })],
  }),
  p("Gründer: Faruk Polat"),
  p("Anschrift: In den Rübgärten 17, 61476 Kronberg im Taunus"),
  p("Telefon / E-Mail: 0152 28487769 / farukpolat@mail.de"),
  ...(FUER_IHK ? [] : [platzhalter("Kundennummer Jobcenter: ", "[Nummer]")]),
  p("Geplanter Beginn der Tätigkeit: nach Bewilligung des Einstiegsgelds, voraussichtlich viertes Quartal 2026"),
  p("Stand: September 2026"),
  abstand(240),
  new Paragraph({
    spacing: { after: 200 },
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: GRUEN, space: 6 } },
    children: [],
  }),
  p("Dieser Businessplan wird zusammen mit dem Antrag auf Einstiegsgeld nach § 16b SGB II eingereicht. Die Tätigkeit wird erst nach Bewilligung aufgenommen und das Gewerbe erst dann angemeldet.",
    { italics: true, color: "444444" }),
);

// 1
inhalt.push(
  h1("1  Zusammenfassung"),
  p("Ab dem 1. Januar 2028 müssen alle inländischen Unternehmen im Geschäftsverkehr untereinander elektronische Rechnungen nach der europäischen Norm EN 16931 ausstellen. Für Unternehmen mit mehr als 800.000 Euro Vorjahresumsatz gilt diese Pflicht bereits ab dem 1. Januar 2027. Die Pflicht, elektronische Rechnungen zu empfangen und verarbeiten zu können, besteht seit dem 1. Januar 2025 ausnahmslos für jeden Betrieb."),
  p("Handwerksbetriebe mit weniger als 800.000 Euro Umsatz verfügen in der Regel weder über eine IT-Abteilung noch über einen Dienstleister, der diese Umstellung für sie übernimmt. Ihre Steuerkanzleien führen die Buchhaltung, richten aber keine Rechnungssoftware im Betrieb ein."),
  p("Das Angebot schließt genau diese Lücke: die technische Einrichtung der vorhandenen Rechnungssoftware für Empfang und Versand elektronischer Rechnungen, zum Festpreis, vor Ort beim Betrieb. Steuerberatung wird ausdrücklich nicht erbracht."),
  p("Die Nachfrage ist gesetzlich erzeugt und terminiert. Sie ist nicht von Konjunktur oder Werbebudget abhängig, sondern von einem Stichtag, der für alle gilt."),
  p("Ich bringe drei Jahre Erfahrung im technischen Außendienst mit eigenverantwortlicher Kundenbetreuung mit sowie eine abgeschlossene Ausbildung als Mediengestalter Digital und Print. Der Vertriebsweg und die Arbeitsweise dieses Vorhabens entsprechen damit meiner bisherigen Tätigkeit."),
);

// 2
inhalt.push(
  h1("2  Zur Person"),
  p("Faruk Polat, geboren am 20. Juli 1976 in Rüsselsheim, deutsche Staatsangehörigkeit."),
  p("In den Rübgärten 17, 61476 Kronberg im Taunus · Telefon 0152 28487769 · farukpolat@mail.de"),
  abstand(80),
  h2("Ausbildung"),
  punkt("08/2016 – 08/2018  Mediengestalter Digital und Print, Setzerei Schaupp, Darmstadt — Abschluss: gut"),
  punkt("07/1999 – 09/2001  Berufskraftfahrer (IHK), VPI Fahrschule Frankfurt — Abschluss: sehr gut"),
  abstand(80),
  h2("Beruflicher Werdegang"),
  punkt("07/2022 – 07/2025  Außendienstmitarbeiter, Dallmayr, Langen — technischer Vertrieb, eigenverantwortliche Betreuung von Geschäftskunden, Erfassung technischer Daten und Dokumentation von Rückmeldungen"),
  punkt("09/2018 – 06/2022  Mediengestalter Digital und Print — Konzeption und Umsetzung technischer Produktionsabläufe, Qualitätskontrolle, präzise Datenaufbereitung"),
  punkt("09/2002 – 10/2015  Flugzeugschlepperfahrer im technischen Bereich, Lufthansa AG, Frankfurt am Main — Bedienung schwerer Spezialfahrzeuge unter Sicherheitsauflagen, Wartung und Instandhaltung"),
  abstand(80),
  h2("Weitere Qualifikationen"),
  punkt("Führerscheinklassen B, C, CE, D und DE sowie Personenbeförderungsschein"),
  punkt("Deutsch und Türkisch jeweils auf Muttersprachenniveau"),
  abstand(120),
  h2("Warum diese Erfahrung das Vorhaben trägt"),
  p("Der Vertriebsweg dieses Vorhabens ist Direktansprache und persönliche Betreuung vor Ort. Genau das war meine Tätigkeit der letzten drei Jahre: Als Außendienstmitarbeiter im technischen Vertrieb habe ich Geschäftskunden eigenverantwortlich betreut, technische Sachverhalte vor Ort erfasst und dokumentiert. Die Arbeitsweise ist dieselbe, nur das Fachgebiet ist ein anderes."),
  p("Die Ausbildung zum Mediengestalter Digital und Print vermittelt den Umgang mit strukturierten Datenformaten, Datenaufbereitung und Qualitätskontrolle. Eine elektronische Rechnung ist nichts anderes als ein strukturierter Datensatz, dessen Prüfung genau diese Arbeitsweise verlangt."),
  p("Dreizehn Jahre im technischen Betrieb eines Luftfahrtunternehmens bedeuten Arbeiten nach Vorschrift, unter Sicherheitsauflagen und mit Dokumentationspflicht. Die Einrichtung einer normkonformen Rechnungsstellung ist ebenfalls Arbeit nach einem Regelwerk, bei der Sorgfalt vor Geschwindigkeit geht."),
  p("Die Führerscheinklassen erlauben Kundentermine im gesamten Rhein-Main-Gebiet ohne Einschränkung. Deutsch und Türkisch auf Muttersprachenniveau erschließen zusätzlich einen Teil des Marktes, der für die meisten Anbieter sprachlich schwer erreichbar ist: die zahlreichen türkischstämmig geführten Handwerksbetriebe der Region, die dieselbe gesetzliche Frist trifft."),
  abstand(80),
  h2("Fachliche Vorbereitung auf diese Tätigkeit"),
  p("Zur Vorbereitung wurden folgende Grundlagen erarbeitet und dokumentiert:"),
  punkt("Einarbeitung in die europäische Norm EN 16931 sowie in die Formate XRechnung und ZUGFeRD/Factur-X"),
  punkt("Erstellung eines eigenen Prüfwerkzeugs, das elektronische Rechnungen einliest und lesbar darstellt; es arbeitet ausschließlich im Browser des Anwenders, sodass keine Rechnungsdaten übertragen werden"),
  punkt("Systematische Erhebung, welche gängigen Rechnungsprogramme elektronische Rechnungen ausgeben können, an welcher Stelle die Funktion aktiviert wird und welche Stammdaten dafür zwingend erforderlich sind"),
  punkt("Aufbau eines Fehlerkatalogs der zehn häufigsten Ursachen, aus denen elektronische Rechnungen von Empfängern zurückgewiesen werden"),
  punkt("Erarbeitung eines strukturierten Ablaufs je Auftrag von der Bestandsaufnahme bis zur geprüften Testrechnung"),
  abstand(80),
  h2("Motivation"),
  p("Nach dem Ende meiner letzten Anstellung suche ich eine Tätigkeit, die meine Erfahrung im Außendienst mit technischer Sorgfalt verbindet und in der ich eigenverantwortlich arbeite. Die E-Rechnungspflicht trifft ab 2028 alle Betriebe, und gerade die kleinen haben niemanden, der die Umstellung für sie übernimmt. Die Tätigkeit erfordert kein Startkapital, keine Warenlager und keine Angestellten und lässt sich vom ersten Auftrag an tragen."),
);

// 3
inhalt.push(
  h1("3  Angebot"),
  p("Die Leistung wird als abgeschlossener Auftrag zum Festpreis erbracht. Es entstehen weder Abonnements noch laufende Kosten für den Kunden."),
  abstand(80),
  h2("Ablauf je Auftrag"),
  punkt("Bestandsaufnahme: eingesetztes Rechnungsprogramm, Rechnungsmenge, betroffene Fristen"),
  punkt("Einrichtung des Empfangswegs für eingehende elektronische Rechnungen und der zugehörigen Ablage"),
  punkt("Aktivierung und Konfiguration des Versands im vorhandenen Programm"),
  punkt("Prüfung der Stammdaten und der Steuerschlüssel, insbesondere bei Bauleistungen nach § 13b UStG und bei der Kleinunternehmerregelung nach § 19 UStG"),
  punkt("Erzeugung einer Testrechnung und Prüfung gegen den offiziellen Validierungsdienst"),
  punkt("Übergabe einer einseitigen Anleitung für das Büro des Betriebs"),
  abstand(120),
  h2("Leistungspakete und Preise"),
  tabelle(
    [3000, 3670, 2400],
    ["Paket", "Für wen", "Festpreis"],
    [
      ["Einrichtung Standard", "Betrieb mit gängigem Rechnungsprogramm", "450 – 650 €"],
      ["Umstieg", "Betrieb ohne Rechnungsprogramm, bisher Word oder Excel", "900 – 1.400 €"],
      ["Nur Empfang", "Kleinunternehmer nach § 19 UStG, dauerhaft vom Versand befreit", "190 – 290 €"],
      ["Datenbereinigung", "Zusatzleistung bei unbrauchbaren Altdaten", "nach Aufwand"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
  abstand(120),
  abstand(60),
  h2("Herleitung des Durchschnittserlöses"),
  p("Die Vorschau rechnet nicht mit einem einzelnen Preis, sondern mit einem angenommenen Auftragsmix. Je zehn Aufträge wird unterstellt:"),
  tabelle(
    [2600, 1500, 2470, 2500],
    ["Paket", "Anteil", "Angesetzt", "Erlös"],
    [
      ["Einrichtung Standard", "6 von 10", "550 €", "3.300 €"],
      ["Umstieg", "2 von 10", "1.150 €", "2.300 €"],
      ["Nur Empfang", "2 von 10", "240 €", "480 €"],
      ["Summe je zehn Aufträge", "", "", "6.080 €"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
  abstand(80),
  p("Daraus ergibt sich ein Durchschnittserlös von 608 Euro. In der Vorschau wird auf 600 Euro abgerundet. Angesetzt ist jeweils die Mitte der Preisspanne, nicht der obere Rand. Die Zusatzleistung Datenbereinigung bleibt vollständig unberücksichtigt, obwohl sie erfahrungsgemäß bei einem Teil der Aufträge anfällt.", { italics: true, color: "444444" }),
);

// 4
inhalt.push(
  new Paragraph({ children: [new PageBreak()] }),
  h1("4  Markt und gesetzlicher Rahmen"),
  tabelle(
    [2400, 3200, 3470],
    ["Ab wann", "Wen es betrifft", "Welche Pflicht"],
    [
      ["seit 01.01.2025", "jedes inländische Unternehmen", "E-Rechnungen empfangen und verarbeiten können"],
      ["ab 01.01.2027", "über 800.000 € Vorjahresumsatz", "E-Rechnungen ausstellen"],
      ["ab 01.01.2028", "alle übrigen Unternehmen", "E-Rechnungen ausstellen"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
  abstand(140),
  p("Ausgenommen sind Kleinbetragsrechnungen bis 250 Euro brutto, Rechnungen an Privatpersonen sowie bestimmte nach § 4 UStG steuerfreie Umsätze. Kleinunternehmer nach § 19 UStG sind vom Ausstellen dauerhaft befreit, von der Empfangspflicht jedoch nicht."),
  p("Für den Markt bedeutet das: Die Nachfrage entsteht nicht durch Überzeugung, sondern durch eine Frist. Sie steigt bis Ende 2027 an und erreicht 2028 ihren Höhepunkt."),
  abstand(80),
  h2("Zielgruppe"),
  punkt("Handwerks- und Baubetriebe mit etwa 3 bis 30 Beschäftigten und einem Umsatz unterhalb von 800.000 Euro"),
  punkt("Betriebe, die ihre Rechnungen selbst schreiben und kein Warenwirtschaftssystem einsetzen"),
  punkt("Besonders betroffen: Betriebe, die Bauleistungen nach § 13b UStG abrechnen"),
  abstand(80),
  h2("Wettbewerb"),
  tabelle(
    [2900, 3200, 2970],
    ["Anbieter", "Was er tut", "Abgrenzung"],
    [
      ["Steuerkanzleien", "Buchhaltung und steuerliche Beurteilung", "richten keine Software im Betrieb ein; sind Empfehlungsgeber, nicht Wettbewerber"],
      ["Softwarehersteller", "liefern die Funktion im Programm", "unterstützen nicht bei der Einrichtung vor Ort"],
      ["IT-Dienstleister", "allgemeine EDV-Betreuung", "kennen die Anforderungen der Norm meist nicht im Detail"],
      ["Anbieter von Zusatzsoftware", "Programme zur Rechnungserstellung", "verkaufen ein Produkt, keine Einrichtung"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
  abstand(140),
  p("Der Wettbewerbsvorteil liegt in der Verbindung aus Fachkenntnis der Norm, persönlicher Erreichbarkeit vor Ort und einem Festpreis ohne Folgekosten."),
);

// 5
inhalt.push(
  h1("5  Vertriebswege"),
  h2("Erster Weg: Steuerkanzleien"),
  p("Eine Kanzlei mit 200 Mandanten betreut 200 Betriebe, die bis 2028 umstellen müssen und die ihre Kanzlei danach fragen werden. Die Einrichtung von Software im Betrieb gehört nicht zum Leistungsbild einer Kanzlei. Angeboten wird daher eine klare Arbeitsteilung: Die steuerliche Beurteilung verbleibt bei der Kanzlei, die technische Einrichtung wird übernommen. Für die Kanzlei entstehen keine Kosten; Vermittlungsentgelte werden ausdrücklich nicht gezahlt."),
  h2("Zweiter Weg: Innungen und Kreishandwerkerschaften"),
  p("Diesen Organisationen obliegt die Unterstützung ihrer Mitgliedsbetriebe bei gesetzlichen Pflichten. Angeboten wird ein kostenloser, herstellerneutraler Kurzvortrag von etwa zwanzig Minuten im Rahmen von Mitgliederversammlungen und Informationsabenden. Ein Vortrag erreicht dreißig bis vierzig Betriebe gleichzeitig."),
  h2("Dritter Weg: Direktansprache"),
  p("Telefonische Ansprache von Handwerksbetrieben in der Region auf Grundlage öffentlich zugänglicher Verzeichnisse, mit dem Hinweis auf die bereits laufende Empfangspflicht als Gesprächsanlass."),
  h2("Vierter Weg: türkischsprachige Betriebe"),
  p("Im Rhein-Main-Gebiet wird eine erhebliche Zahl von Handwerksbetrieben türkischstämmig geführt. Diese Betriebe unterliegen derselben Frist, werden von den üblichen Anbietern aber sprachlich kaum erreicht und informieren sich stark über persönliche Empfehlung innerhalb ihrer Netzwerke. Da ich Türkisch auf Muttersprachenniveau spreche, ist dieser Teil des Marktes für mich ohne Zusatzaufwand zugänglich."),
  h2("Unterstützend: eigene Internetseite"),
  p("Die Seite stellt ein kostenloses Werkzeug bereit, mit dem sich eine elektronische Rechnung lesbar machen lässt, sowie eine kurze Selbstauskunft zur eigenen Betroffenheit. Sie dient als Nachweis der Fachkenntnis im Anschluss an einen persönlichen Kontakt, nicht als eigenständiger Werbekanal."),
);

// 6
inhalt.push(
  new Paragraph({ children: [new PageBreak()] }),
  h1("6  Kapitalbedarf"),
  p("Der Kapitalbedarf ist gering, weil weder Waren noch Maschinen noch Geschäftsräume erforderlich sind. Ein geeigneter Rechner ist vorhanden."),
  tabelle(
    [5670, 3400],
    ["Position", "Betrag"],
    [
      ["Betriebshaftpflichtversicherung, Jahresbeitrag im Voraus", "300 €"],
      ["Erstellung der Allgemeinen Geschäftsbedingungen durch einen Rechtsanwalt", "500 €"],
      ["Domain und Webhosting für ein Jahr", "120 €"],
      ["Visitenkarten, Informationsblätter, Druckkosten", "200 €"],
      ["Fachliteratur und Normzugang", "150 €"],
      ["Rücklage für Fahrtkosten der ersten drei Monate", "300 €"],
      ["Gesamter Kapitalbedarf", "1.570 €"],
    ],
    { summeLetzte: true },
  ),
  abstand(140),
  p("Für diesen Bedarf wird ergänzend eine Förderung nach § 16c SGB II beantragt. Ein Bankdarlehen ist nicht vorgesehen und wäre bei diesem Volumen unwirtschaftlich."),
);

// 7
inhalt.push(
  h1("7  Umsatz- und Rentabilitätsvorschau"),
  h2("Auftragsentwicklung im ersten Jahr"),
  p("Die Planung geht bewusst von einem langsamen Anlauf aus. In den ersten beiden Monaten wird kein Umsatz erwartet, da zunächst die Vertriebswege aufgebaut werden."),
  tabelle(
    [2200, 1900, 2400, 2570],
    ["Zeitraum", "Aufträge", "Umsatz", "Anmerkung"],
    [
      ["Monat 1 – 2", "0", "0 €", "Aufbau, Kanzleien und Innungen ansprechen"],
      ["Monat 3 – 4", "2", "1.200 €", "erste Empfehlungen"],
      ["Monat 5 – 6", "4", "2.400 €", "erste Vorträge wirken"],
      ["Monat 7 – 9", "9", "5.400 €", "Empfehlungen aus abgeschlossenen Aufträgen"],
      ["Monat 10 – 12", "12", "7.200 €", "Frist 2027 rückt näher"],
      ["Jahr 1 gesamt", "27", "16.200 €", ""],
    ],
    { summeLetzte: true },
  ),
  abstand(160),
  h2("Drei-Jahres-Vorschau"),
  tabelle(
    [3070, 2000, 2000, 2000],
    ["", "Jahr 1", "Jahr 2", "Jahr 3"],
    [
      ["Aufträge", "27", "72", "96"],
      ["Umsatz", "16.200 €", "44.640 €", "61.440 €"],
      ["Betriebsausgaben", "3.780 €", "5.500 €", "7.000 €"],
      ["Gewinn vor Steuern", "12.420 €", "39.140 €", "54.440 €"],
      ["Gewinn je Monat im Mittel", "1.035 €", "3.262 €", "4.537 €"],
    ],
    { ersteFett: true, summeLetzte: true },
  ),
  abstand(160),
  h2("Betriebsausgaben im ersten Jahr"),
  tabelle(
    [5670, 3400],
    ["Position", "Jahr 1"],
    [
      ["Fahrtkosten zu Kundenterminen", "900 €"],
      ["Buchführung und Steuerberatung", "600 €"],
      ["Allgemeine Geschäftsbedingungen, einmalig", "500 €"],
      ["Telefon und Internet, anteilig", "360 €"],
      ["Betriebshaftpflichtversicherung", "300 €"],
      ["Werbung und Druckkosten", "300 €"],
      ["Weiterbildung und Fachliteratur", "250 €"],
      ["Büromaterial und Porto", "250 €"],
      ["Software und Prüfwerkzeuge", "200 €"],
      ["Domain und Webhosting", "120 €"],
      ["Summe", "3.780 €"],
    ],
    { summeLetzte: true },
  ),
);

// 8
inhalt.push(
  new Paragraph({ children: [new PageBreak()] }),
  h1("8  Weg aus dem Leistungsbezug"),
  p("Um den Leistungsbezug vollständig zu beenden, muss der monatliche Gewinn den bisherigen Bedarf sowie die dann selbst zu tragende Kranken- und Pflegeversicherung und eine Rücklage für die Einkommensteuer decken."),
  tabelle(
    [5670, 3400],
    ["Position", "monatlich"],
    [
      ["Bisheriger Bedarf einschließlich Kosten der Unterkunft", "[eigenen Betrag eintragen]"],
      ["Freiwillige gesetzliche Kranken- und Pflegeversicherung, geschätzt", "rund 260 €"],
      ["Rücklage für Einkommensteuer", "rund 150 €"],
      ["Erforderlicher Gewinn je Monat", "rund 1.850 €"],
    ],
    { summeLetzte: true },
  ),
  abstand(160),
  p("Nach der vorstehenden Planung wird dieser Wert im Verlauf des zweiten Geschäftsjahres dauerhaft überschritten. Das Einstiegsgeld wird daher für die Aufbauphase benötigt, in der die Vertriebswege wirken, aber noch nicht tragen."),
  p("Die Förderdauer von bis zu 24 Monaten deckt genau diesen Zeitraum ab. Ab dem zweiten Jahr ist die Tätigkeit nach dieser Planung tragfähig."),
  abstand(80),
  h2("Chancen"),
  punkt("Die Nachfrage ist gesetzlich erzeugt und mit einem festen Stichtag versehen"),
  punkt("Sehr geringer Kapitalbedarf, dadurch kein Verschuldungsrisiko"),
  punkt("Empfehlungen wirken im Handwerk stark; Innungen und Kanzleien bündeln viele Betriebe"),
  punkt("Bauleistungen nach § 13b sind ein Sonderfall, den verbreitete Programme derzeit nicht abbilden — hier besteht ein besonderer Beratungsbedarf"),
  abstand(80),
  h2("Risiken und Gegenmaßnahmen"),
  tabelle(
    [4200, 4870],
    ["Risiko", "Gegenmaßnahme"],
    [
      ["Die Nachfrage bricht nach dem Stichtag 2028 ein", "Ausbau des Folgegeschäfts: Prüfung des Empfangswegs, Betreuung bei neuen Formatversionen, Unterstützung bei künftigen Meldepflichten"],
      ["Softwarehersteller vereinfachen die Einrichtung so weit, dass keine Hilfe mehr nötig ist", "Verlagerung des Schwerpunkts auf Betriebe ohne Rechnungsprogramm und auf Sonderfälle wie § 13b"],
      ["Der Anlauf dauert länger als geplant", "Fortführung des Leistungsbezugs während der Aufbauphase; die Kostenstruktur ist so niedrig, dass keine Verluste entstehen"],
      ["Haftung bei fehlerhafter Einrichtung", "Abgrenzung in den Geschäftsbedingungen auf die technische Einrichtung, Betriebshaftpflichtversicherung, keine steuerliche Beratung"],
      ["Wettbewerber treten in den Markt ein", "Regionale Präsenz und persönliche Erreichbarkeit; frühzeitiger Aufbau der Empfehlungswege"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
);

// 9
inhalt.push(
  h1("9  Rechtliche Rahmenbedingungen"),
  tabelle(
    [3000, 6070],
    ["Punkt", "Vorgesehene Umsetzung"],
    [
      ["Rechtsform", "Einzelunternehmen"],
      ["Anmeldung", "Gewerbeanmeldung beim örtlichen Gewerbeamt nach Bewilligung des Einstiegsgeldes"],
      ["Steuer", "Anmeldung beim Finanzamt; Kleinunternehmerregelung nach § 19 UStG wird im ersten Jahr geprüft"],
      ["Erlaubnisse", "keine erforderlich; es handelt sich nicht um ein zulassungspflichtiges Handwerk"],
      ["Abgrenzung", "keine Steuerberatung nach StBerG und keine Rechtsdienstleistung nach RDG; dies wird im Impressum und in den Geschäftsbedingungen ausgewiesen"],
      ["Versicherung", "Betriebshaftpflichtversicherung vor dem ersten Auftrag"],
      ["Datenschutz", "das eingesetzte Prüfwerkzeug verarbeitet Rechnungsdaten ausschließlich lokal beim Anwender; eine Übertragung findet nicht statt"],
    ],
    { ersteFett: true, rechtsAb: false },
  ),
  abstand(200),
  h1("10  Anlagen"),
  punkt("Lebenslauf"),
  punkt("Erhebung der geprüften Rechnungsprogramme mit Angabe der jeweiligen Quelle"),
  punkt("Fehlerkatalog der häufigsten Ablehnungsgründe"),
  punkt("Ablaufplan je Auftrag"),
  punkt("Ausdruck der Internetseite mit dem kostenlosen Prüfwerkzeug"),
  abstand(240),
  p("Ort, Datum und Unterschrift", { color: "888888", italics: true }),
);

// ---------------------------------------------------------------- Dokument

const doc = new Document({
  creator: "Businessplan",
  title: "Businessplan – Einrichtung elektronischer Rechnungen",
  numbering: {
    config: [{
      reference: "striche",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "–",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 200 } } },
      }],
    }],
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 21 } },
    },
  },
  sections: [{
    properties: {
      page: {
        margin: {
          top: convertMillimetersToTwip(25),
          right: convertMillimetersToTwip(25),
          bottom: convertMillimetersToTwip(25),
          left: convertMillimetersToTwip(25),
        },
      },
    },
    children: inhalt,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const datei = FUER_IHK ? "Businessplan-E-Rechnung-IHK.docx" : "Businessplan-E-Rechnung.docx";
  fs.writeFileSync(datei, buf);
  console.log("geschrieben:", datei, buf.length, "Bytes");
});
