#!/usr/bin/env node
/**
 * Erzeugt den fertigen Prüfbericht als Word-Datei aus
 *   funde.csv      – eine Zeile je Fund
 *   bericht.json   – Betrieb, Lieferanten, Muster, Empfehlungen
 *
 *   node erzeuge-bericht.js [--muster]
 *
 * Gerechnet wird hier, nicht von Hand: Summe der belegbaren Funde,
 * Anzahl der Funde, geprüfte Rechnungen, Einkaufsvolumen und die
 * Jahreshochrechnung. Damit stehen im Bericht keine Tippfehler.
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, PageBreak, Footer,
} = require("docx");

const HIER = __dirname;
const MUSTER = process.argv.includes("--muster");

// ------------------------------------------------------------------ Einlesen

function leseCsv(datei) {
  let roh = fs.readFileSync(datei, "utf8");
  if (roh.charCodeAt(0) === 0xfeff) roh = roh.slice(1); // BOM aus Excel
  const zeilen = roh.split(/\r?\n/).filter((z) => z.trim() !== "");
  const kopf = zerlege(zeilen[0]).map((s) => s.toLowerCase());
  return zeilen.slice(1).map((z, i) => {
    const f = zerlege(z);
    if (f.length < kopf.length) {
      throw new Error(`funde.csv Zeile ${i + 2}: ${f.length} Felder, erwartet ${kopf.length}`);
    }
    const o = {};
    kopf.forEach((k, j) => (o[k] = (f[j] || "").trim()));
    return o;
  });
}

/* Semikolon-getrennt, Anführungszeichen werden respektiert. */
function zerlege(zeile) {
  const felder = [];
  let akt = "", inAnf = false;
  for (let i = 0; i < zeile.length; i++) {
    const c = zeile[i];
    if (c === '"') {
      if (inAnf && zeile[i + 1] === '"') { akt += '"'; i++; } else { inAnf = !inAnf; }
    } else if (c === ";" && !inAnf) { felder.push(akt); akt = ""; }
    else { akt += c; }
  }
  felder.push(akt);
  return felder;
}

/* "1.310,40 €" -> 1310.4 */
function zahl(text) {
  const s = String(text).replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}
const eur = (n) => n.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
const eur0 = (n) => Math.round(n).toLocaleString("de-DE") + " €";

const cfg = JSON.parse(fs.readFileSync(path.join(HIER, "bericht.json"), "utf8"));
const funde = leseCsv(path.join(HIER, "funde.csv"));

// ------------------------------------------------------------------ Rechnen

const ERLAUBT = ["sicher", "zu klären"];
funde.forEach((f, i) => {
  if (!ERLAUBT.includes(f.status)) {
    throw new Error(`funde.csv Zeile ${i + 2}: Status "${f.status}" unbekannt. Erlaubt: ${ERLAUBT.join(", ")}`);
  }
});

const sicher   = funde.filter((f) => f.status === "sicher");
const summeSicher = sicher.reduce((s, f) => s + zahl(f.differenz), 0);
const summeAlle   = funde.reduce((s, f) => s + zahl(f.differenz), 0);
const rechnungen  = cfg.lieferanten.reduce((s, l) => s + Number(l.rechnungen || 0), 0);
const volumen     = cfg.lieferanten.reduce((s, l) => s + Number(l.volumen || 0), 0);
const jahr        = summeSicher * 4;

// ------------------------------------------------------------------ Bausteine

const F = "Arial";
const INK = "1F2A28", MUT = "5B6A67", AKZ = "0E5B50", WERT = "B45309", LIN = "D3DAD7";
const BREITE = 9638;

const keinRahmen = { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE},
                     left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} };
const duenn = { style: BorderStyle.SINGLE, size: 4, color: LIN };
const rahmen = { top: duenn, bottom: duenn, left: duenn, right: duenn };

