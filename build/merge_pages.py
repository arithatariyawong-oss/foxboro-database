# -*- coding: utf-8 -*-
"""Collapse OVERVIEW and CUSTOM TABLE into one page that uses the custom-table
layout: the column picker is always in the rail and every column is the user's
to choose, so the tab strip and the whole page-switching branch go away."""
import io, sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"
s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)

SUBS = [
    # ---- CSS: the tab strip is dead ------------------------------------
    ("""/* ============================================================== TABS ==== */
.tabs{
  display:inline-flex; gap:4px; align-self:flex-start; padding:5px;
  background:var(--surface-3); border:1px solid var(--border);
  border-radius:var(--r-pill); box-shadow:var(--press);
}
.tab{
  border:0; background:transparent; color:var(--text-dim);
  padding:11px 30px; border-radius:var(--r-pill); cursor:pointer;
  font-size:13.5px; font-weight:800; letter-spacing:.09em; text-transform:uppercase;
  transition:background .16s ease, color .16s ease, box-shadow .16s ease;
}
.tab:hover{color:var(--text)}
.tab.is-on{background:var(--mint); color:#14322a; box-shadow:var(--lift-sm), var(--inset-hi)}
:root[data-theme="dark"] .tab.is-on{color:#dff5ea}
.tab:focus-visible{outline:3px solid var(--mint-ring); outline-offset:2px}

/* ============================================================ LAYOUT ==== */""",
     """/* ============================================================ LAYOUT ==== */"""),

    # ---- markup: no tab strip ------------------------------------------
    ("""  <nav class="tabs">
    <button class="tab is-on" data-page="overview">Overview</button>
    <button class="tab" data-page="custom">Custom table</button>
  </nav>

  <div class="layout">""",
     """  <div class="layout">"""),

    # ---- markup: column picker and chart are always present ------------
    ('      <section class="fgroup hide" id="gCols">',
     '      <section class="fgroup" id="gCols">'),
    ('      <section class="panel pg-overview" id="pnlCharts">',
     '      <section class="panel" id="pnlCharts">'),

    # ---- state: no current page ----------------------------------------
    ("""const state = {
  page:'overview',
  sets:""",
     """const state = {
  sets:"""),

    ("""function currentCols(){
  return state.page === 'custom' ? state.cols.slice() : defaultCols();
}""",
     """function currentCols(){
  return state.cols.slice();
}"""),

    ("""  if (state.page === 'overview'){
    barChart($('#chType'), typeRows.slice(0, 15), 'type', sel.length);
    $('#chartNote').textContent =
      `15 อันดับแรก จาก ${fmt(typeRows.length)} types · คลิกแท่งเพื่อกรอง`;
  }
  renderTable();""",
     """  barChart($('#chType'), typeRows.slice(0, 15), 'type', sel.length);
  $('#chartNote').textContent =
    `15 อันดับแรก จาก ${fmt(typeRows.length)} types · คลิกแท่งเพื่อกรอง`;
  renderTable();"""),

    ("""  $('#colNote').textContent = `${visCols.length} คอลัมน์` +
    (state.page === 'custom' ? ' · เลือกเพิ่มได้จาก CUSTOM COLUMN ทางซ้าย' : '');""",
     """  $('#colNote').textContent =
    `${visCols.length} คอลัมน์ · เพิ่ม/เอาออกได้ที่ CUSTOM COLUMN ทางซ้าย`;"""),

    # ---- behaviour: drop the page switch -------------------------------
    ("""/* =======================================================================
   9. PAGES / THEME / CSV
   ======================================================================= */
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('is-on', x === t));
  state.page = t.dataset.page;
  document.querySelectorAll('.pg-overview').forEach(p => p.classList.toggle('hide', state.page !== 'overview'));
  $('#gCols').classList.toggle('hide', state.page !== 'custom');
  scroll.scrollTop = 0;
  refresh();
}));

$('#themeBtn')""",
     """/* =======================================================================
   9. THEME / CSV
   ======================================================================= */
$('#themeBtn')"""),

    ("""  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
  if (state.page === 'overview') refresh();
});""",
     """  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
  refresh();                       // the chart's colours come from the theme
});"""),

    ("""addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => {
  if (state.page === 'overview') refresh(); else paintRows();
}, 180); });""",
     """addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(refresh, 180); });"""),
]

missing = []
for old, new in SUBS:
    if old not in s:
        missing.append(old.strip().splitlines()[0][:76])
    else:
        s = s.replace(old, new, 1)

if missing:
    print("NOT FOUND (%d):" % len(missing))
    for m in missing:
        print("   -", m)
    sys.exit(1)

for dead in ("state.page", "pg-overview", 'class="tabs"', "data-page", ".tab{"):
    assert dead not in s, "leftover reference: %s" % dead

io.open(PAGE, "w", encoding="utf8").write(s)
print("merged to a single page: %.1f KB -> %.1f KB" % (n_before / 1024, len(s) / 1024))
