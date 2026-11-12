// Build CE 502 reading-summary slides: two slides per paper.
// Usage: node build_readings_deck.js <content.json> <weekNum> <out.pptx> <embedStart> <embedTotal>
// Builds only the paper slides, footed "CE 502 · Week N · Papers to Read" and numbered
// embedStart.. of embedTotal, ready to be inserted into the weekly deck's "Papers to Read"
// section by merge_into_weekly.ps1 (run_week.py does both).
// Adapted from the DS 501 builder; colours, fonts and positions follow the CE 502 decks
// (course_template.md, section 11).
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [, , contentPath, weekNum, outPath, embedStart, embedTotal] = process.argv;
const papers = JSON.parse(fs.readFileSync(contentPath, "utf8"));
const W = parseInt(weekNum, 10);

const K = {
  navy: "14213D", navyCard: "22335A", accent: "B5491A", accentLight: "F2A65A",
  paper: "F7F6F2", card: "FFFFFC", line: "DDD8CC", ink: "22252B", soft: "2F3640",
  muted: "5A6478", chip: "E6E1D6", track: "E4DFD3", band: "EEF1F6",
  onDark: "F7F6F2", onDark2: "C9D3E3", greenBg: "E6F0EC", green: "2E6B5E", greenInk: "1E4D43",
};
const SANS = "IBM Plex Sans", MONO = "JetBrains Mono";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in, same as the weekly decks
pres.author = "CE 502";
pres.title = `CE 502 · Week ${W} · Reading Summaries`;
pres.theme = { headFontFace: SANS, bodyFontFace: SANS };

const SW = 13.333, MX = 0.89, CW = 11.55; // content width as on the decks' papers slides
const total = parseInt(embedTotal, 10);
let n = parseInt(embedStart, 10) - 1;

function tb(slide, text, o) { slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: SANS }, o)); }

function footer(slide) {
  n += 1;
  tb(slide, `CE 502 · Week ${W} · Papers to Read`, { x: MX, y: 6.96, w: 9.3, h: 0.26, fontSize: 12, color: K.muted });
  tb(slide, `${n} / ${total}`, { x: 11.0, y: 6.96, w: 1.44, h: 0.26, fontSize: 12, color: K.muted, align: "right" });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 7.43, w: SW, h: 0.07, fill: { color: K.track }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 7.43, w: SW * n / total, h: 0.07, fill: { color: K.accent }, line: { type: "none" } });
}

function header(slide, eyebrow, title, pill) {
  tb(slide, eyebrow.toUpperCase(), { x: MX, y: 0.70, w: 10.2, h: 0.26, fontFace: MONO, fontSize: 12, color: K.accent, charSpacing: 1 });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 11.39, y: 0.66, w: 1.05, h: 0.32, rectRadius: 0.16, fill: { color: K.chip }, line: { type: "none" } });
  tb(slide, pill, { x: 11.39, y: 0.66, w: 1.05, h: 0.32, fontFace: MONO, fontSize: 12, color: K.navy, align: "center", valign: "middle" });
  const fsz = title.length > 48 ? 23 : title.length > 40 ? 24.5 : 26;
  tb(slide, title, { x: MX, y: 1.04, w: CW, h: 0.5, fontSize: fsz, bold: true, color: K.navy, valign: "middle" });
}

function card(slide, x, y, w, h, dark) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: dark ? K.navy : K.card }, line: dark ? { type: "none" } : { color: K.line, width: 0.75 },
  });
}

function capLabel(slide, text, x, y, w, color) {
  tb(slide, text.toUpperCase(), { x, y, w, h: 0.3, fontFace: MONO, fontSize: 12, color, charSpacing: 1 });
}