const t = (text, o = {}) => new TextRun({
  text: String(text), font: F, size: o.size || 20, bold: !!o.bold,
  color: o.color || INK, allCaps: !!o.caps, characterSpacing: o.caps ? 20 : undefined,
});
const p = (runs, o = {}) => new Paragraph({
  children: Array.isArray(runs) ? runs : [runs],
  spacing: { before: o.before || 0, after: o.after === undefined ? 100 : o.after, line: 264 },
  alignment: o.align, border: o.border,
});
const leer = (h = 120) => new Paragraph({ children: [], spacing: { after: h } });
const abschnitt = (titel) => new Paragraph({
  children: [t(titel, { bold: true, size: 20, color: AKZ, caps: true })],
  spacing: { before: 320, after: 140 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AKZ } },
});
const zelle = (kinder, o = {}) => new TableCell({
  children: kinder, width: { size: o.w, type: WidthType.DXA },
  margins: { top: 90, bottom: 90, left: 120, right: 120 },
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
  borders: o.borders || rahmen, columnSpan: o.span,
});
const kopfZelle = (text, w, align) =>
  zelle([p(t(text, { bold: true, size: 15, color: MUT, caps: true }), { after: 0, align })], { w, fill: "F1F5F3" });
const txtZelle = (text, w, o = {}) =>
  zelle([p(t(text, { size: 18, color: o.color || INK, bold: o.bold }), { after: 0, align: o.align })], { w, fill: o.fill });
const wertZelle = (text, w, o = {}) => txtZelle(text, w, { ...o, color: WERT });
const tabelle = (spalten, reihen) =>
  new Table({ width: { size: BREITE, type: WidthType.DXA }, columnWidths: spalten, rows: reihen });

const banner = () => new Table({
  width: { size: BREITE, type: WidthType.DXA }, columnWidths: [BREITE],
  rows: [new TableRow({ children: [zelle([
    p(t("Musterbericht — Beispiel mit erfundenen Daten", { bold: true, size: 20, color: "FFFFFF", caps: true }), { after: 40 }),
    p(t("Dies ist kein Bericht eines echten Kunden. Betrieb, Lieferanten, Rechnungsnummern und Beträge sind frei erfunden und dienen nur der Veranschaulichung.", { size: 16, color: "FFFFFF" }), { after: 0 }),
  ], { w: BREITE, fill: "A9451B", borders: keinRahmen })] })],
});

// ------------------------------------------------------------------ Seite 1

