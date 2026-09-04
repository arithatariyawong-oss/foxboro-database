# -*- coding: utf-8 -*-
"""Build sequence-view.html -- ICC's block detail for a sequence block.

03 WEB/13.png is the thing being reproduced: Block Properties beside Input
References beside Output References, for an IND block. Everything in those
three panes comes out of sequence.js (see build/export_sequence.py); the
wiring in the two reference panes exists nowhere in the parameter database,
only in the HLBL source, which is why this page had to be built at all.

Below the three panes sits the source itself, line-numbered, with every
reference on it turned into a link. That is the half ICC does not show on the
same screen, and it is the half that answers "why" -- 13.png tells you
39ACP301 writes 39ACP302.ACTIVE, line 119 of 39ACP301.s tells you it does so
right after reading the batch number.

Popup-only, the same as logic-view.html: reached from signal-map.html's block
menu (build/add_sequence_popup.py), never advertised in the page nav. The
whole stylesheet is lifted verbatim from logic-view.html so the two popups
cannot drift apart, and this page's own rules are appended after it -- which
also keeps that file's closing `.topbar,.pagenav{display:none}` last enough
in the cascade to still win.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
SRC = os.path.join(WEB, "logic-view.html")
OUT = os.path.join(WEB, "sequence-view.html")

base = io.open(SRC, encoding="utf8").read()
m = re.search(r"<style>\n(.*?)\n</style>", base, re.S)
if not m:
    sys.exit("ABORT: no <style> block in logic-view.html")
SHELL_CSS = m.group(1)
if "@font-face" not in SHELL_CSS or "--mint-deep" not in SHELL_CSS:
    sys.exit("ABORT: logic-view.html's stylesheet does not look like the house shell")

m = re.search(r"(/\* ---- wildcard search.*?\n\}\n)", base, re.S)
if not m:
    sys.exit("ABORT: foxMatch() not found in logic-view.html")
FOXMATCH = m.group(1)

CSS = r"""
/* =========================================================== SEQUENCE ==== */
/* The screen is 13.png: three panes in a row, each a two-column table with a
   header strip, and the property list on the left. Under them, the thing ICC
   has no room for -- the source those references were read out of. */
.seqbar{
  display:flex; align-items:center; gap:14px; flex-wrap:wrap; flex:none;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift-sm), var(--inset-hi);
  padding:11px 16px;
}
.seqbar .nm{font-size:17px; font-weight:800; letter-spacing:-.01em}
.seqbar .ty{font-size:10.5px; font-weight:800; letter-spacing:.08em; color:var(--accent);
  background:var(--surface-2); border:1px solid var(--border-soft);
  border-radius:var(--r-pill); padding:2px 9px; white-space:nowrap}
.seqbar .ds{font-size:13px; color:var(--text-dim); min-width:0;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.seqbar .meta{font-size:11.5px; color:var(--text-faint); white-space:nowrap}
.seqbar .sp{margin-left:auto}
.seqbar .search{min-width:280px}

.seqwrap{display:flex; flex-direction:column; gap:0; flex:1; min-height:0}
/* Both halves are flex:1 so they start out sharing the height; without a
   basis of its own the pane row takes its height from 122 property rows and
   leaves the source with nothing. The gutter overwrites this with a pixel
   basis as soon as anyone drags it. */
.panes{display:flex; gap:14px; flex:1 1 0; min-height:120px; align-items:stretch}
.pane{
  flex:1 1 0; min-width:0; display:flex; flex-direction:column;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift-sm); overflow:hidden;
}
.pane.props-pane{flex:1.15 1 0}
.pane-head{
  display:flex; align-items:baseline; gap:9px; flex:none;
  padding:10px 14px; background:var(--btn); border-bottom:1px solid var(--border);
}
.pane-head b{font-size:13.5px; font-weight:800}
.pane-head i{font-style:normal; font-size:11.5px; color:var(--text-dim)}
.pane-head .n{margin-left:auto; font-size:11px; font-weight:800; color:var(--text-faint)}
.pane-filter{flex:none; padding:8px 12px 4px}
.pane-filter input{
  width:100%; border:1px solid var(--border); background:var(--surface-2);
  border-radius:var(--r-pill); padding:7px 13px; font-size:12.5px;
  box-shadow:var(--press); outline:none;
}
.pane-body{flex:1; overflow:auto; min-height:0}

