# -*- coding: utf-8 -*-
"""Lay the basic blocks out as a flowchart and hang the gate sheets inside.

Second half of build/draw_branching_logic.py, kept apart because it is the
part that could need re-tuning: that one is the manual's semantics, this one
is geometry.

Two passes, because a container's size is whatever its gate sheet came out
as and the existing layout() reports that in its own coordinates only: build
every sheet into a detached <g>, append it, read getBBox(), and only then
work out where the containers go. Measuring is cheaper than predicting, and
it cannot drift from what render() actually drew.

Ranks come free. The manual forbids a backward branch (B0193AX 14.8.1), so
rank[k] = 1 + max(rank of predecessors) settles in a single ascending pass —
every predecessor has a lower index than the block it feeds.

Edge routing follows the rule signal-map.html arrived at the hard way: a wire
may only run through a stretch of canvas that is guaranteed empty. Here that
is the band between two rows and the gutter to the right of every container.
An edge to the very next rank drops into the band above its target; anything
longer goes out sideways into the gutter first, one lane per edge, so it can
never be drawn through a container standing between the two.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "logic-view.html"

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


CFG_JS = r"""
/* =======================================================================
   3b. THE FLOWCHART
   One rank per level of the control-flow DAG, one container per basic
   block, the block's own gate sheet inside it. The containers are what
   carry the program's ORDER; the sheets inside are the logic, drawn by
   exactly the same layout()/renderSheet() a straight-line program uses.
   ======================================================================= */
const SVGNS = 'http://www.w3.org/2000/svg';
const CFG_PAD = 13, CFG_HEAD = 22, CFG_ROWGAP = 66, CFG_COLGAP = 46, CFG_GUTTER = 26;