const kopf = [
  ...(MUSTER ? [banner(), leer(200)] : []),
  new Paragraph({ children: [t("Prüfbericht Eingangsrechnungen", { bold: true, size: 34 })], spacing: { after: 60 } }),
  new Paragraph({
    children: [t("Kostenlose Erstprüfung · Prüfstand · Faruk Polat", { size: 18, color: MUT })],
    spacing: { after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: INK } },
  }),
  leer(140),
  tabelle([2200, 2619, 2200, 2619], [
    new TableRow({ children: [
      kopfZelle("Betrieb", 2200), wertZelle(cfg.betrieb, 2619),
      kopfZelle("Erstellt am", 2200), wertZelle(cfg.erstellt_am, 2619),
    ]}),
    new TableRow({ children: [
      kopfZelle("Geprüfter Zeitraum", 2200), wertZelle(cfg.zeitraum, 2619),
      kopfZelle("Geprüft von", 2200), txtZelle(cfg.geprueft_von, 2619),
    ]}),
  ]),

  abschnitt("Das Ergebnis"),
  p([
    t("In den geprüften Rechnungen wurden ", { size: 24 }),
    t(eur(summeAlle), { size: 24, bold: true, color: WERT }),
    t(" zu viel berechnet. Davon sind ", { size: 24 }),
    t(eur(summeSicher), { size: 24, bold: true, color: WERT }),
    t(" belegbar, der Rest ist zu klären.", { size: 24 }),
  ], { after: 200 }),
  tabelle([2410, 2410, 2409, 2409], [
    new TableRow({ children: [
      kopfZelle("Rechnungen geprüft", 2410, AlignmentType.CENTER),
      kopfZelle("Einkaufsvolumen", 2410, AlignmentType.CENTER),
      kopfZelle("Funde", 2409, AlignmentType.CENTER),
      kopfZelle("Davon belegbar", 2409, AlignmentType.CENTER),
    ]}),
    new TableRow({ children: [
      wertZelle(String(rechnungen), 2410, { align: AlignmentType.CENTER, bold: true }),
      wertZelle(eur0(volumen), 2410, { align: AlignmentType.CENTER, bold: true }),
      wertZelle(String(funde.length), 2409, { align: AlignmentType.CENTER, bold: true }),
      wertZelle(eur(summeSicher), 2409, { align: AlignmentType.CENTER, bold: true }),
    ]}),
  ]),

  abschnitt("Prüfumfang je Lieferant"),
  p(t("Wir prüfen dort am gründlichsten, wo der größte Teil des Einkaufs läuft. Diese Tabelle zeigt, welcher Lieferant wie tief geprüft wurde.", { size: 18, color: MUT }), { after: 160 }),
  tabelle([3200, 1300, 1800, 3338], [
    new TableRow({ children: [
      kopfZelle("Lieferant", 3200), kopfZelle("Rechnungen", 1300, AlignmentType.CENTER),
      kopfZelle("Volumen", 1800, AlignmentType.RIGHT), kopfZelle("Prüftiefe", 3338),
    ]}),
    ...cfg.lieferanten.map((l) => new TableRow({ children: [
      wertZelle(l.name, 3200),
      wertZelle(String(l.rechnungen), 1300, { align: AlignmentType.CENTER }),
      wertZelle(eur0(l.volumen), 1800, { align: AlignmentType.RIGHT }),
      txtZelle(l.tiefe, 3338),
    ]})),
  ]),

  abschnitt("Die Funde im Einzelnen"),
  tabelle([1900, 1750, 2050, 1700, 1100, 1138], [
    new TableRow({ children: [
      kopfZelle("Lieferant", 1900), kopfZelle("Rechnung / Datum", 1750),
      kopfZelle("Prüfpunkt", 2050), kopfZelle("Soll → Ist", 1700),
      kopfZelle("Differenz", 1100, AlignmentType.RIGHT), kopfZelle("Status", 1138),
    ]}),
    ...funde.map((f) => new TableRow({ children: [
      wertZelle(f.lieferant, 1900),
      wertZelle(f.rechnung + " · " + f.datum, 1750),
      wertZelle(f.pruefpunkt, 2050),
      wertZelle(f.soll + " → " + f.ist, 1700),
      wertZelle(eur(zahl(f.differenz)), 1100, { align: AlignmentType.RIGHT }),
      wertZelle(f.status, 1138),
    ]})),
    new TableRow({ children: [
      zelle([p(t("Summe belegbar", { bold: true, size: 18 }), { after: 0, align: AlignmentType.RIGHT })],
        { w: 8500, span: 5, fill: "F1F5F3" }),
      zelle([p(t(eur(summeSicher), { bold: true, size: 18, color: WERT }), { after: 0 })],
        { w: 1138, fill: "F1F5F3" }),
    ]}),
  ]),
  p(t("„Sicher“ bedeutet: mit Rechnung und Beleg nachweisbar. „Zu klären“ bedeutet: auffällig, aber ohne weitere Unterlage nicht belegbar. In die Summe zählt nur, was sicher ist.", { size: 16, color: MUT }), { before: 140 }),
];

// ------------------------------------------------------------------ Seite 2