/* the two-column grid every pane uses; the column split differs per pane */
.trow{display:grid; gap:10px; padding:5px 14px; align-items:baseline;
  border-bottom:1px solid var(--border-soft)}
.trow:nth-child(even){background:color-mix(in srgb, var(--surface-2) 55%, transparent)}
.trow.th{
  position:sticky; top:0; z-index:2; background:var(--surface-3);
  border-bottom:1px solid var(--border); font-size:10.5px; font-weight:800;
  letter-spacing:.09em; text-transform:uppercase; color:var(--accent); padding:8px 14px;
}
.props-pane .trow{grid-template-columns:132px minmax(0,1fr)}
.ins-pane   .trow{grid-template-columns:minmax(0,1fr) 92px}
.outs-pane  .trow{grid-template-columns:92px minmax(0,1fr)}
.trow .k{font-size:12px; font-weight:700; word-break:break-word}
.trow .k em{display:block; font-style:normal; font-weight:400; font-size:10.5px;
  color:var(--text-faint); line-height:1.35}
.trow .v{font-size:12.5px; word-break:break-word}
.trow .v.empty{color:var(--text-faint)}
.trow .p{font-size:12px; font-weight:700; color:var(--accent)}

/* a name you can follow; SEQ is this block's own program, not a link */
.lnk{color:var(--wire-hot); cursor:pointer; text-decoration:underline;
  text-decoration-style:dotted; text-underline-offset:3px}
.lnk:hover{text-decoration-style:solid}
.seqtag{font-size:9.5px; font-weight:800; letter-spacing:.07em; color:var(--mint-deep);
  border:1px solid var(--mint-deep); border-radius:999px; padding:0 5px; margin-left:6px;
  vertical-align:1px}
.reftag{font-size:9.5px; font-weight:800; letter-spacing:.07em; color:var(--text-faint);
  border:1px solid var(--border); border-radius:999px; padding:0 5px; margin-left:6px;
  vertical-align:1px}
.pane-empty{padding:20px 16px; font-size:12.5px; color:var(--text-faint); text-align:center}

/* ---- the drag handle between the panes and the source ---- */
.gutter{flex:none; height:14px; cursor:row-resize; display:flex;
  align-items:center; justify-content:center; touch-action:none}
.gutter::before{content:""; width:78px; height:4px; border-radius:99px;
  background:var(--border); transition:background .14s ease}
.gutter:hover::before{background:var(--mint-ring)}

/* ---- the source ---- */
.srcpane{flex:1 1 0; min-height:64px; display:flex; flex-direction:column;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift-sm); overflow:hidden}
.srcpane.fold{flex:0 0 auto; min-height:0}
.srcpane.fold .pane-body,.srcpane.fold .pane-filter{display:none}
.src-body{flex:1; overflow:auto; min-height:0; padding:8px 0 16px;
  font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:12.5px;
  line-height:1.55; tab-size:4}
.lrow{display:grid; grid-template-columns:52px minmax(0,1fr); gap:0 12px}
.lrow:hover{background:color-mix(in srgb, var(--mint) 16%, transparent)}
.lrow .ln{text-align:right; color:var(--text-faint); font-size:11px; user-select:none;
  font-variant-numeric:tabular-nums; padding-right:2px}
.lrow .lc{white-space:pre-wrap; word-break:break-word; padding-right:16px}
.lrow.marked{background:color-mix(in srgb, var(--mint) 22%, transparent)}
.hl-cmt{color:var(--text-faint); font-style:italic}
.hl-str{color:var(--mint-deep)}
.hl-kw{color:var(--accent); font-weight:800}
.hl-num{color:var(--amber-ink)}
.hl-ref{color:var(--wire-hot); cursor:pointer; text-decoration:underline;
  text-decoration-style:dotted; text-underline-offset:3px}
