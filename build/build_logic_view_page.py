# -*- coding: utf-8 -*-
"""Assemble logic-view.html from signal-map.html's shell.

The <head> (fonts, design tokens, every shared component style) is lifted
verbatim out of signal-map.html so the six pages cannot drift apart and the
fonts are byte-identical rather than re-encoded. Only the <title> changes and
a page-specific block is appended before </style>. The <body> and the script
are this page's own.

What the page is: ICC's Logic View. 4,232 blocks (CALC / CALCA / LOGIC /
MATH) carry a step program in STEP01..STEP50 -- a stack machine, documented
in B0193AX section 14.5 -- and ICC draws it as a function block diagram. The
reference the user handed over is 12.png, P3973:P3973ILK, and the page is
built to reproduce it.

Two halves, because only 46% of the programs can be drawn:

  * the STEP LISTING is always shown. It carries the engineers' own comments
    (";LEVEL H", ";AUTO STR CMD"), which is the most valuable thing in the
    whole file, and every operand that names an I/O parameter is annotated
    with the reference that parameter actually reads.
  * the GATE DIAGRAM is drawn when the program has no branch instruction.
    GTO / BIZ / BIF / BIT / BIN / BIP / EXIT and the SSx conditional skips
    make a program sequential, and sequential logic is not a combinational
    diagram -- 2,279 blocks say so plainly rather than being drawn wrong.

The one instruction detail that is easy to get wrong, and that 12.png pins
down: `AND 2` is polyadic and pops TWO operands off the stack, while
`AND BI02` is diadic and pops ONE, combining it with the named parameter.
B0193AX lists both under "Diadic or Polyadic"; the operand is what tells them
apart. P3973ILK uses both forms in one program, so getting it wrong shows up
immediately as a gate with the wrong number of legs.

Idempotent: rewrites logic-view.html every run. Re-run whenever the shell in
signal-map.html changes.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
SRC = os.path.join(WEB, "signal-map.html")
OUT = os.path.join(WEB, "logic-view.html")

src = open(SRC, encoding="utf8").read()
m = re.search(r"<head>.*?</head>", src, re.S)
assert m, "cannot find <head> in signal-map.html"
head = m.group(0)
assert head.count("<title>FOXBORO SIGNAL MAP</title>") == 1, "title anchor moved"
head = head.replace("<title>FOXBORO SIGNAL MAP</title>",
                    "<title>FOXBORO LOGIC VIEW</title>")

PAGE_CSS = """
/* ============================================================ LOGIC ==== */
.split{display:flex; gap:16px; align-items:stretch; min-height:0; flex:1}
.diagram{position:relative; flex:1; min-width:0}
.steps{width:430px; flex:none; display:flex; flex-direction:column;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift); overflow:hidden}
.steps.fold{width:56px}
.steps.fold .steps-body,.steps.fold .steps-head b,.steps.fold .steps-head i{display:none}
.steps-head{display:flex; align-items:center; gap:10px; padding:13px 15px;
  border-bottom:1px solid var(--border); background:var(--btn)}
.steps-head b{font-size:14px; font-weight:800}
.steps-head i{font-style:normal; font-size:12px; color:var(--text-dim); margin-left:auto}
.steps-head .fold-btn{border:1px solid var(--border); background:var(--surface);
  color:var(--text); border-radius:9px; width:26px; height:26px; cursor:pointer;
  font-size:13px; line-height:1; padding:0}
.steps-body{overflow:auto; padding:6px 0 12px}
.srow{display:grid; grid-template-columns:34px 1fr; gap:0 10px; padding:4px 15px;
  font-size:13px; align-items:baseline}
.srow:nth-child(odd){background:var(--row-alt, transparent)}
.srow .no{color:var(--text-faint); font-size:11.5px; text-align:right;
  font-variant-numeric:tabular-nums}