const seite2 = [
  new Paragraph({ children: [new PageBreak()] }),
  ...(MUSTER ? [banner(), leer(160)] : []),

  abschnitt("Was sich wiederholt"),
  p(t("Einzelne Fehler passieren. Muster sind der eigentliche Befund — sie kommen wieder, solange niemand hinschaut.", { size: 18, color: MUT }), { after: 160 }),
  ...cfg.muster.map((m) => p([t(m.lieferant + " — ", { bold: true }), t(m.text, { color: WERT })])),

  abschnitt("Was wir nicht prüfen konnten"),
  p(t("Damit ihr wisst, wo noch etwas liegen kann:", { size: 18, color: MUT }), { after: 140 }),
  ...cfg.nicht_geprueft.map((z) =>
    p([t("• ", { color: AKZ, bold: true }), t(z, { color: WERT })], { after: 60 })),

  abschnitt("Empfohlene nächste Schritte"),
  ...cfg.empfehlungen.map((z, i) =>
    p([t(i + 1 + ". ", { bold: true, color: AKZ }), t(z, { color: WERT })], { after: 80 })),

  abschnitt("Wenn nichts geschieht"),
  p([
    t("Die gefundenen Muster wiederholen sich, solange die Rechnungen nicht laufend geprüft werden. Auf ein Jahr hochgerechnet stehen den "),
    t(eur0(summeSicher), { bold: true, color: WERT }),
    t(" aus einem Quartal grob "),
    t(eur0(jahr), { bold: true, color: WERT }),
    t(" gegenüber — vorausgesetzt, Einkaufsvolumen und Fehlerbild bleiben gleich. Wenn ihr wollt, prüfen wir jede Eingangsrechnung, bevor sie bezahlt wird. Umfang und Preis besprechen wir persönlich."),
  ]),

  abschnitt("Hinweise"),
  p(t("Diese Prüfung umfasst das rechnerische und sachliche Nachvollziehen von Eingangsrechnungen. Sie ist keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes — keine Kontierung, keine Buchführung, keine steuerliche Beurteilung. Diese bleiben eurem Steuerberater vorbehalten.", { size: 16, color: MUT }), { after: 80 }),
  p(t("Die Prüftiefe ist nach Einkaufsvolumen gestaffelt; welcher Lieferant wie tief geprüft wurde, steht auf Seite 1. Eine Gewähr für Vollständigkeit wird nicht übernommen. Gegenüber euren Lieferanten treten wir nicht auf — Beanstandungen erklärt allein euer Betrieb.", { size: 16, color: MUT }), { after: 80 }),
  p(t("Überlassene Originalunterlagen werden zurückgegeben, digitale Kopien spätestens acht Wochen nach Übergabe dieses Berichts gelöscht.", { size: 16, color: MUT })),
];

// ------------------------------------------------------------------ Schreiben

const doc = new Document({
  creator: "Prüfstand · Faruk Polat",
  title: MUSTER ? "Musterbericht Eingangsrechnungen" : "Prüfbericht Eingangsrechnungen",
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 },
              margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } },
    },
    footers: { default: new Footer({ children: [new Paragraph({
      children: [t((MUSTER ? "MUSTERBERICHT · erfundene Daten · " : "") +
        "Prüfstand · Faruk Polat · In den Rübgärten 17 · 61476 Kronberg im Taunus · 0152 28487769 · farukpolat@mail.de",
        { size: 15, color: MUSTER ? "A9451B" : MUT })],
      alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: LIN } },
    })] }) },
    children: [...kopf, ...seite2],
  }],
});

const sicherName = (s) => s.split(",")[0].replace(/[^A-Za-zÄÖÜäöüß0-9]+/g, "_").replace(/^_|_$/g, "");
const name = MUSTER ? "Musterbericht_Pruefstand.docx"
                    : `Pruefbericht_${sicherName(cfg.betrieb)}.docx`;

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(path.join(HIER, name), b);
  console.log(`
  ${name}

  Rechnungen geprüft   ${rechnungen}
  Einkaufsvolumen      ${eur0(volumen)}
  Funde                ${funde.length}  (${sicher.length} sicher, ${funde.length - sicher.length} zu klären)
  Summe belegbar       ${eur(summeSicher)}
  Hochrechnung Jahr    ${eur0(jahr)}
`);
});