.hl-ref.w{color:var(--mint-deep)}
.hl-ref.dead{color:var(--text-dim); cursor:help; text-decoration-style:wavy}
.lnote{grid-column:2; font-family:var(--font-ui); font-size:11.5px;
  color:var(--text-faint); padding:0 16px 3px 0}
.lnote b{font-weight:800; color:var(--text-dim)}
.srclegend{display:flex; gap:14px; flex-wrap:wrap; font-size:11.5px; color:var(--text-dim)}
.srclegend s{text-decoration:none; font-weight:800}
.srclegend s.w{color:var(--mint-deep)}
.srclegend s.r{color:var(--wire-hot)}
"""

BODY = r"""
<div id="boot"><div class="ring"></div><p id="bootMsg">กำลังโหลด sequence source…</p></div>

<div class="app hide" id="app">
  <div class="seqbar">
    <span class="nm" id="bName">—</span>
    <span class="ty" id="bType">IND</span>
    <span class="ds" id="bDesc"></span>
    <span class="meta" id="bMeta"></span>
    <span class="sp"></span>
    <label class="search">
      <input id="q" placeholder="ค้นหา sequence block… ใช้ * ได้" autocomplete="off">
      <i class="mag">⌕</i>
      <div class="results" id="results"></div>
    </label>
    <button class="btn icon" id="themeBtn" title="สลับธีม">◐</button>
  </div>

  <div class="seqwrap" id="wrap">
    <div class="panes" id="panes">
      <section class="pane props-pane">
        <div class="pane-head"><b>Block Properties</b><i>ค่าในบล็อก</i>
          <span class="n" id="nProps"></span></div>
        <div class="pane-filter">
          <input id="fProps" placeholder="กรอง parameter…" autocomplete="off">
        </div>
        <div class="pane-body" id="propsBody"></div>
      </section>

      <section class="pane ins-pane">
        <div class="pane-head"><b>Input References</b><i>อะไรเข้ามาหาบล็อกนี้</i>
          <span class="n" id="nIns"></span></div>
        <div class="pane-body" id="insBody"></div>
      </section>

      <section class="pane outs-pane">
        <div class="pane-head"><b>Output References</b><i>บล็อกนี้ไปถึงอะไร</i>
          <span class="n" id="nOuts"></span></div>
        <div class="pane-body" id="outsBody"></div>
      </section>
    </div>

    <div class="gutter" id="gutter" title="ลากเพื่อปรับส่วนสูง"></div>

    <section class="srcpane" id="srcPane">
      <div class="pane-head">
        <button class="fold-btn" id="foldBtn" title="ย่อ/ขยาย"
          style="border:1px solid var(--border); background:var(--surface); color:var(--text);
                 border-radius:9px; width:26px; height:26px; cursor:pointer; font-size:13px;
                 line-height:1; padding:0">▾</button>
        <b>Sequence Source</b><i id="srcMeta"></i>
        <span class="n"><span class="srclegend">
          <s class="w">เขียนออก</s> <s class="r">อ่านเข้า</s>
        </span></span>
      </div>
      <div class="pane-filter">
        <input id="fSrc" placeholder="ค้นในซอร์ส… (Enter = บรรทัดถัดไป)" autocomplete="off">
      </div>
      <div class="pane-body src-body" id="srcBody"></div>
    </section>
  </div>
</div>
"""

JS = r"""
"use strict";
const $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s)
  .replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

__FOXMATCH__

async function inflate(b64){
  const bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
  for (let i = 0; i < n; i++) u8[i] = bin.charCodeAt(i);
  const st = new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(new TextDecoder().decode(await new Response(st).arrayBuffer()));
}