function renderCFG(cfg){
  world.innerHTML = '';
  const blocks = cfg.blocks;

  /* ---- pass 1: draw each sheet and measure what it came out as ---- */
  const G = blocks.map(blk => {
    const g = document.createElementNS(SVGNS, 'g');
    g.setAttribute('class', 'cfg-sheet');
    g.innerHTML = renderSheet(layout(blk.sheet));
    world.appendChild(g);
    return g;
  });
  const bb = G.map(g => {
    const r = g.getBBox();
    /* an empty block (a bare GTO, say) still needs a body to sit in */
    return { x: r.x, y: r.y, w: Math.max(r.width, 150), h: Math.max(r.height, 26) };
  });

  /* ---- rank: one ascending pass, since every edge runs forward ---- */
  const rank = blocks.map(() => 0);
  blocks.forEach((blk, k) => {
    for (const e of blk.out) rank[e.to] = Math.max(rank[e.to], rank[k] + 1);
  });
  const rows = [];
  rank.forEach((r, k) => { (rows[r] = rows[r] || []).push(k); });

  /* one barycentre pass so a row sits under the blocks that feed it,
     instead of in step order that may cross every edge in the rank */
  const pos = new Map();
  rows.forEach(row => row.forEach((k, i) => pos.set(k, i)));
  const preds = blocks.map(() => []);
  blocks.forEach((blk, k) => { for (const e of blk.out) preds[e.to].push(k); });
  for (let p = 0; p < 3; p++){
    rows.forEach(row => {
      row.sort((a, b) => {
        const ba = preds[a].length ? preds[a].reduce((t, k) => t + pos.get(k), 0) / preds[a].length : pos.get(a);
        const bb2 = preds[b].length ? preds[b].reduce((t, k) => t + pos.get(k), 0) / preds[b].length : pos.get(b);
        return ba - bb2 || a - b;
      });
      row.forEach((k, i) => pos.set(k, i));
    });
  }

  /* ---- place the containers ---- */
  const box = [];
  let y = 0;
  const rowTop = [], rowBot = [];
  rows.forEach((row, r) => {
    let x = 0, tall = 0;
    for (const k of row){
      const w = bb[k].w + CFG_PAD * 2, h = CFG_HEAD + bb[k].h + CFG_PAD;
      box[k] = { x, y, w, h };
      x += w + CFG_COLGAP;
      tall = Math.max(tall, h);
    }
    rowTop[r] = y;
    rowBot[r] = y + tall;
    y = rowBot[r] + CFG_ROWGAP;
  });
  const right = Math.max(...box.map(b => b.x + b.w));

  /* centre every row against the widest one, so the chart reads as a column */
  rows.forEach(row => {
    const last = box[row[row.length - 1]];
    const off = (right - (last.x + last.w)) / 2;
    for (const k of row) box[k].x += off;
  });

  /* ---- pass 2: park each sheet inside its container ---- */
  blocks.forEach((blk, k) => {
    const b = box[k];
    G[k].setAttribute('transform',
      `translate(${b.x + CFG_PAD - bb[k].x},${b.y + CFG_HEAD + CFG_PAD - bb[k].y})`);
  });

  /* ---- the containers themselves, behind the sheets ---- */
  const shells = [];
  blocks.forEach((blk, k) => {
    const b = box[k];
    const cls = 'cfg-node' + (blk.term ? ' cfg-term' : '');
    let g = `<g class="${cls}" data-blk="${k}">`;
    g += `<rect class="cfg-box" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="10"></rect>`;
    g += `<path class="cfg-head" d="M${b.x} ${b.y + 10} a10 10 0 0 1 10 -10 h${b.w - 20} `
       + `a10 10 0 0 1 10 10 v${CFG_HEAD - 10} h${-b.w} z"></path>`;
    g += `<text class="cfg-title" x="${b.x + 10}" y="${b.y + 15}">B${k}</text>`;
    g += `<text class="cfg-sub" x="${b.x + 10 + 22}" y="${b.y + 15}">step ${blk.from}`
       + `${blk.to !== blk.from ? '–' + blk.to : ''}${blk.term ? ' · ' + blk.term : ''}</text>`;
    g += `</g>`;
    shells.push(g);
  });
  const shell = document.createElementNS(SVGNS, 'g');
  shell.innerHTML = shells.join('');
  world.insertBefore(shell, world.firstChild);

  /* ---- the control edges ----
     Anchors: a two-way block leaves at a third and two thirds of its width
     so true and false start apart; everything else leaves from the middle.
     A one-rank hop drops into the empty band above its target. A longer one
     goes out the side into the gutter first — the only stretch of canvas no
     container ever stands in — exactly as signal-map.html routes a column
     skip. */
  const enterRank = new Map(), gutter = new Map();
  const parts = [];
  let lane = 0;
  blocks.forEach((blk, k) => {
    const b = box[k], n = blk.out.length;
    blk.out.forEach((e, i) => {
      const t = box[e.to];
      const sx = n > 1 ? b.x + b.w * (i + 1) / (n + 1) : b.x + b.w / 2;
      const sy = b.y + b.h;
      const tx = t.x + t.w / 2, ty = t.y;
      const r = rank[e.to];
      const rk = (enterRank.get(r) || 0); enterRank.set(r, rk + 1);
      const by = rowTop[r] - 12 - rk * 7;                 // the empty band above the row
      let d;
      if (rank[e.to] === rank[k] + 1 && Math.abs(sx - tx) < 1){
        d = `M${sx} ${sy} V${ty}`;
      } else if (rank[e.to] === rank[k] + 1){
        d = `M${sx} ${sy} V${by} H${tx} V${ty}`;
      } else {
        const gx = right + CFG_GUTTER + (lane++) * 11;
        d = `M${sx} ${sy} V${rowBot[rank[k]] + 14} H${gx} V${by} H${tx} V${ty}`;
      }
      const cls = e.kind === 'true' ? ' t' : '';
      parts.push(`<path class="cfg-wire${cls}" d="${d}"></path>`);
      parts.push(`<path class="cfg-arrow${cls}" d="M${tx} ${ty} l-3.8 -8 h7.6 z"></path>`);
      if (e.kind === 'true' || e.kind === 'false')
        parts.push(`<text class="cfg-lbl${cls}" x="${sx + 5}" y="${sy + 13}">`
                 + `${e.kind === 'true' ? 'ใช่' : 'ไม่'}</text>`);
    });
  });
  const wires = document.createElementNS(SVGNS, 'g');
  wires.innerHTML = parts.join('');
  world.insertBefore(wires, world.firstChild);
}
"""

sub(
    "/* =======================================================================\n"
    "   4. VIEW + PAGE\n",
    CFG_JS.strip() + "\n\n"
    "/* =======================================================================\n"
    "   4. VIEW + PAGE\n",
    "renderCFG()",
)

# ---- show(): pick the straight-line path or the flowchart ---------------
sub(
    "function show(b){\n"
    "  CUR = { dests: b[8] };\n"
    "  $('#q').value = b[0];\n"
    "  $('#results').innerHTML = '';\n"
    "  paintSteps(b);\n"
    "\n"
    "  const c = compile(b);\n"
    "  const nd = $('#nodraw');\n"
    "  if (!c.err && !c.outs.length){\n"
    "    /* a program that never reaches an OUT has nothing to draw a sheet from */\n"
    "    c.err = { op: 'OUT', no: 0, why: 'noout' };\n"
    "  }\n"
    "  if (c.err){\n"
    "    world.innerHTML = '';\n"
    "    nd.classList.remove('hide');\n"
    "    const why = c.err.why === 'op'\n"
    "      ? `คำสั่ง <code>${esc(c.err.op)}</code> ที่ step ${c.err.no} ยังไม่รองรับในผังเกต`\n"
    "      : c.err.why === 'stack'\n"
    "        ? `stack ไม่พอสำหรับ <code>${esc(c.err.op)}</code> ที่ step ${c.err.no}`\n"
    "        : c.err.why === 'noout'\n"
    "          ? `โปรแกรมนี้ไม่มีคำสั่ง <code>OUT</code> จึงไม่มีขาออกให้วาด`\n"
    "          : `โปรแกรมนี้มีคำสั่งกระโดด <code>${esc(c.err.op)}</code> ที่ step ${c.err.no}`;\n"
    "    nd.innerHTML = `<div><b>วาดเป็นผังเกตไม่ได้</b>${why}<br><br>` +\n"
    "      `ลอจิกแบบมีลำดับ (sequential) ไม่ใช่ผังเกตแบบ combinational — ` +\n"
    "      `อ่านจากรายการ step ทางขวาแทน ซึ่งมีคอมเมนต์ของผู้เขียนครบ</div>`;\n"
    "    $('#hint').classList.add('hide');\n"
    "    return;\n"
    "  }\n"
    "  nd.classList.add('hide');\n"
    "  $('#hint').classList.remove('hide');\n"
    "  render(layout(c));\n"
    "  fit();\n"
    "}\n",
    "function show(b){\n"
    "  CUR = { dests: b[8] };\n"
    "  $('#q').value = b[0];\n"
    "  $('#results').innerHTML = '';\n"
    "\n"
    "  const cfg = compileCFG(b);\n"
    "  CUR.cfg = cfg;\n"
    "  paintSteps(b, cfg);\n"
    "  const nd = $('#nodraw'), one = cfg.blocks.length === 1;\n"
    "  const anyOut = cfg.blocks.some(k => k.outs.length);\n"
    "  if (!cfg.err && !anyOut)\n"
    "    cfg.err = { op: 'OUT', no: 0, why: 'noout' };\n"
    "  if (cfg.err){\n"
    "    world.innerHTML = '';\n"
    "    nd.classList.remove('hide');\n"
    "    const why = cfg.err.why === 'noout'\n"
    "      ? `โปรแกรมนี้ไม่มีคำสั่ง <code>OUT</code> จึงไม่มีขาออกให้วาด`\n"
    "      : `คำสั่ง <code>${esc(cfg.err.op)}</code> ที่ step ${cfg.err.no} ยังไม่รองรับในผังเกต`;\n"
    "    nd.innerHTML = `<div><b>วาดเป็นผังไม่ได้</b>${why}<br><br>` +\n"
    "      `อ่านจากรายการ step ทางขวาแทน ซึ่งมีคอมเมนต์ของผู้เขียนครบ</div>`;\n"
    "    $('#hint').classList.add('hide');\n"
    "    return;\n"
    "  }\n"
    "  nd.classList.add('hide');\n"
    "  $('#hint').classList.remove('hide');\n"
    "  /* A program with no branch has exactly one basic block, and it is drawn\n"
    "     the way it always was — no container, no flowchart, same sheet. */\n"
    "  $('#hint').innerHTML = one\n"
    "    ? 'อ่านจากซ้ายไปขวา: ขาเข้า → เกต → ขาออก &nbsp;·&nbsp; ลากเพื่อเลื่อน · ล้อเมาส์เพื่อซูม'\n"
    "    : `${cfg.blocks.length} กล่อง — ในกล่องอ่านซ้ายไปขวา ระหว่างกล่องอ่านบนลงล่าง `\n"
    "      + `&nbsp;·&nbsp; <b style=\"color:var(--mint-deep)\">ใช่</b> = เงื่อนไขเป็นจริง`;\n"
    "  if (one) render(layout(cfg.blocks[0].sheet));\n"
    "  else renderCFG(cfg);\n"
    "  fit();\n"
    "}\n",
    "show(): straight-line sheet or flowchart",
)

# ---- the step listing gets the block bands ------------------------------
sub(
    "function paintSteps(b){\n"
    "  const refs = b[7];\n"
    "  $('#stepMeta').textContent = b[6].length + ' step';\n"
    "  $('#stepsBody').innerHTML = b[6].map(([no, code, cmt]) => {\n",
    "function paintSteps(b, cfg){\n"
    "  const refs = b[7];\n"
    "  /* which basic block each step fell into, so the listing is banded the\n"
    "     same way the diagram is and the two can be read side by side */\n"
    "  const band = new Map();\n"
    "  (cfg ? cfg.blocks : []).forEach(blk => band.set(blk.from, blk));\n"
    "  $('#stepMeta').textContent = b[6].length + ' step'\n"
    "    + (cfg && cfg.blocks.length > 1 ? ' · ' + cfg.blocks.length + ' กล่อง' : '');\n"
    "  $('#stepsBody').innerHTML = b[6].map(([no, code, cmt]) => {\n"
    "    const blk = band.get(no);\n"
    "    const head = (blk && cfg.blocks.length > 1)\n"
    "      ? `<div class=\"sband\">B${blk.id}<i>step ${blk.from}`\n"
    "        + `${blk.to !== blk.from ? '–' + blk.to : ''}`\n"
    "        + `${blk.cond ? ' · ' + esc(blk.op) + ' ' + esc(blk.cond) : ''}`\n"
    "        + `${blk.term ? ' · ' + esc(blk.term) : ''}</i></div>` : '';\n",
    "paintSteps(): band the listing by basic block",
)

sub(
    "    return `<div class=\"srow\">` +\n"
    "      `<div class=\"no\">${no}</div>` +\n",
    "    return head + `<div class=\"srow\">` +\n"
    "      `<div class=\"no\">${no}</div>` +\n",
    "paintSteps(): emit the band header",
)

sub(
    ".srow.dim .code{opacity:.55}\n",
    ".srow.dim .code{opacity:.55}\n"
    ".sband{display:flex; align-items:baseline; gap:8px; margin:9px 0 3px;\n"
    "  padding:3px 15px; background:var(--surface-2); border-top:1px solid var(--border);\n"
    "  border-bottom:1px solid var(--border-soft);\n"
    "  font-size:10.5px; font-weight:800; letter-spacing:.08em; color:var(--accent)}\n"
    ".sband i{font-style:normal; font-weight:400; letter-spacing:0; font-size:11px;\n"
    "  color:var(--text-faint)}\n",
    "CSS: .sband for the step listing",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
