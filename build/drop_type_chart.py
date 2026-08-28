# -*- coding: utf-8 -*-
"""Remove the Rows-by-block-type chart. It repeated the TYPE chips in the rail
(which already carry every type and its row count) and sat below a 76vh table
where nobody would scroll to it. With it goes everything only it used: the bar
renderer, the hover tooltip, the click-to-filter hit layer, and their CSS."""
import io, re, sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"
s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)

# ---- 1. markup -----------------------------------------------------------
SUBS = [
    ("""      </section>

      <section class="panel" id="pnlCharts">
        <div class="panel-head"><h2>Rows by block type <span class="n" id="chartNote"></span></h2></div>
        <div class="charts"><div class="chart" id="chType"></div></div>
      </section>
    </main>""",
     """      </section>
    </main>"""),

    ('<div class="tip" id="tip"></div>\n\n', ''),

    # ---- 2. render path ------------------------------------------------
    ("""  recompute();
  const areaRows = countBy(iArea), typeRows = countBy(iType);""",
     """  recompute();
  const areaRows = countBy(iArea);"""),

    ("""  barChart($('#chType'), typeRows.slice(0, 15), 'type', sel.length);
  $('#chartNote').textContent =
    `15 อันดับแรก จาก ${fmt(typeRows.length)} types · คลิกแท่งเพื่อกรอง`;
  renderTable();""",
     """  renderTable();"""),

    ("""   7. AGGREGATES + CHARTS""", """   7. AGGREGATES"""),

    # ---- 3. nothing left that needs a full refresh on these events -----
    ("""  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
  refresh();                       // the chart's colours come from the theme
});""",
     """  try { localStorage.setItem('fox-theme', cur); } catch (e) {}
});"""),

    ("""addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(refresh, 180); });""",
     """/* only the table cares about the viewport: its visible window is derived
   from the scroller's height */
addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(paintRows, 180); });"""),

    # ---- 4. the share bar died with the Breakdown table ----------------
    ("""\n.sbar{display:block; height:11px; border-radius:4px; background:var(--series); min-width:2px}""",
     ""),

    # ---- 5. the chart hues have no mark left to paint ------------------
    ("""  --series:#2f6b73;              /* chart mark — validated >=3:1 on --surface */\n  --series-soft:#9dbcbf;\n""", ""),
    ("""  --series:#7fb3c4;\n  --series-soft:#46606a;\n""", ""),
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

# ---- 5. the chart CSS block ---------------------------------------------
s, k = re.subn(r"\n/\* charts \*/\n.*?\n(?=/\* =+ TABLES =+ \*/)", "\n", s, count=1, flags=re.S)
assert k == 1, "chart CSS block not removed"

# ---- 6. barChart(), the tooltip and the hit-layer click handler ----------
s, k = re.subn(r"\n/\* Horizontal bars,.*?\n(?=/\* =+\n   8\. REFRESH)", "\n", s, count=1, flags=re.S)
assert k == 1, "barChart/tooltip block not removed"

for dead in ("barChart", "#chType", "chartNote", "pnlCharts", "'#tip'", ".hit", "figcaption",
             "typeRows", ".sbar", "--series"):
    assert dead not in s, "leftover reference: %s" % dead

io.open(PAGE, "w", encoding="utf8").write(s)
print("chart removed: %.1f KB -> %.1f KB" % (n_before / 1024, len(s) / 1024))