/* =======================================================================
   1. DATA — sequence.js only.
   block: [name, cp, descrp, props, srcIdx, ins, outs, labels, refs]
     props [[param, value], ...]        in the SaveAll record's own order
     ins   [[srcName, srcParam, myParam, origin], ...]
     outs  [[myParam, dstName, dstParam, origin], ...]
     refs  [[line, kind, literal, resolvedName, param], ...]  kind 0 read,
           1 write, 2 declared by a #define and used further down
   src:   [filename, text, sections, includes, defines]
   origin 0 = read out of the HLBL source, 1 = an ordinary parameter reference
   ======================================================================= */
let BLOCKS = [], SRCS = [], byName = new Map(), CUR = null;

/* A block's own program is not a place you can navigate to — it is the page
   you are already on — so SEQ is drawn as a badge and everything else as a
   link. */
const isSeq = p => p === 'SEQ';

/* Off-page: anything that is not a sequence block has no view here, so it
   opens in the signal map instead. A new tab and never the parent frame:
   this page is usually an iframe inside signal-map.html, and replacing the
   parent would throw away the map the user was reading. */
function openElsewhere(name){
  window.open('signal-map.html?tag=' + encodeURIComponent(name), '_blank', 'noopener');
}
function go(name){
  const i = byName.get(name);
  if (i !== undefined) show(BLOCKS[i]);
  else openElsewhere(name);
}

/* =======================================================================
   2. THE THREE PANES
   ======================================================================= */
const REFVAL = /^[A-Za-z0-9_]{1,32}:[A-Za-z0-9_]{1,32}\.[A-Za-z0-9_]{1,16}(\.[A-Za-z0-9_]{1,6})?$/;

function paintProps(b, filter){
  const hit = foxMatch(filter);
  const [comp, blk] = [b[0].split(':')[0], b[0].split(':').slice(1).join(':')];
  /* CP / COMPOUND / BLOCK are not fields of the record — ICC synthesises them
     at the top of the pane (13.png), and so does this. */
  const rows = [['CP', b[1]], ['COMPOUND', comp], ['BLOCK', blk]].concat(b[3]);
  const keep = rows.filter(([k, v]) => !hit || hit(k) || hit(v));
  $('#nProps').textContent = hit ? keep.length + ' / ' + rows.length : rows.length;
  $('#propsBody').innerHTML =
    '<div class="trow th"><div>Parameter</div><div>Value</div></div>' +
    (keep.length ? keep.map(([k, v]) => {
      const lab = b[7][k];
      const ref = REFVAL.test(v);
      return '<div class="trow">' +
        '<div class="k">' + esc(k) + (lab ? '<em>' + esc(lab) + '</em>' : '') + '</div>' +
        '<div class="v' + (v === '' ? ' empty' : '') + '">' +
          (ref ? '<span class="lnk" data-go="' + esc(v.split('.')[0] + ':' + v.split(':')[1].split('.')[0]) + '">' + esc(v) + '</span>'
               : (v === '' ? '—' : esc(v))) +
        '</div></div>';
    }).join('') : '<div class="pane-empty">ไม่มี parameter ที่ตรงกับคำค้น</div>');
}

/* The two panes are the same relation read from either end, and a neighbour
   can legitimately appear in BOTH: a main sequence writes 39ACP301.ACTIVE to
   start it and then reads the same bit back in a WAIT UNTIL to know it has
   finished. 13.png shows exactly that, three times over. */
function nameCell(full, param, origin){
  const tag = origin ? '' : (isSeq(param) ? '<span class="seqtag">SEQ</span>' : '');
  const txt = esc(full) + '.' + esc(param);
  return '<span class="lnk" data-go="' + esc(full) + '">' + txt + '</span>' + tag;
}

function paintIns(b){
  $('#nIns').textContent = b[5].length;
  $('#insBody').innerHTML =
    '<div class="trow th"><div>Input References</div><div>Parameter</div></div>' +
    (b[5].length ? b[5].map(r =>
      '<div class="trow"><div class="v">' + nameCell(r[0], r[1], r[3]) + '</div>' +
      '<div class="p">' + esc(r[2]) + '</div></div>').join('')
      : '<div class="pane-empty">ไม่มีอะไรเข้ามาหาบล็อกนี้</div>');
}

