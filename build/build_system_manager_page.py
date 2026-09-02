# -*- coding: utf-8 -*-
"""Assemble system-manager.html from system-monitor.html's shell.

The page follows the screen it replaces: Schneider **System Auditor**
(`09.png`). Everything is on one screen at once -- no tabs, no drill-down
that hides what you were just looking at -- because that is how the real
tool is read: you pick a station in the network diagram and the compound,
type, block and parameter panes all answer at the same time.

Eight panes, the same names the real tool uses:

    Foxboro Network   clickable equipment boxes hanging off a bus
    Parameter         the station's own STA block, parameter by parameter
    Compound List     CP | COMPOUND
    Compound Props    the compound record's parameters
    Blocks Types      ALL TYPES + one row per type, with counts
    Block List        CP | COMPOUND | BLOCK | TYPE
    Block Properties  every parameter of the selected block
    Block Mapping     one hop: the blocks wired into this block's inputs

Nothing here is invented. The network boxes come from the hardware
register (`systems.js`), the compounds and blocks from the SaveAll export
(`data.js`), and which parameter is an input, an output or a data store
from the manual set (`params.js`, via B0193AX).

The `<head>` -- fonts, design tokens, the whole shared shell -- is lifted
out of system-monitor.html verbatim so the two pages cannot drift apart.
Re-run this after any change to that shell.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
SRC = os.path.join(WEB, "system-monitor.html")
OUT = os.path.join(WEB, "system-manager.html")

src = open(SRC, encoding="utf8").read()
m = re.search(r"<head>.*?</head>", src, re.S)
assert m, "cannot find <head> in system-monitor.html"
head = m.group(0)
head = head.replace("<title>FOXBORO FBM (I/O) MODULE MANAGEMENT</title>",
                    "<title>FOXBORO SYSTEM MANAGER</title>")
assert "<title>FOXBORO SYSTEM MANAGER</title>" in head, "title swap failed"

PAGE_CSS = """
/* ====================================================== SYSTEM MANAGER = */
/* The System Auditor screen: one toolbar, one breadcrumb, eight panes that
   are all answering about the same selection at the same time. */

/* ---- toolbar: network scope, breadcrumb, jump-to-tag ----------------- */
.abar{
  display:flex; align-items:center; gap:10px 14px; flex-wrap:wrap;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-pill); box-shadow:var(--lift-sm), var(--inset-hi);
  padding:8px 16px; flex:none;
}
.abar .lbl{font-size:10.5px; font-weight:800; letter-spacing:.11em;
  text-transform:uppercase; color:var(--text-faint)}
.abar select{
  border:1px solid var(--border); background:var(--surface-2); color:var(--text);
  border-radius:var(--r-pill); padding:6px 26px 6px 12px; font-size:12.5px;
  font-weight:700; box-shadow:var(--press); cursor:pointer; appearance:none;
  background-image:linear-gradient(45deg,transparent 50%,var(--text-faint) 50%),
                   linear-gradient(135deg,var(--text-faint) 50%,transparent 50%);
  background-position:calc(100% - 14px) 52%, calc(100% - 9px) 52%;
  background-size:5px 5px, 5px 5px; background-repeat:no-repeat;
}
.abar select:focus-visible{outline:3px solid var(--mint-ring); outline-offset:2px}
.crumb{display:flex; align-items:center; gap:5px; flex-wrap:wrap; font-size:12.5px}
.crumb button{
  border:0; background:transparent; color:var(--accent); cursor:pointer;
  font-size:12.5px; font-weight:800; padding:2px 6px; border-radius:var(--r-sm);
}
.crumb button:hover{background:var(--surface-2)}
.crumb button.here{color:var(--text); cursor:default}
.crumb button.here:hover{background:transparent}
.crumb .sep{color:var(--text-faint); font-size:10px}
.abar .qwrap{position:relative; margin-left:auto; min-width:230px}
.abar .search{min-width:230px}
.hits{
  position:absolute; z-index:60; top:calc(100% + 6px); left:0; right:0;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift); padding:5px;
  max-height:300px; overflow:auto;
}
.hits button{
  display:block; width:100%; text-align:left; border:0; background:transparent;
  color:inherit; border-radius:var(--r-sm); padding:6px 9px; cursor:pointer;
  font-size:12.5px; font:inherit;
}
.hits button:hover{background:var(--surface-2)}
.hits button b{display:block; font-size:12.5px; font-weight:800}
.hits button i{font-style:normal; color:var(--text-faint); font-size:11px}

/* ---- the eight-pane grid -------------------------------------------- */
.auditor{
  display:grid; gap:10px; min-width:0; flex:1 1 auto;
  grid-template-columns:minmax(290px,1.05fr) minmax(215px,.82fr)
                        minmax(132px,.46fr) minmax(330px,1.6fr);
  /* every row is a definite height on purpose: the panes have to scroll
     inside themselves, the way the Auditor's do. With an `auto` (or an
     unresolved `1fr`) row, Block Properties' 105 parameters stretch the
     row instead and the one-screen reading is gone. */
  grid-template-rows:262px 206px 348px;
  grid-template-areas:
    "net    clist  types blist"
    "param  cprops types blist"
    "bprops bmap   bmap  bmap";
}
.a-net{grid-area:net} .a-param{grid-area:param}
.a-clist{grid-area:clist} .a-cprops{grid-area:cprops}
.a-types{grid-area:types} .a-blist{grid-area:blist}
.a-bprops{grid-area:bprops} .a-bmap{grid-area:bmap}

/* the equipment rail eats ~300px, so the grid folds earlier than it would
   on its own; folded away, the wide arrangement comes back */
@media (max-width:1800px){
  .auditor{
    grid-template-columns:minmax(270px,1fr) minmax(205px,.85fr) minmax(310px,1.5fr);
    grid-template-rows:262px 206px 240px 348px;
    grid-template-areas:
      "net    clist  blist"
      "param  cprops blist"
      "types  bprops bprops"
      "bmap   bmap   bmap";
  }
}
@media (max-width:1320px){
  .auditor{
    grid-template-columns:1fr;
    grid-template-rows:repeat(8,300px);
    grid-template-areas:"net" "clist" "types" "blist" "param" "cprops" "bprops" "bmap";
  }
}

/* ---- the equipment tree, 08.png's left half ------------------------- */
/* System Manager's own pane: network › station › FBM module › channel.
   It rides in the shared folding rail, the same gesture as the tag
   table's filter — the shell already carries .rail / .rail-toggle. */
.tree{display:flex; flex-direction:column; gap:1px; margin:0 -6px; min-height:60px}
.tnode{
  display:flex; align-items:center; gap:5px; border-radius:var(--r-sm);
  border:1px solid transparent; padding:4px 8px 4px 4px; cursor:pointer;
  line-height:1.24;
}
.tnode:hover{background:var(--surface-2)}
.tnode.on{background:color-mix(in srgb, var(--mint) 42%, transparent);
  border-color:var(--mint-ring)}