let rq = 0, op = 0;
for (const p of papers) {
  const isReq = p.kind === "Required";
  const idx = isReq ? ++rq : ++op;
  const eyebrow = `Week ${W} · ${p.kind} reading ${idx} · ${p.label}`;
  const pill = isReq ? "Required" : "Optional";

  // Slide A: problem, key ideas, key term
  {
    const s = pres.addSlide(); s.background = { color: K.paper };
    header(s, eyebrow, p.short_title, pill);
    tb(s, p.citation, { x: MX, y: 1.62, w: CW, h: 0.5, fontSize: 12, italic: true, color: K.muted, valign: "top" });
    const top = 2.3, h = 3.05;
    card(s, MX, top, 4.6, h, true);
    capLabel(s, "The problem", MX + 0.28, top + 0.25, 4.0, K.accentLight);
    tb(s, p.problem, { x: MX + 0.28, y: top + 0.65, w: 4.05, h: h - 0.85, fontSize: 15.5, color: K.onDark, valign: "top", lineSpacingMultiple: 1.12 });
    const rx = MX + 4.6 + 0.3, rw = CW - 4.6 - 0.3;
    card(s, rx, top, rw, h, false);
    capLabel(s, "Key ideas", rx + 0.28, top + 0.25, 4, K.accent);
    p.key_ideas.forEach((k, i) => {
      const y = top + 0.68 + i * 0.76;
      tb(s, String(i + 1).padStart(2, "0"), { x: rx + 0.28, y, w: 0.55, h: 0.6, fontFace: MONO, fontSize: 16, bold: true, color: K.accent, valign: "top" });
      tb(s, k, { x: rx + 0.9, y, w: rw - 1.15, h: 0.7, fontSize: 15, color: K.ink, valign: "top" });
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.62, w: CW, h: 0.88, rectRadius: 0.1, fill: { color: K.band }, line: { color: K.line, width: 0.75 } });
    tb(s, [
      { text: "Key term: ", options: { color: K.accent, bold: true } },
      { text: p.key_term.term, options: { color: K.navy, bold: true } },
      { text: ` — ${p.key_term.definition}`, options: { color: K.ink } },
    ], { x: MX + 0.3, y: 5.62, w: CW - 0.6, h: 0.88, fontSize: 15, valign: "middle" });
    footer(s);
    s.addNotes(p.notes_slide1);
  }

  // Slide B: takeaways, course link, limitation, note question
  {
    const s = pres.addSlide(); s.background = { color: K.paper };
    header(s, eyebrow, p.slide2_title, pill);
    const top = 1.8, h = 3.6, lw = 6.85;
    card(s, MX, top, lw, h, false);
    capLabel(s, "What to take away", MX + 0.28, top + 0.25, 5, K.accent);
    p.findings.forEach((f, i) => {
      const y = top + 0.72 + i * 0.92;
      s.addShape(pres.shapes.OVAL, { x: MX + 0.28, y: y + 0.02, w: 0.42, h: 0.42, fill: { color: K.chip }, line: { type: "none" } });
      tb(s, String(i + 1), { x: MX + 0.28, y: y + 0.02, w: 0.42, h: 0.42, fontFace: MONO, fontSize: 14, bold: true, color: K.navy, align: "center", valign: "middle" });
      tb(s, f, { x: MX + 0.9, y, w: lw - 1.15, h: 0.82, fontSize: 15, color: K.ink, valign: "top" });
    });
    const rx = MX + lw + 0.3, rw = CW - lw - 0.3;
    card(s, rx, top, rw, h, true);
    capLabel(s, "This week", rx + 0.28, top + 0.25, rw - 0.5, K.accentLight);
    tb(s, p.course_link, { x: rx + 0.28, y: top + 0.62, w: rw - 0.56, h: 1.55, fontSize: 14, color: K.onDark, valign: "top" });
    capLabel(s, "Limitation", rx + 0.28, top + 2.18, rw - 0.5, K.accentLight);
    tb(s, p.limitation, { x: rx + 0.28, y: top + 2.52, w: rw - 0.56, h: 0.98, fontSize: 13, color: K.onDark2, valign: "top" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.62, w: CW, h: 0.88, rectRadius: 0.1, fill: { color: K.greenBg }, line: { type: "none" } });
    s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 5.62, w: 0.09, h: 0.88, fill: { color: K.green }, line: { type: "none" } });
    tb(s, [
      { text: isReq ? "For your half-page note: " : "To think about: ", options: { color: K.greenInk, bold: true } },
      { text: p.note_question, options: { color: K.ink } },
    ], { x: MX + 0.35, y: 5.62, w: CW - 0.65, h: 0.88, fontSize: 15, valign: "middle" });
    footer(s);
    s.addNotes(p.notes_slide2);
  }
}

pres.writeFile({ fileName: outPath }).then(f => console.log("wrote", f));
