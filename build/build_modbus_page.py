# -*- coding: utf-8 -*-
"""Assemble modbus.html from system-monitor.html's shell.

The <head> (fonts, design tokens, every shared component style) is lifted
verbatim out of system-monitor.html so the four pages cannot drift apart and
the fonts are byte-identical rather than re-encoded. Only the <title> changes
and a small page-specific block is appended before </style>. The <body> and
the script are this page's own -- a single filterable table over modbus.js.

Idempotent: rewrites modbus.html every run. Re-run whenever the shell in
system-monitor.html changes.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
SRC = os.path.join(WEB, "system-monitor.html")
OUT = os.path.join(WEB, "modbus.html")

src = open(SRC, encoding="utf8").read()
m = re.search(r"<head>.*?</head>", src, re.S)
assert m, "cannot find <head> in system-monitor.html"
head = m.group(0)
head = head.replace("<title>FOXBORO FBM (I/O) MODULE MANAGEMENT</title>",
                    "<title>FOXBORO MODBUS COMMUNICATION</title>")
assert "<title>FOXBORO MODBUS COMMUNICATION</title>" in head, "title swap failed"

PAGE_CSS = """
/* ============================================================ MODBUS == */
.filterbar{display:flex; gap:12px 14px; flex-wrap:wrap; align-items:flex-end; margin-bottom:16px}
.filterbar .fld{display:flex; flex-direction:column; gap:4px}
.filterbar .fld.grow{flex:1 1 260px; min-width:220px}
.filterbar label{font-size:10px; font-weight:800; letter-spacing:.11em;
  text-transform:uppercase; color:var(--text-faint); padding-left:4px}
.filterbar select{
  border:1px solid var(--border); background:var(--surface-2); color:var(--text);
  border-radius:var(--r-pill); padding:9px 32px 9px 14px; font-size:13.5px; font-weight:600;
  box-shadow:var(--press); outline:none; cursor:pointer; appearance:none; width:100%;
  background-image:linear-gradient(45deg,transparent 50%,var(--text-faint) 50%),
    linear-gradient(135deg,var(--text-faint) 50%,transparent 50%);
  background-position:calc(100% - 18px) 55%, calc(100% - 13px) 55%;
  background-size:5px 5px, 5px 5px; background-repeat:no-repeat;
}
.filterbar select:focus-visible{outline:3px solid var(--mint-ring); outline-offset:2px}
.filterbar .fld.grow .search{width:100%}
.pill-dir{display:inline-block; min-width:38px; text-align:center; padding:2px 9px;
  border-radius:var(--r-pill); font-size:10.5px; font-weight:800; letter-spacing:.06em}