.tnode .caret{
  flex:none; width:17px; height:17px; padding:0; border:0; cursor:pointer;
  background:transparent; color:var(--text-faint); font-size:9px; line-height:1;
  border-radius:5px; display:flex; align-items:center; justify-content:center;
  transition:transform .14s ease;
}
.tnode .caret:hover{background:var(--surface-3); color:var(--text)}
.tnode .caret.open{transform:rotate(90deg)}
.tnode .caret.leaf{cursor:default; visibility:hidden}
.tnode .tico{flex:none; width:14px; text-align:center; font-size:10px; color:var(--text-faint)}
.tnode.on .tico{color:var(--used-ink)}
.tnode .tlab{min-width:0; display:flex; flex-direction:column}
.tnode .tlab b{font-size:12.5px; font-weight:800; letter-spacing:.01em;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.tnode .tlab em{font-style:normal; font-size:10.5px; color:var(--text-faint);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.tnode.on .tlab em{color:var(--used-ink); opacity:.72}
.tnode .cnt{margin-left:auto; flex:none; font-size:10px; font-weight:800;
  color:var(--text-faint); padding-left:6px}
.tmore{font-size:11px; color:var(--text-faint); font-style:italic; padding:4px 8px 4px 28px}

/* ---- chain-length slider in the Block Mapping header ----------------- */
.dep{display:flex; align-items:center; gap:7px; margin-left:auto;
  text-transform:none; letter-spacing:0; font-size:10.5px; font-weight:700;
  color:var(--text-faint)}
.dep input[type=range]{width:86px; accent-color:var(--mint-deep); cursor:pointer}
.dep b{font-size:11.5px; font-weight:800; color:var(--accent); min-width:9px}
.pn > h3 .dep + .n{margin-left:14px}

/* ---- one pane ------------------------------------------------------- */
.pn{
  display:flex; flex-direction:column; min-width:0; min-height:0;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-md); box-shadow:var(--lift-sm), var(--inset-hi);
  overflow:hidden;
}
.pn > h3{
  flex:none; display:flex; align-items:center; gap:8px;
  font-size:10px; font-weight:800; letter-spacing:.11em; text-transform:uppercase;
  color:var(--text-dim); background:var(--surface-2);
  border-bottom:1px solid var(--border); padding:7px 11px;
}
.pn > h3 .n{margin-left:auto; color:var(--accent); font-size:9.5px; letter-spacing:.04em}
.pn > h3 .pf{
  margin-left:auto; border:1px solid var(--border); background:var(--surface);
  color:var(--text); border-radius:var(--r-pill); padding:2px 9px; font-size:10.5px;
  font-weight:600; letter-spacing:0; text-transform:none; width:104px; box-shadow:var(--press);
}
.pn > h3 .pf:focus-visible{outline:2px solid var(--mint-ring); outline-offset:1px}
.pn > .bd{flex:1 1 auto; min-height:0; overflow:auto; position:relative}
.pn .empty{padding:26px 12px; text-align:center; color:var(--text-faint); font-size:12px}

/* ---- the pane tables ------------------------------------------------ */
.gt{width:100%; border-collapse:separate; border-spacing:0; font-size:12.5px}
.gt th{
  position:sticky; top:0; z-index:2; background:var(--surface-2);
  font-size:9.5px; font-weight:800; letter-spacing:.09em; text-transform:uppercase;
  color:var(--text-faint); text-align:left; padding:6px 10px; white-space:nowrap;
  border-bottom:1px solid var(--border);
}
.gt td{
  padding:4px 10px; border-bottom:1px solid var(--border-soft);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:0;
}
.gt td.w{max-width:none; white-space:normal; word-break:break-word}
.gt tbody tr{cursor:pointer}
.gt tbody tr:hover{background:var(--surface-2)}
.gt tbody tr.on{background:color-mix(in srgb, var(--mint) 46%, transparent)}
.gt tbody tr.on td{color:var(--used-ink); font-weight:700}
.gt td b{font-weight:800}
.gt td .dim{color:var(--text-faint)}
.gt .num{text-align:right; font-variant-numeric:tabular-nums; color:var(--text-faint);
  font-size:11.5px; font-weight:700}
.more{
  display:block; width:100%; border:0; background:transparent; cursor:pointer;
  color:var(--accent); font-size:11.5px; font-weight:700; padding:8px; font:inherit;
}
.more:hover{background:var(--surface-2)}

/* the two-column parameter tables: Parameter, Compound Props, Block Props */
.gt.pv td:first-child{font-weight:800; width:44%; color:var(--text-dim)}
.gt.pv tbody tr{cursor:default}
.gt.pv tbody tr:hover{background:transparent}
.gt.pv td.ref{color:var(--accent); font-weight:700; cursor:pointer}
.gt.pv td.ref:hover{text-decoration:underline}
.gt.pv .sec td{
  background:var(--surface-2); font-size:9.5px; font-weight:800; letter-spacing:.11em;
  text-transform:uppercase; color:var(--text-faint); padding:5px 10px;
}

/* ---- Foxboro Network: boxes on a bus -------------------------------- */
.net{padding:12px 14px 16px}
.nrow{display:flex; flex-wrap:wrap; gap:14px 13px; padding-top:2px}
.nbox{
  position:relative; flex:none; width:104px; margin-top:15px;
  display:flex; flex-direction:column; align-items:center; gap:0;
  background:var(--surface-2); border:1.5px solid var(--text-faint);
  border-radius:3px; padding:6px 5px; cursor:pointer; line-height:1.22;
  font:inherit; color:inherit; text-align:center;
}
.nbox b{font-size:11.5px; font-weight:800; letter-spacing:.01em;
  max-width:100%; overflow:hidden; text-overflow:ellipsis}
.nbox i{font-style:normal; font-size:9.5px; color:var(--text-faint);
  max-width:100%; overflow:hidden; text-overflow:ellipsis}
.nbox:hover{background:var(--surface-3)}
.nbox:focus-visible{outline:3px solid var(--mint-ring); outline-offset:2px}
.nbox.on{background:var(--mint); border-color:var(--mint-ring); color:var(--used-ink)}
.nbox.on i{color:var(--used-ink); opacity:.72}
/* the stub down from the bus, and this box's own slice of the bus — the
   slices of neighbouring boxes meet across the gap and read as one line */
.nbox::before{content:''; position:absolute; left:50%; top:-9px; width:1.5px; height:9px;
  background:var(--text-faint)}
.nbox::after{content:''; position:absolute; left:-7px; right:-7px; top:-9px; height:1.5px;
  background:var(--text-faint)}
.nroot{display:flex; justify-content:flex-start; padding-bottom:0}
.nroot .nbox{margin-top:0; width:118px; background:var(--surface-3)}
.nroot .nbox.on{background:var(--mint)}
.nroot .nbox::before,.nroot .nbox::after{display:none}
.ndrop{width:1.5px; height:13px; background:var(--text-faint); margin-left:58px}

/* ---- Block Mapping --------------------------------------------------- */
.bmap{padding:12px 14px; min-width:max-content}
.bmap svg{display:block; overflow:visible}
.bmap .bx{fill:var(--surface-2); stroke:var(--text-faint); stroke-width:1.2}
.bmap .bx.root{fill:var(--mint); stroke:var(--mint-ring)}
.bmap .bx.ecb{fill:var(--held); stroke:var(--held-edge)}
.bmap a.src{cursor:pointer}
.bmap a.src:hover .bx{stroke-width:2.4}
.bmap a.src:hover .t1{text-decoration:underline}
.bmap a.src:focus-visible .bx{stroke:var(--accent); stroke-width:2.6}
.bmap a.src:focus{outline:none}
.bmap text{font-family:var(--font-ui); fill:var(--text)}
.bmap .t1{font-size:11px; font-weight:800}
.bmap .t2{font-size:9.5px; fill:var(--text-dim)}
.bmap .pin{font-size:9px; font-weight:700; fill:var(--text-dim)}
.bmap .wire{fill:none; stroke:var(--accent); stroke-width:1.3}
.bmap .wlab{font-size:8.5px; font-weight:800; fill:var(--accent)}
.bmap .arrow{fill:var(--accent)}
/* feedback: a cascade's return path runs against every other wire */
.bmap .wire.fb{stroke:var(--amber-deep); stroke-dasharray:4 3}
.bmap .wlab.fb{fill:var(--amber-deep)}
.bmap .arrow.fb{fill:var(--amber-deep)}
.mapnote{padding:6px 14px 12px; font-size:11px; color:var(--text-faint)}

main{display:flex; flex-direction:column; gap:16px; min-width:0}
"""
head = head.replace("</style>", PAGE_CSS + "</style>", 1)

BODY = r"""
<body>

<div id="boot">
  <div class="ring"></div>
  <p id="bootMsg">กำลังโหลดฐานข้อมูล…</p>
</div>

<div class="app hide" id="app">

  <header class="topbar">
    <div>
      <p class="eyebrow">Foxboro I/A Series · equipment &amp; control hierarchy</p>
      <h1>SYSTEM MANAGER</h1>
      <p class="lede" id="lede"></p>
    </div>
    <div class="tools">
      <button class="btn" id="csvBtn">Export CSV</button>
      <button class="btn icon" id="themeBtn" title="สลับธีมสว่าง/มืด">◐</button>
    </div>
  </header>

  <nav class="pagenav" aria-label="หน้าในชุดเครื่องมือ">
    <a href="system-manager.html" aria-current="page"><b>SYSTEM MANAGER</b><i>ผังอุปกรณ์ &amp; บล็อก</i></a>
    <a href="index.html"><b>TAG SEARCH</b><i>ตาราง tag ทั้งหมด</i></a>
    <a href="signal-map.html"><b>SIGNAL MAP</b><i>ผังการเดินสัญญาณ</i></a>
    <a href="system-monitor.html"><b>FBM (I/O) MODULE MANAGEMENT</b><i>โมดูล &amp; spare point</i></a>
    <a href="modbus.html"><b>MODBUS COMMUNICATION</b><i>register IN/OUT ต่ออุปกรณ์</i></a>
  </nav>

  <div class="abar">
    <span class="lbl">Foxboro Network</span>
    <select id="netSel" aria-label="เลือก station"></select>
    <div class="crumb" id="crumb"></div>
    <div class="qwrap">
      <label class="search">
        <input id="q" placeholder="ค้นหา tag / compound / station…" autocomplete="off">
        <i class="mag">⌕</i>
      </label>
      <div class="hits hide" id="hits"></div>
    </div>
  </div>

  <div class="layout">

  <div class="rail-shell">
    <button class="rail-toggle" id="railToggle" type="button"
            aria-expanded="true" aria-controls="rail"
            aria-label="ย่อผังอุปกรณ์" title="ย่อผังอุปกรณ์">&#8249;</button>
    <aside class="rail" id="rail">
      <div class="rail-logo" id="railLogo" role="button" tabindex="0"
           aria-label="หยุดการเคลื่อนไหวของไอคอน"
           title="คลิกเพื่อหยุดการเคลื่อนไหว"></div>
      <div class="rail-head">
        <b>Equipment <span id="nTree" style="color:var(--text-faint);font-weight:700"></span></b>
        <button class="mini" id="collapseAll" title="ยุบทุกกิ่ง">ยุบทั้งหมด</button>
      </div>
      <div class="tree" id="tree"></div>
    </aside>
  </div>

  <div class="auditor">

    <section class="pn a-net">
      <h3>Foxboro Network <span class="n" id="nNet"></span></h3>
      <div class="bd"><div class="net" id="net"></div></div>
    </section>

    <section class="pn a-param">
      <h3>Parameter <span class="n" id="nPar"></span></h3>
      <div class="bd" id="param"></div>
    </section>

    <section class="pn a-clist">
      <h3>Compound List <span class="n" id="nCmp"></span></h3>
      <div class="bd" id="clist"></div>
    </section>

    <section class="pn a-cprops">
      <h3>Compound Properties</h3>
      <div class="bd" id="cprops"></div>
    </section>

    <section class="pn a-types">
      <h3>Blocks Types</h3>
      <div class="bd" id="types"></div>
    </section>

    <section class="pn a-blist">
      <h3>Block List <span class="n" id="nBlk"></span></h3>
      <div class="bd" id="blist"></div>
    </section>

    <section class="pn a-bprops">
      <h3>Block Properties <input class="pf" id="pq" placeholder="กรอง…" autocomplete="off"></h3>
      <div class="bd" id="bprops"></div>
    </section>

    <section class="pn a-bmap">
      <h3>Block Mapping
        <span class="dep">ความยาวโซ่
          <input type="range" id="mdep" min="1" max="6" value="1" aria-label="ความยาวโซ่">
          <b id="mdepN">1</b>
        </span>
        <span class="n" id="nMap"></span>
      </h3>
      <div class="bd" id="bmap"></div>
    </section>

  </div>
  </div>
</div>

<script src="data.js"></script>
<script src="systems.js"></script>
<script src="params.js"></script>
<script>
"use strict";

/* =======================================================================
   1. DECODE  —  base64 -> gzip -> JSON  (works straight off file://)
   ======================================================================= */
const $ = s => document.querySelector(s);
const fmt = n => Number(n || 0).toLocaleString('en-US');
const esc = s => String(s == null ? '' : s)
  .replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const COLL = new Intl.Collator('en', {numeric:true, sensitivity:'base'});

async function decodePayload(b64){
  const bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
  for (let i = 0; i < n; i++) u8[i] = bin.charCodeAt(i);
  const st = new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(new TextDecoder().decode(await new Response(st).arrayBuffer()));
}

/* =======================================================================
   2. COLUMN STORE  —  the same dictionary + sparse codes index.html reads.
   ======================================================================= */
let N = 0, HEAD = [], RAW = [], IDX = new Map();
const denseCache = new Map(), EMPTY_D = [];

function spec(ci){ const s = RAW[ci]; return (s && s.d) ? s : null; }
function dictOf(ci){ const s = spec(ci); return s ? s.d : EMPTY_D; }
function dense(ci){
  let a = denseCache.get(ci);
  if (a) return a;
  const s = spec(ci);
  a = new Int32Array(N).fill(-1);
  if (s){
    if (s.r){ let r = 0; for (let k = 0; k < s.r.length; k++){ r += s.r[k]; a[r] = s.v[k]; } }
    else for (let i = 0; i < s.v.length; i++) a[i] = s.v[i];
  }
  denseCache.set(ci, a);
  return a;
}
function valueAt(ci, row){
  if (ci === undefined || row == null || row < 0) return '';
  const c = dense(ci)[row];
  return c < 0 ? '' : RAW[ci].d[c];
}
const val = (name, row) => valueAt(IDX.get(name), row);

/* every non-empty parameter of one row, in file order.
   Memoised: the chain view walks a couple of dozen rows and comes back to
   the same ones every time the depth slider moves. */
const rvCache = new Map();
function rowValues(row){
  let hit = rvCache.get(row);
  if (hit) return hit;
  if (rvCache.size > 400) rvCache.clear();
  const out = [];
  for (let ci = 0; ci < RAW.length; ci++){
    const sp = RAW[ci];
    if (!sp || !sp.d) continue;
    let code = -1;
    if (sp.r){
      let r = 0;
      for (let k = 0; k < sp.r.length; k++){
        r += sp.r[k];
        if (r === row){ code = sp.v[k]; break; }
        if (r > row) break;                       // delta rows ascend
      }
    } else if (row < sp.v.length) code = sp.v[row];
    if (code >= 0 && sp.d[code] !== '') out.push([HEAD[ci], sp.d[code]]);
  }
  rvCache.set(row, out);
  return out;
}

/* =======================================================================
   3. THE HIERARCHY
   CPS[i] = one station: its rows, its compounds, its modules.
   ======================================================================= */
let SYS = [], MODS = [], GEN = '';
let CPS = [], CPN = new Map();
let iName, iType, iCp;
let NAMEROW = null;
/* "<cp>|<letterbug>" -> the blocks landed on that piece of hardware
   "<cp>|<parent>"    -> the child device ECBs hanging off a module */
const IOMMAP = new Map(), KIDMAP = new Map();

function newStation(name){
  return {n:name, rows:[], cm:new Map(), comps:[], types:new Map(),
          mods:[], si:-1, sta:-1, area:''};
}

function buildIndex(){
  const nmA = dense(iName), dn = dictOf(iName);
  const tyA = dense(iType), dt = dictOf(iType);
  const cpA = dense(iCp),   dc = dictOf(iCp);
  const ciIom = IDX.get('IOM_ID'), ciIomR = IDX.get('IOMIDR'), ciPar = IDX.get('PARENT');
  const iomA = dense(ciIom), di = dictOf(ciIom);
  const iorA = dense(ciIomR), dr = dictOf(ciIomR);
  const parA = dense(ciPar), dp = dictOf(ciPar);

  for (let i = 0; i < N; i++){
    const c = cpA[i]; if (c < 0) continue;
    const cn = dc[c];
    let s = CPN.get(cn);
    if (s === undefined){ s = CPS.length; CPN.set(cn, s); CPS.push(newStation(cn)); }
    const st = CPS[s];
    st.rows.push(i);

    const t = tyA[i] < 0 ? '' : dt[tyA[i]];
    if (t) st.types.set(t, (st.types.get(t) || 0) + 1);
    if (t === 'STA') st.sta = i;

    /* NAME is COMPOUND:BLOCK — the compound's own record carries no colon */
    const full = nmA[i] < 0 ? '' : dn[nmA[i]];
    const k = full.indexOf(':');
    const comp = k > 0 ? full.slice(0, k) : full;
    let cr = st.cm.get(comp);
    if (!cr){ cr = {n:comp, row:-1, rows:[], j:0}; st.cm.set(comp, cr); st.comps.push(cr); }
    if (k > 0) cr.rows.push(i); else cr.row = i;

    /* a redundant pair (FBM05 and friends) is reached by either letterbug:
       IOM_ID names one module, IOMIDR its partner, and the block belongs to
       both — index both or the partner looks like it carries nothing */
    const iv = iomA[i] < 0 ? '' : di[iomA[i]];
    const ir = iorA[i] < 0 ? '' : dr[iorA[i]];
    for (const dd of (ir && ir !== iv) ? [iv, ir] : [iv]){
      if (!dd) continue;
      const kk = cn + '|' + dd; let a = IOMMAP.get(kk); if (!a) IOMMAP.set(kk, a = []); a.push(i);
    }
    const pv = parA[i] < 0 ? '' : dp[parA[i]];
    if (pv && t.slice(0, 3) === 'ECB'){
      const kk = cn + '|' + pv; let a = KIDMAP.get(kk); if (!a) KIDMAP.set(kk, a = []); a.push(i);
    }
  }
}

/* every block bound to a module: straight to its letterbug, or through one
   of its child device ECBs (HART/FF/serial address the child, not the module) */
function modBlocks(st, m){
  const out = [], seen = new Set();
  const push = a => { for (const r of a || []) if (!seen.has(r)){ seen.add(r); out.push(r); } };
  push(IOMMAP.get(st.n + '|' + m.d));
  for (const k of KIDMAP.get(st.n + '|' + m.d) || []){
    const dv = val('DEV_ID', k);
    if (dv) push(IOMMAP.get(st.n + '|' + dv));
  }
  return out.filter(r => val('TYPE', r).slice(0, 3) !== 'ECB');
}

/* the hardware register knows two stations the SaveAll export does not, so
   the network is the union — a station with modules and no blocks still shows */
function mergeSystems(){
  SYS.forEach((s, si) => {
    let i = CPN.get(s.n);
    if (i === undefined){ i = CPS.length; CPN.set(s.n, i); CPS.push(newStation(s.n)); }
    CPS[i].si = si;
    CPS[i].area = s.area || '';
    CPS[i].mods = s.mods.slice().sort((a, b) => COLL.compare(MODS[a].d, MODS[b].d));
  });
  CPS.sort((a, b) => COLL.compare(a.n, b.n));
  CPN = new Map(CPS.map((s, i) => [s.n, i]));
  for (const st of CPS){
    st.comps.sort((a, b) => COLL.compare(a.n, b.n));
    st.comps.forEach((c, j) => { c.j = j; });
  }
}

function nameRow(name){
  if (!NAMEROW){
    NAMEROW = new Map();
    const a = dense(iName), d = dictOf(iName);
    for (let i = 0; i < N; i++){ const c = a[i]; if (c >= 0 && !NAMEROW.has(d[c])) NAMEROW.set(d[c], i); }
  }
  const r = NAMEROW.get(name);
  return r === undefined ? -1 : r;
}

/* never fall back to a bare name when a qualified one was given: the plant
   reuses block names across stations */
const REFRE = /^([A-Za-z0-9_]{0,32}):?([A-Za-z0-9_]{1,32})\.([A-Za-z0-9_]{1,16})$/;
let shortIndex = null;
function buildShortIndex(){
  if (shortIndex) return;
  shortIndex = new Map();
  nameRow('');                                     // forces NAMEROW
  for (const [nm, row] of NAMEROW){
    const s = nm.split(':').pop();
    let a = shortIndex.get(s); if (!a) shortIndex.set(s, a = []);
    a.push(row);
  }
}
function resolveRef(v, from){
  const m = REFRE.exec(v); if (!m) return -1;
  if (m[1]) return nameRow(m[1] + ':' + m[2]);
  buildShortIndex();
  const cands = shortIndex.get(m[2]);
  if (!cands || !cands.length) return -1;
  const cp = val('CP NAME', from);
  const same = cands.filter(r => val('CP NAME', r) === cp);
  return (same.length ? same : cands)[0];
}
const isRefVal = (v, from) =>
  v && v.indexOf('.') > 0 && v.length < 72 && isNaN(Number(v)) &&
  REFRE.test(v) && resolveRef(v, from) >= 0;

/* =======================================================================
   4. STATE
   selCp -1 is ALL NETWORK; selComp -1 is every compound in scope.
   ======================================================================= */
let PARAMS = {};
let selCp = -1, selComp = -1, selType = '', selBlk = -1;
/* selMod is the equipment rail's own scope: pick an FBM in the tree and
   the block panes narrow to what is landed on that module */
let selMod = -1, MODROWS = null;
let blkCap = 300, cmpCap = 300;
let pFilter = '';
let depth = 1;
let expanded = new Set(['net']);

const curSt = () => selCp >= 0 ? CPS[selCp] : null;
const curComp = () => { const s = curSt(); return (s && selComp >= 0) ? s.comps[selComp] : null; };

let ALLROWS = null;
function allRows(){
  if (ALLROWS) return ALLROWS;
  const out = [];
  for (const s of CPS) for (const r of s.rows) out.push(r);
  return ALLROWS = out;
}

/* every block in the current module / compound / station, before the type filter */
function scopeRows(){
  if (selMod >= 0) return MODROWS || [];
  const c = curComp(); if (c) return c.rows;
  const st = curSt();  if (st) return st.rows;
  return allRows();
}

/* type counts for the scope — cached, because ALL NETWORK is 77,010 rows */
let tcKey = null, tcVal = null;
function typeCounts(){
  const key = selCp + '|' + selComp + '|' + selMod;
  if (tcKey === key) return tcVal;
  const rows = scopeRows(), a = dense(iType), d = dictOf(iType);
  const m = new Map();
  for (const r of rows){ const c = a[r]; if (c < 0) continue; const t = d[c];
    m.set(t, (m.get(t) || 0) + 1); }
  tcKey = key;
  return tcVal = [...m.entries()].sort((x, y) => COLL.compare(x[0], y[0]));
}

function blockRows(){
  const rows = scopeRows();
  if (!selType) return rows;
  const a = dense(iType), d = dictOf(iType);
  return rows.filter(r => { const c = a[r]; return c >= 0 && d[c] === selType; });
}

/* =======================================================================
   5. PANE: Foxboro Network — boxes hanging off a bus
   ======================================================================= */
function drawNet(){
  const st = SYS.length ? '' : '';
  let h = '<div class="nroot"><button class="nbox' + (selCp < 0 ? ' on' : '') +
          '" data-cp="-1"><b>ALL</b><i>NETWORK</i></button></div>' +
          '<div class="ndrop"></div><div class="nrow">';
  for (let i = 0; i < CPS.length; i++){
    const s = CPS[i], sy = s.si >= 0 ? SYS[s.si] : null;
    const sub = (sy && sy.sta) ? sy.sta : (s.rows.length ? 'station' : 'register only');
    h += '<button class="nbox' + (i === selCp ? ' on' : '') + '" data-cp="' + i + '" title="' +
         esc(s.n + ' · ' + sub) + '"><b>' + esc(s.n) + '</b><i>' + esc(sub) + '</i></button>';
  }
  $('#net').innerHTML = h + '</div>';
  $('#nNet').textContent = fmt(CPS.length) + ' station';
}

/* =======================================================================
   5b. THE EQUIPMENT RAIL  —  08.png's left half
   network › station › FBM module › channel, the tree System Manager
   itself draws. It rides in the shared folding rail, so the gesture is the
   one the tag table's filter already taught: chevron on the edge, the tile
   as the way back out.
   ======================================================================= */
const MAXKIDS = 250;

const nkey = n => n.k === 'net' ? 'net'
  : n.k === 'cp'  ? 'cp:'  + n.i
  : n.k === 'mod' ? 'mod:' + n.i
  : 'ch:' + n.i + ':' + n.c;

function parseKey(s){
  const p = s.split(':');
  if (p[0] === 'net') return {k:'net'};
  if (p[0] === 'cp')  return {k:'cp',  i:+p[1]};
  if (p[0] === 'mod') return {k:'mod', i:+p[1]};
  return {k:'ch', i:+p[1], c:+p[2]};
}

function kidCount(n){
  if (n.k === 'net') return CPS.length;
  if (n.k === 'cp')  return CPS[n.i].mods.length;
  if (n.k === 'mod') return MODS[n.i].ch.length;
  return 0;
}
function kidsOf(n){
  if (n.k === 'net') return CPS.map((s, i) => ({k:'cp', i}));
  if (n.k === 'cp')  return CPS[n.i].mods.map(mi => ({k:'mod', i:mi}));
  if (n.k === 'mod') return MODS[n.i].ch.map((c, ci) => ({k:'ch', i:n.i, c:ci}));
  return [];
}
function nodeInfo(n){
  if (n.k === 'net') return {lab:'ALL NETWORK', sub:fmt(CPS.length) + ' station', ico:'◎', cnt:''};
  if (n.k === 'cp'){
    const st = CPS[n.i], s = st.si >= 0 ? SYS[st.si] : null;
    return {lab:st.n, sub:(s && s.sta ? s.sta : 'station') + (st.rows.length ? '' : ' · register only'),
            ico:'▤', cnt:st.mods.length || ''};
  }
  if (n.k === 'mod'){
    const m = MODS[n.i];
    return {lab:m.d, sub:(m.m || 'FBM') + (m.md ? ' · ' + m.md : ''), ico:'▥', cnt:m.ch.length || ''};
  }
  const m = MODS[n.i], c = m.ch[n.c];
  return {lab:'CH' + (n.c + 1) + (c[0] ? ' · ' + c[0] : ''),
          sub:c[1] ? c[1] : (c[4] ? 'ECB ' + c[4] + ' · ยังไม่มีบล็อก' : 'ว่าง'),
          ico:c[1] ? '●' : (c[4] ? '◐' : '○'), cnt:''};
}

/* which tree node the panes are currently standing on */
function treeKey(){
  if (selMod >= 0) return 'mod:' + selMod;
  if (selCp >= 0) return 'cp:' + selCp;
  return 'net';
}

function drawTree(){
  const here = treeKey();
  const out = [];
  (function walk(n, dep){
    const k = nkey(n), info = nodeInfo(n), kids = kidCount(n);
    const open = expanded.has(k);
    out.push('<div class="tnode' + (k === here ? ' on' : '') + '" data-k="' + k +
      '" style="padding-left:' + (4 + dep * 13) + 'px">' +
      '<button class="caret' + (kids ? (open ? ' open' : '') : ' leaf') + '" data-act="tog" ' +
      'tabindex="-1" aria-hidden="' + (kids ? 'false' : 'true') + '">&#9654;</button>' +
      '<span class="tico">' + info.ico + '</span>' +
      '<span class="tlab"><b>' + esc(info.lab) + '</b><em>' + esc(info.sub) + '</em></span>' +
      (info.cnt ? '<span class="cnt">' + info.cnt + '</span>' : '') +
      '</div>');
    if (!open || !kids) return;
    const list = kidsOf(n);
    for (const c of list.slice(0, MAXKIDS)) walk(c, dep + 1);
    if (list.length > MAXKIDS)
      out.push('<div class="tmore" style="padding-left:' + (4 + (dep + 1) * 13) + 'px">' +
               'อีก ' + fmt(list.length - MAXKIDS) + ' รายการ</div>');
  })({k:'net'}, 0);
  $('#tree').innerHTML = out.join('');
  $('#nTree').textContent = '(' + fmt(CPS.length) + ')';
  const on = $('#tree .tnode.on');
  if (on) on.scrollIntoView({block:'nearest'});
}

/* open every ancestor of what the panes are showing */
function revealTree(){
  expanded.add('net');
  if (selCp >= 0) expanded.add('cp:' + selCp);
}

/* =======================================================================
   6. PANE: the three Parameter / Value tables
   Parameter (the station's STA block) · Compound Properties · Block Properties
   ======================================================================= */
function pvRows(row, group, filter){
  if (row < 0) return null;
  const rows = rowValues(row);
  const q = (filter || '').trim().toUpperCase();
  const keep = rows.filter(([k, v]) =>
    k !== 'Source.Name' &&
    (!q || k.toUpperCase().indexOf(q) >= 0 || v.toUpperCase().indexOf(q) >= 0));
  if (!group) return [['', keep]];
  const ref = PARAMS[val('TYPE', row)] || {}, sect = ref.s || {};
  const SEC = {I:'Inputs', O:'Outputs', D:'Data stores', X:'อื่น ๆ'};
  const g = {I:[], O:[], D:[], X:[]};
  for (const p of keep) (g[sect[p[0]]] || g.X).push(p);
  return ['I','O','D','X'].filter(k => g[k].length).map(k => [SEC[k], g[k]]);
}

function pvTable(host, row, opt){
  const o = opt || {};
  const box = $('#' + host);
  const secs = pvRows(row, o.group, o.filter);
  if (!secs){ box.innerHTML = '<p class="empty">' + esc(o.none || 'ไม่มี record') + '</p>'; return null; }
  const flat = [];
  let h = '<table class="gt pv"><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>';
  for (const [lab, pairs] of secs){
    if (lab) h += '<tr class="sec"><td colspan="2">' + esc(lab) + ' · ' + pairs.length + '</td></tr>';
    for (const [k, v] of pairs){
      const rf = o.refs && isRefVal(v, row);
      h += '<tr><td>' + esc(k) + '</td><td class="w' + (rf ? ' ref' : '') + '"' +
           (rf ? ' data-ref="' + esc(v) + '"' : '') + '>' + esc(v) + '</td></tr>';
      flat.push([k, v]);
    }
  }
  box.innerHTML = h + '</tbody></table>';
  if (!flat.length) box.innerHTML = '<p class="empty">ไม่พบพารามิเตอร์ที่ตรงกับคำค้น</p>';
  return flat;
}

function drawParam(){
  const st = curSt();
  if (!st){
    /* ALL NETWORK has no station block — report the network itself */
    let t = 0, mods = 0;
    for (const s of CPS){ t += s.rows.length; mods += s.mods.length; }
    const pairs = [['NETWORK', 'TOP'], ['TYPE', 'Foxboro I/A Series'],
                   ['STATIONS', fmt(CPS.length)], ['COMPOUNDS', fmt(CPS.reduce((a,s)=>a+s.comps.length,0))],
                   ['BLOCKS', fmt(t)], ['MODULES', fmt(mods)], ['SNAPSHOT', GEN || '—']];
    $('#param').innerHTML = '<table class="gt pv"><thead><tr><th>Parameter</th><th>Value</th></tr>' +
      '</thead><tbody>' + pairs.map(([k, v]) =>
        '<tr><td>' + esc(k) + '</td><td class="w">' + esc(v) + '</td></tr>').join('') +
      '</tbody></table>';
    $('#nPar').textContent = 'TOP';
    return;
  }
  $('#nPar').textContent = st.n;
  if (st.sta >= 0){ pvTable('param', st.sta, {}); return; }
  const sy = st.si >= 0 ? SYS[st.si] : null;
  const pairs = [['CP', st.n], ['TYPE', (sy && sy.sta) || '—'], ['AREA', st.area || '—'],
                 ['COMPOUNDS', fmt(st.comps.length)], ['BLOCKS', fmt(st.rows.length)],
                 ['MODULES', fmt(st.mods.length)]];
  $('#param').innerHTML = '<table class="gt pv"><thead><tr><th>Parameter</th><th>Value</th></tr>' +
    '</thead><tbody>' + pairs.map(([k, v]) =>
      '<tr><td>' + esc(k) + '</td><td class="w">' + esc(v) + '</td></tr>').join('') +
    '</tbody></table>';
}

function drawCprops(){
  const c = curComp();
  if (!c){ $('#cprops').innerHTML = '<p class="empty">เลือก compound จากรายการ</p>'; return; }
  pvTable('cprops', c.row, {none:'compound นี้ไม่มี record ของตัวเองใน SaveAll'});
}

let bpRows = null;
function drawBprops(){
  $('#pq').value = pFilter;
  bpRows = pvTable('bprops', selBlk,
    {group:true, refs:true, filter:pFilter, none:'เลือก block จาก Block List'});
}

/* =======================================================================
   7. PANE: Compound List · Blocks Types · Block List
   ======================================================================= */
function drawClist(){
  const st = curSt();
  const list = [];
  if (st) st.comps.forEach((c, j) => list.push([st.n, c, selCp, j]));
  else for (let i = 0; i < CPS.length; i++)
    CPS[i].comps.forEach((c, j) => list.push([CPS[i].n, c, i, j]));

  $('#nCmp').textContent = fmt(list.length);
  const show = list.slice(0, cmpCap);
  let h = '<table class="gt"><thead><tr><th>CP</th><th>Compounds</th><th></th></tr></thead><tbody>';
  for (const [cp, c, ci, j] of show){
    const on = ci === selCp && j === selComp;
    h += '<tr' + (on ? ' class="on"' : '') + ' data-cp="' + ci + '" data-j="' + j + '">' +
         '<td>' + esc(cp) + '</td><td><b>' + esc(c.n) + '</b></td>' +
         '<td class="num">' + (c.rows.length || '') + '</td></tr>';
  }
  h += '</tbody></table>';
  if (!show.length) h = '<p class="empty">ไม่มี compound</p>';
  else if (list.length > show.length)
    h += '<button class="more" data-more="cmp">แสดงเพิ่ม · เหลืออีก ' +
         fmt(list.length - show.length) + '</button>';
  $('#clist').innerHTML = h;
}

function drawTypes(){
  const tc = typeCounts();
  const total = tc.reduce((a, t) => a + t[1], 0);
  let h = '<table class="gt"><thead><tr><th>Type</th><th></th></tr></thead><tbody>';
  h += '<tr' + (selType ? '' : ' class="on"') + ' data-ty=""><td><b>ALL TYPES</b></td>' +
       '<td class="num">' + fmt(total) + '</td></tr>';
  for (const [t, n] of tc)
    h += '<tr' + (t === selType ? ' class="on"' : '') + ' data-ty="' + esc(t) + '">' +
         '<td>' + esc(t) + '</td><td class="num">' + fmt(n) + '</td></tr>';
  $('#types').innerHTML = h + '</tbody></table>';
}

/* the rows the Block List is showing, uncapped — Export CSV walks these at
   click time. Building the CSV on every render would cost 77,010 rows of
   string work on ALL NETWORK for a button nobody may press. */
let lastRows = null;
function drawBlist(){
  const rows = blockRows();
  $('#nBlk').textContent = fmt(rows.length);
  const show = rows.slice(0, blkCap);
  let h = '<table class="gt"><thead><tr><th>CP</th><th>Compound</th><th>Block</th>' +
          '<th>Type</th></tr></thead><tbody>';
  for (const r of show){
    const full = val('NAME', r), k = full.indexOf(':');
    h += '<tr' + (r === selBlk ? ' class="on"' : '') + ' data-r="' + r + '">' +
         '<td>' + esc(val('CP NAME', r)) + '</td>' +
         '<td>' + esc(k > 0 ? full.slice(0, k) : '—') + '</td>' +
         '<td><b>' + esc(k > 0 ? full.slice(k + 1) : full) + '</b></td>' +
         '<td>' + esc(val('TYPE', r)) + '</td></tr>';
  }
  h += '</tbody></table>';
  if (!show.length) h = '<p class="empty">ไม่มี block ในขอบเขตนี้</p>';
  else if (rows.length > show.length)
    h += '<button class="more" data-more="blk">แสดงเพิ่ม · เหลืออีก ' +
         fmt(rows.length - show.length) + '</button>';
  $('#blist').innerHTML = h;
  lastRows = rows;
}

/* =======================================================================
   8. PANE: Block Mapping
   The way the Auditor draws it: what feeds this block on the left, the
   block itself on the right with its pins down both edges. The chain
   slider walks that back N hops, a column per hop.

   A block is fed two ways and the drawing has to show both:
     * hardware — IOM_ID names the module, and the module's ECB block is
       the record named <compound>:<IOM_ID> in the same station
     * software — an input parameter whose value is another block's pin

   Only *wired* pins go down the left edge. params.js calls 48 of an AIN's
   parameters inputs because they are settable, not because anything is
   landed on them; drawing those as pins would bury the two that matter.
   ======================================================================= */
const SRC_W = 186, SRC_H = 46, SRC_GAP = 13, BLK_W = 214, PIN_H = 15, WIRE = 118;
const MAXSRC = 8, MAXPIN = 12, MAXNODES = 36;

/* the ECB record for the module this block is landed on */
function iomSource(r){
  const iom = val('IOM_ID', r);
  if (!iom) return -1;
  buildShortIndex();
  const cands = shortIndex.get(iom);
  if (!cands) return -1;
  const cp = val('CP NAME', r);
  const same = cands.filter(x => x !== r && val('CP NAME', x) === cp);
  return same.length ? same[0] : -1;
}

/* everything landed on one block's input side, hardware first */
function sourcesOf(r){
  const sect = (PARAMS[val('TYPE', r)] || {}).s || {};
  const out = [], seen = new Set();
  const es = iomSource(r);
  if (es >= 0){
    out.push({pin:val('PNT_NO', r) ? 'PNT_NO' : 'IOM_ID', row:es});
    seen.add(es + '|hw');
  }
  for (const [k, v] of rowValues(r)){
    if (out.length >= MAXSRC) break;
    if (k === 'Source.Name' || sect[k] !== 'I') continue;
    if (!isRefVal(v, r)) continue;
    const rr = resolveRef(v, r);
    if (rr < 0 || rr === r) continue;              // a self-reference is not a wire
    const kk = rr + '|' + k;
    if (seen.has(kk)) continue;
    seen.add(kk);
    out.push({pin:k, row:rr});
  }
  return out;
}

function drawMap(){
  const box = $('#bmap'), note = $('#nMap');
  if (selBlk < 0){
    box.innerHTML = '<p class="empty">เลือก block จาก Block List เพื่อดูผังการต่อ</p>';
    note.textContent = '';
    return;
  }
  const ty = val('TYPE', selBlk);
  const ref = PARAMS[ty] || {}, sect = ref.s || {}, pdesc = ref.d || {};
  /* outputs are read off the block *type*: SaveAll keeps configuration, not
     running values, so an output pin almost never carries one — but the pin
     is on the block whether or not the export caught a number in it. */
  const outs = Object.keys(sect).filter(k => sect[k] === 'O').map(k => [k, pdesc[k] || '']);
  const outPins = outs.slice(0, MAXPIN);

  /* walk back `depth` hops. A block already drawn keeps its place and just
     gains another wire — a chain that rejoins itself should read as one
     block feeding two things, not as two copies of it. */
  const levels = [[{row:selBlk}]];
  const placed = new Map([[selBlk, {d:0, i:0}]]);
  const edges = [];
  let nodes = 1, cut = false;
  for (let d = 1; d <= depth; d++){
    const prev = levels[d - 1], cur = [];
    for (let pi = 0; pi < prev.length; pi++){
      for (const s of sourcesOf(prev[pi].row)){
        let at = placed.get(s.row);
        if (!at){
          if (nodes >= MAXNODES){ cut = true; continue; }
          at = {d, i:cur.length};
          cur.push({row:s.row});
          placed.set(s.row, at);
          nodes++;
        }
        edges.push({from:at, to:{d:d - 1, i:pi}, pin:s.pin});
      }
    }
    if (!cur.length) break;
    levels.push(cur);
  }
  const L = levels.length - 1;

  /* the left edge of the block carries the pins the first hop lands on */
  const inPins = [];
  for (const e of edges) if (e.to.d === 0 && inPins.indexOf(e.pin) < 0) inPins.push(e.pin);

  /* A cascade loops: the valve a PID drives feeds its own BCALCI back. That
     edge runs right-to-left, against every other wire, so it gets its own
     lane under the boxes rather than a straight line drawn through them. */
  const back = edges.filter(e => e.from.d <= e.to.d);
  const fwd  = edges.filter(e => e.from.d >  e.to.d);

  const blkH = 34 + PIN_H * Math.max(inPins.length, outPins.length, 1) + 8;
  const colH = levels.map((lv, d) =>
    d === 0 ? blkH : lv.length * SRC_H + (lv.length - 1) * SRC_GAP);
  const BACK = back.length ? 22 : 0;
  const H = Math.max.apply(null, colH) + 26 + BACK;
  const pad = 8;
  const xOf = d => pad + (L - d) * (SRC_W + WIRE);
  const topOf = d => 13 + Math.max(0, (H - 26 - BACK - colH[d]) / 2);
  const yOf = (d, i) => topOf(d) + i * ((d === 0 ? blkH : SRC_H) + SRC_GAP);
  const W = xOf(0) + BLK_W + 16;
  const lane = H - 9;

  /* where a wire lands: a pin on the block, or the middle of a source box */
  const landY = e => e.to.d === 0
    ? yOf(0, 0) + 34 + PIN_H * Math.max(0, inPins.indexOf(e.pin)) + PIN_H / 2
    : yOf(e.to.d, e.to.i) + SRC_H / 2;
  const leaveY = e => e.from.d === 0
    ? yOf(0, 0) + blkH / 2
    : yOf(e.from.d, e.from.i) + SRC_H / 2;
  const rightOf = d => xOf(d) + (d === 0 ? BLK_W : SRC_W);

  let s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '">' +
    '<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" ' +
    'orient="auto"><path class="arrow" d="M0 0 L8 4 L0 8 z"/></marker>' +
    '<marker id="ahb" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" ' +
    'orient="auto"><path class="arrow fb" d="M0 0 L8 4 L0 8 z"/></marker></defs>';

  /* the wires first, so the boxes sit on top of them */
  const nth = new Map();
  for (const e of fwd){
    const key = e.from.d + ':' + e.from.i;
    const j = nth.get(key) || 0; nth.set(key, j + 1);
    const sx = rightOf(e.from.d), sy = leaveY(e);
    const mid = sx + 14 + j * 11;
    s += '<path class="wire" marker-end="url(#ah)" d="M' + sx + ' ' + sy +
         ' H' + mid + ' V' + landY(e) + ' H' + (xOf(e.to.d) - 3) + '"/>' +
         '<text class="wlab" x="' + (mid + 4) + '" y="' + (landY(e) - 4) + '">' +
         esc(e.pin) + '</text>';
  }
  /* feedback: out the right, along the lane under everything, back up */
  back.forEach((e, bi) => {
    const sx = rightOf(e.from.d), sy = leaveY(e);
    const tx = xOf(e.to.d) - 3, ty2 = landY(e);
    const outx = sx + 10 + bi * 8, ly = lane - bi * 5;
    s += '<path class="wire fb" marker-end="url(#ahb)" d="M' + sx + ' ' + sy +
         ' H' + outx + ' V' + ly + ' H' + (tx - 13) + ' V' + ty2 + ' H' + tx + '"/>' +
         '<text class="wlab fb" x="' + (tx - 11) + '" y="' + (ty2 - 4) + '">' +
         esc(e.pin) + '</text>';
  });

  /* Every box is a real link into SIGNAL MAP rather than a click handler:
     an <a> inside inline SVG gets the browser's own behaviour — the URL on
     hover, ctrl/middle-click for a new tab, keyboard focus. */
  const mapLink = r =>
    'signal-map.html?tag=' + encodeURIComponent(val('NAME', r));

  /* every hop back from the block */
  for (let d = 1; d <= L; d++){
    levels[d].forEach((nd, i) => {
      const x = xOf(d), y = yOf(d, i);
      const full = val('NAME', nd.row), sty = val('TYPE', nd.row);
      const cls = sty.slice(0, 3) === 'ECB' ? 'bx ecb' : 'bx';
      s += '<a class="src" href="' + esc(mapLink(nd.row)) + '">' +
        '<title>' + esc(full) + ' — เปิดใน SIGNAL MAP</title>' +
        '<rect class="' + cls + '" x="' + x + '" y="' + y + '" width="' + SRC_W +
        '" height="' + SRC_H + '" rx="3"/>' +
        '<text class="t1" x="' + (x + 9) + '" y="' + (y + 18) + '">' +
        esc(clip(full, 26)) + '</text>' +
        '<text class="t2" x="' + (x + 9) + '" y="' + (y + 33) + '">' +
        esc(clip(val('DESCRP', nd.row) || sty, 30)) + '</text>' +
        '</a>';
    });
  }

  /* the block itself */
  const xb = xOf(0), blkY = yOf(0, 0);
  s += '<a class="src" href="' + esc(mapLink(selBlk)) + '">' +
       '<title>' + esc(val('NAME', selBlk)) + ' — เปิดใน SIGNAL MAP</title>' +
       '<rect class="bx root" x="' + xb + '" y="' + blkY + '" width="' + BLK_W +
       '" height="' + blkH + '" rx="3"/>' +
       '<text class="t1" x="' + (xb + BLK_W / 2) + '" y="' + (blkY + 16) +
       '" text-anchor="middle">' + esc(clip(val('NAME', selBlk), 28)) + '</text>' +
       '<text class="t2" x="' + (xb + BLK_W / 2) + '" y="' + (blkY + 28) +
       '" text-anchor="middle">' + esc(clip(val('DESCRP', selBlk) || '', 32)) +
       (val('DESCRP', selBlk) ? ' · ' : '') + esc(ty) + '</text>';
  inPins.forEach((p, i) => {
    s += '<text class="pin" x="' + (xb + 7) + '" y="' + (blkY + 34 + PIN_H * i + 11) + '">' +
         esc(p) + '</text>';
  });
  outPins.forEach((p, i) => {
    s += '<text class="pin" x="' + (xb + BLK_W - 7) + '" y="' + (blkY + 34 + PIN_H * i + 11) +
         '" text-anchor="end">' + esc(p[0]) + '</text>';
  });
  s += '</a>';

  box.innerHTML = '<div class="bmap">' + s + '</svg></div>' +
    '<p class="mapnote">' +
    (nodes > 1 ? 'ต้นทาง ' + (nodes - 1) + ' บล็อก · ' + edges.length + ' เส้น · ลึก ' + L + ' ชั้น'
               : 'ไม่มีอะไรต่อเข้าบล็อกนี้ — ไม่มี IOM_ID และไม่มีพินขาเข้าที่อ้างถึงบล็อกอื่น') +
    ' · คลิกกล่องเพื่อเปิดใน SIGNAL MAP' +
    (back.length ? ' · เส้นประสีเหลือง = ป้อนกลับ ' + back.length + ' เส้น' : '') +
    (cut ? ' · ตัดที่ ' + MAXNODES + ' บล็อก' : '') +
    ' · พินซ้าย = ขาเข้าที่ต่อจริง · พินขวา = output ของบล็อก' +
    (outs.length > MAXPIN ? ' (แสดง ' + MAXPIN + ' จาก ' + outs.length + ')' : '') +
    '</p>';
  note.textContent = val('NAME', selBlk);
}
const clip = (s, n) => String(s).length > n ? String(s).slice(0, n - 1) + '…' : String(s);

/* =======================================================================
   9. BREADCRUMB + NETWORK SELECT
   ======================================================================= */
function drawCrumb(){
  const st = curSt(), c = curComp();
  let h = '<button class="' + (st ? '' : 'here') + '" data-cp="-1">TOP</button>';
  if (st){
    h += '<span class="sep">›</span><button class="' + (c || selMod >= 0 ? '' : 'here') +
         '" data-cp="' + selCp + '">' + esc(st.n) + '</button>';
    if (selMod >= 0){
      h += '<span class="sep">›</span><button class="' + (selBlk < 0 ? 'here' : '') +
           '" data-mod="' + selMod + '">' + esc(MODS[selMod].d) + '</button>';
    } else if (c){
      h += '<span class="sep">›</span><button class="' + (selBlk < 0 ? 'here' : '') +
           '" data-cp="' + selCp + '" data-j="' + c.j + '">' + esc(c.n) + '</button>';
    }
  }
  if (selBlk >= 0){
    const full = val('NAME', selBlk), k = full.indexOf(':');
    h += '<span class="sep">›</span><button class="here">' +
         esc(k > 0 ? full.slice(k + 1) : full) + '</button>';
  }
  $('#crumb').innerHTML = h;
  $('#netSel').value = String(selCp);
}

function fillNetSel(){
  let h = '<option value="-1">TOP · ALL NETWORK</option>';
  CPS.forEach((s, i) => { h += '<option value="' + i + '">' + esc(s.n) + '</option>'; });
  $('#netSel').innerHTML = h;
}

/* =======================================================================
   10. SELECTION
   ======================================================================= */
function firstBlockOf(c){ return c && c.rows.length ? c.rows[0] : -1; }

function pickCp(i){
  selCp = i; selComp = -1; selType = ''; selBlk = -1; selMod = -1; MODROWS = null;
  blkCap = cmpCap = 300; pFilter = '';
  const st = curSt();
  if (st && st.comps.length){ selComp = 0; selBlk = firstBlockOf(st.comps[0]); }
  revealTree();
  render();
}
function pickComp(i, j){
  selCp = i; selComp = j; selType = ''; selMod = -1; MODROWS = null;
  selBlk = firstBlockOf(CPS[i].comps[j]);
  blkCap = 300; pFilter = '';
  revealTree();
  render();
}
/* an FBM picked in the equipment rail scopes the block panes to what is
   landed on it — the tree's answer to "what is on this module" */
function pickMod(mi){
  const ci = CPN.get(SYS[MODS[mi].s].n);
  if (ci === undefined) return;
  selCp = ci; selMod = mi; selComp = -1; selType = '';
  MODROWS = modBlocks(CPS[ci], MODS[mi]);
  selBlk = MODROWS.length ? MODROWS[0] : -1;
  blkCap = cmpCap = 300; pFilter = '';
  revealTree();
  render();
}
function pickType(t){
  selType = t; blkCap = 300; pFilter = '';
  const rows = blockRows();
  selBlk = rows.length ? rows[0] : -1;
  render();
}
function pickBlock(r){ selBlk = r; pFilter = ''; render(); }

/* jump to any row: work the station and compound out of it */
function gotoRow(r){
  const ci = CPN.get(val('CP NAME', r));
  if (ci === undefined) return;
  const st = CPS[ci], full = val('NAME', r), k = full.indexOf(':');
  const cr = st.cm.get(k > 0 ? full.slice(0, k) : full);
  selCp = ci; selComp = cr ? cr.j : -1; selType = ''; selMod = -1; MODROWS = null;
  selBlk = k > 0 ? r : firstBlockOf(cr);
  blkCap = cmpCap = 300; pFilter = '';
  revealTree();
  render();
}

function render(){
  drawTree(); drawNet(); drawCrumb(); drawParam(); drawClist(); drawCprops();
  drawTypes(); drawBlist(); drawBprops(); drawMap();
}

/* =======================================================================
   11. EVENTS
   ======================================================================= */
$('#net').addEventListener('click', e => {
  const b = e.target.closest('.nbox'); if (b) pickCp(+b.dataset.cp);
});
$('#netSel').addEventListener('change', e => pickCp(+e.target.value));
$('#crumb').addEventListener('click', e => {
  const b = e.target.closest('button[data-cp],button[data-mod]'); if (!b) return;
  if (b.dataset.mod !== undefined) pickMod(+b.dataset.mod);
  else if (b.dataset.j !== undefined) pickComp(+b.dataset.cp, +b.dataset.j);
  else pickCp(+b.dataset.cp);
});

/* ---- the equipment rail ---------------------------------------------- */
$('#tree').addEventListener('click', e => {
  const node = e.target.closest('.tnode'); if (!node) return;
  const n = parseKey(node.dataset.k);
  if (e.target.closest('[data-act="tog"]')){
    const k = node.dataset.k;
    if (expanded.has(k)) expanded.delete(k); else expanded.add(k);
    drawTree();
    return;
  }
  if (kidCount(n)) expanded.add(node.dataset.k);
  if (n.k === 'net') pickCp(-1);
  else if (n.k === 'cp') pickCp(n.i);
  else if (n.k === 'mod') pickMod(n.i);
  else {
    const tag = MODS[n.i].ch[n.c][1];
    const r = tag ? nameRow(tag) : -1;
    if (r >= 0) gotoRow(r); else { pickMod(n.i); }
  }
});
$('#collapseAll').addEventListener('click', () => {
  expanded = new Set(['net']);
  drawTree();
});

/* ---- chain length ----------------------------------------------------- */
$('#mdep').addEventListener('input', e => {
  depth = +e.target.value;
  $('#mdepN').textContent = depth;
  drawMap();
});
$('#clist').addEventListener('click', e => {
  if (e.target.closest('[data-more]')){ cmpCap += 500; drawClist(); return; }
  const tr = e.target.closest('tr[data-cp]');
  if (tr) pickComp(+tr.dataset.cp, +tr.dataset.j);
});
$('#types').addEventListener('click', e => {
  const tr = e.target.closest('tr[data-ty]'); if (tr) pickType(tr.dataset.ty);
});
$('#blist').addEventListener('click', e => {
  if (e.target.closest('[data-more]')){ blkCap += 500; drawBlist(); return; }
  const tr = e.target.closest('tr[data-r]'); if (tr) pickBlock(+tr.dataset.r);
});
$('#bprops').addEventListener('click', e => {
  const td = e.target.closest('td.ref'); if (!td) return;
  const r = resolveRef(td.dataset.ref, selBlk);
  if (r >= 0) gotoRow(r);
});
/* the map's boxes are <a> elements — the browser handles the navigation */
let pqt;
$('#pq').addEventListener('input', e => {
  clearTimeout(pqt);
  const raw = e.target.value;
  pqt = setTimeout(() => { pFilter = raw; drawBprops(); }, 140);
});

/* ---- jump-to-tag ----------------------------------------------------- */
let qt;
$('#q').addEventListener('input', e => {
  clearTimeout(qt);
  const raw = e.target.value.trim();
  qt = setTimeout(() => drawHits(raw), 150);
});
$('#q').addEventListener('blur', () => setTimeout(() => $('#hits').classList.add('hide'), 160));
$('#q').addEventListener('focus', () => { if ($('#hits').innerHTML) $('#hits').classList.remove('hide'); });

function drawHits(raw){
  const box = $('#hits');
  if (raw.length < 2){ box.innerHTML = ''; box.classList.add('hide'); return; }
  const up = raw.toUpperCase(), out = [];
  for (const s of CPS){
    if (s.n.toUpperCase().indexOf(up) >= 0)
      out.push(['station', s.n, fmt(s.rows.length) + ' block', {cp:CPN.get(s.n)}]);
    if (out.length >= 6) break;
  }
  const a = dense(iName), d = dictOf(iName);
  for (let i = 0; i < N && out.length < 14; i++){
    const c = a[i]; if (c < 0) continue;
    if (d[c].toUpperCase().indexOf(up) >= 0)
      out.push(['block', d[c], val('DESCRP', i) || val('TYPE', i), {r:i}]);
  }
  if (!out.length){ box.innerHTML = '<p class="empty">ไม่พบ</p>'; box.classList.remove('hide'); return; }
  box.innerHTML = out.map(([k, lab, sub, g], i) =>
    '<button data-i="' + i + '"><b>' + esc(lab) + '</b><i>' + esc(sub) + '</i></button>').join('');
  box.classList.remove('hide');
  box._hits = out;
}
$('#hits').addEventListener('mousedown', e => {
  const b = e.target.closest('button[data-i]'); if (!b) return;
  const g = $('#hits')._hits[+b.dataset.i][3];
  $('#hits').classList.add('hide');
  $('#q').value = '';
  if (g.r !== undefined) gotoRow(g.r); else pickCp(g.cp);
});

/* ---- folding rail: the same gesture as the tag table's filter --------- */
const RAIL_KEY = 'fox-mgr-rail-collapsed';
const railToggle = $('#railToggle'), railLogo = $('#railLogo');
function setRailCollapsed(on, remember){
  document.body.classList.toggle('rail-collapsed', on);
  railToggle.innerHTML = on ? '&#8250;' : '&#8249;';        // the glyph IS the label
  const label = on ? 'เปิดผังอุปกรณ์' : 'ย่อผังอุปกรณ์';
  railToggle.setAttribute('aria-label', label);
  railToggle.setAttribute('aria-expanded', String(!on));
  railToggle.title = label;
  if (remember){ try { localStorage.setItem(RAIL_KEY, on ? '1' : '0'); } catch (e) {} }
}
railToggle.addEventListener('click', () =>
  setRailCollapsed(!document.body.classList.contains('rail-collapsed'), true));

/* Folded, the tile reopens the rail; open, it pauses its own float — the
   second job is what tells a reader the first one is clickable at all. */
railLogo.addEventListener('click', () => {
  if (document.body.classList.contains('rail-collapsed')){ setRailCollapsed(false, true); return; }
  const paused = railLogo.classList.toggle('paused');
  railLogo.title = paused ? 'คลิกเพื่อให้ไอคอนขยับต่อ' : 'คลิกเพื่อหยุดการเคลื่อนไหว';
  railLogo.setAttribute('aria-label', railLogo.title);
});
railLogo.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); railLogo.click(); }
});
try { if (localStorage.getItem(RAIL_KEY) === '1') setRailCollapsed(true, false); } catch (e) {}