function paintOuts(b){
  $('#nOuts').textContent = b[6].length;
  $('#outsBody').innerHTML =
    '<div class="trow th"><div>Parameter</div><div>Output References</div></div>' +
    (b[6].length ? b[6].map(r =>
      '<div class="trow"><div class="p">' + esc(r[0]) + '</div>' +
      '<div class="v">' + nameCell(r[1], r[2], r[3]) + '</div></div>').join('')
      : '<div class="pane-empty">บล็อกนี้ไม่ได้เขียนหรืออ่านบล็อกอื่น</div>');
}

/* =======================================================================
   3. THE SOURCE
   The same lexer build/export_sequence.py runs, for the same reason: HLBL
   comments are { ... } and do NOT nest, so the unbalanced open brace in
   39ACP301.s (a subroutine someone commented out and left that way) has to
   end at the next }, not swallow the rest of the file. Strings are "..."
   with a doubled quote standing for a literal one — the character table in
   39ACP*.s tests for a quote mark by writing four of them in a row, which a
   naive scanner reads as an empty string followed by an unterminated one.
   ======================================================================= */
const KW = new Set([
  'INDEPENDENT_SEQUENCE','SEQUENCE','ENDSEQUENCE','CONSTANTS','VARIABLES','USER_LABELS',
  'STATEMENTS','SUBROUTINE','ENDSUBROUTINE','BLOCK_EXCEPTION','ENDEXCEPTION',
  'IF','THEN','ELSE','ELSEIF','ENDIF','FOR','TO','DOWNTO','DO','ENDFOR','WHILE','ENDWHILE',
  'REPEAT','UNTIL','LOOP','ENDLOOP','CASE','ENDCASE','WAIT','CALL','EXIT','RETURN',
  'AND','OR','NOT','XOR','TRUE','FALSE','IN','OUT','INOUT','SET','CLEAR','ENABLE','DISABLE',
  'MOD','DIV','STRING','ROUND','TRUNC','ABS','SQRT','LN','EXP','SIN','COS','TAN','MIN','MAX',
  'B','I','R','S','S6','S12','PRINT','SEND','SIGNAL','RESUME','SUSPEND','ON','OFF'
]);
const WORD = /[A-Za-z_#][A-Za-z0-9_]*|\d+(?:\.\d+)?/g;
const REF = /:(?:[A-Za-z0-9_']*:)?[A-Za-z0-9_']+\.[A-Za-z0-9_']+/g;

/* character classes: 0 code, 1 comment, 2 string */
function classify(t){
  const n = t.length, k = new Uint8Array(n);
  let i = 0;
  while (i < n){
    const c = t[i];
    if (c === '{'){
      let j = t.indexOf('}', i + 1); j = j < 0 ? n : j + 1;
      k.fill(1, i, j); i = j;
    } else if (c === '"'){
      let j = i + 1;
      while (j < n){
        if (t[j] === '\n') break;
        if (t[j] === '"'){ if (t[j+1] === '"'){ j += 2; continue; } j++; break; }
        j++;
      }
      k.fill(2, i, Math.min(j, n)); i = j;
    } else i++;
  }
  return k;
}

/* one code run -> html, with keywords, numbers and references marked up */
function paintCode(s, links){
  const marks = [];
  REF.lastIndex = 0;
  for (let m; (m = REF.exec(s)); ){
    /* `to` empty means the export could not land it on a block: either the
       name is spliced together at run time (:39FC'FC_NUM1'_AS:...) or no
       block of that name is in the dumps at all. Neither is a link, and
       saying which is which is more useful than styling them the same. */
    const hit = links.get(m[0]);
    const cls = 'hl-ref' + (hit && hit.to ? (hit.w === 1 ? ' w' : '') : ' dead');
    const why = !hit ? '' : hit.w === 1 ? 'เขียนไป ' : hit.w === 2 ? 'ตั้งชื่อย่อให้ ' : 'อ่านจาก ';
    const attr = hit && hit.to
      ? ' data-go="' + esc(hit.to) + '" title="' + esc(why + hit.to + '.' + hit.p) + '"'
      : ' title="' + esc(m[0].indexOf("'") !== -1
                         ? 'ชื่อถูกประกอบตอนรัน — ICC เองก็หาปลายทางไม่ได้'
                         : 'ไม่พบบล็อกนี้ในฐานข้อมูลที่ดัมพ์ไว้') + '"';
    marks.push([m.index, m.index + m[0].length,
                '<span class="' + cls + '"' + attr + '>' + esc(m[0]) + '</span>']);
  }
  WORD.lastIndex = 0;
  for (let m; (m = WORD.exec(s)); ){
    if (marks.some(x => m.index < x[1] && m.index + m[0].length > x[0])) continue;
    const w = m[0].toUpperCase();
    if (KW.has(w))
      marks.push([m.index, m.index + m[0].length, '<span class="hl-kw">' + esc(m[0]) + '</span>']);
    else if (/^[\d#]/.test(m[0]))
      marks.push([m.index, m.index + m[0].length, '<span class="hl-num">' + esc(m[0]) + '</span>']);
  }
  marks.sort((a, b) => a[0] - b[0]);
  let out = '', at = 0;
  for (const [a, b, html] of marks){
    if (a < at) continue;
    out += esc(s.slice(at, a)) + html;
    at = b;
  }
  return out + esc(s.slice(at));
}

function paintSource(b){
  const si = b[4];
  const pane = $('#srcBody');
  if (si < 0){
    $('#srcMeta').textContent = '';
    pane.innerHTML = '<div class="pane-empty">ไม่มีไฟล์ซอร์สของบล็อกนี้ในโฟลเดอร์ S</div>';
    return;
  }
  const [fn, text, sections, includes] = SRCS[si];
  const lines = text.split('\n');
  const kind = classify(text);

  /* every reference this instance resolved, indexed by the line it sits on */
  const byLine = new Map();
  for (const [ln, w, lit, to, p] of b[8]){
    if (!byLine.has(ln)) byLine.set(ln, new Map());
    byLine.get(ln).set(lit, { w, to, p });
  }

  $('#srcMeta').textContent = fn + ' · ' + lines.length.toLocaleString() + ' บรรทัด' +
    (includes.length ? ' · #include ' + includes.length : '');

  let at = 0, html = '';
  for (let i = 0; i < lines.length; i++){
    const raw = lines[i], start = at;
    at += raw.length + 1;
    const links = byLine.get(i + 1) || new Map();

    /* split the line into runs of one class, so a comment tail after code on
       the same line still reads as a comment */
    let body = '', p = 0;
    while (p < raw.length){
      const k = kind[start + p];
      let q = p + 1;
      while (q < raw.length && kind[start + q] === k) q++;
      const seg = raw.slice(p, q);
      body += k === 1 ? '<span class="hl-cmt">' + esc(seg) + '</span>'
            : k === 2 ? '<span class="hl-str">' + esc(seg) + '</span>'
            : paintCode(seg, links);
      p = q;
    }

    /* A reference the line reaches through a #define never appears in the
       text you are looking at — 01LY065.s writes `CBPSPT := Lprevspt;` and
       means V101:01LRCA065.SPT. Those are annotated under the line rather
       than left invisible. */
    const extra = [];
    for (const [lit, hit] of links)
      if (raw.indexOf(lit) === -1 && hit.to)
        extra.push((hit.w === 1 ? '→ เขียน ' : '← อ่าน ') + hit.to + '.' + hit.p);

    html += '<div class="lrow" data-ln="' + (i + 1) + '">' +
      '<div class="ln">' + (i + 1) + '</div><div class="lc">' + (body || ' ') + '</div>' +
      (extra.length ? '<div class="lnote"><b>ผ่าน #define:</b> ' + esc(extra.join('  ·  ')) + '</div>' : '') +
      '</div>';
  }
  pane.innerHTML = html;
  pane.scrollTop = 0;
}

/* =======================================================================
   4. SHOW / SEARCH / SPLIT
   ======================================================================= */
function show(b){
  CUR = b;
  $('#bName').textContent = b[0];
  $('#bDesc').textContent = b[2] || '';
  $('#bDesc').title = b[2] || '';
  $('#bMeta').textContent = 'CP ' + (b[1] || '—') +
    (b[4] >= 0 ? ' · ' + SRCS[b[4]][0] : '');
  $('#q').value = b[0];
  $('#results').innerHTML = '';
  $('#fProps').value = '';
  paintProps(b, '');
  paintIns(b);
  paintOuts(b);
  paintSource(b);
  $('#propsBody').scrollTop = $('#insBody').scrollTop = $('#outsBody').scrollTop = 0;
  try { history.replaceState(null, '', '?tag=' + encodeURIComponent(b[0])); } catch (e) {}
}

document.addEventListener('click', e => {
  const g = e.target.closest('[data-go]');
  if (g){ e.preventDefault(); go(g.dataset.go); }
});

$('#fProps').addEventListener('input', () => { if (CUR) paintProps(CUR, $('#fProps').value); });

/* ---- find in source: Enter walks the hits, it does not re-filter ---- */
let srcHits = [], srcAt = -1, srcQ = '';
function findInSource(){
  const q = $('#fSrc').value.trim(), hit = foxMatch(q);
  $('#srcBody').querySelectorAll('.lrow.marked').forEach(el => el.classList.remove('marked'));
  if (!hit){ srcHits = []; srcAt = -1; srcQ = ''; return; }
  if (q !== srcQ){
    srcQ = q; srcAt = -1;
    const lines = CUR && CUR[4] >= 0 ? SRCS[CUR[4]][1].split('\n') : [];
    srcHits = [];
    for (let i = 0; i < lines.length; i++) if (hit(lines[i])) srcHits.push(i + 1);
  }
  if (!srcHits.length) return;
  srcAt = (srcAt + 1) % srcHits.length;
  const row = $('#srcBody').querySelector('.lrow[data-ln="' + srcHits[srcAt] + '"]');
  if (row){ row.classList.add('marked'); row.scrollIntoView({ block: 'center' }); }
}
$('#fSrc').addEventListener('keydown', e => {
  if (e.key === 'Enter'){ e.preventDefault(); findInSource(); }
});
$('#fSrc').addEventListener('input', () => {
  if (!$('#fSrc').value.trim()){
    srcHits = []; srcAt = -1; srcQ = '';
    $('#srcBody').querySelectorAll('.lrow.marked').forEach(el => el.classList.remove('marked'));
  }
});

/* ---- block search ---- */
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
    return '<div class="rrow" data-i="' + i + '" data-k="' + k + '"><b>' + esc(b[0]) + '</b>' +
      '<span class="ty">' + esc(b[1]) + '</span>' +
      '<span class="ds">' + esc(b[2] || '') + '</span></div>';
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

/* ---- the split between the panes and the source ----
   setPointerCapture, not a document-level mousemove: the pointer crosses the
   iframe's own scrollers on the way down and a plain listener loses the drag
   the moment it does. */
const SPLIT_KEY = 'fox-seq-split';
function setSplit(px){
  const wrap = $('#wrap');
  const h = wrap.clientHeight;
  const v = Math.min(Math.max(px, 120), Math.max(140, h - 120));
  $('#panes').style.flex = '0 0 ' + v + 'px';
}
$('#gutter').addEventListener('pointerdown', e => {
  const wrap = $('#wrap'), top = wrap.getBoundingClientRect().top;
  $('#gutter').setPointerCapture(e.pointerId);
  const move = ev => setSplit(ev.clientY - top);
  const up = ev => {
    $('#gutter').removeEventListener('pointermove', move);
    $('#gutter').removeEventListener('pointerup', up);
    try { localStorage.setItem(SPLIT_KEY, String(ev.clientY - top)); } catch (err) {}
  };
  $('#gutter').addEventListener('pointermove', move);
  $('#gutter').addEventListener('pointerup', up);
});
$('#foldBtn').addEventListener('click', () => {
  const p = $('#srcPane');
  p.classList.toggle('fold');
  $('#foldBtn').textContent = p.classList.contains('fold') ? '▸' : '▾';
});

$('#themeBtn').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', cur);
  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
});
try { const t = localStorage.getItem('fox-theme'); if (t) document.documentElement.setAttribute('data-theme', t); } catch (e) {}

/* =======================================================================
   5. BOOT
   ======================================================================= */
(async function boot(){
  try {
    if (typeof window.FOX_SEQ_B64 !== 'string') throw new Error('ไม่พบไฟล์ sequence.js');
    if (typeof DecompressionStream === 'undefined')
      throw new Error('เบราว์เซอร์นี้ไม่รองรับ DecompressionStream — ใช้ Chrome/Edge รุ่นใหม่');
    const g = await inflate(window.FOX_SEQ_B64);
    BLOCKS = g.blocks; SRCS = g.srcs;
    for (let i = 0; i < BLOCKS.length; i++)
      if (!byName.has(BLOCKS[i][0])) byName.set(BLOCKS[i][0], i);

    $('#boot').classList.add('hide');
    $('#app').classList.remove('hide');
    try {
      const v = parseInt(localStorage.getItem(SPLIT_KEY), 10);
      if (v > 0) setSplit(v);
    } catch (e) {}

    /* ?tag=COMPOUND:BLOCK — a qualified name must match exactly: the plant
       reuses block names across CPs, and the same .s runs in several
       compounds, so a near miss opens a different unit's sequence. Only a
       bare name, which cannot be ambiguous by intent, falls back. */
    const want = new URLSearchParams(location.search).get('tag');
    let i = want ? byName.get(want) : undefined;
    if (i === undefined && want && want.indexOf(':') === -1)
      i = BLOCKS.findIndex(b => b[0].split(':').pop() === want) || undefined;
    if (i !== undefined && i >= 0){ show(BLOCKS[i]); return; }

    $('#propsBody').innerHTML = '<div class="pane-empty">' +
      (want ? esc(want) + ' ไม่ใช่บล็อก IND — Sequence View มีเฉพาะ ' +
              BLOCKS.length.toLocaleString() + ' บล็อก sequence'
            : 'ค้นหาบล็อกด้านบน — มี ' + BLOCKS.length.toLocaleString() +
              ' sequence block จาก ' + SRCS.length.toLocaleString() + ' ไฟล์ซอร์ส') +
      '</div>';
  } catch (e){
    $('#bootMsg').textContent = e.message;
    $('#boot').querySelector('.ring').style.display = 'none';
  }
})();
"""

JS = JS.replace("__FOXMATCH__", FOXMATCH.rstrip())

page = (
    "<!doctype html>\n"
    '<html lang="th">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    "<!-- these files are edited in place; never serve a stale copy -->\n"
    '<meta http-equiv="cache-control" content="no-store">\n'
    "<title>FOXBORO SEQUENCE VIEW</title>\n"
    "<style>\n" + SHELL_CSS + "\n" + CSS + "</style>\n"
    "</head>\n"
    "<body>\n" + BODY + "\n"
    '<script src="sequence.js"></script>\n'
    "<script>\n" + JS + "</script>\n"
    "</body>\n"
    "</html>\n"
)

io.open(OUT, "w", encoding="utf8", newline="").write(page)
print("sequence-view.html written, %.1f KB (%d KB of it the shared stylesheet)"
      % (len(page.encode("utf8")) / 1024, len(SHELL_CSS.encode("utf8")) / 1024))