.pill-dir.in{background:color-mix(in srgb,#7fb3c4 26%,transparent); color:var(--accent);
  border:1px solid color-mix(in srgb,#7fb3c4 45%,transparent)}
.pill-dir.out{background:color-mix(in srgb,#c9973c 24%,transparent); color:var(--amber-ink);
  border:1px solid color-mix(in srgb,#c9973c 42%,transparent)}
:root[data-theme="dark"] .pill-dir.out{color:var(--amber-ink)}
td .bank{font-size:11px; color:var(--text-dim); white-space:nowrap}
td .rw{font-size:9.5px; font-weight:800; letter-spacing:.05em; color:var(--text-faint)}
td.reg{font-weight:700; letter-spacing:.02em; white-space:nowrap}
td .gw{font-weight:700}
td .sub{display:block; color:var(--text-faint); font-size:11.5px; margin-top:1px}
.tagl{color:var(--accent); font-weight:700; text-decoration:none; white-space:nowrap}
.tagl:hover{text-decoration:underline}
.count-in{color:var(--accent); font-weight:800}
.count-out{color:var(--amber-deep); font-weight:800}
main{display:flex; flex-direction:column; gap:16px; min-width:0}
"""
head = head.replace("</style>", PAGE_CSS + "</style>", 1)

BODY = r"""
<body>

<div id="boot"><div class="ring"></div><p id="bootMsg">กำลังโหลดตาราง Modbus…</p></div>

<div class="app hide" id="app">

  <header class="topbar">
    <div>
      <p class="eyebrow">Foxboro I/A Series · serial &amp; ethernet gateways</p>
      <h1>MODBUS COMMUNICATION</h1>
      <p class="lede" id="lede"></p>
    </div>
    <div class="tools">
      <button class="btn" id="csvBtn">Export CSV</button>
      <button class="btn icon" id="themeBtn" title="สลับธีมสว่าง/มืด">◐</button>
    </div>
  </header>

  <nav class="pagenav" aria-label="หน้าในชุดเครื่องมือ">
    <a href="system-manager.html"><b>SYSTEM MANAGER</b><i>ผังอุปกรณ์ &amp; บล็อก</i></a>
    <a href="index.html"><b>TAG SEARCH</b><i>ตาราง tag ทั้งหมด</i></a>
    <a href="signal-map.html"><b>SIGNAL MAP</b><i>ผังการเดินสัญญาณ</i></a>
    <a href="system-monitor.html"><b>FBM (I/O) MODULE MANAGEMENT</b><i>โมดูล &amp; spare point</i></a>
    <a href="modbus.html" aria-current="page"><b>MODBUS COMMUNICATION</b><i>register IN/OUT ต่ออุปกรณ์</i></a>
  </nav>

  <div class="kpis" id="kpis"></div>

  <section class="panel">
    <div class="panel-head">
      <h2 id="mainTitle">รายการ point</h2>
      <div class="tabs" id="tabs">
        <button data-tab="points" class="on">Register points</button>
        <button data-tab="devices">สรุปอุปกรณ์</button>
      </div>
    </div>

    <div class="filterbar" id="filterbar">
      <div class="fld"><label for="fCP">CP</label>
        <select id="fCP"><option value="">ทั้งหมด</option></select></div>
      <div class="fld"><label for="fGW">Gateway</label>
        <select id="fGW"><option value="">ทั้งหมด</option></select></div>
      <div class="fld"><label for="fDev">Device</label>
        <select id="fDev"><option value="">ทั้งหมด</option></select></div>
      <div class="fld"><label for="fDir">ทิศทาง</label>
        <select id="fDir">
          <option value="">IN + OUT</option>
          <option value="0">IN (อ่านจากอุปกรณ์)</option>
          <option value="1">OUT (เขียนไปอุปกรณ์)</option>
        </select></div>
      <div class="fld"><label for="fBank">Register bank</label>
        <select id="fBank">
          <option value="">ทุก bank</option>
          <option value="0">0xxxx · Coil (RW)</option>
          <option value="1">1xxxx · Discrete input (RO)</option>
          <option value="3">3xxxx · Input register (RO)</option>
          <option value="4">4xxxx · Holding register (RW)</option>
          <option value="-1">Packed / ไม่มี register</option>
        </select></div>
      <div class="fld grow"><label for="q">ค้นหา</label>
        <div class="search"><input id="q" placeholder="tag / register / คำอธิบาย / letterbug…" autocomplete="off"><i class="mag">⌕</i></div>
      </div>
    </div>

    <div id="view"></div>
  </section>
</div>

<script src="modbus.js"></script>
<script>
"use strict";
const $ = s => document.querySelector(s);

async function inflate(b64){
  const bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
  for (let i = 0; i < n; i++) u8[i] = bin.charCodeAt(i);
  const st = new Blob([u8]).stream().pipeThrough(new DecompressionStream("gzip"));
  return JSON.parse(new TextDecoder().decode(await new Response(st).arrayBuffer()));
}
const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const fmt = n => Number(n).toLocaleString("en-US");

/* ---- data ---------------------------------------------------------- */
// P row: [dev, dir(0 IN /1 OUT), reg, bank, fmt, block, tag, descrp, eu, lo, hi]
let CPS = [], GWS = [], DEVS = [], PTS = [], GEN = "";
const BANK = {
  "0":  {t:"Coil",             rw:"RW", x:"0xxxx"},
  "1":  {t:"Discrete input",   rw:"RO", x:"1xxxx"},
  "3":  {t:"Input register",   rw:"RO", x:"3xxxx"},
  "4":  {t:"Holding register", rw:"RW", x:"4xxxx"},
  "-1": {t:"packed",           rw:"",   x:""},
};
const gwLabel  = g => `${GWS[g].lb} · ${GWS[g].md || "?"}`;
const devAddr  = d => d.addr ? (d.kind === "RTU" ? "sta " + d.addr : "TCP " + d.addr) : "";
const cpOfDev  = d => CPS[GWS[DEVS[d].g].c];

/* ---- state -------------------------------------------------------- */
let tab = "points";
let fCP = "", fGW = "", fDev = "", fDir = "", fBank = "", q = "";
let shown = 800;

/* ---- filtering --------------------------------------------------- */
function devVisible(di){
  const d = DEVS[di];
  if (fCP  && cpOfDev(di) !== fCP) return false;
  if (fGW  && GWS[d.g].lb !== fGW) return false;
  if (fDev && d.dv !== fDev) return false;
  return true;
}
function filteredPts(){
  const needle = q.trim().toLowerCase();
  return PTS.filter(p => {
    if (!devVisible(p[0])) return false;
    if (fDir  && String(p[1]) !== fDir) return false;
    if (fBank && String(p[3]) !== fBank) return false;
    if (needle){
      const d = DEVS[p[0]];
      const hay = (p[6] + " " + p[7] + " " + p[2] + " " + p[5] + " " +
                   d.dv + " " + GWS[d.g].lb + " " + (d.addr||"")).toLowerCase();
      if (!hay.includes(needle)) return false;
    }
    return true;
  });
}
function filteredDevs(){
  const needle = q.trim().toLowerCase();
  return DEVS.map((d,i) => i).filter(di => {
    if (!devVisible(di)) return false;
    if (needle){
      const d = DEVS[di];
      const hay = (d.dv + " " + d.nm + " " + GWS[d.g].lb + " " + (d.addr||"") + " " +
                   d.proto + " " + d.ds).toLowerCase();
      if (!hay.includes(needle)) return false;
    }
    if (fDir === "0" && !d.in)  return false;
    if (fDir === "1" && !d.out) return false;
    return true;
  });
}

/* ---- rendering -------------------------------------------------- */
function drawKpis(){
  const dv = DEVS.map((_,i) => i).filter(i => devVisible(i)
    && !(fDir === "0" && !DEVS[i].in) && !(fDir === "1" && !DEVS[i].out));
  const pv = filteredPts();
  const nin = pv.filter(p => p[1] === 0).length;
  const tcp = dv.filter(i => DEVS[i].kind === "TCP").length;
  const cell = (k,v,n) => `<div class="kpi"><div class="k">${k}</div><div class="v">${v}</div><div class="n">${n}</div></div>`;
  $("#kpis").innerHTML =
    cell("Gateways", fmt(new Set(dv.map(i => DEVS[i].g)).size), "FBM230/231/232/233") +
    cell("Devices",  fmt(dv.length), `${tcp} Modbus/TCP · ${dv.length - tcp} serial/RTU`) +
    cell("Register points", fmt(pv.length), `${fmt(nin)} IN · ${fmt(pv.length - nin)} OUT`) +
    cell("CPs", fmt(new Set(dv.map(i => cpOfDev(i))).size), "control processors");
}

function pointsView(){
  const list = filteredPts();
  $("#mainTitle").textContent = `รายการ point — ${fmt(list.length)} รายการ`;
  if (!list.length) return `<p class="empty">ไม่พบ point ตามเงื่อนไขที่เลือก</p>`;
  const head = ["CP","Gateway","Device","Dir","Register","Bank","Fmt","Block","Tag","คำอธิบาย","ช่วงค่า"]
    .map(t => `<th class="no">${t}</th>`).join("");
  const slice = list.slice(0, shown);
  const body = slice.map(p => {
    const d = DEVS[p[0]], g = d.g;
    const bk = BANK[String(p[3])] || {t:"",rw:"",x:""};
    const range = (p[9] || p[10]) ? `${esc(p[9])}–${esc(p[10])}${p[8]?" "+esc(p[8]):""}`
                                  : (p[8] ? esc(p[8]) : "—");
    return `<tr>
      <td class="mono">${esc(CPS[GWS[g].c])}</td>
      <td><span class="gw">${esc(GWS[g].lb)}</span><span class="sub">${esc(GWS[g].md||"")}</span></td>
      <td>${esc(d.dv)}<span class="sub">${esc(devAddr(d) || d.proto)}</span></td>
      <td><span class="pill-dir ${p[1]?"out":"in"}">${p[1]?"OUT":"IN"}</span></td>
      <td class="reg">${esc(p[2] || "—")}</td>
      <td><span class="bank">${esc(bk.t||"—")}</span>${bk.rw?` <span class="rw">${bk.rw}</span>`:""}</td>
      <td class="dim">${esc(p[4] || "—")}</td>
      <td class="dim">${esc(p[5])}</td>
      <td><a class="tagl" href="signal-map.html?tag=${encodeURIComponent(p[6])}">${esc(p[6])}</a></td>
      <td class="dim">${esc(p[7] || "—")}</td>
      <td class="dim">${range}</td>
    </tr>`;
  }).join("");
  const more = list.length > shown
    ? `<button class="btn more" id="moreBtn">แสดงเพิ่ม (${fmt(list.length - shown)} เหลือ)</button>` : "";
  return `<div class="tw"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>
    <p class="note">คลิกที่ tag เพื่อเปิดผังสัญญาณ · <b>IN</b> = CP อ่านค่าจากอุปกรณ์ (RIN/IIN/BIN/PAKIN),
      <b>OUT</b> = CP เขียนไปยังอุปกรณ์ (ROUT/IOUT/BOUT/PAKOUT) ·
      register bank ตามมาตรฐาน Modbus (เลขหลักแรกของ address)</p>${more}`;
}

function devicesView(){
  const list = filteredDevs();
  $("#mainTitle").textContent = `สรุปอุปกรณ์ — ${fmt(list.length)} ตัว`;
  if (!list.length) return `<p class="empty">ไม่พบอุปกรณ์ตามเงื่อนไขที่เลือก</p>`;
  const head = ["CP","Gateway","Model","Port","Device","Protocol","Station / IP","Options","IN","OUT","รวม"]
    .map((t,i) => `<th class="no${i>=8?" num":""}">${t}</th>`).join("");
  const body = list.map(di => {
    const d = DEVS[di], g = d.g;
    return `<tr>
      <td class="mono">${esc(CPS[GWS[g].c])}</td>
      <td><span class="gw">${esc(GWS[g].lb)}</span></td>
      <td class="dim">${esc(GWS[g].md||"—")}</td>
      <td class="dim">${esc(d.port||"—")}</td>
      <td>${esc(d.dv)}${d.nm && d.nm!==d.dv ? `<span class="sub">${esc(d.nm)}</span>`:""}</td>
      <td class="dim">${esc(d.proto||"—")}</td>
      <td class="dim">${esc(d.addr || "—")}${d.kind?` <span class="rw">${d.kind}</span>`:""}</td>
      <td class="dim">${esc(d.opt||"—")}</td>
      <td class="num count-in">${d.in?fmt(d.in):"—"}</td>
      <td class="num count-out">${d.out?fmt(d.out):"—"}</td>
      <td class="num"><b>${fmt(d.in + d.out)}</b></td>
    </tr>`;
  }).join("");
  return `<div class="tw"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>
    <p class="note">หนึ่งแถว = ECB201 หนึ่งตัว (อุปกรณ์ serial/Modbus หนึ่งเครื่องบน gateway) ·
      <b>Options</b> จาก DVOPTS เช่น <code>@20</code> คาบสแกน, <code>H</code> holding-base,
      <code>TO</code> timeout, <code>DUPS</code> อนุญาต address ซ้ำ</p>`;
}

function draw(){
  drawKpis();
  $("#view").innerHTML = tab === "points" ? pointsView() : devicesView();
}

/* ---- filter option lists --------------------------------------- */
function fillSelect(el, opts, keep){
  el.innerHTML = `<option value="">${el.id==="fCP"?"ทุก CP":el.id==="fGW"?"ทุก gateway":"ทุก device"}</option>`
    + opts.map(o => `<option value="${esc(o[0])}"${o[0]===keep?" selected":""}>${esc(o[1])}</option>`).join("");
  if (![...el.options].some(o => o.value === keep)) el.value = "";
}
function rebuildSelects(){
  const cps = [...new Set(DEVS.map((_,i) => cpOfDev(i)))].sort();
  fillSelect($("#fCP"), cps.map(c => [c,c]), fCP);

  const gws = [...new Map(DEVS
    .map((_,i) => i)
    .filter(i => !fCP || cpOfDev(i) === fCP)
    .map(i => [GWS[DEVS[i].g].lb, gwLabel(DEVS[i].g)])).entries()]
    .sort((a,b) => a[0].localeCompare(b[0]));
  fillSelect($("#fGW"), gws, fGW);
  fGW = $("#fGW").value;

  const devs = [...new Map(DEVS
    .map((d,i) => i)
    .filter(i => (!fCP || cpOfDev(i) === fCP) && (!fGW || GWS[DEVS[i].g].lb === fGW))
    .map(i => {
      const d = DEVS[i];
      return [d.dv, d.dv + (devAddr(d) ? " · " + devAddr(d) : "")];
    })).entries()]
    .sort((a,b) => a[0].localeCompare(b[0]));
  fillSelect($("#fDev"), devs, fDev);
  fDev = $("#fDev").value;
}

/* ---- CSV ------------------------------------------------------- */
function csv(){
  const rows = [];
  if (tab === "points"){
    rows.push(["CP","GATEWAY","MODEL","DEVICE","STATION/IP","PROTOCOL","DIRECTION",
               "REGISTER","BANK","ACCESS","FORMAT","BLOCK","TAG","DESCRIPTION","EU","LO","HI"]);
    for (const p of filteredPts()){
      const d = DEVS[p[0]], g = d.g, bk = BANK[String(p[3])] || {t:"",rw:""};
      rows.push([CPS[GWS[g].c], GWS[g].lb, GWS[g].md, d.dv, d.addr, d.proto,
                 p[1] ? "OUT" : "IN", p[2], (bk.x?bk.x+" ":"")+bk.t, bk.rw, p[4], p[5], p[6], p[7],
                 p[8], p[9], p[10]]);
    }
  } else {
    rows.push(["CP","GATEWAY","MODEL","PORT","DEVICE","NAME","PROTOCOL","KIND",
               "STATION/IP","OPTIONS","IN","OUT","TOTAL"]);
    for (const di of filteredDevs()){
      const d = DEVS[di], g = d.g;
      rows.push([CPS[GWS[g].c], GWS[g].lb, GWS[g].md, d.port, d.dv, d.nm, d.proto,
                 d.kind, d.addr, d.opt, d.in, d.out, d.in + d.out]);
    }
  }
  const body = rows.map(r => r.map(v => {
    v = String(v == null ? "" : v);
    return /[",\n]/.test(v) ? '"' + v.replace(/"/g,'""') + '"' : v;
  }).join(",")).join("\r\n");
  const blob = new Blob(["﻿" + body], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `foxboro-modbus-${tab}${fCP?"-"+fCP:""}.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

/* ---- events -------------------------------------------------- */
$("#tabs").addEventListener("click", e => {
  const b = e.target.closest("[data-tab]"); if (!b) return;
  tab = b.dataset.tab; shown = 800;
  [...$("#tabs").children].forEach(x => x.classList.toggle("on", x === b));
  draw();
});
$("#fCP").addEventListener("change", e => { fCP = e.target.value; fGW = fDev = ""; shown = 800; rebuildSelects(); draw(); });
$("#fGW").addEventListener("change", e => { fGW = e.target.value; fDev = ""; shown = 800; rebuildSelects(); draw(); });
$("#fDev").addEventListener("change", e => { fDev = e.target.value; shown = 800; draw(); });
$("#fDir").addEventListener("change", e => { fDir = e.target.value; shown = 800; draw(); });
$("#fBank").addEventListener("change", e => { fBank = e.target.value; shown = 800; draw(); });
$("#q").addEventListener("input", e => { q = e.target.value; shown = 800; draw(); });
$("#view").addEventListener("click", e => {
  if (e.target.closest("#moreBtn")){ shown += 1600; draw(); }
});
$("#csvBtn").addEventListener("click", csv);
$("#themeBtn").addEventListener("click", () => {
  const d = document.documentElement.getAttribute("data-theme") === "dark";
  document.documentElement.setAttribute("data-theme", d ? "light" : "dark");
  try { localStorage.setItem("fox-theme", d ? "light" : "dark"); } catch(_){}
});
try {
  const t = localStorage.getItem("fox-theme");
  if (t) document.documentElement.setAttribute("data-theme", t);
} catch(_){}

/* ---- boot -------------------------------------------------- */
(async () => {
  try {
    if (typeof window.FOX_MB_B64 !== "string") throw new Error("ไม่พบไฟล์ modbus.js");
    if (typeof DecompressionStream === "undefined")
      throw new Error("เบราว์เซอร์นี้ไม่รองรับ DecompressionStream — ใช้ Chrome/Edge รุ่นใหม่");
    const d = await inflate(window.FOX_MB_B64);
    CPS = d.cps; GWS = d.gws; DEVS = d.devs; PTS = d.pts; GEN = d.gen;
    const nin = PTS.filter(p => p[1] === 0).length;
    $("#lede").textContent =
      `${fmt(GWS.length)} gateway · ${fmt(DEVS.length)} อุปกรณ์ · ${fmt(PTS.length)} register point `
      + `(${fmt(nin)} IN / ${fmt(PTS.length - nin)} OUT) · ปรับปรุง ${GEN}`;
    rebuildSelects();
    draw();
    $("#boot").classList.add("hide");
    $("#app").classList.remove("hide");
  } catch (err) {
    $("#bootMsg").textContent = "โหลดข้อมูลไม่สำเร็จ: " + err.message;
    console.error(err);
  }
})();
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf8", newline="\n").write("<!doctype html>\n<html lang=\"th\">\n" + head + BODY)
print("modbus.html written  (%.0f KB)" % (os.path.getsize(OUT) / 1024))