/* ---- theme + CSV ----------------------------------------------------- */
$('#themeBtn').addEventListener('click', () => {
  const t = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', t);
  try { localStorage.setItem('fox-theme', t); } catch (e) {}
});
try { const t = localStorage.getItem('fox-theme');
      if (t) document.documentElement.setAttribute('data-theme', t); } catch (e) {}

$('#csvBtn').addEventListener('click', () => {
  if (!lastRows || !lastRows.length) return;
  const qv = v => /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  let out = '﻿CP,COMPOUND,BLOCK,TYPE\n';
  for (const r of lastRows){
    const full = val('NAME', r), k = full.indexOf(':');
    out += [val('CP NAME', r), k > 0 ? full.slice(0, k) : '',
            k > 0 ? full.slice(k + 1) : full, val('TYPE', r)].map(qv).join(',') + '\n';
  }
  const url = URL.createObjectURL(new Blob([out], {type:'text/csv;charset=utf-8'}));
  const a = document.createElement('a');
  a.href = url;
  a.download = 'foxboro-blocklist-' + lastRows.length + '.csv';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
});

/* =======================================================================
   12. BOOT
   ======================================================================= */
(async function boot(){
  try {
    if (typeof window.FOX_DATA_B64 !== 'string') throw new Error('ไม่พบไฟล์ data.js');
    if (typeof DecompressionStream === 'undefined')
      throw new Error('เบราว์เซอร์นี้ไม่รองรับ DecompressionStream — กรุณาใช้ Chrome/Edge รุ่นใหม่');

    $('#bootMsg').textContent = 'กำลังคลายข้อมูล 77,010 แถว…';
    const d = await decodePayload(window.FOX_DATA_B64);
    N = d.n; HEAD = d.h; RAW = d.c;
    HEAD.forEach((h, i) => { if (h && !IDX.has(h)) IDX.set(h, i); });
    iName = IDX.get('NAME'); iType = IDX.get('TYPE'); iCp = IDX.get('CP NAME');

    $('#bootMsg').textContent = 'กำลังอ่านทะเบียนอุปกรณ์…';
    if (typeof window.FOX_SYS_B64 === 'string'){
      const s = await decodePayload(window.FOX_SYS_B64);
      SYS = s.sys; MODS = s.mods; GEN = s.gen || '';
    }
    if (typeof window.FOX_PARAMS_B64 === 'string'){
      try { PARAMS = await decodePayload(window.FOX_PARAMS_B64); } catch (e) { PARAMS = {}; }
    }

    $('#bootMsg').textContent = 'กำลังสร้างผังลำดับชั้น…';
    buildIndex();
    mergeSystems();
    fillNetSel();

    let blocks = 0, comps = 0, mods = 0;
    for (const s of CPS){ blocks += s.rows.length; comps += s.comps.length; mods += s.mods.length; }
    $('#lede').innerHTML =
      '<b>' + fmt(CPS.length) + '</b> station · <b>' + fmt(comps) + '</b> compound · ' +
      '<b>' + fmt(blocks) + '</b> block · <b>' + fmt(mods) + '</b> module';

    /* ?tag=COMPOUND:BLOCK opens straight on that block, ?cp= on a station */
    const p = new URLSearchParams(location.search);
    const tag = p.get('tag'), cp = p.get('cp');
    let done = false;
    if (tag){ const r = nameRow(tag); if (r >= 0){ gotoRow(r); done = true; } }
    if (!done && cp && CPN.has(cp)){ pickCp(CPN.get(cp)); done = true; }
    if (!done) pickCp(CPS.length ? 0 : -1);

    $('#boot').classList.add('hide');
    $('#app').classList.remove('hide');
  } catch (err){
    $('#boot').innerHTML =
      '<p style="max-width:460px;text-align:center">โหลดข้อมูลไม่สำเร็จ<br><b>' +
      esc(err.message) + '</b><br><br>ต้องมี <code>data.js</code>, <code>systems.js</code> และ ' +
      '<code>params.js</code> อยู่โฟลเดอร์เดียวกับ <code>system-manager.html</code></p>';
    console.error(err);
  }
})();
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf8", newline="\n").write(
    "<!doctype html>\n<html lang=\"th\">\n" + head + BODY)
print("system-manager.html written (%.1f KB)" % (os.path.getsize(OUT) / 1024))
