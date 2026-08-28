# -*- coding: utf-8 -*-
"""Make the tag table the page's主 subject: drop the Rows-by-area chart and the
whole Breakdown panel, move the table above what remains, and give it the
height those two panels were using."""
import io, re, sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"
s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)

# ---- 1. markup: charts panel keeps one chart, Breakdown panel goes -------
OLD_PANELS = """      <section class="panel pg-overview" id="pnlCharts">
        <div class="panel-head"><h2>Distribution <span class="n" id="chartNote"></span></h2></div>
        <div class="charts">
          <figure>
            <figcaption>Rows by area <em>คลิกแท่งเพื่อกรอง</em></figcaption>
            <div class="chart" id="chArea"></div>
          </figure>
          <figure>
            <figcaption>Rows by block type <em>12 อันดับแรก</em></figcaption>
            <div class="chart" id="chType"></div>
          </figure>
        </div>
      </section>

      <section class="panel pg-overview" id="pnlAgg">
        <div class="panel-head"><h2>Breakdown <span class="n" id="aggNote"></span></h2></div>
        <div class="tbl-scroll short" id="aggScroll">
          <div class="tbl" id="aggTbl"></div>
        </div>
      </section>

      <section class="panel">"""
NEW_PANELS = """      <section class="panel">"""
assert OLD_PANELS in s, "panels block not found"
s = s.replace(OLD_PANELS, NEW_PANELS, 1)

# the remaining chart now follows the table
OLD_TAIL = """        <div class="empty hide" id="tblEmpty">ไม่พบข้อมูลที่ตรงกับตัวกรอง</div>
      </section>
    </main>"""
NEW_TAIL = """        <div class="empty hide" id="tblEmpty">ไม่พบข้อมูลที่ตรงกับตัวกรอง</div>
      </section>

      <section class="panel pg-overview" id="pnlCharts">
        <div class="panel-head"><h2>Rows by block type <span class="n" id="chartNote"></span></h2></div>
        <div class="charts"><div class="chart" id="chType"></div></div>
      </section>
    </main>"""
assert OLD_TAIL in s, "table tail not found"
s = s.replace(OLD_TAIL, NEW_TAIL, 1)

# ---- 2. the table takes the height the removed panels were using ---------
SUBS = [
    ('  overflow:auto; max-height:620px; position:relative;',
     '  overflow:auto; max-height:min(76vh,960px); min-height:280px; position:relative;'),
    ('.tbl-scroll.short{max-height:370px}', ''),
    # one chart should not stretch the full width of a 1760px board
    ('.charts{display:grid; grid-template-columns:repeat(auto-fit,minmax(390px,1fr)); gap:22px}',
     '.charts{display:grid; grid-template-columns:repeat(auto-fit,minmax(390px,660px));\n'
     '        gap:22px; justify-content:start}'),
    # ---- 3. render only the block-type chart --------------------------
    ("""    barChart($('#chArea'), areaRows, 'area', sel.length);
    barChart($('#chType'), typeRows.slice(0, 12), 'type', sel.length);
    $('#chartNote').textContent = `${fmt(typeRows.length)} types · ${fmt(areaRows.length)} areas`;
    renderAgg();""",
     """    barChart($('#chType'), typeRows.slice(0, 15), 'type', sel.length);
    $('#chartNote').textContent =
      `15 อันดับแรก จาก ${fmt(typeRows.length)} types · คลิกแท่งเพื่อกรอง`;"""),
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

# ---- 4. drop renderAgg() entirely ---------------------------------------
pat = re.compile(r"\nfunction renderAgg\(\)\{.*?\n\}\n", re.S)
s, k = pat.subn("\n", s, count=1)
assert k == 1, "renderAgg() not removed"

for dead in ("#chArea", "#aggNote", "#aggTbl", "#aggScroll", "renderAgg"):
    assert dead not in s, "leftover reference: %s" % dead

io.open(PAGE, "w", encoding="utf8").write(s)
print("table-first layout applied: %.1f KB -> %.1f KB" % (n_before / 1024, len(s) / 1024))