.srow .code{font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:12.5px}
.srow .code .op{font-weight:800; color:var(--accent)}
.srow .code .op.br{color:var(--warn-ink, #a2632b)}
.srow .code .arg{color:var(--text)}
.srow .cmt{grid-column:2; color:var(--text-dim); font-size:12px; margin-top:1px}
.srow .ref{grid-column:2; color:var(--text-faint); font-size:11.5px;
  font-family:ui-monospace,"Cascadia Mono",Consolas,monospace}
.srow.dim .code{opacity:.55}

/* the diagram's own boxes -- an ICC logic sheet, in the house palette */
.lg-io{fill:var(--blk-face); stroke:var(--blk-edge); stroke-width:1}
.lg-gate{fill:var(--blk-head); stroke:var(--blk-head-edge); stroke-width:1}
.lg-out .lg-io{fill:var(--blk-head); stroke:var(--blk-head-edge)}
.lg-name{font-size:11px; font-weight:800; fill:var(--text)}
.lg-ref{font-size:9.5px; fill:var(--text-dim)}
.lg-op{font-size:11.5px; font-weight:800; fill:var(--blk-head-ink);
  letter-spacing:.04em}
.lg-pin{font-size:8.5px; font-weight:700; fill:var(--blk-head-ink); opacity:.8}
.lg-t{font-size:10px; font-weight:700; fill:var(--text-dim)}
.lg-wire{fill:none; stroke:var(--wire); stroke-width:1.4}
.lg-wire.hot{stroke:var(--wire-hot); stroke-width:2.4}
.lg-arrow{fill:var(--wire)}
.lg-arrow.hot{fill:var(--wire-hot)}
.lg-inv{fill:var(--canvas); stroke:var(--wire); stroke-width:1.3}
.lg-node{cursor:default}
.lg-node:hover .lg-io,.lg-node:hover .lg-gate{stroke:var(--wire-hot); stroke-width:1.8}

.nodraw{position:absolute; inset:0; display:flex; align-items:center;
  justify-content:center; padding:30px; pointer-events:none}
.nodraw div{max-width:460px; text-align:center; color:var(--text-dim); font-size:14px;
  line-height:1.65}
.nodraw b{display:block; font-size:15.5px; color:var(--text); margin-bottom:8px}
.nodraw code{font-family:ui-monospace,Consolas,monospace; font-size:12.5px;
  background:var(--btn); border:1px solid var(--border); border-radius:6px;
  padding:1px 6px}
.badge{display:inline-block; font-size:11px; font-weight:800; letter-spacing:.06em;
  padding:3px 9px; border-radius:999px; border:1px solid var(--border);
  background:var(--btn); color:var(--text-dim)}
.badge.ok{background:var(--mint); border-color:var(--mint-deep); color:#17352b}
"""

head = head.replace("</style>", PAGE_CSS + "</style>")
assert PAGE_CSS in head, "page CSS not appended"

BODY = r"""
<body>

<div id="boot"><div class="ring"></div><p id="bootMsg">กำลังโหลด logic program…</p></div>

<div class="app hide" id="app">
  <header class="topbar">
    <div>
      <p class="eyebrow">Foxboro I/A Series · CALC / CALCA / LOGIC step program</p>
      <h1>LOGIC VIEW</h1>
    </div>
    <div class="tools">
      <label class="search">
        <input id="q" placeholder="ค้นหา block ที่มี step program… ใช้ * ได้" autocomplete="off">
        <i class="mag">⌕</i>
        <div class="results" id="results"></div>
      </label>
      <button class="btn icon" id="fit" title="พอดีจอ">⤢</button>
      <button class="btn icon" id="themeBtn" title="สลับธีม">◐</button>
    </div>
  </header>

  <nav class="pagenav" aria-label="หน้าในชุดเครื่องมือ">
    <a href="system-manager.html"><b>SYSTEM MANAGER</b><i>ผังอุปกรณ์ &amp; บล็อก</i></a>
    <a href="index.html"><b>TAG SEARCH</b><i>ตาราง tag ทั้งหมด</i></a>
    <a href="signal-map.html"><b>SIGNAL MAP</b><i>ผังการเดินสัญญาณ</i></a>
    <a href="logic-view.html" aria-current="page"><b>LOGIC VIEW</b><i>ผังลอจิกจาก step</i></a>
    <a href="system-monitor.html"><b>FBM (I/O) MODULE MANAGEMENT</b><i>โมดูล &amp; spare point</i></a>
    <a href="modbus.html"><b>MODBUS COMMUNICATION</b><i>register IN/OUT ต่ออุปกรณ์</i></a>
  </nav>

  <div class="split">
    <div class="diagram stage" id="stage">
      <svg id="svg"><g id="world"></g></svg>
      <div class="nodraw hide" id="nodraw"></div>
      <div class="hint" id="hint">อ่านจากซ้ายไปขวา: ขาเข้า → เกต → ขาออก &nbsp;·&nbsp; ลากเพื่อเลื่อน · ล้อเมาส์เพื่อซูม</div>
    </div>
    <aside class="steps" id="stepsPane">
      <div class="steps-head">
        <button class="fold-btn" id="foldBtn" title="ย่อ/ขยาย">›</button>
        <b>STEP PROGRAM</b><i id="stepMeta"></i>
      </div>
      <div class="steps-body" id="stepsBody"></div>
    </aside>
  </div>
</div>

<div class="tip" id="tip"></div>

<script src="logic.js"></script>
<script>
"use strict";
const $ = s => document.querySelector(s);
"""

SCRIPT = r"""
/* =======================================================================
   1. DATA — logic.js only. Everything the page needs was resolved by
   build/export_logic.py, so this file never touches data.js or graph.js.
   block: [name, type, descrp, cp, area, row, steps, refs, dests, branchy]
   steps: [[stepNo, code, comment], ...]
   ======================================================================= */
let BLOCKS = [], byName = new Map();
const esc = s => String(s == null ? '' : s)
  .replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

async function inflate(b64){
  const bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
  for (let i = 0; i < n; i++) u8[i] = bin.charCodeAt(i);
  const st = new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(new TextDecoder().decode(await new Response(st).arrayBuffer()));
}

/* =======================================================================
   2. THE STEP MACHINE
   CALC / CALCA / LOGIC execute a stack machine (B0193AX §14.5). Only what a
   gate diagram needs is modelled; anything else becomes a generic box with
   the arity the manual gives it, which degrades honestly instead of
   guessing at a shape.

   The detail that is easy to get wrong, and that 12.png pins down:
     AND 2      polyadic — pops TWO operands off the stack
     AND BI02   diadic   — pops ONE and combines it with that parameter
     AND        diadic   — pops two
   B0193AX files both under "Diadic or Polyadic"; the operand is what tells
   them apart. P3973ILK uses both in one program.
   ======================================================================= */

/* pops n from the stack, pushes one result */
const POLY = new Set(['AND','OR','NAND','NOR','XOR','NXOR','ADD','MUL','MIN','MAX',
                      'ANDX','ORX','XORX','NORX','NANX','NXOX','MEDN','AVE']);
const DIADIC = new Set(['SUB','DIV','IDIV','IMOD']);
const UNARY  = new Set(['NOT','NOTX','ABS','SQRT','SQR','LOG','LN','EXP','SIN','TAN',
                        'RND','TRC','INC','DEC','CHS']);
/* B0193AX tables 14-5 and 14-9 classify these by "Instruction Type", and the
   column is what decides their stack effect. Getting it wrong is not subtle:
   reading it as a pop where the manual says otherwise underflows the stack
   and the whole sheet refuses to draw. That was 528 programs on the first
   pass, all of it self-inflicted.
     Input Value / Input Status  -> PUSHES a leaf (RBD reads an input's bad
                                    bit onto the stack; it does not consume)
     Output Value                -> pops
     Output Status               -> touches status only, stack untouched
     Unconditional Clear / Set   -> writes a literal to an output, no stack */
const PUSHLEAF = new Set(['IN','INH','INL','INB','INR','INS','LAC','LACI',
                          'RBD','RCL','RCN','RE','RON','ROO','RQE','RQL','TIM']);
const OUTSTAT  = new Set(['CBD','CE','COO','REL','SBD','SE','SEC','SOO']);
const LITERAL  = { SET: '1', SETB: '1', CLR: '0', CLRB: '0' };
/* the operand is a TIME in seconds, never a count (B0193AX table 14-10).
   TIM is NOT one of these: the manual's own wording is that the operands of
   the timing instructions "except for TIM" name a time value, because TIM
   takes none — it READS the time from midnight onto the stack. Reading it as
   a timer that consumes its input underflowed 41 programs outright and
   cascaded into 355 more that then found SUB with an empty stack. */
const TIMER  = new Set(['DON','DOFF','OSP']);
const FLIP   = new Set(['FF','MRS']);          // 2 in, Q out
const BRANCH = new Set(['GTO','GTI','BIZ','BIF','BIN','BIP','BIT','BII','EXIT',
                        'SSF','SSI','SSN','SSP','SST','SSZ']);
const SINK   = new Set(['OUT','SAC','STH','STL','STM','STMI']);

const isNum = t => /^[-+]?\d+(\.\d+)?$/.test(t);

function parseStep(code){
  const p = code.trim().split(/\s+/);
  return { op: (p[0] || '').toUpperCase(), arg: p.slice(1).join(' ') };
}

/* Build the expression DAG. Returns {nodes, outs, error} — error is set when
   the program does something the diagram cannot honestly show. */
function compile(b){
  const steps = b[6], refs = b[7];
  const nodes = [], stack = [], outs = [];
  const push = n => { n.id = nodes.length; nodes.push(n); stack.push(n.id); return n.id; };
  const leaf = (tok, cmt) => {
    const inv = tok.startsWith('~');
    const nm = inv ? tok.slice(1) : tok;
    return push({ kind: isNum(nm) ? 'const' : 'in', label: nm, inv,
                  ref: refs[nm.toUpperCase()] || '', ins: [], cmt: cmt || '' });
  };
  let err = null;

  for (const [no, code, cmt] of steps){
    const { op, arg } = parseStep(code);
    if (!op || op === 'NOP' || op === 'END') continue;
    if (BRANCH.has(op)){ err = { op, no }; break; }
    if (op === 'CST'){ stack.length = 0; continue; }
    if (op === 'DUP'){ if (stack.length) stack.push(stack[stack.length - 1]); continue; }
    if (op === 'POP'){ stack.pop(); continue; }
    if (op === 'SWP'){
      if (stack.length > 1){ const a = stack.pop(), c = stack.pop(); stack.push(a, c); }
      continue;
    }
    if (PUSHLEAF.has(op)){ leaf(arg, cmt); continue; }
    if (OUTSTAT.has(op) || op === 'CLA' || op === 'CLM') continue;   // status only

    if (LITERAL[op] !== undefined){          // SET BO01 / CLR BO01 -- a literal
      const lit = push({ kind: 'const', label: LITERAL[op], inv: false, ref: '',
                         ins: [], cmt: cmt || '' });
      stack.pop();                           // it feeds the output, not the stack
      outs.push({ param: arg, src: lit, cmt: cmt || '', op, no });
      continue;
    }

    if (SINK.has(op)){
      /* OUT COPIES the accumulator to the parameter, it does not consume it.
         B0193AX calls the top of the stack the accumulator and OUT an
         "Output Value" instruction -- a store, not a pop.
         P3973ILK cannot tell the two readings apart, because its `OR 5`
         takes the top five either way and the leftover sits harmlessly
         underneath. 02MG07_AOUT1:TIMER can: it does `SUB / OUT RO03 /
         IN M02 / SUB`, and that second SUB has one operand unless OUT left
         the first one where it was. */
      const src = stack.length ? stack[stack.length - 1] : null;
      outs.push({ param: arg, src, cmt: cmt || '', op, no });
      continue;
    }

    if (TIMER.has(op)){
      const src = stack.pop();
      if (src === undefined){ err = { op, no, why: 'stack' }; break; }
      push({ kind: 'op', op, label: op, ins: [src], t: arg, cmt: cmt || '' });
      continue;
    }

    if (FLIP.has(op)){
      const b2 = stack.pop(), a2 = stack.pop();
      if (a2 === undefined || b2 === undefined){ err = { op, no, why: 'stack' }; break; }
      push({ kind: 'op', op, label: op, ins: [a2, b2], pins: ['S','R'], out: 'Q',
             cmt: cmt || '' });
      continue;
    }

    if (UNARY.has(op)){
      const src = stack.pop();
      if (src === undefined){ err = { op, no, why: 'stack' }; break; }
      push({ kind: 'op', op, label: op, ins: [src], cmt: cmt || '' });
      continue;
    }

    if (POLY.has(op) || DIADIC.has(op)){
      /* How many operands come from the stack is decided by how many are
         WRITTEN, and all four forms are in use:
           SUB RI05 RI06  both named  -> nothing popped, result pushed
           AND 2          a count     -> pops two (polyadic ops only)
           SUB M01        one named   -> pops one, combines it with M01
           AND            bare        -> pops two
         `AND 2` and `SUB 2` look identical and are not: AND is polyadic so
         the 2 is a count, SUB is diadic so the 2 is the number two. */
      const toks = arg ? arg.split(/[\s,]+/).filter(Boolean) : [];
      const named = t => { const id = leaf(t, ''); stack.pop(); return id; };
      let ins;
      if (toks.length >= 2){
        ins = toks.map(named);
      } else if (toks.length === 1 && POLY.has(op) && isNum(toks[0])){
        const n = Math.max(1, parseInt(toks[0], 10) || 2);
        if (stack.length < n){ err = { op, no, why: 'stack' }; break; }
        ins = stack.splice(stack.length - n, n);
      } else if (toks.length === 1){
        const a2 = stack.pop();
        if (a2 === undefined){ err = { op, no, why: 'stack' }; break; }
        ins = [a2, named(toks[0])];
      } else {
        const b2 = stack.pop(), a2 = stack.pop();
        if (a2 === undefined || b2 === undefined){ err = { op, no, why: 'stack' }; break; }
        ins = [a2, b2];
      }
      push({ kind: 'op', op, label: op, ins, cmt: cmt || '' });
      continue;
    }

    err = { op, no, why: 'op' };                  // an instruction not modelled
    break;
  }
  return { nodes, outs, err };
}
"""

LAYOUT = r"""
/* =======================================================================
   3. LAYOUT + RENDER
   Columns are depth from the inputs, so the sheet reads left to right the
   way ICC draws it: field values on the left, the gates that combine them
   in the middle, the outputs on the right.
   ======================================================================= */
const IOW = 218, IOH = 34, GW = 74, GH = 62, COLGAP = 118, ROWGAP = 16;

function layout(c){
  const { nodes, outs } = c;
  const used = new Set();
  const mark = id => {
    if (id == null || used.has(id)) return;
    used.add(id);
    for (const k of nodes[id].ins) mark(k);
  };
  for (const o of outs) mark(o.src);

  const depth = new Map();
  const dep = id => {
    if (depth.has(id)) return depth.get(id);
    const n = nodes[id];
    const d = n.ins.length ? 1 + Math.max(...n.ins.map(dep)) : 0;
    depth.set(id, d);
    return d;
  };
  for (const id of used) dep(id);
  const maxd = used.size ? Math.max(...[...used].map(id => depth.get(id))) : 0;

  /* every OUT sits one column past the deepest thing feeding it */
  const cols = new Map();
  const put = (d, item) => { if (!cols.has(d)) cols.set(d, []); cols.get(d).push(item); };
  for (const id of used) put(depth.get(id), { id });
  outs.forEach((o, k) => put(o.src == null ? maxd + 1 : depth.get(o.src) + 1,
                             { out: k }));

  /* one barycentre pass, seeded by the order the program pushed things --
     which is already close to right, because an engineer writes a program
     top to bottom in the order the sheet reads */
  const keys = [...cols.keys()].sort((a, b) => a - b);
  const pos = new Map();
  for (const d of keys) cols.get(d).forEach((it, i) => pos.set(key(it), i));
  for (let pass = 0; pass < 3; pass++){
    for (const d of keys){
      const list = cols.get(d);
      const bary = new Map();
      for (const it of list){
        const src = it.out != null ? [outs[it.out].src].filter(x => x != null)
                                   : nodes[it.id].ins;
        bary.set(key(it), src.length
          ? src.reduce((s, k2) => s + (pos.get('n' + k2) || 0), 0) / src.length
          : (pos.get(key(it)) || 0));
      }
      list.sort((a, b) => bary.get(key(a)) - bary.get(key(b)));
      list.forEach((it, i) => pos.set(key(it), i));
    }
  }

  const box = new Map();
  let x = 0;
  for (const d of keys){
    const list = cols.get(d);
    let wide = 0;
    for (const it of list) wide = Math.max(wide, boxW(it, nodes));
    let y = 0;
    for (const it of list){
      const w = boxW(it, nodes), h = boxH(it, nodes);
      box.set(key(it), { x: x + (wide - w) / 2, y, w, h, d });
      y += h + ROWGAP;
    }
    x += wide + COLGAP;
  }
  /* centre each column against the tallest one */
  let tall = 0;
  for (const d of keys){
    const l = cols.get(d), last = l[l.length - 1];
    const b = box.get(key(last));
    tall = Math.max(tall, b.y + b.h);
  }
  for (const d of keys){
    const l = cols.get(d), last = l[l.length - 1];
    const b = box.get(key(last));
    const off = (tall - (b.y + b.h)) / 2;
    for (const it of l) box.get(key(it)).y += off;
  }
  return { cols, keys, box, used, tall, nodes, outs };
}
const key = it => it.out != null ? 'o' + it.out : 'n' + it.id;
const boxW = (it, nodes) =>
  it.out != null ? IOW : (nodes[it.id].kind === 'op' ? GW : IOW);
const boxH = (it, nodes) =>
  it.out != null ? IOH : (nodes[it.id].kind === 'op' ? GH : IOH);

function render(L){
  const { nodes, outs, box } = L;
  const parts = [], wires = [];
  const anchorOut = k => { const b = box.get(k); return [b.x + b.w, b.y + b.h / 2]; };

  /* wires first so the boxes sit on top */
  let wi = 0;
  const legY = (b, i, n) => b.y + b.h * (i + 1) / (n + 1);
  for (const id of L.used){
    const n = nodes[id], b = box.get('n' + id);
    n.ins.forEach((src, i) => {
      const [sx, sy] = anchorOut('n' + src);
      const dy = legY(b, i, n.ins.length), dx = b.x;
      wires.push({ i: wi++, sx, sy, dx, dy });
    });
  }
  outs.forEach((o, k) => {
    if (o.src == null) return;
    const [sx, sy] = anchorOut('n' + o.src);
    const b = box.get('o' + k);
    wires.push({ i: wi++, sx, sy, dx: b.x, dy: b.y + b.h / 2 });
  });
  for (const w of wires){
    const mx = w.dx - 26;
    const d = `M${w.sx} ${w.sy} H${Math.max(mx, w.sx + 10)} V${w.dy} H${w.dx}`;
    parts.push(`<path class="lg-wire" d="${d}"></path>`);
    parts.push(`<path class="lg-arrow" d="M${w.dx} ${w.dy} l-7 -3.6 v7.2 z"></path>`);
  }

  /* input / constant boxes */
  for (const id of L.used){
    const n = nodes[id], b = box.get('n' + id);
    let g = `<g class="lg-node" transform="translate(${b.x},${b.y})">`;
    if (n.kind === 'op'){
      g += `<rect class="lg-gate" x="0" y="0" width="${b.w}" height="${b.h}" rx="3"></rect>`;
      const pins = n.pins || [];
      pins.forEach((p, i) => {
        g += `<text class="lg-pin" x="5" y="${b.h * (i + 1) / (pins.length + 1) + 3}">${esc(p)}</text>`;
      });
      if (n.out) g += `<text class="lg-pin" x="${b.w - 5}" y="${b.h / 2 + 3}" text-anchor="end">${esc(n.out)}</text>`;
      g += `<text class="lg-op" x="${b.w / 2}" y="${b.h / 2 + 4}" text-anchor="middle">${esc(n.label)}</text>`;
      if (n.t) g += `<text class="lg-t" x="${b.w / 2}" y="${b.h + 13}" text-anchor="middle">T#${esc(n.t)}s</text>`;
    } else {
      g += `<rect class="lg-io" x="0" y="0" width="${b.w}" height="${b.h}" rx="3"></rect>`;
      g += `<text class="lg-name" x="${b.w / 2}" y="${n.ref ? 14 : 21}" text-anchor="middle">${esc(n.label)}</text>`;
      if (n.ref)
        g += `<text class="lg-ref" x="${b.w / 2}" y="26" text-anchor="middle">(${esc(clip(n.ref, 34))})</text>`;
      if (n.inv)
        g += `<circle class="lg-inv" cx="${b.w + 5}" cy="${b.h / 2}" r="4.5"></circle>`;
    }
    g += `</g>`;
    parts.push(g);
  }

  /* output boxes */
  outs.forEach((o, k) => {
    const b = box.get('o' + k);
    const dst = (CUR.dests || []).filter(([p]) => p === o.param).map(([, t]) => t);
    let g = `<g class="lg-node lg-out" transform="translate(${b.x},${b.y})">`;
    g += `<rect class="lg-io" x="0" y="0" width="${b.w}" height="${b.h}" rx="3"></rect>`;
    g += `<text class="lg-name" x="${b.w / 2}" y="${dst.length ? 14 : 21}" text-anchor="middle">${esc(o.param)}</text>`;
    if (dst.length)
      g += `<text class="lg-ref" x="${b.w / 2}" y="26" text-anchor="middle">(${esc(clip(dst.join(', '), 34))})</text>`;
    g += `</g>`;
    parts.push(g);
  });

  world.innerHTML = parts.join('');
}
const clip = (s, n) => String(s).length > n ? String(s).slice(0, n - 1) + '…' : String(s);
"""

DRIVER = r"""
/* =======================================================================
   4. VIEW + PAGE
   ======================================================================= */
const svg = $('#svg'), world = $('#world'), tip = $('#tip');
let view = { x: 0, y: 0, k: 1 }, CUR = null;

function apply(){ world.setAttribute('transform', `translate(${view.x},${view.y}) scale(${view.k})`); }
function fit(){
  const bb = world.getBBox(), r = svg.getBoundingClientRect();
  if (!bb.width || !bb.height) return;
  const k = Math.min(r.width / (bb.width + 90), r.height / (bb.height + 90), 1.4);
  view.k = k;
  view.x = (r.width - bb.width * k) / 2 - bb.x * k;
  view.y = (r.height - bb.height * k) / 2 - bb.y * k;
  apply();
}
let drag = null;
svg.addEventListener('pointerdown', e => {
  drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y };
  svg.classList.add('drag'); svg.setPointerCapture(e.pointerId);
});
svg.addEventListener('pointermove', e => {
  if (!drag) return;
  view.x = drag.vx + (e.clientX - drag.x); view.y = drag.vy + (e.clientY - drag.y); apply();
});
svg.addEventListener('pointerup', () => { drag = null; svg.classList.remove('drag'); });
svg.addEventListener('pointercancel', () => { drag = null; svg.classList.remove('drag'); });
svg.addEventListener('wheel', e => {
  e.preventDefault();
  const r = svg.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
  const f = Math.exp(-e.deltaY * 0.0016), k = Math.min(Math.max(view.k * f, 0.1), 4);
  view.x = mx - (mx - view.x) * (k / view.k);
  view.y = my - (my - view.y) * (k / view.k);
  view.k = k; apply();
}, { passive: false });
$('#fit').addEventListener('click', fit);

/* ---- the step listing, always shown ---- */
const OPCLASS = op => BRANCH.has(op) ? 'op br' : 'op';
function paintSteps(b){
  const refs = b[7];
  $('#stepMeta').textContent = b[6].length + ' step';
  $('#stepsBody').innerHTML = b[6].map(([no, code, cmt]) => {
    const { op, arg } = parseStep(code);
    /* annotate every operand that names an I/O parameter this block reads */
    const seen = [];
    for (const tok of (arg.match(/~?[A-Za-z]+\d+/g) || [])){
      const nm = tok.replace(/^~/, '').toUpperCase();
      if (refs[nm]) seen.push(nm + ' = ' + refs[nm]);
    }
    return `<div class="srow">` +
      `<div class="no">${no}</div>` +
      `<div class="code"><span class="${OPCLASS(op)}">${esc(op)}</span>` +
        (arg ? ` <span class="arg">${esc(arg)}</span>` : '') + `</div>` +
      (cmt ? `<div class="cmt">${esc(cmt)}</div>` : '') +
      (seen.length ? `<div class="ref">${esc(seen.join('  ·  '))}</div>` : '') +
      `</div>`;
  }).join('');
}

$('#foldBtn').addEventListener('click', () => {
  const p = $('#stepsPane');
  p.classList.toggle('fold');
  $('#foldBtn').textContent = p.classList.contains('fold') ? '‹' : '›';
  requestAnimationFrame(fit);
});

/* ---- show a block ---- */
function show(b){
  CUR = { dests: b[8] };
  $('#q').value = b[0];
  $('#results').innerHTML = '';
  paintSteps(b);

  const c = compile(b);
  const nd = $('#nodraw');
  if (!c.err && !c.outs.length){
    /* a program that never reaches an OUT has nothing to draw a sheet from */
    c.err = { op: 'OUT', no: 0, why: 'noout' };
  }
  if (c.err){
    world.innerHTML = '';
    nd.classList.remove('hide');
    const why = c.err.why === 'op'
      ? `คำสั่ง <code>${esc(c.err.op)}</code> ที่ step ${c.err.no} ยังไม่รองรับในผังเกต`
      : c.err.why === 'stack'
        ? `stack ไม่พอสำหรับ <code>${esc(c.err.op)}</code> ที่ step ${c.err.no}`
        : c.err.why === 'noout'
          ? `โปรแกรมนี้ไม่มีคำสั่ง <code>OUT</code> จึงไม่มีขาออกให้วาด`
          : `โปรแกรมนี้มีคำสั่งกระโดด <code>${esc(c.err.op)}</code> ที่ step ${c.err.no}`;
    nd.innerHTML = `<div><b>วาดเป็นผังเกตไม่ได้</b>${why}<br><br>` +
      `ลอจิกแบบมีลำดับ (sequential) ไม่ใช่ผังเกตแบบ combinational — ` +
      `อ่านจากรายการ step ทางขวาแทน ซึ่งมีคอมเมนต์ของผู้เขียนครบ</div>`;
    $('#hint').classList.add('hide');
    return;
  }
  nd.classList.add('hide');
  $('#hint').classList.remove('hide');
  render(layout(c));
  fit();
}

/* ---- search ---- */
let hits = [], selK = -1;
function search(){
  const raw = $('#q').value.trim(), hit = foxMatch(raw);
  if (raw.length < 2 || !hit){ $('#results').innerHTML = ''; hits = []; return; }
  hits = [];
  for (let i = 0; i < BLOCKS.length && hits.length < 60; i++)
    if (hit(BLOCKS[i][0])) hits.push(i);
  if (!hits.length)
    for (let i = 0; i < BLOCKS.length && hits.length < 60; i++)
      if (hit(BLOCKS[i][2] || '')) hits.push(i);
  selK = -1;
  $('#results').innerHTML = hits.map((i, k) => {
    const b = BLOCKS[i];
    return `<div class="rrow" data-i="${i}" data-k="${k}"><b>${esc(b[0])}</b>` +
      `<span class="ty">${esc(b[1])}</span><span class="ds">${esc(b[2] || '')}</span></div>`;
  }).join('');
}
$('#q').addEventListener('input', search);
$('#results').addEventListener('click', e => {
  const r = e.target.closest('.rrow'); if (r) show(BLOCKS[+r.dataset.i]);
});
$('#q').addEventListener('keydown', e => {
  if (!hits.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp'){
    e.preventDefault();
    selK = (selK + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length;
    $('#results').querySelectorAll('.rrow').forEach((el, k) => el.classList.toggle('on', k === selK));
  } else if (e.key === 'Enter'){
    e.preventDefault(); show(BLOCKS[hits[selK < 0 ? 0 : selK]]);
  }
});

$('#themeBtn').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', cur);
  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
});
try { const t = localStorage.getItem('fox-theme'); if (t) document.documentElement.setAttribute('data-theme', t); } catch (e) {}
addEventListener('resize', () => { if (CUR) fit(); });

/* =======================================================================
   5. BOOT
   ======================================================================= */
(async function boot(){
  try {
    if (typeof window.FOX_LOGIC_B64 !== 'string') throw new Error('ไม่พบไฟล์ logic.js');
    if (typeof DecompressionStream === 'undefined')
      throw new Error('เบราว์เซอร์นี้ไม่รองรับ DecompressionStream — ใช้ Chrome/Edge รุ่นใหม่');
    const g = await inflate(window.FOX_LOGIC_B64);
    BLOCKS = g.blocks;
    for (let i = 0; i < BLOCKS.length; i++)
      if (!byName.has(BLOCKS[i][0])) byName.set(BLOCKS[i][0], i);

    $('#boot').classList.add('hide');
    $('#app').classList.remove('hide');

    /* ?tag=COMPOUND:BLOCK — how the other pages link straight into a program.
       A qualified name must match exactly: the plant reuses block names across
       CPs, and opening a different unit's interlock is worse than opening
       none. Only a bare name, which cannot be ambiguous by intent, falls back
       to a short lookup. */
    const want = new URLSearchParams(location.search).get('tag');
    let i = want ? byName.get(want) : undefined;
    if (i === undefined && want && want.indexOf(':') === -1){
      const k = BLOCKS.findIndex(b => b[0].split(':').pop() === want);
      if (k >= 0) i = k;
    }
    if (i !== undefined){ show(BLOCKS[i]); return; }
    if (want){
      $('#nodraw').classList.remove('hide');
      $('#nodraw').innerHTML = `<div><b>${esc(want)}</b>` +
        `ไม่มี step program — Logic View มีเฉพาะบล็อก CALC / CALCA / LOGIC / MATH ` +
        `ที่เขียน STEP01–STEP50 ไว้ (${BLOCKS.length.toLocaleString()} บล็อกในฐานข้อมูล)</div>`;
      return;
    }
    $('#nodraw').classList.remove('hide');
    $('#nodraw').innerHTML = `<div><b>LOGIC VIEW</b>` +
      `ค้นหาบล็อกด้านบนเพื่อดูผังลอจิก — มี ${BLOCKS.length.toLocaleString()} บล็อก ` +
      `ที่มี step program (CALC / CALCA / LOGIC / MATH)<br><br>` +
      `ลองพิมพ์ <code>*ILK</code> เพื่อดูบล็อก interlock ทั้งหมด</div>`;
  } catch (e){
    $('#bootMsg').textContent = e.message;
    $('#boot').querySelector('.ring').style.display = 'none';
  }
})();
</script>
</body>
</html>
"""

page = "<!doctype html>\n<html lang=\"th\">\n" + head + BODY + SCRIPT + LAYOUT + DRIVER

# the wildcard matcher, lifted verbatim from signal-map.html so the six pages
# cannot drift apart on what a query means
m = re.search(r"/\* ---- wildcard search -.*?\nfunction foxMatch\(q\)\{.*?\n\}\n", src, re.S)
assert m, "foxMatch not found in signal-map.html -- run add_wildcard_search.py first"
page = page.replace("const $ = s => document.querySelector(s);\n",
                    "const $ = s => document.querySelector(s);\n" + m.group(0), 1)
assert "function foxMatch(q){" in page, "foxMatch not injected"

open(OUT, "w", encoding="utf8", newline="").write(page)
print("logic-view.html written: %d chars" % len(page))
